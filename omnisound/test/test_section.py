# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import (Measure,
                                               Meter, NoteDur,
                                               Swing)
from omnisound.note.containers.section import Section
import omnisound.note.adapters.csound_note as csound_note

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SECTION_NAME = 'section'

SWING_RANGE = 0.1
SWING_DIRECTION = Swing.SwingDirection.Forward
SWING_JITTER_TYPE = Swing.SwingJitterType.Fixed

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

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
    if num_notes is None:
        num_notes = NUM_NOTES
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
    return _measure(meter=meter, swing=swing)


def _measure_list(meter, swing):
    return [_measure(meter, swing), _measure(meter, swing)]


@pytest.fixture
def measure_list(meter, swing):
    return _measure_list(meter, swing)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE, swing_direction=SWING_DIRECTION,
                 swing_jitter_type=SWING_JITTER_TYPE)


@pytest.fixture
def performance_attrs():
    performance_attrs = PerformanceAttrs()
    performance_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    return performance_attrs


def _section(measure_list, meter, swing):
    return Section(measure_list=measure_list, meter=meter, swing=swing, name=SECTION_NAME)


@pytest.fixture
def section(measure_list, meter, swing):
    return _section(measure_list, meter, swing)


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


def test_section(meter, swing, performance_attrs, measure_list):
    # Test: List[Measure] and no instrument or performance_attrs
    # Expect a Section with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    section = _section(measure_list, meter, swing)
    assert section.measure_list == measure_list
    assert section.name == SECTION_NAME
    assert section._meter == meter
    assert section._swing == swing
    assert section._performance_attrs is None
    for measure in section:
        assert measure.meter == meter
        assert measure.swing == swing

    # Test: List[Measure] with instrument and performance_attrs
    # Expect a Section with measures, track_instrument, pa and Notes having reassigned instrument and pa
    section = Section(measure_list=measure_list, performance_attrs=performance_attrs)
    assert section.measure_list == measure_list
    assert section.performance_attrs == performance_attrs


# TODO MOVE THIS TO GENERAL PERF ATTRS TEST
def test_performance_attrs(performance_attrs, measure_list):
    section = Section(measure_list=measure_list, performance_attrs=performance_attrs)
    assert section._performance_attrs == performance_attrs
    pa_dict = section._performance_attrs.as_dict()
    assert pa_dict[ATTR_NAME] == ATTR_VAL
    assert isinstance(pa_dict[ATTR_NAME], ATTR_TYPE)

    new_attr_val = ATTR_VAL - 1
    new_performance_attrs = PerformanceAttrs()
    new_performance_attrs.add_attr(ATTR_NAME, new_attr_val, ATTR_TYPE)
    section._performance_attrs = new_performance_attrs
    pa_dict = section._performance_attrs.as_dict()
    assert pa_dict[ATTR_NAME] == new_attr_val
    assert isinstance(pa_dict[ATTR_NAME], ATTR_TYPE)

    new_attr_val = ATTR_VAL - 1
    new_performance_attrs = PerformanceAttrs()
    new_performance_attrs.add_attr(ATTR_NAME, new_attr_val, ATTR_TYPE)
    section.pa = new_performance_attrs
    pa_dict = section.pa.as_dict()
    assert pa_dict[ATTR_NAME] == new_attr_val
    assert isinstance(pa_dict[ATTR_NAME], ATTR_TYPE)


def test_swing_on_apply_swing(section):
    expected_swing_note_starts = [section[0][0].start + SWING_RANGE,
                                  section[0][1].start + SWING_RANGE,
                                  section[0][2].start + SWING_RANGE,
                                  section[0][3].start + SWING_RANGE,
                                  section[1][0].start + SWING_RANGE,
                                  section[1][1].start + SWING_RANGE,
                                  section[1][2].start + SWING_RANGE,
                                  section[1][3].start + SWING_RANGE]

    # Does adjust notes if swing is on
    section.set_swing_on().apply_swing()
    actual_swing_note_starts = section.get_attr('start')
    assert expected_swing_note_starts == pytest.approx(actual_swing_note_starts)


def test_swing_off_apply_swing(section):
    expected_swing_note_starts = [section[0][0].start + SWING_RANGE,
                                  section[0][1].start + SWING_RANGE,
                                  section[0][2].start + SWING_RANGE,
                                  section[0][3].start + SWING_RANGE,
                                  section[1][0].start + SWING_RANGE,
                                  section[1][1].start + SWING_RANGE,
                                  section[1][2].start + SWING_RANGE,
                                  section[1][3].start + SWING_RANGE]

    # Does not adjust notes if swing is off
    section.set_swing_off().apply_swing()
    actual_swing_note_starts = section.get_attr('start')
    assert expected_swing_note_starts != pytest.approx(actual_swing_note_starts)


def test_assign_swing_apply_swing(section):
    # Expect notes to be adjusted downward instead of upward because we use
    # a new Swing with SwingDirection.Reverse instead of the default Forward
    expected_swing_note_starts = [section[0][0].start - SWING_RANGE,
                                  section[0][1].start - SWING_RANGE,
                                  section[0][2].start - SWING_RANGE,
                                  section[0][3].start - SWING_RANGE,
                                  section[1][0].start - SWING_RANGE,
                                  section[1][1].start - SWING_RANGE,
                                  section[1][2].start - SWING_RANGE,
                                  section[1][3].start - SWING_RANGE]

    # Does adjust notes if swing is on
    new_swing = Swing(swing_range=SWING_RANGE, swing_direction=Swing.SwingDirection.Reverse,
                      swing_jitter_type=Swing.SwingJitterType.Fixed)
    section.swing = new_swing
    section.set_swing_on().apply_swing()
    actual_swing_note_starts = section.get_attr('start')
    assert expected_swing_note_starts == pytest.approx(actual_swing_note_starts)


def test_swing_on_apply_phrasing(section):
    """If there are at least 2 notes, first and last will be adjusted as though first as swing forward
       and last has swing reverse. This class tests use of Swing class by Measure class.
    """
    expected_phrasing_note_starts = [section[0][0].start + SWING_RANGE, section[0][3].start - SWING_RANGE]
    section.set_swing_on().apply_phrasing()
    first_measure = section[0]
    second_measure = section[1]
    assert first_measure[0].start == second_measure[0].start == expected_phrasing_note_starts[0]
    assert first_measure[3].start == second_measure[3].start == expected_phrasing_note_starts[1]


def test_quantizing_on_off(section):
    # Default is quantizing on
    for measure in section.measure_list:
        assert measure.meter.is_quantizing()
    # Can override default
    meter_2 = Meter(beat_note_dur=BEAT_DUR, beats_per_measure=BEATS_PER_MEASURE, quantizing=False)
    assert not meter_2.is_quantizing()
    # Can toggle with methods
    meter_2.quantizing_on()
    assert meter_2.is_quantizing()
    meter_2.quantizing_off()
    assert not meter_2.is_quantizing()


def test_assign_meter_swing(meter, section):
    new_meter = Meter(beats_per_measure=BEATS_PER_MEASURE * 2, beat_note_dur=BEAT_DUR)
    section.meter = new_meter
    assert section.meter == new_meter
    new_swing = Swing(swing_range=SWING_RANGE * 2)
    section._swing = new_swing
    assert section._swing == new_swing


def test_quantize(section, measure_list, swing, meter):
    # BEFORE
    # measure ------------------------*
    # 0    0.25    0.50    0.75    1.00     1.25
    # n0************
    #        n1*****
    #               n2***************
    #                        n3***************

    # AFTER
    # measure ------------------------*
    # 0    0.25    0.50    0.75    1.00
    # n0*********
    #        n1**
    #            n2*****
    #                   n3***********

    for measure in section:
        for note in measure:
            note.duration *= 2
        measure[0].start = 0.0
        measure[1].start = DUR
        measure[2].start = (DUR * 2)
        measure[3].start = (DUR * 3)
    quantized_measure_list = _measure_list(meter, swing)
    quantized_section = _section(measure_list=quantized_measure_list, meter=meter, swing=swing)
    for measure in quantized_section:
        for note in measure:
            note.duration *= 2
        measure[0].start = 0.0
        measure[1].start = DUR
        measure[2].start = (DUR * 2)
        measure[3].start = (DUR * 3)

    quantized_section.quantize()
    # Test dur adjustments
    # Assert that after quantization the durations are adjusted
    # Expected adjustment is -0.125 because:
    # - max adjusted start + duration is 1.25
    # - measure_duration is 1.0
    # - adjustment is note_dur *= (1.0 - 1.25), so after adjustment its 0.5 + (0.5 * -0.25) == 0.375
    expected_dur_adjustment = 0.125
    for i, quantized_measure in enumerate(quantized_section):
        measure = section[i]
        for j, quantized_note in enumerate(quantized_measure):
            note = measure[j]
            assert quantized_note.duration == pytest.approx(note.duration - expected_dur_adjustment)

    # Test start adjustments
    # Expected start adjustments
    # - First note starts at 0.0, no adjustment
    # - Second note is 0.25 - (note.duration * total_adjustment) = 0.125
    # - Third note is 0.5 - (note.duration * total_adjustment) = 0.375
    # - Third note is 0.75 - (note.duration * total_adjustment) = 0.625
    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for quantized_measure in quantized_section:
        for i, note in enumerate(quantized_measure):
            assert note.start == pytest.approx(expected_starts[i])


def test_quantize_to_beat(measure, meter, swing):
    # Test: Note durations not on the beat, quantization required
    no_swing = None
    quantized_measure_list = [_measure(meter=meter, swing=no_swing), _measure(meter=meter, swing=no_swing)]
    quantized_section = _section(measure_list=quantized_measure_list, meter=meter, swing=swing)
    for quantized_measure in quantized_section:
        for note in quantized_measure:
            note.start += 0.05
        quantized_measure[1].start = DUR
        quantized_measure[2].start = (DUR * 2)
        quantized_measure[3].start = (DUR * 3)

    # Quantize and assert the start times match the original start_times, which are on the beat
    quantized_section.quantize_to_beat()
    for quantized_measure in quantized_section:
        for i, quantized_note in enumerate(quantized_measure):
            note = measure[i]
            assert quantized_note.start == pytest.approx(note.start)


def test_set_attr(section):
    expected_amp = 100.1

    for measure in section.measure_list:
        for note in measure:
            assert note.amplitude != pytest.approx(expected_amp)

    section.set_attr('amplitude', expected_amp)
    for measure in section.measure_list:
        for note in measure:
            assert note.amplitude == pytest.approx(expected_amp)


def test_get_attr(section):
    assert section.get_attr('start') == [0.0, 0.25, 0.5, 0.75] + [0.0, 0.25, 0.5, 0.75]


if __name__ == '__main__':
    pytest.main(['-xrf'])
