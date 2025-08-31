from pathlib import Path
import openpyxl
import pandas as pd
from logger import get_logger
from src.lap_dataclasses import CornerMetrics, Corner
from src.telemetry_loader import TelemetryLoader
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
        max_seg = int(self.lap_df["segment_id_x"].max())
        if segment_id < 0 or segment_id > max_seg:
            raise IndexError(f"segment_id: {segment_id} out of range 0..{max_seg}")

        segment = self.lap_df[self.lap_df["segment_id_x"] == segment_id]

        segment_start = segment["segmentStart_m"].iloc[0]
        segment_end = segment["segmentEnd_m"].iloc[0]

        def _get_corner_dfs_from_seg_df(segment_df: pd.DataFrame) -> list[Corner]:
            """

            :param segment_df:
            :return: All corner_dfs from a segment together in a list
            """
            _corners = []
            corner_ids = segment_df["corner_ids"].iloc[0]

            corner_ids = sorted(set(int(c) for c in corner_ids))
            for corner in corner_ids:
                print(type(corner))

            #print(f"corner_ids: {corner_ids}")
            for corner_id in corner_ids:
                # if corner_id is invalid
                max_corner = int(self.lap_df["corner_id"].max())
                if corner_id < 0 or corner_id > max_corner:
                    raise ValueError(f"corner_id '{corner_id}' out of range 0..{max_corner}")
                # load all relevant raw corner_data
                _corner_df = segment_df[segment_df["corner_id"] == corner_id]
                if _corner_df.empty:
                    # try float fallback (falls Quelle noch floatig ist)
                    _corner_df = segment_df[segment_df["corner_id"] == float(corner_id)]
                if _corner_df.empty:
                    log.warning(f"Segment {segment_id}: corner_id {corner_id} nicht gefunden (Typproblem?)")
                    continue

                _corner = self.analyze.corner(_corner_df)
                _corners.append(_corner)

            return _corners

        time_delta = self.analyze.get_time_delta(segment_start, segment_end)
        corners = _get_corner_dfs_from_seg_df(segment)
        for _c in corners:
            print(f"id: {_c.id}")


        #log.debug(f"corners: {corners}")

        # Hier muss ich schon ie CornerMetrics haben und kann dann mit einer
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
                "id": corner.id,   # later corner.id
                "name": corner.name, # later corner.name
                "metrics":{
                    "entry_speed_kmh": corner.metrics.entry_speed_kmh,
                    "apex_speed_kmh": corner.metrics.apex_speed_kmh,
                    "exit_speed_kmh": corner.metrics.exit_speed_kmh,
                    "avg_speed_kmh": corner.metrics.avg_speed_kmh,
                    "min_speed_kmh": corner.metrics.min_speed_kmh,
                    "min_speed_m": corner.metrics.min_speed_m,

                    # G-Forces
                    "g_lat_avg": corner.metrics.g_lat_avg,
                    "g_lat_max": corner.metrics.g_lat_max,
                    "g_lat_min": corner.metrics.g_lat_min,
                    "g_long_avg": corner.metrics.g_lon_avg,
                    "g_long_max": corner.metrics.g_lon_max,
                    "g_long_min": corner.metrics.g_lon_min,

                    # Driver's Input
                    "avg_steering_dgr": corner.metrics.avg_steerangle,
                    "max_steering_dgr": corner.metrics.max_steerangle,
                    "max_steering_m": corner.metrics.max_steerangle_m,

                    "avg_brake": corner.metrics.avg_brake,
                    "max_brake": corner.metrics.max_brake,

                    # OPTIONAL!
                    "tbf95_s": corner.metrics.tbf95_s,  # tbf95_s = 'Time where Brake-Input >= 95% in seconds'

                    "avg_throttle": corner.metrics.avg_throttle,
                    "ttf95_s": corner.metrics.ttf95_s,  # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

                    # Abstract Metrics
                    "brake_point_m": corner.metrics.brake_point_m,  #
                    "brake_delta_m": corner.metrics.brake_delta_m,  #
                    "brake_delta_s": corner.metrics.brake_delta_s,  #
                    "trail_brake_delta_s": corner.metrics.trail_brake_delta_s,
                    "trail_brake_delta_m": corner.metrics.trail_brake_delta_m,

                    "exit_throttle_init_m": corner.metrics.exit_throttle_init_m,
                    # Measurement from where the driver is on the gas again on corner_exit.
                    "avg_exit_throttle": corner.metrics.avg_exit_throttle,  # avg. throttle input from apex_m to exit_m + 100
                    "exit_speed_delta_s": corner.metrics.exit_speed_delta_s,  # avg. Speed from apex_m to exit_m + 100m

                    "rolling_delta_s": corner.metrics.rolling_delta_s,  # Time/s without throttle or brake
                    "rolling_delta_m": corner.metrics.rolling_delta_m,

                    "time_delta_s": corner.metrics.time_delta_s,
                    "cpi_factor": corner.metrics.cpi_factor,
                }
            } # ACHTUNG HIER WEITERMACHEN!!

            for corner in corners]
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

    print("======================")
    for segment in u_all_segments:
        for k,_ in segment.items():
            if k == "corners":
                for corner in segment[k]:
                    print(corner["id"])

