# Copyright 2018 Mark S. Weiss

from typing import List, Union

from aleatoric.note import Note
from aleatoric.utils import validate_optional_type, validate_sequence_of_type, validate_type


class NoteSequence(object):
    """Provides an iterator abstraction over a collection of Notes. If performance_attrs
       are provided, they will be applied to all Notes in the sequence if the notes are
       retrieved through the iterator. Otherwise performance_attrs that are an attribute
       of the note will be used.

       Thus, this lets clients create either type of sequence and transparently just consume
       through the iterator Notes with correct note_attrs and perf_attrs.
    """
    def __init__(self, to_add: Union[List[Note], 'NoteSequence']):
        # Support constructing with empty note_list
        if to_add == list():
            self.note_list = to_add
        else:
            self.note_list = NoteSequence._get_note_list_from_sequence('to_add', to_add)
            if not self.note_list:
                raise ValueError((f'Arg `to_add` must be a NoteSequence or List[Note], '
                                  f'arg: {to_add} type: {type(to_add)}'))

        self.index = 0

    # Manage Note properties
    @property
    def nl(self):
        """Get the underlying note_list. Alias to something shorter for client code convenience.
        """
        return self.note_list
    # /Manage Note properties

    # Manage note list
    def append(self, note: Note) -> 'NoteSequence':
        validate_type('note', note, Note)
        self.note_list.append(note)
        return self

    def extend(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Supports adding a single Note, a NoteSequence or a List[Note]"""

        new_note_list = None
        # Test adding as a NoteSequence
        try:
            validate_type('to_add', to_add, NoteSequence)
            new_note_list = to_add.note_list
            self.note_list.extend(new_note_list)
        except ValueError:
            pass

        # If NoteSequence failed test adding as a List[Note]
        if not new_note_list:
            try:
                validate_sequence_of_type('to_add', to_add, Note)
                new_note_list = to_add
                self.note_list.extend(new_note_list)
            except ValueError:
                pass

        # If both failed add as a Note
        if not new_note_list:
            try:
                validate_type('to_add', to_add, Note)
                self.note_list.append(to_add)
            except ValueError:
                raise ValueError((f'Arg `to_add` must be a Note, NoteSequence or List[Note], '
                                  f'arg: {to_add} type: {type(to_add)}'))

        return self
    # /Manage note list

    def __add__(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Overloads the `+` operator to support adding a single Note, a NoteSequence or a List[Note]"""
        return self.extend(to_add)

    def __lshift__(self, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Overloads the `<<` operator to support adding a single Note, a NoteSequence or a List[Note]"""
        """Support `note_seq << note` syntax for appending notes to a sequence as well as `a + b`"""
        return self.extend(to_add)

    @staticmethod
    def _get_note_list_from_sequence(sequence_name, sequence):
        note_list = None

        try:
            validate_type(sequence_name, sequence, NoteSequence)
            note_list = sequence.note_list
        except ValueError:
            pass

        if not note_list:
            try:
                validate_sequence_of_type(sequence_name, sequence, Note)
                note_list = sequence
            except ValueError:
                pass
                return None

        return note_list

    def insert(self, index: int, to_add: Union[Note, 'NoteSequence', List[Note]]) -> 'NoteSequence':
        """Inserts a single note, all notes in a List[Note] or all notes in a NoteSequence.
           in stack order, i.e. reverse order of the input
        """
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Note)
            self.note_list.insert(index, to_add)
            return self
        except ValueError:
            pass

        note_list = NoteSequence._get_note_list_from_sequence('to_add', to_add)
        if not note_list:
            raise ValueError((f'Arg `to_add` must be a Note, NoteSequence or List[Note], '
                              f'arg: {to_add} type: {type(to_add)}'))
        for note in note_list:
            self.note_list.insert(index, note)
            # Necessary to insert in the same order as input, rather than reverse order from the input
            index += 1

        return self

    def remove(self, to_remove: Union[Note, 'NoteSequence', List[Note]]):
        """Removes a single note, all notes in a List[Note] or all notes in a NoteSequence
        """
        try:
            validate_type('to_remove', to_remove, Note)
            self.note_list.remove(to_remove)
            return self
        except ValueError:
            pass

        if not NoteSequence._get_note_list_from_sequence('to_remove', to_remove):
            raise ValueError((f'Arg `to_remove` must be a Note, NoteSequence or List[Note], '
                              f'arg: {to_remove} type: {type(to_remove)}'))

        for note in to_remove:
            self.note_list.remove(note)

        return self

    # Manage iter / slice
    def __len__(self) -> int:
        return len(self.note_list)

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

    def __eq__(self, other: 'NoteSequence') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.note_list[i] == other.note_list[i] for i in range(len(self.note_list))])
    # /Manage iter / slice

    @staticmethod
    def copy(source_note_sequence: 'NoteSequence') -> 'NoteSequence':
        # Call the copy() for the subclass of this note type
        new_note_list = [(note.__class__.copy(note)) for note in source_note_sequence.note_list]
        new_note_sequence = NoteSequence(to_add=new_note_list)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence
