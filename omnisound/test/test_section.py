# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure, Meter, NoteDur, Swing
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.section import Section

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240

SWING_FACTOR = 0.5

SECTION_NAME = 'section'


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
def performance_attrs():
    performance_attrs = PerformanceAttrs()
    performance_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    return performance_attrs


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(note_list)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR, swing_direction=Swing.SwingDirection.Forward)


@pytest.fixture
def measure(note_list, meter, swing):
    return Measure(to_add=note_list, meter=meter, swing=swing)


@pytest.fixture
def measure_list(measure):
    measure_2 = Measure.copy(measure)
    measure_list = [measure, measure_2]
    return measure_list


@pytest.fixture
def section(measure_list):
    return Section(measure_list, name=SECTION_NAME)


def _apply_swing_and_get_note_starts(measure) -> List[float]:
    measure.apply_swing()
    actual_note_starts = [note.start for note in measure.note_list]
    return actual_note_starts


def test_section(meter, swing, performance_attrs, measure_list):
    # Test: List[Measure] and no instrument or performance_attrs
    # Expect a Section with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    section = Section(measure_list=measure_list, name=SECTION_NAME, meter=meter, swing=swing)
    assert section.measure_list == measure_list
    assert section.name == SECTION_NAME
    assert section.meter == meter
    assert section.swing == swing
    assert section.performance_attrs is None
    for measure in section:
        assert measure.meter == meter
        assert measure.swing == swing

    # Test: List[Measure] with instrument and performance_attrs
    # Expect a Section with measures, track_instrument, pa and Notes having reassigned instrument and pa
    section = Section(measure_list=measure_list, performance_attrs=performance_attrs)
    assert section.measure_list == measure_list
    assert section.performance_attrs == performance_attrs


def test_performance_attrs(performance_attrs, measure_list):
    section = Section(measure_list=measure_list, performance_attrs=performance_attrs)
    assert section.performance_attrs == performance_attrs
    pa_dict = section.performance_attrs.as_dict()
    assert pa_dict[ATTR_NAME] == ATTR_VAL
    assert isinstance(pa_dict[ATTR_NAME], ATTR_TYPE)

    new_attr_val = ATTR_VAL - 1
    new_performance_attrs = PerformanceAttrs()
    new_performance_attrs.add_attr(ATTR_NAME, new_attr_val, ATTR_TYPE)
    section.performance_attrs = new_performance_attrs
    pa_dict = section.performance_attrs.as_dict()
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
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]

    # Does not adjust notes if swing is off
    section.swing_on()
    for measure in section.measure_list:
        actual_note_starts = _apply_swing_and_get_note_starts(measure)
        assert expected_swing_note_starts == pytest.approx(actual_note_starts)


def test_swing_off_apply_swing(section):
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]

    # Does adjust notes if swing is on
    section.swing_off()
    for measure in section.measure_list:
        actual_note_starts = _apply_swing_and_get_note_starts(measure)
        assert expected_swing_note_starts != pytest.approx(actual_note_starts)


def test_assign_swing_apply_swing(section):
    swing_factor = SWING_FACTOR * 2.0
    expected_swing_note_starts = [0.0, 0.5, 1.0, 1.5]

    # Create a new Swing object with a different SWING_FACTOR, assign it to the section
    # and ensure that notes have the exepcted value
    swing = Swing(swing_factor=swing_factor, swing_direction=Swing.SwingDirection.Forward)
    section.swing = swing
    assert section.swing == swing
    section.swing_on()
    for measure in section.measure_list:
        actual_note_starts = _apply_swing_and_get_note_starts(measure)
        assert expected_swing_note_starts == pytest.approx(actual_note_starts)


def test_swing_on_apply_phrasing(note_list, measure, swing, section):
    """If there are at least 2 notes, first and last will be adjusted as though first as swing forward
       and last has swing reverse. This class tests use of Swing class by Measure class.
    """
    expected_phrasing_note_starts = [0.0, 0.375]
    section.swing_on()
    section.apply_phrasing()
    for measure in section.measure_list:
        assert measure[0].start == expected_phrasing_note_starts[0]
        assert measure[-1].start == expected_phrasing_note_starts[-1]

    # If there is only one note in the measure, phrasing is a no-op
    expected_phrasing_note_starts = [note_list[1].start]
    short_measure = Measure([note_list[1]], meter=measure.meter, swing=measure.swing)
    short_measure_2 = Measure.copy(short_measure)
    measure_list = [short_measure, short_measure_2]
    section = Section(measure_list=measure_list)
    section.apply_phrasing()
    for measure in section.measure_list:
        assert measure[0].start == expected_phrasing_note_starts[0]


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
    new_swing = Swing(swing_factor=SWING_FACTOR * 2)
    section.swing = new_swing
    assert section.swing == new_swing


def test_quantize(note_list, section):
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

    def copy_note_list_with_longer_duration(note_list):
        note_list_with_longer_durations = [CSoundNote.copy(note) for note in note_list]
        for note in note_list_with_longer_durations:
            note.dur = note.dur * 2
        return note_list_with_longer_durations

    before_quantize_note_lists = []
    before_quantize_note_lists.append(copy_note_list_with_longer_duration(note_list))
    before_quantize_note_lists.append(copy_note_list_with_longer_duration(note_list))
    for measure in section:
        measure.note_list = copy_note_list_with_longer_duration(note_list)

    section.quantize()

    # Test dur adjustments
    # Assert that after quantization the durations are adjusted
    # Expected adjustment is -0.125 because:
    # - max adjusted start + duration is 1.25
    # - measure_duration is 1.0
    # - adjustment is note_dur *= (1.0 - 1.25), so after adjustment its 0.5 + (0.5 * -0.25) == 0.375
    expected_dur_adjustment = 0.125
    for i, measure in enumerate(section.measure_list):
        for j, note in enumerate(measure.note_list):
            assert note.dur == pytest.approx(before_quantize_note_lists[i][j].dur - expected_dur_adjustment)

    # Test start adjustments
    # Expected start adjustments
    # - First note starts at 0.0, no adjustmentj
    # - Second note is 0.25 - (note.dur * total_adjustment) = 0.125
    # - Third note is 0.5 - (note.dur * total_adjustment) = 0.375
    # - Third note is 0.75 - (note.dur * total_adjustment) = 0.625
    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for measure in section.measure_list:
        for i, note in enumerate(measure.note_list):
            assert note.start == pytest.approx(expected_starts[i])


def test_quantize_to_beat(note_list, section):
    # Test: Note durations not on the beat, quantization required
    note_list_with_offset_start_times = [CSoundNote.copy(note) for note in note_list]
    for note in note_list_with_offset_start_times:
        note.start = note.start + 0.05
    for measure in section.measure_list:
        measure.note_list = note_list_with_offset_start_times

    section.quantize_to_beat()
    # Assert the start times match the original start_times, which are on the beat
    for measure in section.measure_list:
        for i, note in enumerate(note_list):
            assert note.start == pytest.approx(measure.note_list[i].start)


def test_section_add_lshift_extend(measure, measure_list, section):
    expected_len = len(measure_list)
    assert len(section) == expected_len
    # Append/Add and check len again
    expected_len += 1
    section += measure
    assert len(section) == expected_len
    expected_len += 2
    section += [measure, measure]
    assert len(section) == expected_len
    # Append/Add with lshift syntax
    expected_len += 1
    # noinspection PyStatementEffect
    section << measure
    assert len(section) == expected_len
    expected_len += 2
    # noinspection PyStatementEffect
    section << [measure, measure]
    assert len(section) == expected_len
    # Extend
    expected_len += 1
    section.extend(measure)
    expected_len += 2
    section.extend([measure, measure])
    assert len(section) == expected_len


def test_section_insert_remove_getitem(measure, measure_list, section):
    empty_measure_list = []
    section = Section(measure_list=empty_measure_list)
    assert len(section) == 0

    # Insert a single measure at the front of the list
    section.insert(0, measure)
    measure_front = section[0]
    assert measure_front == measure

    # Insert a list of 2 measures at the front of the section
    empty_measure_list = []
    section = Section(measure_list=empty_measure_list)
    measure_1 = Measure.copy(measure)
    measure_1.instrument = INSTRUMENT
    measure_2 = Measure.copy(measure)
    new_instrument = INSTRUMENT + 1
    measure_2.instrument = new_instrument
    measure_list = [measure_1, measure_2]
    section.insert(0, measure_list)
    assert section[0].instrument == [INSTRUMENT, INSTRUMENT, INSTRUMENT, INSTRUMENT]
    assert section[1].instrument == [new_instrument, new_instrument, new_instrument, new_instrument]

    # After removing a measure, the new front note is the one added second to most recently
    expected_instrument = section[1].instrument
    measure_to_remove = section[0]
    section.remove(measure_to_remove)
    assert len(section) == 1
    assert section[0].instrument == expected_instrument


def test_set_get_instrument(section):
    assert section.instrument == [1, 1, 1, 1] + [1, 1, 1, 1]
    assert section.i == [1, 1, 1, 1] + [1, 1, 1, 1]
    section.instrument = 2
    assert section.instrument == [2, 2, 2, 2] + [2, 2, 2, 2]
    assert section.i == [2, 2, 2, 2] + [2, 2, 2, 2]


def test_set_get_start(section):
    assert section.start == [0.0, 0.25, 0.5, 0.75] + [0.0, 0.25, 0.5, 0.75]
    assert section.s == [0.0, 0.25, 0.5, 0.75] + [0.0, 0.25, 0.5, 0.75]
    section.start = 1.0
    assert section.start == [1.0, 1.0, 1.0, 1.0] + [1.0, 1.0, 1.0, 1.0]
    assert section.s == [1.0, 1.0, 1.0, 1.0] + [1.0, 1.0, 1.0, 1.0]


def test_set_get_dur(section):
    assert section.dur == [0.25, 0.25, 0.25, 0.25] + [0.25, 0.25, 0.25, 0.25]
    assert section.d == [0.25, 0.25, 0.25, 0.25] + [0.25, 0.25, 0.25, 0.25]
    section.dur = 1.0
    assert section.dur == [1.0, 1.0, 1.0, 1.0] + [1.0, 1.0, 1.0, 1.0]
    assert section.d == [1.0, 1.0, 1.0, 1.0] + [1.0, 1.0, 1.0, 1.0]


def test_set_get_amp(section):
    assert section.amp == [1, 1, 1, 1] + [1, 1, 1, 1]
    assert section.a == [1, 1, 1, 1] + [1, 1, 1, 1]
    section.amp = 2
    assert section.amp == [2, 2, 2, 2] + [2, 2, 2, 2]
    assert section.a == [2, 2, 2, 2] + [2, 2, 2, 2]


def test_set_get_pitch(section):
    assert section.pitch == [10.1, 10.1, 10.1, 10.1] + [10.1, 10.1, 10.1, 10.1]
    assert section.p == [10.1, 10.1, 10.1, 10.1] + [10.1, 10.1, 10.1, 10.1]
    section.pitch = 10.08
    assert section.pitch == [10.08, 10.08, 10.08, 10.08] + [10.08, 10.08, 10.08, 10.08]
    assert section.p == [10.08, 10.08, 10.08, 10.08] + [10.08, 10.08, 10.08, 10.08]


def test_set_notes_attr(section):
    expected_amp = 100

    for measure in section.measure_list:
        for note in measure:
            assert note.amp != expected_amp

    section.set_notes_attr('amp', expected_amp)
    for measure in section.measure_list:
        for note in measure:
            assert note.amp == expected_amp


def test_get_notes_attr(section):
    assert section.get_notes_attr('start') == [0.0, 0.25, 0.5, 0.75] + [0.0, 0.25, 0.5, 0.75]


def test_transpose(section):
    expected_pitch = 10.02
    section.transpose(interval=1)
    for measure in section.measure_list:
        for note in measure:
            assert note.pitch == expected_pitch


if __name__ == '__main__':
    pytest.main(['-xrf'])
