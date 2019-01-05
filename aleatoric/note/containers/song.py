# Copyright 2018 Mark S. Weiss

from typing import List, Optional, Tuple, Union

from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.track import Track
from aleatoric.note.modifiers.meter import Meter
from aleatoric.note.modifiers.swing import Swing
from aleatoric.utils.utils import (validate_optional_sequence_of_type,
                                   validate_optional_type,
                                   validate_optional_types,
                                   validate_sequence_of_type, validate_type, validate_types)


class Song(object):
    """A song represents a final composition/performance. It consists of a collection of Tracks. Songs are
       passed to Players, which are responsible for using the Song API to retrieve the Notes and PerformanceAttrs
       from the Song and rendering it into a final performance, such as a MIDI file, *.wav file, live performance
       on Supercollider server, etc. The main element of the Song API is that it maintains an ordered list
       of Tracks in the song, which can also be named and accessed by name.

       Tracks can be added with their own optional `track.name` attribute, which if present will be used to map
       the track by name. If the optional standalone `name` arg is passed to methods that take it,
       such as `append()` or `extend()`, then this name will override the name, if any, in `track.name`
       and the track will be mapped to the standalone `name` arg.

       Support meter and swing attributes at the Song level and applies them to all Tracks, all Measures in those
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
        if to_add == list():
            track_list = to_add
        else:
            try:
                validate_optional_sequence_of_type('to_add', to_add, Track)
                track_list = to_add
            except ValueError:
                pass
            if not track_list:
                validate_optional_type('to_add', to_add, Track)
                track_list = [to_add]
        self.track_list = track_list
        for track in track_list:
            if track.name:
                self.track_map[track.name] = track

        self.meter = meter
        if meter:
            for track in self.track_list:
                track.meter = meter
        self.swing = swing
        if swing:
            for track in self.track_list:
                track.swing = swing
        self.performance_attrs = performance_attrs
        if performance_attrs:
            for track in self.track_list:
                track.performance_attrs = performance_attrs

    # Track list management
    def append(self, name: str, track: Track) -> 'Song':
        validate_type('track', track, Track)
        validate_optional_type('name', name, str)
        self.track_list.append(track)

        # Use `name` arg if present, then `track.name` if present
        track_name = name or track.name
        if track_name:
            self.track_map[track_name] = track
        return self

    def extend(self, to_add: Union[Tuple[str, List[Track]], List[Track], Track]) -> 'Song':
        """`to_add` arg can be either:
            - a single Track
            - a List[Track]
            - a List[Tuple[str, Track]]

            - If a Track is passed in, the Track will be added to `track_list` and, if the Track has a name,
            to `track_map` also.
            - If a List[Track] is passed in, Tracks will be added to `track_list` and, if the Track has a name,
            to a `track_map` also.
            - If a List[Tuple[str, Track]] is passed in, Tracks will be added to `track_list` and, added to
            to `track_map` using the `name` associated with each Track in each Tuple
        """
        try:
            validate_type('to_add', to_add, Track)
            self.append('to_add', to_add)
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_type('to_add', to_add, Track)
            self.track_list.extend(to_add)
            for track in to_add:
                if track.name:
                    self.track_map[track.name] = track
            return self
        except ValueError:
            pass

        validate_type('to_add', to_add, tuple)
        for name, track in to_add:
            validate_types(('name', name, str), ('track', track, Track))
            self.track_list.append(track)
            self.track_map[name] = track
        return self

    def __add__(self, to_add: Union[Tuple[str, List[Track]], List[Track], Track]) -> 'Song':
        return self.extend(to_add)

    def __lshift__(self, to_add: Union[Tuple[str, List[Track]], List[Track], Track]) -> 'Song':
        return self.extend(to_add)

    def insert(self, index: int, to_add: Union[Tuple[str, List[Track]], List[Track], Track]) -> 'Song':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Track)
            self.track_list.insert(index, to_add)
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_type('to_add', to_add, Track)
            for track in to_add:
                self.track_list.insert(index, track)
                index += 1
            return self
        except ValueError:
            pass

        validate_type('to_add', to_add, tuple)
        for name, track in to_add:
            validate_types(('name', name, str), ('track', track, Track))
            self.track_list.insert(index, track)
            index += 1
            self.track_map[name] = track
        return self

    def remove(self, to_remove: Tuple[str, Union[List[Track], Track]]) -> 'Song':
        try:
            validate_type('to_remove', to_remove, Track)
            self.track_list.insert(index, to_remove)
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_type('to_remove', to_remove, Track)
            for track in to_remove:
                self.track_list.remove(track)
            return self
        except ValueError:
            pass

        validate_type('to_remove', to_remove, tuple)
        for name, track in to_remove:
            validate_types(('name', name, str), ('track', track, Track))
            self.track_list.remove(track)
            del self.track_map[name]
        return self
    # /Measure list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.track_list)

    def __iter__(self) -> 'Song':
        self.index = 0
        return self

    def __next__(self) -> Track:
        if self.index == len(self.track_list):
            raise StopIteration
        track = self.track_list[self.index]
        self.index += 1
        return Track.copy(track)

    def __eq__(self, other: 'Song') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.track_list[i] == other.track_list[i] for i in range(len(self.track_list))])
    # /Iter / slice support

    @staticmethod
    def copy(source_song: 'Song') -> 'Song':
        track_list = None
        if source_song.track_list:
            track_list = [Track.copy(track) for track in source_song.track_list]

        new_song = Song(to_add=track_list,
                        name=name,
                        meter=source_song.meter,
                        swing=source_song.swing,
                        performance_attrs=source_song.performance_attrs)
        return new_song

