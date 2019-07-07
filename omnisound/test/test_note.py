# Copyright 2019 Mark S. Weiss

from typing import List

import pytest

import omnisound.note.adapters.csound_note as csound_note
from omnisound.note.adapters.note import as_dict, as_list, make_rest_note
from omnisound.note.containers.note_sequence import NoteSequence


INSTRUMENT = 1
STARTS: List[float] = [1.0, 0.5, 1.5]
INT_STARTS: List[int] = [1, 5, 10]
START = STARTS[0]
INT_START = INT_STARTS[0]
DURS: List[float] = [1.0, 2.0, 2.5]
DUR = DURS[0]
AMPS: List[float] = [1.0, 2.0, 3.0]
AMP = AMPS[0]
PITCHES: List[float] = [1.0, 1.5, 2.0]
PITCH = PITCHES[0]

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0

ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
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


def test_as_dict(note):
    expected = ATTR_VALS_DEFAULTS_MAP
    assert as_dict(note) == expected


def test_as_list(note):
    expected = list(ATTR_VALS_DEFAULTS_MAP.values())
    assert as_list(note) == expected


def test_make_rest_note(note):
    attr_vals_defaults_map = {
        'instrument': float(INSTRUMENT),
        'start': START,
        'duration': DUR,
        'amplitude': AMP + 100.0,
        'pitch': PITCH,
    }
    note = _note(attr_vals_defaults_map=attr_vals_defaults_map)
    assert note.amplitude == AMP + 100.0
    make_rest_note(note, 'amplitude')
    assert note.amplitude == 0.0


def test_add_base_attr_name_indexes(note):
    expected_attr_name_idx_map = {
        'instrument': 0,
        'start': 1,
        'duration': 2,
        'dur': 2,
        'amplitude': 3,
        'amp': 3,
        'pitch': 4,
    }
    assert csound_note.ATTR_NAME_IDX_MAP == expected_attr_name_idx_map


if __name__ == '__main__':
    pytest.main(['-xrf'])
