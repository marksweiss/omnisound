# Copyright 2018 Mark S. Weiss

from typing import List, Union

from aleatoric.note import Note
from aleatoric.performance_attrs import PerformanceAttrs
from aleatoric.utils import (validate_optional_type,
                             validate_sequence_of_types, validate_type,
                             validate_type_choice)


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
