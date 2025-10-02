from pathlib import Path

from src.telemetry.telemetry_loader import TelemetryLoader
PROJECT_ROOT = Path(__file__).resolve().parent.parent
print(PROJECT_ROOT)
hot_lap_file_path = "assets/MoTec/spa/Spa-ferrari_296_gt3-fastest_lap_glat-float.csv"
# oder gleich absolut: Path(__file__).resolve().parent / "src" / "assets" / ...

t_loader = TelemetryLoader(base_dir=PROJECT_ROOT / "src")  # nutzt den absolut gesetzten MOTEC_FOLDER
telemetry_df = t_loader.telemetry_from_csv(hot_lap_file_path, "spa")

if __name__ == "__main__":
    print(telemetry_df)