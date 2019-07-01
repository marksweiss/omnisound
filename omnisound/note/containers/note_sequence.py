# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, Iterator, Sequence, Union

import numpy as np

from omnisound.note.adapters.note import Note
from omnisound.utils.utils import validate_optional_sequence_of_type, \
    validate_optional_type, validate_optional_type_choice, validate_sequence_of_type, validate_type, \
    validate_type_choice, validate_type_reference, validate_types


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

    def __init__(self, note_cls: Any = None,
                 num_notes: int = None,
                 num_attributes: int = None,
                 attr_name_idx_map: Dict[str, int] = None,
                 attr_vals_defaults_map: Dict[str, float] = None,
                 child_sequences: Sequence['NoteSequence'] = None):
        validate_type_reference('note_cls', note_cls, Note)
        validate_types(('num_notes', num_notes, int), ('num_attributes', num_attributes, int),
                       ('attr_name_idx_map', attr_name_idx_map, dict))
        validate_optional_type('attr_vals_defaults_map', attr_vals_defaults_map, dict)
        validate_sequence_of_type('attr_name_idx_map', list(attr_name_idx_map.keys()), str)
        validate_sequence_of_type('attr_name_idx_map', list(attr_name_idx_map.values()), int)
        if attr_vals_defaults_map:
            validate_optional_sequence_of_type('attr_vals_map', list(attr_vals_defaults_map.keys()), str)
            validate_optional_sequence_of_type('attr_vals_map', list(attr_vals_defaults_map.values()), float)
        validate_optional_type_choice('child_sequences', child_sequences, (list, set))
        validate_optional_sequence_of_type('child_sequences', child_sequences, 'NoteSequence')

        self.note_cls = note_cls

        # Construct empty 2D numpy array of the specified dimensions. Each row stores a Note's values.
        rows = [[0.0] * num_attributes for _ in range(num_notes)]
        self.note_attr_vals = np.array(rows)
        # THIS MUST NOT BE ALTERED
        self._num_attributes = num_attributes

        self.attr_name_idx_map = attr_name_idx_map
        self.attr_vals_defaults_map = attr_vals_defaults_map
        self.child_sequences = child_sequences

        # Absolute index position over all sequences, that is self.note_attr_vals and the note_attr_vals of each
        # child_sequence, and, recursively, any of its child sequences.
        # So if this sequence has 10 notes and it has one child sequence with 11 notes then self.index
        # will move from 0 to 20 and then reset to 0.
        self.index = 0
        # We can't simply use the size of the 0th axis of the underlying numpy array because a sequence
        # can include child sequences, and `num_notes` is the total number of notes in the sequence and list
        # of child sequences
        self.num_notes = num_notes
        self._range_map_index = 0
        self.range_map = {}
        self.update_range_map()

    def _fast_update_range_map(self, num_entries: int):
        # Must copy into a new dict because we are modifying the keys
        new_range_map = {range_index + num_entries: child_seq
                         for range_index, child_seq in self.range_map.items()}
        self.range_map = new_range_map

    def _fast_append_range_map(self, new_entry: 'NoteSequence'):
        last_range_index = list(self.range_map.keys())[-1]
        self.range_map[last_range_index + len(new_entry.note_attr_vals)] = new_entry

    def update_range_map(self):
        # What we need is a data structure that defines the range of indexes covered by a particular NoteSequence
        # and maps that to a reference to that NoteSequence. This __next__() knows which NoteSequence (this one or
        # one of its children, recursively) it is traversing currently and to retrieve elements from it.
        # We traverse all sequences DFS and flatten that into one list
        # Each index has a length. Each index is mapped to a unique (increasing) integer key, which is the bound
        # of the range of index positions that are in that sequence.
        # Example: This NoteSeq has 10 notes and it has two children, the first has 11 and the second has 12
        #          The _index_range_map is: {10: self, 21: child_1, 33: child_2}
        # The algorithm in __next_() is to walk this, keeping track of the current total value of self.index. Each time
        # this value is above the current key value we increment _index_range_map_index and change the current reference
        # to a sequence to the next one in _index_range_map_index.values(). After we have visited all the keys in
        # _index_range_map we reset self.index and self._index_range_map_index to start over at the beginning
        if self.child_sequences:
            # Add entry in output range map for first child_seq in self.child_seqs
            # noinspection PyAttributeOutsideInit
            self._range_map = {len(self.note_attr_vals) + len(self.child_sequences[0]): self.child_sequences[0]}
            # Init the queue with the child seqs of self
            child_seqs_queue = [child for child in self.child_sequences]
            # Process the queue
            while child_seqs_queue:
                # Peek the front element, it's the next one we are processing
                cur_seq = child_seqs_queue[0]
                # Add the range entry for the element being processed, it's the next range entry
                self._range_map[list(self._range_map.keys())[-1] + len(cur_seq)] = cur_seq
                # Insert each child of the current entry in queue order at the front of the queue before
                # all siblings of the current node but after the current node.
                # So this is a combination of DFS and BFS. It's queue order processing of siblings bug then DFS
                # of each sibling (visit all its children before its sibling)
                for child_seq in reversed(cur_seq.child_sequences):
                    child_seqs_queue.insert(1, child_seq)
                # We are done processing current node. Pop it and then the next element we will process is either
                # this element's first child, just inserted, or it's next sibling if it had no children
                del child_seqs_queue[0]

            # Update num_notes with the last entry in range_map, this is the highest index in the flattened
            # sequence of all notes in self and all child_sequences
            self.num_notes = list(self._range_map.keys())[-1]

    # Manage iter / slice
    def __len__(self) -> int:
        return self.num_notes

    # noinspection PyCallingNonCallable
    def _get_note_for_index(self, index: int) -> Note:
        """Factory method to construct a Note over a stored Note value at an index in the underlying array"""
        validate_type('index', index, int)
        if index >= self.num_notes:
            raise ValueError(f'`index` out of range index: {index} max_index: {self.num_notes}')
        # Simple case, index is in the range of self.attrs
        if index < len(self.note_attr_vals):
            return self.note_cls(attr_vals=self.note_attr_vals[index],
                                 attr_name_idx_map=self.attr_name_idx_map,
                                 attr_vals_defaults_map=self.attr_vals_defaults_map,
                                 note_sequence_num=index)
        # Index is above the range of self.note_attr_vals, so either it is in the range of one of the recursive
        # flattened sequence of child_sequences, or it's invalid
        else:
            index_range_sum = len(self.note_attr_vals)
            for index_range in self._range_map.keys():
                # Dict keys are in order they were written, so ascending order, so each one is the max index
                # for that range. So the first entry it is less than is the entry it is in range of.
                if index < index_range:
                    # Get the note attrs for the note_sequence for the range this index is in
                    note_attrs = self._range_map[index_range]
                    # Adjust index to access the note_attr_vals with offset of 0. The index entry from range_map
                    # is the running sum of all the previous indexes so we need to subtract that from index
                    adjusted_index = index - index_range_sum
                    return self.note_cls(attrs=note_attrs[adjusted_index],
                                         attr_name_index_map=self.attr_name_idx_map,
                                         default_attr_vals_map=self.attr_vals_defaults_map,
                                         row_num=index)
                    # noinspection PyUnreachableCode
                    break
                index_range_sum += index_range

    def __getitem__(self, index: int) -> Note:
        return self._get_note_for_index(index)

    def __iter__(self) -> Iterator[Note]:
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    # noinspection PyCallingNonCallable
    def __next__(self) -> Note:
        if self.index == self.num_notes:
            raise StopIteration
        note = self._get_note_for_index(self.index)
        self.index += 1
        return note

    # noinspection PyCallingNonCallable
    def make_notes(self) -> Sequence[Note]:
        # Get the notes from this sequence
        notes = [self.note_cls(attrs=note_vals,
                               attr_name_index_map=self.attr_name_idx_map,
                               default_attr_vals_map=self.attr_vals_defaults_map,
                               row_num=i)
                 for i, note_vals in enumerate(self.note_attr_vals)]
        # Walk the range map, which is already in the flattened order, and append all notes from that in order
        for note_seq in self._range_map.values():
            notes.extend([self.note_cls(attrs=note_vals,
                                        attr_name_index_map=self.attr_name_idx_map,
                                        default_attr_vals_map=self.attr_vals_defaults_map,
                                        row_num=i)
                          for i, note_vals in enumerate(note_seq.note_attr_vals)])
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
    def append(self, note: Note) -> 'NoteSequence':
        """NOTE: This only supports appending notes to this NoteSequence, not any of its children.
        """
        validate_type('note', note, Note)
        if self.note_attr_vals[0].shape != note.__dict__['_attr_vals'].shape:
            raise NoteSequenceInvalidAppendException(
                    'Note added to a NoteSequence must have the same number of attributes')
        new_note_idx = len(self.note_attr_vals)
        # noinspection PyTypeChecker
        self.note_attr_vals.resize(new_note_idx + 1, self._num_attributes)
        np.copyto(self.note_attr_vals[new_note_idx], note.__dict__['_attr_vals'])
        self._fast_update_range_map(1)
        self.num_notes += 1
        return self

    def append_child_sequence(self, child_sequence: 'NoteSequence') -> 'NoteSequence':
        validate_type('child_sequence', child_sequence, NoteSequence)
        self.child_sequences.append(child_sequence)
        self._fast_append_range_map(child_sequence)
        return self

    def extend(self, note_sequence: 'NoteSequence') -> 'NoteSequence':
        validate_type('note_sequence', note_sequence, NoteSequence)
        if self.note_attr_vals[0].shape != note_sequence.note_attr_vals[0].shape:
            raise NoteSequenceInvalidAppendException(
                'NoteSequence extended to a NoteSequence must have the same number of attributes')
        self.note_attr_vals = np.concatenate((self.note_attr_vals, note_sequence.note_attr_vals))
        self._fast_update_range_map(len(note_sequence))
        self.num_notes += len(note_sequence)
        return self

    def __add__(self, to_add: Union[Note, 'NoteSequence']) -> 'NoteSequence':
        """Overloads the `+` operator to support adding a single Note, a NoteSequence or a List[Note]"""
        if isinstance(to_add, Note):
            return self.append(to_add)
        else:
            return self.extend(to_add)

    def __lshift__(self, to_add: Union[Note, 'NoteSequence']) -> 'NoteSequence':
        return self.__add__(to_add)

    def insert(self, index: int, to_add: Union[Note, 'NoteSequence']) -> 'NoteSequence':
        validate_type('index', index, int)
        validate_type_choice('to_add', to_add, (Note, NoteSequence))

        if isinstance(to_add, Note):
            new_notes = to_add.__dict__['_attr_vals']
        else:
            new_notes = to_add.note_attr_vals
        self.note_attr_vals = np.insert(self.note_attr_vals, index, new_notes, axis=0)

        self._fast_update_range_map(len(new_notes))
        self.num_notes += len(new_notes)
        return self

    def remove(self, to_remove: Union[Note, 'NoteSequence']):
        validate_type_choice('to_add', to_remove, (Note, NoteSequence))
        if isinstance(to_remove, Note):
            notes_to_remove = [to_remove]
        else:
            notes_to_remove = to_remove

        range_start = notes_to_remove[0].note_sequence_num
        range_end = notes_to_remove[-1].note_sequence_num + 1
        self.note_attr_vals = np.delete(self.note_attr_vals, range(range_start, range_end), axis=0)

        self._fast_update_range_map(-1)
        self.num_notes -= 1
        return self

    @staticmethod
    def copy(other: 'NoteSequence') -> 'NoteSequence':
        validate_type('other', other, NoteSequence)
        return NoteSequence(other.note_cls, other.num_notes, other._num_attributes,
                            other.attr_name_idx_map, other.attr_vals_defaults_map,
                            other.child_sequences)

    # /Manage note list
