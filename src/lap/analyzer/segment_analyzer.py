from ..lap_dataclasses import (
    Segment,
    SegmentMetrics
)
import pandas as pd

class SegmentAnalyzer:
    @staticmethod
    def analyze(segment_df: pd.DataFrame) \
            -> Segment:

        if segment_df.empty:
            print("segment_df is empty!")

        seg_id = segment_df["segment_id_x"].iloc[0]
        corner_ids = segment_df["corner_ids"].iloc[0]
        seg_start = segment_df["Distance"].iloc[0]
        seg_end = segment_df["Distance"].iloc[-1]
        description = segment_df["segmentDescription"].iloc[0]

        start_speed_kmh = segment_df[segment_df["Distance"] == seg_start]["SPEED"].iloc[0]
        end_speed_kmh = segment_df[segment_df["Distance"] == seg_end]["SPEED"].iloc[0]
        start_time_s = segment_df[segment_df["Distance"] == seg_start]["Time"].iloc[0]
        end_time_s = segment_df[segment_df["Distance"] == seg_end]["Time"].iloc[0]
        time_delta_s = end_time_s - start_time_s

        avg_speed_kmh = segment_df["SPEED"].mean()
        max_speed_kmh = segment_df["SPEED"].max()
        min_speed_kmh = segment_df["SPEED"].min()

        avg_throttle = segment_df["THROTTLE"].mean()
        avg_brake = segment_df["BRAKE"].mean()


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


        return Segment(
            id=seg_id,
            corner_ids=corner_ids,
            start_m=seg_start,
            end_m=seg_end,
            description=description,
            metrics=analyzed_segment_metrics
        )