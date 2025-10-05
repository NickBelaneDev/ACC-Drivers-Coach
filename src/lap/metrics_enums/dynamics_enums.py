from enum import Enum

class DynamicsSpeed(Enum):
    ENTRY_SPEED_KMH = "metrics_dynamics_speed_entry_speed_kmh"
    APEX_SPEED_KMH = "metrics_dynamics_speed_apex_speed_kmh"
    EXIT_SPEED_KMH = "metrics_dynamics_speed_exit_speed_kmh"
    AVG_SPEED_KMH = "metrics_dynamics_speed_avg_speed_kmh"
    MAX_SPEED_KMH = "metrics_dynamics_speed_max_speed_kmh"
    MIN_SPEED_KMH = "metrics_dynamics_speed_min_speed_kmh"
    MIN_SPEED_M = "metrics_dynamics_speed_min_speed_m"
    DECELERATION_RATE = "metrics_dynamics_speed_deceleration_rate"
    ACCELERATION_RATE = "metrics_dynamics_speed_acceleration_rate"

    STATUS = "metrics_dynamics_speed_status"
    REASON = "metrics_dynamics_speed_reason"


class DynamicsGForce(Enum):
    G_LAT_AVG = "metrics_dynamics_g_force_g_lat_avg"
    G_LAT_MAX = "metrics_dynamics_g_force_g_lat_max"
    G_LAT_MIN = "metrics_dynamics_g_force_g_lat_min"
    G_LON_AVG = "metrics_dynamics_g_force_g_lon_avg"
    G_LON_MAX = "metrics_dynamics_g_force_g_lon_max"
    G_LON_MIN = "metrics_dynamics_g_force_g_lon_min"
    VECTOR_AVG = "metrics_dynamics_g_force_g_force_vector_avg"
    VECTOR_MIN = "metrics_dynamics_g_force_g_force_vector_min"
    VECTOR_MAX = "metrics_dynamics_g_force_g_force_vector_max"
    VECTOR_SMOOTHNESS = "metrics_dynamics_g_force_g_force_vector_smoothness"
    VECTOR_SCORE = "metrics_dynamics_g_force_g_force_vector_score"

    STATUS = "metrics_dynamics_g_force_status"
    REASON = "metrics_dynamics_g_force_reason"


class DynamicsMeta(Enum):
    STATUS = "metrics_dynamics_status"
    REASON = "metrics_dynamics_reason"
