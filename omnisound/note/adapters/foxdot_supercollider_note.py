# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                     MajorKey, MinorKey)
from omnisound.utils.utils import (validate_optional_types, validate_type,
                                   validate_type_choice, validate_types)

FIELDS = ('synth_def', 'delay', 'dur', 'amp', 'degree', 'octave', 'scale')


# noinspection PyAttributeOutsideInit,PyPropertyDefinition
class FoxDotSupercolliderNote(Note):

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

    def __init__(self, synth_def: Any = None,
                 delay: Union[float, int] = None, dur: float = None, amp: float = None,
                 degree: Union[float, int] = None,
                 name: str = None,
                 octave: int = None, scale: str = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_type_choice('delay', delay, (float, int))
        validate_types(('dur', dur, float), ('amp', amp, float))
        validate_type_choice('degree', degree, (float, int))
        validate_optional_types(('name', name, str), ('octave', octave, int), ('scale', scale, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        if scale and scale not in FoxDotSupercolliderNote.SCALES:
            raise ValueError(f'arg `scale` must be None or a string in FoxDotSuperColliderNote.SCALES, scale: {scale}')

        super(FoxDotSupercolliderNote, self).__init__(name=name)
        # Attributes that are not representable as float must be managed at this level in this class and
        # not be created as attributes of the base class
        self.__dict__['_synth_def'] = synth_def
        self.__dict__['_scale'] = scale
        # Add aliased attributes that map to existing base Note attributes
        # Name underlying property with _<prop> because it is wrapped in this class as a @property to handle
        #  type casting from float to int or allowing return of Union[float, int]
        self.add_attr_name('_delay', Note.BASE_ATTR_NAMES['start'])
        self.add_attr_name('_degree', Note.BASE_ATTR_NAMES['pitch'])
        self.__setattr__('_delay', delay)
        self.__setattr__('dur', dur)
        self.__setattr__('amp', amp)
        self.__setattr__('_degree', degree)
        self.__setattr__('_octave', octave)

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
        return self

    def i(self, instrument: Any = None) -> Union['FoxDotSupercolliderNote', Any]:
        if instrument is not None:
            self.__dict['_synth_def'] = instrument
            return self
        else:
            return self.__dict__['_synth_def']

    @property
    def synth_def(self) -> Any:
        return self.__dict__['_synth_def']

    @synth_def.setter
    def synth_def(self, synth_def: Any):
        self.__dict['_synth_def'] = synth_def
        return self

    @property
    def start(self) -> int:
        return int(self._delay)

    @property
    def delay(self) -> int:
        return int(self._delay)

    @delay.setter
    def delay(self, delay: int):
        validate_type('delay', delay, int)
        self._delay = float(delay)
        return self

    @property
    def pitch(self) -> Union[float, int]:
        return self._degree

    @pitch.setter
    def pitch(self, pitch: Union[float, int]):
        validate_type_choice('pitch', pitch, (float, int))
        self._degree = float(pitch)
        return self

    def p(self, pitch: Union[float, int] = None) -> Union['FoxDotSupercolliderNote', float, int]:
        if pitch is not None:
            validate_type_choice('pitch', pitch, (float, int))
            self._degree = float(pitch)
            return self
        else:
            return self._degree

    @property
    def degree(self) -> Union[float, int]:
        return self._degree

    @degree.setter
    def degree(self, degree: Union[float, int]):
        validate_type_choice('degree', degree, (float, int))
        self._degree = float(degree)

    @property
    def octave(self) -> int:
        return int(self._octave)

    @octave.setter
    def octave(self, octave: int):
        validate_type('octave', octave, int)
        self._octave = float(octave)
        return self

    @property
    def scale(self) -> str:
        return self.__dict__['_scale']

    @scale.setter
    def scale(self, scale: str):
        validate_type('scale', scale, str)
        self.__dict__['_scale'] = scale
        return self

    def transpose(self, interval: int):
        """Foxdot pitches as ints are in range 1..12
        """
        validate_type('interval', interval, int)
        self._degree = (self._degree + interval) % NUM_INTERVALS_IN_OCTAVE

    @property
    def performance_attrs(self) -> PerformanceAttrs:
        return self._performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        self._performance_attrs = performance_attrs

    @property
    def pa(self) -> PerformanceAttrs:
        return self._performance_attrs

    @pa.setter
    def pa(self, performance_attrs: PerformanceAttrs):
        self._performance_attrs = performance_attrs

    @classmethod
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> int:
        return cls.PITCH_MAP[key]

    @staticmethod
    def copy(source_note: 'FoxDotSupercolliderNote') -> 'FoxDotSupercolliderNote':
        return FoxDotSupercolliderNote(synth_def=source_note.synth_def,
                                       delay=source_note._delay, dur=source_note.dur,
                                       amp=source_note.amp, degree=source_note._degree,
                                       name=source_note.name,
                                       octave=source_note.octave, scale=source_note.scale,
                                       performance_attrs=source_note._performance_attrs)

    def __eq__(self, other: 'FoxDotSupercolliderNote') -> bool:
        # noinspection PyProtectedMember
        return (self.octave is None and other.octave is None or self.octave == other.octave) and \
            (self.scale is None and other.scale is None or self.scale == other.scale) and \
            self._synth_def == other._synth_def and self._delay == other._delay and self.dur == other.dur and \
            self.amp == other.amp and self._degree == other._degree

    def __str__(self):
        s = (f'name: {self.name} delay: {self._delay} '
             f'dur: {self._dur} amp: {self._amp} degree: {self._degree}')
        if hasattr(self, 'octave'):
            s += f' octave: {self._octave}'
        if hasattr(self, '_scale'):
            s += f' scale: {self._scale}'
        return s
