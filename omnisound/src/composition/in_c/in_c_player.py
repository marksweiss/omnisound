# Copyright 2021 Mark S. Weiss

from statistics import mean
from typing import Any, Callable, List, Optional, Sequence, Union

from omnisound.src.composition.in_c.player_settings import PlayerSettings as ps
from omnisound.src.composition.in_c.in_c_ensemble import InCEnsemble
from omnisound.src.container.measure import Measure
from omnisound.src.container.track import Track
from omnisound.src.note.adapter.note import BaseAttrNames


class InCPlayer:
    # TODO
    PHRASES: Sequence[Sequence[Measure]] = []

    def __init__(self, track: Track):
        super().__init__()
        self.track = track
        self.phrase_idx = 0
        self.cur_start = 0.0
        self.adjusted_phase_count = 0.0
        self.is_at_rest = False
        self.has_advanced = False
        # Provide setter to avoid circular initialization issue, to create the Ensemble you need the players
        # but the players need a reference to their ensemble. So first create players and pass them to Ensemble init,
        # then iterate players and set ensemble reference
        self.ensemble = None

    def set_ensemble(self, ensemble: InCEnsemble):
        self.ensemble = ensemble

    # TODO
    def perform_phrase(self) -> None:
        # select next phrase to play
        # make a copy of measures in next phrase
        # apply transformations to measures
        # write measures to track
        pass

    def should_play_next_phrase(self) -> bool:
        has_advanced = self.reached_last_phrase() or InCPlayer.advance_phrase_idx()
        self._check_has_advanced(has_advanced)
        return self.has_advanced

    def should_play_next_phrase_too_far_behind(self) -> bool:
        if not self.has_advanced and not self.reached_last_phrase():
            self._check_has_advanced(self.too_far_behind())
        return self.has_advanced

    def should_play_next_phrase_seeking_unison(self) -> bool:
        if not self.has_advanced and not self.reached_last_phrase():
            self._check_has_advanced(self.seeking_unison())
        return self.has_advanced

    def should_rest(self) -> bool:
        stay_at_rest_factor = ps.STAY_AT_REST_PROB_FACTOR if self.is_at_rest else ps.NO_FACTOR
        return ps.meets_condition(ps.REST_PROB * stay_at_rest_factor)

    def get_phase_adjustment(self) -> float:
        adjust_phase_prob = ps.ADJ_PHASE_PROB * ps.ADJ_PHASE_PROB_INCREASE_FACTOR
        if self.adjusted_phase_count <= ps.ADJ_PHASE_COUNT_THRESHOLD and \
                ps.meets_condition(adjust_phase_prob):
            self.adjusted_phase_count += 1
            return ps.PHASE_ADJ_DUR
        return 0.0

    def get_amp_adjustment_factor(self) -> float:
        ensemble_max_amp = self.ensemble.aggregate_attr_val(BaseAttrNames.AMPLITUDE.value, max) or 1
        measure_max_amp = self._phrase_aggregate_attr_val(BaseAttrNames.AMPLITUDE.value, max)
        amp_ratio = measure_max_amp / ensemble_max_amp
        if self.seeking_crescendo() and amp_ratio < ps.AMP_ADJ_CRESCENDO_RATIO_THRESHOLD:
            return ps.AMP_CRESCENDO_ADJ_FACTOR
        elif self.seeking_diminuendo() and amp_ratio < ps.AMP_ADJ_DIMINUENDO_RATIO_THRESHOLD:
            return ps.AMP_DIMINUENDO_ADJ_FACTOR
        return ps.NO_FACTOR

    def seeking_crescendo(self) -> bool:
        return self.ensemble.seeking_crescendo() and ps.meets_condition(ps.CRESCENDO_PROB)

    def seeking_diminuendo(self) -> bool:
        return self.ensemble.seeking_decrescendo() and ps.meets_condition(ps.DIMINUENDO_PROB)

    def seeking_unison(self) -> bool:
        return self.ensemble.seeking_unison() and ps.meets_condition(ps.UNISON_PROB)

    def reached_last_phrase(self) -> bool:
        return self.phrase_idx == ps.NUM_PHRASES

    def too_far_behind(self) -> bool:
        return self.ensemble.too_far_behind(self.phrase_idx)

    def transpose_shift(self) -> float:
        if ps.meets_condition(ps.TRANSPOSE_PROB):
            mean_duration = self._phrase_aggregate_attr_val(BaseAttrNames.DURATION.value, mean)
            if ps.meets_condition(ps.TRANSPOSE_DOWN_PROB) and mean_duration > ps.TRANSPOSE_DOWN_DUR_THRESHOLD:
                return ps.TRANSPOSE_SHIFT * ps.TRANSPOSE_SHIFT_DOWN_FACTOR
            else:
                return ps.TRANSPOSE_SHIFT * ps.TRANSPOSE_SHIFT_UP_FACTOR

    def num_plays_last_phrase(self) -> float:
        phrase = InCPlayer.PHRASES[self.phrase_idx]
        max_start = self._phrase_aggregate_attr_val(BaseAttrNames.START, max)
        return (max_start - self.cur_start) / sum(len(measure) for measure in phrase)

    def apply_swing(self):
        phrase = InCPlayer.PHRASES[self.phrase_idx]
        for measure in phrase:
            measure.apply_swing()

    @staticmethod
    def advance_phrase_idx() -> bool:
        return ps.meets_condition(ps.PHRASE_ADVANCE_PROB)

    def _phrase_aggregate_attr_val(self, attr_name: str, agg_func: Callable,
                                   phrase_idx: Optional[int] = None) -> float:
        return agg_func(getattr(note, attr_name) for note in self._get_notes_for_phrase(phrase_idx))

    def _phrase_slice(self, attr_name: str, phrase_idx: Optional[int] = None) -> List[float]:
        return [getattr(note, attr_name) for note in self._get_notes_for_phrase(phrase_idx)]

    def _get_notes_for_phrase(self, phrase_idx: Optional[int] = None) -> Sequence[Any]:
        phrase_idx = self.phrase_idx if phrase_idx is None else phrase_idx
        phrase = InCPlayer.PHRASES[phrase_idx]
        return [note for note in phrase]

    def _check_has_advanced(self, has_advanced: Union[bool, Callable]) -> None:
        if isinstance(has_advanced, bool) and has_advanced:
            self.has_advanced = has_advanced
            self.phrase_idx += 1
        else:
            has_advanced_ret = has_advanced()
            if has_advanced_ret:
                self.has_advanced = has_advanced_ret
                self.phrase_idx += 1
