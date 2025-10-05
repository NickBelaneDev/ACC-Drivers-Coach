import pandas as pd
from typing import Literal
from corner_enums import ReturnFormat
from return_strategies import DictStrategy, DataclassStrategy, DataFrameStrategy, JsonStrategy

from src.lap.analyzer.corner_analyzer import CornerBuilder
from src.lap.dataframe_validation import DataFrameValidator

from src.lap.lap_dataclasses import Corner
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

    def get_corner(self, mode: ReturnFormat = ReturnFormat.DATACLASS):
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner)

    def get_corner_metrics(self, mode: ReturnFormat = ReturnFormat.DATACLASS):
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics)

    def get_driver_performance(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics.driver)


    def get_car_dynamics(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner.metrics.dynamics)


    def get_corner_meta_data(self, mode:ReturnFormat=ReturnFormat.DATACLASS):
        if mode not in STRATEGIES:
            raise KeyError(f"mode: {mode} not in {STRATEGIES=}")
        strategy = STRATEGIES[mode]
        return strategy.get(self.corner)