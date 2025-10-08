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
        score = np.sqrt(brake_data.brake_force_per_meter + brake_data.brake_force_per_second)
        if pd.isna(score) or np.isinf(score):
            return 0.0
        return round(score, 4)

