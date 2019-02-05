# Copyright 2019 Mark S. Weiss

from aleatoric.note.adapters.midi_note import FIELDS, MidiInstrument, MidiNote
from aleatoric.note.adapters.note import NoteConfig
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.containers.measure import Measure, Meter
from aleatoric.note.containers.song import Song
from aleatoric.note.containers.track import MidiTrack
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.generators.chord import Chord
from aleatoric.note.generators.chord_globals import HarmonicChord
from aleatoric.note.generators.scale import Scale
from aleatoric.note.generators.scale_globals import HarmonicScale, MajorKey
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.midi_player import MidiPlayer, MidiPlayerAppendMode


SONG_NAME = 'test_midi_song'
INSTRUMENT: int = MidiInstrument.Vibraphone.value
APPEND_MODE = MidiPlayerAppendMode.AppendAtAbsoluteTime

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
BPM = 120
TEMPO_QPM = BPM * 4
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM, quantizing=True)

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
HARMONIC_CHORD = HarmonicChord.MajorTriad
NOTE_CLS = MidiNote
NOTE_PROTOTYPE = MidiNote(time=0.0, duration=NoteDur.QUARTER.value, velocity=100,
                          pitch=MidiNote.get_pitch_for_key(MajorKey.C, OCTAVE))

SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, note_cls=NOTE_CLS,
              note_prototype=NOTE_PROTOTYPE)
NUM_NOTES_IN_SCALE = 7

NUM_MEASURES = 16
NUM_NOTES_PER_MEASURE = 16
DUR = NoteDur.SIXTEENTH.value


if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    ostinato_track = MidiTrack(name='ostinato', instrument=INSTRUMENT, channel=1)
    chords_track = MidiTrack(name='chords', instrument=MidiInstrument.Acoustic_Grand_Piano.value, channel=2)
    tracks = [ostinato_track, chords_track]
    ostinato_notes = NoteSequence([])
    chords_notes = NoteSequence([])
    for _ in range(NUM_MEASURES):
        for i in range(NUM_NOTES_PER_MEASURE):
            note_config = NoteConfig(FIELDS)
            note_config.time = (i % NUM_NOTES_PER_MEASURE) * DUR
            note_config.duration = DUR
            note_config.velocity = 100 - ((i % 16) * 5)
            note_config.pitch = SCALE[i % NUM_NOTES_IN_SCALE].pitch
            note = MidiNote(**note_config.as_dict())
            ostinato_notes.append(note)

            if i % 2 == 0:
                note_prototype = note.copy(note)
                note_prototype.dur = NoteDur.QUARTER.value
                chord = Chord(harmonic_chord=HARMONIC_CHORD, note_prototype=note, note_cls=MidiNote,
                              octave=OCTAVE - 1, key=KEY)
                chords_notes.extend(chord.note_list)

        ostinato_measure = Measure(ostinato_notes, meter=METER)
        # ostinato_track.append(ostinato_measure)
        chords_measure = Measure(chords_notes, meter=METER)
        ostinato_track.append(chords_measure)
        ostinato_notes = NoteSequence([])
        # chords_track.append(chords_measure)
        chords_notes = NoteSequence([])

    song = Song(to_add=tracks, name=SONG_NAME)

    player = MidiPlayer(song=song, append_mode=APPEND_MODE,
                        midi_file_path='/Users/markweiss/Documents/projects/aleatoric/test_song.mid')
    player.play_all()
    player.write_midi_file()