# Copyright 2018 Mark S. Weiss

from enum import Enum

from omnisound.note.adapters.note import Note
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.utils.utils import (sign, validate_optional_type,
                                   validate_optional_types, validate_type,
                                   validate_types)


class Swing(object):

    DEFAULT_SWING_ON = False
    DEFAULT_SWING_FACTOR = 0.01

    class SwingDirection(Enum):
        Forward = 'Forward'
        Reverse = 'Reverse'
        Both = 'Both'

    DEFAULT_SWING_DIRECTION = SwingDirection.Both

    def __init__(self, swing_on: bool = None, swing_factor: float = None, swing_direction: SwingDirection = None):
        validate_optional_types(('swing_on', swing_on, bool), ('swing_factor', swing_factor, float),
                                ('swing_direction', swing_direction, Swing.SwingDirection))

        if swing_on is None:
            swing_on = Swing.DEFAULT_SWING_ON
        self.swinging = swing_on
        if swing_factor is None:
            swing_factor = Swing.DEFAULT_SWING_FACTOR
        self.swing_factor = swing_factor
        self.swing_direction = swing_direction or Swing.DEFAULT_SWING_DIRECTION

    def is_swing_on(self):
        return self.swinging

    def swing_on(self) -> 'Swing':
        self.swinging = True
        return self

    def swing_off(self) -> 'Swing':
        self.swinging = False
        return self

    def apply_swing(self, note_sequence: NoteSequence, swing_direction: SwingDirection = None):
        """Applies swing to all notes in note_sequence, using current object settings, unless swing_direction
           is provided. In that case the swing_direction arg overrides self.swing_direction and is applied.
        """
        validate_type('note_sequence', note_sequence, NoteSequence)
        validate_optional_type('swing_direction', swing_direction, Swing.SwingDirection)

        if not self.swinging:
            return
        else:
            swing_direction = swing_direction or self.swing_direction
            for note in note_sequence.notes:
                note.start += self.calculate_swing_adj(note, swing_direction)

    def calculate_swing_adj(self, note: Note = None,  swing_direction: SwingDirection = None):
        validate_types(('note', note, Note), ('swing_direction', swing_direction, Swing.SwingDirection))

        swing_adj = note.start * self.swing_factor
        if swing_direction == Swing.SwingDirection.Forward:
            return swing_adj
        elif swing_direction == Swing.SwingDirection.Reverse:
            return -swing_adj
        else:
            return sign() * swing_adj

    def __eq__(self, other: 'Swing') -> bool:
        return self.swinging == other.swinging and \
            self.swing_factor == other.swing_factor and \
            self.swing_direction == other.swing_direction
