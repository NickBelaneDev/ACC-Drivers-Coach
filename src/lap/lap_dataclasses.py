from dataclasses import dataclass
from typing import Optional

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
class ThrottleMetrics:
    avg_throttle: float
    min_throttle: int
    max_throttle: int
    min_throttle_m: int
    max_throttle_m: int
    overall_throttle_power: float

    ttf95: float
    throttle_smoothness: float
    exit_throttle_init_m: Optional[int] = 0

@dataclass(frozen=True)
class TrailBrakeMetrics:
    start_m: int
    end_m: int
    delta_m: int
    delta_s: float
    start_speed_kmh: float
    integral: float
    corr_brake_roty: float
    release_per_m: float
    release_per_s: float
    smoothness: float

@dataclass(frozen=True)
class BrakeMetrics:
    brake_point_m: int
    brake_point_speed: float
    brake_release_m: int
    brake_release_speed: float
    brake_delta_m: int
    brake_delta_s: float

    max_brake: float
    avg_brake: float

    trail_brake_delta_m: int
    trail_brake_delta_s: float
    trail_brake_start_m: int
    trail_brake_end_m: int

    overall_brake_force: float
    brake_force_per_meter: float
    brake_force_per_second: float
    tbf95_s: float

    time_to_full_pressure: Optional[float] = 0.0
    brake_smoothness: Optional[float] = 0.0

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
    min_speed_m: int

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
    max_steerangle_m: int

    avg_brake: float
    max_brake: float

    avg_throttle: float

    tbf95_s: Optional[float] = 0.0      # tbf95_s = 'Time where Brake-Input >= 95% in seconds'
    ttf95_s: Optional[float] = 0.0      # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

    # Abstract Metrics
    brake_point_m: Optional[int] = 0
    brake_release_m: Optional[int] = 0#
    brake_delta_m: Optional[int] = 0      #
    brake_delta_s: Optional[float] = 0.0      #
    trail_brake_delta_s: Optional[float] = 0.0
    trail_brake_delta_m: Optional[int] = 0
    trail_brake_start_m: Optional[int] = 0
    trail_brake_end_m: Optional[int] = 0
    overall_brake_force: Optional[float] = 0.0

    exit_throttle_init_m: Optional[int] = 0 # Measurement from where the driver is on the gas again on corner_exit.
    avg_exit_throttle: Optional[float] = 0.0      # avg. throttle input from apex_m to exit_m + 100
    exit_speed_delta_s: Optional[float] = 0.0     # avg. Speed from apex_m to exit_m + 100m

    rolling_delta_s: Optional[float] = 0.0        # Time/s without throttle or brake
    rolling_delta_m: Optional[int] = 0

    cpi_factor: Optional[float] = 0.0

@dataclass(frozen=True)
class Corner:
    id: int
    name: str
    start_m: float
    apex_m: float
    end_m: float
    metrics: CornerMetrics

