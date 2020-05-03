# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import (Measure,
                                               MeasureSwingNotEnabledException,
                                               Meter, NoteDur,
                                               Swing)
import omnisound.note.adapters.csound_note as csound_note

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SWING_RANGE = 0.1

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


def _note(mn=None, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


def _measure(mn=None, meter=None, swing=None, num_notes=None, attr_vals_defaults_map=None):
    if num_notes is None:
        num_notes = NUM_NOTES
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    measure = Measure(meter=meter,
                      swing=swing,
                      num_notes=num_notes,
                      mn=mn)
    if len(measure) == 4:
        measure[1].start += DUR
        measure[2].start += (DUR * 2)
        measure[3].start += (DUR * 3)
    return measure


@pytest.fixture
def measure(make_note_config, meter, swing):
    return _measure(mn=make_note_config, meter=meter, swing=swing)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE)


def _setup_test_swing(measure, swing_direction, swing_on=True) -> Tuple[Swing, Measure]:
    measure.swing.swing_direction = swing_direction
    if swing_on:
        measure.swing.set_swing_on()
    else:
        measure.swing.set_swing_off()
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


def test_swing_on_off_apply_swing(make_note_config, measure, meter, swing):
    """Integration test of behavior of Measure based on its use of Swing as a helper attribute.
       Assumes Swing is tested, and verifies that Measure behaves as expected when using Swing.
    """
    swing.swing_direction = Swing.SwingDirection.Forward
    swing.swing_jitter_type = Swing.SwingJitterType.Fixed
    expected_swing_note_starts = [measure[0].start + SWING_RANGE,
                                  measure[1].start + SWING_RANGE,
                                  measure[2].start + SWING_RANGE,
                                  measure[3].start + SWING_RANGE]
    measure.swing = swing

    # Does not adjust notes if swing is off
    measure.set_swing_off()
    assert not measure.is_swing_on()
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts != actual_note_starts

    # Does adjust notes if swing is on
    measure.set_swing_on()
    assert measure.is_swing_on()
    actual_note_starts = _apply_swing_and_get_note_starts(measure)
    assert expected_swing_note_starts == actual_note_starts

    # Construct a Measure with no Swing and verify expected exceptions are raised
    no_swing = None
    measure_2 = _measure(mn=make_note_config, meter=meter, swing=no_swing)
    with pytest.raises(MeasureSwingNotEnabledException):
        measure_2.set_swing_on()
    with pytest.raises(MeasureSwingNotEnabledException):
        measure_2.set_swing_off()


def test_apply_phrasing(make_note_config, measure, meter, swing):
    """If there are at least 2 notes, first and last will be adjusted as though first as swing forward
       and last has swing reverse. This class tests use of Swing class by Measure class.
    """
    expected_phrasing_note_starts = [measure[0].start + SWING_RANGE, measure[-1].start - SWING_RANGE]

    measure.set_swing_on()
    # If there are two or more noes, first note adjusted down, last note adjusted up
    measure.apply_phrasing()
    assert measure[0].start == pytest.approx(expected_phrasing_note_starts[0])
    assert measure[-1].start == pytest.approx(expected_phrasing_note_starts[1])

    # If there is only one note in the measure, phrasing is a no-op
    short_measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=1)
    expected_phrasing_note_starts = [short_measure[0].start]
    short_measure.apply_phrasing()
    assert short_measure[0].start == expected_phrasing_note_starts[0]

    # Swing is None by default. Test that operations on swing raise if Swing object not provided to __init__()
    no_swing = None
    measure_no_swing = _measure(mn=make_note_config, meter=meter, swing=no_swing)
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


def test_quantize(make_note_config, measure, meter, swing):
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

    quantized_measure = _measure(mn=make_note_config, meter=meter, swing=swing)
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
        assert note.duration == pytest.approx(measure[i].duration - expected_dur_adjustment)

    # Test start adjustments
    # Expected start adjustments
    # - First note starts at 0.0, no adjustment
    # - Second note is 0.25 - (note.dur * total_adjustment) = 0.125
    # - Third note is 0.5 - (note.dur * total_adjustment) = 0.375
    # - Third note is 0.75 - (note.dur * total_adjustment) = 0.625
    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for i, note in enumerate(quantized_measure):
        assert note.start == pytest.approx(expected_starts[i])


def test_quantize_to_beat(make_note_config, measure, meter):
    # Test: Note durations not on the beat, quantization required
    no_swing = None
    quantized_measure = _measure(mn=make_note_config, meter=meter, swing=no_swing)
    for note in quantized_measure:
        note.start += 0.05
    quantized_measure[1].start = DUR
    quantized_measure[2].start = (DUR * 2)
    quantized_measure[3].start = (DUR * 3)
    # Quantize and assert the start times match the original start_times, which are on the beat
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


def test_add_note_on_beat(make_note_config, meter, swing):
    # Test adding a Note and having it copied and placed at each beat position
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    assert len(measure) == 0
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    for i, _ in enumerate(expected_note_start_times):
        measure.add_note_on_beat(_note(mn=make_note_config), increment_beat=True)
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times


def test_add_notes_on_beat(make_note_config, meter, swing):
    # Test adding a NoteSequence and having each added at the beat position
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    assert len(measure) == 0
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    measure.add_notes_on_beat(_note_sequence(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times

    # Test that adding more notes than there are beat positions raises
    extra_note = _note(mn=make_note_config)
    with pytest.raises(ValueError):
        measure.add_note_on_beat(extra_note)


def test_add_note_on_start(make_note_config, meter, swing):
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    assert len(measure) == 0
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    for i, _ in enumerate(expected_note_start_times):
        measure.add_note_on_start(_note(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times

    # Test case of adding a note that would have a start + dur that would be > measure.max_duration raises
    note = _note(mn=make_note_config)
    note.dur = measure.max_duration + 1
    with pytest.raises(ValueError):
        measure.add_note_on_start(note)


def test_add_notes_on_start(make_note_config, meter):
    # Test adding a NoteSequence and having each added at the next start_time after the previous note's duration
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    assert len(measure) == 0
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    measure.add_notes_on_start(_note_sequence(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times

    # Test that adding notes past measure.max_duration raises
    note_sequence = _note_sequence(mn=make_note_config)
    note_sequence[0].dur = measure.max_duration + 1
    with pytest.raises(ValueError):
        measure.add_notes_on_start(note_sequence)


def test_replace_notes_on_start(make_note_config, meter):
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    assert len(measure) == 0
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    measure.add_notes_on_start(_note_sequence(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times

    expected_note_start_times = [0.0, 0.5, 1.0, 1.5]
    measure.tempo = TEMPO_QPM / 2
    measure.replace_notes_on_start(_note_sequence(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times


def test_set_tempo(measure):
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    expected_dur = DUR
    assert expected_note_start_times == [note.start for note in measure]
    for note in measure:
        assert expected_dur == note.duration

    # Halve the tempo and expect duration and start times to double
    measure.tempo = int(TEMPO_QPM / 2)
    expected_note_start_times = [0.0, 0.5, 1.0, 1.5]
    expected_dur = DUR * 2
    assert [note.start for note in measure] == expected_note_start_times
    for note in measure:
        assert note.duration == expected_dur


def test_add_notes_on_start_set_tempo(make_note_config, meter):
    # Test adding a NoteSequence and having each added at the beat position
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    expected_note_start_times = [0.0, 0.25, 0.5, 0.75]
    measure.add_notes_on_start(_note_sequence(mn=make_note_config))
    assert [note.start for note in measure] == expected_note_start_times

    # Halve the tempo and expect duration and start times to double
    expected_note_start_times = [0.0, 0.5, 1.0, 1.5]
    expected_dur = DUR * 2
    meter.tempo = TEMPO_QPM / 2
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    assert len(measure) == 0
    measure.add_notes_on_start(_note_sequence(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times
    for note in measure:
        assert note.duration == expected_dur


def test_add_note_on_start_set_tempo(make_note_config, meter):
    # Halve the tempo and expect duration and start times to double
    expected_note_start_times = [0.0, 0.5, 1.0, 1.5]
    expected_dur = DUR * 2
    meter.tempo = TEMPO_QPM / 2
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    assert len(measure) == 0
    for _ in range(4):
        measure.add_note_on_start(_note(mn=make_note_config))
    assert len(measure) == 4
    assert [note.start for note in measure] == expected_note_start_times
    for note in measure:
        assert note.duration == expected_dur


def test_measure_add_lshift_extend(make_note_config, meter, swing):
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    expected_len = 0
    assert len(measure) == expected_len
    # Append/Add and check len again
    measure += _note(mn=make_note_config)
    expected_len += 1
    assert len(measure) == expected_len
    # Append/Add with lshift syntax
    measure << _note(mn=make_note_config)
    expected_len += 1
    assert len(measure) == expected_len
    # Append/Add with a Measure
    new_measure = _measure(mn=make_note_config)
    measure += new_measure
    expected_len += 4
    assert len(measure) == expected_len
    # Extend with a NoteSequence
    new_sequence = _note_sequence(mn=make_note_config)
    measure.extend(new_sequence)
    expected_len += 4
    assert len(measure) == expected_len

    # Confirm invariant that notes are sorted by start time is maintained
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    note_seq_1 = _note_sequence(mn=make_note_config)
    note_seq_2 = _note_sequence(mn=make_note_config)
    for note in note_seq_1:
        note.start = 0.1
    for note in note_seq_2:
        note.start = 0.2
    measure.extend(note_seq_2)
    measure.extend(note_seq_1)
    note_starts = [note.start for note in measure]
    assert note_starts == 4 * [0.1] + 4 * [0.2]


def test_append_add_lshift_insert_adjust_tempo(make_note_config, meter):
    meter.tempo = TEMPO_QPM / 2
    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    note = _note(mn=make_note_config)
    assert note.duration == DUR
    measure.append(note)
    assert note.duration == DUR * 2

    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    note = _note(mn=make_note_config)
    assert note.duration == DUR
    measure += note
    assert note.duration == DUR * 2

    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    note = _note(mn=make_note_config)
    assert note.duration == DUR
    measure << note
    assert note.duration == DUR * 2

    measure = _measure(mn=make_note_config, meter=meter, num_notes=0)
    note = _note(mn=make_note_config)
    assert note.duration == DUR
    measure.insert(0, note)
    assert note.duration == DUR * 2


def test_measure_insert_remove_getitem(make_note_config, meter, swing):
    # Insert a single note at the front of the list
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    start = 0.1
    note = _note(mn=make_note_config)
    note.start = start
    measure.insert(0, note)
    note_front = measure[0]
    assert note_front.start == start

    # Insert a NoteSequence at the front of the list
    measure = _measure(mn=make_note_config, meter=meter, swing=swing, num_notes=0)
    note_sequence = _note_sequence(mn=make_note_config)
    start_1 = 0.1
    start_2 = 0.2
    note_sequence[0].start = start_1
    note_sequence[1].start = start_2
    measure.insert(0, note_sequence)
    # Default start is 0.0 and these have been sorted ahead of the two notes with start of
    # 0.1 and 0.2. So we verify the invariant that notes are sorted by start time.
    assert measure[0].start == measure[1].start == 0.0
    assert measure[2].start == pytest.approx(start_1)
    assert measure[3].start == pytest.approx(start_2)

    # After removing two notes, the new front note is the one with start 0.1
    measure.remove((0, 2))
    assert len(measure) == 2
    assert measure[0].start == pytest.approx(start_1)


def test_transpose(measure):
    for note in measure:
        note.pitch = 9.01
    interval = 1
    expected_pitch = 9.02
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)

    for note in measure:
        note.pitch = 9.01
    interval = 5
    expected_pitch = 9.06
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)

    for note in measure:
        note.pitch = 9.01
    interval = 12
    expected_pitch = 10.02
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)

    for note in measure:
        note.pitch = 9.01
    interval = -1
    expected_pitch = 8.11
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)

    for note in measure:
        note.pitch = 9.01
    interval = -12
    expected_pitch = 7.11
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)

    for note in measure:
        note.pitch = 9.01
    interval = -13
    expected_pitch = 7.10
    measure.transpose(interval=interval)
    for note in measure:
        assert note.pitch == pytest.approx(expected_pitch)


if __name__ == '__main__':
    pytest.main(['-xrf'])
