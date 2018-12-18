# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from aleatoric.scale_globals import (MajorKey, MinorKey)
from aleatoric.utils import (validate_sequence_of_types, validate_optional_type,
                             validate_not_none, validate_type, validate_type_choice)


class PerformanceAttrsFrozenException(Exception):
    pass


class PerformanceAttrs(object):
    """Open container for dynamically adding performance attributes to a Note. These attributes
       govern the behavior of the Instrument playing the Note, and not attributes of the Note itself.
       So for example they might parameterize `vibrato` or `tremolo` in a SupercolliderNote.

       Different instruments on different platforms expose different parameters, so this class has no
       fixed attributes. So instead it is just an API for adding attributes in a type-safe way.
       The API lets the caller add an attribute by name and type, and dynamically adds the attribute
       and a validator for it.

       Usage:
       - call add_attr(name, type) for each attribute you want to add
       - call freeze() when you want to make the object read-only
    """
    DEFAULT_NAME = 'PERF_ATTRS'

    def __init__(self, name: str = None):
        self.attr_type_map: Dict[str, Any] = {}
        self.name: str = name or PerformanceAttrs.DEFAULT_NAME
        self.frozen: bool = False

    def add_attr(self, attr_name: str = None, val: Any = None, attr_type: Any = None):
        validate_type('attr_name', attr_name, str)
        validate_not_none('attr_type', attr_type)
        if self.frozen:
            raise PerformanceAttrsFrozenException((f'Attempt to set attribute: {attr_name} '
                                                   f'on frozen PerformanceConfigFactory: {self.name}'))
        self.attr_type_map[attr_name] = attr_type
        setattr(self, attr_name, val)

    def safe_set_attr(self, attr_name, val):
        if attr_name not in self.attr_type_map:
            raise ValueError('Invalid attribute name')
        # noinspection PyTypeHints
        if not isinstance(val, self.attr_type_map[attr_name]):
            raise ValueError(f'val: {val} must be of type: {self.attr_type_map[attr_name]}')
        setattr(self, attr_name, val)

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def is_frozen(self) -> bool:
        return self.frozen

    def __str__(self):
        return ' '.join([f'{attr_name}: {getattr(self, attr_name)}' for attr_name in self.attr_type_map.keys()])

    def as_dict(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.attr_type_map.keys()}


class NoteConfig(ABC):
    @abstractmethod
    def as_dict(self) -> Dict:
        raise NotImplemented('Derived type must implement NoteConfig.as_dict() -> Dict')


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

    @staticmethod
    @abstractmethod
    def get_config() -> NoteConfig:
        """Return a dict config object to be used for convenient note construction. Allows client to construct
           and pass in this object as one arg with `**config` syntax rather than type out all five kw args.
        """
        raise NotImplemented('Derived type must implement Note.get_config() -> NoteConfig')

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

    @abstractmethod
    def get_pitch_for_key(self, key: Union[MajorKey, MinorKey], octave: int) -> Any:
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


class NoteSequence(object):
    """Provides an iterator abstraction over a collection of Notes. If performance_attrs
       are provided, they will be applied to all Notes in the sequence if the notes are
       retrieved through the iterator. Otherwise performance_attrs that are an attribute
       of the note will be used.

       Thus, this lets clients create either type of sequence and transparently just consume
       through the iterator Notes with correct note_attrs and perf_attrs.
    """
    def __init__(self, note_list: List[Note], performance_attrs: PerformanceAttrs = None):
        validate_sequence_of_types('note_list', note_list, Note)
        validate_optional_type('performance_attrs', performance_attrs, PerformanceAttrs)

        self.index = 0
        self.note_list = note_list
        self.performance_attrs = performance_attrs

    @property
    def nl(self):
        """Get the underlying note_list.
           Alias to something shorter for client code convenience.
        """
        return self.note_list

    @property
    def pa(self):
        """Get the underlying performance_attrs.
           Alias to something shorter for client code convenience.
        """
        return self.performance_attrs

    def append(self, note: Note):
        validate_type('note', note, Note)
        self.note_list.append(note)
        return self

    def extend(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        new_note_list = None
        # Support either NoteSequence or a List[Note]
        try:
            validate_type('to_add', to_add, NoteSequence)
            new_note_list = to_add.note_list
        except ValueError:
            pass
        if not new_note_list:
            validate_sequence_of_types('to_add', to_add, Note)
            new_note_list = to_add
        self.note_list.extend(new_note_list)

        return self

    def __len__(self):
        return len(self.note_list)

    def __add__(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Overloads operator + to support appending either single notes or sequences
           Tries to treat `to_add` as a Note and then as a NoteSequence. If both
           fail then it raises the last exception handled. If either succeeds
           then the operation is a success and the Note or NoteList are appended.
        """
        # Try to add as a single Note
        try:
            validate_type('to_add', to_add, Note)
            # If validation did not throw, to add is a single note, append(note)
            self.append(to_add)
            # Return self supports += without any additional code
            return self
        except ValueError:
            pass
        # If we didn't add as a single note, try to add as a NoteSequence
        # NOTE: This is crucial to the design, because any specialized sequence derived from NoteSequence, such
        # as Measure and Chord, can add its notes to any other NoteSequence
        try:
            validate_type('to_add', to_add, NoteSequence)
            # Don't need to validate NoteList because that is validated when NoteSequence constructed
            self.extend(to_add.note_list)
            return self
        except ValueError:
            pass
        # If we didn't add as a single note or NoteSequence, try to add as a List[Note]
        try:
            validate_sequence_of_types('to_add', to_add, Note)
            # If validation did not throw, to add is a list of notes, extend(note_list)
            self.extend(to_add)
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to __add__() must be a Note, NoteSequence or List[Note], arg: {to_add}')

    def __lshift__(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Support `note_seq << note` syntax for appending notes to a sequence as well as `a + b`"""
        return self.__add__(to_add)

    def insert(self, index: int, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Inserts a single note, all notes in a List[Note] or all notes in a NoteSequence.
           in stack order, i.e. reverse order of the input
        """
        validate_type('index', index, int)

        try:
            validate_type_choice('to_add', to_add, (Note, NoteSequence))
            if isinstance(to_add, Note):
                self.note_list.insert(index, to_add)
            else:
                for note in to_add.note_list:
                    self.note_list.insert(index, note)
                    # Necessary to insert in the same order as input, rather than reverse order from the input
                    index += 1
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_types('to_add', to_add, Note)
            for note in to_add:
                self.note_list.insert(index, note)
                # Necessary to insert in the same order as input, rather than reverse order from the input
                index += 1
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to insert() must be a Note, NoteSequence or List[Note], arg: {to_add}')

    def remove(self, to_remove: Union[Note, 'NoteSequence', List[Note]]):
        """Removes a single note, all notes in a List[Note] or all notes in a NoteSequence
        """

        # Swallow exception if the item to be removed is not present in note_list
        def _remove(note):
            try:
                self.note_list.remove(note)
            except ValueError:
                pass

        try:
            validate_type_choice('to_add', to_remove, (Note, NoteSequence))
            if isinstance(to_remove, Note):
                _remove(to_remove)
            else:
                for note in to_remove.note_list:
                    _remove(note)
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_types('to_add', to_remove, Note)
            for note in to_remove:
                _remove(note)
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to remove() must be a Note, NoteSequence or List[Note], arg: {to_remove}')

    def __getitem__(self, index: int) -> Note:
        validate_type('index', index, int)
        if abs(index) >= len(self.note_list):
            raise ValueError(f'`index` out of range index: {index} len(note_list): {len(self.note_list)}')
        return self.note_list[index]

    def __iter__(self) -> 'NoteSequence':
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    def __next__(self) -> Note:
        """Always return a Note object with note_attrs and perf_attrs populated.
           This is the contract clients can expect, and thus this iterator hides
           where perf_attrs came from and always returns a Note ready for use.
           Also this deep copy prevents altering the sequence by reference so
           it can be used and reused.
        """
        if self.index == len(self.note_list):
            raise StopIteration
        note = self.note_list[self.index]
        # perf_attrs comes from the NoteSequence if present, otherwise from the Note
        self.index += 1
        return note.__class__.copy(note)

    def __eq__(self, other):
        if not other or len(self) != len(other):
            return False
        return all([self.note_list[i] == other.note_list[i] for i in range(len(self.note_list))])

    @staticmethod
    def copy(source_note_sequence: 'NoteSequence') -> 'NoteSequence':
        # Call the copy() for the subclass of this note type
        new_note_list = [(note.__class__.copy(note)) for note in source_note_sequence.note_list]
        new_note_sequence = NoteSequence(new_note_list,
                                         source_note_sequence.performance_attrs)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence


if __name__ == '__main__':
    print("Imported")