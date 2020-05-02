# Copyright 2018 Mark S. Weiss

from itertools import chain
from typing import Any, List, Optional

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.note_sequence_sequence import NoteSequenceSequence
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_types,
                                   validate_type)


class Section(NoteSequenceSequence):
    """A Section is a container of Measures that supports adding, removing and modifying Measures.
       Sections support all of the same Note attributes as Measures as setters. If these are set
       they will be applied to all Measures in the Section, which will apply them to all Notes in the Measure.
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

        measure_list = measure_list or []
        super(Section, self).__init__(measure_list)
        # TODO REFACTOR NAME TO 'measures'
        self.measure_list = self.note_seq_seq

        self.name = name
        self._performance_attrs = performance_attrs
        self._meter = meter
        if meter:
            for measure in self.measure_list:
                measure.meter = meter
        self._swing = swing
        if swing:
            for measure in self.measure_list:
                measure.swing = swing
        self.index = 0

        if self._performance_attrs:
            for measure in self.measure_list:
                measure.performance_attrs = self._performance_attrs

    # Properties
    # Quantizing for all Measures in the Section
    @property
    def meter(self):
        return self._meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self._meter = meter
        for measure in self.measure_list:
            measure.meter = meter

    @property
    def tempo(self) -> float:
        return self.meter.tempo_qpm

    @tempo.setter
    def tempo(self, tempo: int):
        self.meter.tempo = tempo
        for measure in self.measure_list:
            measure.tempo = tempo
    # /Properties

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
        return self._swing

    @swing.setter
    def swing(self, swing: Swing):
        validate_type('swing', swing, Swing)
        self._swing = swing
        for measure in self.measure_list:
            measure.swing = swing

    def set_swing_on(self) -> 'Section':
        for measure in self.measure_list:
            measure.set_swing_on()
        return self

    def set_swing_off(self) -> 'Section':
        for measure in self.measure_list:
            measure.set_swing_off()
        return self

    def apply_swing(self) -> 'Section':
        for measure in self.measure_list:
            measure.apply_swing()
        return self

    def apply_phrasing(self) -> 'Section':
        for measure in self.measure_list:
            measure.apply_phrasing()
        return self
    # /Swing for all Measures in the Section

    # Getters and setters for all core note properties, get from all notes, apply to all notes
    @property
    def performance_attrs(self):
        return self._performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self._performance_attrs = performance_attrs
        for measure in self.measure_list:
            measure.performance_attrs = performance_attrs

    def get_attr(self, name: str) -> List[Any]:
        return list(chain.from_iterable([measure.get_attr(name) for measure in self.measure_list]))

    def set_attr(self, name: str, val: Any):
        for measure in self.measure_list:
            measure.set_attr(name, val)
    # Getters and setters for all core note properties, get from all notes, apply to all notes

    # noinspection PyTypeChecker
    @staticmethod
    def copy(source: 'Section') -> 'Section':
        measure_list = None
        if source.measure_list:
            measure_list = [Measure.copy(measure) for measure in source.measure_list]

        new_section = Section(measure_list=measure_list, performance_attrs=source._performance_attrs)
        return new_section
