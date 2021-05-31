# Copyright 2021 Mark S. Weiss

from random import random

class SettingsBase:
    @staticmethod
    def meets_condition(threshold: float) -> bool:
        return random() < threshold
