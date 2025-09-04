import pandas as pd
import numpy as np
from lap_dataclasses import Corner, CornerMetrics, SegmentMetrics, Segment
from src.lap_analyzer import LapAnalyzer



# LapCompare bekommt zwei DFs der ganzen Lap und vergleicht die Analysedaten der Kurven und Segmente.
#
# Was für Werte wollen wir haben?
#
# 1.) TelemetryLoader


class LapCompare:

    def __init__(self, lap: pd.DataFrame):
        self.lap = lap
        self.analyzer = LapAnalyzer()

    def _load_corners(self):


        pass

    def get_comparison_df(self, df):
        pass

    def get_comparison_json(self, df):
        pass