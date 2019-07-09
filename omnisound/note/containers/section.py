# Copyright 2018 Mark S. Weiss

from typing import Sequence, Optional

from omnisound.note.adapters.note import get_num_attributes
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_types, validate_type)


class Section(NoteSequence):
    """A Section is a container of Measures that supports adding, removing and modifying Measures.
       Sections support all of the same Note attributes as Measures as setters. If these are set
       they will be applied to all Measures in the Track, which will apply them to all Notes in the Measure.
       Getters also behave like Measures, retrieving all values for an attribute for all Notes in all Measures
       flattened into a list.

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
        if not len(measures):
            raise ValueError('Must provide non-empty list of Measures to create a Section')

        self.name = name or Section.DEFAULT_NAME
        self.performance_attrs = performance_attrs
        self.meter = meter
        self.swing = swing

        # Call NoteSequence base class init, using the first Measure in MeasureList to be the "primary" sequence
        # in the NoteSequence, and then adding each subsequent Measure as a child sequence. NoteSequence supports
        # managing a "parent" sequence and an arbitrary list of arbitrarily nested child sequences. Notes can be
        # accessed in a flattened manner as one sequence, and each individual child sequence is also its own
        # NoteSequence and can be accessed individually. This supports Section semantics: we add each measure
        # as a child sequence, all siblings on the same level, effectively creating a sequence of measures we can
        # traverse and manage globally from here by applying meter and swing to all of them, but also each measure
        # can be its own note type with its own attributes.
        first_measure = measures[0]
        super(Section, self).__init__(make_note=first_measure.make_note,
                                      num_notes=len(first_measure),
                                      num_attributes=get_num_attributes(first_measure),
                                      attr_name_idx_map=first_measure.attr_name_idx_map,
                                      attr_vals_defaults_map=first_measure.attr_vals_defaults_map,
                                      attr_get_type_cast_map=first_measure.attr_get_type_cast_map)
        # Now add each additional measure as a "sibling" of the first, a child_sequence all on one level
        for measure in measures[1:]:
            self.append_child_sequence(measure)
        # Store first measure in reference to support copy()
        # NOTE: This means calling copy() and then deleting first_measure is a possible bug. Caveat emptor.
        self.first_measure = first_measure

        if meter:
            for measure in self:
                measure.meter = meter
        if swing:
            for measure in self:
                measure.swing = swing
        if self.performance_attrs:
            for measure in self:
                measure.performance_attrs = self.performance_attrs

    # Quantizing for all Measures in the Section
    @property
    def meter(self):
        return self.meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self.meter = meter
        for measure in self:
            measure.meter = meter

    def quantizing_on(self):
        for measure in self:
            measure.quantizing_on()

    def quantizing_off(self):
        for measure in self:
            measure.quantizing_off()

    def quantize(self):
        for measure in self:
            measure.quantize()

    def quantize_to_beat(self):
        for measure in self:
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
        for measure in self:
            measure.swing = swing

    def swing_on(self):
        for measure in self:
            measure.swing_on()

    def swing_off(self):
        for measure in self:
            measure.swing_off()

    def apply_swing(self):
        for measure in self:
            measure.apply_swing()

    def apply_phrasing(self):
        for measure in self:
            measure.apply_phrasing()
    # /Swing for all Measures in the Section

    @property
    def performance_attrs(self):
        return self.performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.performance_attrs = performance_attrs
        for measure in self:
            measure.performance_attrs = performance_attrs

    # Measure list management
    def append(self, measure: Measure) -> 'Section':
        raise NotImplementedError(('Section does not allow the `NoteSequence.append()` operation '
                                   'as this expects an individual Note and Section only allows adding Measures. '
                                   'Measures are NoteSequences and can be added to a Section by calling `extend()`.'))

    def __add__(self, to_add: Measure) -> 'Section':
        if not isinstance(to_add, Measure):
            raise NotImplementedError('Section only allows `NoteSequence.__add__()` for arguments of type Measure')
        return self.extend(to_add)

    def __lshift__(self, to_add: Measure) -> 'Section':
        if not isinstance(to_add, Measure):
            raise NotImplementedError('Section only allows `NoteSequence.__lshift__()` for arguments of type Measure')
        return self.extend(to_add)

    def insert(self, index: int, to_add: Measure) -> 'Section':
        if not isinstance(to_add, Measure):
            raise NotImplementedError('Section only allows `NoteSequence.__lshift__()` for arguments of type Measure')
        return self.insert(index, to_add)

    @staticmethod
    def copy(source: 'Section') -> 'Section':
        measure_list = [source.first_measure]
        measure_list.extend(source.child_sequences)
        return  Section(measures=measure_list, meter=source.meter, swing=source.swing,
                        name=source.name, performance_attrs=source.performance_attrs)
