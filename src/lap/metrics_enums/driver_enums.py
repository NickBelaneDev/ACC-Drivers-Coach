from enum import Enum

class DriverBrake(Enum):
    BRAKE_POINT_M = "metrics_driver_brake_brake_point_m"
    BRAKE_POINT_SPEED = "metrics_driver_brake_brake_point_speed"
    BRAKE_RELEASE_M = "metrics_driver_brake_brake_release_m"
    BRAKE_RELEASE_SPEED = "metrics_driver_brake_brake_release_speed"
    BRAKE_DELTA_S = "metrics_driver_brake_brake_delta_s"
    MAX_BRAKE = "metrics_driver_brake_max_brake"
    AVG_BRAKE = "metrics_driver_brake_avg_brake"
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
    STATUS = "metrics_driver_status"
    REASON = "metrics_driver_reason"
