from src.lap.lap_comparer import LapCompare
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_loader import TelemetryLoader
from src.logger import get_logger
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from src.lap.lap import Lap
from src.lap_scores.brake import BrakeScore
from src.lap.analyzer.throttle_analyzer import ThrottleAnalyzer

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
#user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-2-21-304.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"

if __name__ == "__main__":

    # Loads the basic Telemetry File and converts it to a normed DataFrame
    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")                     # nutzt den absolut gesetzten MOTEC_FOLDER
    record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    print(user_df.info())
    corner_1001_df = user_df[user_df["Distance"] < 1000]
    throttle_analysis = ThrottleAnalyzer.get_throttle_data(corner_1001_df)

    print(throttle_analysis)
    # Create instances of Lap and compare them.
    user_lap = Lap(user_df, "Spa")
    record_lap = Lap(record_df, "Spa")

    # PLAY AREA
    #corner_1001_df = user_lap.get_corner_df_by_id(1001)



    corner_ids = user_lap.corner_ids
    # These are the corner metrics as a df
    u_corners_df:pd.DataFrame = user_lap.get_corner_df_by_id(1001)
    r_corners_df = record_lap.get_corners_df()


    print(u_corners_df)
#    print(f"BrakePoint: {u_corner_13["brake_point_m"]}")
    for _id in corner_ids:

        bs = BrakeScore(user_lap.get_raw_df(corner_id=_id))
        u_brake_score = bs.calculate()
        bs = BrakeScore(record_lap.get_raw_df(corner_id=_id))
        r_brake_score = bs.calculate()
        print(" =================================== "
              "BRAKE SCORE ========================")
        print(f"Corner_id: {_id}")
        print(f"User: {u_brake_score=}")
        print(f"Record: {r_brake_score=}")

    def plotten():
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

    #print("======== USER =============================================================")
    #print(u_corners_df)
    #print("======== REC ==============================================================")
    #print(r_corners_df.info())

    lap_compare = LapCompare(user_df)

    def excel_writer(u_df:pd.DataFrame, r_df: pd.DataFrame):

        _diff_df = lap_compare.calc_corner_differences(u_df, r_df)
        with pd.ExcelWriter("diff_excel.xlsx", engine="openpyxl") as writer:
            u_df.to_excel(writer, sheet_name="sheet_user", index=False)
            r_df.to_excel(writer, sheet_name="sheet_record", index=False)
            _diff_df.to_excel(writer, sheet_name="sheet_diff", index=False)
