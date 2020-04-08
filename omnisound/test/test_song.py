# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import (Measure,
                                               Meter, NoteDur,
                                               Swing)
from omnisound.note.containers.section import Section
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
import omnisound.note.adapters.csound_note as csound_note

SONG_NAME = 'song'

TRACK_NAME = 'track'

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SECTION_NAME = 'section'

SWING_RANGE = 0.1
SWING_DIRECTION = Swing.SwingDirection.Forward
SWING_JITTER_TYPE = Swing.SwingJitterType.Fixed

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 4
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(make_note=csound_note.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=num_attributes,
                                 attr_name_idx_map=attr_name_idx_map,
                                 attr_vals_defaults_map=attr_vals_defaults_map)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note(attr_name_idx_map=None, attr_vals_defaults_map=None,
          attr_get_type_cast_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    return csound_note.make_note(
            _note_sequence(
                    attr_name_idx_map=attr_name_idx_map,
                    attr_vals_defaults_map=attr_vals_defaults_map,
                    num_attributes=num_attributes).note_attr_vals[NOTE_SEQUENCE_IDX],
            attr_name_idx_map,
            attr_get_type_cast_map=attr_get_type_cast_map)


@pytest.fixture
def note():
    return _note()


def _measure(meter=None, swing=None, num_notes=None, attr_vals_defaults_map=None):
    if num_notes is None:
        num_notes = NUM_NOTES
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    measure = Measure(meter=meter,
                      swing=swing,
                      make_note=csound_note.make_note,
                      num_notes=num_notes,
                      num_attributes=NUM_ATTRIBUTES,
                      attr_name_idx_map=ATTR_NAME_IDX_MAP,
                      attr_vals_defaults_map=attr_vals_defaults_map)
    if len(measure) == 4:
        measure[1].start += DUR
        measure[2].start += (DUR * 2)
        measure[3].start += (DUR * 3)
    return measure


@pytest.fixture
def measure(meter, swing):
    return _measure(meter=meter, swing=swing)


def _measure_list(meter, swing):
    return [_measure(meter, swing), _measure(meter, swing)]


@pytest.fixture
def measure_list(meter, swing):
    return _measure_list(meter, swing)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE, swing_direction=SWING_DIRECTION,
                 swing_jitter_type=SWING_JITTER_TYPE)


@pytest.fixture
def performance_attrs():
    performance_attrs = PerformanceAttrs()
    performance_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    return performance_attrs


def _section(measure_list, meter, swing):
    return Section(measure_list=measure_list, meter=meter, swing=swing, name=SECTION_NAME)


@pytest.fixture
def section(measure_list, meter, swing):
    return _section(measure_list, meter, swing)


def _track(measure_list, performance_attrs):
    return Track(to_add=measure_list, name=TRACK_NAME, performance_attrs=performance_attrs)


@pytest.fixture
def track(measure_list, performance_attrs):
    return _track(measure_list, performance_attrs)


@pytest.fixture
def track_list(measure_list, performance_attrs):
    return [_track(measure_list, performance_attrs), _track(measure_list, performance_attrs)]


def test_song(meter, swing, performance_attrs, track_list):
    # Give each track in track_list a distinct name for testing
    track_1_name = 'track_1_name'
    track_2_name = 'track_2_name'
    track_list[0].name = track_1_name
    track_list[1].name = track_2_name

    # Test with List[Track]
    song = Song(track_list, name=SONG_NAME, meter=meter, swing=swing, performance_attrs=performance_attrs)
    assert song.track_list == track_list
    assert song.meter == meter
    assert song.swing == swing
    assert song.performance_attrs == performance_attrs
    assert song.name == SONG_NAME
    # Assert Tracks in Song inherited Swing, Meter and PerformanceAttrs
    for track in track_list:
        assert track._meter == meter
        assert track._swing == swing
        assert track._performance_attrs == performance_attrs
    # Assert track_list and track_map
    assert len(song.track_list) == 2
    assert song.track_list[0].name == track_1_name
    assert song.track_list[1].name == track_2_name
    assert song.track_map[track_1_name] == song.track_list[0] == track_list[0]
    assert song.track_map[track_2_name] == song.track_list[1] == track_list[1]

    # Test with Track
    track = track_list[0]
    song = Song(track, name=SONG_NAME, meter=meter, swing=swing, performance_attrs=performance_attrs)
    assert song.track_list == [track]
    assert song.meter == meter
    assert song.swing == swing
    assert song.performance_attrs == performance_attrs
    assert song.name == SONG_NAME
    assert song.track_list[0]._meter == meter
    assert song.track_list[0]._swing == swing
    assert song.track_list[0]._performance_attrs == performance_attrs
    assert song.track_map[track_1_name] == track

    # Test with Track without name
    track = track_list[0]
    track.name = None
    song = Song(track)
    assert song.track_list == [track]
    assert not song.track_map


def test_song_add_lshift_extend(track, track_list):
    # Append
    song = Song()
    expected_len = 1
    song.append(track)
    assert len(song) == expected_len
    assert song[0] == track

    # noinspection PyShadowingNames
    def _extend_add_lshift(song, track):
        assert len(song) == 1
        assert song[0] == track
        for track in song:
            assert song.track_map[track.name] == track

    # Add a List[Track]
    song = Song()
    song += track
    _extend_add_lshift(song, track)
    # Add a List[Track] with lshift syntax
    song = Song()
    song << track
    _extend_add_lshift(song, track)

    # noinspection PyShadowingNames
    def _extend_add_lshift_list_track(song, track_list):
        assert len(song) == 2
        assert song[0] == track_list[0]
        assert song[1] == track_list[1]
        assert song.track_list == track_list
        for i, track in enumerate(song):
            assert song.track_map[track.name] == track

    # extend() with List[Track]
    song = Song()
    song.extend(track_list)
    _extend_add_lshift_list_track(song, track_list)


def test_song_insert_remove_getitem(track):
    empty_track_list = []
    song = Song(to_add=empty_track_list)
    assert len(song) == 0

    # Insert a single track at the front of the Song track_list
    song.insert(0, track)
    track_front = song[0]
    assert track_front == track

    # Insert a list of 2 tracks at the front of the Song track_list
    empty_track_list = []
    song = Song(to_add=empty_track_list)
    track_1 = Track.copy(track)
    track_1_name = 'track_1_name'
    track_1.name = track_1_name
    track_2 = Track.copy(track)
    track_2_name = 'track_2_name'
    track_2.name = track_2_name
    track_list = [track_1, track_2]
    song.insert(0, track_list)
    assert song[0].name == track_1_name
    assert song[1].name == track_2_name
    assert len(song) == 2
    assert song.track_map[track_1_name] == track_1
    assert song.track_map[track_2_name] == track_2

    # After removing a measure, the new front note is the one added second to most recently
    song.remove((0, 1))
    assert len(song) == 1
    assert song[0] == track_2
    assert song.track_map[track_2_name] == track_2

    # Insert and remove 2 Tracks
    song = Song(to_add=empty_track_list)
    track_1 = Track.copy(track)
    track_2 = Track.copy(track)
    track_1.name = track_1_name
    track_2.name = track_2_name
    track_list = [track_1, track_2]
    song.insert(0, track_list)
    assert len(song) == 2
    song.remove((1, 2))
    assert len(song) == 1
    assert song[0] == track_1
    assert song.track_map[track_1.name] == track_1
    song.remove((0, 1))
    assert len(song) == 0
    assert not song.track_list
    assert not song.track_map


if __name__ == '__main__':
    pytest.main(['-xrf'])
