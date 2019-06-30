# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, Union

from numpy import array
from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                     MajorKey, MinorKey)
from omnisound.utils.utils import (validate_optional_types, validate_type)


# noinspection PyAttributeOutsideInit,PyPropertyDefinition,PyProtectedMember
class FoxDotSupercolliderNote(Note):

    ATTR_NAMES = ('delay', 'dur', 'amp', 'degree', 'octave')
    ATTR_NAME_IDX_MAP = {attr_name: i for i, attr_name in enumerate(ATTR_NAMES)}

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

    def __init__(self,
                 attr_vals: array = None,
                 attr_name_idx_map: Dict[str, int] = None,
                 attr_vals_defaults_map: Dict[str, float] = None,
                 attr_get_type_cast_map: Dict[str, Any] = None,
                 note_sequence_num: int = None,
                 synth_def: Any = None,
                 scale: str = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_optional_types(('scale', scale, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        if scale and scale not in FoxDotSupercolliderNote.SCALES:
            raise ValueError(f'arg `scale` must be None or a string in FoxDotSuperColliderNote.SCALES, scale: {scale}')

        # Handle case of a custom function for type casting getattr return value, for a non-standard attr
        attr_get_type_cast_map = attr_get_type_cast_map or {}
        # Append a default getattr() type cast mappings to int for instrument, velocity and pitch
        attr_get_type_cast_map['start'] = int
        attr_get_type_cast_map['delay'] = int
        attr_get_type_cast_map['octave'] = int
        super(FoxDotSupercolliderNote, self).__init__(
            attr_vals=attr_vals,
            attr_name_idx_map=attr_name_idx_map,
            attr_vals_defaults_map=attr_vals_defaults_map,
            attr_get_type_cast_map=attr_get_type_cast_map,
            note_sequence_num=note_sequence_num)

        # Attributes that are not representable as float must be managed at this level in this class and
        # not be created as attributes of the base class
        self.__dict__['_synth_def'] = synth_def
        self.__dict__['_scale'] = scale
        # Add aliased attributes that map to existing base Note attributes
        # Name underlying property with _<prop> because it is wrapped in this class as a @property to handle
        #  type casting from float to int or allowing return of Union[float, int]
        # -1 because FoxDot doesn't store instrument in index 0, because it's not a numeric type for this note type
        # so all the attributes are shifted left one position

        self.__dict__['performance_attrs'] = performance_attrs

    # Only define explicit properties on this level that diverge from behavior of underlying Note properties
    # - override an existing underlying property (instrument) with different behavior only available at this level
    # - provide accessors only available at this level
    # - provide accessors that have different type behavior than base class attribute
    @property
    def instrument(self) -> Any:
        return self.__dict__['_synth_def']

    @instrument.setter
    def instrument(self, instrument: Any):
        self.__dict__['_synth_def'] = instrument

    @property
    def i(self) -> Union['FoxDotSupercolliderNote', Any]:
        return self.__dict__['_synth_def']

    @i.setter
    def i(self, instrument: Any = None) -> None:
        self.__dict['_synth_def'] = instrument

    @property
    def synth_def(self) -> Any:
        return self.__dict__['_synth_def']

    @synth_def.setter
    def synth_def(self, synth_def: Any):
        self.__dict['_synth_def'] = synth_def

    @property
    def scale(self) -> str:
        return self.__dict__['_scale']

    @scale.setter
    def scale(self, scale: str):
        validate_type('scale', scale, str)
        self.__dict__['_scale'] = scale

    def transpose(self, interval: int):
        """Foxdot pitches as ints are in range 1..12
        """
        validate_type('interval', interval, int)
        super(FoxDotSupercolliderNote, self)._degree = \
            (int(super(FoxDotSupercolliderNote, self).degree) + interval) % NUM_INTERVALS_IN_OCTAVE

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
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> int:
        return cls.PITCH_MAP[key]

    def __eq__(self, other: 'FoxDotSupercolliderNote') -> bool:
        # noinspection PyProtectedMember
        return (self.octave is None and other.octave is None or self.octave == other.octave) and \
            (self.scale is None and other.scale is None or self.scale == other.scale) and \
            self._synth_def == other._synth_def and self.delay == other.delay and self.dur == other.dur and \
            self.amp == other.amp and self.degree == other.degree

    def __str__(self):
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
