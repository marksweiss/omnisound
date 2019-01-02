# Copyright 2018 Mark S. Weiss

from time import sleep

from FoxDot import Player as FD_SC_Player
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import sinepad as fd_sc_synth

from note.adapters.foxdot_supercollider_note import FIELDS, FoxDotSupercolliderNote
from aleatoric.note import NoteConfig, PerformanceAttrs
from note.containers.note_sequence import NoteSequence
from aleatoric.player import Player, PlayerNoNotesException


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

    def play_all(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        for note in self.notes:
            performance_attrs = self.notes.pa or note.pa.as_dict()
            self.sc_player >> note.instrument([note.degree],
                                              dur=note.dur,
                                              amp=note.amp,
                                              **performance_attrs)
            sleep(note.dur)
            self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('SupercolliderPlayer does not support improvising')


if __name__ == '__main__':
    # This is a test
    performance_attrs = PerformanceAttrs()

    notes = []
    note_config = NoteConfig(FIELDS)
    note_config.name = 'test_note'
    note_config.synth_def = fd_sc_synth
    note_config.amp = 1.0
    note_config.oct = 2
    note_config.scale = 'lydian'
    idur = 1.0
    delay = 0.0
    for i in range(15):
        note_config.delay = int(round(delay, 5))
        note_config.dur = round(idur - ((i + 1) * 0.05), 5)
        note_config.degree = i % 5
        note = FoxDotSupercolliderNote(**note_config.as_dict(), performance_attrs=performance_attrs)
        notes.append(note)
        delay += note_config.dur

    note_sequence = NoteSequence(notes)
    player = FoxDotSupercolliderPlayer(note_sequence)
    player.play_each()

    sleep(3)

    notes = []
    note_config.name = 'test_note'
    note_config.synth_def = fd_sc_synth
    note_config.amp = 1.0
    note_config.oct = 5
    note_config.scale = 'chromatic'
    idur = 1.0
    delay = 0.0
    for i in range(15):
        note_config.delay = round(delay, 5)
        note_config.dur = round(idur - ((i + 1) * 0.05), 5) * 0.5
        note_config.degree = i % 5
        note = FoxDotSupercolliderNote(**note_config.as_dict(), performance_attrs=performance_attrs)
        notes.append(note)
        delay += note_config.dur

    note_sequence = NoteSequence(notes)
    player = FoxDotSupercolliderPlayer(note_sequence)
    player.play_all()
