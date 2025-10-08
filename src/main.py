import pandas as pd
from src.lap.corner.corner_enums import ReturnFormat
from src.telemetry.telemetry_loader import TelemetryLoader
from src.logger import get_logger
import src.lap.metrics_enums as me

from pathlib import Path
from src.lap.lap_model import LapModel

import os
log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/telemetry_files/Spa-ferrari_296_gt3-fastest_lap_2-16-650.csv"
#user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-21-304.csv"
user_lap_file_path = "assets/MoTec/spa/telemetry_files/Spa-ferrari_296_gt3-hotlap_2-17-880.csv"



if __name__ == "__main__":

    # Loads the basic Telemetry File and converts it to a normed DataFrame
    t_loader = TelemetryLoader()

    telemetry_files = [file for file in os.listdir("src/assets/MoTec/spa/telemetry_files/")
                       if "-17-" in file
                       or "-16-" in file]
    lap_df_list = []
    lap_corner_model_list = []
    all_files_len = len(telemetry_files)
    counted = 0

    sign = 0
    for f in telemetry_files:

        #try:
        file_path = os.path.join("assets/MoTec/spa/telemetry_files/", f)
        raw_telemetry_df = t_loader.telemetry_from_csv(file_path, "Spa")
        lap = LapModel(raw_telemetry_df,
                       "Spa",
                       "Stuntman Mike")
        lap_df = lap.get_all_analyzed_corners_as_df()
        lap_corner_models = lap.get_all_corner_models()
        lap_corner_model_list.append(lap_corner_models)

        lap_df["lap_file"] = f
        lap_df["lap_time"] = lap.lap_time_s
        lap_df_list.append(lap_df)

        print(f">>> {f} successfully loaded!")
        #except Exception as e:
        #    print(f"{f} failed to load! Exception: {e}")

        counted += 1
        print(f"{counted} / {all_files_len}")

    all_laps_df = pd.concat(lap_df_list, ignore_index=True)
    all_laps_df = all_laps_df.sort_values(by=me.LapMeta.ID.value, ascending=True, kind="mergesort")


    with pd.ExcelWriter("all_laps_with_straights.xlsx", engine="openpyxl") as writer:
        all_laps_df.to_excel(writer, sheet_name="all_laps", index=False)



    raw_record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    raw_user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    user_lap = LapModel(raw_user_df, "Spa", "Stuntman Mike")
    record_lap = LapModel(raw_record_df, "Spa", "Record Man")

    user_corners_df = user_lap.get_all_analyzed_corners_as_df()
    record_corners_df = record_lap.get_all_analyzed_corners_as_df()

    u_corner_04_model = user_lap.get_corner_model(4)

    print(u_corner_04_model.get_driver_performance(mode=ReturnFormat.DICT))

    print(user_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]],
          record_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]])

    #with open("corner_columns.txt", "w") as f:
    #    f.write(str(corners_df.columns))
