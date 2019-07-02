# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import Any, List

from numpy import array
import pytest
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as fd_sc_synth

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.adapters.foxdot_supercollider_note import FoxDotSupercolliderNote
from omnisound.note.adapters.midi_note import MidiInstrument, MidiNote
from omnisound.note.adapters.note import AMP_I, DUR_I, NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.adapters.rest_note import RestNote
from omnisound.note.containers.note_sequence import NoteSequence

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
ATTR_NAME_IDX_MAP = {'instrument': 0, 'start': 1, 'dur': 2, 'amp': 3, 'pitch': 4}
NOTE_SEQUENCE_NUM = 0

PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

SCALE = 'chromatic'
OCTAVE = 4

NOTE_CLS = CSoundNote
ATTR_NAME_IDX_MAP = NOTE_CLS.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(ATTR_VALS)


def _note_sequence():
    note_sequence = NoteSequence(note_cls=NOTE_CLS,
                                 num_notes=NUM_NOTES,
                                 num_attributes=NUM_ATTRIBUTES,
                                 attr_name_idx_map=ATTR_NAME_IDX_MAP)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _setup_note_values(note_type: Any):
    note_values = None
    if note_type == CSoundNote:
        note_values = NoteValues(CSoundNote.ATTR_NAMES)
        note_values.instrument = INSTRUMENT
        note_values.start = START
        note_values.duration = DUR
        note_values.amplitude = AMP
        note_values.pitch = PITCH
    if note_type == MidiNote:
        note_values = NoteValues(MidiNote.ATTR_NAMES)
        note_values.instrument = MIDI_INSTRUMENT.value
        note_values.time = START
        note_values.duration = DUR
        note_values.velocity = AMP
        note_values.pitch = PITCH
    if note_type == FoxDotSupercolliderNote:
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
    attr_name_idx_map['amplitude'] = AMP_I
    attr_name_idx_map['duration'] = DUR_I

    note = CSoundNote(attr_vals=ATTRS, attr_name_idx_map=attr_name_idx_map,
                      seq_idx=NOTE_SEQUENCE_NUM)

    assert note.a == AMP
    assert note.amplitude == AMP

    # note.instrument is returned cast to int, even though all values are stored
    # in the note.attrs as float64, because CSoundNote configures the underlying note to cast the return of getattr()
    assert note.instrument == INSTRUMENT
    assert type(note.instrument) == type(INSTRUMENT) == int

    assert note.start == START
    assert note.dur == DUR
    assert note.duration == DUR
    assert note.amp == int(AMP)
    assert note.pitch == PITCH

    note.instrument += 1.0
    assert note.instrument == INSTRUMENT + 1.0
    note.start += 1.0
    assert note.start == START + 1.0
    note.dur += 1.0
    assert note.dur == DUR + 1.0
    note.amp += 1.0
    assert note.amp == int(AMP + 1.0)
    note.pitch += 1.0
    assert note.pitch == PITCH + 1.0


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs(start, duration, amplitude, pitch):
    # Add an additional non-core dynamically added attribute to verify correct ordering of attrs and str()
    # Note that in real usage only a Generator determines the attributes of a Note because it constructs
    # the underlying storage for all Notes in a NoteSequence. But this shows that the Note interface
    # supports notes with new non-standard attributes, which can be retrieved by name, included in str(note)
    # and can be cast to an arbitrary return type.
    func_table = 100
    attr_vals = array([float(INSTRUMENT), start, duration, amplitude, pitch, func_table])
    attr_name_idx_map = {'i': 0, 'instrument': 0,
                         's': 1, 'start': 1,
                         'd': 2, 'dur': 2, 'duration': 2,
                         'a': 3, 'amp': 3, 'amplitude': 3,
                         'p': 4, 'pitch': 4,
                         'func_table': 5}
    attr_get_type_cast_map = {'func_table': int}
    note = CSoundNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map,
                      attr_get_type_cast_map=attr_get_type_cast_map,
                      seq_idx=NOTE_SEQUENCE_NUM)

    assert note.instrument == INSTRUMENT
    assert note.start == note.s == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.pitch == note.p == pitch
    # Assert that non-core dynamically added attribute (which in real use would only be added by a Generator
    #  and never directly by an end user) has the expected data type
    assert note.func_table == func_table
    assert type(note.func_table) == type(func_table) == int

    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {round(amplitude, 2)} {round(pitch, 2)} {func_table}' == \
        str(note)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs_fluent(start, duration, amplitude, pitch):
    some_other_val = 100.0
    attr_vals = array([float(INSTRUMENT), some_other_val, some_other_val, some_other_val, some_other_val])
    attr_name_idx_map = {'i': 0, 'instrument': 0,
                         's': 1, 'start': 1,
                         'd': 2, 'dur': 2, 'duration': 2,
                         'a': 3, 'amp': 3, 'amplitude': 3,
                         'p': 4, 'pitch': 4}
    note = CSoundNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_NUM)
    note.I(INSTRUMENT).S(start).D(duration).A(amplitude).P(pitch)

    assert note.instrument == INSTRUMENT
    assert note.start == note.s == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.pitch == note.p == pitch
    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {round(amplitude, 2)} {round(pitch, 2)}' == \
           str(note)


def test_csound_note_pitch_precision():
    attr_vals = array([float(INSTRUMENT), START, DUR, AMP, PITCH])
    attr_name_idx_map = {'i': 0, 'instrument': 0,
                         's': 1, 'start': 1,
                         'd': 2, 'dur': 2, 'duration': 2,
                         'a': 3, 'amp': 3, 'amplitude': 3,
                         'p': 4, 'pitch': 4}
    note = CSoundNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_NUM)
    assert note.pitch_precision == CSoundNote.SCALE_PITCH_PRECISION  # == 2
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {round(AMP, 2)} {round(PITCH, 2)}' == str(note)

    note.set_scale_pitch_precision()
    assert note.pitch_precision == CSoundNote.DEFAULT_PITCH_PRECISION  # == 5
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {round(AMP, 5)} {round(PITCH, 5)}' == str(note)


@pytest.mark.parametrize('degree', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('delay', INT_STARTS)
def test_foxdot_supercollider_note_attrs(delay, dur, amp, degree):
    synth_def = fd_sc_synth
    octave = OCTAVE
    scale = SCALE
    attr_vals = array([delay, dur, amp, degree, OCTAVE])
    attr_name_idx_map = {'start': 0, 'delay': 0,
                         'dur': 1,
                         'amp': 2,
                         'pitch': 3, 'degree': 3,
                         'octave': 4}
    note = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_NUM,
                                   synth_def=synth_def, scale=SCALE)

    assert note.delay == note.start == delay
    assert type(note.delay) == int
    assert type(note.start) == int
    assert note.dur == dur
    assert note.amp == amp
    assert note.degree == note.pitch == degree
    assert note.octave == octave
    assert type(note.octave) == int
    assert note.synth_def == synth_def
    assert note.scale == scale
    assert f'delay: {delay} dur: {dur} amp: {float(amp)} degree: {degree} octave: {octave} scale: {scale}' \
           == str(note)

    with pytest.raises(ValueError):
        scale = 'NOT_A_VALID_SCALE'
        _ = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_NUM,
                                    synth_def=synth_def, scale=scale)

    note.delay += 1.0
    assert note.delay == int(delay + 1.0)
    assert type(note.delay) == int
    assert note.start == int(delay + 1.0)
    assert type(note.start) == int
    note.dur += 1.0
    assert note.dur == dur + 1.0
    note.amp += 1.0
    assert note.amp == amp + 1.0
    note.degree += 1.0
    assert note.degree == degree + 1.0


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('velocity', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('time', STARTS)
def test_midi_note_attrs(time, duration, velocity, pitch):
    channel = 2
    attr_vals = array([INSTRUMENT, time, duration, velocity, pitch])
    attr_name_idx_map = {'instrument': 0,
                         'start': 1, 'time': 1,
                         'dur': 2, 'duration': 2,
                         'velocity': 3,
                         'pitch': 4}
    note = MidiNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=NOTE_SEQUENCE_NUM,
                    channel=channel)

    assert note.time == note.start == time
    assert note.duration == note.dur == duration
    assert note.velocity == int(velocity)
    assert type(note.velocity) == int
    assert note.pitch == int(pitch)
    assert type(note.pitch) == int
    expected_str_note = (f'instrument: {INSTRUMENT} time: {time} duration: {duration} '
                         f'velocity: {int(velocity)} pitch: {int(pitch)} channel: {channel}')
    assert expected_str_note == str(note)

    note.time += 1.0
    assert note.time == time + 1.0
    assert note.start == time + 1.0
    note.dur += 1.0
    assert note.dur == duration + 1.0
    assert note.duration == duration + 1.0
    note.velocity += 1.0
    assert note.velocity == int(velocity + 1.0)
    assert type(note.velocity) == int
    note.pitch += 1.0
    assert note.pitch == int(pitch + 1.0)
    assert type(note.pitch) == int


def test_note_values():
    attr_vals = array([float(INSTRUMENT + 1.0), START + 1.0, DUR + 1.0, AMP + 1.0, PITCH + 1.0])
    # The field key names must match the key names in note_values, passed as attr_vals_map
    # The latter come from Note.attr_names, e.g. CSoundNote.attr_names
    attr_name_idx_map = {'instrument': 0,
                         'start': 1,
                         'duration': 2,
                         'amplitude': 3,
                         'pitch': 4}
    note_values = _setup_note_values(CSoundNote)
    note = CSoundNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map,
                      attr_vals_defaults_map=note_values.as_dict(),
                      seq_idx=NOTE_SEQUENCE_NUM)
    # Validate that the values match note_values, not the different values passed to __init__ in attrs
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    time = START
    duration = DUR
    velocity = AMP
    attr_vals = array([INSTRUMENT, time + 1.0, duration + 1.0, velocity + 1.0, PITCH + 1.0])
    attr_name_idx_map = {'instrument': 0,
                         'time': 1,
                         'duration': 2,
                         'velocity': 3,
                         'pitch': 4}
    note_values = _setup_note_values(MidiNote)
    note = MidiNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, attr_vals_defaults_map=note_values.as_dict(),
                    seq_idx=NOTE_SEQUENCE_NUM)
    assert note.instrument == MIDI_INSTRUMENT.value
    assert note.time == START
    assert note.velocity == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    synth_def = fd_sc_synth
    delay = START
    dur = DUR
    amp = AMP
    degree = PITCH
    attr_vals = array([delay + 1.0, dur + 1.0, amp + 1.0, degree + 1.0, float(OCTAVE)])
    attr_name_idx_map = {'delay': 0,
                         'dur': 1,
                         'amp': 2,
                         'degree': 3,
                         'octave': 4}
    note_values = _setup_note_values(FoxDotSupercolliderNote)
    note = FoxDotSupercolliderNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map,
                                   attr_vals_defaults_map=note_values.as_dict(),
                                   seq_idx=NOTE_SEQUENCE_NUM,
                                   synth_def=synth_def, scale=SCALE)
    assert note.synth_def == FOX_DOT_INSTRUMENT
    assert note.degree == START
    assert note.amp == AMP
    assert note.delay == DUR
    assert note.octave == OCTAVE


def test_rest():
    amp = RestNote.REST_AMP + 1.0
    attr_vals = array([float(INSTRUMENT), START, DUR, amp, PITCH])
    attr_name_idx_map = {'instrument': 0, 'start': 1, 'dur': 2, 'amp': 3, 'pitch': 4}
    rest_note = RestNote(attr_vals=attr_vals, attr_name_idx_map=attr_name_idx_map, seq_idx=0)
    assert rest_note.amp != amp
    assert rest_note.amp == RestNote.REST_AMP


if __name__ == '__main__':
    pytest.main(['-xrf'])
