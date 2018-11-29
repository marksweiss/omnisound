# Copyright 2018 Mark S. Weiss

from enum import Enum

from aleatoric.note import NoteSequence
from aleatoric.utils import sign, validate_optional_types, validate_type


class NoteDur(Enum):
    _1_0 = 1.0
    _0_5 = 0.5
    _0_25 = 0.25
    _0_125 = 0.125
    _0_00625 = 0.00625
    _0_0003125 = 0.0003125
    _0_000015625 = 0.000015625
    WHL = _1_0
    WHOLE = _1_0
    HLF = _0_5
    HALF = _0_5
    QRTR = _0_25
    QUARTER = _0_25
    EITH = _0_125
    EIGHTH = _0_125
    SXTNTH = _0_00625
    SIXTEENTH = _0_00625
    THRTYSCND = _0_0003125
    THIRTYSECOND = _0_0003125
    SXTYFRTH = _0_000015625
    SIXTYFOURTH = _0_000015625


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
        self.swing_on = swing_on
        if swing_factor is None:
            swing_factor = Swing.DEFAULT_SWING_FACTOR
        self.swing_factor = swing_factor
        self.swing_direction = swing_direction or Swing.DEFAULT_SWING_DIRECTION

    def is_swing_on(self):
        return self.swing_on

    def swing_on(self):
        self.swing_on = True

    def swing_off(self):
        self.swing_on = False

    def apply_swing(self, note_sequence: NoteSequence):
        validate_type('note_sequence', note_sequence, NoteSequence)

        if not self.swing_on:
            return
        else:
            for note in note_sequence.note_list:
                swing_adj = note.start * self.swing_factor
                if self.swing_direction == Swing.SwingDirection.Forward:
                    note.start += swing_adj
                elif self.swing_direction == Swing.SwingDirection.Reverse:
                    note.start -= swing_adj
                else:
                    note.start += sign() * swing_adj


class Meter(object):

    DEFAULT_QUANTIZING = False

    def __init__(self, beats_per_measure: int = None, beat_dur: NoteDur = None, quantizing: bool = None):
        validate_optional_types(('beats_per_measure', beats_per_measure, int), ('beat_dur', beat_dur, NoteDur),
                                ('quantizing', quantizing, bool))

        self.beats_per_measure = beats_per_measure
        self.beat_dur = beat_dur.value
        self.measure_dur = float(self.beats_per_measure) * self.beat_dur
        if quantizing is None:
            quantizing = Meter.DEFAULT_QUANTIZING
        self.quantizing = quantizing

    def is_quantizing(self):
        return self.quantizing

    def quantizing_on(self):
        self.quantizing = True

    def quantizing_off(self):
        self.quantizing = False

    def quantize(self, note_sequence: NoteSequence):
        validate_type('note_sequence', note_sequence, NoteSequence)

        if self.quantizing:
            notes_dur = sum([note.dur for note in note_sequence.note_list])
            # If notes_duration == measure_duration then exit
            if notes_dur == self.measure_dur:
                return
            else:
                note_adj_factor = self.measure_dur / notes_dur
                # new_note.duration *= note_adj_factor
                # new_note.start = note.start + (new_note.duration - note.duration)
                for note in note_sequence.note_list:
                    new_dur = note.dur * note_adj_factor
                    if note.start > 0.0:
                        note.start = note.start + (new_dur - note.dur)
                    note.dur = new_dur


# TODO Scale class with root, notes in scale, transpose()
# TODO Chord class
# TODO ChordSequence
# This is compact and looks like what I need: https://github.com/gciruelos/musthe
# Good base for scales, chords and generating the notes from them
# Make this the basis of the Scale system and map to pitch values for each backend
class Measure(object):
    """Represents a musical measure in a musical `Score`. As such it includes a `NoteSequence`
       and attributes that affect the performance of all `Note`s in that `NoteSequence`.
       Additional attributes are `Meter`, `BPM`, `Scale` and `Key`.
    """
    def __init__(self, note_sequence: NoteSequence = None, meter: Meter = None, swing: Swing = None):
        validate_optional_types(('note_sequence', note_sequence, NoteSequence), ('meter', meter, Meter),
                                ('swing', swing, Swing))

        self.note_sequence = note_sequence
        self.meter = meter
        self.swing = swing

    def quantize(self):
        self.meter.quantize(self.note_sequence)

    def apply_swing(self):
        self.swing.apply_swing(self.note_sequence)
