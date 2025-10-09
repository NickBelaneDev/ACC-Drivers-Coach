from enum import Enum

class DriverBrake(Enum):
    """
    Enumeration of all driver brake metric field names.

    Each member represents the canonical key used in flattened DataFrames
    or serialized data (e.g., after transforming a dataclass into a row),
    mapping directly to ``DriverPerformance.brake`` attributes and their
    corresponding telemetry-derived values.

    The fields describe braking behavior, including:
      - braking phase geometry and timing (start, release, delta),
      - brake intensity (max, average, integral),
      - trail-braking analysis (correlation, release rate, stability),
      - state management (status, reason).

    These values are used consistently across:
      - Data adapters,
      - Feature extraction,
      - Model evaluation,
      - Data exports (CSV/JSON).
    """
    BRAKE_POINT_M = "metrics_driver_brake_brake_point_m"
    BRAKE_POINT_SPEED = "metrics_driver_brake_brake_point_speed"
    BRAKE_RELEASE_M = "metrics_driver_brake_brake_release_m"
    BRAKE_RELEASE_SPEED = "metrics_driver_brake_brake_release_speed"
    BRAKE_WINDOW_S = "metrics_driver_brake_brake_window_s"
    BRAKE_WINDOW_M = "metrics_driver_brake_brake_window_m"
    MAX_BRAKE = "metrics_driver_brake_max_brake"
    AVG_BRAKE = "metrics_driver_brake_avg_brake"
    BRAKE_FORCE_PER_M = "metrics_driver_brake_brake_force_per_m"
    BRAKE_FORCE_PER_S = "metrics_driver_brake_brake_force_per_s"
    BRAKE_FORCE_PER_METER = "metrics_driver_brake_brake_force_per_meter"
    BRAKE_FORCE_PER_SECOND = "metrics_driver_brake_brake_force_per_second"
    OVERALL_FORCE = "metrics_driver_brake_overall_brake_force"
    TBF95_S = "metrics_driver_brake_tbf95_s"

    TRAIL_START_M = "metrics_driver_brake_trail_brake_start_m"
    TRAIL_END_M = "metrics_driver_brake_trail_brake_end_m"
    TRAIL_START_SPEED = "metrics_driver_brake_trail_brake_start_speed_kmh"
    TRAIL_END_SPEED = "metrics_driver_brake_trail_brake_end_speed_kmh"
    TRAIL_DELTA_S = "metrics_driver_brake_trail_brake_delta_s"
    TRAIL_INTEGRAL = "metrics_driver_brake_trail_brake_integral"
    TRAIL_CORR_BRAKE_ROTY = "metrics_driver_brake_trail_brake_corr_brake_roty"
    TRAIL_RELEASE_RATE = "metrics_driver_brake_trail_brake_release_rate"
    TRAIL_STABILITY = "metrics_driver_brake_trail_brake_stability"

    STATUS = "metrics_driver_brake_status"
    REASON = "metrics_driver_brake_reason"


class DriverThrottle(Enum):
    """
    Enumeration of driver throttle metric field names.

    These constants define the flattened key names associated with
    ``DriverPerformance.throttle`` attributes when metrics are exported
    or adapted into tabular representations.

    Covers both absolute throttle levels and derived quantities such as:
      - acceleration window lengths (Δm, Δs),
      - ramp rate and smoothness,
      - time to reach ≥95% throttle,
      - exit point reference.

    These values are used consistently across:
      - Data adapters,
      - Feature extraction,
      - Model evaluation,
      - Data exports (CSV/JSON).
    """
    AVG_THROTTLE = "metrics_driver_throttle_avg_throttle"
    MIN_THROTTLE = "metrics_driver_throttle_min_throttle"
    MAX_THROTTLE = "metrics_driver_throttle_max_throttle"
    INTEGRAL = "metrics_driver_throttle_integral"
    ACC_DELTA_M = "metrics_driver_throttle_acceleration_delta_m"
    ACC_DELTA_S = "metrics_driver_throttle_acceleration_delta_s"
    ACC_RATE = "metrics_driver_throttle_acceleration_rate"
    TTF95_S = "metrics_driver_throttle_ttf95"
    SMOOTHNESS = "metrics_driver_throttle_throttle_smoothness"
    EXIT_INIT_M = "metrics_driver_throttle_exit_throttle_init_m"

    STATUS = "metrics_driver_throttle_status"
    REASON = "metrics_driver_throttle_reason"


class DriverSteer(Enum):
    """
    Enumeration of driver steering metric field names.

    Represents all flattened key names for metrics within
    ``DriverPerformance.steer``. These capture both input characteristics
    (steering angle, rate, smoothness) and the resulting vehicle response
    (rotation metrics).

    Includes:
      - geometric measures (max steering angle and its position),
      - input variance proxies (smoothness),
      - yaw dynamics (rotation integral, smoothness),
      - optional cross-correlations (e.g., steer–throttle relation).

    These values are used consistently across:
      - Data adapters,
      - Feature extraction,
      - Model evaluation,
      - Data exports (CSV/JSON).
    """
    AVG_ANGLE = "metrics_driver_steer_avg_steerangle"
    MAX_ANGLE = "metrics_driver_steer_max_steerangle"
    MAX_ANGLE_M = "metrics_driver_steer_max_steerangle_m"
    INTEGRAL = "metrics_driver_steer_steering_integral"
    SMOOTHNESS = "metrics_driver_steer_steering_smoothness"
    MAX_ROTATION = "metrics_driver_steer_max_rotation"
    ROTATION_INTEGRAL = "metrics_driver_steer_rotation_integral"
    ROTATION_SMOOTHNESS = "metrics_driver_steer_rotation_smoothness"
    THROTTLE_CORR = "metrics_driver_steer_steering_throttle_correlation"

    STATUS = "metrics_driver_steer_status"
    REASON = "metrics_driver_steer_reason"


class DriverMeta(Enum):
    """
    Enumeration of driver-level meta fields.

    Contains general diagnostic metadata for ``DriverPerformance`` objects,
    separate from the individual input categories (throttle, brake, steer).

    Typically used to record dataclass state and provide traceability across
    different analysis stages or export formats.
    """
    STATUS = "metrics_driver_status"
    REASON = "metrics_driver_reason"
