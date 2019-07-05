# Copyright 2018 Mark S. Weiss

import pytest

import omnisound.note.adapters.csound_note as csound_note
from omnisound.note.containers.note_sequence import NoteSequence

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 1.01
NOTE_SEQUENCE_IDX = 0

ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(ATTR_NAME_IDX_MAP)

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int
# TODO TEST COVERAGE FOR CHILD SEQUENCES


def _note_sequence():
    note_sequence = NoteSequence(make_note=csound_note.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=NUM_ATTRIBUTES,
                                 attr_name_idx_map=ATTR_NAME_IDX_MAP)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note():
    return csound_note.make_note(
        _note_sequence().note_attr_vals[NOTE_SEQUENCE_IDX],
        ATTR_NAME_IDX_MAP,
        NOTE_SEQUENCE_IDX)


def test_len(note_sequence):
    assert len(note_sequence) == NUM_NOTES


def test_get_item(note_sequence):
    note_0 = note_sequence[0]
    note_1 = note_sequence[1]
    assert note_0
    assert note_0.amplitude == 0.0
    assert note_1
    assert note_1.amplitude == 0.0


def test_copy(note_sequence):
    note_sequence[0].amplitude = AMP
    note_sequence[1].amplitude = AMP + 1
    new_note_sequence = NoteSequence.copy(note_sequence)
    assert id(note_sequence) != id(new_note_sequence)
    assert new_note_sequence[0].amplitude == note_sequence[0].amplitude
    assert new_note_sequence[1].amplitude == note_sequence[1].amplitude


def test_eq(note_sequence):
    new_note_sequence = NoteSequence.copy(note_sequence)
    assert note_sequence == new_note_sequence
    note_sequence[0].amplitude = AMP
    assert note_sequence != new_note_sequence


def test_note_sequence_iter_note_attr_properties(note_sequence):
    # Iterate once and assert attributes of elements. This tests __iter__() and __next__()
    first_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        first_loop_count += 1
    # Iterate again. This tests that __iter__() resets the loop state
    second_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        second_loop_count += 1
    assert first_loop_count == second_loop_count


def test_note_sequence_len_append_getitem(note_sequence):
    # Returns note_attr_vals with 2 Notes
    note_3 = _note()
    new_amp = AMP + 1
    note_3.amplitude = new_amp
    # Assert initial len() of note_attr_vals
    assert len(note_sequence) == 2
    # Append and check len again
    note_sequence.append(note_3)
    assert len(note_sequence) == 3
    # Check that last element has modified attribute, using NoteSequence[idx]
    # to access the note directly by index
    assert note_sequence[2].amplitude == new_amp


def test_note_sequence_add_lshift_extend(note_sequence):
    expected_len = 2
    assert len(note_sequence) == expected_len
    # Append/Add and check len again
    note_sequence += _note()
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with lshift syntax
    note_sequence << _note()
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with a NoteSequence
    note_sequence += _note_sequence()
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Extend with a NoteSequence
    note_sequence.extend(_note_sequence())
    expected_len += 2
    assert len(note_sequence) == expected_len


# noinspection PyUnresolvedReferences
def test_note_sequence_insert_remove_getitem():
    note_sequence = NoteSequence(make_note=csound_note.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=NUM_ATTRIBUTES,
                                 attr_name_idx_map=ATTR_NAME_IDX_MAP)

    # Get the first note in the sequence, and get its amplitude
    note_front = note_sequence.note(0)
    note_front_amp = note_front.amplitude
    # Insert a new note at the front of the sequence, with a different amplitude
    new_amp = AMP + 1
    new_note = _note()
    new_note.amplitude = new_amp
    note_sequence.insert(0, new_note)
    new_note_front = note_sequence[0]
    new_note_front_amp = new_note_front.amplitude
    # Assert that the new note inserted can be retrieved and is the expected new first note
    assert note_front_amp != new_note_front_amp
    assert new_note_front.amplitude == new_amp

    # After removing a note, the new front note is the one added second to most recently
    expected_amp = note_sequence[1].amplitude
    note_sequence.remove((0, 1))
    note_front = note_sequence[0]
    assert expected_amp == note_front.amplitude


if __name__ == '__main__':
    pytest.main(['-xrf'])
