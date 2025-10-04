import pandas as pd
import numpy as np

from src.lap.analyzer.brake_analyzer import BrakeAnalyzer
from src.logger import get_logger

from src.lap.lap_dataclasses import Segment, SegmentMetrics, Corner, CornerMetrics
from src.telemetry.telemetry_calculator import TelemetryCalculator

log = get_logger("telemetry_analyzer", to_console=False)

class LapAnalyzer:
    def __init__(self, df: pd.DataFrame=pd.DataFrame()):
        self.corner_metrics = CornerMetrics
        self.lap_df = df

    def set_lap_df(self, df: pd.DataFrame):
        self.lap_df = df
    def get_time_delta(self,start_m: int, end_m: int):
        time_start_df =  self.lap_df[self.lap_df["Distance"] == start_m]
        time_start = time_start_df["Time"].iloc[0]

        time_end_df = self.lap_df[self.lap_df["Distance"] == end_m]
        time_end = time_end_df["Time"].iloc[0]

        return time_end - time_start

    def corner(self, corner_df: pd.DataFrame) -> Corner:
        """
        This is the main function to calculate the necessary corner data and
        put it all together into a Corner object.
        :param corner_df: vertical-slice from a telemetry_df
        :return: Corner Object
        """
        # Zuerst alle Metriken für die CornerMetrics-Instanz sammeln
        time_delta_s = self.get_time_delta(int(corner_df["cornerStart_m"].iloc[0]),
                                           int(corner_df["cornerEnd_m"].iloc[0]))
        entry_speed_kmh = corner_df["SPEED"].iloc[0]
        exit_speed_kmh = corner_df["SPEED"].iloc[-1]  # Letzten Wert für den Ausgang nehmen
        apex_speed_kmh = corner_df[corner_df["Distance"] == corner_df["cornerApex_m"].iloc[0]]["SPEED"].mean()
        avg_speed_kmh = corner_df["SPEED"].mean()
        max_speed_kmh = corner_df["SPEED"].max()
        min_speed_kmh = corner_df["SPEED"].min()
        min_speed_m = corner_df[corner_df["SPEED"] == min_speed_kmh]["Distance"].mean()

        g_lat_avg = corner_df["G_LAT"].abs().mean()
        g_lat_max = corner_df["G_LAT"].abs().max()
        g_lat_min = corner_df["G_LAT"].abs().min()
        g_lon_avg = corner_df["G_LON"].abs().mean()
        g_lon_max = corner_df["G_LON"].abs().max()
        g_lon_min = corner_df["G_LON"].abs().min()

        avg_steerangle = corner_df["STEERANGLE"].abs().mean()

        max_steerangle = corner_df["STEERANGLE"].abs().max()
        max_steerangle_m = corner_df[corner_df["STEERANGLE"].abs() == max_steerangle]["Distance"].mean()

        # IN PROGRESS
        _advanced_brake_data = self._get_brake_points(corner_df)

        avg_brake = _advanced_brake_data["avg_brake"]
        max_brake = _advanced_brake_data["max_brake"]

        brake_point_m = _advanced_brake_data["brake_point_m"]
        brake_release_m = _advanced_brake_data["brake_release_m"]
        brake_delta_m = _advanced_brake_data["brake_delta_m"]
        brake_delta_s = _advanced_brake_data["brake_delta_s"]

        trail_brake_delta_m = _advanced_brake_data["trail_brake_delta_m"]
        trail_brake_delta_s = _advanced_brake_data["trail_brake_delta_s"]
        trail_brake_start_m = _advanced_brake_data["trail_brake_start_m"]
        trail_brake_end_m = _advanced_brake_data["trail_brake_end_m"]
        overall_brake_force = _advanced_brake_data["overall_brake_force"]

        tbf95_s = _advanced_brake_data["tbf95"]

        brake_analysis = BrakeAnalyzer()
        brake_data = brake_analysis.get_brake_data(corner_df)
        trail_brake_data = brake_data.trail_brake
        avg_brake = brake_data.avg_brake
        max_brake = brake_data.max_brake

        avg_throttle = corner_df["THROTTLE"].mean()

        # IN PROGRESS
        _advanced_throttle_data = self._get_throttle_data(corner_df)
        ttf95_s = _advanced_throttle_data["ttf95_s"]
        exit_throttle_init_m = _advanced_throttle_data["exit_throttle_init_m"]
        avg_exit_throttle = _advanced_throttle_data["avg_exit_throttle"]
        exit_speed_delta_s = _advanced_throttle_data["exit_speed_delta_s"]

        is_rolling = corner_df[(corner_df["THROTTLE"] == 0) & (corner_df["BRAKE"] == 0)]
        rolling_delta_m = is_rolling["Distance"].max() - is_rolling["Distance"].min()
        rolling_delta_s = is_rolling["Time"].max() - is_rolling["Time"].min()

        _apex = corner_df["cornerApex_m"].iloc[0]

        cpi_area_df = self._get_df_from_area(_apex - 50, _apex + 50, "gForceVector")
        g_force_vector = cpi_area_df["gForceVector"]
        distance = cpi_area_df["Distance"]

        cpi_factor = np.trapezoid(g_force_vector, distance)
        f = 0.4
        smoothness_factor = (f - 1) * TelemetryCalculator.parameter_stability(corner_df,
                                                                               "STEERANGLE") + f * TelemetryCalculator.parameter_stability(
            corner_df, "ROTY")  # + 0.2 * self.parameter_smoothness(corner_df, "THROTTLE")
        smoothness_factor = round(smoothness_factor, 4)
        # print(f"{smoothness_factor=}")

        # Jetzt die CornerMetrics-Instanz erstellen
        corner_metrics = CornerMetrics(
            time_delta_s=time_delta_s,
            entry_speed_kmh=entry_speed_kmh,
            apex_speed_kmh=apex_speed_kmh,
            exit_speed_kmh=exit_speed_kmh,
            avg_speed_kmh=avg_speed_kmh,
            max_speed_kmh=max_speed_kmh,
            min_speed_kmh=min_speed_kmh,
            min_speed_m=min_speed_m,
            g_lat_avg=g_lat_avg,
            g_lat_max=g_lat_max,
            g_lat_min=g_lat_min,
            g_lon_avg=g_lon_avg,
            g_lon_max=g_lon_max,
            g_lon_min=g_lon_min,
            avg_steerangle=avg_steerangle,
            max_steerangle=max_steerangle,
            max_steerangle_m=max_steerangle_m,
            avg_brake=avg_brake,
            max_brake=max_brake,
            avg_throttle=avg_throttle,
            #tbf95_s=tbf95_s,
            ttf95_s=ttf95_s,
            #brake_point_m=brake_point_m,
            #brake_release_m=brake_release_m,
            #brake_delta_m=brake_delta_m,
            #brake_delta_s=brake_delta_s,
            #trail_brake_delta_s=trail_brake_delta_s,
            #trail_brake_delta_m=trail_brake_delta_m,
            #trail_brake_start_m=trail_brake_start_m,
            #trail_brake_end_m=trail_brake_end_m,
            #overall_brake_force=overall_brake_force,
            #brake_metrics=brake_data,
            exit_throttle_init_m=exit_throttle_init_m,
            avg_exit_throttle=avg_exit_throttle,
            exit_speed_delta_s=exit_speed_delta_s,
            rolling_delta_s=rolling_delta_s,
            rolling_delta_m=rolling_delta_m,
            cpi_factor=cpi_factor  # Platzhalter, falls dieser Wert noch berechnet werden muss

        )

        # Und jetzt die Corner-Instanz mit der CornerMetrics-Instanz erstellen
        corner_instance = Corner(
            id=corner_df["corner_id"].iloc[0],
            name=corner_df["cornerName"].iloc[0],
            start_m=corner_df["cornerStart_m"].iloc[0],
            apex_m=corner_df["cornerApex_m"].iloc[0],
            end_m=corner_df["cornerEnd_m"].iloc[0],
            metrics=corner_metrics
        )

        return corner_instance
    def segment(self, segment_df: pd.DataFrame) -> tuple[Segment, SegmentMetrics]:
        if segment_df.empty:
            print("segment_df is empty!")

        seg_id = segment_df["segment_id_x"].iloc[0]
        corner_ids = segment_df["corner_ids"].iloc[0]
        seg_start = segment_df["Distance"].iloc[0]
        seg_end = segment_df["Distance"].iloc[-1]
        description = segment_df["segmentDescription"].iloc[0]

        start_speed_kmh = segment_df[segment_df["Distance"] == seg_start]["SPEED"].iloc[0]
        end_speed_kmh = segment_df[segment_df["Distance"] == seg_end]["SPEED"].iloc[0]
        start_time_s = segment_df[segment_df["Distance"] == seg_start]["Time"].iloc[0]
        end_time_s = segment_df[segment_df["Distance"] == seg_end]["Time"].iloc[0]
        time_delta_s = end_time_s - start_time_s

        avg_speed_kmh = segment_df["SPEED"].mean()
        max_speed_kmh = segment_df["SPEED"].max()
        min_speed_kmh = segment_df["SPEED"].min()

        avg_throttle = segment_df["THROTTLE"].mean()
        avg_brake = segment_df["BRAKE"].mean()

        analyzed_segment = Segment(
            id=seg_id,
            corner_ids=corner_ids,
            start_m=seg_start,
            end_m=seg_end,
            description=description)

        analyzed_segment_metrics = SegmentMetrics(
            id=seg_id,
            start_speed_kmh=start_speed_kmh,
            end_speed_kmh=end_speed_kmh,
            time_delta_s=time_delta_s,
            avg_speed_kmh=avg_speed_kmh,
            max_speed_kmh=max_speed_kmh,
            min_speed_kmh=min_speed_kmh,
            avg_throttle=avg_throttle,
            avg_brake=avg_brake)

        return analyzed_segment, analyzed_segment_metrics

    def _get_df_from_area(self, start_m: int, end_m: int, data: list[str] | str, df: pd.DataFrame=None):
        lap_df = self.lap_df.copy()

        if df:
            lap_df = df

        if isinstance(data, str):
            if "Distance" in data:
                columns = [data]
            else:
                columns = ["Distance", data]

        elif isinstance(data, list):
            if "Distance" in data:
                columns = data
            else:
                columns = ["Distance"] + data

        else:
            return pd.DataFrame()

        _df = lap_df[
            (lap_df["Distance"] >= start_m) &
            (lap_df["Distance"] <= end_m)
        ]

        return _df[columns] if not _df.empty else pd.DataFrame()

    # =========================================================
    #
    # Ab hier werden die Corner und Segment Instanzen berechnet und angelegt

    # ======== THROTTLE DATA
    @staticmethod
    def _get_throttle_data(telemetry_df: pd.DataFrame, threshold=60) -> pd.DataFrame | None:
#        ttf95_s = telemetry_df[telemetry_df[""]]
        exit_throttle_init_df = telemetry_df[(telemetry_df["THROTTLE"].shift(1) < threshold) & (telemetry_df["THROTTLE"] >= threshold) & (telemetry_df["BRAKE"] <= 3)]
        exit_throttle_init_m = exit_throttle_init_df["Distance"].min()

        avg_exit_throttle = telemetry_df[(telemetry_df["cornerApex_m"].iloc[0] <= telemetry_df["Distance"]) & (telemetry_df["Distance"] <= telemetry_df["Distance"].max())]["THROTTLE"].mean()
        exit_speed_delta_s = 0

        ttf95_s = telemetry_df[telemetry_df["THROTTLE"] >= 95]["Time"].max() - telemetry_df[telemetry_df["THROTTLE"] >= 95]["Time"].min()

        return {
            "ttf95_s": ttf95_s,
            "exit_throttle_init_m": exit_throttle_init_m,
            "avg_exit_throttle": avg_exit_throttle,
            "exit_speed_delta_s": exit_speed_delta_s
        }
    # ======== BRAKE DATA
    @staticmethod
    def _trail_brake_delta(df: pd.DataFrame) -> dict:
        """
        Indicates an area where the driver is braking less than the threshold parameter while steering in a single direction.

        :param df:

        :return: trail_brake_delta_s, trail_brake_delta_m
        """

        delta_df = df[(df["BRAKE"].shift(1) > df["BRAKE"])]
        trail_brake_start_m = delta_df["Distance"].min()
        trail_brake_end_m = delta_df["Distance"].max()
        trail_brake_delta_m = trail_brake_end_m - trail_brake_start_m
        trail_brake_delta_s = delta_df["Time"].max() - delta_df["Time"].min()


        trail_brake_dict = {
            "trail_brake_start_m": trail_brake_start_m,
            "trail_brake_end_m": trail_brake_end_m,
            "trail_brake_delta_m": trail_brake_delta_m,
            "trail_brake_delta_s": trail_brake_delta_s,
        }

        return trail_brake_dict
    def _get_brake_points(self, telemetry_df: pd.DataFrame, threshold=2) -> dict | None:
        """
        ACHTUNG! Noch muss geprüft werden, ob es überhaupt einen Bremspunkt gibt!
        :param telemetry_df:
        :return:
        """

        brake_area_start_m = telemetry_df["brakeArea_m"].iloc[0]
        brake_area_end_m = telemetry_df["cornerApex_m"].iloc[0]

        # "Distance" is always added in get_data_from_area!!
        cols = ["SPEED", "BRAKE", "G_LAT", "G_LON", "STEERANGLE", "Time"]

        brake_df = self._get_df_from_area(brake_area_start_m, brake_area_end_m, cols)

        was_not_braking = brake_df["BRAKE"].shift(1).fillna(0) < threshold
        is_braking = brake_df["BRAKE"] >= threshold

        # This DataFrame is
        _brake_point_df = brake_df[is_braking & was_not_braking]
        if _brake_point_df.empty:
            return {"brake_point_m": 0,"brake_delta_m": 0, "brake_delta_s": 0.0,
                "brake_release_m": 0,"avg_brake": 0, "max_brake": 0, "trail_brake_delta_m": 0,
                "trail_brake_delta_s": 0, "trail_brake_start_m": 0, "trail_brake_end_m": 0, "overall_brake_force":0,  "tbf95": 0}

        # The brake point has been validated
        brake_point_m = _brake_point_df["Distance"].min()            # this is only a row and we need the lowest "Distance"
        brake_point_s = _brake_point_df.loc[_brake_point_df["Distance"].idxmin(), "Time"]

        # Calculate the brake release
        release_mask = (brake_df["BRAKE"].shift(1).fillna(0) >= 1) & (brake_df["BRAKE"] == 0)
        release_rows = brake_df[release_mask]

        if release_rows.empty:
            brake_release_m = brake_df["Distance"].max()
            brake_release_s = brake_df.loc[brake_df["Distance"].idxmax(), "Time"]
        else:
            brake_release_m = release_rows["Distance"].max()
            brake_release_s = release_rows.loc[release_rows["Distance"].idxmax(), "Time"]

        if pd.isna(brake_point_m) or pd.isna(brake_release_m):
            return {"brake_point_m": 0,"brake_delta_m": 0, "brake_delta_s": 0.0,
                "brake_release_m": 0,"avg_brake": 0, "max_brake": 0, "trail_brake_delta_m": 0,
                "trail_brake_delta_s": 0, "trail_brake_start_m": 0, "trail_brake_end_m": 0, "overall_brake_force":0,  "tbf95": 0}

        # Set final variables
        brake_delta_m = brake_release_m - brake_point_m
        brake_delta_s = brake_release_s - brake_point_s

        max_brake = brake_df["BRAKE"].max()
        avg_brake = brake_df[(brake_df["Distance"] >= brake_point_m) & (brake_df["Distance"] <= brake_release_m)]["BRAKE"].mean() #  soll vom Bremspunkt des Fahrers bis zum kompletten Release gehen.

        _trail_brake_data = self._trail_brake_delta(brake_df)

        trail_brake_delta_s = _trail_brake_data["trail_brake_delta_s"]
        trail_brake_delta_m = _trail_brake_data["trail_brake_delta_m"]
        trail_brake_start_m = _trail_brake_data["trail_brake_start_m"]
        trail_brake_end_m = _trail_brake_data["trail_brake_end_m"]

        overall_brake_force = TelemetryCalculator.get_integral(brake_df, "BRAKE")

        tbf95_s = brake_df[brake_df["BRAKE"] >= 95]["Time"].max() - brake_df[brake_df["BRAKE"] >= 95]["Time"].min()


        return {"brake_point_m": brake_point_m,
                "brake_delta_m": brake_delta_m,
                "brake_release_m": brake_release_m,
                "brake_delta_s": brake_delta_s,
                "max_brake": max_brake,
                "avg_brake": avg_brake,
                "trail_brake_delta_m": trail_brake_delta_m,
                "trail_brake_delta_s": trail_brake_delta_s,
                "trail_brake_start_m": trail_brake_start_m,
                "trail_brake_end_m": trail_brake_end_m,
                "overall_brake_force": overall_brake_force,
                "tbf95": tbf95_s}


    # ============================================================================================================= #
    # 'corner' and 'segment' processing the corner and segment data into the main Kennzahlen #



