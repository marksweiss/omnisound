# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from omnisound.src.note.adapter.performance_attrs import PerformanceAttrs
from omnisound.src.container.measure import Measure
from omnisound.src.container.section import Section
from omnisound.src.modifier.meter import Meter
from omnisound.src.modifier.swing import Swing
from omnisound.src.utils.validation_utils import (validate_optional_sequence_of_type, validate_optional_type,
                                                  validate_optional_type_choice,
                                                  validate_optional_types, validate_sequence_of_type, validate_type)


class Track(Section):
    """A Track is a container of Measures that supports adding, removing and modifying Measures.
       A track is one sequence of notes in a Song. For example, in a MIDI Song, it maps
       directly to all the notes in one MIDI Channel. For other backends it is an abstraction holding one
       sequence of notes rendered by one Player in the final Performance.

       Tracks can be constructed empty, or with a list of Measures, and optional PerformanceAttributes.
       PerformanceAttributes and all other Note attributes when set will be applied to all Measures in the Track,
       and therefore to all Notes in each Measure in the Track. An instrument can be provided which will
       likewise be applied to all Measures. Further, Tracks support all of the same Note attributes as Measures
       as setters. If these are set they will be applied to all Measures in the Track, which will apply them to all
       Notes in the Measure. Getters also behave like Measures, retrieving all values for an attribute for all
       Notes in all Measures flattened into a list.

       Sections with names are also added to a map keyed by their name and can be accessed by name and therefore
       modified by reference. So tracks can be managed with sections, e.g. 'intro', 'verse', 'chorus', 'bridge',
       'coda', etc.
    """
    DEFAULT_INSTRUMENT = 0

    def __init__(self, to_add: Optional[Union[List[Measure], Section]] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 name: str = None,
                 instrument: Optional[Union[float, int]] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_types(('meter', meter, Meter),
                                ('swing', swing, Swing),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        validate_optional_type_choice('instrument', instrument, (float, int))

        # Get the measure_list from either List[Measure] or Section
        self._section_map: Dict[str, Section] = {}
        measure_list = []
        if to_add:
            try:
                validate_optional_sequence_of_type('to_add', to_add, Measure)
                measure_list = to_add
            except ValueError:
                pass
            if not measure_list:
                validate_optional_type('to_add', to_add, Section)
                measure_list = to_add.measure_list
                if to_add.name:
                    self._section_map[to_add.name] = to_add
        super(Track, self).__init__(measure_list=measure_list,
                                    meter=meter,
                                    swing=swing,
                                    name=name,
                                    performance_attrs=performance_attrs)

        self.name = name
        self._instrument = instrument
        self.index = 0

        # Set the instrument stored at the Track level. Also if an `instrument` was passed in,
        # modify all Measures, which will in turn modify all of their Notes
        if instrument:
            for measure in measure_list:
                measure.set_attr('instrument', instrument)
            self.instrument = instrument
        else:
            self.instrument = Track.DEFAULT_INSTRUMENT

    # Properties
    def _get_section_map(self) -> Mapping[str, Section]:
        return self._section_map
    section_map = property(_get_section_map, None)

    # TODO Refactor `measure_list` and `section_list` to `measures` and `sections`
    def _get_section_list(self) -> Iterable[Section]:
        return self._section_map.values()
    section_list = property(_get_section_list, None)

    @property
    def instrument(self) -> Union[float, int]:
        return self._instrument

    @instrument.setter
    def instrument(self, instrument: Union[float, int]):
        for measure in self.measure_list:
            measure.set_attr('instrument', instrument)
        self._instrument = instrument

    @property
    def tempo(self) -> float:
        return self.meter.tempo_qpm

    @tempo.setter
    def tempo(self, tempo: int):
        self.meter.tempo = tempo
        for measure in self.measure_list:
            measure.tempo = tempo

    def next_note(self) -> Union[Any, None]:
        for measure in self:
            yield from measure

    # /Properties

    # Measure list management
    def append(self, measure: Measure) -> 'Track':
        validate_type('measure', measure, Measure)
        self.measure_list.append(measure)
        return self

    def extend(self, to_add: Section) -> 'Track':
        validate_type('to_add', to_add, Section)
        self.measure_list.extend(to_add.measure_list)
        if to_add.name:
            self._section_map[to_add.name] = to_add
        return self

    def __add__(self, to_add: Measure) -> 'Track':
        return self.append(to_add)

    def __lshift__(self, to_add: Measure) -> 'Track':
        return self.append(to_add)

    def insert(self, index: int, to_add: Union[Measure, Section]) -> 'Track':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.insert(index, to_add)
            return self
        except ValueError:
            pass

        validate_type('to_add', to_add, Section)
        for measure in to_add.measure_list:
            self.measure_list.insert(index, measure)
            index += 1
        self._section_map[to_add.name] = to_add
        return self

    def remove(self, to_remove: Tuple[int, int]) -> 'Track':
        assert len(to_remove) == 2
        validate_sequence_of_type('to_remove', to_remove, int)
        del self.measure_list[to_remove[0]:to_remove[1]]
        return self
    # /Measure list management

    @staticmethod
    def copy(source_track: 'Track') -> 'Track':
        measure_list = None
        if source_track.measure_list:
            # noinspection PyTypeChecker
            measure_list = [Measure.copy(measure) for measure in source_track.measure_list]
        return Track(to_add=measure_list,
                     name=source_track.name,
                     instrument=source_track.instrument,
                     meter=source_track._meter,
                     swing=source_track._swing,
                     performance_attrs=source_track._performance_attrs)


class MidiTrack(Track):
    MAX_NUM_MIDI_TRACKS: int = 16

    def __init__(self, to_add: Optional[Union[List[Measure], Section]] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 name: Optional[str] = None,
                 instrument: Optional[int] = None,
                 channel: Optional[int] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_type('channel', channel, int)
        self.channel = channel
        super(MidiTrack, self).__init__(to_add=to_add,
                                        meter=meter,
                                        swing=swing,
                                        name=name,
                                        instrument=instrument,
                                        performance_attrs=performance_attrs)
