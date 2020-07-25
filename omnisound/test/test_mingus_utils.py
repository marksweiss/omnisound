# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapter.note import MakeNoteConfig
from omnisound.note.container.note_sequence import NoteSequence
from omnisound.note.generator.scale import Scale
from omnisound.note.generator.scale_globals import HarmonicScale, MajorKey
from omnisound.utils.mingus_utils import (set_note_pitch_to_mingus_key,
                                          set_notes_pitches_to_mingus_keys)
import omnisound.note.adapter.csound_note as csound_note


MINGUS_KEY = 'C'
MINGUS_KEY_LIST = ['C', 'D']
MINGUS_KEY_TO_KEY_ENUM_MAPPING = Scale.KEY_MAPS[MajorKey.__name__]
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


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map={})


def _note_sequence(mn=None, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(num_notes=NUM_NOTES, mn=mn)
    return note_sequence


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


def test_get_note_for_mingus_key(note):
    # Octave = 4, key = 'C' == 4.01 in CSound.
    expected_pitch = 4.01
    # Assert that the prototype note used to create the new note is not the expected pitch after
    # we get the note for the mingus_key.
    assert expected_pitch != pytest.approx(note.pitch)

    set_note_pitch_to_mingus_key(MINGUS_KEY,
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

    set_notes_pitches_to_mingus_keys(MINGUS_KEY_LIST,
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
