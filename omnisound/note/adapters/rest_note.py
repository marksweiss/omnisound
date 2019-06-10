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

    def __init__(self, instrument: Any = None, start: Any = None, dur: Any = None, pitch: Any = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        super(RestNote, self).__init__(name=name, attrs=None,
                                       instrument=instrument, start=start, dur=dur, amp=RestNote.REST_AMP, pitch=pitch)
        self._performance_attrs = performance_attrs

    # Custom Interface
    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP

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
        return RestNote(instrument=source_note.instrument,
                        start=source_note.start, dur=source_note.dur,
                        pitch=source_note.pitch,
                        name=source_note.name,
                        performance_attrs=source_note._performance_attrs)

    def __eq__(self, other: 'RestNote') -> bool:
        return self.instrument == other.instrument and self.start == other.start and \
            self.dur == other.dur and self._pitch == other.pitch

    def __str__(self):
        return f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} {self.pitch}'

    def get_pitch_for_key(self, key, octave):
        raise NotImplemented('RestNote cannot meaningfully implement get_pitch_for_key()')

    def transpose(self, interval):
        raise NotImplemented('RestNote cannot meaningfully implement transpose()')
