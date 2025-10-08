from dataclasses import is_dataclass
from enum import Enum
import pandas as pd
import json
from typing import Any

class DataAdapter:
    """
    Universal adapter for serializing dataclass-based telemetry objects.

    ``DataAdapter`` provides consistent conversion utilities that transform
    nested dataclasses, Enums, and lists into Python dictionaries, JSON strings,
    or pandas DataFrames. It is primarily used by analyzer layers and export
    functions to flatten structured telemetry data for storage or display.

    Features
    --------
    - Recursive traversal of dataclasses (handles nested dataclasses and lists)
    - Enum support (uses ``.value`` instead of object representation)
    - Flattened output for DataFrame export via ``pandas.json_normalize``

    Typical usage
    -------------
    >>> from src.lap.lap_dataclasses import Corner
    >>> corner_obj = Corner(id=1, name="Eau Rouge", start_m=200, apex_m=245, end_m=300)
    >>> dict_obj = DataAdapter.to_dict(corner_obj)
    >>> json_str = DataAdapter.to_json(corner_obj)
    >>> df = DataAdapter.to_dataframe(corner_obj)
    """
    @staticmethod
    def to_dict(data_object) \
            -> dict | list | str | Any:
        """
        Recursively convert dataclass objects into nested dictionaries.

        Supported input types
        ---------------------
        - Dataclass instances → converted field-by-field
        - Lists of dataclasses → recursively handled
        - Enum members → replaced by their ``.value`` strings
        - Primitives and other objects → returned as-is

        Parameters
        ----------
        data_object : Any
            The object to serialize (dataclass, list, Enum, or primitive).

        Returns
        -------
        dict | list | str | Any
            A Python object suitable for JSON serialization or tabular
            normalization (depending on the input structure).

        Notes
        -----
        This method is the internal base for all other conversions
        (``to_json`` and ``to_dataframe``).
        """
        if is_dataclass(data_object):
            return {fld: DataAdapter.to_dict(getattr(data_object, fld)) for fld in data_object.__dataclass_fields__}

        elif isinstance(data_object, list):
            return [DataAdapter.to_dict(item) for item in data_object]

        elif isinstance(data_object, Enum):
            return data_object.value

        else:
            return data_object

    @classmethod
    def to_json(cls, data_object,
                indent: int=4)\
            -> str:
        """
        Serialize a dataclass (or nested structure) into a JSON string.

        Parameters
        ----------
        data_object : Any
            Dataclass, list, or nested structure to be serialized.
        indent : int, optional
            Indentation level for JSON pretty-printing. Default is 4.

        Returns
        -------
        str
            JSON-encoded string representation of the input object.

        Example
        -------
        >>> json_str = DataAdapter.to_json(corner_obj, indent=2)
        >>> print(json_str)
        {
          "id": 1,
          "name": "Eau Rouge",
          "start_m": 200,
          ...
        }
        """
        obj_dict = cls.to_dict(data_object)
        return json.dumps(obj_dict, indent=indent)

    @classmethod
    def to_dataframe(cls, data_object):
        """
        Convert a dataclass or list of dataclasses into a pandas DataFrame.

        The structure is first serialized into a nested dictionary and then
        flattened using ``pandas.json_normalize`` with underscore-based keys.
        Nested objects appear as column names in the format
        ``parent_child_field``.

        Parameters
        ----------
        data_object : Any
            A dataclass or nested structure (single object or list).

        Returns
        -------
        pandas.DataFrame
            Flattened DataFrame suitable for analytics, comparison, or export.

        Example
        -------
        >>> df = DataAdapter.to_dataframe(corner_obj)
        >>> print(df.columns)
        Index(['id', 'name', 'start_m', 'apex_m', 'end_m', ...], dtype='object')
        """
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