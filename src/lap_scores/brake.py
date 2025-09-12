# Was ist ausschlaggebend über die Brems-skills eines Fahrers?

# ========== Positive Faktoren ===================
# - Hohe Brakeforce (Integral des Bremsverlaufs)
# - Später Bremspunkt
# - Stabilität des Fahrzeugs, während des Bremsens
# - Rotation durch das Lösen der Bremse in Kombination mit steigendem Lenkwinkel -> Der gForceVector sollte ab Beginn des Lenkeinschlags möglichst konstant sein (keine große Standardabweichung)
#       - Korrelation zwischen Bremse und Rotation ist interessant zur Auswertung des Trailbrakings
#



import pandas as pd
import numpy as np

from src.telemetry.telemetry_calculator import TelemetryCalculator


class BrakeScore:
    def __init__(self, df: pd.DataFrame):
        self.df = df[["Distance", "BRAKE", "STEER", "G_LAT", "gForceVector", "ROTY"]]
        self.brake_score = self.calculate()


    def calculate(self):
        brake_force = TelemetryCalculator.get_integral(self.df, "BRAKE")

        brake_smoothness = TelemetryCalculator.parameter_smoothness(self.df, "BRAKE")
        steer_smoothness = TelemetryCalculator.parameter_smoothness(self.df, "STEER")
        roty_smoothness = TelemetryCalculator.parameter_smoothness(self.df, "ROTY")
        g_force_v_smoothness = TelemetryCalculator.parameter_smoothness(self.df, "gForceVector")

        brake_roty_corr = TelemetryCalculator.parameter_correlation(self.df, "ROTY", "BRAKE")

