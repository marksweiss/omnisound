# Copyright 2018 Mark S. Weiss

from itertools import chain

from typing import Any, List, Optional, Union

from aleatoric.measure import Measure
from aleatoric.note import PerformanceAttrs
from aleatoric.utils import (validate_optional_type, validate_optional_sequence_of_type,
                             validate_sequence_of_type, validate_type)


class Section(object):
    DEFAULT_INSTRUMENT = 0

    """A Section is a container of Measures that supports adding, removing and modifying Measures.
       Sections support all of the same Note attributes as Measures as setters. If these are set
       they will be applied to all Measures in the Track, which will apply them to all Notes in the Measure.
       Getters also behave like Measures, retrieving all values for an attribute for all Notes in all Measures
       flattened into a list.
    """
    def __init__(self, measure_list: Optional[List[Measure]] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_type('performance_attrs', performance_attrs, PerformanceAttrs)
        validate_optional_sequence_of_type('measure', measure_list, Measure)

        self.measure_list = measure_list or []
        self.performance_attrs = performance_attrs
        self.index = 0

        # TODO TEST
        if self.performance_attrs:
            for measure in self.measure_list:
                measure.performance_attrs = self.performance_attrs

    # Wrappers for Measure methods, call on all measures
    def quantize(self):
        for measure in self.measure_list:
            measure.quantize()

    def quantize_to_beat(self):
        for measure in self.measure_list:
            measure.quantize_to_beat()

    def apply_swing(self):
        for measure in self.measure_list:
            measure.apply_swing()

    def apply_phrasing(self):
        for measure in self.measure_list:
            measure.apply_phrasing()
    # /Wrappers for Measure methods, call on all measures

    # Getters and setters for all core note properties, get from all notes, apply to all notes
    @property
    def pa(self):
        return self.performance_attrs

    # TODO TEST
    @pa.setter
    def pa(self, performance_attrs: PerformanceAttrs):
        self.performance_attrs = performance_attrs
        for measure in self.measure_list:
            measure.performance_attrs = self.performance_attrs

    @property
    def performance_attrs(self):
        return self.performance_attrs

    # TODO TEST
    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.performance_attrs = performance_attrs
        for measure in self.measure_list:
            measure.performance_attrs = self.performance_attrs

    def get_instrument(self) -> List[int]:
        return list(chain.from_iterable([measure.instrument for measure in self.measure_list]))

    def set_instrument(self, instrument: int):
        validate_type('instrument', instrument, int)
        for measure in self.measure_list:
            measure.instrument = instrument

    instrument = property(get_instrument, set_instrument)
    i = property(get_instrument, set_instrument)

    def get_start(self) -> Union[List[float], List[int]]:
        return list(chain.from_iterable([measure.start for measure in self.measure_list]))

    def set_start(self, start: Union[float, int]):
        for measure in self.measure_list:
            measure.start = start

    start = property(get_start, set_start)
    s = property(get_start, set_start)

    def get_dur(self) -> Union[List[float], List[int]]:
        return list(chain.from_iterable([measure.dur for measure in self.measure_list]))

    def set_dur(self, dur: Union[float, int]):
        for measure in self.measure_list:
            measure.dur = dur

    dur = property(get_dur, set_dur)
    d = property(get_dur, set_dur)

    def get_amp(self) -> Union[List[float], List[int]]:
        return list(chain.from_iterable([measure.amp for measure in self.measure_list]))

    def set_amp(self, amp: Union[float, int]):
        for measure in self.measure_list:
            measure.amp = amp

    amp = property(get_amp, set_amp)
    a = property(get_amp, set_amp)

    def get_pitch(self) -> Union[List[float], List[int]]:
        return list(chain.from_iterable([measure.pitch for measure in self.measure_list]))

    def set_pitch(self, pitch: Union[float, int]):
        for measure in self.measure_list:
            measure.pitch = pitch

    pitch = property(get_pitch, set_pitch)
    p = property(get_pitch, set_pitch)

    def transpose(self, interval: int):
        for measure in self.measure_list:
            measure.transpose(interval)

    def set_notes_attr(self, name: str, val: Any):
        for measure in self.measure_list:
            measure.set_notes_attr(name, val)
    # Getters and setters for all core note properties, get from all notes, apply to all notes

    # Measure list management
    def append(self, measure: Measure) -> 'Section':
        validate_type('measure', measure, Measure)
        self.measure_list.append(measure)
        return self

    def extend(self, to_add: Union[Measure, List[Measure]]) -> 'Section':
        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.append(to_add)
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Measure)
        self.measure_list.extend(to_add)

        return self

    def __add__(self, to_add: Union[Measure, List[Measure]]) -> 'Section':
        return self.extend(to_add)

    def __lshift__(self, to_add: Union[Measure, List[Measure]]) -> 'Section':
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

    def remove(self, to_remove: Union[Measure, List[Measure]]) -> 'Section':
        try:
            validate_type('to_remove', to_remove, Measure)
            self.measure_list.remove(to_remove)
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_remove', to_remove, Measure)
        for measure in to_remove:
            self.measure_list.remove(measure)

        return self
    # /Measure list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.measure_list)

    def __iter__(self) -> 'Section':
        self.index = 0
        return self

    def __next__(self) -> Measure:
        if self.index == len(self.measure_list):
            raise StopIteration
        measure = self.measure_list[self.index]
        self.index += 1
        return Measure.copy(measure)

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

        new_section = Section(measure_list=measure_list, performance_attrs=source_section.performance_attrs)
        return new_section
