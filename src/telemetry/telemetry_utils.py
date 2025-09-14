import pandas as pd
import numpy as np
from src.logger import get_logger
from dataclasses import asdict, dataclass

log = get_logger(to_console=False)


def get_df_from_area(start_m: int, end_m: int, data: list[str] | str, df: pd.DataFrame):
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

def get_corner_df_from_df(corner_id: int, df: pd.DataFrame) -> pd.DataFrame:
    """
    corner_id must be in df!
    :return: DataFrame of the corner
    """
    # load all relevant raw corner_data

    _corner_df = df[df["corner_id"] == corner_id]
    if _corner_df.empty:
        # try float fallback (if source is still floaty)
        _corner_df = df[df["corner_id"] == float(corner_id)]

    if _corner_df.empty:
        log.warning(f"Segment {df}: corner_id {corner_id} nicht gefunden (Typproblem?)")

    return _corner_df

def get_segment_df_from_lap_fd(segment_id: int, df: pd.DataFrame) -> pd.DataFrame:
    _segment_df = df[df["segment_id_x"] == segment_id]
    if _segment_df.empty:
        _segment_df = df[df["segment_id_x"] == float(segment_id)]

    if _segment_df.empty:
        log.warning(f"Lap {df}: segment_id {segment_id} nicht gefunden (Typproblem?)")

    return _segment_df

def corner_to_df(corner: dataclass, corner_metrics: dataclass) -> pd.DataFrame:
    """Returns a dictionary with the corner and corner metrics in one format."""
    _corner_dict = asdict(corner)
    _corner_dict.pop("metrics", None)
    _corner_dict |= asdict(corner_metrics)
    return pd.DataFrame([_corner_dict])


def segment_to_df(segment: dataclass, segment_metrics: dataclass) -> pd.DataFrame:
    _segment_dict = asdict(segment)
    _segment_dict |= asdict(segment_metrics)
    return pd.DataFrame([_segment_dict])

# ==== Calc

def sigmoid(x):
    return 1/(1 + np.exp(-x))
