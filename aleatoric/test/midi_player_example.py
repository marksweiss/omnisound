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
from aleatoric.player.midi_player import MidiPlayer


SONG_NAME = 'test_midi_song'

INSTRUMENT: int = MidiInstrument.Acoustic_Grand_Piano.value

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


NUM_NOTES = 16
DUR = NoteDur.SIXTEENTH.value
if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    ostinato_track = MidiTrack(name='ostinato', instrument=INSTRUMENT, channel=1)
    chords_track = MidiTrack(name='chords', instrument=INSTRUMENT, channel=2)
    tracks = [ostinato_track, chords_track]
    ostinato_notes = NoteSequence([])
    chords_notes = NoteSequence([])
    for i in range(1, NUM_NOTES + 1):
        note_config = NoteConfig(FIELDS)
        note_config.time = (i - 1 % 4) * DUR
        note_config.duration = DUR
        note_config.velocity = 100 - ((i % 4) * 10)
        note_config.pitch = SCALE[(i - 1) % 6].pitch
        note = MidiNote(**note_config.as_dict())
        ostinato_notes.append(note)

        chord = Chord(harmonic_chord=HARMONIC_CHORD, note_prototype=note, note_cls=MidiNote,
                      octave=OCTAVE, key=KEY)
        # TODO GET MULTITRACK MIDI TO WORK, AND ADD THESE TO chords_notes
        # TODO FIX MIDIPLAYER TO ACTUALLY ALLOW ADDING MULTIPLE NOTES AT SAME START TIME
        # chords_notes.extend(chord.note_list)
        ostinato_notes.extend(chord.note_list)

        if i % NUM_NOTES == 0:
            ostinato_measure = Measure(ostinato_notes, meter=METER)
            ostinato_track.append(ostinato_measure)
            ostinato_notes = NoteSequence([])
            # chords_measure = Measure(chords_notes, meter=METER)
            # chords_track.append(chords_measure)
            # chords_notes = NoteSequence([])

    song = Song(to_add=tracks, name=SONG_NAME)

    player = MidiPlayer(song=song, midi_file_path='test_song.mid')
    player.play_all()
    player.write_midi_file()