import pandas as pd
import math

from src.lap.dataframe_validation import DataFrameValidator, MissingColumnError, EmptyDataFrameError
from ..lap_dataclasses import SpeedMetrics
from ...telemetry.telemetry_calculator import TelemetryCalculator


class SpeedAnalyzer:
    @staticmethod
    def analyze(df: pd.DataFrame) -> SpeedMetrics:
        """
        Analyzes the spe
        :param df:
        :return:
        """

        cols = ["SPEED", "Distance", "cornerStart_m", "cornerApex_m", "cornerEnd_m"]
        try:
            DataFrameValidator.validate_df(df, cols)
        except MissingColumnError as d_c_e:
            return SpeedMetrics.empty(reason=str(d_c_e))
        except EmptyDataFrameError as e_d_e:
            return SpeedMetrics.empty(reason=str(e_d_e))

        # Refactor the DataFrame end exclude unnecessary meta-data.
        speed_df:pd.DataFrame = df[cols].sort_values(by="Distance").copy()
        #speed_df = speed_df.set_index("Distance", drop=False) # For safety reasons we don't drop the 'Distance' col

        speed_s: pd.Series = speed_df["SPEED"].copy()
        entry_point: float = df["cornerStart_m"].min()
        apex_point: float = df["cornerApex_m"].min()
        end_point: float = df["cornerEnd_m"].min()

        # Calculate and get the appropriate data from the DataFrame
        entry_speed_kmh: float = speed_df.loc[speed_df["Distance"] == entry_point, "SPEED"].iloc[0]
        apex_speed_kmh: float = speed_df.loc[speed_df["Distance"] == apex_point, "SPEED"].iloc[0]
        exit_speed_kmh: float = speed_df.loc[speed_df["Distance"] == end_point, "SPEED"].iloc[0]
        avg_speed_kmh: float = speed_s.mean()
        max_speed_kmh: float = speed_s.max()
        min_speed_kmh: float = speed_s.min()
        min_speed_m: float = speed_df.loc[speed_df["SPEED"].idxmin(), "Distance"]

        deceleration_window: pd.DataFrame = speed_df[speed_df["SPEED"] < speed_df["SPEED"].shift()]
        deceleration_rate: float = TelemetryCalculator.average_change_rate(deceleration_window, "SPEED") if not deceleration_window.empty else math.nan

        acceleration_window: pd.DataFrame = speed_df[speed_df["SPEED"] > speed_df["SPEED"].shift()]
        acceleration_rate: float = TelemetryCalculator.average_change_rate(acceleration_window, "SPEED") if not acceleration_window.empty else math.nan

        return SpeedMetrics(
            entry_speed_kmh=entry_speed_kmh,
            apex_speed_kmh=apex_speed_kmh,
            exit_speed_kmh=exit_speed_kmh,
            avg_speed_kmh=avg_speed_kmh,
            max_speed_kmh=max_speed_kmh,
            min_speed_kmh=min_speed_kmh,
            min_speed_m=min_speed_m,
            deceleration_rate=deceleration_rate,
            acceleration_rate=acceleration_rate
        )