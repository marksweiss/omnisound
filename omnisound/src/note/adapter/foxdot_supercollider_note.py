# Copyright 2018 Mark S. Weiss

from typing import Any, Mapping, Union

from numpy import ndarray

from omnisound.src.note.adapter.note import add_base_attr_name_indexes, getter, setter
from omnisound.src.generator.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                   MajorKey, MinorKey)
from omnisound.src.utils.validation_utils import validate_optional_sequence_of_type, validate_optional_type, \
    validate_sequence_of_type, validate_type

# TODO FIX TO USE DUMMY 0th INDEX FOR INSTRUMENT, SO CORE ATTRS ARE AT SAME INDEX`

CLASS_NAME = 'FoxdotSupercolliderNote'

ATTR_NAMES = ('delay', 'dur', 'amp', 'degree', 'octave')
ATTR_NAME_IDX_MAP = add_base_attr_name_indexes({attr_name: i for i, attr_name in enumerate(ATTR_NAMES)})

SCALES = {'aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian', 'dorian2',
          'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian', 'justMajor', 'justMinor',
          'locrian', 'locrianMajor', 'lydian', 'lydianMinor', 'major', 'majorPentatonic', 'melodicMajor',
          'melodicMinor', 'minor', 'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus',
          'romanianMinor', 'yu', 'zhi'}

PITCH_MAP = {
    MajorKey.C: 0,
    MajorKey.C_s: 1,
    MajorKey.D_f: 1,
    MajorKey.D: 2,
    MajorKey.E_f: 3,
    MajorKey.E: 4,
    MajorKey.F: 5,
    MajorKey.F_s: 6,
    MajorKey.G_f: 6,
    MajorKey.G: 7,
    MajorKey.A_f: 8,
    MajorKey.A: 9,
    MajorKey.B_f: 10,
    MajorKey.B: 11,
    MajorKey.C_f: 11,

    MinorKey.C: 0,
    MinorKey.C_S: 1,
    MinorKey.D: 1,
    MinorKey.D_S: 2,
    MinorKey.E_F: 3,
    MinorKey.E: 4,
    MinorKey.E_S: 5,
    MinorKey.F: 6,
    MinorKey.F_S: 6,
    MinorKey.G: 7,
    MinorKey.A_F: 8,
    MinorKey.A: 9,
    MinorKey.A_S: 10,
    MinorKey.B_F: 10,
    MinorKey.B: 11
}


def transpose(self, interval: int):
    """Foxdot pitches as ints are in range 1..12
    """
    validate_type('interval', interval, int)
    self.degree = int((self.degree + interval) % NUM_INTERVALS_IN_OCTAVE)


# noinspection PyUnusedLocal
def get_pitch_for_key(key: Union[MajorKey, MinorKey], octave: int) -> int:
    return PITCH_MAP[key]


def g_synth_def():
    def _g_synth_def(self) -> Any:
        return self.synth_def
    return _g_synth_def


def s_synth_def():
    def _s_synth_def(self, synth_def: Any) -> None:
        self.synth_def = synth_def
    return _s_synth_def


def g_instrument():
    def _g_instrument(self) -> Any:
        return self.synth_def
    return _g_instrument


def s_instrument():
    def _s_instrument(self, synth_def: Any) -> None:
        self.synth_def = synth_def
    return _s_instrument


def g_scale():
    def _g_scale(self) -> str:
        return self.scale
    return _g_scale


def s_scale():
    def _s_scale(self, scale: str) -> None:
        validate_type('scale', scale, str)
        self.scale = scale
    return _s_scale


# Fluent getters setters for core core note attributes
# noinspection PyPep8Naming
def S(self, attr_val: int):
    validate_type('attr_val', attr_val, int)
    self.note_attr_vals[self.attr_name_idx_map['instrument']] = attr_val
    return self


# noinspection PyPep8Naming
def DE(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['delay']] = attr_val
    return self


# noinspection PyPep8Naming
def DU(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['dur']] = attr_val
    return self


# noinspection PyPep8Naming
def A(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['amp']] = attr_val
    return self


# noinspection PyPep8Naming
def DG(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['degree']] = attr_val
    return self


# noinspection PyPep8Naming
def O(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['octave']] = attr_val
    return self


def eq(self, other: Any) -> bool:
    # noinspection PyProtectedMember
    return (self.octave is None and other.octave is None or
            self.octave == other.octave) and \
           (self.scale is None and other.scale is None or
            self.scale == other.scale) and \
           self._synth_def == other._synth_def and \
           self.delay == other.delay and \
           self.dur == other.dur and \
           self.amp == other.amp and \
           self.degree == other.degree


def to_str(self):
    attr_strs = [
        f'delay: {self.delay}',
        f'dur: {self.dur}',
        f'amp: {self.amp}',
        f'degree: {self.degree}']
    if hasattr(self, 'octave'):
        attr_strs.append(f'octave: {self.octave}')
    if hasattr(self, 'scale'):
        attr_strs.append(f'scale: {self.scale}')
    return ' '.join(attr_strs)


class FoxdotSupercolliderNoteMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)

        # Attributes assigned by the caller
        cls.note_attr_vals = None
        cls.attr_name_idx_map = None
        cls.attr_get_type_cast_map = None
        cls.performance_attrs = None

        # Custom CSound attributes
        cls.synth_def = None
        cls.scale = None

        return cls


def _make_cls(attr_name_idx_map):
    cls_bases = ()
    methods = {}
    # Create dynamically getters and setters for the note attributes for this instantiation of FoxdotSupercollider class
    for attr_name in attr_name_idx_map.keys():
        get_func = getter(attr_name)
        methods[f'g_{attr_name}'] = get_func
        set_func = setter(attr_name)
        methods[f's_{attr_name}'] = set_func
        methods[attr_name] = property(get_func, set_func)
    # Standard Note fluent accessor methods
    methods['S'] = S
    methods['DE'] = DE
    methods['DU'] = DU
    methods['A'] = A
    methods['DG'] = DG
    methods['O'] = O
    # Standard Note API
    methods['transpose'] = transpose
    # Supported dunder methods
    methods['__eq__'] = eq
    methods['__str__'] = to_str
    # Custom CSound methods
    # noinspection PyTypeChecker
    methods['synth_def'] = property(g_synth_def, s_synth_def)
    # noinspection PyTypeChecker
    methods['instrument'] = property(g_instrument, s_instrument)
    # noinspection PyTypeChecker
    methods['scale'] = property(g_scale, s_scale)

    cls = FoxdotSupercolliderNoteMeta(CLASS_NAME, cls_bases, methods)
    return cls


def make_note(note_attr_vals: ndarray,
              attr_name_idx_map: Mapping[str, int],
              attr_get_type_cast_map: Mapping[str, Any] = None):
    validate_type('note_attr_vals', note_attr_vals, ndarray)
    validate_type('attr_name_idx_map', attr_name_idx_map, Mapping)
    validate_sequence_of_type('attr_name_idx_map', attr_name_idx_map.keys(), str)
    validate_optional_type('attr_get_type_cast_map', attr_get_type_cast_map, Mapping)
    if attr_get_type_cast_map:
        validate_optional_sequence_of_type('attr_get_type_cast_map', attr_get_type_cast_map.keys(), str)

    cls = _make_cls(attr_name_idx_map)
    note = cls()

    # Assign core attributes
    note.note_attr_vals = note_attr_vals
    note.attr_name_idx_map = attr_name_idx_map

    # Set mapping of attribute names to functions that cast return type of get() calls, e.g. cast instrument to int
    note.attr_get_type_cast_map = attr_get_type_cast_map or {}
    for attr_name in note.attr_name_idx_map:
        if attr_name not in note.attr_get_type_cast_map:
            note.attr_get_type_cast_map[attr_name] = lambda x: x

    # Octave is always returned as an int
    note.attr_get_type_cast_map['octave'] = int

    return note
