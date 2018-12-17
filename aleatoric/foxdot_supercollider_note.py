# Copyright 2018 Mark S. Weiss

# from enum import Enum
from typing import Any   # , Union

from aleatoric.note import (Note, PerformanceAttrs)
# from scale_globals import (MajorKey, MinorKey)
# from aleatoric.utils import (validate_optional_types, validate_type_choice, validate_type, validate_types)
from aleatoric.utils import (validate_optional_types, validate_types)


class FoxDotSupercolliderNote(Note):

    SCALES = {'aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian', 'dorian2',
              'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian', 'justMajor', 'justMinor',
              'locrian', 'locrianMajor', 'lydian', 'lydianMinor', 'major', 'majorPentatonic', 'melodicMajor',
              'melodicMinor', 'minor', 'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus',
              'romanianMinor', 'yu', 'zhi'}

    # noinspection PyShadowingBuiltins
    def __init__(self, synth_def: Any = None,
                 delay: int = None, dur: float = None, amp: float = None, degree: float = None,
                 name: str = None,
                 oct: int = None, scale: str = None,
                 performance_attrs: PerformanceAttrs = None):
        # start not meaningful for Supercollider
        # Note: cast float(degree). Ints will work with FoxDot for degree so handle this.
        # TODO Change validation for types that support either int or float to be validate_types('x', x, (int, float))
        validate_types(('delay', delay, int), ('dur', dur, float), ('amp', amp, float),
                       ('degree', float(degree), float))
        validate_optional_types(('name', name, str), ('performance_attrs', performance_attrs, PerformanceAttrs),
                                ('oct', oct, int), ('scale', scale, str))
        if scale and scale not in FoxDotSupercolliderNote.SCALES:
            raise ValueError(f'arg `scale` must be None or a string in FoxDotSuperColliderNote.SCALES, scale: {scale}')
        super(FoxDotSupercolliderNote, self).__init__(instrument=synth_def,
                                                      start=delay, dur=dur, amp=amp, pitch=degree,
                                                      name=name,
                                                      performance_attrs=performance_attrs,
                                                      validate=False)
        if oct:
            self.oct = oct
        if scale:
            self.scale = scale

    class NoteConfig(object):
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

    @staticmethod
    def get_config() -> NoteConfig:
        return FoxDotSupercolliderNote.NoteConfig()

    @property
    def synth_def(self):
        return self.instrument

    @synth_def.setter
    def synth_def(self, synth_def: Any):
        # noinspection PyAttributeOutsideInit
        self.instrument = synth_def

    @property
    def delay(self):
        return self.start

    @delay.setter
    def delay(self, delay: int):
        # noinspection PyAttributeOutsideInit
        self.start = delay

    @property
    def degree(self):
        return self.pitch

    @degree.setter
    def degree(self, degree: float):
        # noinspection PyAttributeOutsideInit
        self.pitch = degree

    @staticmethod
    def copy(source_note):
        return FoxDotSupercolliderNote(synth_def=source_note.synth_def,
                                       delay=source_note.delay, dur=source_note.dur,
                                       amp=source_note.amp, degree=source_note.degree,
                                       name=source_note.name,
                                       oct=source_note.oct, scale=source_note.scale,
                                       performance_attrs=source_note.performance_attrs)

    def __eq__(self, other):
        if not super(FoxDotSupercolliderNote).__eq__(other):
            return False
        return ((self.oct is None and other.oct is None or self.oct == other.oct) and
                (self.scale is None and other.scale is None or self.scale == other.scale))

    def __str__(self):
        s = (f'name: {self.name} delay: {self.delay} '
             f'dur: {self.dur} amp: {self.amp} degree: {self.degree}')
        if hasattr(self, 'oct'):
            s += f' oct: {self.oct}'
        if hasattr(self, 'scale'):
            s += f' scale: {self.scale}'
        return s