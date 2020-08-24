# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from omnisound.src.note.adapter.note import MakeNoteConfig
import omnisound.src.note.adapter.foxdot_supercollider_note as foxdot_note
from omnisound.src.note.adapter.note import NoteValues
from omnisound.src.note.adapter.performance_attrs import PerformanceAttrs
from omnisound.src.container.note_sequence import NoteSequence

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


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=foxdot_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=foxdot_note.make_note,
                          get_pitch_for_key=foxdot_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_val_default_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_val_cast_map={})


def _note_sequence(mn=None, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(num_notes=NUM_NOTES, mn=mn)
    return note_sequence


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


def _setup_note_values():
    note_values = NoteValues(foxdot_note.ATTR_NAMES)
    note_values.delay = START
    note_values.dur = DUR
    note_values.amp = AMP
    note_values.degree = PITCH
    note_values.octave = float(OCTAVE)
    return note_values


def test_note(make_note_config):
    note = _note(mn=make_note_config)

    assert note.delay == START
    assert note.dur == DUR
    assert note.amp == AMP
    assert note.degree == PITCH

    note.delay += 1.0
    assert note.delay == START + 1.0
    note.dur += 1.0
    assert note.dur == DUR + 1.0
    note.amp += 1.0
    assert note.amp == AMP + 1.0
    note.degree += 1.0
    assert note.degree == PITCH + 1.0


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_attrs(make_note_config, start, duration, amplitude, pitch):
    attr_name_idx_map = {'delay': 0,
                         'dur': 1,
                         'amp': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_val_default_map = {
        'delay': start,
        'dur': duration,
        'amp': amplitude,
        'degree': pitch,
        'octave': float(OCTAVE),
    }
    note = _note(mn=make_note_config,
                 attr_name_idx_map=attr_name_idx_map,
                 attr_val_default_map=attr_val_default_map,
                 num_attributes=len(attr_name_idx_map))

    assert note.delay == start
    assert note.dur == duration
    assert note.amp == amplitude
    assert note.degree == pitch
    assert note.octave == OCTAVE


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_to_str(make_note_config, start, duration, amplitude, pitch):
    attr_name_idx_map = {'delay': 0,
                         'dur': 1,
                         'amp': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_val_default_map = {
        'delay': start,
        'dur': duration,
        'amp': amplitude,
        'degree': pitch,
        'octave': float(OCTAVE),
    }
    note = _note(mn=make_note_config,
                 attr_name_idx_map=attr_name_idx_map,
                 attr_val_default_map=attr_val_default_map,
                 num_attributes=len(attr_name_idx_map))
    note.scale = SCALE

    assert f'delay: {start} dur: {duration} amp: {float(amplitude)} degree: {pitch} octave: {OCTAVE} scale: {SCALE}' \
        == str(note)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_foxdot_note_attrs_fluent(make_note_config, start, duration, amplitude, pitch):
    # Add multiple aliased property names for note attributes
    attr_name_idx_map = {'delay': 0,
                         'dur': 1,
                         'amp': 2,
                         'degree': 3,
                         'octave': 4}
    # Test assigning default values to each note created in the underlying NoteSequence
    attr_val_default_map = {
        'delay': 0.0,
        'dur': 0.0,
        'amp': 0.0,
        'degree': 0.0,
        'octave': float(0),
    }
    note = _note(mn=make_note_config,
                 attr_name_idx_map=attr_name_idx_map,
                 attr_val_default_map=attr_val_default_map,
                 num_attributes=len(attr_name_idx_map))

    assert note.delay != start
    assert note.dur != duration
    assert note.amp != amplitude
    assert note.degree != pitch
    assert note.octave != OCTAVE

    note.DE(start).DU(duration).A(amplitude).DG(pitch).O(float(OCTAVE))

    assert note.delay == start
    assert note.dur == duration
    assert note.amp == amplitude
    assert note.degree == pitch
    assert note.octave == OCTAVE


def test_note_values(make_note_config):
    note_values = _setup_note_values()
    make_note_config.attr_val_default_map = note_values.as_dict()
    note = _note(mn=make_note_config)

    # noinspection PyTypeChecker
    assert note.delay == START
    assert note.dur == DUR
    assert note.amp == AMP
    assert note.degree == PITCH
    assert note.octave == float(OCTAVE)


if __name__ == '__main__':
    pytest.main(['-xrf'])
