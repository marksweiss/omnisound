# Copyright 2018 Mark S. Weiss

from typing import Dict

from numpy import array

from omnisound.note.adapters.note import Note
from omnisound.note.adapters.performance_attrs import PerformanceAttrs


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0. Doesn't enforce types on any non-string attributes because it is intended
       to be used in conjunction with any other Note type in compositions to simply have a designated type
       for musical rests.
    """

    REST_AMP = 0.0

    def __init__(self,
                 attrs: array = None,
                 attr_name_idx_map: Dict[str, int] = None,
                 attr_vals_map: Dict[str, float] = None,
                 note_num: int = None,
                 performance_attrs: PerformanceAttrs = None):
        attrs[Note.BASE_NAME_INDEX_MAP['amp']] = RestNote.REST_AMP
        super(RestNote, self).__init__(attrs=attrs,
                                       attr_name_idx_map=attr_name_idx_map,
                                       attr_vals_map=attr_vals_map,
                                       note_num=note_num)
        self.__dict__['_performance_attrs'] = performance_attrs

    # Custom Interface
    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP

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

    def __eq__(self, other: 'RestNote') -> bool:
        return self.instrument == other.instrument and self.start == other.start and \
            self.dur == other.dur and self._pitch == other.pitch

    def __str__(self):
        return f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} {self.pitch}'

    def get_pitch_for_key(self, key, octave):
        raise NotImplemented('RestNote cannot meaningfully implement get_pitch_for_key()')

    def transpose(self, interval):
        raise NotImplemented('RestNote cannot meaningfully implement transpose()')
