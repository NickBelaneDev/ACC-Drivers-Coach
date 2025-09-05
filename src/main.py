from src.lap_telemetry import LapTelemetry

from src.telemetry_loader import TelemetryLoader
from logger import get_logger
from pathlib import Path

log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
user_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-8-hotlap_2-17-860.csv"


if __name__ == "__main__":


    t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER

    record_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")
    user_df = t_loader.telemetry_from_csv(user_lap_file_path, "spa")

    #lap_compare = LapCompare(user_df, record_df)





    #
    print(record_df.info())
    lap_record = LapTelemetry(record_df)
    lap_user = LapTelemetry(user_df)

    u_all_segments = lap_user.get_segment_list()
    r_all_segments = lap_record.get_segment_list()



    print(u_all_segments)

    to_print = True

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