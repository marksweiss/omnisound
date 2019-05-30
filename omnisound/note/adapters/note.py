# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List, Union

from numpy import float64, resize, zeros

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import MajorKey, MinorKey
from omnisound.utils.utils import (validate_not_none, validate_type)


class NoteConfig(object):
    def __init__(self, fields):
        self._attr_names = fields
        for field in fields:
            setattr(self, field, None)

    def as_dict(self) -> Dict:
        return {field: getattr(self, field) for field in self._attr_names}

    def as_list(self) -> List:
        return [getattr(self, field) for field in self._attr_names]


class Note(ABC):
    """Models the core attributes of a musical note common to multiple back ends.

       Core properties are defined here that are the property interface for Notes in derived classes, which are
       notes that define the attributes for a specific back end, e.g. `CSoundNote`, `MidiNote`, etc. The core
       properties are `instrument`, `start`, `duration`, `amplitude` and `pitch`. The interface here is abstract so
       types aren't specified, but derived classes are expected to define types and enforce them with validation in
       `__init__()` and all setters. Derived notes may also create aliased properties for these core properties that
       match the conventions of their backend, and of course they may define additional properties specific to that
       backend.

       In addition, each derived type is expected to define equality, a `copy()` constructor, and `str`. Note that
       `str` may be meaningful output, as in the case of `CSoundNote`, which produces a string that can be inserted
       into a CSound score file which CSound uses to render audio. Or it may be merely a string representation of
       the information in the note, as is the case for Midi.

       Finally, each note is responsible for being able to translate a musical key (pitch on a scale) to a valid
       pitch value for that Note's backend, in the `get_pitch_for_key()` method.

       It is is strongly preferred that all getter properties return self in derived classes
       to support fluid interfaces for defining and modifying notes most easily in the least number of lines.
    """

    DEFAULT_NAME = 'Note'

    INSTRUMENT = 0
    START = 1
    DUR = 2
    AMP = 3
    PITCH = 4
    # noinspection SpellCheckingInspection
    BASE_ATTR_NAMES = {
        'instrument': INSTRUMENT,
        'i': INSTRUMENT,
        'start': START,
        's': START,
        'dur': DUR,
        'd': DUR,
        'amp': AMP,
        'a': AMP,
        'pitch': PITCH,
        'p': PITCH,
    }
    NUM_BASE_ATTRS = 5

    def __init__(self, name: str = None):
        self.name = name or Note.DEFAULT_NAME
        # noinspection SpellCheckingInspection
        self._attr_names = deepcopy(Note.BASE_ATTR_NAMES)
        self._attrs = zeros((Note.NUM_BASE_ATTRS, 1), dtype=float64)

    @property
    def num_attrs(self) -> int:
        return len(self._attrs)

    def add_attr(self, attr_name: str, attr_val: Any):
        validate_type('attr_name', attr_name, str)
        validate_not_none('attr_val', attr_val)
        # If the attr is already set in the Note, just assign it a new value
        if attr_name in self._attr_names:
            self._attrs[self._attr_names[attr_name]] = attr_val
        # Else add the new attr
        else:
            next_attr_idx = self.num_attrs
            self._attr_names[attr_name] = next_attr_idx
            resize(self._attrs, (next_attr_idx + 1, 1))
            self._attrs[next_attr_idx] = attr_val

    def __getattr__(self, attr_name: str) -> float64:
        validate_type('attr_name', attr_name, str)
        return self.__dict__[attr_name]

    def __setattr__(self, attr_name: str, attr_val: Any):
        validate_type('attr_name', attr_name, str)
        validate_not_none('attr_val', attr_val)
        self.__dict__[attr_name] = attr_val

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

    @staticmethod
    @abstractmethod
    def copy(source_note: 'Note') -> 'Note':
        raise NotImplemented('Derived type must implement Note.copy() -> Note')

    @abstractmethod
    def __eq__(self, other: 'Note') -> bool:
        raise NotImplemented('Derived type must implement Note.__eq__() -> bool')

    @abstractmethod
    def __str__(self):
        raise NotImplemented('Derived type must implement Note.__str__()')
