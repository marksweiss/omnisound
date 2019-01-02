# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.note_sequence import NoteSequence

# noinspection PyProtectedMember



INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100
PITCH = 1.01
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int


@pytest.fixture
def note_list():
    note_1 = CSoundNote.copy(NOTE)
    note_2 = CSoundNote.copy(NOTE)
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(attr_name=ATTR_NAME, val=ATTR_VAL, attr_type=ATTR_TYPE)
    note_1.performance_attrs = perf_attrs
    note_2.performance_attrs = perf_attrs
    note_list = [note_1, note_2]
    return note_list


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(to_add=note_list)


def test_note_sequence(note_list, note_sequence):
    assert note_sequence
    assert note_sequence.note_list == note_sequence.nl == note_list


def test_note_sequence_iter_note_attr_properties(note_sequence):
    # Iterate once and assert attributes of elements. This tests __iter__() and __next__()
    first_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        # noinspection PyUnresolvedReferences
        assert note.pa.test_attr == ATTR_VAL
        first_loop_count += 1
    # Iterate again. This tests that __iter__() resets the loop state
    second_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        # noinspection PyUnresolvedReferences
        assert note.pa.test_attr == ATTR_VAL
        second_loop_count += 1
    assert first_loop_count == second_loop_count


def test_note_sequence_len_append_getitem(note_sequence):
    # Returns note_list with 2 Notes
    note_3 = CSoundNote.copy(NOTE)
    new_amp = NOTE.amp + 1
    note_3.amp = new_amp
    # Assert initial len() of note_list
    assert len(note_sequence) == 2
    # Append and check len again
    note_sequence.append(note_3)
    assert len(note_sequence) == 3
    # Check that last element has modified attribute, using NoteSequence[idx]
    # to access the note directly by index
    assert note_sequence[2].amp == new_amp


def test_note_sequence_add_lshift_extend(note_sequence):
    expected_len = 2
    assert len(note_sequence) == expected_len
    # Append/Add and check len again
    note_sequence += NOTE
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with lshift syntax
    note_sequence << NOTE
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with a List[Note]
    note_sequence += [NOTE, NOTE]
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Append/Add with a NoteSequence
    new_note_sequence = NoteSequence([NOTE, NOTE])
    note_sequence += new_note_sequence
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Extend with a List[Note]
    note_sequence.extend([NOTE, NOTE])
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Extend with a NoteSequence
    new_note_sequence = NoteSequence([NOTE, NOTE])
    note_sequence.extend(new_note_sequence)
    expected_len += 2
    assert len(note_sequence) == expected_len


def test_note_sequence_insert_remove_getitem(note_sequence):
    note_front = note_sequence[0]
    assert note_front.amp == AMP

    # Insert a single note at the front of the list
    new_amp = AMP + 1
    # noinspection PyTypeChecker
    new_note = CSoundNote.copy(note_front)
    new_note.amp = new_amp
    note_sequence.insert(0, new_note)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp

    # Insert a list of 2 notes at the front of the list
    new_amp_1 = AMP + 2
    # noinspection PyTypeChecker
    new_note_1 = CSoundNote.copy(note_front)
    new_note_1.amp = new_amp_1
    new_amp_2 = AMP + 3
    # noinspection PyTypeChecker
    new_note_2 = CSoundNote.copy(note_front)
    new_note_2.amp = new_amp_2
    new_note_list = [new_note_1, new_note_2]
    note_sequence.insert(0, new_note_list)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp_1
    note_front = note_sequence[1]
    assert note_front.amp == new_amp_2

    # Insert a NoteSequence with 2 notes at the front of the list
    new_amp_1 = AMP + 4
    # noinspection PyTypeChecker
    new_note_1 = CSoundNote.copy(note_front)
    new_note_1.amp = new_amp_1
    new_amp_2 = AMP + 5
    # noinspection PyTypeChecker
    new_note_2 = CSoundNote.copy(note_front)
    new_note_2.amp = new_amp_2
    new_note_list = [new_note_1, new_note_2]
    new_note_sequence = NoteSequence(new_note_list)
    note_sequence.insert(0, new_note_sequence)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp_1
    note_front = note_sequence[1]
    assert note_front.amp == new_amp_2

    # Remove notes added as NoteSequence, List[Note] and Note
    # After removing a note, the new front note is the one added second to most recently
    expected_amp = note_sequence[1].amp
    note_to_remove = note_sequence[0]
    note_sequence.remove(note_to_remove)
    note_front = note_sequence[0]
    assert note_front.amp == expected_amp
    expected_amp = note_sequence[1].amp
    for i in range(4):
        note_to_remove = note_sequence[0]
        note_sequence.remove(note_to_remove)
        note_front = note_sequence[0]
        assert note_front.amp == expected_amp
        expected_amp = note_sequence[1].amp


if __name__ == '__main__':
    pytest.main(['-xrf'])
