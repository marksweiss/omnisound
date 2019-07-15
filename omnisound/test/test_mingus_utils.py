# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import HarmonicScale, MajorKey
from omnisound.utils.mingus_utils import (set_note_pitch_to_mingus_key,
                                          set_notes_pitches_to_mingus_keys)
import omnisound.note.adapters.csound_note as csound_note


MATCHED_KEY_TYPE = MajorKey
MINGUS_KEY = 'C'
MINGUS_KEY_LIST = ['C', 'D']
MINGUS_KEY_TO_KEY_ENUM_MAPPING = Scale.KEY_MAPS[MATCHED_KEY_TYPE.__name__]
OCTAVE = 4
KEY = MajorKey.C
HARMONIC_SCALE = HarmonicScale.Major

NOTE_TYPE = csound_note

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 9.01
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


def test_get_note_for_mingus_key(note):
    # Octave = 4, key = 'C' == 4.01 in CSound.
    expected_pitch = 4.01
    # Assert that the prototype note used to create the new note is not the expected pitch after
    # we get the note for the mingus_key.
    assert expected_pitch != pytest.approx(note.pitch)

    set_note_pitch_to_mingus_key(MATCHED_KEY_TYPE,
                                 MINGUS_KEY,
                                 MINGUS_KEY_TO_KEY_ENUM_MAPPING,
                                 note,
                                 NOTE_TYPE.get_pitch_for_key,
                                 OCTAVE,
                                 validate=True)
    # Assert that the note that returns has the expected pitch mapped to the mingus_key
    assert expected_pitch == pytest.approx(note.pitch)


def test_get_notes_for_mingus_keys(note_sequence):
    # Octave = 4, key = 'C' == 4.01 in CSound.
    expected_pitches = [4.01, 4.03]
    # Assert that the prototype note used to create the new note is not the expected pitch after
    # we get the note for the mingus_key.
    for i, expected_pitch in enumerate(expected_pitches):
        assert not expected_pitch == pytest.approx(note_sequence[i].pitch)

    set_notes_pitches_to_mingus_keys(MATCHED_KEY_TYPE,
                                     MINGUS_KEY_LIST,
                                     MINGUS_KEY_TO_KEY_ENUM_MAPPING,
                                     note_sequence,
                                     NOTE_TYPE.get_pitch_for_key,
                                     OCTAVE,
                                     validate=True)
    # Assert that the note that returns has the expected pitch mapped to the mingus_key
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(note_sequence[i].pitch)


if __name__ == '__main__':
    pytest.main(['-xrf'])
