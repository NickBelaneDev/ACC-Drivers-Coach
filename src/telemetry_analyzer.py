from lap_dataclasses import Corner, CornerMetrics
import pandas as pd
import numpy as np
from logger import get_logger

log = get_logger("telemetry_analyzer", to_console=False)

class Analyze:
    def __init__(self, df: pd.DataFrame):
        self.corner_metrics = CornerMetrics
        self.lap_df = df

    def _get_df_from_corner(self, corner: Corner) -> pd.DataFrame:
        _start = Corner.start_m
        _end = Corner.end_m

        corner_df = self.lap_df[(self.lap_df["Distance"] >= _start) & (self.lap_df["Distance"] <= _end)]

        if corner_df.empty:
            return pd.DataFrame()

        return corner_df

    def get_time_delta(self,start_m: int, end_m: int):
        time_start_df =  self.lap_df[self.lap_df["Distance"] == start_m]
        time_start = time_start_df["Time"].iloc[0]

        time_end_df = self.lap_df[self.lap_df["Distance"] == end_m]
        time_end = time_end_df["Time"].iloc[0]

        return time_end - time_start

    def get_brakepoints(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
        was_not_braking = telemetry_df["BRAKE"].shift(1) < 99
        is_braking = telemetry_df["BRAKE"] >= 99

        brake_point_df = telemetry_df[is_braking & was_not_braking]

        return brake_point_df

    def _get_brakepoints(self, telemetry_df: pd.DataFrame) -> dict | None:
        brake_point_m = 0
        brake_delta_m = 0
        brake_delta_s = 0

        return {"brake_point_m": brake_point_m,
                "brake_delta_m": brake_delta_m,
                "brake_delta_s": brake_delta_s,
                "tbf95": 0}

    def _get_throttle_data(self, telemetry_df: pd.DataFrame) -> pd.DataFrame | None:
        ttf95_s = 0
        exit_throttle_init_m = 0
        avg_exit_throttle = 0
        exit_speed_delta_s = 0
        return {
            "ttf95_s": 0,
            "exit_throttle_init_m": 0,
            "avg_exit_throttle": 0,
            "exit_speed_delta_s": 0
        }

    def get_break_point_difference(self, break_points_01_df: pd.DataFrame, break_points_02_df: pd.DataFrame) -> pd.DataFrame:
        u_b_p = self.get_brakepoints(break_points_01_df)
        r_b_p = self.get_brakepoints(break_points_02_df)

        user_break_points = u_b_p.reset_index(drop=True)
        record_break_points = r_b_p.reset_index(drop=True)

        difference_df = user_break_points["Distance"] - record_break_points["Distance"]
        return difference_df

    @staticmethod
    def get_apex_df(telemetry_df: pd.DataFrame):
        is_accelerating = telemetry_df["SPEED"].shift(1) > telemetry_df["SPEED"]
        is_slowing_down = telemetry_df["SPEED"].shift(-1) > telemetry_df["SPEED"]
        is_steering = telemetry_df["STEERING"].shift(1) > telemetry_df["STEERING"]

        apex_df = telemetry_df[is_accelerating & is_slowing_down]

        return apex_df

    @staticmethod
    def _trail_brake_delta(df: pd.DataFrame, threshold: int=15) -> tuple[float, float]:
        # Brake Input muss niedriger als Schwellwert sein
        delta_df = df[(df["BRAKE"].shift(1) > 0) & (df["BRAKE"].shift(1) < threshold) & (df["BRAKE"].shift(-1) > 0) & (df["BRAKE"].shift(-1) < threshold)]
        trail_brake_start = delta_df["Distance"].min()
        trail_brake_end = delta_df["Distance"].max()
        trail_brake_delta_m = trail_brake_end - trail_brake_start
        trail_brake_delta_s = delta_df["Time"].max() - delta_df["Time"].min()

        return trail_brake_delta_s, trail_brake_delta_m

    def corner(self, corner_df: pd.DataFrame) -> Corner:
        c = Corner

        c.name = corner_df["cornerName"].iloc[0]
        c.id = corner_df["corner_id"].iloc[0]
        c.start_m = corner_df["cornerEnd_m"].iloc[0]
        c.apex_m = corner_df["cornerApex_m"].iloc[0]
        c.end_m = corner_df["cornerStart_m"].iloc[0]

        cm = CornerMetrics
        # Speed Measurements
        cm.time_delta_s = self.get_time_delta(int(c.start_m), int(c.end_m))

        cm.entry_speed_kmh = corner_df["SPEED"].iloc[0]
        cm.exit_speed_kmh = corner_df["SPEED"].iloc[1]
        cm.apex_speed_kmh = corner_df[corner_df["Distance"] == c.apex_m]["SPEED"].mean()
        cm.avg_speed_kmh = corner_df["SPEED"].mean()
        cm.max_speed_kmh = corner_df["SPEED"].max()
        cm.min_speed_kmh = corner_df["SPEED"].min()
        cm.min_speed_m = corner_df[corner_df["SPEED"] == cm.min_speed_kmh]["Distance"].mean()

        # G-Forces
        cm.g_lat_avg = corner_df["G_LAT"].mean()
        cm.g_lat_max = corner_df["G_LAT"].max()
        cm.g_lat_min = corner_df["G_LAT"].min()
        cm.g_lon_avg = corner_df["G_LON"].mean()
        cm.g_lon_max = corner_df["G_LON"].max()
        cm.g_lon_min = corner_df["G_LON"].min()

        # Driver's Input
        # - Steering
        cm.avg_steerangle = corner_df["STEERANGLE"].mean()
        cm.max_steerangle = corner_df["STEERANGLE"].max()
        cm.max_steerangle_m = corner_df[corner_df["STEERANGLE"] == cm.max_steerangle]["Distance"].mean()

        # - Brake
        cm.avg_brake = corner_df["BRAKE"].mean()
        cm.max_brake = corner_df["BRAKE"].max()

        _advanced_brake_data = self._get_brakepoints(corner_df)
        cm.brake_point_m = _advanced_brake_data["brake_point_m"]
        cm.brake_delta_m = _advanced_brake_data["brake_delta_m"]
        cm.brake_delta_s = _advanced_brake_data["brake_delta_s"]
        cm.tbf95_s = _advanced_brake_data["tbf95"]

        _trail_brake_delta = self._trail_brake_delta(corner_df)
        cm.trail_brake_delta_s = _trail_brake_delta[0]
        cm.trail_brake_delta_m = _trail_brake_delta[1]

        # - Throttle
        cm.avg_throttle = corner_df["THROTTLE"].mean()

        _advanced_throttle_data = self._get_throttle_data(corner_df)
        cm.ttf95_s = _advanced_throttle_data["ttf95_s"]
        cm.exit_throttle_init_m = _advanced_throttle_data["exit_throttle_init_m"]
        cm.avg_exit_throttle = _advanced_throttle_data["avg_exit_throttle"]
        cm.exit_speed_delta_s = _advanced_throttle_data["exit_speed_delta_s"]

        # - Rolling
        is_rolling = corner_df[(corner_df["THROTTLE"] == 0) & (corner_df["BRAKE"] == 0)]
        cm.rolling_delta_m = is_rolling["Distance"].max() - is_rolling["Distance"].min()
        cm.rolling_delta_s = is_rolling["Time"].max() - is_rolling["Time"].min()

        c.metrics = cm
        #print(self.corner_metrics.max_brake)
        return c