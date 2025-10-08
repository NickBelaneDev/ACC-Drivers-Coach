import pandas as pd
from pydantic import BaseModel

from .brake_analyzer import BrakeAnalyzer
from .speed_analyzer import SpeedAnalyzer
from .throttle_analyzer import ThrottleAnalyzer
from .steer_analyzer import SteerAnalyzer
from .gforce_analyzer import GForceAnalyzer
from ..dataframe_validation import DataFrameValidator
from ..lap_dataclasses import (
    SpeedMetrics,
    SteerMetrics,
    ThrottleMetrics,
    BrakeMetrics,
    GForceMetrics,
    CarDynamics,
    DriverPerformance,
    CornerMetrics,
    Corner)
from ...logger import get_logger

log = get_logger(
    name="CornerAnalyzer",
    log_file="src/lap/analyzer/log/corner_analyzer.log",
    to_console=False
)
REQUIRED_COLS = {"Distance", "Time"}
class CornerAnalyzer:
    def __init__(
            self,
            corner_df: pd.DataFrame
    ):
        """
        Initialize the analyzer for a single corner's telemetry window.

        Upon construction the provided DataFrame is validated for required columns
        and emptiness. The analyzer then prepares the dedicated sub-analyzers
        for speed, steering, throttle, braking and g-forces.

        :param corner_df:
            A telemetry DataFrame already restricted to the area of one corner
            (from ``cornerStart_m`` up to ``cornerEnd_m``), typically produced by
            the track map merge and filtering pipeline.
        :raises EmptyDataFrameError:
            If ``corner_df`` is empty.
        :raises MissingColumnError:
            If one of the required columns (``"Distance"``, ``"Time"``) is missing.
        """
        DataFrameValidator.validate_df(corner_df,
                                       list(REQUIRED_COLS))
        self.df = corner_df

        self._speed_analyzer = SpeedAnalyzer()
        self._steering_analyzer = SteerAnalyzer()
        self._throttle_analyzer = ThrottleAnalyzer()
        self._brake_analyzer = BrakeAnalyzer()
        self._g_force_analyzer = GForceAnalyzer()


    def _get_time_delta(self) \
            -> float:
        """
        Compute the elapsed time inside the corner window.

        This is simply ``Time.max() - Time.min()`` measured over the complete
        corner DataFrame (from brake point/start to end).

        :return:
            Corner time in seconds as a float.
        """
        return self.df["Time"].max() - self.df["Time"].min()

    def _analyze_car_dynamics(self) \
            -> CarDynamics:
        """
        Analyze vehicle dynamics within the corner.

        Runs the speed and g-force analyzers on the corner DataFrame and bundles
        the results into a ``CarDynamics`` dataclass. If both sub-analyses are
        empty, an empty ``CarDynamics`` object is returned to keep downstream
        logic robust.

        :return:
            A ``CarDynamics`` object containing speed and g-force metrics.
            May be ``CarDynamics.empty(...)`` if no valid data is present.
        """
        speed_metrics: SpeedMetrics = self._speed_analyzer.analyze(self.df)
        g_force_metrics: GForceMetrics = self._g_force_analyzer.analyze(self.df)

        if speed_metrics.is_empty() and g_force_metrics.is_empty():
            return CarDynamics.empty(reason=f"'speed' and 'g_force_metrics' are empty!")

        return CarDynamics(
            speed=speed_metrics, g_force=g_force_metrics
        )

    def _analyze_driver_performance(self) \
            -> DriverPerformance:
        """
        Analyze driver inputs/behavior for the corner.

        Executes the steering, throttle, and brake analyzers on the same window
        and aggregates their atomic metrics into a ``DriverPerformance`` dataclass.
        If all three sub-analyses are empty, an empty ``DriverPerformance`` is
        returned to provide a consistent API contract.

        :return:
            A ``DriverPerformance`` object containing steer, throttle and brake
            metrics, or ``DriverPerformance.empty(...)`` if no signals are valid.
        """
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

    def analyze(self) \
            -> CornerMetrics:
        """
        Run the full corner analysis and assemble a ``CornerMetrics`` object.

        This method is the high-level entry point: it analyzes vehicle dynamics
        and driver performance for the provided corner window, computes the
        elapsed corner time, and packages everything into a single container
        dataclass. If both dynamics and driver metrics are empty, an empty
        ``CornerMetrics`` placeholder is returned.

        Example:
            >>> corner_metrics = CornerBuilder.build_corner(corner_df)
        :return:
            A populated ``CornerMetrics`` dataclass with:
              - ``time_delta_s``: elapsed time in seconds
              - ``dynamics``: car dynamics (speed & g-forces)
              - ``driver``: driver performance (steer, throttle, brake)
            or ``CornerMetrics.empty(...)`` when no valid data exists.
        """
        car_dynamics: CarDynamics = self._analyze_car_dynamics()
        driver_performance: DriverPerformance = self._analyze_driver_performance()

        if car_dynamics.is_empty() and driver_performance.is_empty():
            return CornerMetrics.empty(reason=f"'car_dynamics' and 'driver_performance' are empty!")

        time_delta_s = self._get_time_delta()

        return CornerMetrics(
            time_delta_s=time_delta_s,
            dynamics=car_dynamics,
            driver=driver_performance
        )

class CornerMetadata(BaseModel):
    """
    Lightweight container for corner identity and geometry.

    Instances of this model are derived from the corner-specific
    telemetry window and provide the canonical IDs and distances
    (start, apex, end) used to instantiate the ``Corner`` dataclass.
    """
    id: int
    name: str
    start_m: int
    apex_m: int
    end_m: int

class CornerBuilder:
    """
    If you want to create a Corner Dataclass Object, use the CornerBuilder.build_corner(df) method.
    It is the standard and easiest way of creating Corner Dataclass Objects!
    """
    @staticmethod
    def build_corner(df: pd.DataFrame) \
            -> Corner:
        """
        Construct a ``Corner`` dataclass from a corner-restricted telemetry DataFrame.

        This is the standard method for creating **Corner-Objects** from a raw
        telemetry DataFrame that is already restricted to the area of one corner
        (a **Corner-DataFrame**). It performs the following steps:

          1. Read the **CornerMetadata** (id, name, start_m, apex_m, end_m) from the DataFrame.
          2. Analyze the same window via **CornerAnalyzer.analyze()** to compute all atomic metrics.
          3. Return a fully-populated **Corner** dataclass that serves as the transport format
             for corner data across the application.

        It is important to only create **Corner Objects** with this method to keep
        metadata extraction and analysis consistent.

        :param df:
            A DataFrame consisting only of the associated area of the corner.
        :return:
            ``Corner`` dataclass with meta _information and analyzed metrics.
        """

        def _get_corner_meta_data() -> CornerMetadata:

            corner_id: int = df["corner_id"].min()
            name: str = df["cornerName"].iloc[0]
            start_m: int = df["cornerStart_m"].min()
            apex_m: int = df["cornerApex_m"].min()
            end_m: int = df["cornerEnd_m"].min()

            return CornerMetadata(
                id=corner_id,
                name=name,
                start_m=start_m,
                apex_m=apex_m,
                end_m=end_m
            )

        meta_data = _get_corner_meta_data()
        corner_metrics = CornerAnalyzer(df).analyze()

        return Corner(
            id=meta_data.id,
            name=meta_data.name,
            start_m=meta_data.start_m,
            apex_m=meta_data.apex_m,
            end_m=meta_data.end_m,
            metrics=corner_metrics
        )