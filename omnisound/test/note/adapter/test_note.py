# Copyright 2019 Mark S. Weiss

from typing import List

import pytest

from omnisound.src.note.adapter.note import MakeNoteConfig
import omnisound.src.note.adapter.csound_note as csound_note
from omnisound.src.note.adapter.note import as_dict, as_list, make_rest_note
from omnisound.src.container.note_sequence import NoteSequence


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


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_val_default_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map={})


def _note_sequence(mn=None, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(num_notes=NUM_NOTES, mn=mn)
    return note_sequence


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


def test_as_dict(note):
    expected = ATTR_VALS_DEFAULTS_MAP
    assert as_dict(note) == expected


def test_as_list(note):
    expected = list(ATTR_VALS_DEFAULTS_MAP.values())
    assert as_list(note) == expected


def test_make_rest_note(make_note_config, note):
    attr_val_default_map = {
        'instrument': float(INSTRUMENT),
        'start': START,
        'duration': DUR,
        'amplitude': AMP + 100.0,
        'pitch': PITCH,
    }
    note = _note(mn=make_note_config,
                 attr_val_default_map=attr_val_default_map)
    assert note.amplitude == AMP + 100.0
    make_rest_note(note, 'amplitude')
    assert note.amplitude == 0.0


def test_add_base_attr_name_indexes(note):
    expected_attr_name_idx_map = {
        'instrument': 0,
        'start': 1,
        'duration': 2,
        'amplitude': 3,
        'pitch': 4,
    }
    assert csound_note.ATTR_NAME_IDX_MAP == expected_attr_name_idx_map


if __name__ == '__main__':
    pytest.main(['-xrf'])
