# Copyright 2018 Mark S. Weiss

from typing import Sequence, List, Optional, Tuple, Union

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_types,
                                   validate_sequence_of_type, validate_type)


class Section(object):
    """A Section is a container of Measures that supports adding, removing and modifying Measures.
       Sections support all of the same Note attributes as Measures as setters. If these are set
       they will be applied to all Measures in the Track, which will apply them to all Notes in the Measure.
       Getters also behave like Measures, retrieving all values for an attribute for all Notes in all Measures
       flattened into a list.

       NOTE: This can't derive from NoteSequence because it is a collection of potentially heterogeneous
       NoteSequences, each with different Notes with different attributes, etc.
    """

    DEFAULT_NAME = 'section'

    def __init__(self, measures: Optional[Sequence[Measure]] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 name: Optional[str] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_types(('performance_attrs', performance_attrs, PerformanceAttrs),
                                ('meter', meter, Meter), ('swing', swing, Swing),
                                ('name', name, str))

        validate_optional_sequence_of_type('measures', measures, Measure)
        self.measure_list = measures or []
        self.name = name or Section.DEFAULT_NAME
        self.section_performance_attrs = performance_attrs

        self.section_meter = meter
        if meter:
            for measure in self.measure_list:
                measure.meter = meter
        self.section_swing = swing
        if swing:
            for measure in self.measure_list:
                measure.swing = swing
        self.index = 0

        if self.section_performance_attrs:
            for measure in self.measure_list:
                measure.performance_attrs = self.section_performance_attrs

    # Quantizing for all Measures in the Section
    @property
    def meter(self):
        return self.section_meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self.section_meter = meter
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
        return self.section_swing

    @swing.setter
    def swing(self, swing: Swing):
        validate_type('swing', swing, Swing)
        self.section_swing = swing
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

    @property
    def performance_attrs(self):
        return self.section_performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.section_performance_attrs = performance_attrs
        for measure in self.measure_list:
            measure.performance_attrs = performance_attrs

    # Measure list management
    def append(self, measure: Measure) -> 'Section':
        validate_type('measure', measure, Measure)
        self.measure_list.append(measure)
        return self

    def extend(self, to_add: Union[Measure, Sequence[Measure]]) -> 'Section':
        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.append(to_add)
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Measure)
        self.measure_list.extend(to_add)

        return self

    def __add__(self, to_add: Union[Measure, Sequence[Measure]]) -> 'Section':
        return self.extend(to_add)

    def __lshift__(self, to_add: Union[Measure, Sequence[Measure]]) -> 'Section':
        return self.extend(to_add)

    def insert(self, index: int, to_add: Union[Measure, List[Measure]]) -> 'Section':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.insert(index, to_add)
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Measure)
        for measure in to_add:
            self.measure_list.insert(index, measure)
            index += 1

        return self

    def remove(self, to_remove: Tuple[int, int]) -> 'Section':
        validate_type('to_remove', to_remove, int)
        start_range = to_remove[0]
        end_range = to_remove[1]
        if start_range < 0 or end_range < 0 or end_range >= len(self.measure_list):
            raise ValueError((f'range for remove() is out of range, start_range: {start_range} '
                              f'end_range: {end_range} len: {len(self.measure_list)}'))
        del self.measure_list[to_remove[0]:to_remove[1]]
        return self
    # /Measure list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.measure_list)

    def __getitem__(self, index: int) -> Measure:
        validate_type('index', index, int)
        if abs(index) >= len(self.measure_list):
            raise ValueError(f'`index` out of range index: {index} len(measure_list): {len(self.measure_list)}')
        return self.measure_list[index]

    def __iter__(self) -> 'Section':
        self.index = 0
        return self

    def __next__(self) -> Measure:
        if self.index == len(self.measure_list):
            raise StopIteration
        measure = self.measure_list[self.index]
        self.index += 1
        return measure

    def __eq__(self, other: 'Section') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.measure_list[i] == other.measure_list[i] for i in range(len(self.measure_list))])
    # /Iter / slice support

    @staticmethod
    def copy(source_section: 'Section') -> 'Section':
        measure_list = None
        if source_section.measure_list:
            measure_list = [Measure.copy(measure) for measure in source_section.measure_list]

        new_section = Section(measures=measure_list, meter=source_section.meter, swing=source_section.swing,
                              name=source_section.name, performance_attrs=source_section.performance_attrs)
        return new_section
