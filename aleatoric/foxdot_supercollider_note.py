# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from aleatoric.note import (Note, NoteConfig, PerformanceAttrs)
from scale_globals import (MajorKey, MinorKey)
from aleatoric.utils import (validate_optional_types, validate_type_choice, validate_types)


class FoxDotSupercolliderNoteConfig(NoteConfig):
    def __init__(self):
        self.synth_def = None
        self.delay = None
        self.dur = None
        self.amp = None
        self.degree = None
        self.oct = None
        self.scale = None
        self.name = None

    def as_dict(self):
        return {
            'synth_def': self.synth_def,
            'delay': self.delay,
            'dur': self.dur,
            'amp': self.amp,
            'degree': self.degree,
            'scale': self.scale,
            'oct': self.oct,
            'name': self.name
        }


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
        validate_optional_types(('name', name, str), ('oct', oct, int), ('scale', scale, str),
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
        self._octave = octave

    @property
    def scale(self) -> str:
        return self._scale

    @scale.setter
    def scale(self, scale: str):
        self._scale = scale

    # Base Note Interface
    @staticmethod
    def get_config() -> FoxDotSupercolliderNoteConfig:
        return FoxDotSupercolliderNoteConfig()

    @property
    def instrument(self) -> Any:
        return self._synth_def

    @instrument.setter
    def instrument(self, instrument: Any):
        self._synth_def = instrument

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
        self._delay = start

    @property
    def delay(self) -> int:
        return self._delay

    @delay.setter
    def delay(self, delay: int):
        self._delay = delay

    @property
    def dur(self) -> float:
        return self._dur

    @dur.setter
    def dur(self, dur: float):
        self._dur = dur

    @property
    def amp(self) -> float:
        return self._amp

    @amp.setter
    def amp(self, amp: float):
        self._amp = amp

    @property
    def pitch(self) -> Union[float, int]:
        return self._degree

    @pitch.setter
    def pitch(self, pitch: Union[float, int]):
        self._degree = pitch

    @property
    def degree(self) -> Union[float, int]:
        return self._degree

    @degree.setter
    def degree(self, degree: Union[float, int]):
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

    def get_pitch_for_key(self, key: Union[MajorKey, MinorKey], octave: int) -> int:
        return FoxDotSupercolliderNote.PITCH_MAP[key]

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
        s = (f'name: {self.name} delay: {self.delay} '
             f'dur: {self.dur} amp: {self.amp} degree: {self.degree}')
        if hasattr(self, 'oct'):
            s += f' oct: {self.oct}'
        if hasattr(self, 'scale'):
            s += f' scale: {self.scale}'
        return s