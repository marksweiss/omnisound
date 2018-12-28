# Copyright 2018 Mark S. Weiss

# TODO FEATURE augment, diminish, to_major and to_minor
#  See implementation in mingus https://bspaans.github.io/python-mingus/doc/wiki/tutorialBarModule.html
# TODO FEATURE ChordSequence, i.e. Progressions

from copy import copy
from typing import Any, List, Union

from aleatoric.meter import Meter, NoteDur
from aleatoric.note import Note, PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.swing import Swing
from aleatoric.utils import validate_optional_types, validate_type, validate_types


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
        # Support adding notes offset from end of previous note
        self.start = 0.0
        self.max_duration = self.meter.beats_per_measure * self.meter.beat_dur

    def reset_current_beat(self):
        self.beat = 0

    def increment_beat(self):
        self.beat = min(self.beat + 1, self.meter.beats_per_measure)

    def decrement_beat(self):
        self.beat = max(0, self.beat - 1)

    def add_note_on_beat(self, note: Note, increment_beat=False) -> 'Measure':
        """Modifies the note_sequence in place by setting its start_time to the value of measure.beat.
        If increment_beat == True the measure_beat is also incremented, after the insertion. So this method
        is a convenience method for inserting multiple notes in sequence on the beat.
        """
        validate_types(('note', note, Note), ('increment_beat', increment_beat, bool))

        note.start = self.meter.beat_start_times[self.beat]
        self.note_list.append(note)
        self.note_list.sort(key=lambda x: x.start)
        # Increment beat position if flag set and beat is not on last beat of the measure already
        if increment_beat:
            self.increment_beat()

        return self

    def add_notes_on_beat(self, to_add: Union[Note, NoteSequence, List[Note]]) -> 'Measure':
        """Uses note as a template and makes copies of it to fill the measure. Each new note's start time is set
           to that beat start time.

           NOTE: This *replaces* all notes in the Measure with this sequence of notes on the beat
        """
        # If `to_add` is a Note, the note_list is `to_add` copied beats_per_measure times
        note_list = []
        try:
            validate_type('to_add', to_add, Note)
            note_list = [to_add.__class__.copy(to_add) for _ in range(self.meter.beats_per_measure)]
        except ValueError:
            pass

        # Otherwise the note_list is the NoteSequence or List[Note] passed in. Retrieve it and validate
        # that it doesn't have more notes than there are beats per measure.
        if not note_list:
            # If `to_add` is a NoteSequence or note list, ensure that the number of notes in the sequence
            # is <= the number of beats in the measure, then assign one note to each beat
            note_list = self._get_note_list_from_sequence('to_add', to_add)
            if not note_list:
                raise ValueError((f'Arg `to_add` must be a Note, NoteSequence or List[Note], '
                                  f'arg: {to_add} type: {type(to_add)}'))
            if len(note_list) > self.meter.beats_per_measure:
                raise ValueError(f'Sequence `to_add` must have a number of notes <= to the number of beats per measure')

        # Now iterate the beats per measure and assign each note in note_list to the next start time on the beat
        for i, start in enumerate(self.meter.beat_start_times):
            # There might be fewer notes than beats per measure, because `to_add` is a sequence
            if i == len(note_list):
                break
            note_list[i].start = start

        self.note_list = note_list
        # Maintain the invariant that notes are sorted ascending by start
        self.note_list.sort(key=lambda x: x.start)
        return self

    def add_note_on_start(self, note: Note, increment_start=False) -> 'Measure':
        """Modifies the note_sequence in place by setting its start_time to the value of measure.start.
           If increment_start == True then measure.start is also incremented, after the insertion. So this method
           is a convenience method for inserting multiple notes in sequence.
           Validates that all the durations fit in the total duration of the measure.
        """
        validate_types(('note', note, Note), ('increment_start', increment_start, bool))
        if self.start + note.dur > self.max_duration:
            raise ValueError((f'measure.start {self.start} + note.duration {note.dur} > '
                              f'measure.max_duration {self.max_duration}'))
        note.start = self.start
        self.note_list.append(note)
        self.note_list.sort(key=lambda x: x.start)
        if increment_start:
            self.start += note.dur

        return self

    def add_notes_on_start(self, to_add: Union[NoteSequence, List[Note]]) -> 'Measure':
        """Uses note as a template and makes copies of it to fill the measure. Each new note's start time is set
           to that of the previous notes start + duration.
           Validates that all the durations fit in the total duration of the measure.

           NOTE: This *replaces* all notes in the Measure with this sequence of notes on the beat
        """
        note_list = self._get_note_list_from_sequence('to_add', to_add)
        if not note_list:
            raise ValueError((f'Arg `to_add` must be a NoteSequence or List[Note], '
                              f'arg: {to_add} type: {type(to_add)}'))

        sum_of_durations = sum([note.dur for note in note_list])
        if self.start + sum_of_durations > self.max_duration:
            raise ValueError((f'measure.start {self.start} + sum of note.durations {sum_of_durations} > '
                              f'measure.max_duration {self.max_duration}'))

        for note in note_list:
            note.start = self.start
            self.start += note.dur

        self.note_list = note_list
        # Maintain the invariant that notes are sorted ascending by start
        self.note_list.sort(key=lambda x: x.start)
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

    def set_notes_attr(self, name: str, val: Any):
        """Apply to all notes in note_list"""
        validate_type('name', name, str)
        for note in self.note_list:
            setattr(note, name, val)

    def transpose(self, interval: int):
        for note in self.note_list:
            note.transpose(interval)

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

    def insert(self, index: int, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'Measure':
        super(Measure, self).insert(index, to_add)
        self.note_list.sort(key=lambda x: x.start)
        return self

    def remove(self, to_remove: Union[Note, 'NoteSequence', List[Note]]) -> 'Measure':
        super(Measure, self).remove(to_remove)
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
