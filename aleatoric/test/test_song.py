# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import Measure, Meter, NoteDur, Swing
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.containers.section import Section
from aleatoric.note.containers.track import Track
from aleatoric.note.containers.song import Song


INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

SWING_FACTOR = 0.5

TRACK_NAME = 'track'
SONG_NAME = 'song'


@pytest.fixture
def note_list():
    note_1 = CSoundNote.copy(NOTE)
    note_2 = CSoundNote.copy(NOTE)
    note_2.start += DUR
    note_3 = CSoundNote.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = CSoundNote.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


@pytest.fixture
def performance_attrs():
    performance_attrs = PerformanceAttrs()
    performance_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    return performance_attrs


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(note_list)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_dur=BEAT_DUR)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR)


@pytest.fixture
def measure(note_list, meter, swing):
    return Measure(note_list, meter=meter, swing=swing)


@pytest.fixture
def measure_list(measure):
    measure_2 = Measure.copy(measure)
    measure_list = [measure, measure_2]
    return measure_list


@pytest.fixture
def section(measure_list, performance_attrs):
    return Section(measure_list=measure_list, performance_attrs=performance_attrs)


@pytest.fixture
def track(measure_list, performance_attrs):
    return Track(to_add=measure_list, name=TRACK_NAME, performance_attrs=performance_attrs)


@pytest.fixture
def track_list(track):
    return [Track.copy(track), Track.copy(track)]


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
        assert track.meter == meter
        assert track.swing == swing
        assert track.performance_attrs == performance_attrs
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
    assert song.track_list[0].meter == meter
    assert song.track_list[0].swing == swing
    assert song.track_list[0].performance_attrs == performance_attrs
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
    # extend() with List[Track]
    song = Song()
    song.extend(track)
    _extend_add_lshift(song, track)

    def _extend_add_lshift_list_track(song, track_list):
        assert len(song) == 2
        assert song[0] == track_list[0]
        assert song[1] == track_list[1]
        assert song.track_list == track_list
        for i, track in enumerate(song):
            assert song.track_map[track.name] == track

    # Add a List[Track]
    song = Song()
    song += track_list
    _extend_add_lshift_list_track(song, track_list)
    # Add a List[Track] with lshift syntax
    song = Song()
    song << track_list
    _extend_add_lshift_list_track(song, track_list)
    # extend() with List[Track]
    song = Song()
    song.extend(track_list)
    _extend_add_lshift_list_track(song, track_list)


def test_song_insert_remove_getitem(track, track_list):
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
    song.remove(track_1)
    assert len(song) == 1
    assert song[0] == track_2
    assert len(song.track_map) == 1
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
    song.remove(track_1)
    assert len(song) == 1
    assert song[0] == track_2
    assert song.track_map[track_2.name] == track_2
    song.remove(track_2)
    assert len(song) == 0
    assert not song.track_list
    assert not song.track_map
