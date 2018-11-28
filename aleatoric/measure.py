# Copyright 2018 Mark S. Weiss

from aleatoric.note import NoteSequence
from enum import Enum


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


class Meter(object):

    DEFAULT_QUANTIZING = True

    def __init__(self, beats_per_measure: int = None, beat_dur: NoteDur = None, quantizing: bool = None):
        Meter._validate(beats_per_measure, beat_dur)
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

    @staticmethod
    def _validate(beats_per_measure, beat_dur):
        if not isinstance(beats_per_measure, int) or not isinstance(beat_dur, NoteDur):
            raise ValueError(('`beats_per_measure` arg must be type `int` and `beat_dur type `NoteDur` '
                              f'beats_per_measure: {beats_per_measure} beat_length: {beat_dur}'))


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
    def __init__(self, note_sequence: NoteSequence = None, meter: Meter = None):
        self.note_sequence = note_sequence
        self.meter = meter

    def quantize(self):
        self.meter.quantize(self.note_sequence)