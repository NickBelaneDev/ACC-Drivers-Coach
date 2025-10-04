import pandas as pd
import numpy as np
import math

from .brake_analyzer import BrakeAnalyzer
from .gforce_analyzer import GForceAnalyzer
from .speed_analyzer import SpeedAnalyzer
from .throttle_analyzer import ThrottleAnalyzer
from .steer_analyzer import SteerAnalyzer
from .gforce_analyzer import GForceAnalyzer


class CornerAnalyzer:
    def __init__(self):
        self._speed_analyzer = SpeedAnalyzer
        self._steering_metrics = SteerAnalyzer
        self._throttle_analyzer = ThrottleAnalyzer
        self._brake_analyzer = BrakeAnalyzer
        self._g_force_analyzer = GForceAnalyzer



    def _analyze_atomar_metrics(self):

        raise NotImplementedError


