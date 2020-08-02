# Copyright 2020 Mark S. Weiss

from pathlib import Path

from omnisound.src.note.adapter.midi_note import MidiInstrument
from omnisound.src.container.track import MidiTrack
from omnisound.src.generator.chord_globals import HarmonicChord
from omnisound.src.generator.sequencer.midi_sequencer import (MidiSingleTrackSequencer, MidiMultitrackSequencer,
                                                              MidiWriterSequencer)
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.modifier.swing import Swing

# Meter
BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QUARTER
# noinspection PyTypeChecker
BEAT_DUR_VAL: float = BEAT_DUR.value
BPM = 240
METER = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=BPM, quantizing=True)
# Swing
SWING_FACTOR = 0.005
SWING = Swing(swing_on=True, swing_range=SWING_FACTOR, swing_direction=Swing.SwingDirection.Both)
# Sequencer
SEQUENCER_NAME = 'example_midi_sequencer_song'
NUM_MEASURES = 4
MIDI_FILE_PATH = Path('/Users/markweiss/Documents/projects/omnisound/omnisound/example/example_sequencer_song.mid')

BASE_VELOCITY = 100
VELOCITY_FACTOR = 2


if __name__ == '__main__':

    def get_velocity(j, notes_per_measure):
        return int(BASE_VELOCITY - ((j % notes_per_measure) / VELOCITY_FACTOR))

    track_name = 'ostinato'
    notes_per_measure = int(1 / NoteDur.THIRTYSECOND.value)
    pattern_phrases = []
    for j in range(0, notes_per_measure, 4):
        pattern_phrase = (f'C:4::{get_velocity (j, notes_per_measure)}:0.03125 '
                          f'E:4::{get_velocity (j + 1, notes_per_measure)}:0.03125 '
                          f'G:4::{get_velocity (j + 2, notes_per_measure)}:0.03125 '
                          f'E:4::{get_velocity (j + 3, notes_per_measure)}:0.03125')
        pattern_phrases.append(pattern_phrase)
    pattern = ' '.join(pattern_phrases)
    writer_sequencer = MidiWriterSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                                           meter=METER, swing=SWING,
                                           midi_file_path=MIDI_FILE_PATH)
    writer_sequencer.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Vibraphone.value,
                                              track_type=MidiTrack).channel = 1
    track_name = 'chord'
    pattern = f'C:2:MajorTriad:{BASE_VELOCITY - 10}:1.0'
    writer_sequencer.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Acoustic_Grand_Piano.value,
                                              track_type=MidiTrack).channel = 2
    track_name = 'arpeggiator'
    pattern = f'F:6::{BASE_VELOCITY}:0.25 B:6::{BASE_VELOCITY}:0.25 E:6::{BASE_VELOCITY}:0.25 A:6::{BASE_VELOCITY}:0.25'
    writer_sequencer.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Violin.value,
                                              track_type=MidiTrack,
                                              arpeggiate=True, arpeggiator_chord=HarmonicChord.MajorSeventh).channel = 3
    writer_sequencer.apply_swing()
    writer_sequencer.player.generate_and_write()

    # Now send song to interactive midi player which sends all note events on MIDI channel 1 to any listening devices
    single_track_rt_sequencer = MidiSingleTrackSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                                                         meter=METER, swing=SWING)
    single_track_rt_sequencer.extend(to_add=writer_sequencer.track_list)
    single_track_rt_sequencer.loop()
    single_track_rt_sequencer.play()

    # Now send song to interactive midi player which sends note events for each track to a separate MIDI channel
    multi_track_rt_sequencer = MidiMultitrackSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                                                       meter=METER, swing=SWING)
    multi_track_rt_sequencer.extend(to_add=writer_sequencer.track_list)
    multi_track_rt_sequencer.loop()
    multi_track_rt_sequencer.play()
