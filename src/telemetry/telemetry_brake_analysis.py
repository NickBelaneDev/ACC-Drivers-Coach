# Analyzer for the complete Brake Data
import pandas as pd
import numpy as np
from .telemetry_calculator import TelemetryCalculator
from .telemetry_utils import get_df_from_area
from src.lap.lap_dataclasses import BrakeMetrics


class BrakeAnalysis:
    def __init__(self, df: pd.DataFrame):
        self.lap_df = df
    @staticmethod
    def _trail_brake_delta(df: pd.DataFrame) -> dict:
        """
        Indicates an area where the driver is braking less than the threshold parameter while steering in a single direction.

        :param df:

        :return: trail_brake_delta_s, trail_brake_delta_m
        """

        delta_df = df[(df["BRAKE"].shift(1) > df["BRAKE"])]
        trail_brake_start_m = delta_df["Distance"].min()
        trail_brake_end_m = delta_df["Distance"].max()
        trail_brake_delta_m = trail_brake_end_m - trail_brake_start_m
        trail_brake_delta_s = delta_df["Time"].max() - delta_df["Time"].min()

        trail_brake_dict = {
            "trail_brake_start_m": trail_brake_start_m,
            "trail_brake_end_m": trail_brake_end_m,
            "trail_brake_delta_m": trail_brake_delta_m,
            "trail_brake_delta_s": trail_brake_delta_s,
        }

        return trail_brake_dict

    def get_brake_data(self, telemetry_df: pd.DataFrame, threshold:int=2, as_dict:bool=True) -> dict | BrakeMetrics | None:
        """
        ACHTUNG! Noch muss geprüft werden, ob es überhaupt einen Bremspunkt gibt!
        :param telemetry_df:
        :param threshold:
        :param as_dict:
        :return:
        """

        #print(telemetry_df.info())
        brake_area_start_m = telemetry_df["brakeArea_m"].min()
        brake_area_end_m = telemetry_df["cornerApex_m"].iloc[0]

        # "Distance" is always added in get_data_from_area!!
        cols = ["SPEED", "BRAKE", "G_LAT", "G_LON", "STEERANGLE", "Time"]

        brake_df = get_df_from_area(brake_area_start_m, brake_area_end_m, cols, telemetry_df)

        was_not_braking = brake_df["BRAKE"].shift(1).fillna(0) < threshold
        is_braking = brake_df["BRAKE"] >= threshold

        # This DataFrame is
        _brake_delta_df = brake_df[is_braking & was_not_braking] # This is the area where the car is under braking
        if _brake_delta_df.empty:
            return {"brake_point_m": 0, "brake_delta_m": 0, "brake_delta_s": 0.0,
                    "brake_release_m": 0, "avg_brake": 0, "max_brake": 0, "trail_brake_delta_m": 0,
                    "trail_brake_delta_s": 0, "trail_brake_start_m": 0, "trail_brake_end_m": 0,
                    "overall_brake_force": 0, "tbf95": 0}

        # The brake point has been validated
        brake_point_m = _brake_delta_df["Distance"].min()  # this is only a row and we need the lowest "Distance"
        brake_point_s = _brake_delta_df.loc[_brake_delta_df["Distance"].idxmin(), "Time"]

        # Calculate the brake release
        release_mask = (brake_df["BRAKE"].shift(1).fillna(0) >= 1) & (brake_df["BRAKE"] == 0)
        release_rows = brake_df[release_mask]
        # -> Validation of the _brake_delta_df
        if release_rows.empty:
            brake_release_m = brake_df["Distance"].max()
            brake_release_s = brake_df.loc[brake_df["Distance"].idxmax(), "Time"]
        else:
            brake_release_m = release_rows["Distance"].max()
            brake_release_s = release_rows.loc[release_rows["Distance"].idxmax(), "Time"]

        if pd.isna(brake_point_m) or pd.isna(brake_release_m):
            return {"brake_point_m": 0, "brake_delta_m": 0, "brake_delta_s": 0.0,
                    "brake_release_m": 0, "avg_brake": 0, "max_brake": 0, "trail_brake_delta_m": 0,
                    "trail_brake_delta_s": 0, "trail_brake_start_m": 0, "trail_brake_end_m": 0,
                    "overall_brake_force": 0, "tbf95": 0}

        # The _brake_delta_df is validated!
        # Set final variables
        brake_delta_m = brake_release_m - brake_point_m
        brake_delta_s = brake_release_s - brake_point_s

        brake_point_speed = _brake_delta_df["SPEED"].iloc[0]
        brake_release_speed = _brake_delta_df["SPEED"].iloc[-1]

        max_brake = brake_df["BRAKE"].max()
        avg_brake = brake_df[(brake_df["Distance"] >= brake_point_m) & (brake_df["Distance"] <= brake_release_m)][
            "BRAKE"].mean()  # soll vom Bremspunkt des Fahrers bis zum kompletten Release gehen.

        # Trail Brake Data collect
        _trail_brake_data = self._trail_brake_delta(brake_df)

        trail_brake_delta_s = _trail_brake_data["trail_brake_delta_s"]
        trail_brake_delta_m = _trail_brake_data["trail_brake_delta_m"]
        trail_brake_start_m = _trail_brake_data["trail_brake_start_m"]
        trail_brake_end_m = _trail_brake_data["trail_brake_end_m"]

        # Advanced Brake Data
        overall_brake_force = TelemetryCalculator.get_integral(brake_df, "BRAKE")
        brake_force_per_meter = overall_brake_force / brake_delta_m
        brake_force_per_second = overall_brake_force / brake_delta_s

        tbf95_s = brake_df[brake_df["BRAKE"] >= 95]["Time"].max() - brake_df[brake_df["BRAKE"] >= 95]["Time"].min()

        if as_dict:
            return {"brake_point_m": brake_point_m,
                    "brake_point_speed": brake_point_speed,
                    "brake_delta_m": brake_delta_m,
                    "brake_release_m": brake_release_m,
                    "brake_release_speed": brake_release_speed,
                    "brake_delta_s": brake_delta_s,
                    "max_brake": max_brake,
                    "avg_brake": avg_brake,
                    "trail_brake_delta_m": trail_brake_delta_m,
                    "trail_brake_delta_s": trail_brake_delta_s,
                    "trail_brake_start_m": trail_brake_start_m,
                    "trail_brake_end_m": trail_brake_end_m,
                    "overall_brake_force": overall_brake_force,
                    "brake_force_per_meter": brake_force_per_meter,
                    "brake_force_per_second": brake_force_per_second,
                    "tbf95": tbf95_s}

        else:
            return BrakeMetrics(
                brake_point_m=brake_point_m,
                brake_point_speed=brake_point_speed,
                brake_delta_m=brake_delta_m,
                brake_release_m=brake_release_m,
                brake_release_speed=brake_release_speed,
                brake_delta_s=brake_delta_s,
                max_brake=max_brake,
                avg_brake=avg_brake,
                trail_brake_delta_m=trail_brake_delta_m,
                trail_brake_delta_s=trail_brake_delta_s,
                trail_brake_start_m=trail_brake_start_m,
                trail_brake_end_m=trail_brake_end_m,
                overall_brake_force=overall_brake_force,
                brake_force_per_meter=brake_force_per_meter,
                brake_force_per_second=brake_force_per_second,
                tbf95_s=tbf95_s
            )