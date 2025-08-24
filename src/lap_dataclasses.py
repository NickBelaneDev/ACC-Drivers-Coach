from dataclasses import dataclass
from typing import Optional

from pyasn1_modules.rfc5914 import TrustAnchorInfo


@dataclass(frozen=True)
class Segment:
    id: int
    name: str
    start_m: float
    end_m: float

@dataclass(frozen=True)
class Corner:
    id: int
    name: str
    start_m: float
    apex_m: float
    end_m: float
    tolerance_m: float

@dataclass(frozen=True)
class SegmentMetrics:
    segment: Segment
    time_user_s: float
    time_record_s: float
    delt_s: float

@dataclass(frozen=True)
class CornerMetrics:
    corner: Corner
    entry_user_kmh: float
    entry_record_kmh: float
    apex_user_kmh: float
    apex_record_kmh: float
    exit_user_kmh: float
    exit_record_kmh: float
    g_lat_user: float
    g_lat_record: float
    steer_angle_user: float
    steer_angle_record: float
    brake_user_m: Optional[float]
    brake_record_m: Optional[float]
    brake_delta_m: Optional[float]
    ttf95_user_s: Optional[float]
    ttf95_record_s: Optional[float]
    ttf95_delta_s: Optional[float]
    time_user_s: float
    time_record_s: float
    time_delta_s: float