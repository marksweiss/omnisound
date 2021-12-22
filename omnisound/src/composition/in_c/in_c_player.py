# Copyright 2021 Mark S. Weiss

from statistics import mean
from typing import Any, Callable, Generator, List, Optional, Union

from omnisound.src.composition.in_c.player_settings import PlayerSettings as ps
from omnisound.src.composition.in_c.in_c_ensemble import InCEnsemble
from omnisound.src.container.measure import Measure
from omnisound.src.container.track import Track
from omnisound.src.generator.scale_globals import M
from omnisound.src.modifier.meter import NoteDur
from omnisound.src.note.adapter.midi_note import ATTR_NAMES, DEFAULT_MAKE_NOTE_CONFIG, MidiInstrument, pitch_for_key
from omnisound.src.note.adapter.note import BaseAttrNames, set_attr_vals_from_dict
from omnisound.src.container.note_sequence import NoteSequence
from omnisound.src.player.play_hook import PlayHook


def make_measure(instrument: MidiInstrument, octave: int,
                 note_attr_vals_lst: List[List[Union[float, int]]]) -> Measure:
    # ATTR_NAMES = ('instrument', 'time', 'duration', 'velocity', 'pitch')
    measure = Measure(num_notes=0, mn=DEFAULT_MAKE_NOTE_CONFIG)
    for note_attr_vals in note_attr_vals_lst:
        note = NoteSequence.new_note(DEFAULT_MAKE_NOTE_CONFIG)
        # Pass in instrument and don't require notes passed in to include start ('time' in MIDI)
        # because it is set automatically by #add_note_on_start(). Just cuts down on boilerplate defining notes.
        # set pitch_for_key() here for same reason.
        note_attr_vals = [instrument, 0.0] + note_attr_vals
        note_attr_vals[2] = note_attr_vals[2].value
        note_attr_vals[4] = pitch_for_key(note_attr_vals[4], octave)
        set_attr_vals_from_dict(note, dict(zip(ATTR_NAMES, note_attr_vals)))
        # Don't validate that we don't exceed measure duration for meter because this score is not written as a series
        # of correct measures in terms of total duration, but rather as a series of independent measures in the same
        # meter but with varying length -- this is the source of the phase evolutions that are the point of the piece.
        measure.add_note_on_start(note, validating=False)
    return measure


class InCPlayer(PlayHook):
    def __init__(self, track: Track, instrument: MidiInstrument = MidiInstrument.Acoustic_Grand_Piano):
        super().__init__()
        self.track = track
        self.instrument = instrument.value
        self.phrase_idx = 0
        self.cur_phrase_count = 0
        self.cur_start = 0.0
        self.adjusted_phase_count = 0.0
        self.is_at_rest = False
        self.has_advanced = False
        # Provide setter to avoid circular initialization issue, to create the Ensemble you need the players
        # but the players need a reference to their ensemble. So first create players and pass them to Ensemble init,
        # then iterate players and set ensemble reference
        self.ensemble = None
        self.source_phrases: List[Measure] = self._load_phrases()
        # TODO JUST MAKE THIS MEASURES
        self.output: List[Measure] = []
        self.output.append(self.source_phrases[0])

    def _load_phrases(self) -> List[Measure]:  # sourcery skip: merge-list-append
        sections = []

        eighth_rest = [NoteDur.EITH, 0, M.C]
        qrtr_rest = [NoteDur.QRTR, 0, M.C]
        measures = []
        # args: instrument, octave, [duration, velocity, pitch]
        # ATTR_NAMES = ('instrument', 'time', 'duration', 'velocity', 'pitch')
        measures.append(make_measure(self.instrument, 4, [
            [NoteDur.EITH, 70, M.C],
            [NoteDur.QRTR, 100, M.E],
            [NoteDur.EITH, 70, M.C],
            [NoteDur.QRTR, 100, M.E],
            [NoteDur.EITH, 70, M.C],
            [NoteDur.QRTR, 100, M.E],
        ]))
        measures.append(make_measure(self.instrument, 4, [
            [NoteDur.EITH, 70, M.C],
            [NoteDur.EITH, 100, M.E],
            [NoteDur.EITH, 100, M.F],
            [NoteDur.QRTR, 100, M.E],
        ]))
        measures.append(make_measure(self.instrument, 4, [
            eighth_rest,
            [NoteDur.EITH, 100, M.E],
            [NoteDur.EITH, 100, M.F],
            [NoteDur.EITH, 100, M.E],
        ]))
        return measures

    def set_ensemble(self, ensemble: InCEnsemble):
        self.ensemble = ensemble

    def append_note_to_output(self, note: Any) -> None:
        self.output[-1].append(note)

    def copy_cur_phrase_to_output(self) -> None:
        self.output.append(Measure.copy(self.source_phrases[self.phrase_idx]))

    def flush_output_and_reset_state(self) -> None:
        for measure in self.output:
            self.track.append(measure)
        self.output = []
        self.copy_cur_phrase_to_output()
        self.cur_start = 0.0
        self.has_advanced = False

    # TODO
    def perform_phrase(self) -> None:
        # select next phrase to play
        # make a copy of measures in next phrase
        # apply transformations to measures
        # write measures to track
        pass

    def play_next_phrase(self) -> bool:
        has_advanced = self.has_reached_last_phrase() or InCPlayer._should_advance_phrase_idx()
        self._check_has_advanced(has_advanced)
        return self.has_advanced

    def should_play_next_phrase_too_far_behind(self) -> bool:
        if not self.has_advanced and not self.has_reached_last_phrase():
            self._check_has_advanced(self._is_too_far_behind())
        return self.has_advanced

    def play_next_phrase_seeking_unison(self) -> bool:
        if not self.has_advanced and not self.has_reached_last_phrase():
            self._check_has_advanced(self.is_seeking_unison())
        return self.has_advanced

    def should_rest(self) -> bool:
        stay_at_rest_factor = ps.STAY_AT_REST_PROB_FACTOR if self.is_at_rest else ps.NO_FACTOR
        return ps.meets_condition(ps.REST_PROB * stay_at_rest_factor)

    def get_phase_adjustment(self) -> float:
        adjust_phase_prob = ps.ADJ_PHASE_PROB * ps.ADJ_PHASE_PROB_INCREASE_FACTOR
        if self.adjusted_phase_count <= ps.ADJ_PHASE_COUNT_THRESHOLD and ps.meets_condition(adjust_phase_prob):
            self.adjusted_phase_count += 1
            return ps.PHASE_ADJ_DUR
        return 0.0

    def get_amp_adjustment_factor(self) -> float:
        ensemble_max_amp = self.ensemble.aggregate_attr_val(BaseAttrNames.AMPLITUDE.value, max) or 1
        phrase_max_amp = self.phrase_aggregate_attr_val(BaseAttrNames.AMPLITUDE.value, max)
        amp_ratio = phrase_max_amp / ensemble_max_amp
        if self.is_seeking_crescendo() and amp_ratio < ps.AMP_ADJ_CRESCENDO_RATIO_THRESHOLD:
            return ps.AMP_CRESCENDO_ADJ_FACTOR
        elif self.is_seeking_diminuendo() and amp_ratio < ps.AMP_ADJ_DIMINUENDO_RATIO_THRESHOLD:
            return ps.AMP_DIMINUENDO_ADJ_FACTOR
        return ps.NO_FACTOR

    def is_seeking_crescendo(self) -> bool:
        return self.ensemble.is_seeking_crescendo() and ps.meets_condition(ps.CRESCENDO_PROB)

    def is_seeking_diminuendo(self) -> bool:
        return self.ensemble.is_seeking_decrescendo() and ps.meets_condition(ps.DIMINUENDO_PROB)

    def is_seeking_unison(self) -> bool:
        return self.ensemble.is_seeking_unison() and ps.meets_condition(ps.UNISON_PROB)

    def has_reached_last_phrase(self) -> bool:
        return self.phrase_idx == ps.NUM_PHRASES

    def transpose_shift(self) -> float:
        if ps.meets_condition(ps.TRANSPOSE_PROB):
            mean_duration = self.phrase_aggregate_attr_val(BaseAttrNames.DURATION.value, mean)
            if ps.meets_condition(ps.TRANSPOSE_DOWN_PROB) and mean_duration > ps.TRANSPOSE_DOWN_DUR_THRESHOLD:
                return ps.TRANSPOSE_SHIFT * ps.TRANSPOSE_SHIFT_DOWN_FACTOR
            else:
                return ps.TRANSPOSE_SHIFT * ps.TRANSPOSE_SHIFT_UP_FACTOR

    # TODO return type is not correct
    # TODO WHAT IS THIS?
    def num_plays_last_phrase(self) -> float:
        max_start = self.phrase_aggregate_attr_val(BaseAttrNames.START, max)
        return (max_start - self.cur_start) / sum(len(self.output[:-1]))

    def apply_swing(self) -> None:
        for measure in self.output:
            measure.apply_swing()

    def phrase_aggregate_attr_val(self, attr_name: str, agg_func: Callable,
                                  phrase_idx: Optional[int] = None) -> float:
        return agg_func(self._phrase_slice(attr_name, phrase_idx))

    def _is_too_far_behind(self) -> bool:
        return self.ensemble.is_too_far_behind(self.phrase_idx)

    @staticmethod
    def _should_advance_phrase_idx() -> bool:
        return ps.meets_condition(ps.PHRASE_ADVANCE_PROB)

    def _phrase_slice(self, attr_name: str, phrase_idx: Optional[int] = None) -> List[float]:
        return [getattr(note, attr_name) for note in self._get_notes_for_phrase(phrase_idx)]

    def _get_notes_for_phrase(self, phrase_idx: Optional[int] = None) -> Generator:
        # Gets source notes, not modified notes from self.output
        phrase_idx = self.phrase_idx if phrase_idx is None else phrase_idx
        phrase = self.source_phrases[phrase_idx]
        yield from phrase

    def _check_has_advanced(self, has_advanced: Union[bool, Callable]) -> None:
        if isinstance(has_advanced, bool) and has_advanced:
            self.has_advanced = has_advanced
            self.phrase_idx += 1
        else:
            has_advanced_ret = has_advanced()
            if has_advanced_ret:
                self.has_advanced = has_advanced_ret
                self.phrase_idx += 1

    def __str__(self) -> str:
        return (f'{self.track = } '
                f'{self.instrument = } '
                f'{self.phrase_idx = } '
                f'{self.cur_phrase_count = } '
                f'{self.cur_start = } '
                f'{self.adjusted_phase_count = } '
                f'{self.is_at_rest = } '
                f'{self.has_advanced = } '
                f'{self.ensemble = } '
                f'{self.source_phrases = }\n\n')
