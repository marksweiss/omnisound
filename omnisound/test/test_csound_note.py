# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import List

import pytest

import omnisound.note.adapters.csound_note as csound_note
from omnisound.note.adapters.note import AMP_I, DUR_I, NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence

INSTRUMENT = 1
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


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
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


def _setup_note_values():
    note_values = NoteValues(csound_note.ATTR_NAMES)
    note_values.instrument = INSTRUMENT
    note_values.start = START
    note_values.duration = DUR
    note_values.amplitude = AMP
    note_values.pitch = PITCH
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


if __name__ == '__main__':
    pytest.main(['-xrf'])
