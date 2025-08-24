import pandas as pd, numpy as np
from pandas import DataFrame
from logger import get_logger
import json
from pathlib import Path
log = get_logger(to_console=False)

MOTEC_FOLDER = Path("assets/MoTec")

file_path_user = "assets/MoTec/Spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"
file_path_fastest_lap = "assets/MoTec/Spa/Spa-ferrari_296_gt3-fastest_lap.csv"

class LapTelemetry:
    def __init__(self, lap_df: DataFrame):
        self.telemetry_lap_df = lap_df or pd.DataFrame()


    @staticmethod
    def get_break_points(telemetry_df: DataFrame) -> DataFrame:

        was_not_braking = telemetry_df["BRAKE"].shift(1) < 99
        is_braking = telemetry_df["BRAKE"] >= 99

        brake_point_df = telemetry_df[is_braking & was_not_braking]

        return brake_point_df
    def get_break_point_difference(self, break_points_01_df: DataFrame, break_points_02_df: DataFrame) -> DataFrame:
        u_b_p = self.get_break_points(break_points_01_df)
        r_b_p = self.get_break_points(break_points_02_df)

        user_break_points = u_b_p.reset_index(drop=True)
        record_break_points = r_b_p.reset_index(drop=True)

        difference_df = user_break_points["Distance"] - record_break_points["Distance"]
        return difference_df

    @staticmethod
    def get_apex_df(telemetry_df: DataFrame):

        is_accelerating = telemetry_df["SPEED"].shift(1) > telemetry_df["SPEED"]
        is_slowing_down = telemetry_df["SPEED"].shift(-1) > telemetry_df["SPEED"]
        is_steering = telemetry_df["STEERING"].shift(1) > telemetry_df["STEERING"]



        apex_df = telemetry_df[is_accelerating & is_slowing_down]

        return apex_df

class MoTec:
    def __init__(self):
        self.telemetry_lap_df: pd.DataFrame | None = None

    def telemetry_from_csv(self, file_path: str, track: str) -> DataFrame | None:
        """Loads the Telemetry from a MoTec csv file and validates it for further use."""

        def _get_file_paths(_track: str):
            """

            :param _track: Name of the racetrack
            :return: segments_file_path, corners_file_path
            """
            corners = ""
            segments = ""

            try:
                track_folder = MOTEC_FOLDER / _track.lower()
                _segments_path = track_folder / f"{_track.lower()}_segments.json"
                _corners_path = track_folder / f"{_track.lower()}_corners.json"
                return _segments_path, _corners_path

            except Exception as e:
                print(f"Segmente und Corners konnten nicht geladen werden! {e}")
                return ""

        try:
            segments_path, corners_path = _get_file_paths(track)
            segments_df, corners_df  = self._load_map(segments_path, corners_path)

            _telemetry_df = pd.read_csv(file_path, skiprows=14).drop(0)
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
                right_on="cornerStart_m",
                direction="backward"
            )

            self.telemetry_lap_df = full_telemetry_df

            return full_telemetry_df

        except Exception as e:
            print(f"load_from_csv[ERROR]: {e}")
            return None

    def _load_map(self, file_path_segments, file_path_corners) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Loads the segments- and corners-JSON to a DataFrame and returns it as a tuple
        :param file_path_segments:
        :param file_path_corners:
        :return: segments_df, corners_df
        """
        with open(file_path_segments, "r") as f:
            segments = json.load(f)
        with open(file_path_corners, "r") as f:
            corners = json.load(f)

        corners_df = pd.json_normalize(corners["corners"])
        corners_df_sorted = corners_df.sort_values('cornerStart_m')

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

    motec = MoTec()
    user_df = motec.telemetry_from_csv(file_path_user, "spa")
    record_df = motec.telemetry_from_csv(file_path_fastest_lap, "spa")

    record_df.to_csv("record_telemetry.csv", index=False, encoding="utf-8")
    user_df.to_csv("user_telemetry.csv", index=False, encoding="utf-8")

    print(user_df.info())
