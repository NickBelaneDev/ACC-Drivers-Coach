import pandas as pd
from logger import get_logger

log = get_logger(to_console=False)


def get_corner_df_from_df(corner_id: int, df: pd.DataFrame) -> pd.DataFrame:
    try:
        max_corner = int(self.lap_df["corner_id"].max())
    except Exception as e:
        print("max_corner not found!")
        max_corner = int(df["corner_id"].max())
        pass

    if corner_id < 0 or corner_id > max_corner:
        raise ValueError(f"corner_id '{corner_id}' out of range 0..{max_corner}")

    # load all relevant raw corner_data
    _corner_df = df[df["corner_id"] == corner_id]
    if _corner_df.empty:
        # try float fallback (if source is still floaty)
        _corner_df = df[df["corner_id"] == float(corner_id)]

    if _corner_df.empty:
        log.warning(f"Segment {df}: corner_id {corner_id} nicht gefunden (Typproblem?)")

    return _corner_df