# Copyright 2018 Mark S. Weiss

from copy import copy
from typing import List, Union

from aleatoric.meter import Meter, NoteDur
from aleatoric.note import Note, PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.swing import Swing
from aleatoric.utils import validate_optional_types, validate_type, validate_types

# TODO FEATURE augment, diminish, to_major and to_minor
#  See implementation in mingus https://bspaans.github.io/python-mingus/doc/wiki/tutorialBarModule.html
# TODO FEATURE ChordSequence, i.e. Progressions

# TODO transpose
# TODO consistent application of all Note transformation operations up the hierarchy from Note to NoteSequence
#  to Measure to Track to Song
# TODO Solidify the idea that we can manage notes in time sequence offset by measure so there is a song
#  time but each measure just starts again at 0. THIS WILL BE MANAGED BY TRACK


class MeasureSwingNotEnabledException(Exception):
    pass


class MeasureBeatInvalidPositionException(Exception):
    pass


class Measure(NoteSequence):
    """Represents a musical measure in a musical Score. As such it includes a NoteSequence
       and attributes that affect the performance of all Notes in that NoteSequence.
       Additional attributes are Meter, BPM, Scale and Key.

       Also manages musical notions of time. So maintains a Meter and knows how long a beat is,
       current beat position, and can add notes on beat or at a specified time. Also manages the
       notes in the underlying note_sequence in order sorted by start_time.
    """

    DEFAULT_METER = Meter(beats_per_measure=4, beat_dur=NoteDur.QUARTER, quantizing=True)

    def __init__(self, note_list: List[Note], performance_attrs: PerformanceAttrs = None,
                 meter: Meter = None, swing: Swing = None):
        validate_optional_types(('swing', swing, Swing), ('meter', meter, Meter))
        super(Measure, self).__init__(note_list=note_list, performance_attrs=performance_attrs)

        # Sort notes by start time to manage adding on beat
        # NOTE: This modifies the note_sequence in place
        self.note_list.sort(key=lambda x: x.start)
        self.meter = meter or copy(Measure.DEFAULT_METER)
        self.swing = swing
        # Support adding notes based on Meter
        self.beat = 0
        # TODO TEST
        # Support adding notes offset from end of previous note
        self.start = 0.0
        self.max_duration = self.meter.beats_per_measure * self.meter.beat_dur

    def reset_current_beat(self):
        self.beat = 0

    def increment_beat(self):
        self.beat = min(self.beat + 1, self.meter.beats_per_measure)

    def decrement_beat(self):
        self.beat = max(0, self.beat - 1)

    def add_note_on_current_beat(self, note: Note, increment_beat=False) -> 'Measure':
        """Modifies the note_sequence in place by setting its start_time to the value of measure.beat.
        If increment_beat == True the measure_beat is also incremented, after the insertion. So this method
        is a convenience method for inserting multiple notes in sequence on the beat.
        """
        validate_types(('note', note, Note), ('increment_beat', increment_beat, bool))

        note.start = self.meter.beat_start_times[self.beat]
        self.note_list += note
        self.note_list.sort(key=lambda x: x.start)
        # Increment beat position if flag set and beat is not on last beat of the measure already
        if increment_beat:
            self.increment_beat()

        return self

    # TODO Support Note, NoteSequence or List[Note], add each on beat
    #  If it's a Note, repeat it N times
    # TODO TEST
    def fill_measure_with_notes_on_beat(self, note: Note) -> 'Measure':
        """Uses note as a template and makes copies of it to fill the measure. Each new note's start time is set
        to that beat start time.
        """
        validate_type('note', note, Note)

        for start in self.meter.beat_start_times:
            new_note = note.copy(note)
            new_note.start = start
            self.note_list.append(new_note)
        self.note_list.sort(key=lambda x: x.start)

        return self

    # TODO Support Note, NoteSequence or List[Note], add each on beat
    #  If it's a Note, repeat it N times
    # TODO TEST
    def add_notes_after_previous_note(self, note: Note) -> 'Measure':
        """Appends a note into the Measure after the start + duration of the note in the Measure closest
           to the end of the Measure. Checks for new_note.start + new_note.duration running off the end
           of the Measure.
        """
        validate_type('note', note, Note)
        duration = float(note.dur)
        if self.start + duration > self.max_duration:
            raise ValueError(('Adding `note` extends past the end of the Measure '
                              f'max_duration: {self.max_duration} note end: {self.start + duration}'))

        note.start = self.start
        self.append(note)
        self.start += duration

        return self

    def quantize(self):
        self.meter.quantize(self)

    def quantize_to_beat(self):
        self.meter.quantize_to_beat(self)

    def apply_swing(self):
        """Moves all notes in Measure according to how self.swing is configured.
        """
        if self.swing:
            self.swing.apply_swing(self)
        else:
            raise MeasureSwingNotEnabledException('Measure.apply_swing() called but swing is None in Measure')

    def apply_phrasing(self):
        """Moves the first note in Measure forward and the last back by self.swing.swing.swing_factor.
           The idea is to slightly accentuate the metric phrasing of each measure. Handles boundary condition
           of having 0 or 1 notes. If there is only 1 note no adjustment is made.
        """
        if len(self.note_list) > 1:
            self.note_list[0].start += \
                self.swing.calculate_swing_adj(self.note_list[0], Swing.SwingDirection.Forward)
            self.note_list[-1].start += \
                self.swing.calculate_swing_adj(self.note_list[-1], Swing.SwingDirection.Reverse)

    # Wrap all parant methods that mutate note_list, because this
    # class maintains the invariant that note_list is sorted by
    # note.start_time ascending
    # noinspection PyUnresolvedReferences
    def append(self, note: Note) -> 'Measure':
        super(Measure, self).append(note)
        self.note_list.sort(key=lambda x: x.start)
        return self

    # noinspection PyUnresolvedReferences
    def extend(self, to_add: Union[Note, NoteSequence, List[Note]]) -> 'Measure':
        super(Measure, self).extend(to_add)
        self.note_list.sort(key=lambda x: x.start)
        return self

    # noinspection PyUnresolvedReferences
    def __add__(self, to_add: Union[Note, NoteSequence, List[Note]]) -> 'Measure':
        return self.extend(to_add)

    # noinspection PyUnresolvedReferences
    def __lshift__(self, to_add: Union[Note, NoteSequence, List[Note]]) -> 'Measure':
        return self.extend(to_add)

    def insert(self, index: int, note: Note) -> 'Measure':
        super(Measure, self).insert(index, note)
        self.note_list.sort(key=lambda x: x.start)
        return self

    def remove(self, note: Note) -> 'Measure':
        super(Measure, self).remove(note)
        self.note_list.sort(key=lambda x: x.start)
        return self

    # noinspection PyUnresolvedReferences
    @staticmethod
    def copy(source_measure: 'Measure') -> 'Measure':
        # Call the dup() for the subclass of this note type
        new_note_list = [(note.copy(note))
                         for note in source_measure.note_sequence.note_list]
        new_measure = Measure(note_list=new_note_list,
                              performance_attrs=source_measure.note_sequence.performance_attrs,
                              meter=source_measure.meter, swing=source_measure.swing)
        new_measure.beat = source_measure.beat
        return new_measure
