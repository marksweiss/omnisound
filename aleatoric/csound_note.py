# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from aleatoric.note import (Note, PerformanceAttrs)
from aleatoric.scale_globals import (MajorKey, MinorKey)
from aleatoric.utils import (validate_optional_types, validate_type_choice, validate_type, validate_types)


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

        MinorKey.c: 1.01,
        MinorKey.c_s: 1.02,
        MinorKey.d: 1.03,
        MinorKey.d_s: 1.04,
        MinorKey.e_f: 1.04,
        MinorKey.e: 1.05,
        MinorKey.e_s: 1.06,
        MinorKey.f: 1.06,
        MinorKey.f_s: 1.07,
        MinorKey.g: 1.08,
        MinorKey.a_f: 1.09,
        MinorKey.a: 1.10,
        MinorKey.a_s: 1.11,
        MinorKey.b_f: 1.11,
        MinorKey.b: 1.12,
    }

    MIN_OCTAVE = 1.0
    MAX_OCTAVE = 12.0

    def __init__(self, instrument: Any = None,
                 start: float = None, duration: float = None, amplitude: int = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('start', start, float), ('duration', duration, float), ('amplitude', amplitude, int),
                       ('pitch', pitch, float))
        validate_optional_types(('name', name, str), ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(CSoundNote, self).__init__(instrument=instrument,
                                         start=start, dur=duration, amp=amplitude, pitch=pitch,
                                         name=name,
                                         performance_attrs=performance_attrs,
                                         validate=False)

    class NoteConfig(object):
        def __init__(self):
            self.instrument = None
            self.start = None
            self.duration = None
            self.amplitude = None
            self.pitch = None
            self.name = None

        def as_dict(self):
            return {
                'instrument': self.instrument,
                'start': self.start,
                'duration': self.duration,
                'amplitude': self.amplitude,
                'pitch': self.pitch,
                'name': self.name
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return CSoundNote.NoteConfig()

    @property
    def duration(self):
        return self.dur

    @duration.setter
    def duration(self, duration: float):
        # noinspection PyAttributeOutsideInit
        self.dur = duration

    @property
    def amplitude(self):
        return self.amp

    @amplitude.setter
    def amplitude(self, amplitude: int):
        # noinspection PyAttributeOutsideInit
        self.amp = amplitude

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if CSoundNote.MIN_OCTAVE < octave < CSoundNote.MAX_OCTAVE:
            raise ValueError((f'Arg `octave` must be in range '
                              f'{CSoundNote.MIN_OCTAVE} <= octave <= {CSoundNote.MAX_OCTAVE}'))
        return CSoundNote.PITCH_MAP[key] + (float(octave) - 1.0)

    @staticmethod
    def copy(source_note):
        return CSoundNote(instrument=source_note.instrument,
                          start=source_note.start, duration=source_note.dur,
                          amplitude=source_note.amp, pitch=source_note.pitch,
                          name=source_note.name,
                          performance_attrs=source_note.performance_attrs)

    def __str__(self):
        # TODO HANDLE FLOAT ROUNDING ON PITCH BY CHANGING PRECISION TO .2, FIX TESTS
        return f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} {self.pitch:.5f}'
