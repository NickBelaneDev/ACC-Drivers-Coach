from ..lap_dataclasses import (
    Segment,
    SegmentMetrics
)
import pandas as pd

class SegmentAnalyzer:
    """
    Analyzes high-level telemetry segments between corners.

    The ``SegmentAnalyzer`` processes a section of telemetry data representing
    a track segment (i.e., the distance between two defined corner zones).
    It computes key speed, timing, and control metrics such as average throttle,
    braking intensity, and total travel time.

    The result is returned as a ``Segment`` dataclass that contains both
    metadata (IDs, start/end distances, description) and the associated
    ``SegmentMetrics``.
    """
    @staticmethod
    def analyze(segment_df: pd.DataFrame) \
            -> Segment:
        """
        Analyze a telemetry DataFrame for a single track segment.

        This method extracts structural _information (segment ID, corner IDs,
        distances, and description) as well as aggregated driving metrics
        (speed, throttle, brake). It summarizes the driver’s performance
        over the segment in a ``SegmentMetrics`` object and wraps it into
        a ``Segment`` dataclass for further use.

        Parameters
        ----------
        segment_df : pandas.DataFrame
            The telemetry subset representing a single segment. Expected
            columns include:
            - ``segment_id_x`` : numeric ID of the segment
            - ``corner_ids`` : IDs of corners within the segment
            - ``segmentDescription`` : textual segment label
            - ``Distance`` : distance array of the segment
            - ``SPEED`` : vehicle speed (km/h)
            - ``Time`` : lap time (s)
            - ``THROTTLE`` : throttle input (%)
            - ``BRAKE`` : brake input (%)

        Returns
        -------
        Segment
            Dataclass containing the segment’s metadata and calculated
            metrics such as speed averages, throttle and brake usage.

        Notes
        -----
        - If the DataFrame is empty, a warning is printed but processing continues.
        - The returned ``Segment`` serves as a container for both metadata and
          analyzed performance statistics of the segment.
        """
        if segment_df.empty:
            print("segment_df is empty!")
        try:
            # --- Extract meta _information
            seg_id = segment_df["segment_id_x"].iloc[0]
            corner_ids = segment_df["corner_ids"].iloc[0]
            seg_start = segment_df["Distance"].iloc[0]
            seg_end = segment_df["Distance"].iloc[-1]
            description = segment_df["segmentDescription"].iloc[0]

            # --- Speed and timing characteristics
            start_speed_kmh = segment_df[segment_df["Distance"] == seg_start]["SPEED"].iloc[0]
            end_speed_kmh = segment_df[segment_df["Distance"] == seg_end]["SPEED"].iloc[0]
            start_time_s = segment_df[segment_df["Distance"] == seg_start]["Time"].iloc[0]
            end_time_s = segment_df[segment_df["Distance"] == seg_end]["Time"].iloc[0]
            time_delta_s = end_time_s - start_time_s

            # --- Aggregate averages for speed and inputs
            avg_speed_kmh = segment_df["SPEED"].mean()
            max_speed_kmh = segment_df["SPEED"].max()
            min_speed_kmh = segment_df["SPEED"].min()
            avg_throttle = segment_df["THROTTLE"].mean()
            avg_brake = segment_df["BRAKE"].mean()

        except Exception as e:
            return Segment.empty(reason=f"segment-analyzer\n"
                                        f"{e=} ")
        # --- Build metrics dataclass
        analyzed_segment_metrics = SegmentMetrics(
            id=seg_id,
            start_speed_kmh=start_speed_kmh,
            end_speed_kmh=end_speed_kmh,
            time_delta_s=time_delta_s,
            avg_speed_kmh=avg_speed_kmh,
            max_speed_kmh=max_speed_kmh,
            min_speed_kmh=min_speed_kmh,
            avg_throttle=avg_throttle,
            avg_brake=avg_brake
        )

        # --- Wrap metrics into segment container
        return Segment(
            id=seg_id,
            corner_ids=corner_ids,
            start_m=seg_start,
            end_m=seg_end,
            description=description,
            metrics=analyzed_segment_metrics
        )