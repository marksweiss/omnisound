# Copyright 2018 Mark S. Weiss

from math import copysign
from random import random


def sign():
    return copysign(1.0, random() - 0.5)

