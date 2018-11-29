# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.measure import Measure, Meter, NoteDur, Swing
from aleatoric.note import Note, NoteSequence

INSTRUMENT = 1
START = 0
DUR = NoteDur.QUARTER.value
AMP = 1.0
PITCH = 10.1
NOTE = Note(instrument=INSTRUMENT, start=START, dur=DUR, amp=AMP, pitch=PITCH)

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

SWING_FACTOR = 0.5


@pytest.fixture
def note_list():
    note_1 = Note.copy(NOTE)
    note_2 = Note.copy(NOTE)
    note_2.start += DUR
    note_3 = Note.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = Note.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


def _setup_test_swing(note_list, swing_direction):
    note_sequence = NoteSequence(note_list)
    swing = Swing(swing_on=True, swing_factor=SWING_FACTOR, swing_direction=swing_direction)
    measure = Measure(note_sequence=note_sequence, swing=swing)
    measure.apply_swing()
    actual_note_starts = [note.start for note in measure.note_sequence.note_list]
    return actual_note_starts


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
    # Assert that the quantized note start times have been adjusted as exepected
    for i, note in enumerate(note_sequence.note_list):
        start_before_quantization = note.start
        start_after_quantization = note_sequence_with_longer_durations.note_list[i].start
        assert start_after_quantization == 0.0 and start_before_quantization == 0.0 or \
            start_after_quantization == start_before_quantization - 0.25


def test_swing_forward(note_list):
    actual_note_starts = _setup_test_swing(note_list, Swing.SwingDirection.Forward)
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_reverse(note_list):
    actual_note_starts = _setup_test_swing(note_list, Swing.SwingDirection.Reverse)
    expected_swing_note_starts = [0.0, .125, 0.25, 0.375]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_both(note_list):
    actual_note_starts = _setup_test_swing(note_list, Swing.SwingDirection.Both)
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values, either start += (swing_factor * start) or
    # start -= (swing_factor * start)
    expected_swing_note_starts = [(0.0, 0.0), (0.125, 0.375), (0.25, 0.75), (0.375, 1.125)]
    for i, actual_note_start in enumerate(actual_note_starts):
        assert actual_note_start in expected_swing_note_starts[i]


if __name__ == '__main__':
    pytest.main(['-xrf'])

