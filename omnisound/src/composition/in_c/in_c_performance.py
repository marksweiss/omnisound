# Copyright 2021 Mark S. Weiss

from pathlib import Path

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
from omnisound.src.player.midi.midi_player import MidiPlayerAppendMode

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
MIDI_FILE_PATH = Path('/Users/markweiss/Documents/projects/omnisound/omnisound/src/composition/in_c/rendered/in_c.mid')

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

# Ensemble Pre-play

# "It is very important that performers listen very carefully to one another and this means occasionally to drop
# out and listen. ... As an ensemble, it is very desirable to play very softly as well as very loudly and to try to
# diminuendo and crescendo together."
# This handler controls whether all Players in Ensemble will enter crescendo or descrescendo state.  If they do then
# all amp-related hanlders will be skipped for as long as the de/crescendo lasts. Instead all Players will move
# amp up/down one step each iteration, for the number of steps of the de/crescendo. The amount amp changes overall
# is controlled in EnsembleSetting#max_amp_range_for_seeking_crescendo
def instruction_4_ensemble_preplay(ensemble: InCEnsemble) -> None:
    if ensemble.is_seeking_crescendo():
        ensemble.set_crescendo_state()
    elif ensemble.is_seeking_decrescendo():
        ensemble.set_decrescendo_state()

# Player Set Next Phrase

# "Patterns are to be played consecutively with each performer having the freedom to determine how many
#  times he or she will repeat each pattern before moving on to the next.  There is no fixed rule
#  as to the number of repetitions a pattern may have, however, since performances normally average
#  between 45 minutes and an hour and a half, it can be assumed that one wuld repeat each pattern
#  from somewhere between 45 seconds and a minute and a half or longer."
def instruction_3_player_set_next_phrase(player: InCPlayer) -> None:
    if not player.has_advanced:
        player.play_next_phrase()


#  "... As the performance progresses, performers should stay within 2 or 3 patterns of each other. ..."
def instruction_6_player_set_next_phrase(player: InCPlayer) -> None:
    if not player.has_advanced:
        player.should_play_next_phrase_too_far_behind()


# "The group should aim to merge into a unison at least once or twice during the performance.
# At the same time, if the players seem to be consistently too much in the same alignment of a pattern,
# they should try shifting their alignment by an eighth note or quarter note with what’s going on in the rest of the ensemble."
def instruction_10_player_set_next_phrase(player: InCPlayer) -> None:
    if not player.has_advanced:
        player.play_next_phrase_seeking_unison()

# Player Set Output

# This implements de/crescendo amp adjustment on each player after the ensemble handler sets whether
#  or not the orchestra is in de/crescendo
def instruction_4_player_set_output(player: InCPlayer) -> None:
    # Ensemble manages current state of whether all Players are in de/crescendo, and if so by how
    #  much each Player adjusts their volume. All each Player does is call this, if there is
    #  no current de/crescendo then crescendo_amp_adj() returns 0
    amp_adj = player.ensemble.crescendo_amp_adj()
    for measure in player.output:
        for note in measure:
            note.volume = max(note.volume + amp_adj, 0)


# "Each pattern can be played in unison or canonically in any alignment with itself or with its neighboring patterns"
def instruction_5_player_set_output(player: InCPlayer) -> None:
    # Construct the rest Note, which may have 0 duration. If it does not, prepend it to the next output to change
    # it's alignment
    rest_note_dur = player.get_phase_adjustment()
    if rest_note_dur > 0.0:
        rest_note = NoteSequence.new_note(midi_note.DEFAULT_NOTE_CONFIG)
        rest_note.duration = rest_note_dur
        rest_note.volume = 0
        player.append_note_to_output(rest_note)


# "It is OK to transpose patterns by an octave, especially to transpose up.  Transposing down by octaves
# works best on the patterns containing notes of long durations."
# TODO HOW TO IMPLEMENT THIS PART OF THIS INSTRUCTION "Augmentation of rhythmic values can also be effective."
def instruction_11_player_set_output(player: InCPlayer) -> None:
    shift = player.transpose_shift()
    for measure in player.output:
        # noinspection PyUnresolvedReferences
        measure.transpose(interval=shift)


# "The ensemble can be aided by the means of an eighth note pulse played on the high c’s of the piano or on a
# mallet instrument. It is also possible to use improvised percussion in strict rhythm (drum set, cymbals, bells, etc.),
# if it is carefully done and doesn’t overpower the ensemble."
# NOTE: This must be run as the last preplay step as it relies on all players having selected their current phrase
def instruction_7_special_preplay(ensemble: InCEnsemble):
    ensemble.output_pulse_phrase()

# Ensemble Post-play

# This adjusts the state of the ensemble tracking what step in a de/crescendo it's in
def instruction_4_ensemble_postplay(ensemble: InCEnsemble) -> None:
    ensemble.increment_crescendo()


# TODO MOVE TO player.reset_state_and_output()
# Extra helper handler to set player post-play state -- whether they have advanced
#  a phrase or not.  If not, increment player counter on current phrase
# Depends on separate checks in instruction handlers for instructions 3, 6 and 10
def instruction_3_6_10_player_postplay(player: InCPlayer) -> None:
    if not player.has_advanced:
        # TODO WHERE IS THIS USED?
        player.cur_phrase_count += 1
    else:
        player.cur_phrase_count = 0


class InCPerformance:
    ENSEMBLE_PREPLAY_INSTRUCTIONS = [
        instruction_4_ensemble_preplay,
    ]

    PLAYER_SET_NEXT_PHRASE_INSTRUCTIONS = [
        instruction_3_player_set_next_phrase,
        instruction_6_player_set_next_phrase,
        instruction_10_player_set_next_phrase,
    ]

    PLAYER_SET_OUTPUT_INSTRUCTIONS = [
        instruction_4_player_set_output,
        instruction_5_player_set_output,
        instruction_11_player_set_output,
        instruction_7_special_preplay,
    ]

    SPECIAL_PREPLAY_INSTRUCTIONS = {
        instruction_7_special_preplay,
    }

    ENSEMBLE_POSTPLAY_INSTRUCTIONS = {
        instruction_4_ensemble_postplay,
    }

    PLAYER_POSTPLAY_INSTRUCTIONS = {
        instruction_3_6_10_player_postplay,
    }

    def __init__(self, ensemble: InCEnsemble):
        self.ensemble = ensemble

    def perform(self) -> None:
        while not self.ensemble.has_reached_conclusion():
            for instruction in InCPerformance.ENSEMBLE_PREPLAY_INSTRUCTIONS:
                instruction(self.ensemble)

            for instruction in InCPerformance.PLAYER_SET_NEXT_PHRASE_INSTRUCTIONS:
                # TODO THIS SHOULD BE OPERATING ON self.output. IS IT?
                map(instruction, self.ensemble.players)

            # TODO DO WE NEED play_phrase()?
            for player in self.ensemble.players:
                player.copy_cur_phrase_to_output()
            self.ensemble.pulse_player.copy_cur_phrase_to_output()

            for instruction in InCPerformance.PLAYER_SET_OUTPUT_INSTRUCTIONS:
                map(instruction, self.ensemble.players)

            # TODO
            for player in self.ensemble.players:
                player.flush_output_and_reset_state()
            # We only need to call this for the flush, but the other side effects are no-op in this case
            self.ensemble.pulse_player.flush_output_and_reset_state()

            for instruction in InCPerformance.SPECIAL_PREPLAY_INSTRUCTIONS:
                instruction(self.ensemble)
            for instruction in InCPerformance.ENSEMBLE_POSTPLAY_INSTRUCTIONS:
                instruction(self.ensemble)

        for player in self.ensemble.players:
            print(player.track.measure_list)
        # TODO self.reset_ensemble_and_players()


def make_track(i: int):
    return MidiTrack(to_add=None, swing=SWING, name=str(f'Channel {i} {INSTRUMENT.name}'),
                     instrument=INSTRUMENT.value, channel=i)


if __name__ == '__main__':
    measure_list = []
    while not measure_list:
        # TODO RESTORE
        players = [InCPlayer(make_track(i)) for i in range(1, 2)]  # MidiTrack.MAX_NUM_MIDI_TRACKS + 1)]
        # Construct player to fulfill instruction 7 to produce a pulse
        pulse_player = InCPlayer(make_track(MidiTrack.MAX_NUM_MIDI_TRACKS + 1))
        ensemble = InCEnsemble(to_add=players, pulse_player=pulse_player)
        for player in players:
            player.ensemble = ensemble
        pulse_player.ensemble = ensemble
        performance = InCPerformance(ensemble)
        performance.perform()
        song = Song(to_add=[MidiTrack.copy(player.track) for player in ensemble.players])

        measure_list = song.track_list[0].measure_list
        if measure_list:
            # TEMP DEBUG
            print(measure_list)

            writer = MidiWriter(song=song, midi_file_path=MIDI_FILE_PATH,
                                append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote)
            writer.generate_and_write()
