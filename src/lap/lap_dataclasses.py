from dataclasses import dataclass
from typing import Optional, Literal
import math

Status = Literal["ok", "empty", "invalid"]

@dataclass(frozen=True)
class Segment:
    id: int
    start_m: int
    end_m: int
    description: str
    corner_ids: list
@dataclass(frozen=True)

class SegmentMetrics:
    id: int
    start_speed_kmh: Optional[float] = 0.0
    end_speed_kmh: Optional[float] = 0.0

    avg_speed_kmh: Optional[float] = 0.0
    max_speed_kmh: Optional[float] = 0.0
    min_speed_kmh: Optional[float] = 0.0

    avg_throttle: Optional[float] = 0.0
    avg_brake: Optional[float] = 0.0

    time_delta_s: Optional[float] = 0.0
    total_cpi_score: Optional[float] = 0.0

@dataclass(frozen=True)
class SpeedMeasurements:
    # Speed Measurements
    entry_speed_kmh: float
    apex_speed_kmh: float
    exit_speed_kmh: float
    avg_speed_kmh: float
    max_speed_kmh: float
    min_speed_kmh: float
    min_speed_m: float

@dataclass(frozen=True)
class DriverInputMetrics:
    avg_steerangle: float
    max_steerangle: float
    max_steerangle_m: float

@dataclass(frozen=True)
class ThrottleMetrics:
    avg_throttle: float
    min_throttle: float
    max_throttle: float
    min_throttle_m: float
    max_throttle_m: float
    overall_throttle_power: float

    ttf95: float
    throttle_smoothness: float
    exit_throttle_init_m: Optional[int] = 0



@dataclass(frozen=True)
class TrailBrakeMetrics:
    start_m: float
    end_m: float
    start_speed_kmh: float
    end_speed_kmh: float

    delta_m: float
    delta_s: float
    integral: float

    corr_brake_roty: float
    release_per_m: float
    release_per_s: float
    smoothness: float

    status: Status = "ok"
    reason: Optional[str] = None
    @classmethod
    def empty(cls, reason: str = "no-trailbrake-detected") -> "TrailBrakeMetrics":
        return cls(
            start_m=math.nan, end_m=math.nan, start_speed_kmh=math.nan, end_speed_kmh=math.nan,
            delta_m=math.nan, delta_s=math.nan, integral=math.nan, corr_brake_roty=math.nan,
            release_per_s=math.nan, release_per_m=math.nan, smoothness=math.nan, status="empty", reason=reason
        )
@dataclass(frozen=True)
class BrakeMetrics:
    brake_point_m: float
    brake_point_speed: float
    brake_release_m: float
    brake_release_speed: float
    brake_delta_m: float
    brake_delta_s: float

    max_brake: float
    avg_brake: float
    trail_brake: TrailBrakeMetrics

    overall_brake_force: float
    brake_force_per_meter: float
    brake_force_per_second: float
    tbf95_s: float

    brake_smoothness: float
    status: Status = "ok"
    reason: Optional[str] = None


    @classmethod
    def empty(cls, reason: str = "no-braking-detected") -> "BrakeMetrics":
        return cls(
            brake_point_m=math.nan, brake_point_speed=math.nan,
            brake_delta_m=math.nan, brake_release_m=math.nan, brake_release_speed=math.nan,
            brake_delta_s=math.nan, max_brake=math.nan, avg_brake=math.nan,
            trail_brake=TrailBrakeMetrics.empty(reason=reason),
            overall_brake_force=0.0, brake_force_per_meter=math.nan, brake_force_per_second=math.nan,
            tbf95_s=math.nan, brake_smoothness=math.nan, status="empty", reason=reason
        )

@dataclass(frozen=True)
class CornerMetrics:
    time_delta_s: float

    # Speed Measurements
    entry_speed_kmh: float
    apex_speed_kmh: float
    exit_speed_kmh: float
    avg_speed_kmh: float
    max_speed_kmh: float
    min_speed_kmh: float
    min_speed_m: float

    # G-Forces
    g_lat_avg: float
    g_lat_max: float
    g_lat_min: float
    g_lon_avg: float
    g_lon_max: float
    g_lon_min: float

    # Driver's Input
    avg_steerangle: float
    max_steerangle: float
    max_steerangle_m: float

    # Darf raus!
    avg_brake: float
    max_brake: float

    avg_throttle: float

    tbf95_s: Optional[float] = 0.0      # tbf95_s = 'Time where Brake-Input >= 95% in seconds'
    ttf95_s: Optional[float] = 0.0      # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

    # Abstract Metrics
    # Replace with brake_metrics:
    ####
    brake_point_m: Optional[int] = 0
    brake_release_m: Optional[int] = 0#
    brake_delta_m: Optional[int] = 0      #
    brake_delta_s: Optional[float] = 0.0      #
    trail_brake_delta_s: Optional[float] = 0.0
    trail_brake_delta_m: Optional[float] = 0
    trail_brake_start_m: Optional[float] = 0
    trail_brake_end_m: Optional[float] = 0
    overall_brake_force: Optional[float] = 0.0
    ###
    brake_metrics: Optional[BrakeMetrics] = None

    throttle_metrics: Optional[ThrottleMetrics] = None


    exit_throttle_init_m: Optional[float] = 0 # Measurement from where the driver is on the gas again on corner_exit.
    avg_exit_throttle: Optional[float] = 0.0      # avg. throttle input from apex_m to exit_m + 100
    exit_speed_delta_s: Optional[float] = 0.0     # avg. Speed from apex_m to exit_m + 100m

    rolling_delta_s: Optional[float] = 0.0        # Time/s without throttle or brake
    rolling_delta_m: Optional[float] = 0

    cpi_factor: Optional[float] = 0.0

@dataclass(frozen=True)
class CornerMetricsNew:
    time_delta_s: float
    speed_and_g_force: Optional[SpeedMeasurments] = None
    driver_input: Optional[DriverInputMetrics] = None
    brake_metrics: Optional[BrakeMetrics] = None# -> Also includes the TrailBrakeMetrics as a separate DataClass
    throttle_metrics: Optional[ThrottleMetrics] = None
    scores: Optional[Scores] = None

@dataclass(frozen=True)
class Corner:
    id: int
    name: str
    start_m: float
    apex_m: float
    end_m: float
    metrics: CornerMetrics

