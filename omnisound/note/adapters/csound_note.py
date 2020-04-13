# Copyright 2018 Mark S. Weiss

from typing import Any, Mapping, Union

from numpy import ndarray

from omnisound.note.adapters.note import add_base_attr_name_indexes, getter, setter
from omnisound.note.generators.scale_globals import (NUM_NOTES_IN_OCTAVE, MajorKey, MinorKey)
from omnisound.utils.utils import (validate_optional_type, validate_optional_sequence_of_type,
                                   validate_sequence_of_type, validate_type, validate_type_choice)


CLASS_NAME = 'CSoundNote'

ATTR_NAMES = ('instrument', 'start', 'duration', 'amplitude', 'pitch')
ATTR_NAME_IDX_MAP = add_base_attr_name_indexes({attr_name: i for i, attr_name in enumerate(ATTR_NAMES)})

PITCH_MAP = {
    MajorKey.C: 1.01,
    MajorKey.C_s: 1.02,
    MajorKey.D_f: 1.02,
    MajorKey.D: 1.03,
    MajorKey.E_f: 1.04,
    MajorKey.E: 1.05,
    MajorKey.F: 1.06,
    MajorKey.F_s: 1.07,
    MajorKey.G_f: 1.07,
    MajorKey.G: 1.08,
    MajorKey.A_f: 1.09,
    MajorKey.A: 1.10,
    MajorKey.B_f: 1.11,
    MajorKey.B: 1.12,
    MajorKey.C_f: 1.12,

    MinorKey.C: 1.01,
    MinorKey.C_S: 1.02,
    MinorKey.D: 1.03,
    MinorKey.D_S: 1.04,
    MinorKey.E_F: 1.04,
    MinorKey.E: 1.05,
    MinorKey.E_S: 1.06,
    MinorKey.F: 1.06,
    MinorKey.F_S: 1.07,
    MinorKey.G: 1.08,
    MinorKey.A_F: 1.09,
    MinorKey.A: 1.10,
    MinorKey.A_S: 1.11,
    MinorKey.B_F: 1.11,
    MinorKey.B: 1.12,
}

MIN_OCTAVE = 1
MAX_OCTAVE = 12

DEFAULT_PITCH_PRECISION = SCALE_PITCH_PRECISION = 2


class CSoundInvalidTransposeError(Exception):
    pass


# Return a function that binds the pitch_precision to a function that returns a string that
# formats the value passed to it (the current value of pitch in the ToStrValWrapper in the OrderedAttr)
def pitch_to_str(pitch_prec):
    def _pitch_to_str(p):
        return str(round(p, pitch_prec))
    return _pitch_to_str


# TODO MODIFY AS MATRIX TRANSFORM GENERIC
def transpose(self, interval: int):
    """NOTE: This is only valid to call with pitches in the CSound octave.western_scale style, e.g. 4.01 for C4.

    Algorithm:
    There are 11 notes in each octave, so project each note in octave.pitch notation into 0-based vector space with
    11 slots per octave. e.g. C4 == 4.01 = 44.

    The formula to convert a note into this space is:
      (octave * 11) + (pitch - 1), e.g. 4.01 = (4 * 11) + (1 - 1) == 44
    The formula to convert a note from this space back SCALE PITCH PRECISION is the complement:
       (value % 11) + (remainder + 1)

    Examples:
        5.01 + interval 1 = 55 + 1 = 56, converted 56 % 11 + 1 + 1 = 5.02
        5.01 + interval 11 = 54 + 11 = 65, converted 65 % 11 + 10 + 1 = 5.11
        5.01 + interval 12 == 54 + 12 = 66, converted 66 % 11 + 0 + 1 = 6.01
        5.10 + interval 23 == 54 + 23 = 77, converted 77 % 11 + 0 + 1 = 7.01
        5.01 - interval 1 = 55 - 1 - 54, converted 54 % 11 + 10 + 1 = 4.11
        5.01 - interval 11 = 55 - 11 = 44, converted 44 % 11 + 0 + 1 = 4.01
        5.01 - interval 12 = 55 - 12 = 43, converted 43 % 11 + 10 + 1 = 3.11
        5.01 - interval 23 = 55 - 23 = 32, converted 32 % 11 + 10 + 1 = 2.11
    """
    if self.pitch_precision != SCALE_PITCH_PRECISION:
        raise CSoundInvalidTransposeError(('CSound pitch_precision must be SCALE_PITCH_PRECISION, '
                                           'which is `octave.pitch` notation like 4.01 for C4, to transpose'))
    validate_type('interval', interval, int)

    # Get current pitch as an integer in the range 1..11, == 1..NUM_NOTES_IN_OCTAVE
    cur_octave, cur_pitch = str(round(self.pitch, 2)).split('.')
    cur_octave = int(cur_octave)
    cur_pitch = int(cur_pitch)
    # -1 to adjust for 1-based values in CSound scale notation
    int_scale_pitch = (cur_octave * NUM_NOTES_IN_OCTAVE) + (cur_pitch - 1)
    int_scale_pitch += interval
    new_octave, new_pitch = divmod(int_scale_pitch, NUM_NOTES_IN_OCTAVE)
    # +1 to adjust for 1-based values in CSound scale notation
    new_pitch += 1
    self.pitch = round(new_octave + (new_pitch / 100.0), 2)


def get_pitch_for_key(key: Union[MajorKey, MinorKey], octave: int) -> float:
    validate_type_choice('key', key, (MajorKey, MinorKey))
    validate_type('octave', octave, int)
    if not (MIN_OCTAVE < octave < MAX_OCTAVE):
        raise ValueError((f'Arg `octave` must be in range '
                          f'{MIN_OCTAVE} <= octave <= {MAX_OCTAVE}'))
    return PITCH_MAP[key] + (float(octave) - 1.0)


# Prototypes/Implementations of CSound-specific accessors
def g_pitch_precision():
    def _g_pitch_precision(self) -> int:
        return self.pitch_precision
    return _g_pitch_precision


def s_pitch_precision():
    def _s_pitch_precision(self, pitch_precision: int) -> None:
        validate_type('pitch_precision', pitch_precision, int)
        self.pitch_precision = pitch_precision
        self.attr_to_str_formatter_map['pitch'] = pitch_to_str(self.pitch_precision)
    return _s_pitch_precision


def set_scale_pitch_precision(self):
    self.pitch_precision = SCALE_PITCH_PRECISION
    self.attr_to_str_formatter_map['pitch'] = pitch_to_str(self.pitch_precision)


def set_attr_str_formatter(self, attr_name: str, formatter: Any):
    validate_type('attr_name', attr_name, str)
    self.attr_to_str_formatter_map[attr_name] = formatter


# Fluent getters setters for core core note attributes
# noinspection PyPep8Naming
def I(self, attr_val: int):
    validate_type('attr_val', attr_val, int)
    self.note_attr_vals[self.attr_name_idx_map['instrument']] = attr_val
    return self


# noinspection PyPep8Naming
def S(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['start']] = attr_val
    return self


# noinspection PyPep8Naming
def D(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['duration']] = attr_val
    return self


# noinspection PyPep8Naming
def A(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['amplitude']] = attr_val
    return self


# noinspection PyPep8Naming
def P(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['pitch']] = attr_val
    return self


# Method implementations for dunder magic methods so the object supports `__eq__` and `__str__`, etc.
def eq(self, other) -> bool:
    return self.instrument == other.instrument and \
        self.start == other.start and \
        self.duration == other.duration and \
        self.amplitude == other.amplitude and \
        self.pitch == other.pitch


def to_str(self) -> str:
    """Note the intricate nested f-string for pitch. This lets the user control the precision of the string
       formatting for pitch to enforce two places for scale pitch syntax, e.g. Middle C == 4.01, and to also
       allow arbitrary precision for floating point values in Hz.

       Note also that we defer all string handling to the ToStrValWrapper class. The class sets up the to_str
       for the core attributes of the object correctly.
       Attributes are either integers, which require no special handling, floats other than pitch,
       which require precision handling, or pitch, which requires precision handling but is a special case
       because CSound overloads float syntax to express Western 12-tone scale values using float notation.
    """
    attr_strs = [f'i {self.attr_to_str_formatter_map["instrument"](self.instrument)}',
                 f'{self.attr_to_str_formatter_map["start"](self.start)}',
                 f'{self.attr_to_str_formatter_map["duration"](self.duration)}',
                 f'{self.attr_to_str_formatter_map["amplitude"](self.amplitude)}',
                 f'{self.attr_to_str_formatter_map["pitch"](self.pitch)}']
    for attr_name in self.attr_name_idx_map.keys():
        if attr_name not in ATTR_NAMES:
            attr_strs.append(f'{self.attr_to_str_formatter_map[attr_name](getattr(self, attr_name))}')

    return ' '.join(attr_strs)


# Meta class for dynamically creating a CSoundNote class with property accessors for an arbitrary list
# of note attributes. Accessors are dynamically created in `_make_cls()`. This is the mechanism for overloading
# class creation and passing that dynamically created list of methods in to Python `type` class, which is the
# meta class that creates classes. Methods are passed in argument named `dct` by common convention.
# NOTE: Through experimentation found that by creating attributes here in the `cls` object, we can refer to them
#  in the `getter()` and `setter()` wrappers through `self`, if we create them in overloaded `__new__()`. This
#  did not work with overloaded `__init__()`.
class CSoundNoteMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)

        # Attributes assigned by the caller
        cls.note_attr_vals = None
        cls.attr_name_idx_map = None
        cls.attr_get_type_cast_map = None
        cls.performance_attrs = None

        # Custom CSound attributes
        cls.pitch_precision = DEFAULT_PITCH_PRECISION
        cls.attr_to_str_formatter_map = {}

        return cls


def _make_cls(attr_name_idx_map):
    cls_bases = ()
    methods = {}
    # Create dynamically getters and setters for the note attributes for this instantiation of a CSoundNote class
    for attr_name in attr_name_idx_map.keys():
        get_func = getter(attr_name)
        methods[f'g_{attr_name}'] = get_func
        set_func = setter(attr_name)
        methods[f's_{attr_name}'] = set_func
        methods[attr_name] = property(get_func, set_func)
    # Standard Note accessor methods
    methods['I'] = I
    methods['S'] = S
    methods['D'] = D
    methods['A'] = A
    methods['P'] = P
    # Standard Note API
    methods['transpose'] = transpose
    # Supported dunder methods
    methods['__eq__'] = eq
    methods['__str__'] = to_str
    # Custom CSound methods
    # noinspection PyTypeChecker
    methods['pitch_precision'] = property(g_pitch_precision, s_pitch_precision)
    methods['set_scale_pitch_precision'] = set_scale_pitch_precision
    methods['set_attr_str_formatter'] = set_attr_str_formatter

    cls = CSoundNoteMeta(CLASS_NAME, cls_bases, methods)
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

    # Set string formatters for note attributes, this is specific to CSound per the comments
    note.set_attr_str_formatter('instrument', lambda x: str(x))
    note.set_attr_str_formatter('start', lambda x:  f'{x:.5f}')
    note.set_attr_str_formatter('duration', lambda x:  f'{x:.5f}')
    note.set_attr_str_formatter('amplitude', lambda x: str(x))
    # Handle case that pitch is a float and will have rounding but that sometimes we want
    # to use it to represent fixed pitches in Western scale, e.g. 4.01 == Middle C, and other times
    # we want to use to represent arbitrary floats in Hz. The former case requires .2f precision,
    # and for the latter case we default to .5f precision but allow any precision.
    # This is DEFAULT_PITCH_PRECISION to start with. User can call setter to update the value.
    note.set_attr_str_formatter('pitch', pitch_to_str(note.pitch_precision))

    # Set mapping of attribute names to functions that cast return type of get() calls, e.g. cast instrument to int
    note.attr_get_type_cast_map = attr_get_type_cast_map or {}
    for attr_name in note.attr_name_idx_map:
        if attr_name not in note.attr_get_type_cast_map:
            note.attr_get_type_cast_map[attr_name] = lambda x: x
    # Instrument is always returned as an int
    note.attr_get_type_cast_map['instrument'] = int

    return note
