import pandas as pd


from src.lap.lap_analyzer import LapAnalyzer
from src.lap.lap_telemetry import LapTelemetry

from logger import get_logger
from src.telemetry.telemetry_calculator import TelemetryCalculator
from src.telemetry.telemetry_utils import get_corner_df_from_df, get_segment_df_from_lap_fd, segment_to_df, corner_to_df

log = get_logger("Lap - logger", to_console=False)

class Lap:
    def __init__(self, raw_lap_df: pd.DataFrame, track_name: str, driver: str = "User"):
        """Initial API Object for working with laps."""
        self._raw_df: pd.DataFrame = TelemetryCalculator.calc_g_force_vector(raw_lap_df)
        self._analyze = LapAnalyzer(self._raw_df)
        self._telemetry = LapTelemetry(self._raw_df)

        # --- public settings ---
        self.track_name: str = track_name
        self.lap_time_s: float = self._raw_df["Time"].iloc[-1] - self._raw_df["Time"].iloc[0]

        self.corners_df = self._load_corners()
        self.segments_df = self._load_segments()
        self.driver = driver
        self.corner_ids = self._raw_df["corner_id"].dropna().unique().tolist()
        self.segment_ids = self._raw_df["segment_id_x"].dropna().unique().tolist()

    def __repr__(self):
        print(f"Track: {self.track_name}\nLap-Time: {self.lap_time_s}")
    def __str__(self):
        return f"Track: {self.track_name}\nLap-Time: {self.lap_time_s}"
    def get_corners_df(self, frmt:str="DataFrame") -> pd.DataFrame | dict:
        """
        Returns a DataFrame with all corners' calculated and meta-data.
        :param frmt: ["DataFrame", "dict"]
        """
        if frmt == "DataFrame":
            return self.corners_df
        elif frmt == "dict":
            return self.corners_df.to_dict(orient="index")

    def get_segments_df(self, frmt:str="DataFrame") -> pd.DataFrame | dict:
        """
          Returns a DataFrame with all segments' calculated and meta-data.
          :param frmt: ["DataFrame", "dict"]
          """
        if frmt == "DataFrame":
            return self.segments_df
        elif frmt == "dict":
            return self.segments_df.to_dict(orient="index")

    def get_corner_df_by_id(self, _id: int) -> pd.DataFrame:
        """Returns all calculated and meta corner data in a single row DataFrame."""
        if _id not in self.corner_ids:
            raise ValueError(f"{id=}, not in self.corner_ids!")

        _corner = self.corners_df.loc[[_id]]
        return _corner
    def get_segment_df_by_id(self, _id: int) -> pd.DataFrame:
        """Returns all calculated and meta segment data in a single row DataFrame."""
        if _id not in self.segment_ids:
            raise ValueError(f"{id=}, not in self.segment_ids!")
        _segment = self.segments_df.loc[[_id]]
        return _segment

    def get_raw_df(self, segment_id: int=None, corner_id: int=None, area: tuple[int,int]=None) -> pd.DataFrame:
        """Get the raw normalized DataFrame for a certain area. You can either choose segment_id, corner_id or area. By default, you get the complete raw_df."""
        def slice_by_distance(start: int, end: int):
            return self._raw_df[(self._raw_df["Distance"] >= start) & (self._raw_df["Distance"] <= end)].copy()
        if segment_id and segment_id in self.segment_ids:
            mask = self._raw_df["segment_id_x"] == segment_id
            _start = self._raw_df[mask]["Distance"].min()
            _end = self._raw_df[mask]["Distance"].max()

            return slice_by_distance(_start, _end)

        if corner_id and corner_id in self.corner_ids:
            _start = self._raw_df[self._raw_df["corner_id"] == corner_id]["Distance"].iloc[0]
            _end = self._raw_df[self._raw_df["corner_id"] == corner_id]["Distance"].iloc[-1]

            return slice_by_distance(_start, _end)

        if area:
            _start, _end = area
            if not (self._raw_df["Distance"] == _start).any() or not (self._raw_df["Distance"] == _start).any():
                return pd.DataFrame()
            if _start > _end:
                return slice_by_distance(_end, _start)
            return slice_by_distance(_start, _end)

        return self._raw_df


    def _load_segments(self, _lap_df:pd.DataFrame=None) -> pd.DataFrame:
        """Loads and returns a DataFrame consisting of all analyzed segments."""
        lap_df = self._raw_df
        if _lap_df is not None:
            log.debug(f"{lap_df.info()=}")

        segments = []
        # Filling all the rows
        for _id in sorted(lap_df["segment_id_x"].dropna().unique()):
            _segment_df = get_segment_df_from_lap_fd(_id, lap_df)
            _segment, _segment_metrics = self._analyze.segment(_segment_df)
            #print(f"{_segment=}")
            segment_df = segment_to_df(_segment, _segment_metrics)

            segments.append(segment_df)
        _final_df = pd.concat(segments, ignore_index=True)

        #print(_final_df)
        return _final_df.fillna(0)
    def _load_corners(self, _lap_df:pd.DataFrame=None) -> pd.DataFrame:
        """Loads and returns a DataFrame consisting of all analyzed corners."""
        lap_df = self._raw_df
        if _lap_df is not None:
            log.debug(f"{lap_df.info()=}")
        corners: list = []
        for _id in sorted(lap_df["corner_id"].dropna().unique()):
            _corner_df = get_corner_df_from_df(_id, lap_df)
            _corner = self._analyze.corner(_corner_df)
            _corner_metrics = _corner.metrics
            corner_df = corner_to_df(_corner, _corner_metrics)
            corners.append(corner_df)

        _final_df = pd.concat(corners, ignore_index=True)

        return _final_df.fillna(0)


