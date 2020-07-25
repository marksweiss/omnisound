# Copyright 2018 Mark S. Weiss

from enum import Enum
from random import random

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.utils.math_utils import (sign)
from omnisound.utils.validation_utils import validate_optional_type, validate_optional_types, validate_type, \
    validate_types


# TODO THIS LOGIC IS ALL WRONG. SHOULD NOT USE A FACTOR PROPORTIONAL TO START!! SHOULD USE JITTER RANGE
#  and either fixed or randomly jitter (start +- swing) within that range, without moving start time more than that.
class Swing(object):

    DEFAULT_SWING_ON = False
    DEFAULT_SWING_RANGE = 0.01

    class SwingDirection(Enum):
        Forward = 'Forward'
        Reverse = 'Reverse'
        Both = 'Both'

    DEFAULT_SWING_DIRECTION = SwingDirection.Both

    class SwingJitterType(Enum):
        Fixed = 'Fixed'
        Random = 'Random'

    DEFAULT_SWING_JITTER_TYPE = SwingJitterType.Fixed

    def __init__(self, swing_on: bool = None,
                 swing_range: float = None,
                 swing_direction: SwingDirection = None,
                 swing_jitter_type: SwingJitterType = None):
        validate_optional_types(('swing_on', swing_on, bool), ('swing_range', swing_range, float),
                                ('swing_direction', swing_direction, Swing.SwingDirection),
                                ('swing_jitter_type', swing_jitter_type, Swing.SwingJitterType))

        if swing_on is None:
            swing_on = Swing.DEFAULT_SWING_ON
        self.swing_on = swing_on
        if swing_range is None:
            self.swing_range = Swing.DEFAULT_SWING_RANGE
        else:
            self.swing_range = swing_range
        self.swing_direction = swing_direction or Swing.DEFAULT_SWING_DIRECTION
        self.swing_jitter_type = swing_jitter_type or Swing.DEFAULT_SWING_JITTER_TYPE

    def is_swing_on(self):
        return self.swing_on

    def set_swing_on(self) -> 'Swing':
        self.swing_on = True
        return self

    def set_swing_off(self) -> 'Swing':
        self.swing_on = False
        return self

    def apply_swing(self, note_sequence: NoteSequence,
                    swing_direction: SwingDirection = None,
                    swing_jitter_type: SwingJitterType = None):
        """Applies swing to all notes in note_sequence, using current object settings, unless swing_direction
           is provided. In that case the swing_direction arg overrides self.swing_direction and is applied.
        """
        validate_type('note_sequence', note_sequence, NoteSequence)
        if self.swing_on:
            for note in note_sequence:
                note.start += self.calculate_swing_adjust(swing_direction, swing_jitter_type)
                if note.start < 0.0:
                    note.start = 0.0

    # This is also called from Measure directly, so it validates the swing_direction and swing_jitter_type args
    def calculate_swing_adjust(self,
                               swing_direction: SwingDirection = None,
                               swing_jitter_type: SwingJitterType = None):
        validate_optional_types(('swing_direction', swing_direction, Swing.SwingDirection),
                                ('swing_jitter_type', swing_jitter_type, Swing.SwingJitterType))
        swing_direction = swing_direction or self.swing_direction
        swing_jitter_type = swing_jitter_type or self.swing_jitter_type

        swing_adjust = self.swing_range
        if swing_jitter_type == Swing.SwingJitterType.Random:
            swing_adjust *= random()

        if swing_direction == Swing.SwingDirection.Forward:
            return swing_adjust
        elif swing_direction == Swing.SwingDirection.Reverse:
            return -swing_adjust
        elif swing_direction == Swing.SwingDirection.Both:
            return sign() * swing_adjust

    def __eq__(self, other: 'Swing') -> bool:
        return self.swing_on == other.swing_on and \
               self.swing_range == pytest.approx(other.swing_range) and \
               self.swing_direction == other.swing_direction and \
               self.swing_jitter_type == other.swing_jitter_type
