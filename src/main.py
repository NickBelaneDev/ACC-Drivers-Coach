from src.lap.adapter import DataAdapter
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

    #print(user_df.info())
    """
    corner_df = get_raw_corner_df_from_df(4, user_df)
    corner = CornerBuilder.build_corner(corner_df)
    corner_dict = DataAdapter.to_dict(corner)
    """

    user_lap = Lap(raw_user_df, "Spa", "Stuntman Mike")
    record_lap = Lap(raw_record_df, "Spa", "Record Man")
    #print(test_lap.corners[13])
    user_corners_df = user_lap.get_all_analyzed_corners_as_df()
    record_corners_df = record_lap.get_all_analyzed_corners_as_df()

    for e in me.DriverSteer:
        print(e.value())

    print(user_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]],
          record_corners_df[[me.LapMeta.NAME.value, me.DriverBrake.BRAKE_RELEASE_M.value, me.DriverSteer.INTEGRAL.value]])

    #with open("corner_columns.txt", "w") as f:
    #    f.write(str(corners_df.columns))
    """
    with pd.ExcelWriter("corner_test_02.xlsx", engine="openpyxl") as writer:

        _df = DataAdapter.to_dataframe(test_lap)
        _df.to_excel(writer, sheet_name="user_lap-01", index=False)
    """

    def plotten():
        user_lap = Lap(user_df, "Spa")
        record_lap = Lap(raw_record_df, "Spa")

        corner_ids = user_lap.corner_ids

        # These are the corner metrics as a df
        u_corners_df: pd.DataFrame = user_lap.get_corner_df_by_id(1)
        r_corners_df = record_lap.get_corners_df()

        u_raw_df = user_lap.get_raw_df()
        distance = u_raw_df["Distance"]
        _u_speed = u_raw_df["SPEED"]

        r_raw_df = record_lap.get_raw_df()
        _r_speed = r_raw_df["SPEED"]
        _r_speed = _r_speed.drop(_r_speed.index[-1])
        # ===== ======= ===================================================================
        # ===== ======= ===================================================================
        # ===== MATPLOT ===================================================================
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(distance, _u_speed, color='red')
        ax.plot(distance, _r_speed, color='blue', linestyle="--")
        ax.set_title("ACC Driver Coach")
        ax.set_xlabel("Distance/m")
        ax.set_ylabel("Speed/kmh")
        ax.legend()
        ax.grid(True)
        plt.show()




    def excel_writer(u_df:pd.DataFrame, r_df: pd.DataFrame):
        lap_compare = LapCompare(u_df)
        _diff_df = lap_compare.calc_corner_differences(u_df, r_df)
        with pd.ExcelWriter("diff_excel.xlsx", engine="openpyxl") as writer:
            u_df.to_excel(writer, sheet_name="sheet_user", index=False)
            r_df.to_excel(writer, sheet_name="sheet_record", index=False)
            _diff_df.to_excel(writer, sheet_name="sheet_diff", index=False)
