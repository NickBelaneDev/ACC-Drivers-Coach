# Analyzer for the complete Brake Data
import pandas as pd
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_df_from_area
from src.lap.lap_dataclasses import BrakeMetrics, TrailBrakeMetrics


class BrakeAnalyzer:
    """
    Analyzes braking behavior throughout a corner and transition phases.

    The ``BrakeAnalyzer`` identifies braking phases within the telemetry data,
    including the main braking event, the brake release phase, and potential
    trail braking zones (where braking continues deep into the corner while steering).

    It produces a comprehensive set of braking metrics that describe how, when,
    and how effectively the driver decelerates — including timing, intensity,
    release dynamics, and smoothness. The results are aggregated into
    ``BrakeMetrics`` and ``TrailBrakeMetrics`` dataclasses.
    """

    @staticmethod
    def _trail_brake_zone(df: pd.DataFrame) -> dict | TrailBrakeMetrics:
        """
        Detect and evaluate the trail-braking phase.

        A trail-brake zone is defined as the period where brake pressure is
        being released gradually (brake signal decreasing) while the vehicle
        continues turning. The method quantifies this phase in terms of distance,
        duration, and correlation with rotation (ROTY), as well as smoothness and
        stability of brake release.

        Parameters
        ----------
        df : pandas.DataFrame
            Telemetry data for the braking region of the corner, including
            at least the columns:
            ``["Distance", "BRAKE", "Time", "ROTY", "gForceVector", "SPEED"]``.

        Returns
        -------
        TrailBrakeMetrics
            Dataclass containing trail-brake metrics such as start/end distance,
            speeds, integral brake force, correlation to rotation, and stability.
        """
        cols = ["Distance", "BRAKE", "Time", "ROTY", "gForceVector", "SPEED"]
        trail_brake_window_df = df[(df["BRAKE"].shift(1) > df["BRAKE"])][cols] # This is the DataFrame where the driver is trail braking (releasing the brakes slowly while steering into the corner).
        trail_brake_start_m: int = trail_brake_window_df["Distance"].min()
        trail_brake_start_speed: float = trail_brake_window_df["SPEED"].iloc[0] if not trail_brake_window_df.empty else 0.0
        trail_brake_end_speed_kmh: float = trail_brake_window_df["SPEED"].iloc[-1] if not trail_brake_window_df.empty else 0.0
        trail_brake_end_m: int = trail_brake_window_df["Distance"].max()
        trail_brake_delta_s: float = trail_brake_window_df["Time"].max() - trail_brake_window_df["Time"].min()

        trail_brake_integral: float = TelemetryCalculator.get_integral(trail_brake_window_df, "BRAKE")
        trail_brake_corr_brake_roty: float = TelemetryCalculator.parameter_correlation(trail_brake_window_df, "BRAKE", "ROTY")
        trail_brake_release_rate: float = TelemetryCalculator.average_change_rate(trail_brake_window_df, "BRAKE")
        trail_brake_stability: float = 1 / TelemetryCalculator.change_rate_var(trail_brake_window_df, "BRAKE") # We divide 1 by the change_rate_var to interpret high values as good.


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

    def analyze(self, telemetry_df: pd.DataFrame,
                brake_threshold:int=2) \
            -> BrakeMetrics:
        """
        Perform a complete braking-phase analysis from telemetry data.

        This method identifies key braking events (initial brake, release point,
        and trail braking) within the telemetry DataFrame and computes a set of
        quantitative metrics describing braking performance, timing, and dynamics.

        Parameters
        ----------
        telemetry_df : pandas.DataFrame
            Raw telemetry DataFrame containing the full corner range. Must include
            braking, speed, and time data (and their associated distances).
        brake_threshold : int, optional
            Minimum brake value (in %) to be considered "braking". Defaults to 2.

        Returns
        -------
        BrakeMetrics
            Dataclass summarizing braking performance, including:
            - brake onset and release points (distance & time),
            - maximum and average brake values,
            - braking duration and total brake force,
            - trail-brake metrics (if detected).

        Notes
        -----
        - The braking zone is currently defined as the first point where
          brake input exceeds the ``brake_threshold``.
        - The method also calls ``_trail_brake_zone`` to evaluate
          extended braking during corner entry.
        """
        brake_area_start_m = telemetry_df["brakeArea_m"].min()
        brake_area_end_m = telemetry_df["cornerApex_m"].iloc[0]

        cols = ["SPEED", "BRAKE", "G_LAT", "G_LON", "STEERANGLE", "Time", "gForceVector", "ROTY"] # 'Distance' is by default in the get_df_from_area() function

        brake_df = get_df_from_area(brake_area_start_m, brake_area_end_m, cols, telemetry_df)

        def _find_braking_window() -> pd.DataFrame:
            """
            Identify the braking window where the driver transitions from
            not braking to active braking (based on a given threshold).
            """
            # TODO: Write a safe version of the function!
            # FIXME: Currently the braking window is only the braking point... You get the point...
            was_not_braking = brake_df["BRAKE"].shift(1).fillna(0) < brake_threshold
            is_braking = brake_df["BRAKE"] >= brake_threshold
            _braking_zone_df = brake_df[is_braking & was_not_braking] # This is the area where the car is under braking
            return (
                _braking_zone_df
                if not _braking_zone_df.empty
                else pd.DataFrame
            )

        braking_zone_df = _find_braking_window()
        if braking_zone_df.empty:
            return BrakeMetrics.empty("no-brake-point-detected")

        brake_point_m = braking_zone_df["Distance"].min()  # this is only a row and we need the lowest "Distance"
        brake_point_s = braking_zone_df.loc[braking_zone_df["Distance"].idxmin(), "Time"]

        def _calc_brake_release_point() -> tuple:
            """
            Detect when the driver fully releases the brakes (BRAKE == 0 after being >0).
            Returns the distance and time of full release.
            """
            # Calculate the point where the driver is completely off the brakes
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

        # --- Core metrics
        brake_delta_s = brake_release_s - brake_point_s
        brake_point_speed = braking_zone_df["SPEED"].iloc[0]
        brake_release_speed = brake_df[brake_df["Distance"] == brake_release_m]["SPEED"].min()
        max_brake = brake_df["BRAKE"].max()
        avg_brake = brake_df[(brake_df["Distance"] >= brake_point_m) &
                             (brake_df["Distance"] <= brake_release_m)]["BRAKE"].mean()  # soll vom Bremspunkt des Fahrers bis zum kompletten Release gehen.

        # --- Sub-analyses
        trail_brake_metrics = self._trail_brake_zone(brake_df)
        overall_brake_force = TelemetryCalculator.get_integral(brake_df, "BRAKE")

        # Time to reach full braking (95%)
        tbf95_s = brake_df[brake_df["BRAKE"] >= 95]["Time"].max() - brake_df[brake_df["BRAKE"] >= 95]["Time"].min()

        return BrakeMetrics(
            brake_point_m=brake_point_m,
            brake_point_speed=brake_point_speed,
            brake_release_m=brake_release_m,
            brake_release_speed=brake_release_speed,
            brake_window_s=brake_delta_s,
            max_brake=max_brake,
            avg_brake=avg_brake,
            overall_brake_force=overall_brake_force,
            tbf95_s=tbf95_s,
            trail_brake=trail_brake_metrics,
        )

