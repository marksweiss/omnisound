# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from collections import OrderedDict

from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                     MajorKey, MinorKey)
from omnisound.utils.utils import (validate_not_none, validate_optional_types, validate_type,
                                   validate_type_choice, validate_types)

FIELDS = ('instrument', 'start', 'duration', 'amplitude', 'pitch', 'name')


class ToStrValWrapper(object):
    def __init__(self, attr_val: Any, to_str: Any = None):
        self.val = attr_val
        self.to_str = to_str or self._to_str

    @staticmethod
    def _to_str(x):
        return str(x)

    def __eq__(self, other):
        return self.val == other.val


# Return a function that binds the pitch_precision to a function that returns an fstring that
# formats the value passed to it (the current value of pitch in the ToStrValWrapper in the OrderedAttr)
def pitch_to_str(pitch_prec):
    def _pitch_to_str(p):
        return f'{{p:.{pitch_prec}}}'
    return _pitch_to_str

# TODO EXTEND UNIT TESTS FOR ADDITIONAL ATTRS
# TODO EXTEND UNIT TESTS FOR CUSTOM TO_STR() HANDLING


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

        self._to_str_val_wrappers = OrderedDict()
        self._to_str_val_wrappers['instrument'] = ToStrValWrapper(self._instrument)
        self._to_str_val_wrappers['start'] = ToStrValWrapper(self._start, lambda x: f'{x:.5f}')
        self._to_str_val_wrappers['duration'] = ToStrValWrapper(self._duration, lambda x: f'{x:.5f}')
        self._to_str_val_wrappers['amplitude'] = ToStrValWrapper(self._amplitude)
        self._to_str_val_wrappers['pitch'] = ToStrValWrapper(self.pitch, pitch_to_str(self._pitch_precision))

    # Custom Interface
    def add_attr(self, attr_name: str, attr_val: Any, to_str: Any = None):
        validate_type('attr_name', attr_name, str)
        validate_not_none('attr_name', attr_val)
        setattr(self, attr_name, attr_val)
        self._to_str_val_wrappers[attr_name] = ToStrValWrapper(attr_val, to_str)

    @property
    def pitch_precision(self) -> int:
        return self._pitch_precision

    @pitch_precision.setter
    def pitch_precision(self, pitch_precision: int):
        validate_type('pitch_precision', pitch_precision, int)
        self._pitch_precision = pitch_precision

    def set_scale_pitch_precision(self):
        self._pitch_precision = CSoundNote.SCALE_PITCH_PRECISION

    # Base Note Interface
    @property
    def instrument(self) -> int:
        return self._instrument

    @instrument.setter
    def instrument(self, instrument: int):
        validate_type('instrument', instrument, int)
        self._instrument = instrument
        self._to_str_val_wrappers['instrument'] = ToStrValWrapper(instrument)

    def i(self, instrument: int = None) -> Union['CSoundNote', int]:
        if instrument is not None:
            validate_type('instrument', instrument, int)
            self._instrument = instrument
            self._to_str_val_wrappers['instrument'] = ToStrValWrapper(instrument)
            return self
        else:
            return self._instrument

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, start: float):
        validate_type('start', start, float)
        self._start = start
        self._to_str_val_wrappers['start'] = ToStrValWrapper(start, lambda x: f'{x:.5f}')

    def s(self, start: float = None) -> Union['CSoundNote', float]:
        if start is not None:
            validate_type('start', start, float)
            self._start = start
            self._to_str_val_wrappers['start'] = ToStrValWrapper(start, lambda x: f'{x:.5f}')
            return self
        else:
            return self._start

    @property
    def dur(self) -> float:
        return self._duration

    @dur.setter
    def dur(self, duration: float):
        validate_type('duration', duration, float)
        self._duration = duration
        self._to_str_val_wrappers['duration'] = ToStrValWrapper(duration, lambda x: f'{x:.5f}')

    def d(self, duration: float = None) -> Union['CSoundNote', float]:
        if duration is not None:
            validate_type('duration', duration, float)
            self._duration = duration
            self._to_str_val_wrappers['duration'] = ToStrValWrapper(duration, lambda x: f'{x:.5f}')
            return self
        else:
            return self._duration

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        validate_type('duration', duration, float)
        self._duration = duration
        self._to_str_val_wrappers['duration'] = ToStrValWrapper(duration, lambda x: f'{x:.5f}')

    @property
    def amp(self) -> int:
        return self._amplitude

    @amp.setter
    def amp(self, amplitude: int):
        validate_type('amplitude', amplitude, int)
        self._amplitude = amplitude
        self._to_str_val_wrappers['amplitude'] = ToStrValWrapper(amplitude)

    def a(self, amplitude: int = None) -> Union['CSoundNote', int]:
        if amplitude is not None:
            validate_type('amplitude', amplitude, int)
            self._amplitude = amplitude
            self._to_str_val_wrappers['amplitude'] = ToStrValWrapper(amplitude)
            return self
        else:
            return self._amplitude

    @property
    def amplitude(self) -> int:
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amplitude: int):
        validate_type('amplitude', amplitude, int)
        self._amplitude = amplitude
        self._to_str_val_wrappers['amplitude'] = ToStrValWrapper(amplitude)

    @property
    def pitch(self) -> float:
        return self._pitch

    @pitch.setter
    def pitch(self, pitch: float):
        validate_type('pitch', pitch, float)
        self._to_str_val_wrappers['pitch'] = ToStrValWrapper(pitch, pitch_to_str(self._pitch_precision))
        self._pitch = pitch

    def p(self, pitch: float = None) -> Union['CSoundNote', float]:
        if pitch is not None:
            validate_type('pitch', pitch, float)
            self._pitch = pitch
            self._to_str_val_wrappers['pitch'] = ToStrValWrapper(pitch, pitch_to_str(self._pitch_precision))
            return self
        else:
            return self._pitch

    def transpose(self, interval: int):
        validate_type('interval', interval, int)
        # Get current pitch as an integer in the range 1..11
        cur_pitch_str = str(self._pitch)
        cur_octave, cur_pitch = cur_pitch_str.split('.')
        # Calculate the new_pitch by incrementing it and modding into the number of intervals in an octave
        # Then divide by 100 and add the octave to convert this back to CSound syntax
        #  which is the {octave}.{pitch in range 1..12}
        # Handle the case where the interval moves the pitch into the next octave
        if int(cur_pitch) + interval > NUM_INTERVALS_IN_OCTAVE:
            cur_octave = int(cur_octave) + 1
        self._pitch = float(cur_octave) + (((int(cur_pitch) + interval) % NUM_INTERVALS_IN_OCTAVE) / 100)

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
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> float:
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if not (cls.MIN_OCTAVE < octave < cls.MAX_OCTAVE):
            raise ValueError((f'Arg `octave` must be in range '
                              f'{cls.MIN_OCTAVE} <= octave <= {cls.MAX_OCTAVE}'))
        return cls.PITCH_MAP[key] + (float(octave) - 1.0)

    @staticmethod
    def copy(source_note: 'CSoundNote') -> 'CSoundNote':
        return CSoundNote(instrument=source_note.instrument,
                          start=source_note.start, duration=source_note.dur,
                          amplitude=source_note.amp, pitch=source_note.pitch,
                          name=source_note.name,
                          performance_attrs=source_note.performance_attrs)

    def __eq__(self, other: 'CSoundNote') -> bool:
        """NOTE: Equality ignores Note.name and Note.performance_attrs. Two CSoundNotes are considered equal
           if they have the same note attributes.
        """
        return self._instrument == other._instrument and self._start == other._start and \
               self._duration == other.duration and self._amplitude == other._amplitude and \
               self._pitch == other._pitch and self._to_str_val_wrappers == other._to_str_val_wrappers

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
        return ' '.join([f'{v.to_str(v.val)}' for v in self._to_str_val_wrappers.values()])
