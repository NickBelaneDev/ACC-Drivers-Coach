from abc import ABC, abstractmethod
from typing import Any
import pandas as pd
from dataclasses import dataclass
from src.lap.lap_dataclasses import Corner
from src.lap.adapter import DataAdapter


class ToReturnStrategy(ABC):
    """Abstract base for conversion strategies.

    Converts a :class:`Corner` object into a requested target representation
    (e.g., pandas DataFrame, dataclass instance, dict, or JSON). Use this
    interface to keep calling code agnostic of the concrete output format.

    Notes:
        - Strategies are stateless and thread-safe.
        - Implementations must not mutate the input ``corner``.

    Example:
        >>> strategy = DataFrameStrategy  # or DictStrategy, JsonStrategy, ...
        >>> result = strategy.get(corner)  # returns format defined by strategy
    """

    @staticmethod
    @abstractmethod
    def get(corner: dataclass) -> Any:
        """Convert a corner into the strategy's target representation.

        Args:
            corner: The corner object to convert.

        Returns:
            The converted representation as defined by the concrete strategy.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
        """
        raise NotImplementedError("The method is not set yet!")


class DataFrameStrategy(ToReturnStrategy):
    """Return a pandas DataFrame representation of a corner.

    The DataFrame typically contains a single row with all metadata and
    computed metrics of the given corner. This format is convenient for
    downstream analytics, joins, and vectorized operations.

    Example:
        >>> df = DataFrameStrategy.get(corner)
        >>> assert isinstance(df, pd.DataFrame)
        >>> df.columns  # stable, enum-backed column names
    """

    @staticmethod
    def get(corner: dataclass) -> pd.DataFrame:
        """Convert the corner into a one-row pandas DataFrame.

        Args:
            corner: The corner to convert.

        Returns:
            pd.DataFrame: A single-row DataFrame containing the corner's
            fields and derived metrics.
        """
        return DataAdapter.to_dataframe(corner)


class DataclassStrategy(ToReturnStrategy):
    """Return the dataclass instance unchanged (pass-through).

    Useful when you want to work with the strongly-typed ``Corner`` object
    in domain logic, without any serialization or structural changes.

    Example:
        >>> c = DataclassStrategy.get(corner)
        >>> c is corner  # True
    """

    @staticmethod
    def get(corner: dataclass) -> "Corner":
        """Return the input dataclass instance as-is.

        Args:
            corner: The corner to return.

        Returns:
            Corner: The same dataclass instance (no copy, no mutation).
        """
        return corner


class DictStrategy(ToReturnStrategy):
    """Return a plain Python dict representation of a corner.

    The dictionary is JSON-serializable and suitable for storage, logging,
    or lightweight APIs where a full DataFrame is unnecessary.

    Example:
        >>> payload = DictStrategy.get(corner)
        >>> import json; json.dumps(payload)  # serialize as JSON
    """

    @staticmethod
    def get(corner: dataclass) -> dict:
        """Convert the corner into a JSON-serializable dictionary.

        Args:
            corner: The corner to convert.

        Returns:
            dict: A flat or nested dictionary (depending on the adapter)
            containing all corner fields and metrics.
        """
        return DataAdapter.to_dict(corner)


class JsonStrategy(ToReturnStrategy):
    """Return a JSON-ready representation of a corner.

    Depending on your ``DataAdapter.to_json`` implementation, this may
    return either a pretty-printed JSON *string* or a JSON-serializable
    *dict*. In this codebase the adapter typically returns a pretty string
    with ``indent=4``.

    Example:
        >>> doc = JsonStrategy.get(corner)
        >>> print(doc)  # human-readable JSON (indent=4)
    """

    @staticmethod
    def get(corner: dataclass) -> dict:
        """Convert the corner into a JSON representation.

        Args:
            corner: The corner to convert.

        Returns:
            dict: A JSON-serializable object or a preformatted JSON string,
            depending on ``DataAdapter.to_json``. By convention, this project
            uses pretty-printed JSON with indent=4.
        """
        return DataAdapter.to_json(corner)