from src.lap.lap_comparer import LapCompare
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_loader import TelemetryLoader
from logger import get_logger
from pathlib import Path
import pandas as pd
from src.lap.lap import Lap


log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-860.csv"


if __name__ == "__main__":

    # Loads the basic Telemetry File and converts it to a normed DataFrame
    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")                     # nutzt den absolut gesetzten MOTEC_FOLDER
    record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")
    # Create instances of Lap and compare them.
    user_lap = Lap(user_df, "Spa")
    record_lap = Lap(record_df, "Spa")

    print(user_lap.corner_ids)

    u_corners_df = user_lap.get_corners_df(frmt="dict")
    r_corners_df = record_lap.get_corners_df()

    print("======== USER =============================================================")
    print(u_corners_df)
    print("======== REC ==============================================================")
    print(r_corners_df.info())

    raw_df = user_lap.get_raw_df(corner_id=1006)
    print(f"correlation: {TelemetryCalculator.parameter_correlation(raw_df, "TYRE_TAIR_LF", "G_LAT")}")
    print(f"smoothness: {TelemetryCalculator.parameter_smoothness(raw_df, "STEERANGLE")}")
    lap_compare = LapCompare(user_df)
    def excel_writer(u_df:pd.DataFrame, r_df: pd.DataFrame, file_name):

        _diff_df = lap_compare.calc_corner_differences(u_df, r_df)
        with pd.ExcelWriter("diff_excel.xlsx", engine="openpyxl") as writer:
            u_df.to_excel(writer, sheet_name="sheet_user", index=False)
            r_df.to_excel(writer, sheet_name="sheet_record", index=False)
            _diff_df.to_excel(writer, sheet_name="sheet_diff", index=False)
