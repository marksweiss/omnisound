# Copyright 2019 Mark S. Weiss

from aleatoric.note.adapters.midi_note import (FIELDS, MidiInstrument, MidiNote)
from aleatoric.note.adapters.note import NoteConfig
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import (Measure, Meter)
from aleatoric.note.containers.song import Song
from aleatoric.note.containers.track import MidiTrack
from aleatoric.note.containers.note_sequence import NoteSequence
# from aleatoric.note.generators.scale_globals import MajorKey
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.midi_player import MidiPlayer


SONG_NAME = 'test_midi_song'
TRACK_NAME = 'vibes_mesh'

INSTRUMENT: int = MidiInstrument.Vibraphone.value
CHANNEL = 1

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
TEMPO_QPM = 240
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM, quantizing=True)


# FIELDS = ('instrument', 'time', 'duration', 'velocity', 'pitch', 'name', 'channel')
if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()
    track = MidiTrack(name=TRACK_NAME, instrument=INSTRUMENT, channel=CHANNEL)

    notes = NoteSequence([])
    for i in range(100):
        note_config = NoteConfig(FIELDS)
        note_config.duration = NoteDur.QUARTER
        note_config.velocity = 100 - ((i % 4) * 5)
        note_config.channel = CHANNEL
        note = MidiNote(**note_config.as_dict())
        notes.append(note)
        if i % 4 == 0:
            measure = Measure(notes, meter=METER)
            measure.quantize_to_beat()
            track.append(measure)
            notes = NoteSequence([])

    song = Song(to_add=track, name=SONG_NAME)

    player = MidiPlayer(song=song, midi_file_path='test_song.mid')
    player.play_all()
    player.write_midi_file()
