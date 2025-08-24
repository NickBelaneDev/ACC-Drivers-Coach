from pathlib import Path
import openpyxl
import pandas as pd
from logger import get_logger
from src.motec_csv_practice import TelemetryLoader

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"


class LapTelemetry:
    def __init__(self, lap_df: pd.DataFrame):
        self.lap_df = lap_df


    def _get_time_delta(self, area: pd.DataFrame, start_m: int, end_m: int):
        time_start_df =  self.lap_df[self.lap_df["Distance"] == start_m]
        time_start = time_start_df["Time"].iloc[0]

        time_end_df = self.lap_df[self.lap_df["Distance"] == end_m]
        time_end = time_end_df["Time"].iloc[0]

        return time_end - time_start


    def get_all_segments(self):
        segments_num = self.lap_df["segment_id_x"].max()
        all_segments = []

        for idx in range(1, segments_num + 1):
            all_segments.append(self._get_segment_data(idx))
            pass
        return all_segments

    def _get_segment_data(self, segment_id: int) -> dict:
        if 0 > segment_id > self.lap_df["segment_id_x"].max():
            raise IndexError(f"segment_id: {segment_id} out of range!")

        segment = self.lap_df[self.lap_df["segment_id_x"] == segment_id]

        segment_start = segment["segmentStart_m"].iloc[0]
        segment_end = segment["segmentEnd_m"].iloc[0]

        time_delta = self._get_time_delta(self.lap_df, segment_start, segment_end)

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
            ]
        }

        for key in segment_data["metrics"]:
            segment_data["metrics"][key]  = round(segment_data["metrics"][key], 3)

        log.info(f"segment_data successfully loaded: {segment_data}")
        return segment_data
    def _get_corner_data(self, corner_id: int):
        if 0 > corner_id > self.lap_df["corner_id"].max():
            raise ValueError(f"corner_id '{corner_id}' out of range")



if __name__ == "__main__":
    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER

    telemetry_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")


    #print(telemetry_df.info())
    lap_record = LapTelemetry(telemetry_df)
    lap_user = LapTelemetry(user_df)

    #segment = lap._get_segment_data(5)
    #segment.to_excel(f"Spa_segment_{5}.xlsx", index=False)
    r_all_segments = lap_record.get_all_segments()
    u_all_segments = lap_user.get_all_segments()

    total_time = 0
    for segment in r_all_segments:
        print(segment)
        total_time += segment["metrics"]["timeDelta"]
    print("======================")

    for segment in u_all_segments:
        print(segment)
        total_time += segment["metrics"]["timeDelta"]



    print(f"total_time{total_time}")
    #print(f"Segments: {lap.get_all_segments()}")
