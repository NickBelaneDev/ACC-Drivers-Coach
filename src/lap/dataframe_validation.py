import pandas as pd
import math
import numpy as np

from src.logger import get_logger

log = get_logger(name="data_frame_validator", to_console=False, level="DEBUG")
class DataFrameColumnError(Exception):
    pass

class EmptyDataFrameError(Exception):
    pass

class DataFrameValidator:
    @staticmethod
    def validate_df(df: pd.DataFrame, cols: list[str]) -> bool:
        """Check if the DataFrame is not empty and has all cols. Raises a DataFrameColumnError if not."""
        if df.empty:
            raise EmptyDataFrameError(f"Empty DataFrame!")

        df_cols = df.columns

        if "Distance" not in df_cols:
            raise DataFrameColumnError(f"'Distance' Column not in DataFrame!")

        if df[df["Distance"] == 0].all():
            raise DataFrameColumnError(f"'Distance' Column consists only of 0")

        if pd.api.types.is_float_dtype(df["Distance"]):
            raise DataFrameColumnError(f"'Distance' Column is type float!")

        for col in cols:
            if col not in df_cols:
                raise DataFrameColumnError(f"col: {col} is missing!")

        return True

