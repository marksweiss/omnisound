# Copyright 2018 Mark S. Weiss

from typing import Union

from chord_globals import ChordCls
from note_sequence import NoteSequence
from scale_globals import MajorKey, MinorKey, ScaleCls

# TODO init takes key and ChordCls and note_prototype, remove Scale
#  Constructs note_list of copies of prototype, for notes in Chord, which it gets from mingus
#  Construct NoteSeq from list
#  Staticmethod to return inversion of a Chord, take Chord as argument
#  Staticmethod to return the triad for a key and ScaleCls
#  Staticmethod to return all the triads in a key
class Chord(NoteSequence):

    def __init__(self, key: Union[MajorKey, MinorKey] = None, scale: ScaleCls = None,
                 chord: Chord = None):
        pass
        # m_notes =
