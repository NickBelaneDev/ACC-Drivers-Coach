import pandas as pd
from typing import Literal

from .adapter import DataAdapter
from .analyzer.corner_analyzer import CornerBuilder
from .analyzer.segment_analyzer import SegmentAnalyzer

from .corner.corner_enums import ReturnFormat
from .dataframe_validation import (
    DataFrameValidator,
    EmptyDataFrameError
)

from src.logger import get_logger
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import (
    get_raw_corner_df_from_df,
    get_segment_df_from_lap_fd,
)
from .corner.corner_model import CornerModel
log = get_logger("Lap - logger", to_console=False)

class LapModel:
    """
    High-level API for analyzing a single lap’s telemetry.

    This model wraps the normalized lap DataFrame and exposes convenient methods to:
      - build corner models and segment summaries,
      - retrieve analyzed corner/segment data in multiple formats,
      - slice the raw lap DataFrame by segment, corner, or explicit distance range.

    Internally it precomputes the g-force vector, sets up analyzers/builders, and
    caches corner/segment structures for fast access in downstream code.
    """
    def __init__(self,
                 raw_lap_df: pd.DataFrame,
                 track_name: str,
                 driver: str = "User"):
        """
        Initialize a lap model from raw, normalized telemetry.

        The constructor:
          1) computes the resultant g-force vector for the entire lap,
          2) prepares analyzers/builders for corners and segments,
          3) derives basic lap/meta info (lap time, available corner/segment IDs),
          4) builds all corner models and segment summaries up front.

        Parameters
        ----------
        raw_lap_df : pandas.DataFrame
            Normalized telemetry for a *single* lap. Must include at least:
            ``Distance``, ``Time``, corner markers (e.g. ``corner_id`` and related columns),
            and segment markers (e.g. ``segment_id_x`` and related columns).
        track_name : str
            Human-readable track label (e.g., "Spa").
        driver : str, optional
            Driver identifier; defaults to "User".

        Attributes set
        --------------
        track_name : str
            Track label passed in.
        lap_time_s : float
            Elapsed lap time (``Time.iloc[-1] - Time.iloc[0]``).
        corner_ids : list[int]
            Unique, non-null corner IDs present in the lap.
        segment_ids : list[int]
            Unique, non-null segment IDs present in the lap.
        corner_models : dict[int, CornerModel]
            Built corner models keyed by corner ID.
        segments_df : pandas.DataFrame
            Concatenated segment metrics (one row per segment).
        driver : str
            Driver identifier.
        """

        self._raw_df: pd.DataFrame = TelemetryCalculator.calc_g_force_vector(raw_lap_df)

        self._segment_analyzer = SegmentAnalyzer()
        self._corner_builder = CornerBuilder()

        # --- public settings ---
        self.track_name: str = track_name
        self.lap_time_s: float = self._raw_df["Time"].iloc[-1] - self._raw_df["Time"].iloc[0]
        self.driver = driver

        self.corner_ids = self._raw_df["corner_id"].dropna().unique().tolist()
        self.segment_ids = self._raw_df["segment_id_x"].dropna().unique().tolist()

        self.corner_models: dict[int, CornerModel] = self._load_corner_models()
        self.segments_df = self._load_segments()

    def __repr__(self):
        """
        Developer-friendly representation.

        Returns
        -------
        str
            A compact summary with track name and lap time.
        """
        print(f"Track: {self.track_name}\n"
              f"Lap-Time: {self.lap_time_s}")
    def __str__(self):
        """
        Human-readable string with the most relevant lap context.

        Returns
        -------
        str
            Multiline summary with track and lap time.
        """
        return (f"Track: {self.track_name}\n"
                f"Lap-Time: {self.lap_time_s}")

    # Private Methods
    def _dirty_corner_validation(self,
                                 corner_id) \
            -> bool:
        """
        Quick validation that a corner exists and is non-empty.

        This helper ensures the ID is present in the lap and the built corner model
        is not empty. It raises explicit errors to avoid silent failures.

        Parameters
        ----------
        corner_id : int
            Corner ID to validate.

        Returns
        -------
        bool
            ``True`` if validation passes.

        Raises
        ------
        ValueError
            If the corner is not part of this lap or the corner model is empty.
        """
        if corner_id not in self.corner_ids:
            raise ValueError(f"{id=}, not in self.corner_ids!")

        _corner = self.corner_models[corner_id]

        if _corner.is_empty():
            raise ValueError("Empty Corner!")

        return True

    def _load_segments(self,
                       raw_lap_df: pd.DataFrame=None) \
            -> pd.DataFrame:
        """
        Build and return a DataFrame with analyzed metrics for all segments.

        For each segment ID present in the lap, this method:
          - extracts the raw segment window from the lap,
          - analyzes it via ``SegmentAnalyzer``,
          - converts the resulting dataclass into a one-row DataFrame, and
          - concatenates all segment rows into a single DataFrame.

        Parameters
        ----------
        raw_lap_df : pandas.DataFrame, optional
            Not used yet. If provided, will be ignored (reserved for future API).

        Returns
        -------
        pandas.DataFrame
            One row per segment with segment metadata and metrics.
            Missing values are filled with 0 for downstream robustness.
        """
        lap_df = self._raw_df
        if raw_lap_df is not None:
            log.debug(f"{lap_df.info()=}")

        segments = []
        for _id in sorted(lap_df["segment_id_x"].dropna().unique()):
            raw_segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            segment = self._segment_analyzer.analyze(raw_segment_df)
            analyzed_segment_df = DataAdapter.to_dataframe(segment)
            segments.append(analyzed_segment_df)

        _final_df = pd.concat(segments, ignore_index=True)
        if _final_df.empty:
            raise EmptyDataFrameError(message="The '_final_df' is empty!")

        log.info("successfully loaded all segments!")
        return _final_df.fillna(0)

    def _load_corner_models(self,
                            raw_lap_df: pd.DataFrame=None)\
            -> dict[int, CornerModel]:
        """
        Build all corner models for this lap and return them as a dict.

        Iterates over all available corner IDs, extracts each corner’s raw window,
        and constructs a ``CornerModel``. This is typically performed once during
        initialization and cached in ``self.corner_models``.

        Parameters
        ----------
        raw_lap_df : pandas.DataFrame, optional
            Not implemented yet. Passing a value will raise ``NotImplementedError``.

        Returns
        -------
        dict[int, CornerModel]
            Mapping from corner ID to the corresponding built ``CornerModel``.

        Raises
        ------
        NotImplementedError
            If ``raw_lap_df`` is provided.
        """
        raw_df = self._raw_df
        if raw_lap_df is not None:
            raise NotImplementedError

        corner_models_dict: dict = {}
        for _id in self.corner_ids:
            raw_corner_df = get_raw_corner_df_from_df(_id, raw_df)

            corner_model = CornerModel(raw_corner_df)
            corner_models_dict[_id] = corner_model

        return corner_models_dict

    def _create_lap_dataclass(self):
        """
        Construct and return a ``Lap`` dataclass for this model.

        Notes
        -----
        - Not implemented yet; the method is intended to produce a top-level
          `Lap` container with metadata and the list of ``Corner`` entities
          (and possibly segment aggregates) for serialization or export.
        """
        raise NotImplementedError

    FRMT = Literal["DataFrame", "dict"]
    def get_corner_model(self,
                         corner_id: int) \
            -> CornerModel:
        """
        Retrieve a built ``CornerModel`` by corner ID.

        This is the primary entry point when you want to query metrics or
        raw windows for a specific corner using the corner-level API.

        Parameters
        ----------
        corner_id : int
            The corner to access.

        Returns
        -------
        CornerModel
            The corresponding model for the requested corner.

        Raises
        ------
        ValueError
            If the corner ID is invalid or the corner is empty.
        """
        self._dirty_corner_validation(corner_id)
        return self.corner_models[corner_id]

    def get_all_corner_models(self) -> dict[int, CornerModel]:
        """
        Return all built corner models keyed by corner ID.

        Returns
        -------
        dict[int, CornerModel]
            Mapping from corner ID to ``CornerModel``.
        """
        return self.corner_models

    def get_analyzed_corner_df(self,
                               corner_id: int) \
            -> pd.DataFrame:
        """
        Return a one-row DataFrame with metadata and metrics for a corner.

        This calls the corner’s strategy layer to emit the *analyzed* corner
        in tabular form, suitable for concatenation across corners or export.

        Parameters
        ----------
        corner_id : int
            Corner whose analyzed data should be returned.

        Returns
        -------
        pandas.DataFrame
            Single-row DataFrame with the corner’s meta + metric fields.

        Raises
        ------
        ValueError
            If the corner ID is invalid or the corner is empty.
        """

        self._dirty_corner_validation(corner_id)
        corner_model = self.get_corner_model(corner_id)

        return corner_model.get_corner(mode=ReturnFormat.DATAFRAME)

    def get_all_analyzed_corners_as_df(self) -> pd.DataFrame:
        """
        Return a concatenated DataFrame of all analyzed corners.

        Each corner contributes a one-row DataFrame (via the corner model’s
        strategy conversion). The result is a flat table with one row per corner.

        Returns
        -------
        pandas.DataFrame
            Concatenated table of all corners.

        Raises
        ------
        EmptyDataFrameError
            If, after concatenation, the result is empty.
        """
        corners_list = [c.get_corner(mode=ReturnFormat.DATAFRAME) for _, c in self.corner_models.items()]
        corners_df = pd.concat(corners_list)

        if corners_df.empty:
            raise EmptyDataFrameError()
        return corners_df

    def get_raw_lap_df(self,
                       segment_id: int=None,
                       corner_id: int=None,
                       area: tuple[int,int]=None) \
            -> pd.DataFrame:
        """
        Slice and return the raw, normalized lap DataFrame by region of interest.

        You can request one of three slice modes:
          1) by ``segment_id`` → returns the sub-DataFrame spanning that segment,
          2) by ``corner_id``  → returns the sub-DataFrame spanning that corner,
          3) by explicit ``area`` → a distance tuple ``(start_m, end_m)``.

        If none are provided, the complete raw lap DataFrame is returned.

        Parameters
        ----------
        segment_id : int, optional
            Segment identifier present in ``self.segment_ids``.
        corner_id : int, optional
            Corner identifier present in ``self.corner_ids``.
        area : tuple[int, int], optional
            Explicit distance range ``(start_m, end_m)`` in meters.

        Returns
        -------
        pandas.DataFrame
            A copy of the requested window. If the explicit ``area`` distances
            are not present in the lap DataFrame, an **empty** DataFrame is returned.

        Notes
        -----
        - When ``area`` is provided with ``start_m > end_m``, the bounds are swapped.
        - Slices are inclusive on both ends: ``Distance >= start`` and ``<= end``.
        """

        def slice_by_distance(start: int, end: int):
            return self._raw_df[(self._raw_df["Distance"] >= start) & (self._raw_df["Distance"] <= end)].copy()

        if segment_id and segment_id in self.segment_ids:
            mask = self._raw_df["segment_id_x"] == segment_id
            _start = self._raw_df[mask]["Distance"].min()
            _end = self._raw_df[mask]["Distance"].max()
            return slice_by_distance(_start, _end)

        if corner_id and corner_id in self.corner_ids:
            _start = self._raw_df[self._raw_df["corner_id"] == corner_id]["Distance"].iloc[0]
            _end = self._raw_df[self._raw_df["corner_id"] == corner_id]["Distance"].iloc[-1]
            return slice_by_distance(_start, _end)

        if area:
            _start, _end = area
            if not (self._raw_df["Distance"] == _start).any() or not (self._raw_df["Distance"] == _start).any():
                return pd.DataFrame()
            if _start > _end:
                return slice_by_distance(_end, _start)
            return slice_by_distance(_start, _end)

        return self._raw_df

    # ------ still in progress not used yet!
    def _get_segments_df(self, frmt:FRMT="DataFrame") -> pd.DataFrame | dict:
        """
          Returns a DataFrame with all segments' calculated and meta-data.
          :param frmt: ["DataFrame", "dict"]
          """

        if frmt == "DataFrame":
            return self.segments_df
        elif frmt == "dict":
            return self.segments_df.to_dict(orient="index")

    def _get_segment_df_by_id(self, _id: int) -> pd.DataFrame:
        """Returns all calculated and meta segment data in a single row DataFrame."""

        if _id not in self.segment_ids:
            raise ValueError(f"{id=}, not in self.segment_ids!")
        _segment = self.segments_df.loc[[_id]]
        return _segment



