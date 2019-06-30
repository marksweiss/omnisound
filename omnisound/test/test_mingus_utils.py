# Copyright 2018 Mark S. Weiss

from numpy import array, copy as np_copy
import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import MajorKey
from omnisound.utils.mingus_utils import (set_note_pitch_to_mingus_key,
                                          set_notes_pitches_to_mingus_keys)

MATCHED_KEY_TYPE = MajorKey
MINGUS_KEY = 'C'
MINGUS_KEY_LIST = ['C', 'D']
MINGUS_KEY_TO_KEY_ENUM_MAPPING = Scale.KEY_MAPS[MATCHED_KEY_TYPE.__name__]
NOTE_TYPE = CSoundNote
OCTAVE = 4

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 1.01
ATTR_VALS = array([float(INSTRUMENT), START, DUR, AMP, PITCH])
NOTE_SEQUENCE_NUM = 0

NOTE_CLS = CSoundNote
ATTR_NAME_IDX_MAP = NOTE_CLS.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(ATTR_VALS)


@pytest.fixture
def note():
    return _note()


@pytest.fixture
def note_sequence():
    note_sequence = NoteSequence(note_cls=NOTE_CLS,
                                 num_notes=NUM_NOTES,
                                 num_attributes=NUM_ATTRIBUTES,
                                 attr_name_idx_map=ATTR_NAME_IDX_MAP)
    return note_sequence


def _note():
    # Must construct each test Note with a new instance of underlying storage to avoid aliasing bugs
    attr_vals = np_copy(ATTR_VALS)
    return CSoundNote(attr_vals=attr_vals, attr_name_idx_map=ATTR_NAME_IDX_MAP, note_sequence_num=NOTE_SEQUENCE_NUM)


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
                                 NOTE_TYPE,
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
                                     NOTE_TYPE,
                                     OCTAVE,
                                     validate=True)
    # Assert that the note that returns has the expected pitch mapped to the mingus_key
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(note_sequence[i].pitch)


if __name__ == '__main__':
    pytest.main(['-xrf'])
