# Copyright 2018 Mark S. Weiss

from time import sleep

from abc import abstractmethod, ABCMeta
from typing import List

from FoxDot import Player as SC_Player
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as sc_sd_pluck

from note import Note, PerformanceAttrs, SupercolliderNoteAttrs


class Player(metaclass=ABCMeta):

    # TODO ADD play_all() and figure out "note group" with one perf_attr_config for all note_attrs

    @abstractmethod
    def play_each(self):
        raise NotImplementedError()

    def __init__(self, notes: List[Note]):
        # Only validate if the list is not empty
        if notes is not None and notes:
            # All elements are a subclass of Note. This still allows heterogeneous Notes.
            for n in notes:
                if not isinstance(n, Note):
                    raise ValueError(f'arg notes must be None or empty list or type List[Note]')
        self.notes = notes


class SupercolliderPlayer(Player):
    def __init__(self, notes: List[Note]):
        super(SupercolliderPlayer, self).__init__(notes)
        self.sc_player = SC_Player()

    def play_each(self):
        ret = self.sc_player >> sc_sd_pluck()
        print(ret)
        print(sc_sd_pluck)
        print(sc_sd_pluck())
        for n in self.notes:
            self.sc_player >> n.note_attrs.instrument([n.note_attrs.degree],
                                                      dur=n.note_attrs.dur,
                                                      amp=n.note_attrs.amp,
                                                      **n.performance_attrs.asdict())
            sleep(n.note_attrs.dur)


if __name__ == '__main__':
    note_attrs = SupercolliderNoteAttrs(synth_def=sc_sd_pluck,
                                        delay=0, dur=1.0, amp=1.0, degree=1,
                                        name='test_note',
                                        oct=4, scale='chromatic')
    performance_attrs = PerformanceAttrs()
    note = Note(note_attrs=note_attrs, performance_attrs=performance_attrs)
    notes = [note]
    player = SupercolliderPlayer(notes=notes)
    player.play_each()
