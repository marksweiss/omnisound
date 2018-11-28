# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.measure import Measure, Meter, NoteDur
from aleatoric.note import Note, NoteSequence

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

INSTRUMENT = 1
START = 0
DUR = NoteDur.QUARTER.value
AMP = 1.0
PITCH = 10.1
NOTE = Note(instrument=INSTRUMENT, start=START, dur=DUR, amp=AMP, pitch=PITCH)


@pytest.fixture(scope='module')
def note_list():
    note_1 = Note.copy(NOTE)
    note_2 = Note.copy(NOTE)
    note_2.start += DUR
    note_3 = Note.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = Note.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


def test_quantize(note_list):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    note_sequence_before_quantization = NoteSequence(note_list)
    note_sequence = NoteSequence(note_list)
    meter = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_dur=BEAT_DUR, quantizing=True)
    measure = Measure(note_sequence=note_sequence, meter=meter)
    measure.quantize()
    # Relies on Note.__eq__
    assert note_sequence_before_quantization.note_list == note_sequence.note_list

    # Test: Note durations do not sum to measure duration and no quantizing required
    # Copy the list of notes
    note_list_with_longer_durations = [Note.copy(note) for note in note_list]
    # Modify the note durations in the copy to be longer and require quantization
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2
    note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)

    # Assert that the original list and the copied list notes do not have equivalent durations
    assert [note.dur for note in note_sequence_with_longer_durations.note_list] != \
           [note.dur for note in note_sequence.note_list]
    # Now quantize the copied the note list
    measure = Measure(note_sequence=note_sequence_with_longer_durations, meter=meter)
    measure.quantize()
    # Now assert that after quantization the durations in both note lists are identical
    assert [note.dur for note in note_sequence_with_longer_durations.note_list] == \
           [note.dur for note in note_sequence.note_list]
    # TODO Add check for expected note start times after quantization


if __name__ == '__main__':
    pytest.main(['-xrf'])

