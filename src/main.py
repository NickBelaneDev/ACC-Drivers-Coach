from src.lap_telemetry import LapTelemetry
from src.lap_comparer import LapCompare
from src.telemetry_loader import TelemetryLoader
from logger import get_logger
from pathlib import Path
import pandas as pd

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-860.csv"


if __name__ == "__main__":


    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER

    record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")
    #print(user_df)
    lap_compare_u = LapCompare(user_df)
    lap_compare = LapCompare(record_df)

    rec_seg_df = lap_compare.load_segments_df()
    #print(rec_seg_df)
    u_seg_df = lap_compare_u.load_segments_df()
    #print(u_seg_df)

    u_c_df = lap_compare_u.load_corners()
    r_c_df = lap_compare.load_corners()
    print("========= USER ========")
    print(u_c_df.info())
    print("========= REC ========")
    print(r_c_df)

    diff_df = lap_compare.calc_corner_differences(u_c_df, r_c_df)
    with pd.ExcelWriter("diff_excel.xlsx", engine="openpyxl") as writer:
        u_c_df.to_excel(writer, sheet_name="sheet_user", index=False)
        r_c_df.to_excel(writer, sheet_name="sheet_record", index=False)
        diff_df.to_excel(writer, sheet_name="sheet_01", index=False)
    print(diff_df["exit_throttle_init_m"])

    #print(record_df.info())
    #lap_record = LapTelemetry(record_df)
    #lap_user = LapTelemetry(user_df)

    u_all_segments = None
    #r_all_segments = lap_record.get_segment_list()

    to_print = False

    if to_print:
        print("======================")
        for segment in u_all_segments:
            for _k, _ in segment.items():
                if _k == "corners":
                    for corner in segment[_k]:
                        print("======================")
                        print(f"{corner["id"]}\n"
                              f"{corner["name"]}\n"
                              f"start: {corner["start_m"]}  end: {corner["end_m"]}")

                        _metrics = corner["metrics"]
                        #print(_metrics)
                        for o, l in _metrics.items():
                           print(f" - {o}: {l}")