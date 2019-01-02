# Copyright 2018 Mark S. Weiss

from bisect import bisect_left
from enum import Enum

from aleatoric.note_sequence import NoteSequence
from aleatoric.utils import validate_optional_types, validate_type


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
    """Class to represent and manage Meter in a musical Measure/Bar. Offers facilities for representing and
       calculating meter using traditional units or floating point values. Can also apply quantizing to a
       NoteSequence to either fit the notes with the same ration of separation between them but scaled to the
       duration of the Measure, or to fit notes to the closest beat in the Measure. str displays information about
       the configuration of the object, but repr displays the meter in traditional notation.
    """
    def __init__(self, beats_per_measure: int = None, beat_dur: NoteDur = None, quantizing: bool = True):
        validate_optional_types(('beats_per_measure', beats_per_measure, int), ('beat_dur', beat_dur, NoteDur),
                                ('quantizing', quantizing, bool))

        self.beats_per_measure = beats_per_measure
        self.beat_dur = beat_dur.value
        self.beats_per_note = self.beat_dur / self.beats_per_measure
        # Use arg value of beats_per_measure because we want to use range(int)
        self.beat_start_times = [0.0 + (self.beat_dur * i) for i in range(self.beats_per_measure)]
        self.measure_dur = self.beats_per_measure * self.beat_dur
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

    def quantize_to_beat(self, note_sequence: NoteSequence):
        """Adjusts each note start_time to the closest beat time, so that each note will start on a beat.
        """
        validate_type('note_sequence', note_sequence, NoteSequence)

        if self.quantizing:
            # First quantize() to make sure notes in NoteSequence are scaled to duration of Measure
            self.quantize(note_sequence)
            # Then adjust note start times to closest beat
            # Algorithm:
            #  - self.beat_start_times is sorted, so use binary search strategy to find closest note in O(logN) time
            #  - call bisect to find insertion point for note in the sequence of start times, the cases are:
            #  -   insertion point i == 0, we are done, the note quantizes to the first beat
            #  -   insertion point i > 0, then note.start >= beat_start_times[i - 1] <= note.start < beat_start_times[i]
            #  -     in this case test distance of each beat_start_time to note.start and pick the closest one

            # Append measure end time to beat_start_times as a sentinel value for bisect()
            beat_start_times = self.beat_start_times + [self.measure_dur]
            for note in note_sequence.note_list:
                i = bisect_left(beat_start_times, note.start)
                # Note maps to 0th beat
                if i == 0:
                    note.start = 0.0
                    continue
                # Note starts after last beat, so maps to last beat
                elif i == len(beat_start_times):
                    note.start = self.beat_start_times[-1]
                    continue
                # Else note.start is between two beats in the range 1..len(beat_start_times) - 1
                # The note is either closests to beat_start_times[i - 1] or beat_start_times[i]
                prev_start = beat_start_times[i - 1]
                next_start = beat_start_times[i]
                prev_gap = note.start - prev_start
                next_gap = next_start - note.start
                if prev_gap <= next_gap:
                    note.start = prev_start
                else:
                    note.start = next_start

    def __str__(self):
        return (f'beats_per_measure: {self.beats_per_measure} beat_dur: {self.beat_dur} '
                f'beats_per_note: {self.beats_per_note} quantizing: {self.quantizing}')

    def __repr__(self):
        return f'{self.beats_per_measure} / {self.beat_dur}'

    def __eq__(self, other: 'Meter') -> bool:
        return self.beats_per_measure == other.beats_per_measure and \
            self.beat_dur == other.beat_dur and \
            self.quantizing == other.quantizing
