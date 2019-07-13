# Copyright 2018 Mark S. Weiss

from itertools import chain
from typing import Any, List, Optional, Tuple

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_types,
                                   validate_sequence_of_type, validate_type, validate_types)


class NoteSequenceSequence(object):
    def __init__(self, note_seq_seq: List[NoteSequence]):
        validate_type('note_seq_seq', note_seq_seq, List)
        validate_sequence_of_type('note_seq_seq', note_seq_seq, NoteSequence)
        self.note_seq_seq = note_seq_seq

    # Measure list management
    def append(self, seq: NoteSequence) -> 'NoteSequenceSequence':
        validate_type('seq', seq, NoteSequence)
        self.note_seq_seq.append(seq)
        return self

    def __add__(self, to_add: NoteSequence) -> 'NoteSequenceSequence':
        return self.append(to_add)

    def __lshift__(self, to_add: NoteSequence) -> 'NoteSequenceSequence':
        return self.append(to_add)

    def insert(self, index: int, to_add: NoteSequence) -> 'NoteSequenceSequence':
        validate_types(('index', index, int), ('to_add', to_add, NoteSequence))
        self.note_seq_seq.insert(index, to_add)
        return self

    def remove(self, to_remove: Tuple[int, int]) -> 'NoteSequenceSequence':
        validate_type('to_remove', to_remove, Tuple)
        validate_sequence_of_type('to_remove', to_remove, int)
        del self.note_seq_seq[to_remove[0]:to_remove[1]]
        return self
    # /Measure list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.note_seq_seq)

    def __getitem__(self, index: int) -> NoteSequence:
        validate_type('index', index, int)
        if abs(index) >= len(self.note_seq_seq):
            raise ValueError(f'`index` out of range index: {index} len(note_seq_seq): {len(self.note_seq_seq)}')
        return self.note_seq_seq[index]

    def __iter__(self) -> 'NoteSequenceSequence':
        self.index = 0
        return self

    def __next__(self) -> NoteSequence:
        if self.index == len(self.note_seq_seq):
            raise StopIteration
        note_seq = self.note_seq_seq[self.index]
        self.index += 1
        return note_seq

    def __eq__(self, other: 'NoteSequenceSequence') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([note_seq == other.note_seq_seq[i] for i, note_seq in enumerate(self.note_seq_seq)])

    @staticmethod
    def copy(other: 'NoteSequenceSequence'):
        return NoteSequenceSequence([NoteSequence.copy(note_seq) for note_seq in other.note_seq_seq])
    # /Iter / slice support


class Section(NoteSequenceSequence):
    """A Section is a container of Measures that supports adding, removing and modifying Measures.
       Sections support all of the same Note attributes as Measures as setters. If these are set
       they will be applied to all Measures in the Track, which will apply them to all Notes in the Measure.
       Getters also behave like Measures, retrieving all values for an attribute for all Notes in all Measures
       flattened into a list.
    """
    def __init__(self,
                 measure_list: List[Measure],
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 name: str = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_types(('measure_list', measure_list, List),
                                ('performance_attrs', performance_attrs, PerformanceAttrs),
                                ('meter', meter, Meter), ('swing', swing, Swing),
                                ('name', name, str))
        validate_optional_sequence_of_type('measure_list', measure_list, Measure)
        super(Section, self).__init__(measure_list)

        self.measure_list = measure_list or []
        self.name = name
        self.performance_attrs = performance_attrs
        self.meter = meter
        if meter:
            for measure in self.measure_list:
                measure.meter = meter
        self.swing = swing
        if swing:
            for measure in self.measure_list:
                measure.swing = swing
        self.index = 0

        if self.performance_attrs:
            for measure in self.measure_list:
                measure.performance_attrs = self.performance_attrs

    # Quantizing for all Measures in the Section
    @property
    def meter(self):
        return self.meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self.meter = meter
        for measure in self.measure_list:
            measure.meter = meter

    def quantizing_on(self):
        for measure in self.measure_list:
            measure.quantizing_on()

    def quantizing_off(self):
        for measure in self.measure_list:
            measure.quantizing_off()

    def quantize(self):
        for measure in self.measure_list:
            measure.quantize()

    def quantize_to_beat(self):
        for measure in self.measure_list:
            measure.quantize_to_beat()
    # /Quantizing for all Measures in the Section

    # Swing for all Measures in the Section
    @property
    def swing(self):
        return self.swing

    @swing.setter
    def swing(self, swing: Swing):
        validate_type('swing', swing, Swing)
        self.swing = swing
        for measure in self.measure_list:
            measure.swing = swing

    def swing_on(self):
        for measure in self.measure_list:
            measure.swing_on()

    def swing_off(self):
        for measure in self.measure_list:
            measure.swing_off()

    def apply_swing(self):
        for measure in self.measure_list:
            measure.apply_swing()

    def apply_phrasing(self):
        for measure in self.measure_list:
            measure.apply_phrasing()
    # /Swing for all Measures in the Section

    # Getters and setters for all core note properties, get from all notes, apply to all notes
    @property
    def performance_attrs(self):
        return self.performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.performance_attrs = performance_attrs
        for measure in self.measure_list:
            measure.performance_attrs = performance_attrs

    def get_attr(self, name: str) -> List[Any]:
        return list(chain.from_iterable([measure.get_attr(name) for measure in self.measure_list]))

    def set_attr(self, name: str, val: Any):
        for measure in self.measure_list:
            measure.set_attr(name, val)
    # Getters and setters for all core note properties, get from all notes, apply to all notes

    @staticmethod
    def copy(source: 'Section') -> 'Section':
        measure_list = None
        if source.measure_list:
            measure_list = [Measure.copy(measure) for measure in source.measure_list]

        new_section = Section(measure_list=measure_list, performance_attrs=source.performance_attrs)
        return new_section
