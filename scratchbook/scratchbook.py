import numpy as np
import pandas as pd
import json
from src.motec_csv_practice import MoTec


hot_lap_file_path = "../src/assets/MoTec/Spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"
track_map_file_path = "../src/assets/MoTec/Spa/spa_segments.json"
corners_file_path = "../src/assets/MoTec/Spa/spa_corners.json"
motec = MoTec()

telemetry_df = motec.telemetry_from_csv(hot_lap_file_path)
# Trackmap auslesen
with open(track_map_file_path, "r") as f:
    track_map = json.load(f)

with open(corners_file_path, "r") as f:
    corners_map = json.load(f)
# Corner in Dataframe konvertieren
corners_df = pd.json_normalize(corners_map["corners"])
corners_df_sorted = corners_df.sort_values('cornerStart_m')

segments_df = pd.json_normalize(track_map["segments"])
segments_df_sorted = segments_df.sort_values('segmentStart_m')

telemetry_df_sorted = telemetry_df.sort_values("Distance")

telemetry_with_segments_df = pd.merge_asof(
    left=telemetry_df_sorted,
    right=segments_df,
    left_on="Distance",
    right_on="segmentStart_m",
    direction="backward"
)

# Sortieren der DataFrames nach Distance

full_telemetry_df = pd.merge_asof(
    left=telemetry_with_segments_df,
    right=corners_df_sorted,
    left_on="Distance",
    right_on="cornerStart_m",
    direction="backward"
)


if __name__ == "__main__":
    print(telemetry_with_segments_df)
