# Copyright 2021 Mark S. Weiss

from omnisound.src.composition.in_c.in_c_ensemble import InCEnsemble
from omnisound.src.composition.in_c.in_c_player import InCPlayer
from omnisound.src.container.song import Song
from omnisound.src.container.track import MidiTrack
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.player.midi.midi_writer import MidiWriter
from omnisound.src.modifier.swing import Swing
from omnisound.src.note.adapter.midi_note import MidiInstrument


BEATS_PER_MEASURE = 4
BEAT_NOTE_DUR = NoteDur.QRTR
TEMPO_QPM = 240
METER = Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM, quantizing=False)
SWING_RANGE = 0.001
# TODO MODIFY PER TRACK?
SWING = Swing(swing_range=SWING_RANGE, swing_direction=Swing.SwingDirection.Both,
              swing_jitter_type=Swing.SwingJitterType.Random)
# TODO INSTRUMENT PER TRACK
INSTRUMENT = MidiInstrument.Vibraphone
MIDI_FILE_PATH = "Users/markweiss/in_c"


class InCPerformance:
    def __init__(self, ensemble: InCEnsemble):
        self.ensemble = ensemble

    def perform(self):
        while not self.ensemble.reached_conclusion():
            ensemble.perform()


if __name__ == 'main':
    players = []
    for i in range(1, MidiTrack.MAX_NUM_MIDI_TRACKS + 1):
        track = MidiTrack(to_add=None, swing=SWING, name=str(f'Channel {i} {INSTRUMENT}'), instrument=INSTRUMENT,
                          channel=i)
        players.append(InCPlayer(track))
    ensemble = InCEnsemble(to_add=players)

    performance = InCPerformance(ensemble)
    performance.perform()

    song = Song(to_add=[MidiTrack.copy(player.track) for player in ensemble])
    writer = MidiWriter(song=song, midi_file_path=MIDI_FILE_PATH)
    writer.generate_and_write()
