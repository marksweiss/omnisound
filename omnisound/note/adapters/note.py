# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Sequence, Union

from numpy import float64, array

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import MajorKey, MinorKey
from omnisound.utils.utils import validate_type_choice


INSTRUMENT_I = I = 0
START_I = S = 1
DUR_I = D = 2
AMP_I = A = 3
PITCH_I = P = 4


class NoteValues(object):
    DEFAULT_VAL = 0.0

    def __init__(self, attr_names):
        self._attr_names = attr_names
        for attr_name in attr_names:
            setattr(self, attr_name, None)

    def as_dict(self) -> Mapping:
        return {field: getattr(self, field) or NoteValues.DEFAULT_VAL for field in self._attr_names}

    def as_list(self) -> List:
        return [getattr(self, field) for field in self._attr_names]

    def as_array(self) -> array:
        return array(self.as_list())


# noinspection PyPep8Naming
class Note(ABC):
    # noinspection SpellCheckingInspection
    BASE_NAME_INDEX_MAP = {
        'instrument': INSTRUMENT_I,
        'i': INSTRUMENT_I,
        'start': START_I,
        's': START_I,
        'dur': DUR_I,
        'd': DUR_I,
        'amp': AMP_I,
        'a': AMP_I,
        'pitch': PITCH_I,
        'p': PITCH_I,
    }

    def __init__(self,
                 # Ideally we would strongly type this as NoteSequence, but that is a circular dependency
                 note_sequence: Any = None,
                 note_sequence_index: int = None,
                 attr_vals_defaults_map: Mapping[str, float] = None,
                 attr_get_type_cast_map: Mapping[str, Any] = None):
        self.ns = note_sequence
        self.ns_idx = note_sequence_index
        self._attr_get_type_cast_map = attr_get_type_cast_map or {}

        if attr_vals_defaults_map:
            # The user provided attributes and values. For any of them that match BASE_ATTR_NAMES, simply
            # set the value for that attribute from the value provided.
            for attr_name, attr_val in attr_vals_defaults_map.items():
                validate_type_choice(attr_name, attr_val, (float, int))
                self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map[attr_name]] = \
                    float64(attr_val)

    # These standard methods are provided without the ability to override names, etc., to provide API for fluent
    # chaining calls to set all common Note attributes on one line
    # e.g. - note.I(1).S(1.0).D(2.5).A(400).P(440)
    def I(self, instrument: Union[float, int]):
        validate_type_choice('attr_name', instrument, (float, int))
        self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map['instrument']] = float64(instrument)
        return self

    def S(self, start: Union[float, int]):
        validate_type_choice('attr_name', start, (float, int))
        self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map['start']] = float64(start)
        return self

    def D(self, dur: Union[float, int]):
        validate_type_choice('attr_name', dur, (float, int))
        self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map['dur']] = float64(dur)
        return self

    def A(self, amp: Union[float, int]):
        validate_type_choice('attr_name', amp, (float, int))
        self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map['amp']] = float64(amp)
        return self

    def P(self, pitch: Union[float, int]):
        validate_type_choice('attr_name', pitch, (float, int))
        self.ns.note_attr_vals[self.ns_idx][self.ns.attr_name_idx_map['pitch']] = float64(pitch)
        return self

    def as_list(self) -> List[float]:
        return [self.ns.note_attr_vals[self.ns_idx][i] for i in range(len(self.ns.attr_name_idx_map))]

    @abstractmethod
    def transpose(self, interval: int):
        raise NotImplemented('Derived type must implement Note.transpose -> Note')

    @property
    @abstractmethod
    def performance_attrs(self) -> PerformanceAttrs:
        raise NotImplemented('Derived type must implement Note.performance_attrs -> PerformanceAttrs')

    @performance_attrs.setter
    @abstractmethod
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        raise NotImplemented('Derived type must implement Note.performance_attrs')

    @property
    @abstractmethod
    def pa(self) -> PerformanceAttrs:
        """Alias to something shorter for client code convenience."""
        raise NotImplemented('Derived type must implement Note.pa -> PerformanceAttrs')

    @pa.setter
    @abstractmethod
    def pa(self, performance_attrs: PerformanceAttrs):
        """Alias to something shorter for client code convenience."""
        raise NotImplemented('Derived type must implement Note.pa')

    @classmethod
    @abstractmethod
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> Any:
        raise NotImplemented('Note subtypes must implement get_pitch() and return a valid pitch value for their type')

    @abstractmethod
    def __eq__(self, other: 'Note') -> bool:
        raise NotImplemented('Derived type must implement Note.__eq__() -> bool')

    @abstractmethod
    def __str__(self):
        raise NotImplemented('Derived type must implement Note.__str__()')
