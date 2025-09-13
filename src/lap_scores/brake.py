# Was ist ausschlaggebend über die Brems-skills eines Fahrers?

# ========== Positive Faktoren ===================
# - Hohe Brakeforce (Integral des Bremsverlaufs)
# - Später Bremspunkt
# - Stabilität des Fahrzeugs, während des Bremsens
# - Rotation durch das Lösen der Bremse in Kombination mit steigendem Lenkwinkel -> Der gForceVector sollte ab Beginn des Lenkeinschlags möglichst konstant sein (keine große Standardabweichung)
#       - Korrelation zwischen Bremse und Rotation ist interessant zur Auswertung des Trailbrakings
#
from src.logger import get_logger
from src.telemetry.telemetry_utils import sigmoid


import pandas as pd
import numpy as np

from src.telemetry.telemetry_calculator import TelemetryCalculator


class BrakeScore:
    def __init__(self, df: pd.DataFrame):
        self.df = df[["Distance", "BRAKE", "STEER", "G_LAT", "gForceVector", "ROTY"]]
        self.brake_score = self.calculate()


    def calculate(self):
        brake_force = sigmoid(TelemetryCalculator.get_integral(self.df, "BRAKE"))

        brake_smoothness = sigmoid(TelemetryCalculator.parameter_smoothness(self.df, "BRAKE"))
        steer_smoothness = sigmoid(TelemetryCalculator.parameter_smoothness(self.df, "STEER"))
        roty_smoothness = sigmoid(TelemetryCalculator.parameter_smoothness(self.df, "ROTY"))
        g_force_v_smoothness = sigmoid(TelemetryCalculator.parameter_smoothness(self.df, "gForceVector"))

        brake_roty_corr = sigmoid(TelemetryCalculator.parameter_correlation(self.df, "ROTY", "BRAKE"))

