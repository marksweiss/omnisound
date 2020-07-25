# Copyright 2019 Mark S. Weiss

from omnisound.note.adapters.midi_note import (ATTR_GET_TYPE_CAST_MAP, ATTR_NAME_IDX_MAP, ATTR_NAMES, CLASS_NAME,
                                               NUM_ATTRIBUTES, get_pitch_for_key, make_note, MidiInstrument)
from omnisound.note.adapters.note import MakeNoteConfig, NoteValues
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
from omnisound.player.midi_player import MidiPlayerAppendMode
from omnisound.player.midi_writer import MidiWriter


SONG_NAME = 'test_midi_song'
APPEND_MODE = MidiPlayerAppendMode.AppendAtAbsoluteTime

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
# noinspection PyTypeChecker
BEAT_DUR_VAL: float = BEAT_DUR.value
BPM = 240
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=BPM, quantizing=True)

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
HARMONIC_CHORD = HarmonicChord.MajorTriad
NUM_NOTES_IN_CHORD = 3

NOTE_CONFIG = MakeNoteConfig(cls_name=CLASS_NAME,
                             num_attributes=NUM_ATTRIBUTES,
                             make_note=make_note,
                             get_pitch_for_key=get_pitch_for_key,
                             attr_name_idx_map=ATTR_NAME_IDX_MAP,
                             attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)
SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE,
              mn=NOTE_CONFIG)
NUM_NOTES_IN_SCALE = 7

NUM_MEASURES = 4
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
    swing_factor = 0.008
    swing = Swing(swing_on=True, swing_range=swing_factor, swing_direction=Swing.SwingDirection.Both)

    dur = NoteDur.THIRTYSECOND
    # noinspection PyTypeChecker
    dur_val: float = dur.value
    notes_per_measure = int((1 / dur_val) * (BEATS_PER_MEASURE * BEAT_DUR_VAL))
    for _ in range(NUM_MEASURES):
        note_config = MakeNoteConfig.copy(NOTE_CONFIG)
        ostinato_measure = Measure(meter=METER, swing=swing, mn=note_config)

        for i in range(notes_per_measure):
            note_values = NoteValues(ATTR_NAMES)
            note_values.time = i * dur_val
            note_values.duration = dur_val
            note_values.velocity = int(BASE_VELOCITY - ((i % notes_per_measure) / VELOCITY_FACTOR))
            note_values.pitch = SCALE[i % NUM_NOTES_IN_SCALE].pitch
            note_config.attr_vals_defaults_map = note_values.as_dict()
            note = NoteSequence.new_note(note_config)
            ostinato_measure.append(note)
        ostinato_measure.apply_swing()
        ostinato_track.append(ostinato_measure)

    # Chords
    octave = OCTAVE - 2
    dur = NoteDur.WHOLE

    # noinspection PyTypeChecker
    dur_val: float = dur.value
    notes_per_measure = int((1 / dur_val) * (BEATS_PER_MEASURE * BEAT_DUR_VAL))
    for _ in range(NUM_MEASURES):
        note_config = MakeNoteConfig.copy(NOTE_CONFIG)
        chords_measure = Measure(meter=METER, swing=swing, num_notes=0,
                                 mn=note_config)

        for i in range(notes_per_measure):
            note_values = NoteValues(ATTR_NAMES)
            note_values.time = 0.0
            note_values.duration = dur_val
            note_values.velocity = BASE_VELOCITY - 10
            chord_root = SCALE[i % NUM_NOTES_IN_SCALE]
            note_values.pitch = chord_root.pitch

            note_config.attr_vals_defaults_map = note_values.as_dict()

            chord_note = NoteSequence.new_note(note_config)
            # Now get the chord for the current key
            chord_root_key = SCALE.keys[i % NUM_NOTES_IN_SCALE]
            chord = Chord(harmonic_chord=HARMONIC_CHORD, octave=octave, key=chord_root_key,
                          mn=note_config)
            chords_measure.extend(chord)
        chords_track.append(chords_measure)

    # Render the tracks in the song
    tracks = [ostinato_track, chords_track]
    song = Song(to_add=tracks, name=SONG_NAME)
    writer = MidiWriter(song=song, append_mode=APPEND_MODE,
                        midi_file_path='/Users/markweiss/Documents/projects/omnisound/omnisound/test/test_song.mid')
    writer.generate_and_write()
