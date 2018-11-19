# Copyright 2018 Mark S. Weiss

from abc import abstractmethod, ABC
from typing import List

from FoxDot import Player

from note import Note


class Player(ABC):

    @abstractmethod
    def play(self):
        raise NotImplementedError()

    def __init__(self, notes: List[Note] = None):
        # Only validate if the list is not empty
        if notes is not None and notes:
            # All elements are a subclass of Note. This still allows heterogeneous Notes.
            for note in notes:
                if not isinstance(note, Note):
                    raise ValueError(f'arg notes must be None or empty list or type List[Note]')
        self.notes = notes or list()


class SupercolliderPlayer(Player):

    def __init__(self, notes=None):
        super(SupercolliderPlayer, self).__init__(notes=notes)
        self.sc_player = Player()

    def play(self):
        for note in self.notes:
            self.sc_player >> note.note_attrs.instrument([note.note_attrs.degree],
                                                         dur=note.note_attrs.dur, amp=note.note_attrs.amp,
                                                         **note.performance_attrs.asdict())
