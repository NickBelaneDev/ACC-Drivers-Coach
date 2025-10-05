from src.lap.adapter import DataAdapter
from src.lap.corner.corner_enums import ReturnFormat
from src.lap.lap_comparer import LapCompare
from src.telemetry.telemetry_loader import TelemetryLoader
from src.logger import get_logger
import src.lap.metrics_enums as me

import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from src.lap.lap import Lap


log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_2-16-650.csv"
#user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-21-304.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-hotlap_2-17-880.csv"

if __name__ == "__main__":

    # Loads the basic Telemetry File and converts it to a normed DataFrame
    t_loader = TelemetryLoader()#(base_dir=PROJECT_ROOT / "src")                     # nutzt den absolut gesetzten MOTEC_FOLDER
    raw_record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    raw_user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    user_lap = Lap(raw_user_df, "Spa", "Stuntman Mike")
    record_lap = Lap(raw_record_df, "Spa", "Record Man")

    user_corners_df = user_lap.get_all_analyzed_corners_as_df()
    record_corners_df = record_lap.get_all_analyzed_corners_as_df()

    corner_02_model = user_lap.get_corner_model(4)

    print(corner_02_model.get_driver_performance(mode=ReturnFormat.DICT))
    print(user_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]],
          record_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]])

    #with open("corner_columns.txt", "w") as f:
    #    f.write(str(corners_df.columns))
    """
    with pd.ExcelWriter("corner_test_02.xlsx", engine="openpyxl") as writer:

        _df = DataAdapter.to_dataframe(test_lap)
        _df.to_excel(writer, sheet_name="user_lap-01", index=False)
    """
