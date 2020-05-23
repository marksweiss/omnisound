# Copyright 2020 Mark S. Weiss

from omnisound.note.adapters.midi_note import MidiInstrument
from omnisound.note.containers.measure import Meter
from omnisound.note.containers.track import MidiTrack
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.midi_sequencer import MidiSingleTrackSequencer, MidiWriterSequencer
from omnisound.note.modifiers.meter import NoteDur
from omnisound.note.modifiers.swing import Swing
from omnisound.player.midi_player import MidiPlayerAppendMode


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
SEQUENCER_NAME = 'test_midi_sequencer_song'
NUM_MEASURES = 4
MIDI_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/test_sequencer_song.mid'
WRITER_SEQUENCER = MidiWriterSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                                       meter=METER, swing=SWING,
                                       midi_file_path=MIDI_FILE_PATH)
INTERACTIVE_SEQUENCER = MidiSingleTrackSequencer(name=SEQUENCER_NAME, num_measures=NUM_MEASURES,
                                                 meter=METER, swing=SWING)

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
    WRITER_SEQUENCER.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Vibraphone.value,
                                              track_type=MidiTrack).channel = 1

    track_name = 'chord'
    pattern = f'C:2:MajorTriad:{BASE_VELOCITY - 10}:1.0'
    WRITER_SEQUENCER.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Acoustic_Grand_Piano.value,
                                              track_type=MidiTrack).channel = 2

    track_name = 'arpeggiator'
    pattern = f'F:6::{BASE_VELOCITY}:0.25 B:6::{BASE_VELOCITY}:0.25 E:6::{BASE_VELOCITY}:0.25 A:6::{BASE_VELOCITY}:0.25'
    WRITER_SEQUENCER.add_pattern_as_new_track(track_name=track_name, pattern=pattern,
                                              instrument=MidiInstrument.Violin.value,
                                              track_type=MidiTrack,
                                              arpeggiate=True, arpeggiator_chord=HarmonicChord.MajorSeventh).channel = 3

    # Now render all tracks into one multi-track MIDI file
    WRITER_SEQUENCER.apply_swing()
    WRITER_SEQUENCER.play()
    # noinspection PyUnresolvedReferences
    WRITER_SEQUENCER.player.write_midi_file()

    # Now send song to interactive midi player which sends all note events on MIDI channel 1 to any listening devices
    for track in WRITER_SEQUENCER:
        INTERACTIVE_SEQUENCER.append(track)
    INTERACTIVE_SEQUENCER.play()
