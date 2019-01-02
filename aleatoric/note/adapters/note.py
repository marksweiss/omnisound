# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.generators.scale_globals import MajorKey, MinorKey


class NoteConfig(object):
    def __init__(self, fields):
        self._fields = fields
        for field in fields:
            setattr(self, field, None)

    def as_dict(self) -> Dict:
        return {field: getattr(self, field) for field in self._fields}

    def as_list(self) -> List:
        return [getattr(self, field) for field in self._fields]


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
       the information in the note.

       Finally, each note is responsible for being able to translate a musical key (pitch on a scale) to a valid
       pitch value for that Note's backend, in the `get_pitch_for_key()` method.

       It is is strongly preferred that all getter properties return self in derived classes
       to support fluid interfaces and defining notes most easily in the least number of lines.
    """

    DEFAULT_NAME = 'Note'

    def __init__(self, name: str = None):
        self._name = name or Note.DEFAULT_NAME

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    @abstractmethod
    def instrument(self):
        raise NotImplemented('Derived type must implement Note.instrument')

    @instrument.setter
    @abstractmethod
    def instrument(self, instrument):
        raise NotImplemented('Derived type must implement Note.instrument')

    @property
    @abstractmethod
    def start(self):
        raise NotImplemented('Derived type must implement Note.start')

    @start.setter
    @abstractmethod
    def start(self, start):
        raise NotImplemented('Derived type must implement Note.start')

    @property
    @abstractmethod
    def dur(self):
        raise NotImplemented('Derived type must implement Note.dur')

    @dur.setter
    @abstractmethod
    def dur(self, dur):
        raise NotImplemented('Derived type must implement Note.dur')

    @property
    @abstractmethod
    def amp(self):
        raise NotImplemented('Derived type must implement Note.amp')

    @amp.setter
    @abstractmethod
    def amp(self, amp):
        raise NotImplemented('Derived type must implement Note.amp')

    @property
    @abstractmethod
    def pitch(self):
        raise NotImplemented('Derived type must implement Note.pitch')

    @pitch.setter
    @abstractmethod
    def pitch(self, pitch):
        raise NotImplemented('Derived type must implement Note.pitch')

    @abstractmethod
    def i(self, instrument=None):
        """Fluent getter and setter that handles case of receiving an arg or not and either returns self as
           a setter or returns self._instrument as a getter.
        """
        raise NotImplemented('Derived type must implement Note.i')

    @abstractmethod
    def s(self, start=None):
        """Fluent getter and setter that handles case of receiving an arg or not and either returns self as
           a setter or returns self._start as a getter.
        """
        raise NotImplemented('Derived type must implement Note.s')

    @abstractmethod
    def d(self, dur=None):
        """Fluent getter and setter that handles case of receiving an arg or not and either returns self as
           a setter or returns self._dur as a getter.
        """
        raise NotImplemented('Derived type must implement Note.d')

    @abstractmethod
    def a(self, amp=None):
        """Fluent getter and setter that handles case of receiving an arg or not and either returns self as
           a setter or returns self._amp as a getter.
        """
        raise NotImplemented('Derived type must implement Note.a')

    @abstractmethod
    def p(self, pitch=None):
        """Fluent getter and setter that handles case of receiving an arg or not and either returns self as
           a setter or returns self._pitch as a getter.
        """
        raise NotImplemented('Derived type must implement Note.p')

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
