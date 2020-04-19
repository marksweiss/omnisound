# Copyright 2020 Mark S. Weiss

from typing import List, Tuple

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import Meter, NoteDur, Swing
from omnisound.note.generators.sequencer import Sequencer, InvalidPatternException
import omnisound.note.adapters.csound_note as csound_note

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
ATTR_GET_TYPE_CAST_MAP = csound_note.ATTR_GET_TYPE_CAST_MAP
NUM_NOTES = 4
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
DEFAULT_IS_QUANTIZING = False
SWING_RANGE = 0.1

SEQUENCER_NAME = 'Sequencer'
NUM_MEASURES = 4
PATTERN_RESOLUTION = NoteDur.QUARTER

TRACK_NAME = 'Track 1'
PATTERN = ('C:4::100 D:4::100 E:4::100 F:4::100|C:4::100 D:4::100 E:4::100 F:4::100|'
           'C:4::100 D:4::100 E:4::100 F:4::100|C:4::100 D:4::100 E:4::100 F:4::100')


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


@pytest.fixture
def meter():
    return Meter(beat_note_dur=BEAT_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                 quantizing=DEFAULT_IS_QUANTIZING)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE)


def _sequencer(meter, swing):
    return Sequencer(name=SEQUENCER_NAME,
                     num_measures=NUM_MEASURES,
                     pattern_resolution=PATTERN_RESOLUTION,
                     meter=meter,
                     make_note=csound_note.make_note,
                     num_attributes=NUM_ATTRIBUTES,
                     attr_name_idx_map=ATTR_NAME_IDX_MAP,
                     attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                     attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP,
                     get_pitch_for_key=csound_note.get_pitch_for_key,
                     swing=swing)


@pytest.fixture
def sequencer(meter, swing):
    return _sequencer(meter, swing)


def test_init(sequencer):
    assert isinstance(sequencer, Sequencer)


def test_add_track(sequencer):
    ret = sequencer.add_track(track_name=TRACK_NAME)
    assert ret == TRACK_NAME
    assert len(sequencer) == 1


def test_set_pattern_for_track(sequencer):
    sequencer.add_track(track_name=TRACK_NAME)
    sequencer.set_track_pattern(track_name=TRACK_NAME, pattern=PATTERN)
    assert len(sequencer.track_list) == 1
    assert sequencer.track_list[0].name == TRACK_NAME
    assert len(sequencer.track_list[0].measure_list) == NUM_MEASURES


def test_add_pattern_as_track(sequencer, meter, swing):
    sequencer.add_track(track_name=TRACK_NAME)
    sequencer.add_pattern_as_track(track_name=TRACK_NAME, pattern=PATTERN)
    track = sequencer.track(TRACK_NAME)

    # Defaults for fixtures have swing off
    expected_starts = [0.0, DUR, 2 * DUR, 3 * DUR]
    first_measure = track.measure_list[0]
    for i, note in enumerate(first_measure):
        assert expected_starts[i] == note.start

    # Make a new sequencer with swing on and verify the start times are adjusted from being on the beat
    swing.set_swing_on()
    swing.swing_direction = Swing.SwingDirection.Forward
    new_sequencer = _sequencer(meter, swing)
    new_sequencer.add_pattern_as_track(track_name=TRACK_NAME, pattern=PATTERN)
    first_measure = new_sequencer.track(TRACK_NAME).measure_list[0]
    for i, note in enumerate(first_measure):
        assert expected_starts[i] < note.start


def test_pattern_resolution(meter, swing):
    new_pattern_resolution = NoteDur.EIGHTH
    sequencer = Sequencer(name=SEQUENCER_NAME,
                          num_measures=NUM_MEASURES,
                          pattern_resolution=new_pattern_resolution,
                          meter=meter,
                          make_note=csound_note.make_note,
                          num_attributes=NUM_ATTRIBUTES,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          swing=swing)

    # Fixture pattern raises because it has four notes per measure but we halved the pattern resolution
    # so there need to be 8 notes per measure
    with pytest.raises(InvalidPatternException):
        sequencer.add_pattern_as_track(track_name=TRACK_NAME, pattern=PATTERN)

    new_pattern = ('C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100')
    sequencer.add_pattern_as_track(track_name=TRACK_NAME, pattern=new_pattern)
    track = sequencer.track(TRACK_NAME)
    first_measure = track.measure_list[0]
    new_dur = DUR / 2
    eighth_note_pattern_resolution_expected_starts = [0.0, new_dur, 2 * new_dur, 3 * new_dur,
                                                      4 * new_dur, 5 * new_dur, 6 * new_dur, 7 * new_dur]
    for i, note in enumerate(first_measure):
        assert eighth_note_pattern_resolution_expected_starts[i] == note.start
