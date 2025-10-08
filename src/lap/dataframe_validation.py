import pandas as pd
from src.logger import get_logger

log = get_logger(name="data_frame_validator", to_console=False, level="DEBUG")
class MissingColumnError(Exception):
    """
    Raised when a required column is missing from the DataFrame.

    Attributes
    ----------
    col : str
        The name of the column that was not found.
    """
    def __init__(self, col: str):
        super().__init__(f"Required column '{col}' is missing.")

class EmptyDataFrameError(Exception):
    """
    Raised when the provided DataFrame is empty.

    Typically used to stop analysis early before attempting
    metric computations on invalid or uninitialized datasets.
    """
    def __init__(self, message="DataFrame is empty!"):
        super().__init__(message)



class DataFrameValidator:
    """
    Utility class for validating pandas DataFrames used in telemetry analysis.

    The ``DataFrameValidator`` provides a consistent interface for ensuring
    that incoming telemetry DataFrames contain the required structural fields
    and are non-empty before further processing.

    It prevents common downstream errors by:
      - enforcing mandatory column presence (e.g., ``Distance``, ``Time``),
      - detecting empty or partially incomplete DataFrames,
      - optionally validating a custom subset of columns.

    Example
    -------
    >>> df = pd.DataFrame({"Distance": [0, 1], "Time": [0.1, 0.2], "Speed": [120, 140]})
    >>> DataFrameValidator.validate_df(df, ["Speed"])
    True

    Raises
    ------
    EmptyDataFrameError
        If the DataFrame contains no rows.
    MissingColumnError
        If one of the required columns is not present.
    TypeError
        If the ``Distance`` column has an invalid data type (e.g., float).
    """
    @staticmethod
    def validate_df(df: pd.DataFrame,
                    cols: list[str] | str=None) \
            -> bool:
        """
        Validate that a DataFrame is suitable for telemetry analysis.

        Checks include:
          1. The DataFrame is not empty.
          2. The column ``Distance`` exists and is not of type float.
          3. The column ``Time`` exists (or other specified columns).
          4. All user-specified columns (via ``cols``) are present.

        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to validate.
        cols : list[str] | str, optional
            Specific column(s) that must be present. If not provided,
            defaults to ``["Distance", "Time"]``.

        Returns
        -------
        bool
            Returns ``True`` if validation succeeds. Intended to be
            used as a lightweight assertion before analysis.

        Raises
        ------
        EmptyDataFrameError
            If the DataFrame contains no rows.
        MissingColumnError
            If one of the required columns is missing.
        TypeError
            If the ``Distance`` column is of type float instead of int.

        Notes
        -----
        - ``Distance`` is assumed to represent cumulative lap distance
          in meters and must therefore be an integer-like sequence.
        - The method raises rather than returning ``False`` to make
          validation failures explicit and debuggable.
        """
        # TODO: Add the possibility to insert strings on top of lists.
        if df.empty:
            raise EmptyDataFrameError(f"Empty DataFrame!")
        to_check_cols = ["Distance", "Time"]

        if cols:
            to_check_cols = cols

        df_cols = df.columns

        if "Distance" not in df_cols:
            raise MissingColumnError(f"col: 'Distance' is missing!")

        if pd.api.types.is_float_dtype(df["Distance"]):
            raise TypeError(f"'Distance' Column is type float!")

        for col in to_check_cols:
            if col not in df_cols:
                raise MissingColumnError(f"col: {col} is missing!")
        return True

