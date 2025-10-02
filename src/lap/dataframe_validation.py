import pandas as pd
import math
import numpy as np

class DataFrameColumnError(Exception):
    pass

class DataFrameValidator:

    @staticmethod
    def check_has_cols(df: pd.DataFrame, cols: list[str]) -> bool:
        """Check if the DataFrame is not empty and has all cols. Raises a ValueError if not."""
        if df.empty:
            raise ValueError(f"Empty DataFrame!")

        df_cols = df.columns

        missing_cols: list[str] = []
        for col in cols:
            if col not in df_cols:
                if col in missing_cols:
                    raise DataFrameColumnError(f"col: {col} is already in missing_cols: {missing_cols}! ")
                missing_cols.append(col)

        return True

