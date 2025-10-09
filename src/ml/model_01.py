
import src.lap.metrics_enums as me
from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np
from src.telemetry.telemetry_loader import TelemetryLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
telemetry_folder = PROJECT_ROOT / "src" / "assets" / "MoTeC" / "spa" / "telemetry_files"

# Loads the basic Telemetry File and converts it to a normed DataFrame
if __name__ == "__main__":
    t_loader = TelemetryLoader()

    telemetry_files = [
        file for file in telemetry_folder.iterdir() #os.listdir(telemetry_folder)#("src/assets/MoTec/spa/telemetry_files/")
        #if "-17-" in file
        #or "-16-" in file
    ]

    lap_df_list = []
    lap_corner_model_list = []
    all_files_len = len(telemetry_files)
    counted = 0
    """
    for f in telemetry_files:
        raw_telemetry_df = t_loader.telemetry_from_csv(str(f), "Spa")
        lap = LapModel(raw_telemetry_df,
                       "Spa",
                       "Stuntman Mike")
        lap_df = lap.get_all_analyzed_corners_as_df()
        lap_df = lap_df[
            [
                me.LapMeta.ID.value,
                me.DynamicsSpeed.SPEED_INTEGRAL.value,
                me.LapMeta.START_M.value,
                me.LapMeta.TIME_DELTA_S.value
            ]
        ]
        lap_df["lap_file"] = f
        lap_df["lap_time"] = lap.lap_time_s
        lap_df_list.append(lap_df)

        print(f">>> {f} successfully loaded!")

        counted += 1
        print(f"{counted} / {all_files_len}")
    """
    all_laps_csv = PROJECT_ROOT / "test_output" / "all_laps_with_straights_2132.csv"
    all_laps_df = pd.read_csv(str(all_laps_csv))
    #all_laps_df = pd.concat(lap_df_list, ignore_index=True)
    #all_laps_df = all_laps_df.sort_values(by=me.LapMeta.ID.value, ascending=True, kind="mergesort")

    X = all_laps_df[
        [
            me.DriverBrake.BRAKE_FORCE_PER_M.value,
            me.DriverBrake.BRAKE_WINDOW_M.value,
            me.DriverBrake.BRAKE_WINDOW_S.value,
            me.DriverBrake.BRAKE_POINT_M.value,
            me.DriverBrake.BRAKE_RELEASE_M.value,
            me.DriverBrake.TRAIL_INTEGRAL.value,
            me.DriverBrake.OVERALL_FORCE.value,

            me.DynamicsGForce.VECTOR_SCORE.value,
            me.DynamicsSpeed.ENTRY_SPEED_KMH.value,
            me.DynamicsSpeed.SPEED_INTEGRAL.value,
            me.DynamicsGForce.VECTOR_AVG.value,
        ]
    ]
    y = all_laps_df[
        me.LapMeta.TIME_DELTA_S.value
    ]

    X = X.replace([np.inf, -np.inf], np.nan)
    y = y.replace([np.inf, -np.inf], np.nan)

    # Falls im Target NaNs sind: rausfiltern
    mask = y.notna()
    X, y = X.loc[mask], y.loc[mask]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler(with_mean=False)),  # Scaling ist optional bei LinearRegression
        ("model", LinearRegression())
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("R² :", r2_score(y_test, y_pred))



