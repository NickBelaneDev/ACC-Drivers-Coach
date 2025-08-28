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

    def delta_m(self, a, b) -> float:

        return b-a


    def get_break_points(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
        was_not_braking = telemetry_df["BRAKE"].shift(1) < 99
        is_braking = telemetry_df["BRAKE"] >= 70

        brake_point_df = telemetry_df[is_braking & was_not_braking]

        return brake_point_df

    def get_break_point_difference(self, break_points_01_df: pd.DataFrame, break_points_02_df: pd.DataFrame) -> pd.DataFrame:
        u_b_p = self.get_break_points(break_points_01_df)
        r_b_p = self.get_break_points(break_points_02_df)

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

    def corner(self, corner_df: pd.DataFrame):
        c = Corner
        c.name = corner_df["cornerName"].iloc[0]
        c.id = corner_df["corner_id"]
        c.start_m = corner_df["cornerEnd_m"].iloc[0]
        c.apex_m = corner_df["cornerApex_m"].iloc[0]
        c.end_m = corner_df["cornerStart_m"].iloc[0]

        cm = CornerMetrics
        # Speed Measurements
        cm.time_delta_s = self.get_time_delta(int(c.start_m), int(c.end_m))

        cm.entry_speed_kmh = corner_df["SPEED"].iloc[0]
        cm.exit_speed_kmh = corner_df["SPEED"].iloc[1]
        cm.apex_speed_kmh = corner_df[corner_df["Distance"] == c.apex_m]["SPEED"]
        cm.avg_speed_kmh = corner_df["SPEED"].mean()
        cm.max_speed_kmh = corner_df["SPEED"].max()
        cm.min_speed_kmh = corner_df["SPEED"].min()
        cm.min_speed_m = corner_df[corner_df["SPEED"] == cm.min_speed_kmh]["Distance"]

        # G-Forces
        cm.g_lat_avg = corner_df["G_LAT"].mean()
        cm.g_lat_max = corner_df["G_LAT"].max()
        cm.g_lat_min = corner_df["G_LAT"].min()
        cm.g_long_avg = corner_df["G_LONG"].mean()
        cm.g_long_max = corner_df["G_LONG"].max()
        cm.g_long_min = corner_df["G_LONG"].min()

        # Driver's Input
        cm.avg_steerangle = corner_df["STEERANGLE"].mean()
        cm.max_steerangle = corner_df["STEERANGLE"].max()
        cm.max_steerangle_m = corner_df[corner_df["STEERANGLE"] == cm.max_steerangle]["Distance"]

        cm.avg_brake = corner_df["BRAKE"].mean()
        cm.max_brake = corner_df["BRAKE"].max()

        cm.avg_throttle = corner_df["THROTTLE"].mean()

        _trail_brake_delta = self._trail_brake_delta(corner_df)
        cm.trail_brake_delta_s = _trail_brake_delta[0]
        cm.trail_brake_delta_m = _trail_brake_delta[1]

        _break_point = self.get_breakpoint(c)

        c.corner_metrics = cm
        print("--> corner_metrics")
        #print(self.corner_metrics.max_brake)
        return c