# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import List

import pytest

import omnisound.note.adapters.foxdot_supercollider_note as foxdot_note
from omnisound.note.adapters.note import NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence

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

SCALE = 'chromatic'
OCTAVE = 4

ATTR_VALS_DEFAULTS_MAP = {'delay': START,
                          'dur': DUR,
                          'amp': AMP,
                          'degree': PITCH,
                          'octave': float(OCTAVE)}
NOTE_SEQUENCE_IDX = 0

# TODO TEST PERFORMANCE ATTRS
PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

NOTE_CLS_NAME = foxdot_note.CLASS_NAME
ATTR_NAME_IDX_MAP = foxdot_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(foxdot_note.ATTR_NAMES)


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes  or NUM_ATTRIBUTES
    note_sequence = NoteSequence(make_note=foxdot_note.make_note,
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
    return foxdot_note.make_note(
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
    note_values = NoteValues(foxdot_note.ATTR_NAMES)
    note_values.delay = START
    note_values.dur = DUR
    note_values.amp = AMP
    note_values.degree = PITCH
    note_values.octave = float(OCTAVE)
    return note_values


def test_note():
    # Test adding a non-standard mapping
    attr_name_idx_map = deepcopy(ATTR_NAME_IDX_MAP)
    attr_name_idx_map['a'] = ATTR_NAME_IDX_MAP['amp']
    attr_name_idx_map['duration'] = ATTR_NAME_IDX_MAP['dur']
    note = _note(attr_name_idx_map=attr_name_idx_map)

    assert note.delay == START
    assert note.duration == DUR
    assert note.dur == DUR
    assert note.amp == AMP
    assert note.a == AMP
    assert note.degree == PITCH

    note.delay += 1.0
    assert note.delay == START + 1.0
    note.duration += 1.0
    assert note.duration == DUR + 1.0
    assert note.dur == DUR + 1.0
    note.amp += 1.0
    assert note.amp == AMP + 1.0
    assert note.a == AMP + 1.0
    note.degree += 1.0
    assert note.degree == PITCH + 1.0


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_attrs(start, duration, amplitude, pitch):
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'delay': 0,
                         'd': 1, 'dur': 1, 'duration': 1,
                         'a': 2, 'amp': 2, 'amplitude': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_vals_defaults_map = {
        'delay': start,
        'dur': duration,
        'amp': amplitude,
        'degree': pitch,
        'octave': float(OCTAVE),
    }
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 num_attributes=len(attr_vals_defaults_map))

    assert note.delay == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.degree == pitch
    assert note.octave == OCTAVE


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_to_str(start, duration, amplitude, pitch):
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'delay': 0,
                         'd': 1, 'dur': 1, 'duration': 1,
                         'a': 2, 'amp': 2, 'amplitude': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_vals_defaults_map = {
        'delay': start,
        'dur': duration,
        'amp': amplitude,
        'degree': pitch,
        'octave': float(OCTAVE),
    }
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 num_attributes=len(attr_vals_defaults_map))
    note.scale = SCALE

    assert f'delay: {start} dur: {duration} amp: {float(amplitude)} degree: {pitch} octave: {OCTAVE} scale: {SCALE}' \
        == str(note)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_attrs_fluent(start, duration, amplitude, pitch):
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'delay': 0,
                         'd': 1, 'dur': 1, 'duration': 1,
                         'a': 2, 'amp': 2, 'amplitude': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_vals_defaults_map = {
        'delay': 0.0,
        'dur': 0.0,
        'amp': 0.0,
        'degree': 0.0,
        'octave': float(0),
    }
    note = _note(attr_name_idx_map=attr_name_idx_map,
                 attr_vals_defaults_map=attr_vals_defaults_map,
                 num_attributes=len(attr_vals_defaults_map))

    assert note.delay != start
    assert note.duration == note.dur == note.d != duration
    assert note.amplitude == note.amp == note.a != amplitude
    assert note.degree != pitch
    assert note.octave != OCTAVE

    note.DE(start).DU(duration).A(amplitude).DG(pitch).O(float(OCTAVE))

    assert note.delay == start
    assert note.duration == note.dur == note.d == duration
    assert note.amplitude == note.amp == note.a == amplitude
    assert note.degree == pitch
    assert note.octave == OCTAVE


def test_note_values():
    note_values = _setup_note_values()
    note = _note(attr_vals_defaults_map=note_values.as_dict())

    # noinspection PyTypeChecker
    assert note.delay == START
    assert note.dur == DUR
    assert note.amp == AMP
    assert note.degree == PITCH
    assert note.octave == float(OCTAVE)


if __name__ == '__main__':
    pytest.main(['-xrf'])
