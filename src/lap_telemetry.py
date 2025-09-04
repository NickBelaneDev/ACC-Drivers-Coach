from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from logger import get_logger
from src.lap_dataclasses import CornerMetrics, Corner, Segment
from src.telemetry_loader import TelemetryLoader
from src.lap_analyzer import LapAnalyzer
from src.telemetry_utils import get_corner_df_from_df
import math

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"

class LapTelemetry:
    def __init__(self, lap_df: pd.DataFrame):
        """
        Get all relevant data metrics for the LLM.
        :param lap_df:
        """
        # Calculate the gForceVector, I know it's ugly yet, will fix it later.
        self.lap_df = LapAnalyzer.calc_g_force_vector(lap_df)
        self.analyze = LapAnalyzer(self.lap_df)

    def get_lap_df(self):
        return self.lap_df

    def get_corner_df_from_df(self, corner_id: int, df:pd.DataFrame) -> pd.DataFrame:
        try:
            max_corner = int(self.lap_df["corner_id"].max())
        except Exception as e:
            print("max_corner not found!")
            max_corner = int(df["corner_id"].max())
            pass


        if corner_id < 0 or corner_id > max_corner:
            raise ValueError(f"corner_id '{corner_id}' out of range 0..{max_corner}")

        # load all relevant raw corner_data
        _corner_df = df[df["corner_id"] == corner_id]
        if _corner_df.empty:
            # try float fallback (if source is still floaty)
            _corner_df = df[df["corner_id"] == float(corner_id)]

        if _corner_df.empty:
            log.warning(f"Segment {df}: corner_id {corner_id} nicht gefunden (Typproblem?)")

        return _corner_df

    def _get_analyzed_corners_from_df(self, df:pd.DataFrame):
        """
        The given Dataframe must have corner_ids as alist in iloc[0]
        :param df:
        :return:
        """

        _corners = []
        corner_ids = df["corner_ids"].iloc[0]

        if not corner_ids:
            raise ValueError(f"corner_ids_df is empty!\n{corner_ids}")

        corner_ids = sorted(set(int(c) for c in corner_ids))

        for corner_id in corner_ids:
            # if corner_id is invalid


            _corner_df = get_corner_df_from_df(corner_id, df)
            _corner = self.analyze.corner(_corner_df)
            _corners.append(_corner)

        return _corners
    def _get_segment_data(self, segment_id: int) -> dict:
        """

        :param segment_id:
        :return: A dictionary with the corresponding segments and laps.
        """
        max_seg = int(self.lap_df["segment_id_x"].max())
        if segment_id < 0 or segment_id > max_seg:
            raise IndexError(f"segment_id: {segment_id} out of range 0..{max_seg}")

        segment_df = self.lap_df[self.lap_df["segment_id_x"] == segment_id]

        segment_start = segment_df["segmentStart_m"].iloc[0]
        segment_end = segment_df["segmentEnd_m"].iloc[0]
        time_delta = self.analyze.get_time_delta(segment_start, segment_end)

        corners = self._get_analyzed_corners_from_df(segment_df)

        # Dieses Dictionary sollst du für Streamlit verfügbar machen.
        segment_data = {
            "metrics": {
                "avgThrottle": segment_df["THROTTLE"].mean(),
                "avgBreak": segment_df["BRAKE"].mean(),
                "avgSpeed": segment_df["SPEED"].mean(),
                "topSpeed": segment_df["SPEED"].max(),
                "minSpeed": segment_df["SPEED"].min(),
                "maxGForceVector": segment_df["gForceVector"].mean(),
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
                "name": corner.name,
                "start_m": corner.start_m,
                "end_m": corner.end_m,
                "apex_m": corner.apex_m,
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

                    "tbf95_s": corner.metrics.tbf95_s,  # tbf95_s = 'Time where Brake-Input >= 95% in seconds'

                    # Abstract Metrics
                    "brake_point_m": corner.metrics.brake_point_m,
                    "brake_release_m": corner.metrics.brake_release_m, #
                    "brake_delta_m": corner.metrics.brake_delta_m,  #
                    "brake_delta_s": corner.metrics.brake_delta_s,  #
                    "trail_brake_delta_s": corner.metrics.trail_brake_delta_s,
                    "trail_brake_delta_m": corner.metrics.trail_brake_delta_m,
                    "trail_brake_start_m": corner.metrics.trail_brake_start_m,
                    "trail_brake_end_m": corner.metrics.trail_brake_end_m,

                    "avg_throttle": corner.metrics.avg_throttle,
                    "ttf95_s": corner.metrics.ttf95_s,  # ttf95_s = 'Time where Throttle-Input >= 95% in seconds'

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


        # Round all Data
        for key in segment_data["metrics"]:
            segment_data["metrics"][key]  = round(segment_data["metrics"][key], 3)

        for i, _ in enumerate(segment_data["corners"]):
            _corner = segment_data["corners"][i]
            for k in _corner:
                if k == "metrics":
                    for _key in _corner["metrics"]:
                        _corner["metrics"][_key] = round(_corner["metrics"][_key], 3)
            segment_data["corners"][i] = _corner

        log.info(f"segment_data successfully loaded: {segment_data}")

        return segment_data

    def get_segment_list(self) -> list:
        """
        Returns a list witch all analysed segments as Dictionaries inside.
        Ment to be sent to LLMs for drivers analysis.
        Do not use this, if you want to calc with the data!!
        :return:
        """
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

    u_all_segments = lap_user.get_segment_list()
    r_all_segments = lap_record.get_segment_list()




    total_time_r = 0

    print("======================")
    for segment in r_all_segments:
        for _k,_ in segment.items():
            if _k == "corners":
                for corner in segment[_k]:
                    print("======================")
                    print(f"{corner["id"]}\n"
                          f"{corner["name"]}\n"
                          f"start: {corner["start_m"]}  end: {corner["end_m"]}")

                    _metrics = corner["metrics"]["cpi_factor"]
                    print(_metrics)
                    #for o, l in _metrics.item():
                    #    print(f" - {o}: {l}")


