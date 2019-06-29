# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, Union

from numpy import array
from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE, MajorKey, MinorKey)
from omnisound.utils.utils import (validate_optional_types, validate_type, validate_type_choice, validate_types)

CSOUND_ATTR_NAMES = ('instrument', 'start', 'duration', 'amplitude', 'pitch')


# Return a function that binds the pitch_precision to a function that returns a string that
# formats the value passed to it (the current value of pitch in the ToStrValWrapper in the OrderedAttr)
def pitch_to_str(pitch_prec):
    def _pitch_to_str(p):
        return str(round(p, pitch_prec))
    return _pitch_to_str


class CSoundNote(Note):
    """Models a note with attributes aliased to and specific to CSound
       and with a str() that prints CSound formatted output.
    """

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

    def __init__(self,
                 attr_vals: array = None,
                 attr_name_idx_map: Dict[str, int] = None,
                 # TODO RENAME attr_default_vals_map
                 attr_vals_defaults_map: Dict[str, float] = None,
                 attr_get_type_cast_map: Dict[str, Any] = None,
                 note_sequence_num: int = None,
                 pitch_precision: int = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_optional_types(('pitch_precision', pitch_precision, int),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))

        # Handle case of a custom function for type casting getattr return value, for a non-standard attr
        attr_get_type_cast_map = attr_get_type_cast_map or {}
        # First set a function to convert this value to a str(), which CSoundNote requires for all attributes
        # The user can always override this by calling set_to_str_for_attr(), but since we know the attr is
        # non-standard we can provide a default here
        self.__dict__['_to_str_val_wrappers'] = dict()
        for attr_name in attr_get_type_cast_map:
            self.__dict__['_to_str_val_wrappers'][attr_name] = lambda x: str(x)
        # Then append a default getattr() type cast mapping for instrument, which we always want to return as int
        attr_get_type_cast_map['instrument'] = int
        # Then pass the attrs array, map of attr names to attr array indexes, map of attr names to default values
        # and map of attr names to getattr() type case values, to base Note, which then uses all this config
        # to provide get/set semantics over the Note
        super(CSoundNote, self).__init__(attr_vals=attr_vals,
                                         attr_name_idx_map=attr_name_idx_map,
                                         attr_vals_defaults_map=attr_vals_defaults_map,
                                         attr_get_type_cast_map=attr_get_type_cast_map,
                                         note_sequence_num=note_sequence_num)

        # Add custom property names for this Note type, map to correct underlying attribute index in base class
        # str_to_val_wrappers are assigned in self.__setattr__()
        self.__dict__['_to_str_val_wrappers']['instrument'] = lambda x: str(x)
        self.__dict__['_to_str_val_wrappers']['start'] = lambda x:  f'{x:.5f}'
        self.__dict__['_to_str_val_wrappers']['duration'] = lambda x:  f'{x:.5f}'
        self.__dict__['_to_str_val_wrappers']['amplitude'] = lambda x: str(x)

        # Handle case that pitch is a float and will have rounding but that sometimes we want
        # to use it to represent fixed pitches in Western scale, e.g. 4.01 == Middle C, and other times
        # we want to use to represent arbitrary floats in Hz. The former case requires .2f precision,
        # and for the latter case we default to .5f precision but allow any precision.
        self.__dict__['_pitch_precision'] = pitch_precision or CSoundNote.DEFAULT_PITCH_PRECISION
        self.__dict__['_to_str_val_wrappers']['pitch'] = pitch_to_str(self.__dict__['_pitch_precision'])

        self.__dict__['_performance_attrs'] = performance_attrs

    # noinspection PyStatementEffect
    def set_to_str_for_attr(self, attr_name: str, to_str: Any = None):
        """Supports adding new attributes and assigning proper to_str handling for them in this class. Note that
           this does not create a wrapper that also converts the type correctly. This requires static override
           properties such as we have for instrument and amplitude. Clients using this will still need to cast
           return values from float if they desire another type.
        """
        validate_type('attr_name', attr_name, str)
        if not to_str:
            to_str = lambda x: str(x)
        self.__dict__['_to_str_val_wrappers'][attr_name] = to_str

    @property
    def pitch_precision(self) -> int:
        return self.__dict__['_pitch_precision']

    @pitch_precision.setter
    def pitch_precision(self, pitch_precision: int):
        validate_type('pitch_precision', pitch_precision, int)
        self.__dict__['_pitch_precision'] = pitch_precision

    def set_scale_pitch_precision(self):
        self.__dict__['_pitch_precision'] = CSoundNote.SCALE_PITCH_PRECISION

    # TODO MODIFY AS MATRIX TRANSFORM GENERIC
    #  ARGS:
    #  - field name
    #  - value
    #  - operator (e.g. sum, product, dot product, etc.)
    def transpose(self, interval: int):
        validate_type('interval', interval, int)
        # Get current pitch as an integer in the range 1..11
        cur_pitch_str = str(self.pitch)
        cur_octave, cur_pitch = cur_pitch_str.split('.')
        # Calculate the new_pitch by incrementing it and modding into the number of intervals in an octave
        # Then divide by 100 and add the octave to convert this back to CSound syntax
        #  which is the {octave}.{pitch in range 1..12}
        # Handle the case where the interval moves the pitch into the next octave
        if int(cur_pitch) + interval > NUM_INTERVALS_IN_OCTAVE:
            cur_octave = int(cur_octave) + 1
        # noinspection PyAttributeOutsideInit
        self.pitch = float(cur_octave) + (((int(cur_pitch) + interval) % NUM_INTERVALS_IN_OCTAVE) / 100)

    @property
    def performance_attrs(self) -> PerformanceAttrs:
        return self.__dict__['_performance_attrs']

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self.__dict__['_performance_attrs'] = performance_attrs

    @property
    def pa(self) -> PerformanceAttrs:
        return self.__dict__['_performance_attrs']

    @pa.setter
    def pa(self, performance_attrs: PerformanceAttrs):
        self.__dict__['_performance_attrs'] = performance_attrs

    @classmethod
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> float:
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if not (cls.MIN_OCTAVE < octave < cls.MAX_OCTAVE):
            raise ValueError((f'Arg `octave` must be in range '
                              f'{cls.MIN_OCTAVE} <= octave <= {cls.MAX_OCTAVE}'))
        return cls.PITCH_MAP[key] + (float(octave) - 1.0)

    def __eq__(self, other: 'CSoundNote') -> bool:
        """NOTE: Equality ignores Note.name, Note.performance_attrs and to_str().
           Two CSoundNotes are considered equal if they have the same note attributes.
        """
        return self.instrument == other.instrument and \
            self.start == other.start and \
            self.duration == other.duration and \
            self.amplitude == other.amplitude and \
            self.pitch == other.pitch

    def __str__(self):
        """Note the intricate nested f-string for pitch. This lets the user control the precision of the string
           formatting for pitch to enforce two places for scale pitch syntax, e.g. Middle C == 4.01, and to also
           allow arbitrary precision for floating point values in Hz.

           Note also that we defer all string handling to the ToStrValWrapper class. The class sets up the to_str
           for the core attributes of the object correctly. And we expect that any calls to add_attr() to add
           new attributes also correctly set up to_str for that attribute and it's type. Attributes are either
           integers, which require no special handling, floats other than pitch, which require precision handling,
           or pitch, which requires precision handling but is a special case because CSound overloads float syntax
           to express Western 12-tone scale values using float notation.
        """
        attr_strs = [f'i {self.__dict__["_to_str_val_wrappers"]["instrument"](self.instrument)}',
                     f'{self.__dict__["_to_str_val_wrappers"]["start"](self.start)}',
                     f'{self.__dict__["_to_str_val_wrappers"]["duration"](self.duration)}',
                     f'{self.__dict__["_to_str_val_wrappers"]["amplitude"](self.amplitude)}',
                     f'{self.__dict__["_to_str_val_wrappers"]["pitch"](self.pitch)}']
        for attr_name in self.__dict__["_attr_name_idx_map"].keys():
            if attr_name not in CSOUND_ATTR_NAMES and attr_name not in self.BASE_NAME_INDEX_MAP:
                attr_strs.append(f'{self.__dict__["_to_str_val_wrappers"][attr_name](self.__getattr__(attr_name))}')

        return ' '.join(attr_strs)
