import pandas as pd
import math
import numpy as np

from src.logger import get_logger

log = get_logger(name="data_frame_validator", to_console=False, level="DEBUG")
class MissingColumnError(Exception):
    def __init__(self, col: str):
        super().__init__(f"Required column '{col}' is missing.")

class EmptyDataFrameError(Exception):
    def __init__(self, message="DataFrame is empty!"):
        super().__init__(message)



class DataFrameValidator:
    @staticmethod
    def validate_df(df: pd.DataFrame, cols: list[str] | str =None) -> bool:
        """Check if the DataFrame is not empty and has all cols. Raises a DataFrameColumnError if not."""
        # TODO: Add the possibility to insert strings on top of lists.
        if df.empty:
            raise EmptyDataFrameError(f"Empty DataFrame!")
        to_check_cols = ["Distance", "Time"]

        if cols:
            to_check_cols = cols

        df_cols = df.columns

        if "Distance" not in df_cols:
            raise MissingColumnError("Distance")

        if pd.api.types.is_float_dtype(df["Distance"]):
            raise TypeError(f"'Distance' Column is type float!")

        for col in to_check_cols:
            if col not in df_cols:
                raise MissingColumnError(f"col: {col} is missing!")

        return True

