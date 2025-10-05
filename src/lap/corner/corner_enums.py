from enum import Enum


class ReturnFormat(Enum):
    DATAFRAME = "dataframe"
    DATACLASS = "dataclass"
    DICT = "dict"
    JSON = "json"