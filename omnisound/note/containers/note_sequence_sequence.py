# Copyright 2019 Mark S. Weiss

from typing import List, Sequence, Tuple

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.utils.utils import (validate_optional_sequence_of_type, validate_sequence_of_type,
                                   validate_type, validate_types)


class NoteSequenceSequence(object):
    def __init__(self, note_seq_seq: List[NoteSequence]):
        validate_type('note_seq_seq', note_seq_seq, List)
        validate_optional_sequence_of_type('note_seq_seq', note_seq_seq, NoteSequence)
        self.note_seq_seq = note_seq_seq

    # TODO REFACTOR TO EXTEND
    # Measure list management
    def append(self, seq: NoteSequence) -> 'NoteSequenceSequence':
        validate_type('seq', seq, NoteSequence)
        self.note_seq_seq.append(seq)
        return self

    def extend(self, seqs: Sequence[NoteSequence]) -> 'NoteSequenceSequence':
        validate_sequence_of_type('seqs', seqs, NoteSequence)
        self.note_seq_seq.extend(seqs)
        return self

    def __add__(self, to_add: NoteSequence) -> 'NoteSequenceSequence':
        return self.append(to_add)

    def __lshift__(self, to_add: NoteSequence) -> 'NoteSequenceSequence':
        return self.append(to_add)

    def insert(self, index: int, to_add: NoteSequence) -> 'NoteSequenceSequence':
        validate_types(('index', index, int), ('to_add', to_add, NoteSequence))
        self.note_seq_seq.insert(index, to_add)
        return self

    def remove(self, to_remove: Tuple[int, int]) -> 'NoteSequenceSequence':
        validate_type('to_remove', to_remove, Tuple)
        validate_sequence_of_type('to_remove', to_remove, int)
        del self.note_seq_seq[to_remove[0]:to_remove[1]]
        return self
    # /Measure list management

    # Iter / slice support
    def __len__(self) -> int:
        return len(self.note_seq_seq)

    def __getitem__(self, index: int) -> NoteSequence:
        validate_type('index', index, int)
        if abs(index) >= len(self.note_seq_seq):
            raise IndexError(f'`index` out of range index: {index} len(note_seq_seq): {len(self.note_seq_seq)}')
        return self.note_seq_seq[index]

    def __iter__(self) -> 'NoteSequenceSequence':
        self.index = 0
        return self

    def __next__(self) -> NoteSequence:
        if self.index == len(self.note_seq_seq):
            raise StopIteration
        note_seq = self.note_seq_seq[self.index]
        self.index += 1
        return note_seq

    def __eq__(self, other: 'NoteSequenceSequence') -> bool:
        if not other or len(self) != len(other):
            return False
        return all([note_seq == other.note_seq_seq[i] for i, note_seq in enumerate(self.note_seq_seq)])

    @staticmethod
    def copy(other: 'NoteSequenceSequence'):
        return NoteSequenceSequence([NoteSequence.copy(note_seq) for note_seq in other.note_seq_seq])
    # /Iter / slice support
