# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import Any, List

from numpy import array
import pytest
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as fd_sc_synth

import omnisound.note.adapters.csound_note as csound_note
from omnisound.note.adapters.foxdot_supercollider_note import FoxDotSupercolliderNote
from omnisound.note.adapters.midi_note import MidiInstrument, MidiNote
from omnisound.note.adapters.note import AMP_I, DUR_I, NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.adapters.rest_note import RestNote
from omnisound.note.containers.note_sequence import NoteSequence

INSTRUMENT = 1
FOX_DOT_INSTRUMENT = fd_sc_synth
MIDI_INSTRUMENT = MidiInstrument.Accordion
STARTS: List[float] = [1.0, 0.5, 1.5]
INT_STARTS: List[int] = [1, 5, 10]
START = STARTS[0]
INT_START = INT_STARTS[0]
DURS: List[float] = [1.0, 2.0, 2.5]
DUR = DURS[0]
AMPS: List[float] = [1.0, 2.0, 3.0]
AMP = AMPS[0]
PITCHES: List[float] = [1.0, 1.5, 2.0]
PITCH = PITCHES[0]

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0

PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

SCALE = 'chromatic'
OCTAVE = 4

NOTE_CLS_NAME = csound_note.CLASS_NAME
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


def _note_sequence(attr_name_idx_map = None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes  or NUM_ATTRIBUTES
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


def _setup_note_values(note_cls_name: str):
    note_values = None
    if note_cls_name == 'CSoundNote':
        note_values = NoteValues(csound_note.ATTR_NAMES)
        note_values.instrument = INSTRUMENT
        note_values.start = START
        note_values.duration = DUR
        note_values.amplitude = AMP
        note_values.pitch = PITCH
    if note_cls_name == 'MidiNote':
        note_values = NoteValues(MidiNote.ATTR_NAMES)
        note_values.instrument = MIDI_INSTRUMENT.value
        note_values.time = START
        note_values.duration = DUR
        note_values.velocity = AMP
        note_values.pitch = PITCH
    if note_cls_name == 'FoxDotSupercolliderNote':
        note_values = NoteValues(FoxDotSupercolliderNote.ATTR_NAMES)
        note_values.delay = INT_START
        note_values.dur = DUR
        note_values.amp = AMP
        note_values.degree = PITCH
        note_values.octave = float(OCTAVE)
    return note_values


def test_note():
    # Test adding a non-standard mapping
    attr_name_idx_map = deepcopy(ATTR_NAME_IDX_MAP)
    attr_name_idx_map['a'] = AMP_I
    attr_name_idx_map['dur'] = DUR_I
    note = _note(attr_name_idx_map=attr_name_idx_map)

    # note.instrument is returned cast to int, even though all values are stored
    # in the note.attrs as float64, because CSoundNote configures the underlying note to cast the return of getattr()
    assert note.instrument == INSTRUMENT
    assert type(note.instrument) == type(INSTRUMENT) == int

    assert note.start == START
    assert note.duration == DUR
    assert note.dur == DUR
    assert note.amplitude == AMP
    assert note.a == AMP
    assert note.pitch == PITCH

    note.instrument += 1.0
    assert note.instrument == int(INSTRUMENT + 1.0)
    note.start += 1.0
    assert note.start == START + 1.0
    note.duration += 1.0
    assert note.duration == DUR + 1.0
    assert note.dur == DUR + 1.0
    note.amplitude += 1.0
    assert note.amplitude == AMP + 1.0
    assert note.a == AMP + 1.0
    note.pitch += 1.0
    assert note.pitch == PITCH + 1.0


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs(start, duration, amplitude, pitch):
    # Add an additional non-core dynamically added attribute to verify correct ordering of attrs and str()
    func_table = 100
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'i': 0, 'instrument': 0,
                         's': 1, 'start': 1,
                         'd': 2, 'dur': 2, 'duration': 2,
                         'a': 3, 'amp': 3, 'amplitude': 3,
                         'p': 4, 'pitch': 4,
                         'func_table': 5}
    # Test using a custom cast function for an attribute, a custom attribute
    attr_get_type_cast_map = {'func_table': int}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_vals_defaults_map = {
        'instrument': float(INSTRUMENT),
        'start': start,
        'duration': duration,
        'amplitude': amplitude,
        'pitch': pitch,
        'func_table': float(func_table),
    }
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 attr_get_type_cast_map=attr_get_type_cast_map,
                 num_attributes=len(attr_vals_defaults_map))

    assert note.instrument == note.i == int(INSTRUMENT)
    assert type(note.instrument) == int
    assert note.start == note.s == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.pitch == note.p == pitch
    # Assert that non-core dynamically added attribute (which in real use would only be added by a Generator
    #  and never directly by an end user) has the expected data type
    assert note.func_table == func_table
    assert type(note.func_table) == type(func_table) == int


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_to_str(start, duration, amplitude, pitch):
    func_table = 100
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'instrument': 0,
                         'start': 1,
                         'duration': 2,
                         'amplitude': 3,
                         'pitch': 4,
                         'func_table': 5}
    # Test using a custom cast function for an attribute, a custom attribute
    attr_get_type_cast_map = {'func_table': int}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_vals_defaults_map = {
        'instrument': float(INSTRUMENT),
        'start': start,
        'duration': duration,
        'amplitude': amplitude,
        'pitch': pitch,
        'func_table': float(func_table),
    }
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 attr_get_type_cast_map=attr_get_type_cast_map,
                 num_attributes=len(attr_vals_defaults_map))
    # Have to manually add the string formatter for additional custom note attributes
    note.set_attr_str_formatter('func_table', lambda x: str(x))

    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {round(amplitude, 2)} {round(pitch, 2)} {func_table}' == \
        str(note)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs_fluent(start, duration, amplitude, pitch):
    # Add an additional non-core dynamically added attribute to verify correct ordering of attrs and str()
    func_table = 100
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'i': 0, 'instrument': 0,
                         's': 1, 'start': 1,
                         'd': 2, 'dur': 2, 'duration': 2,
                         'a': 3, 'amp': 3, 'amplitude': 3,
                         'p': 4, 'pitch': 4,
                         'func_table': 5}
    # Test using a custom cast function for an attribute, a custom attribute
    attr_get_type_cast_map = {'func_table': int}
    # Set the note value to not equal the values passed in to the test
    attr_vals_defaults_map = {
        'instrument': float(INSTRUMENT + 1),
        'start': 0.0,
        'duration': 0.0,
        'amplitude': 0.0,
        'pitch': 0.0,
        'func_table': float(func_table),
    }
    # Don't pass in attr_vals_defaults_map, so not creating a Note with the values passed in to each test
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_get_type_cast_map=attr_get_type_cast_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 num_attributes=len(attr_vals_defaults_map))

    # Assert the note does not have the expected attr values
    assert note.start == note.s != start
    assert note.duration == note.dur == note.d != duration
    assert note.amplitude == note.amp == note.a != amplitude
    assert note.pitch == note.p != pitch
    # Then use the fluent accessors with chained syntax to assign the values passed in to this test
    note.I(INSTRUMENT).S(start).D(duration).A(amplitude).P(pitch)
    # Assert the note now has the expected attr values
    assert note.start == note.s == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.pitch == note.p == pitch


def test_csound_note_pitch_precision(note):
    assert note.pitch_precision == csound_note.DEFAULT_PITCH_PRECISION  # == 5
    note.set_scale_pitch_precision()
    assert note.pitch_precision == csound_note.SCALE_PITCH_PRECISION  # == 2


# @pytest.mark.parametrize('degree', PITCHES)
# @pytest.mark.parametrize('amp', AMPS)
# @pytest.mark.parametrize('dur', DURS)
# @pytest.mark.parametrize('delay', INT_STARTS)
# def test_foxdot_supercollider_note_attrs(delay, dur, amp, degree):
#     synth_def = fd_sc_synth
#     octave = OCTAVE
#     scale = SCALE
#     attr_vals = array([delay, dur, amp, degree, OCTAVE])
#     attr_name_idx_map = {'start': 0, 'delay': 0,
#                          'dur': 1,
#                          'amp': 2,
#                          'pitch': 3, 'degree': 3,
#                          'octave': 4}
#     note = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_IDX,
#                                    synth_def=synth_def, scale=SCALE)
#
#     assert note.delay == note.start == delay
#     assert type(note.delay) == int
#     assert type(note.start) == int
#     assert note.dur == dur
#     assert note.amp == amp
#     assert note.degree == note.pitch == degree
#     assert note.octave == octave
#     assert type(note.octave) == int
#     assert note.synth_def == synth_def
#     assert note.scale == scale
#     assert f'delay: {delay} dur: {dur} amp: {float(amp)} degree: {degree} octave: {octave} scale: {scale}' \
#            == str(note)
#
#     with pytest.raises(ValueError):
#         scale = 'NOT_A_VALID_SCALE'
#         _ = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_IDX,
#                                     synth_def=synth_def, scale=scale)
#
#     note.delay += 1.0
#     assert note.delay == int(delay + 1.0)
#     assert type(note.delay) == int
#     assert note.start == int(delay + 1.0)
#     assert type(note.start) == int
#     note.dur += 1.0
#     assert note.dur == dur + 1.0
#     note.amp += 1.0
#     assert note.amp == amp + 1.0
#     note.degree += 1.0
#     assert note.degree == degree + 1.0
#
#
# @pytest.mark.parametrize('pitch', PITCHES)
# @pytest.mark.parametrize('velocity', AMPS)
# @pytest.mark.parametrize('duration', DURS)
# @pytest.mark.parametrize('time', STARTS)
# def test_midi_note_attrs(time, duration, velocity, pitch):
#     channel = 2
#     attr_vals = array([INSTRUMENT, time, duration, velocity, pitch])
#     attr_name_idx_map = {'instrument': 0,
#                          'start': 1, 'time': 1,
#                          'dur': 2, 'duration': 2,
#                          'velocity': 3,
#                          'pitch': 4}
#     note = MidiNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_IDX,
#                     channel=channel)
#
#     assert note.time == note.start == time
#     assert note.duration == note.dur == duration
#     assert note.velocity == int(velocity)
#     assert type(note.velocity) == int
#     assert note.pitch == int(pitch)
#     assert type(note.pitch) == int
#     expected_str_note = (f'instrument: {INSTRUMENT} time: {time} duration: {duration} '
#                          f'velocity: {int(velocity)} pitch: {int(pitch)} channel: {channel}')
#     assert expected_str_note == str(note)
#
#     note.time += 1.0
#     assert note.time == time + 1.0
#     assert note.start == time + 1.0
#     note.dur += 1.0
#     assert note.dur == duration + 1.0
#     assert note.duration == duration + 1.0
#     note.velocity += 1.0
#     assert note.velocity == int(velocity + 1.0)
#     assert type(note.velocity) == int
#     note.pitch += 1.0
#     assert note.pitch == int(pitch + 1.0)
#     assert type(note.pitch) == int
#
#
# def test_note_values():
#     attr_vals = array([float(INSTRUMENT + 1.0), START + 1.0, DUR + 1.0, AMP + 1.0, PITCH + 1.0])
#     # The field key names must match the key names in note_values, passed as attr_vals_map
#     # The latter come from Note.attr_names, e.g. CSoundNote.attr_names
#     attr_name_idx_map = {'instrument': 0,
#                          'start': 1,
#                          'duration': 2,
#                          'amplitude': 3,
#                          'pitch': 4}
#     note_values = _setup_note_values(CSoundNote)
#     note = CSoundNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map,
#                       attr_vals_defaults_map=note_values.as_dict(),
#                       seq_idx=NOTE_SEQUENCE_IDX)
#     # Validate that the values match note_values, not the different values passed to __init__ in attrs
#     assert note.instrument == INSTRUMENT
#     assert note.start == START
#     assert note.amplitude == AMP
#     assert note.duration == DUR
#     assert note.pitch == PITCH
#
#     time = START
#     duration = DUR
#     velocity = AMP
#     attr_vals = array([INSTRUMENT, time + 1.0, duration + 1.0, velocity + 1.0, PITCH + 1.0])
#     attr_name_idx_map = {'instrument': 0,
#                          'time': 1,
#                          'duration': 2,
#                          'velocity': 3,
#                          'pitch': 4}
#     note_values = _setup_note_values(MidiNote)
#     note = MidiNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, attr_vals_defaults_map=note_values.as_dict(),
#                     seq_idx=NOTE_SEQUENCE_IDX)
#     assert note.instrument == MIDI_INSTRUMENT.value
#     assert note.time == START
#     assert note.velocity == AMP
#     assert note.duration == DUR
#     assert note.pitch == PITCH
#
#     synth_def = fd_sc_synth
#     delay = START
#     dur = DUR
#     amp = AMP
#     degree = PITCH
#     attr_vals = array([delay + 1.0, dur + 1.0, amp + 1.0, degree + 1.0, float(OCTAVE)])
#     attr_name_idx_map = {'delay': 0,
#                          'dur': 1,
#                          'amp': 2,
#                          'degree': 3,
#                          'octave': 4}
#     note_values = _setup_note_values(FoxDotSupercolliderNote)
#     note = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map,
#                                    attr_vals_defaults_map=note_values.as_dict(),
#                                    seq_idx=NOTE_SEQUENCE_IDX,
#                                    synth_def=synth_def, scale=SCALE)
#     assert note.synth_def == FOX_DOT_INSTRUMENT
#     assert note.degree == START
#     assert note.amp == AMP
#     assert note.delay == DUR
#     assert note.octave == OCTAVE
#
#
# def test_rest():
#     amp = RestNote.REST_AMP + 1.0
#     attr_vals = array([float(INSTRUMENT), START, DUR, amp, PITCH])
#     attr_name_idx_map = {'instrument': 0, 'start': 1, 'dur': 2, 'amp': 3, 'pitch': 4}
#     rest_note = RestNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=0)
#     assert rest_note.amp != amp
#     assert rest_note.amp == RestNote.REST_AMP


if __name__ == '__main__':
    pytest.main(['-xrf'])
