from enum import Enum

class DynamicsSpeed(Enum):
    """
    Enumeration of all vehicle speed dynamic field names.

    Each member represents the canonical flattened key for
    ``CarDynamics.speed`` attributes, as used in exports, feature tables,
    and internal data adapters. These values describe how the car’s
    velocity evolves throughout a corner — from entry to exit.

    Covers:
      - Absolute speed measurements (entry, apex, exit, min/max/avg),
      - The distance of the minimum-speed point (for corner geometry),
      - Overall acceleration and deceleration rates,
      - Dataclass status and diagnostic reason fields.

    Typical usage:
      - Data export to CSV/JSON,
      - Car-dynamics dashboards,
      - Model input features for load-based performance analysis.
    """
    BRAKE_AREA_SPEED_KMH = "metrics_dynamics_brake_area_speed_kmh"
    ENTRY_SPEED_KMH = "metrics_dynamics_speed_entry_speed_kmh"
    APEX_SPEED_KMH = "metrics_dynamics_speed_apex_speed_kmh"
    EXIT_SPEED_KMH = "metrics_dynamics_speed_exit_speed_kmh"
    AVG_SPEED_KMH = "metrics_dynamics_speed_avg_speed_kmh"
    MAX_SPEED_KMH = "metrics_dynamics_speed_max_speed_kmh"
    MIN_SPEED_KMH = "metrics_dynamics_speed_min_speed_kmh"
    MIN_SPEED_M = "metrics_dynamics_speed_min_speed_m"
    SPEED_INTEGRAL = "metrics_dynamics_speed_integral"
    DECELERATION_RATE = "metrics_dynamics_speed_deceleration_rate"
    ACCELERATION_RATE = "metrics_dynamics_speed_acceleration_rate"

    STATUS = "metrics_dynamics_speed_status"
    REASON = "metrics_dynamics_speed_reason"


class DynamicsGForce(Enum):
    """
    Enumeration of all g-force dynamic field names.

    Defines the flattened schema keys for ``CarDynamics.g_force`` attributes,
    representing the car’s physical load behavior during cornering.

    Covers:
      - Lateral and longitudinal accelerations (mean, min, max),
      - The combined g-force vector and its smoothness,
      - The integrated “g-force score” representing total corner load,
      - Diagnostic metadata for empty/invalid metric states.

    These metrics describe the grip envelope and stability of the car,
    critical for understanding balance and dynamic limits.

    Typical usage:
      - Data export to CSV/JSON,
      - Car-dynamics dashboards,
      - Model input features for load-based performance analysis.
    """

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
    """
    Enumeration of meta fields for the overall ``CarDynamics`` object.

    Contains general diagnostic _information separate from the specific
    metric groups (``Speed`` and ``GForce``). Used to record the status
    and reason for empty or invalid dynamics composites.

    This allows ``CarDynamics`` instances to carry consistent metadata
    across nested analyses, ensuring traceability throughout the pipeline.
    """
    STATUS = "metrics_dynamics_status"
    REASON = "metrics_dynamics_reason"
