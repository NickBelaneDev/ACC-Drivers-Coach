import pandas as pd, numpy as np
from pandas import DataFrame
from src.logger import get_logger
import json
from pathlib import Path

from .telemetry_calculator import TelemetryCalculator
log = get_logger(to_console=False)

file_path_user = "../assets/MoTec/spa/telemetry_files/Spa-ferrari_296_gt3-hotlap_2-17-880.csv"
file_path_fastest_lap = "../../old/Spa-ferrari_296_gt3-fastest_lap.csv"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
#print(f"PROJECT_ROOT: {PROJECT_ROOT}")
BASE_DIR = PROJECT_ROOT

class TelemetryLoader:
    """
    Load and normalize MoTeC lap telemetry, enriched with track map metadata.

    This loader:
      1) reads a MoTeC CSV (single lap) and resamples it to a 1 m distance grid,
      2) loads track **segments** and **corners** from JSON, sorted by their start markers,
      3) merges telemetry with segments (asof on ``segmentStart_m``) and corners
         (asof on ``brakeArea_m``) to attach IDs/descriptions to each row,
      4) computes the resultant g-force vector and returns a single, merged DataFrame.

    The result is a **normalized, integer-meter “Distance”** DataFrame with sufficient
    metadata to run corner/segment analyzers downstream.
    """
    def __init__(self,
                 base_dir: Path=BASE_DIR):
        """
              Initialize the loader with a project root.

              Parameters
              ----------
              base_dir : pathlib.Path, optional
                  Base directory used to resolve relative asset paths
                  (track JSONs, MoTeC CSVs). Defaults to repository base.
              """
        self.telemetry_lap_df: pd.DataFrame | None = None
        self.base_dir = base_dir

    def telemetry_from_csv(self,
                           telemetry_file: str,
                           track: str) \
            -> DataFrame | None:
        """
               Load, resample, and enrich a MoTeC hotlap CSV with segments & corners.

               Workflow
               --------
               1) Resolve asset paths for the given track (segments & corners JSON).
               2) Read MoTeC CSV (skipping MoTeC header rows), drop first empty row.
               3) Resample all channels to a 1 m ``Distance`` grid via linear interpolation.
               4) Merge ``segments`` by as-of join on ``segmentStart_m`` (backward).
               5) Merge ``corners`` by as-of join on ``brakeArea_m`` (backward).
               6) Clean corner metadata beyond ``cornerEnd_m`` → set to NaN.
               7) Compute ``gForceVector`` and return the full DataFrame.

               Parameters
               ----------
               telemetry_file : str
                   Relative path to the MoTeC CSV file (from ``base_dir``).
               track : str
                   Track key (e.g., ``"spa"`` or ``"donnington"``). Case-insensitive.

               Returns
               -------
               pandas.DataFrame | None
                   Telemetry enriched with segment & corner metadata, resampled to
                   1 m **integer** ``Distance``. Also available on ``self.telemetry_lap_df``.

               Raises
               ------
               ValueError
                   If ``track`` is not recognized.
               FileNotFoundError
                   If CSV or JSON files do not exist at the resolved locations.
               json.JSONDecodeError
                   If the track JSON files are malformed.
               KeyError
                   If expected keys are missing in the JSON maps.

               Notes
               -----
               - The CSV is read with ``skiprows=14`` to skip MoTeC header meta.
               - Corner metadata is nulled (NaN) after ``cornerEnd_m`` to avoid leakage
                 of the previous corner’s labels into the next segment.
               - ``corner_id`` is converted to integer where present.
               """
        if track.lower() not in ["spa", "donnington"]:
            raise ValueError(f"track: {track} could not be found!")

        def _get_file_paths(_track: str):
            """
            Resolve asset file paths for track segments and corners.

            Parameters
            ----------
            _track : str
                Track key.

            Returns
            -------
            tuple[pathlib.Path, pathlib.Path]
                (segments_file_path, corners_file_path)

            Notes
            -----
            Raises are not suppressed here; upstream callers will see
            file/JSON errors as-is for easier debugging.
            """

            try:
                track_folder = self.base_dir / "assets"  / "MoTec" / _track.lower()
                log.debug(f"track_folder: {track_folder}")
                _segments_path = track_folder / f"{_track.lower()}_segments.json"
                _corners_path = track_folder / f"{_track.lower()}_corners.json"
                return _segments_path, _corners_path

            except Exception as e:
                print(f"Segmente und Corners konnten nicht geladen werden! {e}")
                return ""

        segments_path, corners_path = _get_file_paths(track)
        segments_df, corners_df  = self._load_map(segments_path, corners_path)

        # Red the telemetry.csv
        orig_hotlap_path = self.base_dir / telemetry_file

        _telemetry_df = pd.read_csv(orig_hotlap_path, skiprows=14, low_memory=False, engine="c").drop(0)
        telemetry_df = self._resample_df(_telemetry_df)

        telemetry_df_sorted = telemetry_df.sort_values("Distance")
        # merge the segments with the telemetry
        telemetry_with_segments_df = pd.merge_asof(
            left=telemetry_df_sorted,
            right=segments_df,
            left_on="Distance",
            right_on="segmentStart_m",
            direction="backward"
        )
        # Add the corners on top
        full_telemetry_df = pd.merge_asof(
            left=telemetry_with_segments_df,
            right=corners_df,
            left_on="Distance",
            right_on="brakeArea_m",
            direction="backward"
        )

        full_telemetry_df["corner_id"] = full_telemetry_df["corner_id"].dropna().astype(int)

        mask = full_telemetry_df["Distance"] > full_telemetry_df["cornerEnd_m"]
        corner_cols = corners_df.columns
        full_telemetry_df.loc[mask, corner_cols] = np.nan

        self.telemetry_lap_df = full_telemetry_df

        # TODO: The calculation of the gForceVector and more need their own class!
        full_telemetry_df = TelemetryCalculator.calc_g_force_vector(full_telemetry_df)
        log.info(f"Successfully loaded the DataFrame!")
        return full_telemetry_df

    @staticmethod
    def _load_map(file_path_segments, file_path_corners) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load track **segments** and **corners** JSON files as DataFrames.

        The JSON structure is expected to contain a top-level ``"segments"`` or
        ``"corners"`` key whose value is a list of dictionaries (one per item).
        Data is normalized via ``pd.json_normalize`` and sorted by the respective
        alignment columns used for as-of merges.

        Parameters
        ----------
        file_path_segments : str | pathlib.Path
            Path to the segments JSON file.
        file_path_corners : str | pathlib.Path
            Path to the corners JSON file.

        Returns
        -------
        tuple[pandas.DataFrame, pandas.DataFrame]
            ``(segments_df_sorted, corners_df_sorted)``:
              - segments sorted by ``segmentStart_m``,
              - corners sorted by ``brakeArea_m``.

        Raises
        ------
        FileNotFoundError
            If paths cannot be opened.
        json.JSONDecodeError
            If JSON content is malformed.
        KeyError
            If expected top-level keys (``"segments"``, ``"corners"``) are missing.

        See Also
        --------
        pandas.json_normalize : Flattens nested JSON into tabular form.
        """
        with open(file_path_segments, "r") as f:
            segments = json.load(f)
        with open(file_path_corners, "r") as f:
            corners = json.load(f)

        corners_df = pd.json_normalize(corners["corners"])
        corners_df_sorted = corners_df.sort_values('brakeArea_m')

        segments_df = pd.json_normalize(segments["segments"])
        segments_df_sorted = segments_df.sort_values("segmentStart_m")

        return segments_df_sorted, corners_df_sorted

    @staticmethod
    def _resample_df(lap_data: DataFrame,
                     step=1.0) \
            -> pd.DataFrame:
        """
        Resample a MoTeC lap to an integer-meter distance grid (linear interp).

        Given irregularly spaced samples (by ``Distance``), this method builds an
        integer grid from ``floor(min(Distance))`` to ``ceil(max(Distance))`` with
        the provided step (default 1.0 m) and linearly interpolates **all channels**
        onto this grid. The output ``Distance`` is cast to ``int``.

        Parameters
        ----------
        lap_data : pandas.DataFrame
            Raw MoTeC CSV content after header removal. Must contain ``Distance``
            and all channels to be resampled.
        step : float, optional
            Grid spacing in meters. Defaults to 1.0.

        Returns
        -------
        pandas.DataFrame
            Resampled telemetry where:
              - ``Distance`` is integer meters (int),
              - all other numeric channels are linearly interpolated.

        Notes
        -----
        - Non-numeric channel values are coerced to NaN prior to interpolation.
        - Rows with missing ``Distance`` are dropped before resampling.
        - This function makes a defensive copy of the input DataFrame.
        """
        telemetry = lap_data.copy()
        telemetry["Distance"] = pd.to_numeric(telemetry["Distance"], errors="coerce")
        telemetry = telemetry.dropna(subset=["Distance"]).sort_values("Distance")

        track_distance = telemetry["Distance"].astype(float).values

        start_meter = int(np.floor(track_distance.min()))
        end_meter = int(np.ceil(track_distance.max()))
        meter_grid = np.arange(start_meter, end_meter, step)

        resampled_data = {"Distance": meter_grid}

        for col in telemetry:
            if col == "Distance":
                continue
            channel_values = pd.to_numeric(telemetry[col], errors="coerce")
            resampled_data[col] = np.interp(
                meter_grid.astype(float),
                track_distance,
                channel_values)

        df_out = pd.DataFrame(resampled_data)
        df_out["Distance"] = df_out["Distance"].astype(int)
        return df_out

if __name__ == "__main__":

    motec = TelemetryLoader(Path(__file__).resolve().parent)

    user_df = motec.telemetry_from_csv(file_path_user, "spa")
    record_df = motec.telemetry_from_csv(file_path_fastest_lap, "spa")

    #record_df.to_csv("record_telemetry.csv", index=False, encoding="utf-8")
    #user_df.to_csv("user_telemetry.csv", index=False, encoding="utf-8")

    print(user_df)
