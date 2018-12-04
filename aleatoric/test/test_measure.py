# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from aleatoric.measure import Measure, NoteDur, Swing
from aleatoric.note import Note, NoteSequence
from aleatoric.utils import sign

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
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


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(note_list)


@pytest.fixture
def measure(note_sequence):
    return Measure(note_sequence=note_sequence, beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR)


def _setup_test_swing(note_sequence, swing_direction, swing_on=True) -> Tuple[Swing, Measure]:
    swing = Swing(swing_on=swing_on, swing_factor=SWING_FACTOR, swing_direction=swing_direction)
    measure = Measure(note_sequence=note_sequence,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=True, swing=swing)
    return swing, measure


def _apply_swing_and_get_note_starts(measure) -> List[float]:
    measure.apply_swing()
    actual_note_starts = [note.start for note in measure.note_sequence.note_list]
    return actual_note_starts


def test_quantize(note_list):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    note_sequence_before_quantization = NoteSequence(note_list)
    note_sequence = NoteSequence(note_list)
    measure = Measure(note_sequence=note_sequence,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=True)
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
    measure = Measure(note_sequence=note_sequence_with_longer_durations,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=True)
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


def test_quantize_to_beat(note_list):
    # Simplest test case: Note durations are on the beat, no quantization
    note_sequence_before_quantization = NoteSequence(note_list)
    note_sequence = NoteSequence(note_list)
    measure = Measure(note_sequence=note_sequence,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=True)
    measure.quantize_to_beat()
    assert note_sequence_before_quantization.note_list == note_sequence.note_list

    # Test: Note durations not on the beat, quantization required
    note_list_with_offset_start_times = [Note.copy(note) for note in note_list]
    # Modify the note start_times in the copy to be offset from the beats
    for i, note in enumerate(note_list_with_offset_start_times):
        note.start = note.start + 0.05
        # Assert the new start_time doesn't match the start_time for the same note in the original note_list
        assert note.start != note_list[i].start
    # Quantize and assert the start times match the original start_times, which are on the beat
    note_sequence_with_offset_start_times = NoteSequence(note_list_with_offset_start_times)
    measure = Measure(note_sequence=note_sequence_with_offset_start_times,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=True)
    measure.quantize_to_beat()
    assert [note.start for note in note_sequence_with_offset_start_times.note_list] == \
           [note.start for note in note_sequence.note_list]


def test_quantize_on_off(note_list):
    note_sequence = NoteSequence(note_list)

    # Test: Should quantize with quantize set on
    note_list_with_longer_durations = [Note.copy(note) for note in note_list]
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2
    note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)

    quantizing = True
    measure = Measure(note_sequence=note_sequence_with_longer_durations,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=quantizing)
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

    # Test: Should not quantize with quantize set off
    note_list_with_longer_durations = [Note.copy(note) for note in note_list]
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2
    note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)

    quantizing = False
    measure = Measure(note_sequence=note_sequence_with_longer_durations,
                      beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR,
                      quantizing=quantizing)
    measure.quantize()
    # Now assert that after quantization the durations in both note lists are not identical
    assert [note.dur for note in note_sequence_with_longer_durations.note_list] != \
           [note.dur for note in note_sequence.note_list]
    # Assert that the quantized note start times have not been adjusted
    for i, note in enumerate(note_sequence.note_list):
        start_before_quantization = note.start
        start_after_quantization = note_sequence_with_longer_durations.note_list[i].start
        assert start_after_quantization == start_before_quantization


def test_swing_forward(note_sequence):
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    _, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Forward)
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts == actual_note_starts


def test_swing_reverse(note_sequence):
    expected_swing_note_starts = [0.0, .125, 0.25, 0.375]
    _, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Reverse)
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts == actual_note_starts


def test_swing_both(note_sequence):
    expected_swing_note_starts = [(0.0, 0.0), (0.125, 0.375), (0.25, 0.75), (0.375, 1.125)]
    _, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Both)
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values, either start += (swing_factor * start) or
    # start -= (swing_factor * start)
    for i, actual_note_start in enumerate(actual_note_starts):
        assert actual_note_start in expected_swing_note_starts[i]


def test_swing_on_off(note_sequence):
    # Default is swing off
    swing = Swing(swing_factor=SWING_FACTOR, swing_direction=Swing.SwingDirection.Forward)
    assert not swing.is_swing_on()
    # Can override default
    swing = Swing(swing_on=True, swing_factor=SWING_FACTOR, swing_direction=Swing.SwingDirection.Forward)
    assert swing.is_swing_on()
    # Can toggle with methods
    swing.swing_off()
    assert not swing.is_swing_on()
    swing.swing_on()
    assert swing.is_swing_on()

    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    # Does not adjust notes if swing is off
    swing_on = False
    swing, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Forward, swing_on=swing_on)
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts != actual_note_starts
    # Does adjust notes if swing is on
    swing_on = True
    swing, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Forward, swing_on=swing_on)
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts == actual_note_starts


def test_measure_beat(measure):
    assert measure.beat == 0
    measure.increment_beat()
    assert measure.beat == 1
    measure.increment_beat()
    assert measure.beat == 2
    measure.decrement_beat()
    assert measure.beat == 1
    # Test not changing on boundary values
    measure.decrement_beat()
    assert measure.beat == 0
    measure.decrement_beat()
    assert measure.beat == 0
    for i in range(measure.meter.beats_per_measure + 10):
        assert measure.beat <= measure.meter.beats_per_measure


def test_measure_apply_phrasing(note_list, note_sequence):
    # If there are at least 2 notes, first and last will be adjusted as though first as swing forward
    # and last has swing reverse
    expected_phrasing_note_starts = [0.0, 0.375]
    _, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Forward)
    measure.apply_phrasing()
    assert measure.note_sequence[0].start == expected_phrasing_note_starts[0]
    assert measure.note_sequence[-1].start == expected_phrasing_note_starts[-1]

    # If there is only one note in the measure, phrasing is a no-op
    expected_phrasing_note_starts = [note_list[1].start]
    note_sequence = NoteSequence([note_list[1]])
    _, measure = _setup_test_swing(note_sequence, Swing.SwingDirection.Forward)
    measure.apply_phrasing()
    assert measure.note_sequence[0].start == expected_phrasing_note_starts[0]


def test_measure_fill_measure_with_note(note_list):
    empty_note_sequence = NoteSequence([])
    measure = Measure(note_sequence=empty_note_sequence, beats_per_measure=BEATS_PER_MEASURE, beat_duration=BEAT_DUR)
    note = note_list[0]
    assert len(measure.note_sequence) == 0

    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    measure.fill_measure_with_note(note)
    assert len(measure.note_sequence) == 4
    assert [note.start for note in measure.note_sequence] == expected_note_start_times


if __name__ == '__main__':
    pytest.main(['-xrf'])

