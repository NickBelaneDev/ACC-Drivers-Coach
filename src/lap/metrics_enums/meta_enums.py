from enum import Enum

class LapMeta(Enum):
    """
    Enumeration of top-level lap and corner metadata field names.

    ``LapMeta`` defines the canonical schema keys for identifying and
    describing high-level lap or corner entities. These keys appear in
    flattened DataFrame or JSON representations of analyzed telemetry
    objects such as ``Corner``, ``Segment``, or ``Lap``.

    The members include both structural identifiers and diagnostic metadata
    inherited from the ``Emptyable`` status system.

    Categories
    -----------
    **Identifiers**
      - ``ID`` → Unique object or corner ID within the lap.
      - ``NAME`` → Human-readable label (e.g., "Pouhon", "Lap 16").

    **Geometry**
      - ``BRAKE_AREA_M`` → Brake_Area distance in meters (track coordinate).
      - ``START_M`` → Start distance in meters (track coordinate).
      - ``APEX_M`` → Apex point distance in meters (track coordinate).
      - ``END_M`` → End distance in meters (track coordinate).
      - ``LENGTH`` → Length of the corner window in meters.

    **Lifecycle / Status**
      - ``STATUS`` → Object-level validity (``ok``, ``empty``, ``invalid``).
      - ``REASON`` → Explanation string for non-OK states.

    **Metrics**
      - ``TIME_DELTA_S`` → Duration of the analyzed section (seconds).
      - ``METRICS_STATUS`` → Status of the nested metric bundle.
      - ``METRICS_REASON`` → Diagnostic reason associated with metrics.

    Usage
    -----
    These constants ensure consistent naming when:
      - exporting structured dataclasses (e.g., ``Corner``, ``Lap``),
      - building pandas DataFrames or feature sets,
      - serializing and deserializing telemetry analysis.

    Example
    -------
    >>> from src.lap.metrics_enums import LapMeta
    >>> LapMeta.TIME_DELTA_S.value
    'metrics_time_delta_s'
    """
    ID = "id"
    NAME = "name"
    BRAKE_AREA_M = "brake_area_m"
    START_M = "start_m"
    APEX_M = "apex_m"
    END_M = "end_m"
    LENGTH_M = "length_m"
    STATUS = "status"
    REASON = "reason"
    TIME_DELTA_S = "metrics_time_delta_s"
    METRICS_STATUS = "metrics_status"
    METRICS_REASON = "metrics_reason"
