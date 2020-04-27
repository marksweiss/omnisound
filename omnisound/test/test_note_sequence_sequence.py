# Copyright 2019 Mark S. Weiss

import pytest

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.note_sequence_sequence import NoteSequenceSequence
import omnisound.note.adapters.csound_note as csound_note

INSTRUMENT = 1
START = 0.0
DUR = 0.25
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


@pytest.fixture
def note_sequence_sequence(note_sequence):
    return NoteSequenceSequence(note_seq_seq=[note_sequence, note_sequence])


def test_section_append_add_lshift(note_sequence, note_sequence_sequence):
    expected_len = len(note_sequence_sequence)

    expected_len += 1
    note_sequence_sequence.append(note_sequence)
    assert len(note_sequence_sequence) == expected_len

    expected_len += 1
    note_sequence_sequence += note_sequence
    assert len(note_sequence_sequence) == expected_len

    expected_len += 1
    # noinspection PyStatementEffect
    note_sequence_sequence << note_sequence
    assert len(note_sequence_sequence) == expected_len


def test_section_insert_remove_len(note_sequence):
    empty_note_sequence_sequence = NoteSequenceSequence(note_seq_seq=[])

    # Insert a single measure at the front of the list
    empty_note_sequence_sequence.insert(0, note_sequence)
    note_sequence_front = empty_note_sequence_sequence[0]
    assert note_sequence_front == note_sequence
    assert len(empty_note_sequence_sequence) == 1

    # After removing a measure, the new front note is the one added second to most recently
    empty_note_sequence_sequence.remove((0, 1))
    assert len(empty_note_sequence_sequence) == 0


def test_copy_equal(note_sequence_sequence):
    other_note_sequence_sequence = NoteSequenceSequence.copy(note_sequence_sequence)
    assert other_note_sequence_sequence == note_sequence_sequence


def test_iter_getitem(note_sequence, note_sequence_sequence):
    for ns in note_sequence_sequence:
        assert ns == note_sequence
        assert ns[0].start == note_sequence[0].start


if __name__ == '__main__':
    pytest.main(['-xrf'])
