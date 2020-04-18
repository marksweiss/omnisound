# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import (Measure,
                                               Meter, NoteDur,
                                               Swing)
from omnisound.note.containers.section import Section
from omnisound.note.containers.track import Track
import omnisound.note.adapters.csound_note as csound_note

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
          num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.make_note(make_note=csound_note.make_note,
                                  num_attributes=num_attributes,
                                  attr_name_idx_map=attr_name_idx_map,
                                  attr_vals_defaults_map=attr_vals_defaults_map)


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


@pytest.fixture
def track(measure_list, performance_attrs):
    return Track(to_add=measure_list, name=TRACK_NAME, performance_attrs=performance_attrs)


def test_track(performance_attrs, measure_list, meter, swing, section):
    # Test: List[Measure] and no instrument or performance_attrs
    # Expect a Track with measures, no instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=measure_list, name=TRACK_NAME)
    assert track.measure_list == measure_list
    assert track.name == TRACK_NAME
    assert track.instrument == Track.DEFAULT_INSTRUMENT
    assert track._meter is None
    assert track._swing is None
    assert track._performance_attrs is None

    # Test: Section and no instrument or performance_attrs
    # Expect a Track with measures, no instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=section)
    assert track.measure_list == section.measure_list
    assert track.instrument == Track.DEFAULT_INSTRUMENT
    assert track._meter is None
    assert track._swing is None
    assert track._performance_attrs is None

    # Test: List[Measure] with instrument, meter, swing and performance_attrs
    # Expect a Track with measures and all other attributes
    track = Track(to_add=measure_list, instrument=INSTRUMENT, meter=meter, swing=swing,
                  performance_attrs=performance_attrs)
    assert track.measure_list == measure_list
    assert track.instrument == INSTRUMENT
    assert track._meter == meter
    assert track._swing == swing
    assert track._performance_attrs == performance_attrs

    # Test: List[Measure] with instrument, meter, swing and performance_attrs
    # Expect a Track with measures and all other attributes
    track = Track(to_add=section, instrument=INSTRUMENT, meter=meter, swing=swing,
                  performance_attrs=performance_attrs)
    assert track.measure_list == section.measure_list
    assert track.instrument == INSTRUMENT
    assert track._meter == meter
    assert track._swing == swing
    assert track._performance_attrs == performance_attrs


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


def test_init_set_get_instrument(measure_list, section):
    track = Track(to_add=measure_list, instrument=INSTRUMENT)
    for measure in track:
        for note in measure:
            assert note.instrument == INSTRUMENT
    assert track.get_attr('instrument') == [1, 1, 1, 1] + [1, 1, 1, 1]
    assert track.instrument == INSTRUMENT

    new_instrument = INSTRUMENT + 1
    track.instrument = new_instrument
    for measure in track:
        for note in measure:
            assert note.instrument == new_instrument
    assert track.instrument == new_instrument
    assert track.get_attr('instrument') == [new_instrument, new_instrument, new_instrument, new_instrument,
                                            new_instrument, new_instrument, new_instrument, new_instrument]


if __name__ == '__main__':
    pytest.main(['-xrf'])
