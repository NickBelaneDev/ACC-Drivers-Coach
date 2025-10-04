import pandas as pd, numpy as np
from pandas import DataFrame
from src.logger import get_logger
import json
from pathlib import Path

from .telemetry_calculator import TelemetryCalculator
log = get_logger(to_console=False)

file_path_user = "../assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"
file_path_fastest_lap = "../../old/Spa-ferrari_296_gt3-fastest_lap.csv"


class TelemetryLoader:
    def __init__(self, base_dir: Path):
        self.telemetry_lap_df: pd.DataFrame | None = None
        self.base_dir = base_dir

    def telemetry_from_csv(self, hotlap_path: str, track: str) -> DataFrame | None:
        """

        :param hotlap_path: path to the hotlap.csv file from MoTec
        :param track: name of the track the hotlap corresponds to
        :return: A sorted DataFrame with the complete raw telemetry and track meta-data normed to Distance by 1m.
        """
        if track.lower() not in ["spa", "donnington"]:
            raise ValueError(f"track: {track} could not be found!")

        def _get_file_paths(_track: str):

            """

            :param _track: Name of the racetrack
            :return: segments_file_path, corners_file_path
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
        orig_hotlap_path = self.base_dir / hotlap_path

        _telemetry_df = pd.read_csv(orig_hotlap_path, skiprows=14, low_memory=False).drop(0)
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
        return full_telemetry_df

    @staticmethod
    def _load_map(file_path_segments, file_path_corners) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Returns the segments- and corners-JSON converted to a DataFrame.
        :param file_path_segments:
        :param file_path_corners:
        :return: segments_df, corners_df
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
    def _resample_df(lap_data: DataFrame, step=1.0) -> pd.DataFrame:
        """Resamples the samplerate the length of the racetrack."""
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
