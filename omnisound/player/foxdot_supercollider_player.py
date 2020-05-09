# Copyright 2018 Mark S. Weiss

from time import sleep

from FoxDot import Player as FD_SC_Player

# noinspection PyProtectedMember
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.player.player import Player, PlayerNoNotesException


class FoxDotSupercolliderPlayer(Player):
    def __init__(self, note_sequence: NoteSequence):
        super(FoxDotSupercolliderPlayer, self).__init__(note_sequence)
        self.sc_player = FD_SC_Player()

    def play_each(self):
        if not self.notes:
            raise PlayerNoNotesException('No notes to play')
        for note in self.notes:
            performance_attrs = note.pa.as_dict()
            self.sc_player >> note.instrument([note.degree],
                                              dur=note.dur,
                                              amp=note.amp,
                                              **performance_attrs)
            sleep(note.dur)
            self.sc_player.stop()

    def play(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        for note in self.notes:
            performance_attrs = note.pa.as_dict()
            self.sc_player >> note.instrument([note.degree],
                                              dur=note.dur,
                                              amp=note.amp,
                                              **performance_attrs)
            sleep(note.dur)
            self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('SupercolliderPlayer does not support improvising')
