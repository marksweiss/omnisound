# Copyright 2020 Mark S. Weiss

from omnisound.note.containers.measure import Meter
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.midi_sequencer import MidiSequencer
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import HarmonicScale, MajorKey
from omnisound.note.modifiers.meter import NoteDur
from omnisound.note.modifiers.swing import Swing


# Meter
BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
# noinspection PyTypeChecker
BEAT_DUR_VAL: float = BEAT_DUR.value
BPM = 240
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=BPM, quantizing=True)
# Swing
SWING_FACTOR = 0.002
SWING = Swing(swing_on=True, swing_range=SWING_FACTOR, swing_direction=Swing.SwingDirection.Both)
# Sequencer
SEQUENCER_NAME = 'test_midi_sequencer_song'
NUM_MEASURES = 4
MIDI_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/test_sequencer_song.mid'
SEQUENCER = MidiSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                          pattern_resolution=BEAT_DUR, meter=METER, swing=SWING,
                          midi_file_path=MIDI_FILE_PATH)
# Scale
KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
HARMONIC_CHORD = HarmonicChord.MajorTriad
NUM_NOTES_IN_CHORD = 3
SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE,
              mn=SEQUENCER.mn)
NUM_NOTES_IN_SCALE = 7
# Algo Comp Settings
BASE_VELOCITY = 100
VELOCITY_FACTOR = 2

