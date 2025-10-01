from dataclasses import is_dataclass
from enum import Enum
import pandas as pd
import json

class DataAdapter:

    @staticmethod
    def to_dict(data_object):
        if is_dataclass(data_object):
            return {fld: DataAdapter.to_dict(getattr(data_object, fld)) for fld in data_object.__dataclass_fields__}

        elif isinstance(data_object, list):
            return [DataAdapter.to_dict(item) for item in data_object]

        elif isinstance(data_object, Enum):
            return data_object.value

        else:
            return data_object

    @classmethod
    def to_json(cls, data_object, indent: int=4):
        obj_dict = cls.to_dict(data_object)
        return json.dumps(obj_dict, indent=indent)

    @classmethod
    def to_dataframe(cls, data_object):
        obj_dict = cls.to_dict(data_object)
        return pd.json_normalize(obj_dict, sep="_")

if __name__ == "__main__":
    from src.lap.lap_dataclasses import SpeedMetrics, GForceMetrics, CarDynamics
    speed_metrics = SpeedMetrics(
        entry_speed_kmh=150.0,  # Geschwindigkeit vor der Kurve
        apex_speed_kmh=95.0,  # Minimum am Scheitel
        exit_speed_kmh=160.0,  # wieder rausbeschleunigt
        avg_speed_kmh=125.0,  # Runden-/Sektor-Schnitt
        max_speed_kmh=220.0,  # Top-Speed auf der Geraden
        min_speed_kmh=40.0,  # langsamste Stelle (z. B. Haarnadel)
        min_speed_m=1350.0,  # Streckenmeter der langsamsten Stelle
        deceleration_rate=9.2,  # ~0.94 g (m/s²) beim Bremsen
        acceleration_rate=4.6  # ~0.47 g (m/s²) beim Beschleunigen
    )

    g_force_metrics = GForceMetrics(
        g_lat_avg=0.65,  # mittlere Querbeschl. über den Stint
        g_lat_max=1.15,  # Peak in schneller Kurve
        g_lat_min=-1.12,  # Peak in entgegengesetzter Richtung
        g_lon_avg=0.12,  # im Mittel leicht positiv (mehr Beschl. als Bremsen)
        g_lon_max=0.65,  # starkes Beschleunigen aus langsamer Kurve
        g_lon_min=-1.05,  # hartes Bremsen vor Schikane
        g_force_vector_avg=0.72,  # Resultierende im Mittel
        g_force_vector_min=0.05,  # fast lastfrei (Coast)
        g_force_vector_max=1.55,  # kombiniertes Maximum (Bremsen + Einlenken)
        g_force_vector_smoothness=0.81,  # 0..1 "wie ruhig" die Kurve verläuft
        g_force_vector_score=86.0  # z. B. 0..100 Bewertung
    )

    car_dynamics = CarDynamics(
        speed=speed_metrics,
        g_force=g_force_metrics
    )


    car_dynamics_df = DataAdapter.to_dataframe(car_dynamics)
    car_dynamics_dict = DataAdapter.to_dict(car_dynamics)

    print(car_dynamics_dict)
    print(car_dynamics_df["speed_entry_speed_kmh"])