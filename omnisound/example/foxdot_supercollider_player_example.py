# Copyright 2018 Mark S. Weiss

from time import sleep

# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import sinepad as fd_sc_synth

from omnisound.note.adapter.foxdot_supercollider_note import (ATTR_NAMES,
                                                              FoxDotSupercolliderNote)
from omnisound.note.adapter.note import NoteValues
from omnisound.note.adapter.performance_attrs import PerformanceAttrs
from omnisound.note.container.note_sequence import NoteSequence
from omnisound.player.supercollider.foxdot_supercollider_player import \
    FoxDotSupercolliderPlayer

if __name__ == '__main__':
    # This is a test
    performance_attrs = PerformanceAttrs()

    notes = []
    note_config = NoteValues(ATTR_NAMES)
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
    player.play()
