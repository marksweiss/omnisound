# Copyright 2019 Mark S. Weiss

from aleatoric.note.adapters.midi_note import (FIELDS, MidiInstrument, MidiNote)
from aleatoric.note.adapters.note import NoteConfig
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import (Measure, Meter)
from aleatoric.note.containers.song import Song
from aleatoric.note.containers.track import MidiTrack
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.generators.scale import Scale
from aleatoric.note.generators.scale_globals import HarmonicScale, MajorKey
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.midi_player import MidiPlayer


SONG_NAME = 'test_midi_song'
TRACK_NAME = 'vibes_mesh'

INSTRUMENT: int = MidiInstrument.Vibraphone.value
CHANNEL = 1

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
BPM = 120
TEMPO_QPM = BPM * 4
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM, quantizing=True)

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
NOTE_CLS = MidiNote
NOTE_PROTOTYPE = MidiNote(time=0.0, duration=NoteDur.QUARTER.value, velocity=100,
                          pitch=MidiNote.get_pitch_for_key(MajorKey.C, OCTAVE))

SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, note_cls=NOTE_CLS,
              note_prototype=NOTE_PROTOTYPE)

TRACK = MidiTrack(name=TRACK_NAME, instrument=INSTRUMENT, channel=CHANNEL)

NUM_NOTES = 128
DUR = NoteDur.QUARTER.value
if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    notes = NoteSequence([])
    for i in range(1, NUM_NOTES + 1):
        note_config = NoteConfig(FIELDS)
        note_config.time = (i - 1 % 4) * DUR
        note_config.duration = DUR
        note_config.velocity = 100 - ((i % 4) * 5)
        note_config.pitch = SCALE[(i - 1) % 6].pitch
        note = MidiNote(**note_config.as_dict())
        notes.append(note)
        if i % NUM_NOTES == 0:
            measure = Measure(notes, meter=METER)
            TRACK.append(measure)
            notes = NoteSequence([])

    song = Song(to_add=TRACK, name=SONG_NAME)

    player = MidiPlayer(song=song, midi_file_path='test_song.mid')
    player.play_all()
    player.write_midi_file()