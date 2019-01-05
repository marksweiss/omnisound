# Copyright 2018 Mark S. Weiss

from time import sleep

import midi.

from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.player.player import Player, PlayerNoNotesException


class MidiPlayer(Player):
    def __init__(self, note_sequence: NoteSequence):
        super(MidiPlayer, self).__init__(note_sequence)

    def play_each(self):
        if not self.notes:
            raise PlayerNoNotesException('No notes to play')
        # for note in self.notes:
        #     performance_attrs = note.pa.as_dict()
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def play_all(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        # for note in self.notes:
        #     performance_attrs = note.pa.as_dict()
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')
