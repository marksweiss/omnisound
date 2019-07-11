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
        self._performance_attrs = performance_attrs
        self._meter = meter
        self._swing = swing

        # Call NoteSequence base class init, using the first Measure in MeasureList to be the "primary" sequence
        # in the NoteSequence, and then adding each subsequent Measure as a child sequence. NoteSequence supports
        # managing a sequence of notes and an arbitrary list of arbitrarily nested child sequences. Notes can be
        # accessed in a flattened manner as one sequence, and each individual child sequence is also its own
        # NoteSequence and can be accessed individually. This supports Section semantics: we add each measure
        # as a child sequence, all siblings on the same level, effectively creating a sequence of measures we can
        # traverse and manage globally from here by applying meter and swing to all of them, but also each measure
        # can be its own note type with its own attributes.
        # TODO EXPLAIN FIRST MEASURE
        self.first_measure = measures[0]

        # TEMP DEBUG
        import pdb; pdb.set_trace()

        super(Section, self).__init__(make_note=self.first_measure.make_note,
                                      num_notes=len(self.first_measure),
                                      num_attributes=get_num_attributes(self.first_measure),
                                      attr_name_idx_map=self.first_measure.attr_name_idx_map,
                                      attr_vals_defaults_map=self.first_measure.attr_vals_defaults_map,
                                      attr_get_type_cast_map=self.first_measure.attr_get_type_cast_map,
                                      child_sequences=measures[1:])
        self.measures = [self.first_measure] + [measure for measure in self][1:]
        # TODO GET RID OF THIS
        # Now add each additional measure as a "sibling" of the first, a child_sequence all on one level
        # for measure in measures[1:]:
        #     self.append_child_sequence(measure)
        if meter:
            for measure in self.measures:
                measure.meter = meter
        if swing:
            for measure in self.measures:
                measure.swing = swing
        if self._performance_attrs:
            for measure in self.measures:
                measure._performance_attrs = performance_attrs

    # Quantizing for all Measures in the Section
    @property
    def meter(self):
        return self._meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self._meter = meter
        for measure in self:
            measure._meter = meter

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
        return self._swing

    @swing.setter
    def swing(self, swing: Swing):
        validate_type('swing', swing, Swing)
        self._swing = swing
        for measure in self:
            measure._swing = swing

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
        return self._performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self._performance_attrs = performance_attrs
        for measure in self:
            measure._performance_attrs = performance_attrs

    # Measure list management
    # TODO ONLY ALLOW APPENDING CHILD SEQUENCES OR OVERLOAD IMPLEMENTATION TO JUST DO THAT AND PRESENT
    # AS SEQUENCE OF MEASURES AND SEQUENCE OF NOTES
    # TODO IS THIS WORTH IT? BACK TO JUST WRITING QA LIST WRAPPER AND DON'T DERIVE FROM NOTE SEQU
    # MAYBE ANOTHER SIMPLE SEQUENCE BASE
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
        return  Section(measures=measure_list, meter=source._meter, swing=source._swing,
                        name=source.name, performance_attrs=source._performance_attrs)
