# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from aleatoric.note import Note, PerformanceAttrs
from aleatoric.scale_globals import MajorKey, MinorKey
from aleatoric.utils import (validate_optional_types, validate_type, validate_type_choice,
                             validate_types)


FIELDS = ('synth_def', 'delay', 'dur', 'amp', 'degree', 'octave', 'scale')


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

        MinorKey.c: 0,
        MinorKey.c_s: 1,
        MinorKey.d: 1,
        MinorKey.d_s: 2,
        MinorKey.e_f: 3,
        MinorKey.e: 4,
        MinorKey.e_s: 5,
        MinorKey.f: 6,
        MinorKey.f_s: 6,
        MinorKey.g: 7,
        MinorKey.a_f: 8,
        MinorKey.a: 9,
        MinorKey.a_s: 10,
        MinorKey.b_f: 10,
        MinorKey.b: 11
    }

    def __init__(self, synth_def: Any = None,
                 delay: int = None, dur: float = None, amp: float = None, degree: Union[float, int] = None,
                 name: str = None,
                 octave: int = None, scale: str = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('delay', delay, int), ('dur', dur, float), ('amp', amp, float))
        validate_type_choice('degree', degree, (float, int))
        validate_optional_types(('name', name, str), ('octave', octave, int), ('scale', scale, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(FoxDotSupercolliderNote, self).__init__(name=name)
        if scale and scale not in FoxDotSupercolliderNote.SCALES:
            raise ValueError(f'arg `scale` must be None or a string in FoxDotSuperColliderNote.SCALES, scale: {scale}')
        self._synth_def = synth_def
        self._delay = delay
        self._dur = dur
        self._amp = amp
        self._degree = degree
        self._octave = octave
        self._scale = scale
        self._performance_attrs = performance_attrs

    # Custom Interface
    @property
    def octave(self) -> int:
        return self._octave

    @octave.setter
    def octave(self, octave: int):
        validate_type('octave', octave, int)
        self._octave = octave

    @property
    def scale(self) -> str:
        return self._scale

    @scale.setter
    def scale(self, scale: str):
        validate_type('scale', scale, str)
        self._scale = scale

    # Base Note Interface
    @property
    def instrument(self) -> Any:
        return self._synth_def

    @instrument.setter
    def instrument(self, instrument: Any):
        self._synth_def = instrument

    def i(self, instrument: Any = None) -> Union['FoxDotSupercolliderNote', Any]:
        if instrument is not None:
            self._synth_def = instrument
            return self
        else:
            return self._synth_def

    @property
    def synth_def(self) -> Any:
        return self._synth_def

    @synth_def.setter
    def synth_def(self, synth_def: Any):
        self._synth_def = synth_def

    @property
    def start(self) -> int:
        return self._delay

    @start.setter
    def start(self, start: int):
        validate_type('start', start, int)
        self._delay = start

    def s(self, start: int = None) -> Union['FoxDotSupercolliderNote', int]:
        if start is not None:
            validate_type('start', start, int)
            self._delay = start
            return self
        else:
            return self._delay

    @property
    def delay(self) -> int:
        return self._delay

    @delay.setter
    def delay(self, delay: int):
        validate_type('delay', delay, int)
        self._delay = delay

    @property
    def dur(self) -> float:
        return self._dur

    @dur.setter
    def dur(self, dur: float):
        validate_type('dur', dur, float)
        self._dur = dur

    def d(self, duration: float = None) -> Union['FoxDotSupercolliderNote', float]:
        if duration is not None:
            validate_type('duration', duration, float)
            self._dur = duration
            return self
        else:
            return self._dur

    @property
    def amp(self) -> float:
        return self._amp

    @amp.setter
    def amp(self, amp: float):
        self._amp = amp

    def a(self, amp: float = None) -> Union['FoxDotSupercolliderNote', float]:
        if amp is not None:
            validate_type('amp', amp, float)
            self._amp = amp
            return self
        else:
            return self._amp

    @property
    def pitch(self) -> Union[float, int]:
        return self._degree

    @pitch.setter
    def pitch(self, pitch: Union[float, int]):
        validate_type_choice('pitch', pitch, (float, int))
        self._degree = pitch

    def p(self, pitch: Union[float, int] = None) -> Union['FoxDotSupercolliderNote', float, int]:
        if pitch is not None:
            validate_type_choice('pitch', pitch, (float, int))
            self._degree = pitch
            return self
        else:
            return self._degree

    @property
    def degree(self) -> Union[float, int]:
        return self._degree

    @degree.setter
    def degree(self, degree: Union[float, int]):
        validate_type_choice('pitch', pitch, (float, int))
        self._degree = degree

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
        return FoxDotSupercolliderNote(synth_def=source_note._synth_def,
                                       delay=source_note._delay, dur=source_note._dur,
                                       amp=source_note._amp, degree=source_note._degree,
                                       name=source_note._name,
                                       octave=source_note._octave, scale=source_note._scale,
                                       performance_attrs=source_note._performance_attrs)

    def __eq__(self, other: 'FoxDotSupercolliderNote') -> bool:
        return (self._octave is None and other._octave is None or self._octave == other._octave) and \
            (self._scale is None and other._scale is None or self._scale == other._scale) and \
            self._synth_def == other._synth_def and self._delay == other._delay and self._dur == other._dur and \
            self._amp == other._amp and self._degree == other._degree

    def __str__(self):
        s = (f'name: {self._name} delay: {self._delay} '
             f'dur: {self._dur} amp: {self._amp} degree: {self._degree}')
        if hasattr(self, 'octave'):
            s += f' octave: {self._octave}'
        if hasattr(self, 'scale'):
            s += f' scale: {self._scale}'
        return s
