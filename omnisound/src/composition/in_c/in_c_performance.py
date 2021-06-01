# Copyright 2021 Mark S. Weiss

from omnisound.src.composition.in_c.in_c_ensemble import InCEnsemble
from omnisound.src.composition.in_c.in_c_player import InCPlayer
from omnisound.src.container.note_sequence import NoteSequence
from omnisound.src.container.song import Song
from omnisound.src.container.track import MidiTrack
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.player.midi.midi_writer import MidiWriter
from omnisound.src.modifier.swing import Swing
from omnisound.src.note.adapter.midi_note import MidiInstrument
import omnisound.src.note.adapter.midi_note as midi_note


BEATS_PER_MEASURE = 4
BEAT_NOTE_DUR = NoteDur.QRTR
TEMPO_QPM = 240
METER = Meter(beat_note_dur=BEAT_NOTE_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM, quantizing=False)
SWING_RANGE = 0.001
# TODO MODIFY PER TRACK?
SWING = Swing(swing_range=SWING_RANGE, swing_direction=Swing.SwingDirection.Both,
              swing_jitter_type=Swing.SwingJitterType.Random)

NUM_ATTRIBUTES = len(midi_note.ATTR_NAMES)

# TODO INSTRUMENT PER TRACK
INSTRUMENT = MidiInstrument.Vibraphone
MIDI_FILE_PATH = "Users/markweiss/in_c"

PLAYER = 'player'
ENSEMBLE = 'ensemble'

# No-op Instructions
####################
# Included here only for completeness relative to the original score. These instructions aren't relevant for a
# software performance of the score.

# "All performers play from the same page of 53 melodic patterns played in sequence."
def instruction_1():
    pass

# "Any number of any kind of instruments can play.  A group of about 35 is desired if possible but smaller or
# larger groups will work.  If vocalist(s) join in they can use any vowel and consonant sounds they like."
def instruction_2():
    pass

# "If for some reason a pattern can’t be played, the performer should omit it and go on."
def instruction_12():
    pass

# "Instruments can be amplified if desired.  Electronic keyboards are welcome also."
def instruction_13():
    pass

# Performance Instructions
##########################

# "Patterns are to be played consecutively with each performer having the freedom to determine how many
#  times he or she will repeat each pattern before moving on to the next.  There is no fixed rule
#  as to the number of repetitions a pattern may have, however, since performances normally average
#  between 45 minutes and an hour and a half, it can be assumed that one would repeat each pattern
#  from somewhere between 45 seconds and a minute and a half or longer."
def instruction_3_player_preplay(player: InCPlayer) -> None:
    player.check_advance_to_next_phrase()


# "It is very important that performers listen very carefully to one another and this means occasionally to drop
# out and listen. ... As an ensemble, it is very desirable to play very softly as well as very loudly and to try to
# diminuendo and crescendo together."
# This handler controls whether all Players in Ensemble will enter crescendo or descrescendo state.  If they do then
# all amp-related hanlders will be skipped for as long as the de/crescendo lasts. Instead all Players will move
# amp up/down one step each iteration, for the number of steps of the de/crescendo. The amount amp changes overall
# is controlled in EnsembleSetting#max_amp_range_for_seeking_crescendo
def instruction_4_ensemble_preplay(ensemble: InCEnsemble) -> None:
    if ensemble.seeking_crescendo():
        ensemble.set_crescendo_state()
    elif ensemble.seeking_decrescendo():
        ensemble.set_decrescendo_state()


# This implements de/crescendo amp adjustment on each player after the ensemble handler sets whether
#  or not the orchestra is in de/crescendo
def instruction_4_player_preplay(player: InCPlayer) -> None:
    # Ensemble manages current state of whether all Players are in de/crescendo, and if so by how
    #  much each Player adjusts their volume. All each Player does is call this, if there is
    #  no current de/crescendo then crescendo_amp_adj() returns 0
    amp_adj = player.ensemble.crescendo_amp_adj()
    for note in player.current_phrase():
        note.volume = max(note.volume + amp_adj, 0)


# This adjusts the state of the ensemble tracking what step in a de/crescendo it's in
def instruction_4_ensemble_postplay(ensemble: InCEnsemble) -> None:
    ensemble.crescendo_increment()

# "Each pattern can be played in unison or canonically in any alignment with itself or with its neighboring patterns"
def instruction_5_player_preplay(player: InCPlayer):
    # Construct the rest Note, which may have 0 duration. If it does not, prepend it to the next output to change
    # it's alignment
    rest_note_dur = player.get_phase_adjustment()
    if rest_note_dur > 0.0:
        player.reset_output()
        rest_note = NoteSequence.new_note(midi_note.DEFAULT_NOTE_CONFIG)
        rest_note.duration = rest_note_dur
        rest_note.volume = 0
        player.append_note_to_output(rest_note)


class InCPerformance:
    ENSEMBLE_PREPLAY_INSTRUCTIONS = {
        instruction_4_ensemble_preplay.__name__: instruction_4_ensemble_preplay,
    }

    ENSEMBLE_POSTPLAY_INSTRUCTIONS = {
        instruction_4_ensemble_postplay.__name__: instruction_4_ensemble_postplay,
    }

    PLAYER_PREPLAY_INSTRUCTIONS = {
        instruction_3_player_preplay.__name__: instruction_3_player_preplay,
        instruction_4_player_preplay.__name__: instruction_4_player_preplay,
    }

    PLAYER_POSTPLAY_INSTRUCTIONS = {

    }

    def __init__(self, ensemble: InCEnsemble):
        self.ensemble = ensemble

    def perform(self) -> None:
        InCPerformance._register_hooks()
        while not self.ensemble.reached_conclusion():
            pass

    @staticmethod
    def _register_hooks() -> None:
        for name, instruction in InCPerformance.PLAYER_PREPLAY_INSTRUCTIONS.items():
            for player in ensemble.players:
                player.add_pre_play_hook(name, instruction)
        for name, instruction in InCPerformance.PLAYER_POSTPLAY_INSTRUCTIONS.items():
            for player in ensemble.players:
                player.add_post_play_hook(name, instruction)

        for name, instruction in InCPerformance.ENSEMBLE_PREPLAY_INSTRUCTIONS.items():
            ensemble.add_pre_play_hook(name, instruction)
        for name, instruction in InCPerformance.ENSEMBLE_POSTPLAY_INSTRUCTIONS.items():
            ensemble.add_post_play_hook(name, instruction)


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
