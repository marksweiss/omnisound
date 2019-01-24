# Copyright 2018 Mark S. Weiss

from itertools import chain
from typing import Dict, List, Optional, Union

from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import Measure
from aleatoric.note.containers.section import Section
from aleatoric.note.modifiers.meter import Meter
from aleatoric.note.modifiers.swing import Swing
from aleatoric.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_type,
                                   validate_optional_types,
                                   validate_sequence_of_type, validate_type)


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
                 instrument: Optional[int] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_types(('meter', meter, Meter),
                                ('swing', swing, Swing),
                                ('instrument', instrument, int),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))

        self.name = name
        self._section_map = {}

        # Get the measure_list from either List[Measure] or Section
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

        self.index = 0

        # Set the instrument stored at the Track level. Also if an `instrument` was passed in,
        # modify all Measures, which will in turn modify all of their Notes
        if instrument:
            for measure in measure_list:
                measure.instrument = instrument
            self.track_instrument = instrument
        else:
            self.track_instrument = Track.DEFAULT_INSTRUMENT

        super(Track, self).__init__(measure_list=measure_list,
                                    meter=meter,
                                    swing=swing,
                                    name=name,
                                    performance_attrs=performance_attrs)

    # Getters and setters for all core note properties, get from all notes, apply to all notes
    def get_instrument(self) -> List[int]:
        return list(chain.from_iterable([measure.instrument for measure in self.measure_list]))

    def set_instrument(self, instrument: int):
        validate_type('instrument', instrument, int)
        self.track_instrument = instrument
        for measure in self.measure_list:
            measure.instrument = instrument

    instrument = property(get_instrument, set_instrument)
    i = property(get_instrument, set_instrument)
    # Getters and setters for all core note properties, get from all notes, apply to all notes

    # Section accessor. Read only
    def get_section_map(self) -> Dict[str, Section]:
        return self._section_map

    section_map = property(get_section_map, None)
    # /Section accessor. Read only

    # Measure list management
    def append(self, measure: Measure) -> 'Track':
        validate_type('measure', measure, Measure)
        self.measure_list.append(measure)
        return self

    def extend(self, to_add: Union[Measure, List[Measure], Section]) -> 'Track':
        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.append(to_add)
            return self
        except ValueError:
            pass

        try:
            validate_type('to_add', to_add, Section)
            self.measure_list.extend(to_add.measure_list)
            if to_add.name:
                self._section_map[to_add.name] = to_add
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Measure)
        self.measure_list.extend(to_add)

        return self

    def __add__(self, to_add: Union[Measure, List[Measure], Section]) -> 'Track':
        return self.extend(to_add)

    def __lshift__(self, to_add: Union[Measure, List[Measure], Section]) -> 'Track':
        return self.extend(to_add)

    def insert(self, index: int, to_add: Union[Measure, List[Measure], Section]) -> 'Track':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Measure)
            self.measure_list.insert(index, to_add)
            return self
        except ValueError:
            pass

        try:
            validate_type('to_add', to_add, Section)
            for measure in to_add.measure_list:
                self.measure_list.insert(index, measure)
                index += 1
            self._section_map[to_add.name] = to_add
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Measure)
        for measure in to_add:
            self.measure_list.insert(index, measure)
            index += 1

        return self

    def remove(self, to_remove: Union[Measure, List[Measure], Section]) -> 'Track':
        try:
            validate_type('to_remove', to_remove, Measure)
            self.measure_list.remove(to_remove)
            return self
        except ValueError:
            pass

        try:
            validate_type('to_remove', to_remove, Section)
            for measure in to_remove.measure_list:
                self.measure_list.remove(measure)
            if to_remove.name:
                del self._section_map[to_remove.name]
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

    def __getitem__(self, index: int) -> Measure:
        validate_type('index', index, int)
        if abs(index) >= len(self.measure_list):
            raise ValueError(f'`index` out of range index: {index} len(measure_list): {len(self.measure_list)}')
        return self.measure_list[index]

    def __iter__(self) -> 'Track':
        self.index = 0
        return self

    def __next__(self) -> Measure:
        if self.index == len(self.measure_list):
            raise StopIteration
        measure = self.measure_list[self.index]
        self.index += 1
        return measure

    def __eq__(self, other: 'Track') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.measure_list[i] == other.measure_list[i] for i in range(len(self.measure_list))])
    # /Iter / slice support

    @staticmethod
    def copy(source_track: 'Track') -> 'Track':
        measure_list = None
        if source_track.measure_list:
            measure_list = [Measure.copy(measure) for measure in source_track.measure_list]

        new_track = Track(to_add=measure_list,
                          name=source_track.name,
                          instrument=source_track.track_instrument,
                          meter=source_track.meter,
                          swing=source_track.swing,
                          performance_attrs=source_track.performance_attrs)
        return new_track


class MidiTrack(Track):
    def __init__(self, to_add: Optional[Union[List[Measure], Section]] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 name: Optional[str] = None,
                 instrument: Optional[int] = None,
                 channel: int = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_type('channel', channel, int)
        self.channel = channel
        super(MidiTrack, self).__init__(to_add=to_add,
                                        meter=meter,
                                        swing=swing,
                                        name=name,
                                        instrument=instrument,
                                        performance_attrs=performance_attrs)
