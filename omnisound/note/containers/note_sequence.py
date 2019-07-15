# Copyright 2018 Mark S. Weiss

# TODO ADD OPTIONALs TO ALL SIGNATURES
# TODO EQUALITY TESTS EVERYWHERE
# TOOD COPY TESTS

from typing import Any, Mapping, Iterator, Sequence, Tuple

import numpy as np

from omnisound.utils.utils import validate_optional_sequence_of_type, \
    validate_optional_type, validate_optional_type_choice, validate_sequence_of_type, validate_type, validate_types


class NoteSequenceInvalidAppendException(Exception):
    pass


class NoteSequence(object):
    """Provides an iterator abstraction over a collection of Notes. Also owns the storage for the collection
       of Notes as a Numpy array of rank 2. The shape of the array is the number of note attributes and the
       depth of it is the number of note_attr_vals.

       Because the underlying storage is fixed size, there is a default sequence length of 1, but the caller can
       pre-allocate by providing a value for the `num_notes` argument. If note_attr_vals are added exceeding the size
       of the array it is resized.

       Note that in this model a sequence of Notes exist upon the construction of a NoteSequence, even though
       no individual Note "objects" have been allocated. Each column in the array represents an attribute of a note.
       The first five columns always represent the attributes `instrument`, `start`, `duration`,
       `amplitude` and `pitch`. Additional attributes can be added through an OO interface, which causes the underlying
       array to be resized to add a column. So, note attributes and their representation exist at this level, for all
       can be manipulated in vector space through matrix operations.

       The Note base class and its derived classes form a second-level interface. Each Note when constructed is
       passed a reference to a row in a numpy array owned by a NoteSequence. So a Note is just a view over that
       row in the matrix and just an interface to read and write values for a single note, rather than manipulating
       all values at once.

       NOTE: Appending to a a child must be done directly and it also invalidates the range_map in any
       sequence that the child is a child_sequence of. If you want to modify a Sequence B that is in A.child_sequences,
       you must 1) modify B, and then 2) call A.update_range_map().
    """

    def __init__(self, make_note: Any = None,
                 num_notes: int = None,
                 num_attributes: int = None,
                 attr_name_idx_map: Mapping[str, int] = None,
                 attr_vals_defaults_map: Mapping[str, float] = None,
                 attr_get_type_cast_map: Mapping[str, Any] = None,
                 child_sequences: Sequence['NoteSequence'] = None):
        validate_types(('num_notes', num_notes, int), ('num_attributes', num_attributes, int),
                       ('attr_name_idx_map', attr_name_idx_map, dict))
        validate_optional_type('attr_vals_defaults_map', attr_vals_defaults_map, dict)
        validate_sequence_of_type('attr_name_idx_map', attr_name_idx_map.keys(), str)
        validate_sequence_of_type('attr_name_idx_map', attr_name_idx_map.values(), int)
        if attr_vals_defaults_map:
            validate_optional_sequence_of_type('attr_vals_map', list(attr_vals_defaults_map.keys()), str)
            validate_optional_sequence_of_type('attr_vals_map', list(attr_vals_defaults_map.values()), float)
        validate_optional_type_choice('child_sequences', child_sequences, (list, set))
        validate_optional_sequence_of_type('child_sequences', child_sequences, NoteSequence)

        self.make_note = make_note
        self.attr_get_type_cast_map = attr_get_type_cast_map

        # Construct empty 2D numpy array of the specified dimensions. Each row stores a Note's values.
        rows = [[0.0] * num_attributes for _ in range(num_notes)]
        self.note_attr_vals = np.array(rows)
        if num_notes > 0:
            # THIS MUST NOT BE ALTERED
            self._num_attributes = self.note_attr_vals.shape[1]

        self.attr_name_idx_map = attr_name_idx_map
        self.attr_vals_defaults_map = attr_vals_defaults_map
        if attr_vals_defaults_map:
            assert set(attr_vals_defaults_map.keys()) <= set(attr_name_idx_map.keys())
            self.attr_vals_defaults_map = attr_vals_defaults_map
            for note_attr in self.note_attr_vals:
                for attr_name, attr_val in self.attr_vals_defaults_map.items():
                    note_attr[self.attr_name_idx_map[attr_name]] = attr_val

        self.child_sequences = child_sequences or []

        # Absolute index position over all sequences, that is self.note_attr_vals and the note_attr_vals of each
        # child_sequence, and, recursively, any of its child sequences.
        # So if this sequence has 10 notes and it has one child sequence with 11 notes then self.index
        # will move from 0 to 20 and then reset to 0.
        self.index = 0
        self.range_map = {0: self}

    def note(self, index):
        return self._get_note_for_index(index)

    def update_range_map(self):
        # What we need is a data structure that defines the range of indexes covered by a particular NoteSequence
        # and maps that to a reference to that NoteSequence.
        # Example: This NoteSeq has 10 notes and it has two children, the first has 11 and the second has 12
        #          The _index_range_map is: {10: self, 21: child_1, 33: child_2}
        def _update_seq_subtree(update_seq, seqs_queue):
            seqs_queue.append(update_seq)
            for child in update_seq.child_sequences:
                _update_seq_subtree(child, seqs_queue)
        child_seqs_queue = []
        for child_seq in self.child_sequences:
            _update_seq_subtree(child_seq, child_seqs_queue)

        last_index = len(self.note_attr_vals)
        for seq in child_seqs_queue:
            self.range_map[last_index] = seq
            # Only add the actual length of the next sequence, because len() is overloaded for this type
            # and gets the last key and sequence in the range map and adds the key to the length of that sequence's
            # note_attr_vals. So if we take len(sequences) here rather than len(sequence.note_attr_vals) we will
            # double count the last sequence in the current range_map
            last_index += len(seq.note_attr_vals)

    # Manage iter / slice
    def __len__(self) -> int:
        k, v = tuple(self.range_map.items())[-1]
        return k + len(v.note_attr_vals)

    # noinspection PyCallingNonCallable
    def _get_note_for_index(self, index: int) -> Any:
        """Factory method to construct a Note over a stored Note value at an index in the underlying array"""
        validate_type('index', index, int)
        if index >= len(self):
            raise IndexError(f'`index` out of range index: {index} max_index: {len(self)}')
        # Simple case, index is in the range of self.attrs
        if index < len(self.note_attr_vals):
            return self.make_note(self.note_attr_vals[index],
                                  self.attr_name_idx_map,
                                  attr_get_type_cast_map=self.attr_get_type_cast_map)
        # Index is above the range of self.note_attr_vals, so either it is in the range of one of the recursive
        # flattened sequence of child_sequences, or it's invalid
        else:
            index_range_sum = len(self.note_attr_vals)
            for index_range in self.range_map.keys():
                # Dict keys are in order they were written, so ascending order, so each one is the max index
                # for that range. So the first entry it is less than is the entry it is in range of.
                if index < index_range:
                    # Get the note attrs for the note_sequence for the range this index is in
                    note_attrs = self.range_map[index_range]
                    # Adjust index to access the note_attr_vals with offset of 0. The index entry from range_map
                    # is the running sum of all the previous indexes so we need to subtract that from index
                    adjusted_index = index - index_range_sum
                    return self.make_note(note_attrs[adjusted_index],
                                          self.attr_name_idx_map,
                                          attr_get_type_cast_map=self.attr_get_type_cast_map)
                    # noinspection PyUnreachableCode
                    break
                index_range_sum += index_range

    def __getitem__(self, index: int) -> Any:
        return self._get_note_for_index(index)

    def __iter__(self) -> Iterator[Any]:
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    # noinspection PyCallingNonCallable
    def __next__(self) -> Any:
        if self.index == len(self):
            raise StopIteration
        note = self._get_note_for_index(self.index)
        self.index += 1
        return note

    # noinspection PyCallingNonCallable
    def make_notes(self) -> Sequence[Any]:
        notes = []
        for note_seq in self.range_map.values():
            notes.extend([self.make_note(note_seq.note_attr_vals[i],
                                         self.attr_name_idx_map,
                                         attr_get_type_cast_map=self.attr_get_type_cast_map)
                          for i in range(note_seq.note_attr_vals.shape[0])])
        return notes

    def __eq__(self, other: 'NoteSequence') -> bool:
        # All child sequences must match and the notes in self in both NoteSequences must match
        if len(self.child_sequences) != len(other.child_sequences):
            return False
        if not np.array_equal(self.note_attr_vals, other.note_attr_vals):
            return False
        for i, note_sequence in enumerate(self.child_sequences):
            if not np.array_equal(note_sequence, other.child_sequences[i]):
                return False
        return True
    # /Manage iter / slice

    # Manage note list
    def append(self, note: Any) -> 'NoteSequence':
        """NOTE: This only supports appending notes to this NoteSequence, not any of its children.
        """
        # Handle case of adding note to a currently empty sequence
        if len(self.note_attr_vals) and self.note_attr_vals[0].shape != note.note_attr_vals.shape:
            raise NoteSequenceInvalidAppendException(
                    'Note added to a NoteSequence must have the same number of attributes')
        # Either this is the first note in the sequence, or it's not and we validated its shape conforms
        num_attributes = note.note_attr_vals.shape[0]
        new_note_idx = len(self.note_attr_vals)
        # noinspection PyTypeChecker
        self.note_attr_vals.resize(new_note_idx + 1, num_attributes)
        np.copyto(self.note_attr_vals[new_note_idx], note.note_attr_vals)
        self.update_range_map()
        return self

    def append_child_sequence(self, child_sequence: 'NoteSequence') -> 'NoteSequence':
        if id(self) == id(child_sequence):
            raise ValueError('Cycle detected! Attempt to append a NoteSequence to itself as a child sequence.')
        validate_type('child_sequence', child_sequence, NoteSequence)
        self.child_sequences.append(child_sequence)
        self.update_range_map()
        return self

    def extend(self, note_sequence: 'NoteSequence') -> 'NoteSequence':
        validate_type('note_sequence', note_sequence, NoteSequence)
        if len(self.note_attr_vals) and self.note_attr_vals[0].shape != note_sequence.note_attr_vals[0].shape:
            raise NoteSequenceInvalidAppendException(
                'NoteSequence extended to a NoteSequence must have the same number of attributes')
        # Either this is the first note in the sequence, or it's not
        # If it is, make this sequence the note_attr_vals of this sequence. If it is not, append these notes
        # to the existing sequence -- we have already confirmed the shapes conform if  existing sequence is not empty.
        if len(self.note_attr_vals):
            self.note_attr_vals = np.concatenate((self.note_attr_vals, note_sequence.note_attr_vals))
        else:
            self.note_attr_vals = np.copy(note_sequence.note_attr_vals)
        self.update_range_map()
        return self

    def __add__(self, to_add: Any) -> 'NoteSequence':
        """Overloads the `+` operator to support adding a single Note, a NoteSequence or a List[Note]"""
        if isinstance(to_add, NoteSequence):
            return self.extend(to_add)
        else:
            return self.append(to_add)

    def __lshift__(self, to_add: Any) -> 'NoteSequence':
        return self.__add__(to_add)

    def insert(self, index: int, to_add: Any) -> 'NoteSequence':
        validate_type('index', index, int)

        new_notes = to_add.note_attr_vals
        if len(new_notes.shape) == 1:
            new_notes_num_attributes = new_notes.shape[0]
        else:
            new_notes_num_attributes = new_notes.shape[1]
        if len(self.note_attr_vals):
            num_attributes = self.note_attr_vals.shape[1]
        else:
            num_attributes = 0
        if num_attributes and num_attributes != new_notes_num_attributes:
            raise NoteSequenceInvalidAppendException(
                    'NoteSequence inserted into a NoteSequence must have the same number of attributes')

        if len(self.note_attr_vals):
            self.note_attr_vals = np.insert(self.note_attr_vals, index, new_notes, axis=0)
        else:
            # Must copy the list of the underlying note array to initialize storage for a NoteSequence
            # because NoteSequence arrays are 2D
            if len(new_notes.shape) == 1:
                new_notes = [new_notes]
            self.note_attr_vals = np.copy(new_notes)

        self.update_range_map()
        return self

    def remove(self, range_to_remove: Tuple[int, int]) -> 'NoteSequence':
        assert len(range_to_remove) == 2
        validate_sequence_of_type('range_to_remove', range_to_remove, int)
        # noinspection PyTupleAssignmentBalance
        range_start, range_end = range_to_remove
        self.note_attr_vals = np.delete(self.note_attr_vals, range(range_start, range_end), axis=0)

        self.update_range_map()
        return self

    @staticmethod
    def copy(source: 'NoteSequence') -> 'NoteSequence':
        validate_type('source', source, NoteSequence)
        copy = NoteSequence(make_note=source.make_note,
                            num_notes=len(source),
                            num_attributes=source._num_attributes,
                            attr_name_idx_map=source.attr_name_idx_map,
                            attr_vals_defaults_map=source.attr_vals_defaults_map,
                            child_sequences=source.child_sequences)
        # Copy the underlying np array from source note to target
        copy.note_attr_vals = np.copy(source.note_attr_vals)
        return copy

    # /Manage note list
