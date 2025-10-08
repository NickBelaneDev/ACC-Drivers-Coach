from dataclasses import dataclass, field
from typing import Optional

import math
from abc import ABC, abstractmethod
from enum import Enum

# ====================================================
# version 1.01, date: 09.30.2025, © written by Robert Millotat
#
# Dataclasses define the structured telemetry payloads we pass between analyzers.
# They encapsulate both the computed metrics and a lightweight status protocol
# (ok/empty/invalid) to keep downstream code robust.

class StatusEnum(Enum):
    """Standard lifecycle flags for metric containers."""
    ok = "ok"
    empty = "empty"
    invalid = "invalid"
class Emptyable:
    """
    Mixin that provides a common status/empty protocol for dataclasses.

    Dataclasses inheriting from ``Emptyable`` implement:
      - ``empty(reason)``: classmethod returning a sentinel instance.
      - Predicate helpers: ``is_ok()``, ``is_empty()``, ``is_invalid()``.
      - ``get_reason()`` for human-readable failure context.
    """

    @classmethod
    @abstractmethod
    def empty(cls, reason:str):
        """
        Return a sentinel instance where numeric fields are ``math.nan``
        (or sensible neutral defaults) and ``status`` is ``StatusEnum.empty``.

        Parameters
        ----------
        reason : str
            Human-readable explanation why no valid data is present.

        Returns
        -------
        Any
            An instance of the concrete dataclass in an "empty" state.
        """
        raise NotImplementedError
    def is_ok(self) -> bool:
        """True iff the instance represents valid, computed metrics."""
        return getattr(self, "status", None) == StatusEnum.ok
    def is_empty(self) -> bool:
        """True iff the instance is a sentinel “empty” object."""
        return getattr(self, "status", None) == StatusEnum.empty
    def is_invalid(self) -> bool:
        """True iff the instance is explicitly marked as invalid."""
        return getattr(self, "status", None) == StatusEnum.invalid
    def get_reason(self) -> str:
        """Optional textual reason for empty/invalid states, else ``None``."""
        return getattr(self, "reason", None)

# --- Level 1: Atomic metrics -------------------------------------------------

@dataclass(frozen=True)
class SpeedMetrics(Emptyable):
    """
    Corner speed characteristics.

    Contains entry/apex/exit speeds, global statistics, the location of minimum
    speed, and coarse acceleration/deceleration rates across the corner window.
    """

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
    """
    Lateral/longitudinal and resultant g-force metrics.

    Includes averages, extrema, a smoothness proxy for the g-vector, and an
    integral “g-load score” over distance.
    """
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
    """
    Throttle usage and acceleration-phase characteristics.

    Captures overall throttle stats (avg/min/max, integral), acceleration window
    length in meters/seconds, average ramp rate, time to ≥95% (``ttf95``),
    a smoothness proxy, and the initial distance at which acceleration begins.
    """
    avg_throttle: float
    min_throttle: float
    max_throttle: float

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
            integral=math.nan, acceleration_delta_m=math.nan, acceleration_rate=math.nan,
            acceleration_delta_s=math.nan, ttf95=math.nan, throttle_smoothness=math.nan,
            exit_throttle_init_m=math.nan, status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class TrailBrakeMetrics(Emptyable):
    """
    Metrics describing the trail-braking phase.

    Includes geometric bounds, corresponding speeds, duration, integrated brake
    effort, correlation to yaw rate (ROTY), release rate and stability proxies.
    """
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
        """Brake effort per meter over the trail-brake span."""
        _delta = self.delta_m
        if math.isnan(_delta) or math.isnan(self.integral) or _delta == 0:
            return math.nan
        return self.integral / _delta


    @property
    def release_per_s(self):
        """Brake effort per second over the trail-brake duration."""
        _delta = self.delta_s
        if math.isnan(_delta) or math.isnan(self.integral) or _delta == 0:
            return math.nan
        return self.integral / _delta


    @property
    def delta_m(self):
        """Distance covered during trail braking (meters)."""
        if math.isnan(self.start_m) or math.isnan(self.end_m):
            return math.nan
        return self.end_m - self.start_m


    @property
    def speed_delta_kmh(self):
        """Speed change over trail braking (km/h)."""
        if math.isnan(self.end_speed_kmh) or math.isnan(self.start_speed_kmh):
            return math.nan
        return self.end_speed_kmh - self.start_speed_kmh


    @classmethod
    def empty(cls, reason: str="no-trailbrake-detected") -> "TrailBrakeMetrics":
        return cls(
            start_m=math.nan, end_m=math.nan, start_speed_kmh=math.nan, end_speed_kmh=math.nan,
            delta_s=math.nan, integral=math.nan, corr_brake_roty=math.nan, release_rate=math.nan,
            stability=math.nan, status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class BrakeMetrics(Emptyable):
    """
    Comprehensive braking metrics for a corner.

    Contains brake onset/release positions and speeds, braking duration, peak and
    average brake values, overall brake force (integral), time at ≥95% brake, and
    nested ``TrailBrakeMetrics``.
    """
    brake_point_m: float
    brake_point_speed: float
    brake_release_m: float
    brake_release_speed: float
    brake_window_s: float

    max_brake: float
    avg_brake: float

    overall_brake_force: float
    tbf95_s: float
    trail_brake: TrailBrakeMetrics

    status: StatusEnum = StatusEnum.ok
    reason: Optional[str] = None

    @property
    def brake_force_per_meter(self) -> float:
        """Average braking effort per meter within the main braking interval."""
        d = self.brake_window_m
        return self.overall_brake_force / d if (d != 0 and not math.isnan(d)) else math.nan

    @property
    def brake_force_per_second(self) -> float:
        """Average braking effort per second within the main braking interval."""
        d = self.brake_window_s
        return self.overall_brake_force / d if (d != 0 and not math.isnan(d)) else math.nan

    @property
    def brake_window_m(self) -> float:
        """Distance from brake onset to full release (meters)."""
        if math.isnan(self.brake_release_m) or math.isnan(self.brake_point_m):
            return math.nan
        return self.brake_release_m - self.brake_point_m

    @classmethod
    def empty(cls, reason: str = "no-braking-detected") -> "BrakeMetrics":
        return cls(
            brake_point_m=math.nan, brake_point_speed=math.nan,
            brake_release_m=math.nan, brake_release_speed=math.nan,
            brake_window_s=math.nan, max_brake=math.nan, avg_brake=math.nan,
            trail_brake=TrailBrakeMetrics.empty(reason=reason),
            overall_brake_force=0.0, tbf95_s=math.nan,
            status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class SteerMetrics(Emptyable):
    """
    Steering input and rotation dynamics.

    Includes average/peak steering angle and its location, steering integral and
    smoothness, plus yaw (ROTY) maxima, integral and smoothness.
    """
    avg_steerangle: float
    max_steerangle: float
    max_steerangle_m: float
    steering_integral: float
    steering_smoothness: float  # df[STEERANGLE].diff().std()

    max_rotation: float
    rotation_integral: float
    rotation_smoothness: float

    steering_throttle_correlation: float = None
    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason:str="no-steer-metrics-found"):
        return cls(
            avg_steerangle=math.nan, max_steerangle=math.nan, max_steerangle_m=math.nan, steering_integral=math.nan,
            steering_smoothness=math.nan, max_rotation=math.nan, rotation_integral=math.nan,
            rotation_smoothness=math.nan, status=StatusEnum.empty, reason=reason
        )

class TyreMetrics(Emptyable):
    """Placeholder for future tyre-related metrics (temperatures, slip, wear)."""
    pass



# --- Level 2: Composite metrics ---------------------------------------------

@dataclass(frozen=True)
class CarDynamics(Emptyable):
    """
    Physical vehicle behavior within a corner.

    Bundles speed and g-force metrics; future extensions may add yaw/roll or tyre data.
    """
    speed: SpeedMetrics
    g_force: GForceMetrics

    status: StatusEnum = StatusEnum.ok
    reason: str = None


    @classmethod
    def empty(cls, reason="missing-car-dynamics") -> "CarDynamics":
        return cls(
            speed=SpeedMetrics.empty(reason=reason), g_force=GForceMetrics.empty(reason=reason),
            status=StatusEnum.empty, reason=reason
        )


@dataclass(frozen=True)
class DriverPerformance(Emptyable):
    """
    Aggregated driver inputs across the corner.

    Collects throttle, brake and steering metrics into one container for
    driver-focused analysis and scoring.
    """
    throttle: ThrottleMetrics
    brake: BrakeMetrics
    steer: SteerMetrics


    status: StatusEnum = StatusEnum.ok
    reason: str = None


    @classmethod
    def empty(cls, reason="missing-car-dynamics") -> "DriverPerformance":
        return cls(
            throttle=ThrottleMetrics.empty(reason=reason), brake=BrakeMetrics.empty(reason=reason),
            steer=SteerMetrics.empty(reason=reason), status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class PerformanceScores(Emptyable):
    """
    Derived, normalized scores.

    Intended for high-level KPIs like smoothness, braking quality and throttle control.
    """
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



# --- Level 3: Analysis unit --------------------------------------------------


@dataclass(frozen=True)
class CornerMetrics(Emptyable):
    """
    Full metric package for a single corner.

    This container aggregates all computed analytics for one corner: the elapsed
    time inside the corner window (from the analyzer’s definition) and two
    composite bundles that separate the vehicle’s physical behavior from the
    driver’s control inputs:

      • ``dynamics`` → physical vehicle response (e.g., g-forces, speed profile),
      • ``driver``   → human inputs and their patterns (throttle, brake, steer).

    Together, these provide a coherent snapshot that higher-level modules
    (e.g., coaching, scoring, setup-recommendation) can consume without
    touching raw telemetry. Instances follow the common status protocol
    (``StatusEnum``) defined by ``Emptyable`` to make downstream code robust.

    Attributes
    ----------
    time_delta_s : float
        Elapsed time (in seconds) within the corner window as used by the
        analyzer (typically derived from min/max of ``Time`` within the
        per-corner DataFrame).
    dynamics : Optional[CarDynamics]
        Physical vehicle metrics bundle (speed metrics + g-force metrics).
        May be an empty composite if inputs were invalid/missing.
    driver : Optional[DriverPerformance]
        Driver input metrics bundle (throttle, brake, steering). May be empty.
    status : StatusEnum
        Lifecycle flag (``ok``, ``empty``, ``invalid``).
    reason : str
        Optional human-readable explanation for non-OK states (for logging/UI).

    Notes
    -----
    - Consumers should prefer the predicate helpers ``is_ok()``, ``is_empty()``,
      ``is_invalid()`` over direct ``status`` checks.
    - Empty composites in ``dynamics`` / ``driver`` indicate error handling
      occurred upstream but allow the object to remain structurally valid.
    """
    time_delta_s: float
    dynamics: Optional[CarDynamics] = None
    driver: Optional[DriverPerformance] = None
    #scores: Optional[PerformanceScores] = None // We will add this later on!

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            time_delta_s=math.nan,
            dynamics=CarDynamics.empty(reason=reason),
            driver=DriverPerformance.empty(reason=reason),
            # scores=PerformanceScores.empty(reason=reason),
            status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class Corner(Emptyable):
    """
        Corner entity: identity, geometry and metrics.

        Represents a single corner as a domain entity that combines:
          • a stable identity (``id``, ``name``),
          • track geometry references in meters (``start_m``, ``apex_m``, ``end_m``),
          • an optional ``CornerMetrics`` payload with all computed analytics.

        This class is the canonical transport type for corner-level workflows and
        is intentionally minimal: it carries just enough metadata to align telemetry
        windows and cross-reference with track models or maps.

        Attributes
        ----------
        id : int
            Unique corner identifier (track-model dependent).
        name : str
            Human-readable name (e.g., "Pouhon", "T1 Hairpin").
        start_m : float
            Track distance at corner start (meters along lap distance).
        apex_m : float
            Track distance at the geometric/telemetry apex (meters).
        end_m : float
            Track distance where the corner ends (meters).
        metrics : Optional[CornerMetrics]
            Computed metric bundle. Defaults to an **empty** placeholder so that
            downstream code can safely access fields without Nones.
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional explanation for non-OK states.

        Examples
        --------
        >>> # Accessing car dynamics safely
        >>> if corner.metrics and corner.metrics.dynamics.is_ok():
        ...     v_max = corner.metrics.dynamics.speed.max_speed_kmh
    """
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


@dataclass(frozen=True)
class Lap(Emptyable):
    """
        Lap container combining metadata and aggregated structures.

        Encapsulates a single lap’s identity and provenance (file, driver), optional
        pre-computed per-segment deltas for quick comparisons, and the ordered list
        of ``Corner`` entities that form the lap. This class is the top-level unit
        for lap-wise analytics, export, and cross-lap benchmarking.

        Attributes
        ----------
        id : int
            Unique lap identifier (session-tooling dependent).
        name : str
            Display name or label for the lap (e.g., "PB 2:17.750").
        file : Optional[str]
            Source filename or URI used to derive telemetry (if applicable).
        driver : Optional[str]
            Driver identifier/name associated with this lap.
        segment_time_deltas : Optional[float]
            Aggregated time delta across segments (optional pre-computation).
            Consumers may keep this ``nan`` and compute deltas on demand.
        corners : Optional[list[Corner]]
            The corners that compose this lap, in lap order.
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional explanation for non-OK states.

        Notes
        -----
        - The lap can be valid even if individual corners carry empty metrics; use
          the corner-level status helpers to gate detailed reads.
        - Keep ``file``/``driver`` optional to support datasets that do not carry
          those attributes.
    """
    id: int
    name: str
    file: Optional[str]
    driver: Optional[str]
    segment_time_deltas: Optional[float]
    corners: Optional[list[Corner]]

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            id=0, name="", file="", driver="", corners=[], segment_time_deltas=math.nan,
            status=StatusEnum.empty, reason=reason
        )


@dataclass(frozen=True)
class SegmentMetrics(Emptyable):
    @dataclass(frozen=True)
    class CornerMetrics(Emptyable):
        """
        Full metric package for a single corner.

        This container aggregates all computed analytics for one corner: the elapsed
        time inside the corner window (from the analyzer’s definition) and two
        composite bundles that separate the vehicle’s physical behavior from the
        driver’s control inputs:

          • ``dynamics`` → physical vehicle response (e.g., g-forces, speed profile),
          • ``driver``   → human inputs and their patterns (throttle, brake, steer).

        Together, these provide a coherent snapshot that higher-level modules
        (e.g., coaching, scoring, setup-recommendation) can consume without
        touching raw telemetry. Instances follow the common status protocol
        (``StatusEnum``) defined by ``Emptyable`` to make downstream code robust.

        Attributes
        ----------
        time_delta_s : float
            Elapsed time (in seconds) within the corner window as used by the
            analyzer (typically derived from min/max of ``Time`` within the
            per-corner DataFrame).
        dynamics : Optional[CarDynamics]
            Physical vehicle metrics bundle (speed metrics + g-force metrics).
            May be an empty composite if inputs were invalid/missing.
        driver : Optional[DriverPerformance]
            Driver input metrics bundle (throttle, brake, steering). May be empty.
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional human-readable explanation for non-OK states (for logging/UI).

        Notes
        -----
        - Consumers should prefer the predicate helpers ``is_ok()``, ``is_empty()``,
          ``is_invalid()`` over direct ``status`` checks.
        - Empty composites in ``dynamics`` / ``driver`` indicate error handling
          occurred upstream but allow the object to remain structurally valid.
        """
        time_delta_s: float
        dynamics: Optional[CarDynamics] = None
        driver: Optional[DriverPerformance] = None
        # scores: Optional[PerformanceScores] = None

        status: StatusEnum = StatusEnum.ok
        reason: str = None

        @classmethod
        def empty(cls, reason="missing-information"):
            return cls(
                time_delta_s=math.nan,
                dynamics=CarDynamics.empty(reason=reason),
                driver=DriverPerformance.empty(reason=reason),
                status=StatusEnum.empty, reason=reason
            )

    @dataclass(frozen=True)
    class Corner(Emptyable):
        """
        Corner entity: identity, geometry and metrics.

        Represents a single corner as a domain entity that combines:
          • a stable identity (``id``, ``name``),
          • track geometry references in meters (``start_m``, ``apex_m``, ``end_m``),
          • an optional ``CornerMetrics`` payload with all computed analytics.

        This class is the canonical transport type for corner-level workflows and
        is intentionally minimal: it carries just enough metadata to align telemetry
        windows and cross-reference with track models or maps.

        Attributes
        ----------
        id : int
            Unique corner identifier (track-model dependent).
        name : str
            Human-readable name (e.g., "Pouhon", "T1 Hairpin").
        start_m : float
            Track distance at corner start (meters along lap distance).
        apex_m : float
            Track distance at the geometric/telemetry apex (meters).
        end_m : float
            Track distance where the corner ends (meters).
        metrics : Optional[CornerMetrics]
            Computed metric bundle. Defaults to an **empty** placeholder so that
            downstream code can safely access fields without Nones.
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional explanation for non-OK states.

        Examples
        --------
        >>> # Accessing car dynamics safely
        >>> if corner.metrics and corner.metrics.dynamics.is_ok():
        ...     v_max = corner.metrics.dynamics.speed.max_speed_kmh
        """
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

    @dataclass(frozen=True)
    class Lap(Emptyable):
        """
            Lap container combining metadata and aggregated structures.

            Encapsulates a single lap’s identity and provenance (file, driver), optional
            pre-computed per-segment deltas for quick comparisons, and the ordered list
            of ``Corner`` entities that form the lap. This class is the top-level unit
            for lap-wise analytics, export, and cross-lap benchmarking.

            Attributes
            ----------
            id : int
                Unique lap identifier (session-tooling dependent).
            name : str
                Display name or label for the lap (e.g., "PB 2:17.750").
            file : Optional[str]
                Source filename or URI used to derive telemetry (if applicable).
            driver : Optional[str]
                Driver identifier/name associated with this lap.
            segment_time_deltas : Optional[float]
                Aggregated time delta across segments (optional pre-computation).
                Consumers may keep this ``nan`` and compute deltas on demand.
            corners : Optional[list[Corner]]
                The corners that compose this lap, in lap order.
            status : StatusEnum
                Lifecycle flag (``ok``, ``empty``, ``invalid``).
            reason : str
                Optional explanation for non-OK states.

            Notes
            -----
            - The lap can be valid even if individual corners carry empty metrics; use
              the corner-level status helpers to gate detailed reads.
            - Keep ``file``/``driver`` optional to support datasets that do not carry
              those attributes.
        """
        id: int
        name: str
        file: Optional[str]
        driver: Optional[str]
        segment_time_deltas: Optional[float]
        corners: Optional[list[Corner]]

        status: StatusEnum = StatusEnum.ok
        reason: str = None

        @classmethod
        def empty(cls, reason="missing-information"):
            return cls(
                id=0, name="", file="", driver="", corners=[], segment_time_deltas=math.nan,
                status=StatusEnum.empty, reason=reason
            )

    @dataclass(frozen=True)
    class SegmentMetrics(Emptyable):
        """
        Aggregated metrics for a track segment (between corners).

        Summarizes how the car was driven across a linear segment bounded by corner
        endpoints (e.g., exit of corner n to approach of corner n+1). Designed for
        coarse-grained performance comparisons (per-driver, per-setup, per-session).

        Attributes
        ----------
        id : int
            Segment identifier (track-model dependent).
        start_speed_kmh : float
            Speed at the segment's first sample (km/h).
        end_speed_kmh : float
            Speed at the segment's last sample (km/h).
        avg_speed_kmh : float
            Mean speed across the segment (km/h).
        max_speed_kmh : float
            Maximum recorded segment speed (km/h).
        min_speed_kmh : float
            Minimum recorded segment speed (km/h).
        avg_throttle : float
            Average throttle input over the segment (%).
        avg_brake : float
            Average brake input over the segment (%).
        time_delta_s : float
            Travel time across the segment (seconds).
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional explanation for non-OK states.

        Notes
        -----
        - This container does not include detailed corner dynamics; it is intentionally
          lightweight for reporting and aggregation across many laps.
        """
    id: int
    start_speed_kmh: float
    end_speed_kmh: float

    avg_speed_kmh: float
    max_speed_kmh: float
    min_speed_kmh: float

    avg_throttle: float
    avg_brake: float

    time_delta_s: float
    #total_cpi_score: float

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            id=0, start_speed_kmh=math.nan, end_speed_kmh=math.nan,
            avg_speed_kmh=math.nan, max_speed_kmh=math.nan,
            min_speed_kmh=math.nan, avg_throttle=math.nan,
            avg_brake=math.nan, time_delta_s=math.nan,
            status=StatusEnum.empty, reason=reason
        )

@dataclass(frozen=True)
class Segment(Emptyable):
    """
        Segment entity with geometry, membership and metrics.

        Represents a linear portion of the track between two corner-defined bounds
        and the set of corner IDs associated with that stretch. Pairs structural
        metadata (geometry + description) with a compact ``SegmentMetrics`` payload
        for fast summaries and comparisons.

        Attributes
        ----------
        id : int
            Segment identifier (track-model dependent).
        start_m : int
            Start position of the segment in track meters (lap distance).
        end_m : int
            End position of the segment in track meters (lap distance).
        description : str
            Human-readable label describing the segment (e.g., "Kemmel Straight").
        corner_ids : list
            Corner IDs included in or bounding this segment (track-model reference).
        metrics : Optional[SegmentMetrics]
            Aggregated performance metrics for the segment; may be empty depending
            on upstream validation and data availability.
        status : StatusEnum
            Lifecycle flag (``ok``, ``empty``, ``invalid``).
        reason : str
            Optional explanation for non-OK states.

        Examples
        --------
        >>> if segment.metrics and segment.metrics.is_ok():
        ...     print(segment.metrics.avg_speed_kmh)
    """
    id: int
    start_m: int
    end_m: int
    description: str
    corner_ids: list
    metrics: Optional[SegmentMetrics]

    status: StatusEnum = StatusEnum.ok
    reason: str = None

    @classmethod
    def empty(cls, reason="missing-information"):
        return cls(
            id=0, start_m=math.nan, end_m=math.nan,
            description="", corner_ids=[],
            metrics=SegmentMetrics.empty(reason="empty or invalid Segment object."),
            status=StatusEnum.empty, reason=reason
        )









