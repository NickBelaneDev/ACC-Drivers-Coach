import pandas as pd
from .brake_analyzer import BrakeAnalyzer
from .gforce_analyzer import GForceAnalyzer
from .speed_analyzer import SpeedAnalyzer
from .throttle_analyzer import ThrottleAnalyzer
from .steer_analyzer import SteerAnalyzer
from .gforce_analyzer import GForceAnalyzer
from ..dataframe_validation import DataFrameValidator, MissingColumnError, EmptyDataFrameError
from ..lap_dataclasses import SpeedMetrics, SteerMetrics, ThrottleMetrics, BrakeMetrics, GForceMetrics, CarDynamics, \
    DriverPerformance, CornerMetrics, Corner

REQUIRED_COLS = {"Distance", "Time"}
class CornerAnalyzer:
    def __init__(self, corner_df: pd.DataFrame):
        """
        When calling the constructor, the DataFrame will be validated. EmptyDataFrameError, MissingColumnError can raise!
        :param corner_df: DataFrame of the corner we want to analyze.
        """
        DataFrameValidator.validate_df(corner_df, list(REQUIRED_COLS))
        self.df = corner_df

        self._speed_analyzer = SpeedAnalyzer()
        self._steering_analyzer = SteerAnalyzer()
        self._throttle_analyzer = ThrottleAnalyzer()
        self._brake_analyzer = BrakeAnalyzer()
        self._g_force_analyzer = GForceAnalyzer()


    def _get_time_delta(self) -> float:
        return self.df["Time"].max() - self.df["Time"].min()

    def _analyze_car_dynamics(self) -> CarDynamics:
        speed_metrics: SpeedMetrics = self._speed_analyzer.analyze(self.df)
        g_force_metrics: GForceMetrics = self._g_force_analyzer.analyze(self.df)

        if speed_metrics.is_empty() and g_force_metrics.is_empty():
            return CarDynamics.empty(reason=f"'speed' and 'g_force_metrics' are empty!")

        return CarDynamics(
            speed=speed_metrics, g_force=g_force_metrics
        )

    def _analyze_driver_performance(self) -> DriverPerformance:
        steering_metrics: SteerMetrics = self._steering_analyzer.analyze(self.df)
        throttle_metrics: ThrottleMetrics = self._throttle_analyzer.analyze(self.df)
        brake_metrics: BrakeMetrics = self._brake_analyzer.analyze(self.df)

        if steering_metrics.is_empty() and throttle_metrics.is_empty() and brake_metrics.is_empty():
            return DriverPerformance.empty(reason=f"'steer', 'throttle' and 'brake' are all empty!")

        return DriverPerformance(
            steer=steering_metrics,
            throttle=throttle_metrics,
            brake=brake_metrics
        )
    def _get_corner_meta_data(self):
        corner_id: int = self.df["corner_id"].min()
        name: str = self.df["cornerName"].iloc[0] if not None else self.df["corner_name"].iloc[-1]
        start_m: int = self.df["cornerStart_m"].min()
        apex_m: int = self.df["cornerApex_m"].min()
        end_m: int = self.df["cornerEnd_m"].min()


        return {"id": corner_id,
        "name":  name,
        "start_m": start_m,
        "apex_m": apex_m,
        "end_m": end_m}

    def analyze(self) -> Corner:
        car_dynamics: CarDynamics = self._analyze_car_dynamics()
        driver_performance: DriverPerformance = self._analyze_driver_performance()

        if car_dynamics.is_empty() and driver_performance.is_empty():
            return CornerMetrics.empty(reason=f"'car_dynamics' and 'driver_performance' are empty!")

        time_delta_s = self._get_time_delta()

        corner_metrics = CornerMetrics(
            time_delta_s=time_delta_s,
            dynamics=car_dynamics,
            driver=driver_performance
        )

        corner_meta_data = self._get_corner_meta_data()

        return Corner(
            id=corner_meta_data["id"],
            name=corner_meta_data["name"],
            start_m=corner_meta_data["start_m"],
            apex_m=corner_meta_data["apex_m"],
            end_m=corner_meta_data["end_m"],
            metrics=corner_metrics
        )


