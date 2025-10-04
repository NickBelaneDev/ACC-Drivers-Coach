# Was ist ausschlaggebend über die Brems-skills eines Fahrers?

# ========== Positive Faktoren ===================
# - Hohe Brakeforce (Integral des Bremsverlaufs)
# - Später Bremspunkt
# - Stabilität des Fahrzeugs, während des Bremsens
# - Rotation durch das Lösen der Bremse in Kombination mit steigendem Lenkwinkel -> Der gForceVector sollte ab Beginn des Lenkeinschlags möglichst konstant sein (keine große Standardabweichung)
#       - Korrelation zwischen Bremse und Rotation ist interessant zur Auswertung des Trailbrakings
#
from src.logger import get_logger
from src.lap.analyzer.brake_analyzer import BrakeAnalyzer

import pandas as pd
import numpy as np

from src.telemetry.telemetry_calculator import TelemetryCalculator
log = get_logger(to_console=False, log_file="brake_score_log.log", level="DEBUG")

class BrakeScore:
    def __init__(self, df: pd.DataFrame):
        """df is a DataFrame where the car is under braking"""
        self.df: pd.DataFrame = df #df[["Distance", "BRAKE", "STEERANGLE", "G_LAT", "gForceVector", "ROTY", "SPEED"]].sort_values("Distance").copy()
        self._analysis = BrakeAnalyzer(df)


    def calculate(self) -> float:
        braking_mask = self.df["BRAKE"].fillna(0) > 2
        if not braking_mask.any():
            return 0.0

        raw_brake_df = self.df[braking_mask]
        #print(f"{raw_brake_df["BRAKE"]}")
        brake_data = self._analysis.analyze(self.df)
        """
        delta_v = max(brake_data.brake_point_speed - brake_data.brake_release_speed, 0.0)
        brake_efficiency = delta_v / max(brake_data.overall_brake_force, 1e-6)

        def safe_smooth(col):
            val = TelemetryCalculator.parameter_smoothness(self.df, col)
            return 0.0 if pd.isna(val) else float(val)

        brake_smoothness = safe_smooth("BRAKE")
        steer_smoothness = safe_smooth("STEERANGLE")
        roty_smoothness = safe_smooth("ROTY")
        g_force_v_smoothness = safe_smooth("gForceVector")


        brake_roty_corr = brake_data.trail_brake.corr_brake_roty
        brake_point_speed_kmh = brake_data.brake_point_speed
        brake_release_speed_kmh = brake_data.brake_release_speed

        g_force_q95 = TelemetryCalculator.quantile(raw_brake_df, "gForceVector")

        log.debug({
            "brake_smoothness": brake_smoothness,
            "steer_smoothness": steer_smoothness,
            "roty_smoothness": roty_smoothness,
            "g_force_v_smoothness": g_force_v_smoothness,
            "brake_roty_corr": brake_roty_corr,
            "brake_efficiency": brake_efficiency,
            "g_force_q95": g_force_q95
        })

        base_quality = (

            0.4 * steer_smoothness +
            0.4 * roty_smoothness +
            0.7 * max(brake_roty_corr, 0.0) +
            0.4 * brake_smoothness +
            0.01 * g_force_v_smoothness
        )
        print(f"{brake_data.overall_brake_force=}")
        #print(f"{base_quality=}")
        score = brake_point_speed_kmh*(base_quality/100) * np.sqrt(max(brake_data.brake_force_per_second, 0.0))
        """
        score = np.sqrt(brake_data.brake_force_per_meter + brake_data.brake_force_per_second)
        if pd.isna(score) or np.isinf(score):
            return 0.0
        return round(score, 4)

