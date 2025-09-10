from src.lap_telemetry import LapTelemetry
from src.lap_comparer import LapCompare
from src.telemetry_loader import TelemetryLoader
from logger import get_logger
from pathlib import Path
import pandas as pd
from src.lap import Lap


log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-860.csv"


if __name__ == "__main__":

    # Loads the basic Telemetry File and converts it to a normed DataFrame
    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER
    record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    # Create instances of Lap and compare them.
    user_lap = Lap(user_df, "Spa")
    record_lap = Lap(record_df, "Spa")
    u_corners_df = user_lap.get_corners_df()
    r_corners_df = record_lap.get_corners_df()
    print(u_corners_df.info())
    print("======== USER =============================================================")
    print(u_corners_df[["name","brake_point_m","overall_brake_force"]])
    print("======== REC ==============================================================")
    print(r_corners_df[["name","brake_point_m", "overall_brake_force"]])
    raw_df = user_lap.get_raw_df(corner_id=1008)
    print(user_lap._analyze.parameter_correlation(raw_df, "STEERANGLE", "ROTY"))

    lap_compare = LapCompare(user_df)
    def excel_writer(u_df:pd.DataFrame, r_df: pd.DataFrame, file_name):

        _diff_df = lap_compare.calc_corner_differences(u_df, r_df)
        with pd.ExcelWriter("diff_excel.xlsx", engine="openpyxl") as writer:
            u_df.to_excel(writer, sheet_name="sheet_user", index=False)
            r_df.to_excel(writer, sheet_name="sheet_record", index=False)
            _diff_df.to_excel(writer, sheet_name="sheet_diff", index=False)
