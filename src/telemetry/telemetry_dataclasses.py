from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class BrakeMetrics:
    brake_point_m: int
    brake_point_speed: float
    brake_delta_m: int
    brake_release_m: int
    brake_release_speed: float
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
    brake_smoothness: float
    tbf95_s: float

