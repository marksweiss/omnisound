# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, List, Optional, Union

# from aleatoric.scale import MajorKey, MinorKey
from aleatoric.utils import (validate_sequence_of_types, validate_optional_type, validate_optional_types,
                             validate_not_none, validate_type, validate_type_choice, validate_types)


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


class Note(object):
    """Models the core attributes of a musical note common to multiple back ends"""

    name: Optional[str]
    DEFAULT_INSTRUMENT = '1'
    DEFAULT_START = 0.0
    DEFAULT_DUR = 0.0
    DEFAULT_AMP = 0.0
    DEFAULT_PITCH = 0.0
    DEFAULT_NAME = 'Note'

    def __init__(self, instrument: Any = None,
                 start: float = None, dur: float = None, amp: float = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None,
                 validate=True):
        if validate:
            validate_optional_types(('start', start, float), ('dur', dur, float), ('amp', amp, float),
                                    ('pitch', pitch, float), ('name', name, str),
                                    ('performance_attrs', performance_attrs, PerformanceAttrs))

        self.instrument = instrument or Note.DEFAULT_INSTRUMENT
        self.start = start or Note.DEFAULT_START
        self.dur = dur or Note.DEFAULT_DUR
        self.amp = amp or Note.DEFAULT_AMP
        self.pitch = pitch or Note.DEFAULT_PITCH
        self.name = name or Note.DEFAULT_NAME
        self.performance_attrs = performance_attrs or PerformanceAttrs()

    class NoteConfig(object):
        def __init__(self):
            self.instrument = None
            self.start = None
            self.dur = None
            self.amp = None
            self.pitch = None
            self.name = None

        def as_dict(self):
            return {
                'instrument': self.instrument,
                'start': self.start,
                'dur': self.dur,
                'amp': self.amp,
                'pitch': self.pitch,
                'name': self.name
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return Note.NoteConfig()

    @staticmethod
    def copy(source_note):
        validate_types(('start', source_note.start, float), ('dur', source_note.dur, float),
                       ('amp', source_note.amp, float), ('pitch', source_note.pitch, float))
        validate_optional_types(('name', source_note.name, str),
                                ('performance_attrs', source_note.performance_attrs, PerformanceAttrs))

        return Note(instrument=source_note.instrument,
                    start=source_note.start, dur=source_note.dur, amp=source_note.amp, pitch=source_note.pitch,
                    name=source_note.name,
                    performance_attrs=source_note.performance_attrs)

    def __eq__(self, other):
        """NOTE: equality of Notes is defined for note attributes only, not for performance attributes."""
        validate_types(('start', other.start, float), ('dur', other.dur, float),
                       ('amp', other.amp, float), ('pitch', other.pitch, float))
        return self.instrument == other.instrument and \
            self.start == other.start and \
            self.dur == other.dur and \
            self.amp == other.amp and \
            self.pitch == other.pitch

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} delay: {self.start:.5f} '
                f'dur: {self.dur:.5f} amp: {self.amp} pitch: {self.pitch:.5f}')

    @property
    def pa(self):
        """Get the underlying performance_attrs.
           Alias to something shorter for client code convenience.
        """
        return self.performance_attrs

    # TODO Signature should be get_pitch(self, key: Union[MajorKey, MinorKey], octave: int)
    #  But we elide the type information on the first argument to avoid a circular reference
    def get_pitch(self, key: Any, octave: int):
        raise NotImplemented('Note subtypes must implement get_pitch() and return valid pitch values for their type')


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