# Copyright 2018 Mark S. Weiss

from time import sleep

# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import sinepad as fd_sc_synth

from aleatoric.note.adapters.foxdot_supercollider_note import (FIELDS,
                                                               FoxDotSupercolliderNote)
from aleatoric.note.adapters.note import NoteConfig
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.generators.chord import Chord, HarmonicChord
from aleatoric.note.generators.scale import HarmonicScale, Scale
from aleatoric.note.generators.scale_globals import HarmonicScale, MajorKey
from aleatoric.player.foxdot_supercollider_player import \
    FoxDotSupercolliderPlayer

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
NOTE_CLS = FoxDotSupercolliderNote


if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    note_config = NoteConfig(FIELDS)
    note_config.name = 'test_note'
    note_config.synth_def = fd_sc_synth
    note_config.amp = 1.0
    note_config.oct = 2
    note_config.scale = 'lydian'
    note = FoxDotSupercolliderNote(**note_config.as_dict(), performance_attrs=performance_attrs)

    scale = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, note_cls=NOTE_CLS, note_prototype=note)
    notes_in_scale = scale.note_list

    notes = []
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
