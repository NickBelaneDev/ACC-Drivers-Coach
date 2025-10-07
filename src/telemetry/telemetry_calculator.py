import pandas as pd
import numpy as np
import math
from src.logger import get_logger

log = get_logger("telemetry_calculator_log", to_console=False)


# The TelemetryCalculator needs some nice error handling, logging and DataFrame validation to it
# Tasks:
#   1.) Add a private DataFrame Validation Method to ensure all requested data is inside the df. The method shall either return the full df or just the asked cols.
class TelemetryCalculator:
    def __init__(self):
        pass
        #self.df = df

    @staticmethod
    def calc_g_force_vector(df: pd.DataFrame) -> pd.DataFrame:
        """Calculates the gForceVector and adds it to the dataframe.
        :param df: pd.DataFrame
        :return complete DataFrame with the gForceVector
        """
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
    def average_change_rate(df: pd.DataFrame, col:str, distance_col:str="Distance") -> float:

        _s = df.sort_values(by=distance_col)[col].reset_index(drop=True).copy()

        avg_c_r = _s.diff().mean()
        return avg_c_r if avg_c_r else math.nan

    @staticmethod
    def change_rate_var(df: pd.DataFrame, col: str, distance_col: str = "Distance") -> float:

        _s: pd.DataFrame = df.sort_values(by=distance_col)[col].reset_index(drop=True).copy()

        avg_c_r = _s.diff().var()
        return avg_c_r if avg_c_r else math.nan

    @staticmethod
    def parameter_stability(df: pd.DataFrame, col: str, amplitude_mode: bool=False, distance_col:str= "Distance") -> float:
        """Standardabweichung der Parameter auf dt"""
        _df = df.sort_values(by=distance_col).reset_index(drop=True).copy()

        delta_t = _df[distance_col].diff()
        delta_t.replace(0, np.nan, inplace=True)
        delta_val = _df[col].diff().div(delta_t)
        delta_val.replace([np.inf, -np.inf], np.nan).dropna()
        if amplitude_mode:
            delta_val = delta_val.abs()

        if delta_val.empty:
            return 0.0
        stability = min((delta_val.std(), 1e-6))
        return round(stability, 4) if stability > 1e-6 else 1e-6

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
    def get_integral(df: pd.DataFrame, col: str, amplitude_mode=False, distance_col:str= "Distance") -> float:

        _df = df.sort_values(by=distance_col).copy()
        dist_col = _df[distance_col]
        if amplitude_mode:
            parameter_col = _df[col].abs()
        else:
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


    # Wenn speed_from_rads zu sehr von der eigentlichen Geschwindigkeit abweicht, haben wir ein Übersteuern.

    @staticmethod
    def calculate_speed_from_rads(rad_per_second: np.ndarray, wheel_radius_m: float) -> np.ndarray:
        """
        Calculates speed in km/h from wheel rotation in rad/s.

        Args:
            rad_per_second: Wheel rotation speed in radians per second.
            wheel_radius_m: Radius of the wheel in meters.

        Returns:
            Speed in km/h.
        """
        # m/s = rad/s * radius
        speed_m_per_s = rad_per_second * wheel_radius_m
        # km/h = m/s * 3.6
        speed_kmh = speed_m_per_s * 3.6
        return speed_kmh