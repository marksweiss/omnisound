# Copyright 2018 Mark S. Weiss

from abc import abstractmethod, ABC
from typing import List

from FoxDot import Player
from FoxDot.lib.SCLang._SynthDefs import pluck as sc_sd_pluck

from note import Note, PerformanceAttrs, SupercolliderNote, SupercolliderNoteAttrs


class Player(ABC):

    # TODO ADD play_all() and figure out "note group" with one perf_attr_config for all note_attrs

    @abstractmethod
    def play_each(self):
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

    def play_each(self):
        for note in self.notes:
            self.sc_player >> note.note_attrs.instrument([note.note_attrs.degree],
                                                         dur=note.note_attrs.dur, amp=note.note_attrs.amp,
                                                         **note.performance_attrs.asdict())


if __name__ == '__main__':
    note_attrs = SupercolliderNoteAttrs(synth_def=sc_sd_pluck(), dur=1.0, amp=0.5, degree=1,
                                        name='test_note', oct=5, scale='chromatic')
    performance_attrs = PerformanceAttrs()
    note = Note(note_attrs=note_attrs, performance_attrs=performance_attrs)
    player = SupercolliderPlayer(notes=[note])
    player.play_each()
