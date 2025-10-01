import pandas as pd
from dataclasses import dataclass, field, is_dataclass
from typing import Optional, Literal
import numpy as np
import math
from abc import ABC, abstractmethod
from enum import Enum
import json
from streamlit.web.server.server import start_listening_unix_socket


Status = Literal["ok", "empty", "invalid"]

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
    start_speed_kmh: Optional[float]
    end_speed_kmh: Optional[float] = 0.0

    avg_speed_kmh: Optional[float] = 0.0
    max_speed_kmh: Optional[float] = 0.0
    min_speed_kmh: Optional[float] = 0.0

    avg_throttle: Optional[float] = 0.0
    avg_brake: Optional[float] = 0.0

    time_delta_s: Optional[float] = 0.0
    total_cpi_score: Optional[float] = 0.0

##############################################
# TO BE REMOVED!!
##############################################

@dataclass(frozen=True)
class ThrottleMetrics:
    avg_throttle: float
    min_throttle: float
    max_throttle: float
    min_throttle_m: float
    max_throttle_m: float
    overall_throttle_power: float

    ttf95: float
    throttle_smoothness: float
    exit_throttle_init_m: Optional[int] = 0

@dataclass(frozen=True)
class TrailBrakeMetrics:
    start_m: float
    end_m: float
    start_speed_kmh: float
    end_speed_kmh: float

    delta_m: float
    delta_s: float
    integral: float

    corr_brake_roty: float
    release_per_m: float
    release_per_s: float
    smoothness: float

    status: Status = "ok"
    reason: Optional[str] = None

    @classmethod
    def empty(cls, reason: str = "no-trailbrake-detected") -> "TrailBrakeMetrics":
        return cls(
            start_m=math.nan, end_m=math.nan, start_speed_kmh=math.nan, end_speed_kmh=math.nan,
            delta_m=math.nan, delta_s=math.nan, integral=math.nan, corr_brake_roty=math.nan,
            release_per_s=math.nan, release_per_m=math.nan, smoothness=math.nan, status="empty", reason=reason
        )

@dataclass(frozen=True)
class BrakeMetrics:
    brake_point_m: float
    brake_point_speed: float
    brake_release_m: float
    brake_release_speed: float
    brake_delta_m: float
    brake_delta_s: float

    max_brake: float
    avg_brake: float
    trail_brake: TrailBrakeMetrics

    overall_brake_force: float
    brake_force_per_meter: float
    brake_force_per_second: float
    tbf95_s: float

    brake_smoothness: float
    status: Status = "ok"
    reason: Optional[str] = None


    @classmethod
    def empty(cls, reason: str = "no-braking-detected") -> "BrakeMetrics":
        return cls(
            brake_point_m=math.nan, brake_point_speed=math.nan,
            brake_delta_m=math.nan, brake_release_m=math.nan, brake_release_speed=math.nan,
            brake_delta_s=math.nan, max_brake=math.nan, avg_brake=math.nan,
            trail_brake=TrailBrakeMetrics.empty(reason=reason),
            overall_brake_force=0.0, brake_force_per_meter=math.nan, brake_force_per_second=math.nan,
            tbf95_s=math.nan, brake_smoothness=math.nan, status="empty", reason=reason
        )

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
    min_speed_m: float

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
    max_steerangle_m: float

    # Darf raus!
    avg_brake: float
    max_brake: float

    avg_throttle: float

    tbf95_s: Optional[float] = 0.0      # tbf95_s = 'Time where Brake-Input >= 95% in seconds'
    ttf95_s: Optional[float] = 0.0      # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

    # Abstract Metrics
    # Replace with brake_metrics:
    ####
    brake_point_m: Optional[int] = 0
    brake_release_m: Optional[int] = 0#
    brake_delta_m: Optional[int] = 0      #
    brake_delta_s: Optional[float] = 0.0      #
    trail_brake_delta_s: Optional[float] = 0.0
    trail_brake_delta_m: Optional[float] = 0
    trail_brake_start_m: Optional[float] = 0
    trail_brake_end_m: Optional[float] = 0
    overall_brake_force: Optional[float] = 0.0
    ###
    brake_metrics: Optional[BrakeMetrics] = None

    throttle_metrics: Optional[ThrottleMetrics] = None


    exit_throttle_init_m: Optional[float] = 0 # Measurement from where the driver is on the gas again on corner_exit.
    avg_exit_throttle: Optional[float] = 0.0      # avg. throttle input from apex_m to exit_m + 100
    exit_speed_delta_s: Optional[float] = 0.0     # avg. Speed from apex_m to exit_m + 100m

    rolling_delta_s: Optional[float] = 0.0        # Time/s without throttle or brake
    rolling_delta_m: Optional[float] = 0

    cpi_factor: Optional[float] = 0.0


#    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###################################




# ====================================================
# version 1.01, date: 09.30.2025, © written by Robert Millotat
#
# To grant good structured corner information we are working with Dataclasses.
# The Dataclass is from where we define, what information we want to have. From here on we work our way up
# to the raw DataFrame, which comes from the telemetry.csv files delivered by the TelemetryLoader-class.
#
# The dataclass objects are the data-type we use to communicate between classes and send calculated
# telemetry numbers to other classes.

class StatusEnum(Enum):
    ok = "ok"
    empty = "empty"
    invalid = "invalid"
class Emptyable:
    """A class that delivers the .empty() and validation method/s for all other dataclasses."""


    @classmethod
    @abstractmethod
    def empty(cls, reason:str):
        """
        Creates an empty object filled with math.nan for any number. Used to handle validation later on
        and to improve the overall workflow with those objects: when we are calculating the data and come into errors,
        we can return an empty instance of the object.
        :param reason: description of why the object is empty.
        :return: Empty dataclass object.
        """
        raise NotImplementedError
    def is_ok(self) -> bool:
        return getattr(self, "status", None) == StatusEnum.ok
    def is_empty(self) -> bool:
        return getattr(self, "status", None) == StatusEnum.empty
    def is_invalid(self) -> bool:
        return getattr(self, "status", None) == StatusEnum.invalid

# --- Stufe 1: Atomare Metriken ---

@dataclass(frozen=True)
class SpeedMetrics(Emptyable):
    """

    """
    # ... entry_speed_kmh, apex_speed_kmh, etc.
    entry_speed_kmh: float
    apex_speed_kmh: float
    exit_speed_kmh: float
    avg_speed_kmh: float
    max_speed_kmh: float
    min_speed_kmh: float
    min_speed_m: float

    deceleration_rate: float
    acceleration_rate: float

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason:str="no-speed-measurements-detected"):
        return cls(
            entry_speed_kmh=math.nan, apex_speed_kmh=math.nan, exit_speed_kmh=math.nan,
            avg_speed_kmh=math.nan, max_speed_kmh=math.nan, min_speed_kmh=math.nan,
            min_speed_m=math.nan, deceleration_rate=math.nan, acceleration_rate=math.nan, reason=reason, status=StatusEnum.empty
        )

@dataclass(frozen=True)
class GForceMetrics(Emptyable):
    # ... g_lat_avg, g_lon_max, etc.
    # G-Forces
    g_lat_avg: float
    g_lat_max: float
    g_lat_min: float
    g_lon_avg: float
    g_lon_max: float
    g_lon_min: float

    g_force_vector_avg: float
    g_force_vector_min: float
    g_force_vector_max: float

    g_force_vector_smoothness: float
    g_force_vector_score: float

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason: str = "no-gForce-measurements-detected"):
        return cls(
            g_lat_avg=math.nan, g_lat_max=math.nan, g_lat_min=math.nan,
            g_lon_avg=math.nan, g_lon_max=math.nan, g_lon_min=math.nan,
            g_force_vector_avg=math.nan, g_force_vector_min=math.nan, g_force_vector_max=math.nan,
            g_force_vector_smoothness=math.nan, g_force_vector_score=math.nan, status=StatusEnum.empty,
            reason=reason
        )

@dataclass(frozen=True)
class ThrottleMetrics(Emptyable):
    # ... avg_throttle, ttf95, etc.
    avg_throttle: float
    min_throttle: float
    max_throttle: float
    min_throttle_m: float
    max_throttle_m: float

    integral: float
    acceleration_delta_m: float
    acceleration_delta_s: float
    acceleration_rate: float
    ttf95: float
    throttle_smoothness: float  # df[THROTTLE].diff().std()
    exit_throttle_init_m: float

    status: StatusEnum = StatusEnum.ok
    reason: str = None


    @classmethod
    def empty(cls, reason: str = "no-gForce-measurements-detected"):
        return cls(
            avg_throttle=math.nan, min_throttle=math.nan, max_throttle=math.nan,
            min_throttle_m=math.nan, max_throttle_m=math.nan,
            integral=math.nan, acceleration_delta_m=math.nan, acceleration_rate=math.nan,
            acceleration_delta_s=math.nan, ttf95=math.nan, throttle_smoothness=math.nan,
            exit_throttle_init_m=math.nan, status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class TrailBrakeMetrics(Emptyable):
    start_m: float
    end_m: float
    start_speed_kmh: float
    end_speed_kmh: float

    delta_s: float
    integral: float

    corr_brake_roty: float

    release_rate: float # df[BRAKE].diff().avg()
    stability: float    # df[BRAKE].diff().std()

    status: StatusEnum = StatusEnum.ok
    reason: Optional[str] = None

    @property
    def release_per_m(self):
        _delta = self.delta_m
        if math.isnan(_delta) or math.isnan(self.integral) or _delta == 0:
            return math.nan
        return self.integral / _delta


    @property
    def release_per_s(self):
        _delta = self.delta_s
        if math.isnan(_delta) or math.isnan(self.integral) or _delta == 0:
            return math.nan
        return self.integral / _delta


    @property
    def delta_m(self):
        if math.isnan(self.start_m) or math.isnan(self.end_m):
            return math.nan
        return self.end_m - self.start_m


    @property
    def speed_delta_kmh(self):
        if math.isnan(self.end_speed_kmh) or math.isnan(self.start_speed_kmh):
            return math.nan
        return self.end_speed_kmh - self.start_speed_kmh


    @classmethod
    def empty(cls, reason: str = "no-trailbrake-detected") -> "TrailBrakeMetrics":
        return cls(
            start_m=math.nan, end_m=math.nan, start_speed_kmh=math.nan, end_speed_kmh=math.nan,
            delta_s=math.nan, integral=math.nan, corr_brake_roty=math.nan, release_rate=math.nan,
            stability=math.nan, status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class BrakeMetrics(Emptyable):
    brake_point_m: float
    brake_point_speed: float
    brake_release_m: float
    brake_release_speed: float
    brake_delta_s: float

    max_brake: float
    avg_brake: float

    overall_brake_force: float
    tbf95_s: float
    trail_brake: TrailBrakeMetrics

    status: StatusEnum = StatusEnum.ok
    reason: Optional[str] = None

    @property
    def brake_force_per_meter(self) -> float:
        d = self.brake_delta_m
        return self.overall_brake_force / d if (d != 0 and not math.isnan(d)) else math.nan

    @property
    def brake_force_per_second(self) -> float:
        d = self.brake_delta_s
        return self.overall_brake_force / d if (d != 0 and not math.isnan(d)) else math.nan

    @property
    def brake_delta_m(self) -> float:
        if math.isnan(self.brake_release_m) or math.isnan(self.brake_point_m):
            return math.nan
        return self.brake_release_m - self.brake_point_m

    @classmethod
    def empty(cls, reason: str = "no-braking-detected") -> "BrakeMetrics":
        return cls(
            brake_point_m=math.nan, brake_point_speed=math.nan,
            brake_release_m=math.nan, brake_release_speed=math.nan,
            brake_delta_s=math.nan, max_brake=math.nan, avg_brake=math.nan,
            trail_brake=TrailBrakeMetrics.empty(reason=reason),
            overall_brake_force=0.0, tbf95_s=math.nan,
            status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class SteerMetrics(Emptyable):
    avg_steerangle: float
    max_steerangle: float
    max_steerangle_m: float
    steering_smoothness: float # df[STEERANGLE].diff().std()

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason:str="no-steer-metrics-found"):
        return cls(
            avg_steerangle=math.nan, max_steerangle=math.nan, max_steerangle_m=math.nan,
            steering_smoothness=math.nan, status=StatusEnum.empty, reason=reason
        )

class TyreMetrics(Emptyable):
    pass


# --- Stufe 2: Zusammengesetzte Metriken ---

@dataclass(frozen=True)
class CarDynamics(Emptyable):
    """Beschreibt die physikalische Bewegung des Fahrzeugs."""
    speed: SpeedMetrics
    g_force: GForceMetrics

    status: StatusEnum = StatusEnum.ok
    reason: str = None
    # roty: RotyMetrics
    # Hier könnten zukünftig z.B. Reifendaten hinzukommen

    @classmethod
    def empty(cls, reason="missing-car-dynamics") -> "CarDynamics":
        return cls(
            speed=SpeedMetrics.empty(reason=reason), g_force=GForceMetrics.empty(reason=reason),
            status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class DriverPerformance(Emptyable):
    """Fasst alle Aktionen des Fahrers zusammen."""
    throttle: ThrottleMetrics
    brake: BrakeMetrics
    steer: SteerMetrics
    # Hier könnten z.B. Lenk-Metriken hinzukommen

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    # roty: RotyMetrics
    # Hier könnten zukünftig z.B. Reifendaten hinzukommen

    @classmethod
    def empty(cls, reason="missing-car-dynamics") -> "DriverPerformance":
        return cls(
            throttle=ThrottleMetrics.empty(reason=reason), brake=BrakeMetrics.empty(reason=reason),
            steer=SteerMetrics.empty(reason=reason), status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class PerformanceScores(Emptyable):
    """Enthält alle abgeleiteten Bewertungen und Scores."""
    smoothness_score: float
    braking_score: float
    throttle_score: float

    status: StatusEnum = StatusEnum.ok
    reason: str = None
    @classmethod
    def empty(cls, reason="missing-scores"):
        return cls(
            smoothness_score=math.nan, braking_score=math.nan, throttle_score=math.nan,
            status=StatusEnum.empty, reason=reason
        )


# --- Stufe 3: Analyse-Einheit ---

@dataclass(frozen=True)
class CornerMetrics(Emptyable):
    time_delta_s: float
    dynamics: Optional[CarDynamics] = None
    driver: Optional[DriverPerformance] = None
    scores: Optional[PerformanceScores] = None

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            time_delta_s=math.nan, dynamics=CarDynamics.empty(reason=reason), driver=DriverPerformance.empty(reason=reason),
            scores=PerformanceScores.empty(reason=reason), status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class Corner(Emptyable):
    id: int
    name: str
    start_m: float
    apex_m: float
    end_m: float

    metrics: Optional[CornerMetrics] = field(
    default_factory=lambda: CornerMetrics.empty(
        reason="optional-default-corner-metrics-in-corner-dataclass"
    )
)

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            id=0, name="", start_m=math.nan, apex_m=math.nan, end_m=math.nan,
            status=StatusEnum.empty, reason=reason
        )














