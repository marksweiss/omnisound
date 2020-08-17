# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.container.note_sequence import NoteSequence
import omnisound.src.note.adapter.csound_note as csound_note

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

BEATS_PER_MEASURE = 4
BEAT_NOTE_DUR = NoteDur.QRTR
TEMPO_QPM = 240
# 4 beats per measure, quarter note is one beat, 240 QPM, so each quarter_note is 1/4 second, measure is 1 sec
MEASURE_DUR = 1
DEFAULT_IS_QUANTIZING = True

NOTE_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
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
                          attr_val_default_map=NOTE_DEFAULTS_MAP,
                          attr_get_type_cast_map={})


def _note_sequence(mn=None, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or NOTE_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(num_notes=NUM_NOTES, mn=mn)
    return note_sequence


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn=None, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or NOTE_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


@pytest.fixture
def meter():
    return Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                 quantizing=DEFAULT_IS_QUANTIZING)


def test_meter():
    meter = Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                  quantizing=DEFAULT_IS_QUANTIZING)

    assert meter.beats_per_measure == BEATS_PER_MEASURE
    assert meter.beat_note_dur == BEAT_NOTE_DUR
    # noinspection PyTypeChecker
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


def _setup_test_quantize(mn=None, meter=None, quantize_on=True):
    sequence_before_quantize = _note_sequence(mn=mn)
    for note in sequence_before_quantize:
        note.duration *= 2
    sequence_before_quantize[1].start += DUR
    sequence_before_quantize[2].start += (DUR * 2)
    sequence_before_quantize[3].start += (DUR * 3)

    sequence_after_quantize = _note_sequence(mn=mn)
    for note in sequence_after_quantize:
        note.duration *= 2
    sequence_after_quantize[1].start += DUR
    sequence_after_quantize[2].start += (DUR * 2)
    sequence_after_quantize[3].start += (DUR * 3)

    if quantize_on:
        meter.quantizing_on()
    else:
        meter.quantizing_off()

    meter.quantize(sequence_after_quantize)

    return sequence_before_quantize, sequence_after_quantize


def test_quantize_on_off(make_note_config, note_sequence, meter):
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

    # Test quantize on
    note_list_before_quantize, note_list_after_quantize = _setup_test_quantize(mn=make_note_config,
                                                                               meter=meter,
                                                                               quantize_on=True)

    # Test dur adjustments
    # Expected adjustment is -0.125 because:
    # - max adjusted start +/duration is 1.25
    # - measure_duration is 1.0
    # - adjustment is note_dur *= (1.0 - 1.25), so after adjustment its 0.5 + (0.5 * -0.25) == 0.375
    expected_dur_adjustment = 0.125
    for i, note in enumerate(note_list_after_quantize):
        assert note.duration == pytest.approx(note_list_before_quantize[i].duration - expected_dur_adjustment)

    # Test start adjustments
    # Expected start adjustments
    # - First note starts at 0.0, no adjustment
    # - Second note is 0.25 - (note.duration * total_adjustment) = 0.125
    # - Third note is 0.5 - (note.duration * total_adjustment) = 0.375
    # - Third note is 0.75 - (note.duration * total_adjustment) = 0.625
    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for i, note in enumerate(note_list_after_quantize):
        assert note.start == pytest.approx(expected_starts[i])

    # Test quantize off
    note_list_before_quantize, note_list_after_quantize = _setup_test_quantize(mn=make_note_config,
                                                                               meter=meter,
                                                                               quantize_on=False)

    expected_dur_adjustment = 0.125
    for i, note in enumerate(note_list_after_quantize):
        assert note.duration != pytest.approx(note_list_before_quantize[i].duration - expected_dur_adjustment)

    expected_starts = [0.0, 0.125, 0.375, 0.625]
    for i, note in enumerate(note_list_after_quantize):
        assert note.start == pytest.approx(0.0) or note.start != pytest.approx(expected_starts[i])


def test_quantize_to_beat(make_note_config, note_sequence, meter):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    # Also note_list is already sorted by start ascending, so the order after quantization will be unchanged

    note_sequence[1].start += DUR
    note_sequence[2].start += (DUR * 2)
    note_sequence[3].start += (DUR * 3)

    note_starts_before_quantize = [note.start for note in note_sequence]
    note_durations_before_quantize = [note.duration for note in note_sequence]
    meter.quantize_to_beat(note_sequence)
    note_starts_after_quantize = [note.start for note in note_sequence]
    note_durations_after_quantize = [note.duration for note in note_sequence]
    assert note_starts_before_quantize == note_starts_after_quantize and \
        note_durations_before_quantize == note_durations_after_quantize

    # Test: Note durations not on the beat, quantization required
    note_sequence_with_offset_start_times = _note_sequence(mn=make_note_config)
    note_sequence_with_offset_start_times[1].start += DUR
    note_sequence_with_offset_start_times[2].start += (DUR * 2)
    note_sequence_with_offset_start_times[3].start += (DUR * 3)
    # Modify the note start_times in the copy to be offset from the beats
    for i, note in enumerate(note_sequence_with_offset_start_times):
        note.start += 0.05
        assert note.start != note_sequence[i].start
    # Quantize and then assert the start times match the original start_times, which are on the beat
    meter.quantize_to_beat(note_sequence_with_offset_start_times)
    assert [note.start for note in note_sequence_with_offset_start_times] == \
           [note.start for note in note_sequence]


def test_tempo(meter):
    assert meter.tempo == TEMPO_QPM
    quarter_note_dur_secs = meter.quarter_note_dur_secs
    note_dur_secs = meter.note_dur_secs
    measure_dur_secs = meter.measure_dur_secs

    new_tempo = TEMPO_QPM / 2
    meter.tempo = new_tempo
    assert meter.tempo == new_tempo
    assert meter.quarter_note_dur_secs == pytest.approx(2 * quarter_note_dur_secs)
    assert meter.note_dur_secs == pytest.approx(2 * note_dur_secs)
    assert meter.measure_dur_secs == pytest.approx(2 * measure_dur_secs)


if __name__ == '__main__':
    pytest.main(['-xrf'])
