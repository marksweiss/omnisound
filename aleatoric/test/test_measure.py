# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from aleatoric.csound_note import CSoundNote
from aleatoric.measure import Measure, Meter, NoteDur, Swing
from aleatoric.note_sequence import NoteSequence

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

SWING_FACTOR = 0.5


@pytest.fixture
def note_list():
    note_1 = CSoundNote.copy(NOTE)
    note_2 = CSoundNote.copy(NOTE)
    note_2.start += DUR
    note_3 = CSoundNote.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = CSoundNote.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(note_list)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_dur=BEAT_DUR)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR)


@pytest.fixture
def measure(note_list, meter, swing):
    return Measure(note_list, meter=meter, swing=swing)


def _setup_test_swing(measure, swing_direction, swing_on=True) -> Tuple[Swing, Measure]:
    measure.swing.swing_direction = swing_direction
    if swing_on:
        measure.swing.swing_on()
    else:
        measure.swing.swing_off()
    return measure.swing, measure


def _apply_swing_and_get_note_starts(measure) -> List[float]:
    measure.apply_swing()
    actual_note_starts = [note.start for note in measure.note_list]
    return actual_note_starts


def test_quantize(note_list, measure):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    # Also note_list is already sorted by start ascending, so the order after quantiazation will be unchanged
    measure.meter.quantizing_on()
    measure.quantize()
    for i, note in enumerate(note_list):
        # Relies on CSoundNote.__eq__
        assert note == measure.note_list[i]

    # Test: Note durations do not sum to measure duration and no quantizing required
    # Copy the list of notes
    note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_list]
    # Modify the note durations in the copy to be longer and require quantization
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2
    # Assert that the original list and the copied list notes do not have equivalent durations
    assert [note.dur for note in note_list_with_longer_durations] != \
           [note.dur for note in note_list]
    # Now quantize the copied the note list
    measure_with_longer_durations = Measure(note_list_with_longer_durations, meter=measure.meter)
    measure_with_longer_durations.quantize()
    # Now assert that after quantization the durations in both note lists are identical
    assert [note.dur for note in note_list_with_longer_durations] == \
           [note.dur for note in note_list]
    # Assert that the quantized note start times have been adjusted as exepected
    for i, note in enumerate(note_list):
        start_after_quantization = note_list_with_longer_durations[i].start
        start_before_quantization = note.start
        assert start_after_quantization == 0.0 and start_before_quantization == 0.0 or \
            start_after_quantization == start_before_quantization - 0.25


def test_quantize_to_beat(note_list, measure):
    # Simplest test case: Note durations are on the beat, no quantization
    measure.meter.quantizing_on()
    measure.quantize_to_beat()
    for i, note in enumerate(note_list):
        # Relies on CSoundNote.__eq__
        assert note == measure.note_list[i]

    # Test: Note durations not on the beat, quantization required
    note_list_with_offset_start_times = [CSoundNote.copy(note) for note in note_list]
    # Modify the note start_times in the copy to be offset from the beats
    for i, note in enumerate(note_list_with_offset_start_times):
        note.start = note.start + 0.05
        # Assert the new start_time doesn't match the start_time for the same note in the original note_list
        assert note.start != note_list[i].start
    # Quantize and assert the start times match the original start_times, which are on the beat
    measure_with_offset_start_times = Measure(note_list_with_offset_start_times, meter=measure.meter)
    measure_with_offset_start_times.quantize_to_beat()
    assert [note.start for note in note_list_with_offset_start_times] == \
           [note.start for note in note_list]


def test_quantize_on_off(note_list, meter):
    # Test: Should quantize with quantize set on
    note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_list]
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2

    meter.quantizing_on()
    measure = Measure(note_list_with_longer_durations, meter=meter)
    measure.quantize()
    # Now assert that after quantization the durations in both note lists are identical
    assert [note.dur for note in note_list_with_longer_durations] == \
           [note.dur for note in note_list]
    # Assert that the quantized note start times have been adjusted as exepected
    for i, note in enumerate(note_list):
        start_after_quantization = note_list_with_longer_durations[i].start
        start_before_quantization = note.start
        assert start_after_quantization == 0.0 and start_before_quantization == 0.0 or \
            start_after_quantization == start_before_quantization - 0.25

    # Test: Should not quantize with quantize set off
    note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_list]
    for note in note_list_with_longer_durations:
        note.dur = note.dur * 2

    meter.quantizing_off()
    measure = Measure(note_list_with_longer_durations, meter=meter)
    measure.quantize()
    # Now assert that after quantization the durations in both note lists are not identical
    assert [note.dur for note in note_list_with_longer_durations] != \
           [note.dur for note in note_list]
    # Assert that the quantized note start times have not been adjusted
    for i, note in enumerate(note_list):
        start_after_quantization = note_list_with_longer_durations[i].start
        start_before_quantization = note.start
        assert start_after_quantization == start_before_quantization


def test_measure_swing_on_off(swing, measure):
    """Integration test of behavior of Measure based on its use of Swing as a helper attribute.
       Assumes Swing is tested, and verifies that Measure behaves as expected when using Swing.
    """
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    # Does not adjust notes if swing is off
    swing.swing_off()
    swing.swing_direction = Swing.SwingDirection.Forward
    measure.swing = swing
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts != actual_note_starts
    # Does adjust notes if swing is on
    swing.swing_on()
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


def test_measure_apply_phrasing(note_list, measure):
    # If there are at least 2 notes, first and last will be adjusted as though first as swing forward
    # and last has swing reverse
    expected_phrasing_note_starts = [0.0, 0.375]
    measure.swing.swing_on()
    measure.apply_phrasing()
    assert measure[0].start == expected_phrasing_note_starts[0]
    assert measure[-1].start == expected_phrasing_note_starts[-1]

    # If there is only one note in the measure, phrasing is a no-op
    expected_phrasing_note_starts = [note_list[1].start]
    short_measure = Measure([note_list[1]], meter=measure.meter, swing=measure.swing)
    short_measure.apply_phrasing()
    assert short_measure[0].start == expected_phrasing_note_starts[0]


def test_measure_fill_measure_with_note(note_list, meter, swing):
    empty_note_list = []
    measure = Measure(empty_note_list, meter=meter, swing=swing)
    assert len(measure) == 0

    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    note = note_list[0]
    measure.fill_measure_with_note(note)
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times


if __name__ == '__main__':
    pytest.main(['-xrf'])
