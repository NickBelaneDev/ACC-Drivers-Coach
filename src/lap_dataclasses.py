from dataclasses import dataclass
from typing import Optional

from pyasn1_modules.rfc5914 import TrustAnchorInfo


@dataclass(frozen=True)
class Segment:
    id: int
    name: str
    start_m: int
    end_m: int

@dataclass(frozen=True)
class SegmentMetrics:
    segment: Segment
    time_user_s: float

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
