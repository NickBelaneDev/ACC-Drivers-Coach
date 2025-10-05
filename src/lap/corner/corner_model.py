import pandas as pd
from typing import Literal
from .corner_enums import ReturnFormat
import src.lap.metrics_enums as me
from .return_strategies import DictStrategy, DataclassStrategy, DataFrameStrategy, JsonStrategy

from src.lap.analyzer.corner_analyzer import CornerBuilder
from src.lap.dataframe_validation import DataFrameValidator, EmptyDataFrameError

from src.lap.lap_dataclasses import Corner
from src.telemetry.telemetry_utils import get_df_from_area

MODE = Literal["DataFrame", "dict", "json", "dataclass"]


STRATEGIES = {ReturnFormat.DATAFRAME: DataFrameStrategy,
              ReturnFormat.DATACLASS: DataclassStrategy,
              ReturnFormat.DICT: DictStrategy,
              ReturnFormat.JSON: JsonStrategy}

class CornerModel:
    def __init__(self, raw_corner_df: pd.DataFrame):
        DataFrameValidator.validate_df(raw_corner_df)
        self.raw_corner_df = raw_corner_df
        self._corner_builder = CornerBuilder
        self.corner = self._load_corner_object_from_raw_df()

    def _load_corner_object_from_raw_df(self):
        corner = self._corner_builder.build_corner(self.raw_corner_df)
        return corner

    def is_empty(self):
        return self.corner.is_empty()

    def get_raw_corner_df(self, cols: list=None) -> pd.DataFrame | None:
        if not cols:
            return self.raw_corner_df
        if cols:
            DataFrameValidator.validate_df(self.raw_corner_df, cols)

            if len(cols) == 1:
                cols = cols[0]

            return self.raw_corner_df[cols]
        raise ValueError(f"Could not return the raw_corner_df.")

    CORNER_WINDOW_CHECKPOINTS = Literal["brake_point", "start", "apex", "end"]

    def get_raw_corner_df_window(
            self,
            start: CORNER_WINDOW_CHECKPOINTS="brake_point",
            end: CORNER_WINDOW_CHECKPOINTS="end",
            cols: list[str] | str = None
    ) -> pd.DataFrame:
        """
        Returns a section of the raw corner telemetry DataFrame between two defined checkpoints.

        This method slices ``self.raw_corner_df`` between two positional references
        within a corner (e.g. from brake point to apex or apex to exit).
        The valid checkpoints are: ``"brake_point"``, ``"start"``, ``"apex"``, and ``"end"``.
        On default the method returns the complete ``self.raw_corner_df``.

        If ``end`` is located before ``start``, the values are automatically swapped.
        Optionally, you can specify which telemetry columns to include in the result.

        :param start:
            The starting reference point of the slice.
            One of ``"brake_point"``, ``"start"``, ``"apex"``, or ``"end"``.
        :param end:
            The ending reference point of the slice.
            One of ``"brake_point"``, ``"start"``, ``"apex"``, or ``"end"``.
        :param cols:
            A list of telemetry column names or a single column name to include in the result.
            If ``None``, all available columns are returned.
        :type cols: list[str] | str | None
        :raises EmptyDataFrameError:
            If the resulting DataFrame is empty after slicing or column selection.
        :return:
            A copy of the filtered DataFrame containing telemetry data between the selected checkpoints.
        :rtype: pandas.DataFrame

        **Example:**
            >>> df = CornerModel().get_raw_corner_df_window(
            ...     start="brake_point",
            ...     end="apex",
            ...     cols=["SPEED", "BRAKE"]
            ... )
        """

        corner_map = {
            "brake_point": self.corner.metrics.driver.brake.brake_point_m,
            "start": self.corner.start_m,
            "apex": self.corner.apex_m,
            "end": self.corner.end_m,
        }

        _start = corner_map[start]
        _end = corner_map[end]

        # swap if order is reversed
        if _end < _start:
            _start, _end = _end, _start

        df = self.raw_corner_df.query("Distance >= @_start and Distance <= @_end").copy()

        if cols:
            # normalize cols type
            if isinstance(cols, str):
                cols = [cols]

            # validate before filtering
            DataFrameValidator.validate_df(df, cols)

            # select only requested columns
            df = df[cols]

        if df.empty:
            raise EmptyDataFrameError("Resulting corner DataFrame is empty.")

        return df

    def get_corner(self, mode: ReturnFormat = ReturnFormat.DATACLASS):
        """
            Returns the full corner object containing both meta-data and all calculated metrics.

            This method gives access to the complete `Corner` instance for the currently
            analyzed corner, including identifiers, geometry (start, apex, end), and
            performance-related values. The output format can be freely chosen.

            :param mode:
                Defines the output format of the returned corner data.
                Options include `ReturnFormat.DATACLASS`, `ReturnFormat.DICT`,
                `ReturnFormat.DATAFRAME`, or `ReturnFormat.JSON`.
            :type mode: ReturnFormat
            :raises KeyError:
                If the provided mode is not supported by the strategy map.
            :return:
                The complete corner object in the chosen format.
            :rtype: dataclass | dict | pandas.DataFrame | str
            """
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner)

    def get_corner_metrics(self, mode: ReturnFormat = ReturnFormat.DATACLASS):
        """
        Returns all calculated metrics for the selected corner.

        These include measurements such as entry speed, apex speed, braking distance,
        average steering angle, throttle input, and g-forces.
        This is the primary method if you only need the numeric analysis of a corner.

        :param mode:
            Defines the output format for the metrics (dataclass, dict, DataFrame, or JSON).
        :type mode: ReturnFormat
        :raises KeyError:
            If the requested mode is not available in the strategy map.
        :return:
            The corner's performance metrics in the requested format.
        :rtype: dataclass | dict | pandas.DataFrame | str
        """
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics)

    def get_driver_performance(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        """
        Returns the driver-specific performance data for this corner.

        This includes all data that describe how the driver performed in this section,
        such as braking behavior, throttle timing, trail braking, and input smoothness.
        Use this method to focus on the human performance aspect rather than vehicle physics.

        :param mode:
            Output format for the driver performance data.
        :type mode: ReturnFormat
        :raises KeyError:
            If the selected mode is not supported.
        :return:
            Driver performance metrics in the chosen format.
        :rtype: dataclass | dict | pandas.DataFrame | str
        """
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics.driver)

    def get_car_dynamics(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        """
        Returns the physical dynamics of the car throughout this corner.

        This includes parameters such as longitudinal and lateral g-forces,
        speed evolution, rotation rate (ROTY), and vehicle balance.
        Use this to analyze how the car behaves and reacts to driver input.

        :param mode:
            Output format for the car dynamics data.
        :type mode: ReturnFormat
        :raises KeyError:
            If the provided mode is not supported by the available strategies.
        :return:
            Car dynamics information in the selected format.
        :rtype: dataclass | dict | pandas.DataFrame | str
        """
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics.dynamics)

    def get_corner_meta_data(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        """
        Returns meta-information about the current corner.

        This includes descriptive and positional data such as corner name,
        start distance, apex distance, and end distance. It does not contain
        performance metrics but defines the corner’s geometry and identity on the track.

        :param mode:
            Output format for the meta data (dataclass, dict, DataFrame, or JSON).
        :type mode: ReturnFormat
        :raises KeyError:
            If the given mode is not part of the supported strategy list.
        :return:
            Corner meta data in the requested format.
        :rtype: dataclass | dict | pandas.DataFrame | str
        """
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]

        meta_data_corner = Corner(
            id=self.corner.id,
            name=self.corner.name,
            start_m=self.corner.start_m,
            apex_m=self.corner.apex_m,
            end_m=self.corner.end_m,
            metrics=None
        )

        return strategy.get(meta_data_corner)