# Copyright 2018 Mark S. Weiss

# TODO FEATURE augment, diminish, to_major and to_minor
#  See implementation in mingus https://bspaans.github.io/python-mingus/doc/wiki/tutorialBarModule.html
# TODO FEATURE ChordSequence, i.e. Progressions

from copy import copy
from typing import Any, List, Union

import pytest

from aleatoric.meter import Meter, NoteDur
from aleatoric.note import Note, PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.swing import Swing
from aleatoric.utils import validate_optional_sequence_of_type, validate_optional_types, validate_type, validate_types


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

    def __init__(self, to_add: Union[List[Note], NoteSequence],
                 meter: Meter = None,
                 swing: Swing = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_optional_types(('meter', meter, Meter), ('swing', swing, Swing),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        # Don't validate to_add because it's validated in NoteSequence.__init__()
        super(Measure, self).__init__(to_add=to_add)

        # Sort notes by start time to manage adding on beat
        # NOTE: This modifies the note_sequence in place
        self.note_list.sort(key=lambda x: x.start)
        self.meter = meter or copy(Measure.DEFAULT_METER)
        self.swing = swing
        self.measure_performance_attrs = performance_attrs
        # Support adding notes based on Meter
        self.beat = 0
        # Support adding notes offset from end of previous note
        self.next_note_start = 0.0
        self.max_duration = self.meter.beats_per_measure * self.meter.beat_dur

    # Beat state management
    def reset_current_beat(self):
        self.beat = 0

    def increment_beat(self):
        self.beat = min(self.beat + 1, self.meter.beats_per_measure)

    def decrement_beat(self):
        self.beat = max(0, self.beat - 1)
    # /Beat state management

    # Adding notes in sequence on the beat
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
        for i, beat_start_time in enumerate(self.meter.beat_start_times):
            # There might be fewer notes than beats per measure, because `to_add` is a sequence
            if i == len(note_list):
                break
            note_list[i].start = beat_start_time

        self.note_list = note_list
        # Maintain the invariant that notes are sorted ascending by start
        self.note_list.sort(key=lambda x: x.start)
        return self
    # /Adding notes in sequence on the beat

    # Adding notes in sequence from the current start time, one note immediately after another
    def add_note_on_start(self, note: Note, increment_start=False) -> 'Measure':
        """Modifies the note_sequence in place by setting its start_time to the value of measure.start.
           If increment_start == True then measure.start is also incremented, after the insertion. So this method
           is a convenience method for inserting multiple notes in sequence.
           Validates that all the durations fit in the total duration of the measure.
        """
        validate_types(('note', note, Note), ('increment_start', increment_start, bool))
        if self.next_note_start + note.dur > self.max_duration:
            raise ValueError((f'measure.next_note_start {self.next_note_start} + note.duration {note.dur} > '
                              f'measure.max_duration {self.max_duration}'))
        note.start = self.next_note_start
        self.note_list.append(note)
        self.note_list.sort(key=lambda x: x.start)
        if increment_start:
            self.next_note_start += note.dur

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
        if self.next_note_start + sum_of_durations > self.max_duration:
            raise ValueError((f'measure.next_note_start {self.next_note_start} + '
                              f'sum of note.durations {sum_of_durations} > '
                              f'measure.max_duration {self.max_duration}'))

        for note in note_list:
            note.start = self.next_note_start
            self.next_note_start += note.dur

        self.note_list = note_list
        # Maintain the invariant that notes are sorted ascending by start
        self.note_list.sort(key=lambda x: x.start)
        return self
    # Adding notes in sequence from the current start time, one note immediately after another

    # Quantize notes
    def quantizing_on(self):
        self.meter.quantizing_on()

    def quantizing_off(self):
        self.meter.quantizing_off()

    def is_quantizing(self):
        return self.meter.is_quantizing()

    def quantize(self):
        self.meter.quantize(self)

    def quantize_to_beat(self):
        self.meter.quantize_to_beat(self)
    # /Quantize notes

    # Apply Swing and Phrasing to notes
    def swing_on(self):
        if self.swing:
            self.swing.swing_on()
        else:
            raise MeasureSwingNotEnabledException('Measure.swing_on() called but swing is None in Measure')

    def swing_off(self):
        if self.swing:
            self.swing.swing_off()
        else:
            raise MeasureSwingNotEnabledException('Measure.swing_off() called but swing is None in Measure')

    def is_swing_on(self):
        if self.swing:
            return self.swing.is_swing_on()
        else:
            raise MeasureSwingNotEnabledException('Measure.is_swing_on() called but swing is None in Measure')

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
        if self.swing:
            if len(self.note_list) > 1:
                self.note_list[0].start += \
                    self.swing.calculate_swing_adj(self.note_list[0], Swing.SwingDirection.Forward)
                self.note_list[-1].start += \
                    self.swing.calculate_swing_adj(self.note_list[-1], Swing.SwingDirection.Reverse)
        else:
            raise MeasureSwingNotEnabledException('Measure.apply_phrasing() called but swing is None in Measure')
    # /Apply Swing and Phrasing to notes

    # Getters and setters for all core note properties, get from all notes, apply to all notes
    # Getters retrieve the value for a note property from each note and return a list of values
    # Setters apply a value for a note property to each note in the note_list
    # Getters and setters for all core note properties, get from all notes, apply to all notes
    @property
    def pa(self):
        return self.measure_performance_attrs

    @pa.setter
    def pa(self, performance_attrs: PerformanceAttrs):
        self.measure_performance_attrs = performance_attrs
        for note in self.note_list:
            note.performance_attrs = performance_attrs

    @property
    def performance_attrs(self):
        return self.section_performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.measure_performance_attrs = performance_attrs
        for note in self.note_list:
            note.performance_attrs = performance_attrs

    def get_instrument(self) -> List[int]:
        return [note.instrument for note in self.note_list]

    def set_instrument(self, instrument: int):
        for note in self.note_list:
            note.instrument = instrument

    instrument = property(get_instrument, set_instrument)
    i = property(get_instrument, set_instrument)

    def get_start(self) -> Union[List[float], List[int]]:
        return [note.start for note in self.note_list]

    def set_start(self, start: Union[float, int]):
        for note in self.note_list:
            note.start = start

    start = property(get_start, set_start)
    s = property(get_start, set_start)

    def get_dur(self) -> Union[List[float], List[int]]:
        return [note.dur for note in self.note_list]

    def set_dur(self, dur: Union[float, int]):
        for note in self.note_list:
            note.dur = dur

    dur = property(get_dur, set_dur)
    d = property(get_dur, set_dur)

    def get_amp(self) -> Union[List[float], List[int]]:
        return [note.amp for note in self.note_list]

    def set_amp(self, amp: Union[float, int]):
        for note in self.note_list:
            note.amp = amp

    amp = property(get_amp, set_amp)
    a = property(get_amp, set_amp)

    def get_pitch(self) -> Union[List[float], List[int]]:
        return [note.pitch for note in self.note_list]

    def set_pitch(self, pitch: Union[float, int]):
        for note in self.note_list:
            note.pitch = pitch

    pitch = property(get_pitch, set_pitch)
    p = property(get_pitch, set_pitch)

    def transpose(self, interval: int):
        for note in self.note_list:
            note.transpose(interval)
    # Getters and setters for all core note properties, get from all notes, apply to all notes

    # Dynamic setter for any other attributes not common to all Notes, e.g. `channel` in MidiNote
    def get_notes_attr(self, name: str) -> List[Any]:
        """Return list of all values for attribute `name` from all notes in the measure, in start time order"""
        validate_type('name', name, str)
        return [getattr(note, name) for note in self.note_list]

    def set_notes_attr(self, name: str, val: Any):
        """Apply to all notes in note_list"""
        validate_type('name', name, str)
        for note in self.note_list:
            setattr(note, name, val)
    # /Dynamic setter for any other attributes not common to all Notes, e.g. `channel` in MidiNote

    # NoteSequence note_list management
    # Wrap all parent methods to maintain invariant that note_list is sorted by note.start_time ascending
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
    # /NoteSequence note_list management

    # Iterator support
    def __eq__(self, other: 'Measure') -> bool:
        if len(self.note_list) != len(other.note_list):
            return False
        for i, note in enumerate(self.note_list):
            if note != other.note_list[i]:
                return False
        return self.meter == other.meter and \
            self.swing == other.swing and \
            self.beat == other.beat and \
            self.next_note_start == pytest.approx(other.next_note_start) and \
            self.max_duration == pytest.approx(other.max_duration)
    # /Iterator support

    # noinspection PyUnresolvedReferences
    @staticmethod
    def copy(source_measure: 'Measure') -> 'Measure':
        # Call the dup() for the subclass of this note type
        new_note_list = [(note.copy(note))
                         for note in source_measure.note_list]
        new_measure = Measure(to_add=new_note_list,
                              meter=source_measure.meter, swing=source_measure.swing,
                              performance_attrs=source_measure.measure_performance_attrs)
        new_measure.beat = source_measure.beat
        return new_measure
