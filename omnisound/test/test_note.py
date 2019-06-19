# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import Any, List

from numpy import array
import pytest
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as fd_sc_synth

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.adapters.foxdot_supercollider_note import \
    FIELDS as FOXDOT_FIELDS
from omnisound.note.adapters.foxdot_supercollider_note import \
    FoxDotSupercolliderNote
from omnisound.note.adapters.midi_note import FIELDS as MIDI_FIELDS
from omnisound.note.adapters.midi_note import MidiInstrument, MidiNote
from omnisound.note.adapters.note import Note, NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.adapters.rest_note import RestNote

INSTRUMENT = 1
FOX_DOT_INSTRUMENT = fd_sc_synth
MIDI_INSTRUMENT = MidiInstrument.Accordion
STARTS: List[float] = [0.0, 0.5, 1.0]
INT_STARTS: List[int] = [0, 5, 10]
START = STARTS[0]
INT_START = INT_STARTS[0]
DURS: List[float] = [0.0, 1.0, 2.5]
DUR = DURS[0]
AMPS: List[float] = [0.0, 1.0, 2.0]
AMP = AMPS[0]
PITCHES: List[float] = [0.0, 0.5, 1.0]
PITCH = PITCHES[0]

ATTRS = array([float(INSTRUMENT), START, DUR, AMP, PITCH])
ATTR_NAME_IDX_MAP = deepcopy(Note.BASE_NAME_INDEX_MAP)
ATTR_NAME_IDX_MAP.update({attr_name: i for i, attr_name in enumerate(CSoundNote.ATTR_NAMES)})
ATTR_VALS_MAP = {attr_name: ATTRS[i] for i, attr_name in enumerate(CSoundNote.ATTR_NAMES)}
ROW_NUM = 0
NOTE = CSoundNote(attrs=ATTRS,
                  attr_name_idx_map=ATTR_NAME_IDX_MAP,
                  attr_vals_map=ATTR_VALS_MAP,
                  row_num=ROW_NUM)

PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

SCALE = 'chromatic'
OCTAVE = 4


def _setup_note_values(note_type: Any):
    note_values = None
    if note_type == CSoundNote:
        note_values = NoteValues(CSoundNote.ATTR_NAMES)
        note_values.instrument = INSTRUMENT
        note_values.start = START
        note_values.duration = DUR
        note_values.amplitude = AMP
        note_values.pitch = PITCH
    # if note_type == MidiNote:
    #     note_values = NoteValues(MIDI_FIELDS)
    #     note_values.instrument = MIDI_INSTRUMENT
    #     note_values.time = START
    #     note_values.duration = DUR
    #     note_values.velocity = int(AMP)
    #     note_values.pitch = int(PITCH)
    # if note_type == FoxDotSupercolliderNote:
    #     note_values = NoteValues(FOXDOT_FIELDS)
    #     note_values.synth_def = FOX_DOT_INSTRUMENT
    #     note_values.delay = INT_START
    #     note_values.dur = DUR
    #     note_values.amp = float(AMP)
    #     note_values.degree = PITCH
    return note_values


def test_note():
    assert NOTE.instrument == INSTRUMENT
    assert NOTE.start == START
    assert NOTE.amplitude == AMP
    assert NOTE.duration == DUR
    assert NOTE.pitch == PITCH


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs(start, duration, amplitude, pitch):
    # Add an additional non-core dynamically added attribute to verify correct ordering of attrs and str()
    func_table = 100

    attrs = array([float(INSTRUMENT), start, duration, amplitude, pitch, func_table])
    attr_name_idx_map = deepcopy(ATTR_NAME_IDX_MAP)
    attr_name_idx_map['func_table'] = 5

    note = CSoundNote(attrs=attrs,
                      attr_name_idx_map=attr_name_idx_map,
                      attr_vals_map=ATTR_VALS_MAP,
                      row_num=ROW_NUM)

    # TEMP DEBUG
    import pdb; pdb.set_trace()

    assert note.instrument == INSTRUMENT
    assert note.start == note.s == start
    assert note.duration == note.d == duration
    assert note.amplitude == note.a == amplitude
    assert note.pitch == note.p == pitch
    assert note.func_table == func_table

    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {round(amplitude, 2)} {round(pitch, 2)} {func_table}' == \
           str(note)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs_fluent(start, duration, amplitude, pitch):
    some_other_value = 100.0
    note = CSoundNote(instrument=int(some_other_value), start=some_other_value, duration=some_other_value,
                      amplitude=some_other_value, pitch=some_other_value)

    note.I(INSTRUMENT).S(start).D(duration).A(amplitude).P(pitch)

    assert note.instrument == INSTRUMENT
    assert note.start == note.s == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.pitch == note.p == pitch
    # Add an additional non-core dynamically added attribute to verify correct ordering of attrs and str()
    func_table = 100
    note.add_attr('func_table', func_table, to_str=lambda x: str(int(x)))
    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {round(amplitude, 2)} {round(pitch, 2)} {func_table}' == \
           str(note)


def test_csound_note_pitch_precision():
    note = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR,
                      amplitude=AMP, pitch=PITCH)
    assert note.pitch_precision == CSoundNote.SCALE_PITCH_PRECISION
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {round(AMP, 2)} {round(PITCH, 2)}' == str(note)

    note.set_scale_pitch_precision()
    assert note.pitch_precision == CSoundNote.DEFAULT_PITCH_PRECISION  # 5
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {round(AMP, 5)} {round(PITCH, 5)}' == str(note)


# @pytest.mark.parametrize('degree', PITCHES)
# @pytest.mark.parametrize('amp', AMPS)
# @pytest.mark.parametrize('dur', DURS)
# @pytest.mark.parametrize('delay', INT_STARTS)
# def test_foxdot_supercollider_note_attrs(delay, dur, amp, degree):
#     synth_def = fd_sc_synth
#     octave = OCTAVE
#     scale = SCALE
#     note = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
#                                    amp=float(amp), degree=degree, octave=octave, scale=scale)
#     assert note.delay == note.start == note.s == delay
#     assert note.dur == note.d == dur
#     assert note.amp == note.a == float(amp)
#     assert note.degree == note.pitch == note.p == degree
#     assert note.octave == octave
#     assert note.scale == scale
#     assert f'name: Note delay: {delay} dur: {dur} amp: {float(amp)} degree: {degree} octave: {octave} scale: {scale}' \
#            == str(note)
#
#     with pytest.raises(ValueError):
#         scale = 'NOT_A_VALID_SCALE'
#         _ = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
#                                     amp=amp, degree=degree, octave=octave, scale=scale)
#
#     scale = SCALE
#     note = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
#                                    amp=float(amp), degree=degree, octave=octave, scale=scale)
#     note.s = delay + 1
#     note.d = dur + 1
#     note.a = float(amp + 1)
#     note.p = degree + 1
#     assert note.s == delay + 1
#     assert note.d == dur + 1
#     assert note.a == amp + 1
#     assert note.p == degree + 1


# @pytest.mark.parametrize('pitch', PITCHES)
# @pytest.mark.parametrize('velocity', AMPS)
# @pytest.mark.parametrize('duration', DURS)
# @pytest.mark.parametrize('time', STARTS)
# def test_midi_note_attrs(time, duration, velocity, pitch):
#     note = MidiNote(instrument=INSTRUMENT, time=time, duration=duration,
#                     velocity=int(velocity), pitch=int(pitch))
#     assert note.time == note.start == note.s == time
#     assert note.duration == note.dur == note.d == duration
#     assert note.velocity == note.amp == note.a == int(velocity)
#     assert note.pitch == note.p == int(pitch)
#     expected_str_note = (f'name: Note instrument: {INSTRUMENT} time: {time} duration: {duration} '
#                          f'velocity: {int(velocity)} pitch: {int(pitch)} channel: 1')
#     assert expected_str_note == str(note)
#
#     note = MidiNote(instrument=INSTRUMENT, time=time, duration=duration,
#                     velocity=int(velocity), pitch=int(pitch))
#     new_pitch = int(pitch + 1.0)
#     note.s = time + 1
#     note.d = duration + 1
#     note.a = int(velocity) + 1
#     note.p = new_pitch
#     assert note.s == time + 1
#     assert note.d == duration + 1
#     assert note.a == velocity + 1
#     assert note.p == new_pitch


def test_note_values():
    note_config = _setup_note_values(CSoundNote)
    note = CSoundNote(**note_config.as_dict())
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_values(CSoundNote)
    note_config_list = note_config.as_list()
    note = CSoundNote(*note_config_list)
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_values(CSoundNote)
    # Can return a numpy array of the Note to manipulate using numpy
    note_config_array = note_config.as_array()
    # Can convert the array to a Python list to pass with * like any other list
    note_config_list = note_config_array.tolist()
    # Must handle any validation of types required by the underlying note type *after* the conversion, because
    # Python list can have values of any type, but numpy array is a C-style fixed-type collection that stores
    # all values as numpy.float64
    # Instrument is validated as an int in CSoundNote
    note_config_list[0] = int(note_config_list[0])
    note = CSoundNote(*note_config_list)
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    # note_config = _setup_note_config(MidiNote)
    # note = MidiNote(**note_config.as_dict())
    # assert note.instrument == MIDI_INSTRUMENT.value
    # assert note.time == START
    # assert note.velocity == AMP
    # assert note.duration == DUR
    # assert note.pitch == PITCH
    #
    # note_config = _setup_note_config(MidiNote)
    # note = MidiNote(*note_config.as_list())
    # assert note.instrument == MIDI_INSTRUMENT.value
    # assert note.time == START
    # assert note.velocity == AMP
    # assert note.duration == DUR
    # assert note.pitch == PITCH
    #
    # note_config = _setup_note_config(FoxDotSupercolliderNote)
    # note = FoxDotSupercolliderNote(**note_config.as_dict())
    # assert note.synth_def == FOX_DOT_INSTRUMENT
    # assert note.degree == START
    # assert note.amp == AMP
    # assert note.delay == DUR
    # assert note.pitch == PITCH
    #
    # note_config = _setup_note_config(FoxDotSupercolliderNote)
    # note = FoxDotSupercolliderNote(*note_config.as_list())
    # assert note.synth_def == FOX_DOT_INSTRUMENT
    # assert note.degree == START
    # assert note.amp == AMP
    # assert note.delay == DUR
    # assert note.pitch == PITCH


# def test_rest():
#     rest_note = RestNote(instrument=INSTRUMENT, start=START, dur=DUR, pitch=PITCH)
#     assert rest_note.amp == 0.0


if __name__ == '__main__':
    pytest.main(['-xrf'])
