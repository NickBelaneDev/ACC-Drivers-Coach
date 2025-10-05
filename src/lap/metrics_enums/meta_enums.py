from enum import Enum

class LapMeta(Enum):
    ID = "id"
    NAME = "name"
    START_M = "start_m"
    APEX_M = "apex_m"
    END_M = "end_m"
    STATUS = "status"
    REASON = "reason"
    TIME_DELTA_S = "metrics_time_delta_s"
    METRICS_STATUS = "metrics_status"
    METRICS_REASON = "metrics_reason"
