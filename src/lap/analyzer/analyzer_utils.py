from abc import ABC, abstractmethod
import pandas as pd
from dataclasses import dataclass
class AnalyzerMother:
    """"""
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> dataclass:
        raise NotImplementedError