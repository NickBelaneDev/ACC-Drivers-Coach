# Was ist ausschlaggebend über die Brems-skills eines Fahrers?

# ========== Positive Faktoren ===================
# - Hohe Brakeforce (Integral des Bremsverlaufs)
# - Später Bremspunkt
# - Stabilität des Fahrzeugs, während des Bremsens
# - Rotation durch das Lösen der Bremse in Kombination mit steigendem Lenkwinkel -> Der gForceVector sollte ab Beginn des Lenkeinschlags möglichst konstant sein (keine große Standardabweichung)
#       - Korrelation zwischen Bremse und Rotation ist interessant zur Auswertung des Trailbrakings
#
from src.logger import get_logger
from src.lap.analyzer.brake_analysis import BrakeAnalysis

import pandas as pd
import numpy as np

from src.telemetry.telemetry_calculator import TelemetryCalculator
log = get_logger(to_console=False, log_file="brake_score_log.log")

class BrakeScore:
    def __init__(self, df: pd.DataFrame):
        """df is a DataFrame where the car is under braking"""
        self.df: pd.DataFrame = df #df[["Distance", "BRAKE", "STEERANGLE", "G_LAT", "gForceVector", "ROTY", "SPEED"]].sort_values("Distance").copy()
        self._analysis = BrakeAnalysis(df)


    def calculate(self):
        braking_mask = self.df["BRAKE"].fillna(0) > 2
        if not braking_mask.any():
            return 0.0

        brake_data = self._analysis.get_brake_data(self.df, as_dict=False)

        delta_v = max(brake_data.brake_point_speed - brake_data.brake_release_speed, 0.0)
        brake_efficiency = delta_v / max(brake_data.overall_brake_force, 1e-6)

        def safe_smooth(col):
            val = TelemetryCalculator.parameter_smoothness(self.df, col)
            return 0.0 if pd.isna(val) else float(val)

        brake_smoothness = safe_smooth("BRAKE")
        steer_smoothness = safe_smooth("STEERANGLE")
        roty_smoothness = safe_smooth("ROTY")
        g_force_v_smoothness = safe_smooth("gForceVector")

        brake_roty_corr = TelemetryCalculator.parameter_correlation(self.df, "ROTY", "BRAKE")

        log.debug({
            "brake_smoothness": brake_smoothness,
            "steer_smoothness": steer_smoothness,
            "roty_smoothness": roty_smoothness,
            "g_force_v_smoothness": g_force_v_smoothness,
            "brake_roty_corr": brake_roty_corr,
            "brake_efficiency": brake_efficiency
        })

        base_quality = (
            0.3 * g_force_v_smoothness +
            0.1 * steer_smoothness +
            0.1 * roty_smoothness +
            0.15 * max(brake_roty_corr, 0.0) +
            0.5 * brake_efficiency +
            0.2 * brake_smoothness
        )
        log.debug(f"{base_quality=}")
        score = base_quality * np.sqrt(max(brake_data.brake_force_per_meter, 0.0))

        if pd.isna(score) or np.isinf(score):
            return 0.0
        return round(score, 4)



"""
is_braking = self.df[self.df["BRAKE"] > 2]

brake_distance = float(is_braking["Distance"].max() - is_braking["Distance"].min())
print(f"Brake_distance: {is_braking}")
entry_speed = float(self.df["SPEED"].iloc[0]) if "SPEED" in self.df else 0.0
apex_speed = float(self.df.loc[self.df["SPEED"].idxmin(), "SPEED" ]) if "SPEED" in self.df else entry_speed

brake_force = TelemetryCalculator.get_integral(is_braking, "BRAKE")
brake_force_per_meter = brake_force / max(brake_distance, 1e-6)"""