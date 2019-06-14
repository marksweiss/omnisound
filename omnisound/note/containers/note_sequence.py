# Copyright 2018 Mark S. Weiss

from typing import Sequence, Union

from omnisound.note.adapters.note import Note
from omnisound.utils.utils import validate_type


class NoteSequence(object):
    """Provides an iterator abstraction over a collection of Notes. If performance_attrs
       are provided, they will be applied to all Notes in the sequence if the notes are
       retrieved through the iterator. Otherwise performance_attrs that are an attribute
       of the note will be used.

       Thus, this lets clients create either type of sequence and transparently just consume
       through the iterator Notes with correct note_attrs and perf_attrs.
    """
    def __init__(self, notes: Sequence[Note] = None, child_sequences: Sequence[Sequence[Note]] = None):
        self.notes = list(notes)
        self.child_sequences = child_sequences
        self.index = 0

    # Manage iter / slice
    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, index: int) -> Note:
        validate_type('index', index, int)
        if abs(index) >= len(self.notes):
            raise ValueError(f'`index` out of range index: {index} len(notes): {len(self.notes)}')
        return self.notes[index]

    def __iter__(self) -> 'NoteSequence':
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    def __next__(self) -> Note:
        if self.index == len(self.notes):
            raise StopIteration
        note = self.notes[self.index]
        self.index += 1
        return note

    def __eq__(self, other: 'NoteSequence') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([self.notes[i] == other.notes[i] for i in range(len(self.notes))])
    # /Manage iter / slice

    # Manage note list
    def append(self, note: Note) -> 'NoteSequence':
        validate_type('note', note, Note)
        self.notes.append(note)
        return self

    def extend(self, new_notes: Union['NoteSequence', Sequence[Note]]) -> 'NoteSequence':
        self.notes.extend(new_notes)
        return self

    def __add__(self, to_add: Union[Note, 'NoteSequence', Sequence[Note]]) -> 'NoteSequence':
        """Overloads the `+` operator to support adding a single Note, a NoteSequence or a List[Note]"""
        if isinstance(to_add, Note):
            return self.append(to_add)
        else:
            return self.extend(to_add)

    def __lshift__(self, to_add: Union[Note, 'NoteSequence', Sequence['Note']]) -> 'NoteSequence':
        return self.__add__(to_add)

    def insert(self, index: int, to_add: Union[Note, 'NoteSequence', Sequence[Note]]) -> 'NoteSequence':
        validate_type('index', index, int)

        try:
            validate_type('to_add', to_add, Note)
            self.notes.insert(index, to_add)
            return self
        except ValueError:
            pass

        for note in to_add:
            self.notes.insert(index, note)
            # Necessary to insert in the same order as input, rather than reverse order from the input
            index += 1

        return self

    def remove(self, to_remove: Union[Note, 'NoteSequence', Sequence[Note]]):
        try:
            validate_type('to_remove', to_remove, Note)
            self.notes.remove(to_remove)
            return self
        except ValueError:
            pass

        for note in to_remove:
            self.notes.remove(note)

        return self
    # /Manage note list

    @staticmethod
    def copy(source_note_sequence: 'NoteSequence') -> 'NoteSequence':
        # Call the copy() for the subclass of this note type
        new_notes = [(note.__class__.copy(note)) for note in source_note_sequence.notes]
        new_note_sequence = NoteSequence(notes=new_notes)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence
