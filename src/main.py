import datetime

import pandas as pd
from src.telemetry.telemetry_loader import TelemetryLoader
from src.logger import get_logger
import src.lap.metrics_enums as me
from pathlib import Path
from src.lap.lap_model import LapModel

import os
log = get_logger(to_console=False,log_file="lap_telemetry_log.log")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def collect_motec_csv_files(track: str, path=None):
    """Returns all raw telemetry files from a track."""

    _telemetry_dir = f"src/assets/MoTec/{track}/telemetry_files/"
    telemetry_files = [
        file for file in os.listdir(_telemetry_dir)
    ]

    return telemetry_files

def load_calculated_lap_dataframe(
        file_name: str,
        raw_telemetry_df: pd.DataFrame,
        track_name: str,
        driver: str) \
        -> pd.DataFrame:
    """

    :param file_name: the file_name will be added to the DataFrame
    :param raw_telemetry_df: the raw DataFrame from the TelemetryLoader.telemetry_from_csv
    :param track_name: Name of the track, only moderating use case
    :param driver: Name of the driver, only moderating use case
    :return: A DataFrame with all calculated metrics of the lap.
    """
    lap = LapModel(raw_telemetry_df,
                   track_name,
                   driver)

    lap_df = lap.get_all_analyzed_corners_as_df()

    # Add additional meta-data to the data_frame
    lap_df["lap_file"] = file_name
    lap_df["lap_time"] = lap.lap_time_s

    return lap_df

def load_raw_telemetry_df_from_file_path(loader:TelemetryLoader,
                                       track:str,
                                       file:str) \
    -> pd.DataFrame:
    file_path = os.path.join(f"assets/MoTec/{track}/telemetry_files/", file)
    raw_telemetry_df = loader.telemetry_from_csv(file_path, track)

    return raw_telemetry_df

def load_all_calculated_lap_dataframes(track: str,
                                       telemetry_files)\
        -> pd.DataFrame:
    """

    :param track: name of the track folder, e.g. for Brands Hatch you want to call 'brands_hatch' as it is in the src/assets/MoTec
    :param telemetry_files: A list with the names of the telemetry_files
    :return: A DataFrame with all analyzed Lap-DataFrames ordered by corner_id from fastest to slowest.
    """
    # Fill the lap_df_list with all Lap instances
    lap_df_list = []
    all_files_len = len(telemetry_files)
    counted = 0

    t_loader = TelemetryLoader()
    for f in telemetry_files:
        raw_telemetry_df = load_raw_telemetry_df_from_file_path(t_loader, track, f)

        # Create a LapModel for every file
        lap_df = load_calculated_lap_dataframe(f, raw_telemetry_df, "Brands Hatch", "Stuntman Mike")
        lap_df_list.append(lap_df)

        print(f">>> {f} successfully loaded!")
        counted += 1
        print(f"{counted} / {all_files_len}")


    all_laps_df = pd.concat(lap_df_list, ignore_index=True)
    all_laps_df = all_laps_df.sort_values(by=me.LapMeta.ID.value, ascending=True, kind="mergesort")

    return all_laps_df

def write_to_excel_file(track: str,
                        to_csv=True,
                        sheet:str=None) -> bool:
    """NOTE: this function has magic strings/paths!"""

    if not isinstance(track, str):
        raise ValueError(f"'track' must be a string!")

    # Set the sheet name of the exported Excel file
    if not sheet:
        final_sheet = f"{track}{datetime.date.today()}"
    else:
        final_sheet = sheet

    telemetry_files = collect_motec_csv_files(track)
    all_laps_df = load_all_calculated_lap_dataframes(track, telemetry_files)

    if to_csv:
        all_laps_df.to_csv(f"test_output/{track}.csv")

    with pd.ExcelWriter(f"test_output/{track}.xlsx", engine="openpyxl") as writer:
        try:
            all_laps_df.to_excel(writer, sheet_name=final_sheet, index=False)
            return True
        except Exception as e:
            log.error(f"Failed to write 'all_laps_df.to_excel()'\nException occurred: {e}")
            return False

if __name__ == "__main__":
    write_to_excel_file("brands_hatch")

