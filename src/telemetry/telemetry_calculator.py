import pandas as pd
import numpy as np
from src.logger import get_logger

log = get_logger("telemetry_calculator_log", to_console=False)
class TelemetryCalculator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @staticmethod
    def calc_g_force_vector(df: pd.DataFrame):
        with_vector_df = df.copy()
        # Calculate the G-Force Index
        g_lat = df["G_LAT"].abs()
        g_lon = df["G_LON"].abs()
        g_lat_max_ref = 2
        g_lon_max_ref = 2
        term_lat = (g_lat / g_lat_max_ref) ** 2
        term_lon = (g_lon / g_lon_max_ref) ** 2

        with_vector_df["gForceVector"] = np.sqrt(term_lat + term_lon)
        return with_vector_df

    @staticmethod
    def parameter_smoothness(df: pd.DataFrame, col: str, amplitude_mode: bool=False, distance_col:str= "Distance") -> float:
        """Standardabweichung der Parameter auf dt"""
        _df = df.sort_values(by=distance_col).copy()

        delta_t = _df[distance_col].diff()
        delta_t.replace(0, np.nan, inplace=True)
        delta_val = _df[col].diff().div(delta_t)
        delta_val.replace([np.inf, -np.inf], np.nan).dropna()
        if amplitude_mode:
            delta_val = delta_val.abs()

        if delta_val.empty:
            return 0.0
        smoothness = float(1 / (delta_val.std() + 1e-6))
        return round(smoothness, 4)

    @staticmethod
    def parameter_correlation(raw_df: pd.DataFrame, col_01: str, col_02: str, distance_col: str = 'Distance') -> float:
        """
        Calculates the Input-Response Correlation Coefficient (IRK).

        This function correlates the driver's steering velocity with the car's
        yaw acceleration to determine if the driver is reacting to or causing
        instability.

        Args:
            raw_df: A pandas DataFrame with telemetry data for a single corner.
            col_01: The name of the first column.
            col_02: The name of the second column.
            distance_col: The name of the t column.

        Returns:
            The Pearson correlation coefficient between steering velocity and
            yaw acceleration as a float. Returns 0.0 if calculation is not possible.
        """

        _cols = raw_df.columns
        if col_01 not in _cols or col_02 not in _cols:
            log.warning(f"{col_01=} or {col_02=} not in {_cols=}")
            return 0.0

        # Calculating the diff()
        raw_corner_df: pd.DataFrame = raw_df.sort_values(by=distance_col).copy()
        delta_t = raw_corner_df[distance_col].diff()
        delta_t.replace(0, np.nan, inplace=True)
        col_01_velocity = raw_corner_df[col_01].diff() / delta_t
        col_02_velocity = raw_corner_df[col_02].diff() / delta_t

        correlation_df = pd.DataFrame({
            "col_01_velocity": col_01_velocity,
            "col_02_velocity": col_02_velocity
        }).replace([np.inf, -np.inf], np.nan).dropna()

        if len(correlation_df) < 3 or correlation_df["col_01_velocity"].std() == 0 or correlation_df["col_02_velocity"].std() == 0 :
            return 0.0

        correlation_score = float(correlation_df["col_01_velocity"].corr(correlation_df["col_02_velocity"]))
        return round(correlation_score, 4) if pd.notna(correlation_score) else 0.0

    @staticmethod
    def get_integral(df: pd.DataFrame, col: str, distance_col:str= "Distance") -> float:
        _df = df.sort_values(by=distance_col).copy()

        dist_col = _df[distance_col]
        parameter_col = _df[col]

        trapz = np.trapezoid(parameter_col, dist_col)
        return round(trapz, 4)

    @staticmethod
    def quantile(df: pd.DataFrame, col: str, quantile:int=0.95, distance_col:str = "Distance") -> float:
        _quantile = quantile
        if quantile > 1:
            _quantile = 1
        if quantile < 0:
            _quantile = 0

        _df:pd.DataFrame = df.sort_values(by=distance_col).copy()

        if not _df.empty:
            return _df[col].quantile(q=_quantile)
        return 0.0