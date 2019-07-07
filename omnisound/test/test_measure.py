# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import (Measure,
                                               MeasureSwingNotEnabledException,
                                               Meter, NoteDur,
                                               Swing)
import omnisound.note.adapters.csound_note as csound_note

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SWING_FACTOR = 0.5

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
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


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(make_note=csound_note.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=num_attributes,
                                 attr_name_idx_map=attr_name_idx_map,
                                 attr_vals_defaults_map=attr_vals_defaults_map)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note(attr_name_idx_map=None, attr_vals_defaults_map=None,
          attr_get_type_cast_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    return csound_note.make_note(
            _note_sequence(
                    attr_name_idx_map=attr_name_idx_map,
                    attr_vals_defaults_map=attr_vals_defaults_map,
                    num_attributes=num_attributes).note_attr_vals[NOTE_SEQUENCE_IDX],
            attr_name_idx_map,
            attr_get_type_cast_map=attr_get_type_cast_map)


@pytest.fixture
def note():
    return _note()


def _measure(meter=None, swing=None, num_notes=None, attr_vals_defaults_map=None):
    num_notes = num_notes or NUM_NOTES
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    measure = Measure(meter=meter,
                      swing=swing,
                      make_note=csound_note.make_note,
                      num_notes=num_notes,
                      num_attributes=NUM_ATTRIBUTES,
                      attr_name_idx_map=ATTR_NAME_IDX_MAP,
                      attr_vals_defaults_map=attr_vals_defaults_map)
    if len(measure) == 4:
        measure[1].start += DUR
        measure[2].start += (DUR * 2)
        measure[3].start += (DUR * 3)
    return measure


@pytest.fixture
def measure(meter, swing):
    return _measure(meter, swing)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR)


def _setup_test_swing(measure, swing_direction, swing_on=True) -> Tuple[Swing, Measure]:
    measure.swing.swing_direction = swing_direction
    if swing_on:
        measure.swing.swing_on()
    else:
        measure.swing.swing_off()
    return measure.swing, measure


def _apply_swing_and_get_note_starts(measure) -> List[float]:
    measure.apply_swing()
    actual_note_starts = [note.start for note in measure]
    return actual_note_starts


def test_measure(measure, meter, swing):
    # Assert post-invariant of `Measure.__init__()`, which is that notes are sorted ascending by start
    for i in range(len(measure) - 2):
        assert measure[i].start <= measure[i + 1].start
    # Verify attribute assignments
    assert measure.beat == 0
    assert measure.next_note_start == 0.0
    assert measure.max_duration == measure.meter.beats_per_measure * measure.meter.beat_note_dur.value
    assert measure.meter == meter
    assert measure.swing == swing


def test_swing_on_off_apply_swing(measure, meter, swing):
    """Integration test of behavior of Measure based on its use of Swing as a helper attribute.
       Assumes Swing is tested, and verifies that Measure behaves as expected when using Swing.
    """
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]

    swing.swing_direction = Swing.SwingDirection.Forward
    measure.swing = swing
    # Does not adjust notes if swing is off
    measure.swing_off()
    assert not measure.is_swing_on()
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts != actual_note_starts

    # Does adjust notes if swing is on
    measure.swing_on()
    assert measure.is_swing_on()
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts == actual_note_starts

    # Construct a Measure with no Swing and verify expected exceptions are raised
    no_swing = None
    measure_2 = _measure(meter=meter, swing=no_swing)
    with pytest.raises(MeasureSwingNotEnabledException):
        measure_2.swing_on()
    with pytest.raises(MeasureSwingNotEnabledException):
        measure_2.swing_off()


def test_apply_phrasing(measure, meter, swing):
    """If there are at least 2 notes, first and last will be adjusted as though first as swing forward
       and last has swing reverse. This class tests use of Swing class by Measure class.
    """
    expected_phrasing_note_starts = [0.0, 0.375]

    measure.swing_on()
    # If there are two or more noes, first note adjusted down, last note adjusted up
    measure.apply_phrasing()
    assert measure[0].start == expected_phrasing_note_starts[0]
    assert measure[-1].start == expected_phrasing_note_starts[-1]

    # If there is only one note in the measure, phrasing is a no-op
    short_measure = _measure(meter=meter, swing=swing, num_notes=1)
    expected_phrasing_note_starts = [short_measure[0].start]
    short_measure.apply_phrasing()
    assert short_measure[0].start == expected_phrasing_note_starts[0]

    # Swing is None by default. Test that operations on swing raise if Swing object not provided to __init__()
    no_swing = None
    measure_no_swing = _measure(meter, no_swing)
    with pytest.raises(MeasureSwingNotEnabledException):
        measure_no_swing.apply_phrasing()


def test_quantizing_on_off(measure):
    # Default is quantizing on
    assert measure.is_quantizing()
    # Can override default
    meter_2 = Meter(beat_note_dur=BEAT_DUR, beats_per_measure=BEATS_PER_MEASURE, quantizing=False)
    measure.meter = meter_2
    assert not measure.is_quantizing()
    # Can toggle with methods
    measure.quantizing_on()
    assert measure.is_quantizing()
    measure.quantizing_off()
    assert not measure.is_quantizing()


def test_quantize(measure, meter, swing):
    # BEFORE
    # measure ------------------------*
    # 0    0.25    0.50    0.75    1.00     1.25
    # n0************
    #        n1*************
    #               n2***************
    #                        n3***************

    # AFTER
    # measure ------------------------*
    # 0    0.25    0.50    0.75    1.00
    # n0*********
    #    n1*********
    #           n2**********
    #                   n3************

    for note in measure:
        note.duration *= 2
    measure[0].start = 0.0
    measure[1].start = DUR
    measure[2].start = (DUR * 2)
    measure[3].start = (DUR * 3)

    quantized_measure = _measure(meter, swing)
    for note in quantized_measure:
        note.duration *= 2
    quantized_measure[0].start = 0.0
    quantized_measure[1].start = DUR
    quantized_measure[2].start = (DUR * 2)
    quantized_measure[3].start = (DUR * 3)

    quantized_measure.quantize()

    # Test dur adjustments
    # Assert that after quantization the durations are adjusted
    # Expected adjustment is -0.125 because:
    # - max adjusted start + duration is 1.25
    # - measure_duration is 1.0
    # - adjustment is note_dur *= (1.0 - 1.25), so after adjustment its 0.5 + (0.5 * -0.25) == 0.375
    expected_dur_adjustment = 0.125
    for i, note in enumerate(quantized_measure):
        assert note.dur == pytest.approx(measure[i].dur - expected_dur_adjustment)

    # Test start adjustments
    # Expected start adjustments
    # - First note starts at 0.0, no adjustment
    # - Second note is 0.25 - (note.dur * total_adjustment) = 0.125
    # - Third note is 0.5 - (note.dur * total_adjustment) = 0.375
    # - Third note is 0.75 - (note.dur * total_adjustment) = 0.625
    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for i, note in enumerate(quantized_measure):
        assert note.start == pytest.approx(expected_starts[i])


def test_quantize_to_beat(measure, meter):
    # Test: Note durations not on the beat, quantization required
    note_list_with_offset_start_times = [_note() for _ in range(len(measure))]
    for note in note_list_with_offset_start_times:
        note.start = note.start + 0.05
    note_list_with_offset_start_times[1].start += DUR
    note_list_with_offset_start_times[2].start += (DUR * 2)
    note_list_with_offset_start_times[3].start += (DUR * 3)
    # Quantize and assert the start times match the original start_times, which are on the beat
    quantized_measure = _measure()
    quantized_measure.quantize_to_beat()
    for i, note in enumerate(quantized_measure):
        assert note.start == pytest.approx(measure[i].start)


def test_beat(measure):
    """Beat management logic is in Measure class, but it relies on Meter attribute helper class for state
       of what is beats per measure for the Measure. This test tests the interaction between the classes.
    """
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


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_add_notes_on_beat(note_list, meter, swing):
#     # Test adding a Note and having it copied and placed at each beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     assert len(measure) == 0
#     expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
#     note = note_list[0]
#     measure.add_notes_on_beat(note)
#     assert len(measure) == 4
#     assert [note.start for note in measure] == expected_note_start_times
#
#     # Test adding a list of notes and having each added at the beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
#     measure.add_notes_on_beat(note_list)
#     assert len(measure) == 4
#     assert [note.start for note in measure] == expected_note_start_times
#
#     # Test adding a NoteSequence and having each added at the beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
#     measure.add_notes_on_beat(NoteSequence(note_list))
#     assert len(measure) == 4
#     assert [note.start for note in measure] == expected_note_start_times
#
#     # Test that adding more notes than there are beat positions raises
#     extra_note = CSoundNote.copy(note_list[0])
#     note_list.append(extra_note)
#     with pytest.raises(ValueError):
#         measure.add_notes_on_beat(note_list)


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_add_note_on_beat(meter, swing):
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#
#     # Each note is added on the beat without incrementing the beat, by default ...
#     expected_note_start_time = 0.0
#     measure.add_note_on_beat(CSoundNote.copy(_note()))
#     assert len(measure) == 1
#     assert measure[0].start == expected_note_start_time
#
#     # ... So this note starts at the same time as the last note. But this call passes a flag
#     #  to override the default and increment the beat when adding this note ...
#     expected_note_start_time = 0.0
#     measure.add_note_on_beat(CSoundNote.copy(_note()), increment_beat=True)
#     assert len(measure) == 2
#     assert measure[1].start == expected_note_start_time
#
#     # ... so this note starts on the second beat, after the beat at which the last note was added
#     expected_note_start_time = 0.25
#     measure.add_note_on_beat(CSoundNote.copy(_note()))
#     assert len(measure) == 3
#     assert measure[2].start == expected_note_start_time


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_add_notes_on_start(note_list, meter, swing):
#     # Test adding a Note and having it copied and placed at each beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     assert len(measure) == 0
#
#     # Test adding a list of notes and having each added at the beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
#     measure.add_notes_on_start(note_list)
#     assert len(measure) == 4
#     assert [note.start for note in measure] == expected_note_start_times
#
#     # Test adding a NoteSequence and having each added at the beat position
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
#     measure.add_notes_on_start(NoteSequence(note_list))
#     assert len(measure) == 4
#     assert [note.start for note in measure] == expected_note_start_times
#
#     # Test that adding notes past measure.max_duration raises
#     note = CSoundNote.copy(_note())
#     note.dur = measure.max_duration + 1
#     note_list = [note]
#     with pytest.raises(ValueError):
#         measure.add_notes_on_start(note_list)


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_add_note_on_start(meter, swing):
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#
#     # Each note is added at measure.start, without incrementing the start, by default ...
#     expected_note_start_time = 0.0
#     measure.add_note_on_start(CSoundNote.copy(_note()))
#     assert len(measure) == 1
#     assert measure[0].start == expected_note_start_time
#
#     # ... So this note starts at the same time as the last note. But this call passes a flag
#     #  to override the default and increment the start when adding this note ...
#     expected_note_start_time = 0.0
#     measure.add_note_on_start(CSoundNote.copy(_note()), increment_start=True)
#     assert len(measure) == 2
#     assert measure[1].start == expected_note_start_time
#
#     # ... so this note starts on the second beat, after the beat at which the last note was added
#     expected_note_start_time = 0.25
#     measure.add_note_on_start(CSoundNote.copy(_note()))
#     assert len(measure) == 3
#     assert measure[2].start == expected_note_start_time
#
#     # Test case of adding a note that would have a start + dur that would be > measure.max_duration raises
#     note = CSoundNote.copy(_note())
#     note.dur = measure.max_duration + 1
#     with pytest.raises(ValueError):
#         measure.add_note_on_start(note)


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_measure_add_lshift_extend(meter, swing):
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     expected_len = 0
#
#     assert len(measure) == expected_len
#     # Append/Add and check len again
#     measure += _note()
#     expected_len += 1
#     assert len(measure) == expected_len
#     # Append/Add with lshift syntax
#     measure << _note()
#     expected_len += 1
#     assert len(measure) == expected_len
#     # Append/Add with a List[Note]
#     measure += [_note(), _note()]
#     expected_len += 2
#     assert len(measure) == expected_len
#     # Append/Add with a NoteSequence
#     new_measure = Measure(NoteSequence(to_add=[_note(), _note()]), meter=meter, swing=swing)
#     measure += new_measure
#     expected_len += 2
#     assert len(measure) == expected_len
#     # Extend with a List[Note]
#     measure.extend([_note(), _note()])
#     expected_len += 2
#     assert len(measure) == expected_len
#     # Extend with a NoteSequence
#     new_measure = Measure(NoteSequence(to_add=[_note(), _note()]), meter=meter, swing=swing)
#     measure.extend(new_measure)
#     expected_len += 2
#     assert len(measure) == expected_len


# TODO BROKEN UNTIL NOTE SEQ MANAGING ARRAY CHANGES
# def test_measure_insert_remove_getitem(meter, swing):
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#
#     # Insert a single note at the front of the list
#     start = 0.1
#     note = CSoundNote.copy(_note())
#     note.start = start
#     measure.insert(0, note)
#     note_front = measure[0]
#     assert note_front.start == start
#
#     # Insert a list of 2 notes at the front of the list
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     note_1 = CSoundNote.copy(_note())
#     note_2 = CSoundNote.copy(_note())
#     start_1 = 0.1
#     note_1.start = start_1
#     start_2 = 0.2
#     note_2.start = start_2
#     note_list = [note_1, note_2]
#     measure.insert(0, note_list)
#     assert measure[0].start == start_1
#     assert measure[1].start == start_2
#
#     # Insert a NoteSequence of 2 notes at the front of the list
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     note_1 = CSoundNote.copy(_note())
#     note_2 = CSoundNote.copy(_note())
#     start_1 = 0.1
#     note_1.start = start_1
#     start_2 = 0.2
#     note_2.start = start_2
#     note_list = [note_1, note_2]
#     measure.insert(0, NoteSequence(note_list))
#     assert measure[0].start == start_1
#     assert measure[1].start == start_2
#
#     # After removing a note, the new front note is the one added second to most recently
#     expected_start = measure[1].start
#     note_to_remove = measure[0]
#     measure.remove(note_to_remove)
#     assert len(measure) == 1
#     assert measure[0].start == pytest.approx(expected_start)
#
#     # Remove notes added as NoteSequence and List[Note]
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     note_1 = CSoundNote.copy(_note())
#     note_2 = CSoundNote.copy(_note())
#     note_list = [note_1, note_2]
#     measure.insert(0, note_list)
#     assert len(measure) == 2
#     measure.remove(note_list)
#     assert len(measure) == 0
#
#     empty_note_list = []
#     measure = Measure(to_add=empty_note_list, meter=meter, swing=swing)
#     note_1 = CSoundNote.copy(_note())
#     note_2 = CSoundNote.copy(_note())
#     note_list = [note_1, note_2]
#     measure.insert(0, NoteSequence(note_list))
#     assert len(measure) == 2
#     measure.remove(NoteSequence(note_list))
#     assert len(measure) == 0


def test_set_notes_attr(measure):
    expected_amp = 100
    expected_dur = NoteDur.EIGHTH.value

    for note in measure:
        assert note.amp != expected_amp
    for note in measure:
        assert note.dur != expected_dur

    measure.set_attr('amp', expected_amp)
    measure.set_attr('dur', expected_dur)
    for note in measure:
        assert note.amp == expected_amp
    for note in measure:
        assert note.dur == expected_dur


def test_get_notes_attr(measure):
    assert measure.get_attr('start') == [0.0, 0.25, 0.5, 0.75]


def test_transpose(measure):
    expected_pitch = 10.02
    measure.transpose(interval=1)
    for note in measure:
        assert note.pitch == expected_pitch


if __name__ == '__main__':
    pytest.main(['-xrf'])
