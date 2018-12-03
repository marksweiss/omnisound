# Copyright 2018 Mark S. Weiss

from bisect import bisect_left
from enum import Enum

from aleatoric.note import Note, NoteSequence
from aleatoric.utils import sign, validate_optional_type, validate_optional_types, validate_type, validate_types


# TODO transpose, augment, diminish, to_major and to_minor and placing notes on beat
#  See implementation in mingus https://bspaans.github.io/python-mingus/doc/wiki/tutorialBarModule.html
# TODO consistent container semantics from NoteSequence to Measure to Track to Song
# TODO consistent application of all Note transformation operations up the hierarchy from Note to NoteSequence
#  to Measure to Track to Song
# TODO Relationship of Players and Ensembles to the Song hierarchy


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
        self.swinging = swing_on
        if swing_factor is None:
            swing_factor = Swing.DEFAULT_SWING_FACTOR
        self.swing_factor = swing_factor
        self.swing_direction = swing_direction or Swing.DEFAULT_SWING_DIRECTION

    def is_swing_on(self):
        return self.swinging

    def swing_on(self):
        self.swinging = True

    def swing_off(self):
        self.swinging = False

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
            for note in note_sequence.note_list:
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


class Meter(object):
    """Class to represent and manage Meter in a musical Measure/Bar. Offers facilities for representing and
       calculating meter using traditional units or floating point values. Can also apply quantizing to a
       NoteSequence to either fit the notes with the same ration of separation between them but scaled to the
       duration of the Measure, or to fit notes to the closest beat in the Measure. str displays information about
       the configuration of the object, but repr displays the meter in traditional notation.
    """
    def __init__(self, beats_per_measure: int = None, beat_dur: NoteDur = None, quantizing: bool = None):
        validate_optional_types(('beats_per_measure', beats_per_measure, int), ('beat_dur', beat_dur, NoteDur),
                                ('quantizing', quantizing, bool))

        self.beats_per_measure = beats_per_measure
        self.beat_dur = beat_dur.value
        self.beats_per_note = self.beat_dur / self.beats_per_measure
        # Use arg value of beats_per_measure because we want to use range(int)
        self.beat_start_times = [0.0 + (self.beat_dur * i) for i in range(self.beats_per_measure)]
        self.measure_dur = self.beats_per_measure * self.beat_dur
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
            beat_start_times = self.beat_start_times + [self.beat_dur]
            for note in note_sequence.note_list:
                i = bisect_left(beat_start_times, note.start)
                # Note maps to 0th beat
                if i == 0:
                    note.start = 0.0
                # Note starts after last beat, so maps to last beat
                elif i == len(beat_start_times):
                    note.start = self.beat_start_times[-1]
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


class MeasureSwingNotEnabledException(Exception):
    pass


class MeasureBeatInvalidPositionException(Exception):
    pass


# TODO Scale class with root, notes in scale, transpose()
# TODO Chord class
# TODO ChordSequence
# TODO Solidify the idea that we can manage notes in time sequence offset by measure so there is a song
#  time but each measure just starts again at 0
# This class makes that assumption

# This is compact and looks like what I need: https://github.com/gciruelos/musthe
# Good base for scales, chords and generating the notes from them
# Make this the basis of the Scale system and map to pitch values for each backend
class Measure(object):
    """Represents a musical measure in a musical Score. As such it includes a NoteSequence
       and attributes that affect the performance of all Notes in that NoteSequence.
       Additional attributes are Meter, BPM, Scale and Key.

       Also manages musical notions of time. So maintains a Meter and knows how long a beat is,
       current beat position, and can add notes on beat or at a specified time. Also manages the
       notes in the underlying note_sequence in order sorted by start_time.
    """

    DEFAULT_QUANTIZING = False

    def __init__(self, note_sequence: NoteSequence = None, beats_per_measure: int = None,
                 beat_duration: NoteDur = None, quantizing: bool = DEFAULT_QUANTIZING,
                 swing: Swing = None):
        validate_types(('note_sequence', note_sequence, NoteSequence),
                       ('beats_per_measure', beats_per_measure, int),
                       ('beat_duration', beat_duration, NoteDur))
        validate_optional_types(('swing', swing, Swing), ('quantizing', quantizing, bool))

        self.note_sequence = note_sequence
        # Sort notes by start time to manage adding on beat
        # NOTE: This modifies the note_sequence in place
        self.note_sequence.note_list.sort(key=lambda x: x.start)
        self.meter = Meter(beat_dur=beat_duration, beats_per_measure=beats_per_measure, quantizing=quantizing)
        self.swing = swing
        # Support adding notes based on Meter
        self.beat = 0

    def reset_current_beat(self):
        self.beat = 0

    def increment_beat(self):
        self.beat = min(self.beat + 1, self.meter.beats_per_measure)

    def decrement_beat(self):
        self.beat = max(0, self.beat - 1)

    def add_note(self, note: Note):
        validate_type('note', note, Note)
        self.note_sequence += note
        self.note_sequence.note_list.sort(key=lambda x: x.start)

    def __add__(self, note: Note):
        self.add_note(note)

    def add_note_on_current_beat(self, note: Note, increment_beat=False):
        """Modifies the note_sequence in place by setting its start_time to the value of measure.beat.
        If increment_beat == True the measure_beat is also incremented, after the insertion. So this method
        is a convenience method for inserting multiple notes in sequence on the beat.
        """
        validate_types(('note', note, Note), ('increment_beat', increment_beat, bool))

        note.start = self.meter.beat_start_times[self.beat]
        self.note_sequence += note
        self.note_sequence.note_list.sort(key=lambda x: x.start)
        # Increment beat position if flag set and beat is not on last beat of the measure already
        if increment_beat:
            self.increment_beat()

    def fill_measure_with_note(self, note: Note):
        """Uses note as a template and makes copies of it to fill the measure. Each new note's start time is set
        to that beat start time.
        """
        validate_type('note', note, Note)

        for start in self.meter.beat_start_times:
            new_note = note.__class__.copy(note)
            new_note.start = start
            self.note_sequence += note
        self.note_sequence.note_list.sort(key=lambda x: x.start)

    def quantize(self):
        self.meter.quantize(self.note_sequence)

    def quantize_to_beat(self):
        self.meter.quantize_to_beat(self.note_sequence)

    def apply_swing(self):
        """Moves all notes in Measure according to how self.swing is configured.
        """
        if self.swing:
            self.swing.apply_swing(self.note_sequence)
        else:
            raise MeasureSwingNotEnabledException('Measure.apply_swing() called but swing is None in Measure')

    def apply_phrasing(self):
        """Moves the first note in Measure forward and the last back by self.swing.swing.swing_factor.
           The idea is to slightly accentuate the metric phrasing of each measure. Handles boundary condition
           of having 0 or 1 notes. If there is only 1 note no adjustment is made.
        """
        if len(self.note_sequence) > 1:
            self.swing.calculate_swing_adj(self.note_sequence[0], Swing.SwingDirection.Forward)
            self.swing.calculate_swing_adj(self.note_sequence[-1], Swing.SwingDirection.Reverse)
