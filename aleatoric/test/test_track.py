# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import Measure, Meter, NoteDur, Swing
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.containers.section import Section
from aleatoric.note.containers.track import Track

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
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR)


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


def test_track(performance_attrs, measure_list, meter, swing, section):
    # Test: List[Measure] and no instrument or performance_attrs
    # Expect a Track with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=measure_list, name=TRACK_NAME)
    assert track.measure_list == measure_list
    assert track.name == TRACK_NAME
    assert track.track_instrument == Track.DEFAULT_INSTRUMENT
    assert track.meter is None
    assert track.swing is None
    assert track.performance_attrs is None

    # Test: Section and no instrument or performance_attrs
    # Expect a Track with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=section)
    assert track.measure_list == section.measure_list
    assert track.track_instrument == Track.DEFAULT_INSTRUMENT
    assert track.meter is None
    assert track.swing is None
    assert track.performance_attrs is None

    # Test: List[Measure] with instrument, meter, swing and performance_attrs
    # Expect a Track with measures and all other attributes
    track = Track(to_add=measure_list, instrument=INSTRUMENT, meter=meter, swing=swing,
                  performance_attrs=performance_attrs)
    assert track.measure_list == measure_list
    assert track.track_instrument == INSTRUMENT
    assert track.meter == meter
    assert track.swing == swing
    assert track.performance_attrs == performance_attrs

    # Test: List[Measure] with instrument, meter, swing and performance_attrs
    # Expect a Track with measures and all other attributes
    track = Track(to_add=section, instrument=INSTRUMENT, meter=meter, swing=swing,
                  performance_attrs=performance_attrs)
    assert track.measure_list == section.measure_list
    assert track.track_instrument == INSTRUMENT
    assert track.meter == meter
    assert track.swing == swing
    assert track.performance_attrs == performance_attrs


def test_track_section_map(section):
    # Case: falsey track.name, not added to map
    section_name = ''
    section.name = section_name
    track = Track(to_add=section)
    assert not track.section_map
    # Case: has track.name, added to map
    section_name = 'section'
    section.name = section_name
    track = Track(to_add=section)
    assert track.section_map
    assert track.section_map[section_name] == section
    # Case: removed from map
    track.remove(section)
    assert not track.section_map


def test_init_set_get_instrument(measure_list, section):
    track = Track(to_add=measure_list, instrument=INSTRUMENT)
    for measure in track.measure_list:
        for note in measure.note_list:
            assert note.instrument == INSTRUMENT
    assert track.instrument == [1, 1, 1, 1] + [1, 1, 1, 1]
    assert track.track_instrument == INSTRUMENT

    track = Track(to_add=section, instrument=INSTRUMENT)
    for measure in track.measure_list:
        for note in measure.note_list:
            assert note.instrument == INSTRUMENT
    assert track.instrument == [1, 1, 1, 1] + [1, 1, 1, 1]
    assert track.track_instrument == INSTRUMENT

    new_instrument = INSTRUMENT + 1
    track.instrument = new_instrument
    for measure in track.measure_list:
        for note in measure.note_list:
            assert note.instrument == new_instrument
    assert track.track_instrument == new_instrument
    assert track.instrument == [new_instrument, new_instrument, new_instrument, new_instrument,
                                new_instrument, new_instrument, new_instrument, new_instrument]


def test_track_add_lshift_extend(measure, measure_list, section, track):
    expected_len = len(measure_list)
    assert len(track) == expected_len
    # Append/Add and check len again
    expected_len += 1
    track += measure
    assert len(track) == expected_len

    expected_len += 2
    track += [measure, measure]
    assert len(track) == expected_len

    expected_len += len(section)
    track += section
    assert len(track) == expected_len

    # Append/Add with lshift syntax
    expected_len += 1
    track << measure
    assert len(track) == expected_len

    expected_len += 2
    track << [measure, measure]
    assert len(track) == expected_len

    expected_len += len(section)
    track << section
    assert len(track) == expected_len

    # Extend
    expected_len += 1
    track.extend(measure)
    assert len(track) == expected_len

    expected_len += 2
    track.extend([measure, measure])
    assert len(track) == expected_len

    expected_len += len(section)
    track.extend(section)
    assert len(track) == expected_len


def test_section_insert_remove_getitem(measure, measure_list, section, track):
    empty_measure_list = []
    track = Track(to_add=empty_measure_list)
    assert len(track) == 0

    # Insert a single measure at the front of the list
    track.insert(0, measure)
    measure_front = section[0]
    assert measure_front == measure

    # Insert a list of 2 measures at the front of the Track
    empty_measure_list = []
    track = Track(to_add=empty_measure_list)
    measure_1 = Measure.copy(measure)
    measure_1.instrument = INSTRUMENT
    measure_2 = Measure.copy(measure)
    new_instrument = INSTRUMENT + 1
    measure_2.instrument = new_instrument
    measure_list = [measure_1, measure_2]
    track.insert(0, measure_list)
    assert track[0].instrument == [INSTRUMENT, INSTRUMENT, INSTRUMENT, INSTRUMENT]
    assert track[1].instrument == [new_instrument, new_instrument, new_instrument, new_instrument]

    # Insert a Section with two measures to the front of the Track
    empty_measure_list = []
    track = Track(to_add=empty_measure_list)
    measure_1 = Measure.copy(measure)
    measure_1.instrument = INSTRUMENT
    measure_2 = Measure.copy(measure)
    new_instrument = INSTRUMENT + 1
    measure_2.instrument = new_instrument
    measure_list = [measure_1, measure_2]
    section = Section(measure_list=measure_list)
    track.insert(0, section)
    assert track[0].instrument == [INSTRUMENT, INSTRUMENT, INSTRUMENT, INSTRUMENT]
    assert track[1].instrument == [new_instrument, new_instrument, new_instrument, new_instrument]

    # After removing a measure, the new front note is the one added second to most recently
    expected_instrument = track[1].instrument
    measure_to_remove = track[0]
    track.remove(measure_to_remove)
    assert len(track) == 1
    assert track[0].instrument == expected_instrument


if __name__ == '__main__':
    pytest.main(['-xrf'])
