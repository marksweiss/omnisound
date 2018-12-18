# Copyright 2018 Mark S. Weiss

from typing import Union

from aleatoric.note import (Note, NoteConfig, PerformanceAttrs)
from aleatoric.scale_globals import (MajorKey, MinorKey)
from aleatoric.utils import (validate_optional_types, validate_type_choice, validate_type, validate_types)


class CSoundNoteConfig(NoteConfig):
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

    DEFAULT_PITCH_PRECISION = SCALE_PITCH_PRECISION = 2

    def __init__(self, instrument: int = None,
                 start: float = None, duration: float = None, amplitude: int = None, pitch: float = None,
                 name: str = None,
                 pitch_precision: int = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('instrument', instrument, int), ('start', start, float),
                       ('duration', duration, float), ('amplitude', amplitude, int),
                       ('pitch', pitch, float))
        validate_optional_types(('name', name, str), ('pitch_precision', pitch_precision, int),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(CSoundNote, self).__init__(name=name)
        self._instrument = instrument
        self._start = start
        self._duration = duration
        self._amplitude = amplitude
        self._pitch = pitch
        self._performance_attrs = performance_attrs
        # Handle case that pitch is a float and will have rounding but that sometimes we want
        # to use it to represent fixed pitches in Western scale, e.g. 4.01 == Middle C, and other times
        # we want to use to represent arbitrary floats in Hz. The former case requires .2f precision,
        # and for the latter case we default to .5f precision but allow any precision.
        self._pitch_precision = pitch_precision or CSoundNote.DEFAULT_PITCH_PRECISION

    # Custom Interface
    # TODO NEED TESTS FOR THESE THREE METHODS
    @property
    def pitch_precision(self) -> int:
        return self._pitch_precision

    @pitch_precision.setter
    def pitch_precision(self, pitch_precision: int):
        validate_type(pitch_precision, 'pitch_precision', int)
        self._pitch_precision = pitch_precision

    def set_scale_pitch_precision(self):
        self._pitch_precision = CSoundNote.SCALE_PITCH_PRECISION

    # Base Note Interface
    @staticmethod
    def get_config() -> CSoundNoteConfig:
        return CSoundNoteConfig()

    @property
    def instrument(self) -> int:
        return self._instrument

    @instrument.setter
    def instrument(self, instrument: int):
        self._instrument = instrument

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, start: float):
        self._start = start

    @property
    def dur(self) -> float:
        return self._duration

    @dur.setter
    def dur(self, duration: float):
        self._duration = duration

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = duration

    @property
    def amp(self) -> int:
        return self._amplitude

    @amp.setter
    def amp(self, amplitude: int):
        self._amplitude = amplitude

    @property
    def amplitude(self) -> int:
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amplitude: int):
        self._amplitude = amplitude

    @property
    def pitch(self) -> float:
        return self._pitch

    @pitch.setter
    def pitch(self, pitch: float):
        self._pitch = pitch

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

    def get_pitch_for_key(self, key: Union[MajorKey, MinorKey], octave: int) -> float:
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if CSoundNote.MIN_OCTAVE < octave < CSoundNote.MAX_OCTAVE:
            raise ValueError((f'Arg `octave` must be in range '
                              f'{CSoundNote.MIN_OCTAVE} <= octave <= {CSoundNote.MAX_OCTAVE}'))
        return CSoundNote.PITCH_MAP[key] + (float(octave) - 1.0)

    @staticmethod
    def copy(source_note) -> 'CSoundNote':
        return CSoundNote(instrument=source_note.instrument,
                          start=source_note.start, duration=source_note.dur,
                          amplitude=source_note.amp, pitch=source_note.pitch,
                          name=source_note.name,
                          performance_attrs=source_note.performance_attrs)

    def __eq__(self, other: 'CSoundNote') -> bool:
        """NOTE: Equality ignores Note.name and Note.peformance_attrs. Two CSountNotes are considered equal
           if they have the same note attributes.
        """
        return self._instrument == other._instrument and self._start == other._start and \
            self._duration == other.duration and self._amplitude == other._amplitude and \
            self._pitch == other._pitch

    def __str__(self):
        return (f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} '
                f'{self.pitch}:.{self._pitch_precision}f')