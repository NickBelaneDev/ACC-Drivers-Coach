from pathlib import Path
import openpyxl
import pandas as pd
from logger import get_logger
from src.lap_dataclasses import CornerMetrics
from src.motec_csv_practice import TelemetryLoader
from src.telemetry_analyzer import Analyze

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"


class LapTelemetry:
    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df = lap_df
        self.analyze = Analyze(lap_df)

    def _get_segment_data(self, segment_id: int) -> dict:
        if 0 > segment_id > self.lap_df["segment_id_x"].max():
            raise IndexError(f"segment_id: {segment_id} out of range!")

        segment = self.lap_df[self.lap_df["segment_id_x"] == segment_id]

        segment_start = segment["segmentStart_m"].iloc[0]
        segment_end = segment["segmentEnd_m"].iloc[0]

        def _get_corner_dfs_from_seg_df(segment_df: pd.DataFrame) -> list[CornerMetrics]:
            """

            :param segment_df:
            :return: All corner_dfs from a segment together in a list
            """
            _corner_dfs = []
            corner_ids = segment_df["corner_ids"].iloc[0]
            for corner_id in corner_ids:
                # if corner_id is invalid
                if 0 > corner_id > self.lap_df["corner_id"].max():
                    raise ValueError(f"corner_id '{corner_id}' out of range")
                # load all relevant raw corner_data
                corner_df = segment_df[segment_df["corner_id"] == corner_id]
                corner_metrics = self.analyze.corner(corner_df)
                _corner_dfs.append(corner_metrics)
            return _corner_dfs

        time_delta = self.analyze.get_time_delta(segment_start, segment_end)
        corner_dfs = _get_corner_dfs_from_seg_df(segment)
        #corner_data = [corner for corner in Analyze.corner()]

        print(corner_dfs)
        # Hier muss ich die CornerMetrics haben und kann dann mit einer
        # Loop alles im Dictionary füllen, was an Kurvendaten da ist.

        segment_data = {
            "metrics":{
                "avgThrottle": segment["THROTTLE"].mean(),
                "avgBreak": segment["BRAKE"].mean(),
                "avgSpeed": segment["SPEED"].mean(),
                "topSpeed": segment["SPEED"].max(),
                "minSpeed": segment["SPEED"].min(),
                "timeDelta": time_delta
            },

            "geo":{
                "start_m": segment_start,
                "end_m": segment_end,
                "totalDistance": segment_end - segment_start
            },

            "corners":[
                {
                "id": "EMPTY",   # later corner.id
                "name": "EMPTY", # later corner.name
                "metrics":{
                    "entry_speed_kmh": float,
                    "apex_speed_kmh": float,
                    "exit_speed_kmh": float,
                    "avg_speed_kmh": float,
                    "min_speed_kmh": float,
                    "min_speed_m": float,

                    # G-Forces
                    "g_lat_avg": float,
                    "g_lat_max": float,
                    "g_lat_min": float,
                    "g_long_avg": float,
                    "g_long_max": float,
                    "g_long_min": float,

                    # Driver's Input
                    "avg_steering_dgr": float,
                    "max_steering_dgr": float,
                    "max_steering_m": float,

                    "avg_brake": float,
                    "max_brake": float,

                    # OPTIONAL!
                    "tbf95_s": Optional[float],  # tbf95_s = 'Time where Brake-Input >= 95% in seconds'

                    "avg_throttle": float,
                    "ttf95_s": Optional[float],  # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

                    # Abstract Metrics
                    "brake_point_m": Optional[float],  #
                    "brake_delta_m": Optional[float],  #
                    "brake_delta_s": Optional[float],  #
                    "trail_brake_delta_s": Optional[float],
                    "trail_brake_delta_m": Optional[float],

                    "exit_throttle_init_m": Optional[float],
                    # Measurement from where the driver is on the gas again on corner_exit.
                    "avg_exit_throttle": Optional[float],  # avg. throttle input from apex_m to exit_m + 100
                    "exit_speed_delta_s": Optional[float],  # avg. Speed from apex_m to exit_m + 100m

                    "rolling_delta_s": Optional[float],  # Time/s without throttle or brake
                    "rolling_delta_m": Optional[float],

                    "steering_delta_s": Optional[float],

                    "time_delta_s": float,
                    "cpi_factor": Optional[float],

                }
            } # ACHTUNG HIER WEITERMACHEN!!

            for corner_metric in corner_dfs]
        }


        for key in segment_data["metrics"]:
            segment_data["metrics"][key]  = round(segment_data["metrics"][key], 3)

        log.info(f"segment_data successfully loaded: {segment_data}")

        return segment_data

    def get_all_segments(self):
        segments_num = self.lap_df["segment_id_x"].max()
        all_segments = []

        for idx in range(1, segments_num + 1):
            all_segments.append(self._get_segment_data(idx))
            pass
        return all_segments

if __name__ == "__main__":
    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER

    telemetry_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    #print(telemetry_df.info())
    lap_record = LapTelemetry(telemetry_df)
    lap_user = LapTelemetry(user_df)

    u_all_segments = lap_user.get_all_segments()

    total_time_r = 0

    #print("======================")
    total_time_u = 0
    for segment in u_all_segments:
    #    print("====== SEGMENT =======")
        for k, v in segment.items():
            print(f"{k}: {v}")
        total_time_u += segment["metrics"]["timeDelta"]
    #print(f"total_time_r: {total_time_r}")

    #print(f"Segments: {lap.get_all_segments()}")
