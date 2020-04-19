# Copyright 2020 Mark S. Weiss

from typing import List, Tuple

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import Meter, NoteDur, Swing
from omnisound.note.generators.sequencer import Sequencer
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


@pytest.fixture
def sequencer(meter, swing):
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


def test_init(sequencer):
    assert isinstance(sequencer, Sequencer)


def test_add_track(sequencer):
    ret = sequencer.add_track(track_name=TRACK_NAME)
    assert ret == TRACK_NAME
    assert len(sequencer) == 1


def test_set_pattern_for_track_simple(sequencer):
    """Tests setting a simple pattern, with no chords, no meter and no swing"""
    # pattern = 'C:4:MajorSeventh:100|D:4:MajorSeventh:100|E:4:MajorSeventh:100|F:4:MajorSeventh:100|'
    sequencer.add_track(track_name=TRACK_NAME)
    sequencer.set_track_pattern(track_name=TRACK_NAME, pattern=PATTERN)
    assert len(sequencer.track_list) == 1
    assert sequencer.track_list[0].name == TRACK_NAME
    assert len(sequencer.track_list[0].measure_list) == NUM_MEASURES

