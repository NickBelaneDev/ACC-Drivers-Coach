# Analyzer for the complete Brake Data
import pandas as pd
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_df_from_area
from src.lap.lap_dataclasses import BrakeMetrics, TrailBrakeMetrics


class BrakeAnalyzer:
    @staticmethod
    def _trail_brake_zone(df: pd.DataFrame) -> dict | TrailBrakeMetrics:
        """
        Indicates an area where the driver is braking less than the threshold parameter while steering in a single direction.

        :param df:

        :return: trail_brake_dict
        """

        delta_df = df[(df["BRAKE"].shift(1) > df["BRAKE"])][["Distance", "BRAKE", "Time", "ROTY", "gForceVector", "SPEED"]] # This is the DataFrame where the driver is trail braking (releasing the brakes slowly while steering into the corner).
        trail_brake_start_m: int = delta_df["Distance"].min()
        trail_brake_start_speed: float = delta_df["SPEED"].iloc[0] if not delta_df.empty else 0.0
        trail_brake_end_speed_kmh: float = delta_df["SPEED"].iloc[-1] if not delta_df.empty else 0.0
        trail_brake_end_m: int = delta_df["Distance"].max()
        trail_brake_delta_s: float = delta_df["Time"].max() - delta_df["Time"].min()

        trail_brake_integral: float = TelemetryCalculator.get_integral(delta_df, "BRAKE")
        trail_brake_corr_brake_roty: float = TelemetryCalculator.parameter_correlation(delta_df, "BRAKE", "ROTY")
        trail_brake_release_rate: float = TelemetryCalculator.average_change_rate(delta_df, "BRAKE")
        trail_brake_stability: float = TelemetryCalculator.parameter_stability(delta_df, "BRAKE") # + TelemetryCalculator.parameter_smoothness(delta_df, "gForceVector")


        return TrailBrakeMetrics(
            start_m=trail_brake_start_m,
            end_m=trail_brake_end_m,
            start_speed_kmh=trail_brake_start_speed,
            end_speed_kmh=trail_brake_end_speed_kmh,
            delta_s=trail_brake_delta_s,
            integral=trail_brake_integral,
            corr_brake_roty=trail_brake_corr_brake_roty,
            release_rate=trail_brake_release_rate,
            stability=trail_brake_stability
        )

    def analyze(self, telemetry_df: pd.DataFrame, threshold:int=2) -> BrakeMetrics:
        brake_area_start_m = telemetry_df["brakeArea_m"].min()
        brake_area_end_m = telemetry_df["cornerApex_m"].iloc[0]

        cols = ["SPEED", "BRAKE", "G_LAT", "G_LON", "STEERANGLE", "Time", "gForceVector", "ROTY"] # 'Distance' is by default in the get_df_from_area() function

        brake_df = get_df_from_area(brake_area_start_m, brake_area_end_m, cols, telemetry_df)

        def _find_braking_window() -> pd.DataFrame:
            # TODO: Write a safe version of the function!
            # FIXME: Currently the braking window is only the braking point... You get the point...
            was_not_braking = brake_df["BRAKE"].shift(1).fillna(0) < threshold
            is_braking = brake_df["BRAKE"] >= threshold
            _braking_zone_df = brake_df[is_braking & was_not_braking] # This is the area where the car is under braking
            return _braking_zone_df if not _braking_zone_df.empty else pd.DataFrame

        braking_zone_df = _find_braking_window()
        if braking_zone_df.empty:
            return BrakeMetrics.empty("no-brake-point-detected")

        brake_point_m = braking_zone_df["Distance"].min()  # this is only a row and we need the lowest "Distance"
        brake_point_s = braking_zone_df.loc[braking_zone_df["Distance"].idxmin(), "Time"]

        def _calc_brake_release_point() -> tuple:
            """
            This is the point, where the brake is fully released and standing. mask(n=0 while n-1>=1)
            :return:
            """
            # Calculate the brake release
            _brake_release_mask = (brake_df["BRAKE"].shift(1).fillna(0) >= 1) & (brake_df["BRAKE"] == 0)
            _release_rows = brake_df[_brake_release_mask]

            # -> Validation of the _brake_delta_df
            if _release_rows.empty:
                _brake_release_m = brake_df["Distance"].max()
                _brake_release_s = brake_df.loc[brake_df["Distance"].idxmax(), "Time"]
            else:
                _brake_release_m = _release_rows["Distance"].max()
                _brake_release_s = _release_rows.loc[_release_rows["Distance"].idxmax(), "Time"]

            return _brake_release_m, _brake_release_s
        brake_release_m, brake_release_s = _calc_brake_release_point()

        if pd.isna(brake_point_m) or pd.isna(brake_release_m):
            return BrakeMetrics.empty("invalid-brake-interval")

        # The _brake_delta_df is validated!
        # Set final variables
        brake_delta_s = brake_release_s - brake_point_s

        brake_point_speed = braking_zone_df["SPEED"].iloc[0]
        brake_release_speed = brake_df[brake_df["Distance"] == brake_release_m]["SPEED"].min()

        max_brake = brake_df["BRAKE"].max()
        avg_brake = brake_df[(brake_df["Distance"] >= brake_point_m) & (brake_df["Distance"] <= brake_release_m)][
            "BRAKE"].mean()  # soll vom Bremspunkt des Fahrers bis zum kompletten Release gehen.

        # Trail Brake Data collect
        trail_brake_zone = self._trail_brake_zone(brake_df)

        # Advanced Brake Data
        overall_brake_force = TelemetryCalculator.get_integral(brake_df, "BRAKE")
        tbf95_s = brake_df[brake_df["BRAKE"] >= 95]["Time"].max() - brake_df[brake_df["BRAKE"] >= 95]["Time"].min()

        return BrakeMetrics(
            brake_point_m=brake_point_m,
            brake_point_speed=brake_point_speed,
            brake_release_m=brake_release_m,
            brake_release_speed=brake_release_speed,
            brake_delta_s=brake_delta_s,
            max_brake=max_brake,
            avg_brake=avg_brake,
            overall_brake_force=overall_brake_force,
            tbf95_s=tbf95_s,
            trail_brake=trail_brake_zone,
        )

