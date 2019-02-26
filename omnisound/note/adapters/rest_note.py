# Copyright 2018 Mark S. Weiss

from typing import Any

from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0. Doesn't enforce types on any non-string attributes because it is intended
       to be used in conjunction with any other Note type in compositions to simply have a designated type
       for musical rests.
    """

    REST_AMP = 0.0

    def __init__(self, instrument: Any = None,
                 start: Any = None, dur: Any = None, pitch: Any = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        super(RestNote, self).__init__(name=name)
        self._instrument = instrument
        self._start = start
        self._dur = dur
        self._amp = RestNote.REST_AMP
        self._pitch = pitch
        self._performance_attrs = performance_attrs

    # Custom Interface
    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP

    # Base Note Interface
    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        self._instrument = instrument

    def i(self, instrument=None):
        if instrument is not None:
            self._instrument = instrument
            return self
        else:
            return self._instrument

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start

    def s(self, start=None):
        if start is not None:
            self._start = start
            return self
        else:
            return self._start

    @property
    def dur(self) -> float:
        return self._dur

    @dur.setter
    def dur(self, dur):
        self._dur = dur

    def d(self, dur=None):
        if dur is not None:
            self._dur = dur
            return self
        else:
            return self._dur

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, amp):
        self._amp = amp

    def a(self, amp=None):
        if amp is not None:
            self._amp = amp
            return self
        else:
            return self._amp

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, pitch):
        self._pitch = pitch

    def p(self, pitch=None):
        if pitch is not None:
            self._pitch = pitch
            return self
        else:
            return self._pitch

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

    @staticmethod
    def copy(source_note: 'RestNote') -> 'RestNote':
        return RestNote(instrument=source_note._instrument,
                        start=source_note._start, dur=source_note._dur,
                        pitch=source_note._pitch,
                        name=source_note._name,
                        performance_attrs=source_note._performance_attrs)

    def __eq__(self, other: 'RestNote') -> bool:
        return self._instrument == other._instrument and self._start == other._start and \
            self._dur == other.dur and self._pitch == other._pitch

    def __str__(self):
        return f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} {self.pitch}'

    def get_pitch_for_key(self, key, octave):
        raise NotImplemented('RestNote cannot meaningfully implement get_pitch_for_key()')

    def transpose(self, interval):
        raise NotImplemented('RestNote cannot meaningfully implement transpose()')
