# Copyright 2019 Mark S. Weiss

from omnisound.note.adapters.midi_note import FIELDS, MidiInstrument, MidiNote
from omnisound.note.adapters.note import NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure, Meter
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import MidiTrack
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import HarmonicScale, MajorKey
from omnisound.note.modifiers.meter import NoteDur
from omnisound.note.modifiers.swing import Swing
from omnisound.player.midi_player import MidiPlayer, MidiPlayerAppendMode


SONG_NAME = 'test_midi_song'
APPEND_MODE = MidiPlayerAppendMode.AppendAtAbsoluteTime

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
BEAT_DUR_VAL: float = BEAT_DUR.value
BPM = 120
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=BPM, quantizing=True)

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
BASE_VELOCITY = 100
VELOCITY_FACTOR = 2


if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    # Declare track containers
    ostinato_track = MidiTrack(name='ostinato',
                               instrument=MidiInstrument.Vibraphone.value,
                               channel=1)
    chords_track = MidiTrack(name='chords',
                             instrument=MidiInstrument.Acoustic_Grand_Piano.value,
                             channel=2)

    # Ostinato
    dur = NoteDur.THIRTYSECOND
    dur_val: float = dur.value
    notes_per_measure = int((1 / BEAT_DUR_VAL) * ((1 / dur_val) / (1 / BEAT_DUR_VAL)))
    swing_factor = 0.01
    swing = Swing(swing_on=True, swing_factor=swing_factor, swing_direction=Swing.SwingDirection.Both)

    for _ in range(NUM_MEASURES):
        ostinato_notes = NoteSequence([])
        for i in range(notes_per_measure):
            note_config = NoteValues(FIELDS)
            note_config.time = (i % notes_per_measure) * dur_val
            note_config.duration = dur_val
            note_config.velocity = int(BASE_VELOCITY - ((i % notes_per_measure) / VELOCITY_FACTOR))
            note_config.pitch = SCALE[i % NUM_NOTES_IN_SCALE].pitch
            note = MidiNote(**note_config.as_dict())
            ostinato_notes.append(note)
        ostinato_measure = Measure(ostinato_notes, swing=swing, meter=METER)
        ostinato_measure.apply_swing()
        ostinato_track.append(ostinato_measure)

    # Chords
    dur = NoteDur.WHOLE
    dur_val: float = dur.value
    notes_per_measure = int((1 / BEAT_DUR_VAL) * (dur_val / BEAT_DUR_VAL))
    octave = OCTAVE - 2

    for _ in range(NUM_MEASURES):
        chords_notes = NoteSequence([])
        for i in range(notes_per_measure):
            note_config = NoteValues(FIELDS)
            note_config.time = 0.0
            note_config.duration = dur_val
            note_config.velocity = BASE_VELOCITY - 20
            chord_root = SCALE[i % NUM_NOTES_IN_SCALE]
            note_config.pitch = chord_root.pitch
            chord_note = MidiNote(**note_config.as_dict())
            # Now get the chord for the current key
            chord_root_key = SCALE.keys[i % NUM_NOTES_IN_SCALE]
            scale = Scale(key=chord_root_key, octave=octave, harmonic_scale=HARMONIC_SCALE,
                          note_cls=NOTE_CLS, note_prototype=chord_note)
            chord = Chord(harmonic_chord=HARMONIC_CHORD, note_prototype=chord_note, note_cls=MidiNote,
                          octave=octave, key=chord_root_key)
            # Append all the notes in the chord note list to the measure notes
            chords_notes.extend(chord.note_list)
        chords_measure = Measure(chords_notes, meter=METER)
        chords_track.append(chords_measure)

    # Render the tracks in the song
    tracks = [ostinato_track, chords_track]
    song = Song(to_add=tracks, name=SONG_NAME)
    player = MidiPlayer(song=song, append_mode=APPEND_MODE,
                        midi_file_path='/Users/markweiss/Documents/projects/omnisound/test_song.mid')
    player.play_all()
    player.write_midi_file()