import pandas as pd
from typing import Literal

from .adapter import DataAdapter
from .analyzer.corner_analyzer import CornerAnalyzer, CornerBuilder
from .analyzer.lap_analyzer import LapAnalyzer
from .corner.corner_enums import ReturnFormat
from .dataframe_validation import EmptyDataFrameError
from .lap_dataclasses import Corner, CornerMetrics
from src.logger import get_logger
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_raw_corner_df_from_df, get_segment_df_from_lap_fd, segment_to_df, corner_to_df
from .corner.corner_model import CornerModel
log = get_logger("Lap - logger", to_console=False)

class Lap:
    def __init__(self, raw_lap_df: pd.DataFrame, track_name: str, driver: str = "User"):
        """Initial API Object for working with laps."""
        self._raw_df: pd.DataFrame = TelemetryCalculator.calc_g_force_vector(raw_lap_df)
        self._analyze = LapAnalyzer(self._raw_df)
        self._corner_builder = CornerBuilder()

        # --- public settings ---
        self.track_name: str = track_name
        self.lap_time_s: float = self._raw_df["Time"].iloc[-1] - self._raw_df["Time"].iloc[0]
        self.corner_ids = self._raw_df["corner_id"].dropna().unique().tolist()
        self.segment_ids = self._raw_df["segment_id_x"].dropna().unique().tolist()
        self.corners = self._load_corner_models() # ACHGTUNG DEBUG HIER!

        self.segments_df = self._load_segments()
        self.driver = driver


    def __repr__(self):
        print(f"Track: {self.track_name}\nLap-Time: {self.lap_time_s}")
    def __str__(self):
        return f"Track: {self.track_name}\nLap-Time: {self.lap_time_s}"

    # Private Methods
    def _dirty_corner_validation(self, corner_id) -> bool:
        """
        Raises a ValueError if something is wrong with the corner_id.
        :param corner_id:
        :return: True if the corner is okay, else a ValueError will raise.
        """
        if corner_id not in self.corner_ids:
            raise ValueError(f"{id=}, not in self.corner_ids!")

        _corner = self.corners[corner_id]

        if _corner.is_empty():
            raise ValueError("Empty Corner!")

        return True

    def _load_segments(self, raw_lap_df:pd.DataFrame=None) -> pd.DataFrame:
        """Loads and returns a DataFrame consisting of all analyzed segments."""
        lap_df = self._raw_df
        if raw_lap_df is not None:
            log.debug(f"{lap_df.info()=}")

        segments = []
        # Filling all the rows
        for _id in sorted(lap_df["segment_id_x"].dropna().unique()):
            _segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            _segment, _segment_metrics = self._analyze.segment(_segment_df)
            #print(f"{_segment=}")
            segment_df = segment_to_df(_segment, _segment_metrics)

            segments.append(segment_df)
        _final_df = pd.concat(segments, ignore_index=True)

        #print(_final_df)
        return _final_df.fillna(0)
    def _load_corner_models(self, raw_lap_df:pd.DataFrame=None) -> dict[int, CornerModel]:
        """Loads and returns a Dictionary with all analyzed corners as dataclasses.
        :param raw_lap_df is not implemented yet!
        """
        raw_df = self._raw_df
        if raw_lap_df is not None:
            raise NotImplementedError

        corners_dict: dict = {}
        for _id in self.corner_ids:
            raw_corner_df = get_raw_corner_df_from_df(_id, raw_df)

            corner_model = CornerModel(raw_corner_df)
            corners_dict[_id] = corner_model

        return corners_dict

    FRMT = Literal["DataFrame", "dict"]
    def get_corner_model(self, corner_id: int) -> CornerModel:

        self._dirty_corner_validation(corner_id)
        return self.corners[corner_id]

    def get_analyzed_corner_df(self, corner_id: int) -> pd.DataFrame:
        """Returns all calculated and meta corner data in a single row DataFrame."""

        self._dirty_corner_validation(corner_id)
        corner_model = self.get_corner_model(corner_id)

        return corner_model.get_corner(mode=ReturnFormat.DATAFRAME)

    def get_all_analyzed_corners_as_df(self) -> pd.DataFrame:
        corners_list = [c.get_corner(mode=ReturnFormat.DATAFRAME) for _, c in self.corners.items()]
        corners_df = pd.concat(corners_list)
        if corners_df.empty:
            raise EmptyDataFrameError()
        return corners_df

    def get_raw_lap_df(self, segment_id: int=None, corner_id: int=None, area: tuple[int,int]=None) -> pd.DataFrame:
        """Get the raw normalized DataFrame for a certain area. You can either choose segment_id, corner_id or area. By default, you get the complete raw_df."""
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

    def get_segments_df(self, frmt:FRMT="DataFrame") -> pd.DataFrame | dict:
        """
          Returns a DataFrame with all segments' calculated and meta-data.
          :param frmt: ["DataFrame", "dict"]
          """
        if frmt == "DataFrame":
            return self.segments_df
        elif frmt == "dict":
            return self.segments_df.to_dict(orient="index")
    def get_segment_df_by_id(self, _id: int) -> pd.DataFrame:
        """Returns all calculated and meta segment data in a single row DataFrame."""
        if _id not in self.segment_ids:
            raise ValueError(f"{id=}, not in self.segment_ids!")
        _segment = self.segments_df.loc[[_id]]
        return _segment



