# Copyright 2018 Mark S. Weiss

from typing import List, Optional, Tuple, Union

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.track import Track
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_type,
                                   validate_optional_types,
                                   validate_sequence_of_type, validate_type)


class Song:
    """A song represents a final composition/performance. It consists of a collection of Tracks. Songs are
       passed to Players, which are responsible for using the Song API to retrieve the Notes and PerformanceAttrs
       from the Song and rendering it into a final performance, such as a MIDI file, *.wav file, live performance
       on Supercollider server, etc. The main element of the Song API is that it maintains an ordered list
       of Tracks in the song, which can also be named and accessed by name.

       Song supports Meter and Swing attributes at the Song level and applies them to all Tracks, all Measures in those
       Tracks, to all Notes in those Measures. These attributes make sense to apply globally at the Song level. Also
       supports Song-level PerformanceAttributes, to, for example, apply some effect etc. to all Notes in all
       Tracks in the Song.
    """

    def __init__(self, to_add: Optional[Union[List[Track], Track]] = None,
                 name: str = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        validate_optional_types(('meter', meter, Meter),
                                ('swing', swing, Swing),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        self.name = name
        self.track_map = {}
        self.index = 0

        track_list = []
        if to_add:
            try:
                validate_optional_sequence_of_type('to_add', to_add, Track)
                track_list = to_add
            except ValueError:
                pass
            if not track_list:
                validate_optional_type('to_add', to_add, Track)
                track_list = [to_add]
        self.track_list = track_list
        for track in self.track_list:
            if track.name:
                self.track_map[track.name] = track

        self._meter = meter
        if meter:
            for track in self.track_list:
                track._meter = meter
        self._swing = swing
        if swing:
            for track in self.track_list:
                track._swing = swing
        self._performance_attrs = performance_attrs
        if performance_attrs:
            for track in self.track_list:
                track._performance_attrs = performance_attrs

    @property
    def meter(self):
        return self._meter

    @meter.setter
    def meter(self, meter: Meter):
        validate_type('meter', meter, Meter)
        self._meter = meter
        for track in self.track_list:
            track.meter = meter

    @property
    def tempo(self) -> float:
        return self.meter.tempo_qpm

    @tempo.setter
    def tempo(self, tempo: int):
        self.meter.tempo = tempo
        for track in self.track_list:
            track.tempo = tempo

    def quantizing_on(self):
        for track in self.track_list:
            track.quantizing_on()

    def quantizing_off(self):
        for track in self.track_list:
            track.quantizing_off()

    def quantize(self):
        for track in self.track_list:
            track.quantize()

    def quantize_to_beat(self):
        for track in self.track_list:
            track.quantize_to_beat()
    # /Quantizing for all Measures in the Section

    # Swing for all Measures in the Section
    @property
    def swing(self):
        return self._swing

    @swing.setter
    def swing(self, swing: Swing):
        validate_type('swing', swing, Swing)
        self._swing = swing
        for track in self.track_list:
            track.swing = swing

    def set_swing_on(self) -> 'Song':
        for track in self.track_list:
            track.set_swing_on()
        return self

    def set_swing_off(self) -> 'Song':
        for track in self.track_list:
            track.set_swing_off()
        return self

    def apply_swing(self) -> 'Song':
        for track in self.track_list:
            track.apply_swing()
        return self

    def apply_phrasing(self) -> 'Song':
        for track in self.track_list:
            track.apply_phrasing()
        return self

    @property
    def performance_attrs(self):
        return self._performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        validate_type('performance_attrs', performance_attrs, PerformanceAttrs)
        self._performance_attrs = performance_attrs
        for track in self.track_list:
            track.performance_attrs = performance_attrs
    # /Swing for all Measures in the Section

    # Track list management
    def append(self, track: Track) -> 'Song':
        validate_type('track', track, Track)
        self.track_list.append(track)
        if track.name:
            self.track_map[track.name] = track
        return self

    def extend(self, to_add: List[Track]) -> 'Song':
        validate_sequence_of_type('to_add', to_add, Track)
        self.track_list.extend(to_add)
        for track in to_add:
            if track.name:
                self.track_map[track.name] = track
        return self

    def __add__(self, to_add: Track) -> 'Song':
        return self.append(to_add)

    def __lshift__(self, to_add: Track) -> 'Song':
        return self.append(to_add)

    def insert(self, index: int, to_add: Union[List[Track], Track]) -> 'Song':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Track)
            self.track_list.insert(index, to_add)
            if to_add.name:
                self.track_map[to_add.name] = to_add
            return self
        except ValueError:
            pass

        validate_sequence_of_type('to_add', to_add, Track)
        for track in to_add:
            self.track_list.insert(index, track)
            # noinspection PyUnresolvedReferences
            if track.name:
                # noinspection PyUnresolvedReferences
                self.track_map[track.name] = track
            index += 1
        return self

    def remove(self, to_remove: Tuple[int, int]) -> 'Song':
        assert len(to_remove) == 2
        validate_sequence_of_type('to_remove', to_remove, int)
        start_range = to_remove[0]
        end_range = to_remove[1]
        assert start_range >= 0 and end_range <= len(self.track_list)
        tracks_to_remove = self.track_list[start_range:end_range]
        for track in tracks_to_remove:
            if track.name:
                del self.track_map[track.name]
        del self.track_list[start_range:end_range]
        return self
    # /Track list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.track_list)

    def __getitem__(self, index: int) -> Track:
        validate_type('index', index, int)
        if abs(index) >= len(self.track_list):
            raise IndexError(f'`index` out of range index: {index} len(track_list): {len(self.track_list)}')
        return self.track_list[index]

    def __iter__(self) -> 'Song':
        self.index = 0
        return self

    def __next__(self) -> Track:
        if self.index == len(self.track_list):
            raise StopIteration
        track = self.track_list[self.index]
        self.index += 1
        return track

    def __eq__(self, other: 'Song') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.track_list[i] == other.track_list[i] for i in range(len(self.track_list))])
    # /Iter / slice support

    @staticmethod
    def copy(source: 'Song') -> 'Song':
        track_list = None
        if source.track_list:
            track_list = [Track.copy(track) for track in source.track_list]

        new_song = Song(to_add=track_list,
                        name=source.name,
                        meter=source._meter,
                        swing=source._swing,
                        performance_attrs=source._performance_attrs)
        return new_song
