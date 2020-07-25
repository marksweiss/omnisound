# Copyright 2018 Mark S. Weiss

from bisect import bisect_left
from enum import Enum
from typing import Union

import pytest

from omnisound.note.container.note_sequence import NoteSequence
from omnisound.utils.validation_utils import validate_optional_types, validate_type, validate_type_choice


class NoteDur(Enum):
    _1_0 = 1.0
    _0_5 = 0.5
    _0_25 = 0.25
    _0_125 = 0.125
    _0_0625 = 0.0625
    _0_03125 = 0.03125
    _0_015625 = 0.015625
    WHL = _1_0
    WHOLE = _1_0
    HLF = _0_5
    HALF = _0_5
    QRTR = _0_25
    QUARTER = _0_25
    EITH = _0_125
    EIGHTH = _0_125
    SXTNTH = _0_0625
    SIXTEENTH = _0_0625
    THRTYSCND = _0_03125
    THIRTYSECOND = _0_03125
    SXTYFRTH = _0_015625
    SIXTYFOURTH = _0_015625


class InvalidQuantizationDurationException(Exception):
    pass


# TODO THIS NEEDS A NOTION OF TEMPO TO MAKE beat_start_times and quantizing valid
class Meter:
    """Class to represent and manage Meter in a musical Measure/Bar. Offers facilities for representing and
       calculating meter using traditional units or floating point values. Can also apply quantizing to a
       NoteSequence to either fit the notes with the same ration of separation between them but scaled to the
       duration of the Measure, or to fit notes to the closest beat in the Measure. str displays information about
       the configuration of the object, but repr displays the meter in traditional notation.

       `beat_duration` - the duration of one beat
       `beats_per_measure` - the number of quarter-note beats per measure

       For example: 4
                    4
       - `beats_per_measure` is an integer, 4
       - `beat_duration` argument is the duration of a beat in the measure, NoteDur.QUARTER
       In 4/4, there are 4 beats per measure and each beat is a quarter note.

       For example: 6
                    8
       - `beats_per_measure` is an integer, 6 - `beat_duration` argument is a NoteDuration, e.g NoteDur.EIGHTH
       In 6/8, there are 6 beats per measure and each beat is an eighth note
    """

    DEFAULT_QUARTER_NOTES_PER_MINUTE = 60
    SECS_PER_MINUTE = 60
    QUARTER_NOTE_DUR: float = NoteDur.QUARTER.value

    def __init__(self, beats_per_measure: int = None, beat_note_dur: NoteDur = None,
                 tempo: int = None, quantizing: bool = True):
        validate_optional_types(('beats_per_measure', beats_per_measure, int), ('beat_dur', beat_note_dur, NoteDur),
                                ('tempo', tempo, int), ('quantizing', quantizing, bool))

        self.quantizing = quantizing

        # Meter notation
        # Numerator of meter
        self.beats_per_measure = beats_per_measure
        # Inverse of denominator of meter, e.g. 4/4 is quarter note is 1 beat
        self.beat_note_dur = beat_note_dur
        # Meter in musical notation as a tuple, e.g. (4, 4)
        # noinspection PyTypeChecker
        self.meter_notation = (self.beats_per_measure, int(1 / self.beat_note_dur.value))

        # Each note is some fraction of a quarter note. So for N / 4 meters, this ratio is 1.
        # For N / 8 meters, e.g. 6 / 8, this ration os 0.5. This ratio multiplied by the actual time duration
        # of a quarter note, derived from the tempo in qpm, is the duration of a note
        # noinspection PyTypeChecker
        self.quarter_notes_per_beat_note = int(self.beat_note_dur.value / Meter.QUARTER_NOTE_DUR)

        # Actual note duration
        # Map note durations from meter, which are unitless, to time, using tempo, which is a ratio of
        # quarter-note beats to time. qpm == quarter notes per minute
        self._set_tempo_attributes(tempo)

    def _set_tempo_attributes(self, tempo: int):
        self.tempo_qpm = tempo or Meter.DEFAULT_QUARTER_NOTES_PER_MINUTE
        self.quarter_note_dur_secs = Meter.SECS_PER_MINUTE / self.tempo_qpm
        self.note_dur_secs = self.quarter_notes_per_beat_note * self.quarter_note_dur_secs
        self.measure_dur_secs = self.note_dur_secs * self.beats_per_measure
        self.beat_start_times_secs = [self.note_dur_secs * i for i in range(self.beats_per_measure)]

    def _get_tempo(self):
        return self.tempo_qpm

    def _set_tempo(self, tempo: int):
        self._set_tempo_attributes(tempo)

    tempo = property(_get_tempo, _set_tempo)

    def get_secs_for_note_time(self, note_time_val: Union[float, int, NoteDur]):
        """Helper to convert a note time in NoteDur or float that represents either a note start_time or
           note duration within a measure in the measure's meter into an absolute floating point value in
           seconds.
        """
        validate_type_choice('note_time_val', note_time_val, (float, int, NoteDur))

        dur = note_time_val
        if not isinstance(note_time_val, float) \
                and not isinstance(note_time_val, int) \
                and note_time_val in NoteDur:
            dur = note_time_val.value
        # noinspection PyTypeChecker
        return self.note_dur_secs * dur

    def is_quantizing(self):
        return self.quantizing

    def quantizing_on(self):
        self.quantizing = True

    def quantizing_off(self):
        self.quantizing = False

    def quantize(self, note_sequence: NoteSequence):
        """
        Also for the degree of quantization is this ratio:
        - `notes_duration` = `max(note.start + note.dur) for note in note_sequence`
        -- if the notes_duration matches the measure duration, then no quantization needed, return
        -- if notes run too long they must be shortened and have their start times made earlier
        -- if the notes don't run long enough, they must be lengthened to and have their start times made later

        - `total_adjustment` = `measure_duration - notes_duration`
        -- negative adjustment if notes_duration too long, positive adjustment if notes_duration not long enough
        -- total_adjustment must be < a whole note, i.e. < 1.0

        - Duration adjustment
        -- Each note.dur adjusted by `note.dur += (note.dur * total_adjustment)`

        - Start adjustment
        -- `start_adjustment = total_adjustment / len(note_sequence)`
        -- `for i, note in enumerate(note_sequence):
               note.start += start_adjustment * i`

        Example: Notes run longer than the duration of the measure

        measure ------------------------*
        0    0.25    0.50    0.75    1.00     1.25
        *********            *********************
        n0                   n1

        notes_duration = 1.25
        total_adjustment = 1.0 - 1.25 = -0.25
        start_adjustment = -0.25 / 2 = -0.125

        n0.dur += (0.25 * -0.25) = 0.25 -= 0.0625 = 0.1875
        n1.dur += (0.50 * -0.25) = 0.50 -= 0.125  = 0.375

        n0 index = 0, n0.start += 0.0
        n1 index = 1, n1.start += 1 * -0.125 = 0.75 -= 0.125 = 0.625

        measure ------------------------*
        0    0.25    0.50    0.75    1.00     1.25
        ****               **************
        (0.0, 0.1875)       (0.625, 0.375)
        n0                   n1
        """
        validate_type('note_sequence', note_sequence, NoteSequence)

        if self.quantizing:
            notes_dur = max([note.start + note.duration for note in note_sequence])
            if notes_dur == self.measure_dur_secs:
                return

            total_adjustment = self.measure_dur_secs - notes_dur
            # if abs(total_adjustment) > 1.0:
            #     raise InvalidQuantizationDurationException((f'quantization adjustment value of {total_adjustment} '
            #                                                 '> than maximum allowed adjustment of 1.0'))
            for note in note_sequence:
                dur_adjustment = note.duration * total_adjustment
                # Normalize duration adjustment by duration of note, because whole note == 1 and that is the entire
                # duration of a measure and the max adjustment, so every note adjusts as a ratio of its duration
                # to the total adjustment needed
                note.duration += dur_adjustment
                # Each note that doesn't start at 0 exactly adjusts forward/back by the amount its duration adjusted
                start_adjustment = total_adjustment - dur_adjustment
                if round(note.start, 1) > 0.0:
                    note.start += start_adjustment
                    # Note can't adjust to < 0.0 or > 1.0
                    if round(note.start, 1) == pytest.approx(0.0):
                        note.start = 0.0
                    elif round(note.start, 1) == pytest.approx(1.0):
                        note.start = 1.0 - note.duration

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
            beat_start_times = self.beat_start_times_secs + [self.measure_dur_secs]
            for note in note_sequence:
                i = bisect_left(beat_start_times, note.start)
                # Note maps to 0th beat
                if i == 0:
                    note.start = 0.0
                    continue
                # Note starts after last beat, so maps to last beat
                elif i == len(beat_start_times):
                    note.start = self.beat_start_times_secs[-1]
                    continue
                # Else note.start is between two beats in the range 1..len(beat_start_times) - 1
                # The note is either closest to beat_start_times[i - 1] or beat_start_times[i]
                prev_start = beat_start_times[i - 1]
                next_start = beat_start_times[i]
                prev_gap = note.start - prev_start
                next_gap = next_start - note.start
                if prev_gap <= next_gap:
                    note.start = prev_start
                else:
                    note.start = next_start

    def __str__(self):
        return (f'beats_per_measure: {self.beats_per_measure} beat_dur: {self.beat_note_dur} '
                f'quantizing: {self.quantizing}')

    # noinspection PyTypeChecker
    def __repr__(self):
        dur = self.beat_note_dur.value
        return f'{self.beats_per_measure} / {int(1 / dur)}'

    def __eq__(self, other: 'Meter') -> bool:
        return self.beats_per_measure == other.beats_per_measure and \
               self.beat_note_dur == other.beat_note_dur and \
               self.quantizing == other.quantizing
