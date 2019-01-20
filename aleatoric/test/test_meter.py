# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.containers.measure import Meter, NoteDur
from aleatoric.note.containers.note_sequence import NoteSequence

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1

BEATS_PER_MEASURE = 4
BEAT_NOTE_DUR = NoteDur.QRTR
TEMPO_QPM = 240
# 4 beats per measure, quarter note is one beat, 240 QPM, so each quarter_note is 1/4 second, measure is 1 sec
MEASURE_DUR = 1
DEFAULT_IS_QUANTIZING = True


@pytest.fixture()
def note():
    return CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)


@pytest.fixture
def note_sequence(note):
    note_1 = CSoundNote.copy(note)
    note_2 = CSoundNote.copy(note)
    note_2.start += DUR
    note_3 = CSoundNote.copy(note)
    note_3.start += (DUR * 2)
    note_4 = CSoundNote.copy(note)
    note_4.start += (DUR * 3)
    note_list = [note_1, note_2, note_3, note_4]
    return NoteSequence(note_list)


@pytest.fixture
def meter():
    return Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                 quantizing=DEFAULT_IS_QUANTIZING)


def test_meter():
    meter = Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                  quantizing=DEFAULT_IS_QUANTIZING)

    assert meter.beats_per_measure == BEATS_PER_MEASURE
    assert meter.beat_note_dur == BEAT_NOTE_DUR
    beat_note_dur: float = BEAT_NOTE_DUR.value
    assert meter.meter_notation == (BEATS_PER_MEASURE, int(1 / beat_note_dur))
    assert meter.tempo_qpm == TEMPO_QPM
    assert meter.quarter_note_dur_secs == pytest.approx(Meter.SECS_PER_MINUTE / TEMPO_QPM)
    assert meter.quarter_notes_per_beat_note == pytest.approx(beat_note_dur / Meter.QUARTER_NOTE_DUR)
    assert meter.note_dur_secs == pytest.approx(meter.quarter_notes_per_beat_note * meter.quarter_note_dur_secs)
    assert meter.measure_dur_secs == pytest.approx(MEASURE_DUR)
    # 4/4
    # 4 quarter note beats per measure
    # 1 whole note beat per measure
    expected_beat_start_times_secs = [0.0, 0.25, 0.5, 0.75]
    for i, start in enumerate(meter.beat_start_times_secs):
        assert start == pytest.approx(expected_beat_start_times_secs[i])


def test_quantizing_on_off(meter):
    # Default is quantizing on
    assert meter.is_quantizing()
    # Can override default
    meter_2 = Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, quantizing=False)
    assert not meter_2.is_quantizing()
    # Can toggle with methods
    meter_2.quantizing_on()
    assert meter_2.is_quantizing()
    meter_2.quantizing_off()
    assert not meter_2.is_quantizing()


# def test_quantize(note_sequence, meter):
#     # Simplest test case: Note durations sum to measure duration and no quantizing required
#     # Also note_list is already sorted by start ascending, so the order after quantiazation will be unchanged
#     expected_note_sequence = NoteSequence.copy(note_sequence)
#     meter.quantize(note_sequence)
#     assert expected_note_sequence == note_sequence

    # Test: Note durations do not sum to measure duration and quantizing required
    # Copy the list of notes
    # note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_sequence]
    # note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)
    # # Modify the note durations in the copy to be longer and require quantization
    # for note in note_list_with_longer_durations:
    #     note.dur = note.dur * 2
    # # Assert that the original list and the copied list notes do not have equivalent durations
    # assert [note.dur for note in note_sequence_with_longer_durations] != \
    #        [note.dur for note in note_sequence]
    # # Now quantize the copied note list
    # meter.quantize(note_sequence_with_longer_durations)
    # # Now assert that after quantization the durations in both note lists are identical
    # assert [note.dur for note in note_sequence_with_longer_durations] == \
    #        [note.dur for note in note_sequence]
    # # Assert that the quantized note start times have been adjusted as expected
    # for i, note in enumerate(note_sequence):
    #     start_after_quantization = note_sequence_with_longer_durations[i].start
    #     start_before_quantization = note.start
    #     assert start_after_quantization == 0.0 and start_before_quantization == 0.0 or \
    #         start_after_quantization == start_before_quantization - 0.25


# def test_quantize_on_off(note_sequence, meter):
#     # Test: Should quantize with quantize set on
#     note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_sequence]
#     for note in note_list_with_longer_durations:
#         note.dur = note.dur * 2
#     note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)
#     meter.quantizing_on()
#     meter.quantize(note_sequence_with_longer_durations)
#     # Now assert that after quantization the durations in both note lists are identical
#     assert [note.dur for note in note_sequence_with_longer_durations] == \
#            [note.dur for note in note_sequence]
#     # Assert that the quantized note start times have been adjusted as exepected
#     for i, note in enumerate(note_sequence):
#         start_after_quantization = note_sequence_with_longer_durations[i].start
#         start_before_quantization = note.start
#         assert start_after_quantization == 0.0 and start_before_quantization == 0.0 or \
#             start_after_quantization == start_before_quantization - 0.25

# # Test: Should not quantize with quantize set off
# note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_sequence]
# for note in note_list_with_longer_durations:
#     note.dur = note.dur * 2
# note_sequence_with_longer_durations = NoteSequence(note_list_with_longer_durations)
# meter.quantizing_off()
# meter.quantize(note_sequence_with_longer_durations)
# # Now assert that after quantization the durations in both note lists are not identical
# assert [note.dur for note in note_sequence_with_longer_durations] != \
#        [note.dur for note in note_sequence]
# # Assert that the quantized note start times have not been adjusted
# for i, note in enumerate(note_sequence):
#     start_after_quantization = note_sequence_with_longer_durations[i].start
#     start_before_quantization = note.start
#     assert start_after_quantization == start_before_quantization


def test_quantize_to_beat(note_sequence, meter):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    # Also note_list is already sorted by start ascending, so the order after quantiazation will be unchanged
    expected_note_sequence = NoteSequence.copy(note_sequence)
    meter.quantize_to_beat(note_sequence)
    assert expected_note_sequence == note_sequence

    # Test: Note durations not on the beat, quantization required
    note_list_with_offset_start_times = [CSoundNote.copy(note) for note in note_sequence]
    note_sequence_with_offset_start_times = NoteSequence(note_list_with_offset_start_times)
    # Modify the note start_times in the copy to be offset from the beats
    for i, note in enumerate(note_list_with_offset_start_times):
        note.start = note.start + 0.05
        assert note.start != note_sequence[i].start
    # Quantize and assert the start times match the original start_times, which are on the beat
    meter.quantize_to_beat(note_sequence_with_offset_start_times)
    assert [note.start for note in note_sequence_with_offset_start_times] == \
           [note.start for note in note_sequence]


if __name__ == '__main__':
    pytest.main(['-xrf'])
