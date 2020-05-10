# Copyright 2020 Mark S. Weiss

from omnisound.note.adapters.midi_note import MidiInstrument
from omnisound.note.containers.measure import Meter
from omnisound.note.generators.midi_sequencer import MidiSequencer
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
                          meter=METER, swing=SWING, midi_file_path=MIDI_FILE_PATH)
# Algo Comp Settings
BASE_VELOCITY = 100
VELOCITY_FACTOR = 2


if __name__ == '__main__':

    def get_velocity(j, notes_per_measure):
        return int(BASE_VELOCITY - ((j % notes_per_measure) / VELOCITY_FACTOR))

    track_name = 'ostinato'
    instrument = MidiInstrument.Vibraphone.value
    notes_per_measure = int(1 / NoteDur.THIRTYSECOND.value)
    pattern_phrases = []
    for j in range(notes_per_measure, step=4):
        pattern_phrase = (f'C:4::{get_velocity (j, notes_per_measure)} '
                          f'E:4::{get_velocity (j + 1, notes_per_measure)} '
                          f'G:4::{get_velocity (j + 2, notes_per_measure)} '
                          f'E:4::{get_velocity (j + 3, notes_per_measure)}')
        pattern_phrases.append(pattern_phrase)
    pattern = ' '.join(pattern_phrases)
    SEQUENCER.add_pattern_as_new_track(track_name=track_name, pattern=pattern, instrument=instrument)
    SEQUENCER.track(track_name).apply_swing()

    track_name = 'chord'
    instrument = MidiInstrument.Acoustic_Grand_Piano.value
    notes_per_measure = int(1 / NoteDur.WHOLE.value)
    pattern_measures = []
    for i in range(NUM_MEASURES):
        for j in range(notes_per_measure):
            pattern_phrase = f'C:2:MajorTriad:{BASE_VELOCITY - 10}'
            pattern_phrases.append(pattern_phrase)
        pattern_measures.append(' '.join(pattern_phrases))
    pattern = '|'.join(pattern_measures)
    SEQUENCER.add_pattern_as_new_track(track_name=track_name, pattern=pattern, instrument=instrument)

    SEQUENCER.play()