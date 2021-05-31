# Copyright 2021 Mark S. Weiss

from enum import Enum
from random import randint
from statistics import mean
from typing import Callable, Generic, Optional, Sequence, Tuple, TypeVar

from omnisound.src.composition.in_c.ensemble_settings import EnsembleSettings as es
from omnisound.src.player.ensemble import Ensemble

# Constructed with T = InCPlayer
T = TypeVar('T')


class CrescendoDirection(Enum):
    CRESCENDO = 1,
    DECRESCENDO = -1


class InCEnsemble:
    def __init__(self, to_add: Optional[Sequence[Generic[T]]]):
        self.players = list(to_add)
        self._unison_count = 0
        self.perform_steps_count = 0
        self._reached_concluding_unison = False
        self.crescendo_amp_adj = 0
        self.in_crescendo = False
        self.in_decrescendo = False
        self.crescendo_step_count = 0
        self.max_crescendo_step_count = 0
        self.in_crescendo_decrescendo = False
        self.in_decrescendo_crescendo = False
        self.crescendo_sign = 1

    # TODO
    def perform(self) -> None:
        for player in self.players:
            player.perform_phrase()

    def too_far_behind(self, phrase_idx: int) -> bool:
        return self._max_phrase_idx() - phrase_idx >= es.PHRASES_IDX_RANGE_THRESHOLD

    def seeking_unison(self) -> bool:
        return not self._reached_unison() and \
               self._phrase_idx_range() <= es.MAX_PHRASES_IDX_RANGE_FOR_SEEKING_UNISON and \
               es.meets_condition(es.UNISON_PROB)

    def reached_concluding_unison(self) -> bool:
        if not self._reached_concluding_unison:
            self._reached_concluding_unison = all(player.reached_last_phrase for player in self.players)
        return self._reached_concluding_unison

    def reached_conclusion(self) -> bool:
        return self._unison_count >= len(self)

    def seeking_crescendo(self) -> bool:
        return not self.in_crescendo_decrescendo and es.meets_condition(es.CRESCENDO_PROB)

    def seeking_decrescendo(self) -> bool:
        return not self.in_crescendo_decrescendo and es.meets_condition(es.DECRESCENDO_PROB)

    def in_crescendo_or_decrescendo(self) -> bool:
        return self.in_crescendo_decrescendo or self.in_decrescendo_crescendo

    # TODO Can we simplify all this code to just be "in crescendo" and "criscendo direction"
    def set_crescendo_state(self) -> None:
        self._set_crescendo_state(CrescendoDirection.CRESCENDO)

    # TODO Can we simplify all this code to just be "in crescendo" and "criscendo direction"
    def set_decrescendo_state(self) -> None:
        self._set_crescendo_state(CrescendoDirection.DECRESCENDO)

    # TODO Can we simplify all this code to just be "in crescendo" and "criscendo direction"
    def _set_crescendo_state(self, crescendo_direction: CrescendoDirection) -> None:
        if self.in_decrescendo_crescendo or self.in_crescendo_decrescendo:
            return
        self.max_crescendo_step_count = randint(es.MIN_CRESCENDO_NUM_STEPS,
                                                es.MAX_CRESCENDO_NUM_STEPS - es.MIN_CRESCENDO_NUM_STEPS + 1)
        self.max_crescendo_step_count = min(self.max_crescendo_step_count, es.CRESCENDO_MAX_AMP_RANGE)
        self.crescendo_amp_adj = es.CRESCENDO_MAX_AMP_RANGE / self.max_crescendo_step_count
        self.crescendo_amp_adj = max(self.crescendo_amp_adj, es.DEFAULT_AMP)
        self.crescendo_step_count = 0
        self.in_crescendo_decrescendo = True
        self.crescendo_sign = crescendo_direction.value
        if crescendo_direction == CrescendoDirection.CRESCENDO:
            self.in_crescendo = True
            self.in_decrescendo = False
        else:
            self.in_decrescendo = True
            self.in_crescendo = False

    # TODO Can we simplify all this code to just be "in crescendo" and "criscendo direction"
    def crescendo_increment(self) -> None:
        # Test increment step_count and test for boundary transitions
        #  from crescendo to decrescendo and exit from de/crescendo
        if self.in_crescendo_decrescendo:
            self.in_crescendo, self.in_decrescendo = self._crescendo_increment(self.in_crescendo, self.in_decrescendo)
        elif self.in_decrescendo_crescendo:
            self.in_decrescendo, self.in_crescendo = self._crescendo_increment(self.in_decrescendo, self.in_crescendo)

    def _crescendo_increment(self, crescendo_flag: bool, other_crescendo_flag: bool) -> Tuple[bool, bool]:
        # Case 1: In crescendo but not finished, no switch, just increment step count
        if crescendo_flag and self.crescendo_step_count <= self.max_crescendo_step_count:
            self.crescendo_step_count += 1
        # Case 2: In descrescendo but not finished, no switch, just decrement step count
        elif other_crescendo_flag and self.crescendo_step_count > 0:
            self.crescendo_step_count -= 1
        # Case 3: Just finished crescendo, switch to decrescendo to come back down
        elif crescendo_flag and self.crescendo_step_count > self.max_crescendo_step_count:
            other_crescendo_flag = True
            crescendo_flag = False
            self.crescendo_step_count -= 1
        # Case 4: Finished crescendo and then decrescendo, done with entire cycle, no amp adjustment
        elif other_crescendo_flag and self.crescendo_step_count <= 0:
            self.in_crescendo_decrescendo = False
            other_crescendo_flag = False
            crescendo_flag = False
            self.crescendo_step_count = 0

        return crescendo_flag, other_crescendo_flag

    def crescendo_amp_adjustment(self) -> float:
        if self.in_crescendo_or_decrescendo():
            return self.crescendo_sign * self.crescendo_step_count * self.crescendo_amp_adj
        return 0.0

    def max_amp(self) -> float:
        return max(player.amplitude for player in self.players)

    def aggregate_attr_val(self, attr_name: str, agg_func: Callable) -> float:
        agg_func(player.getatrr(attr_name) for player in self.players)

    def min_attr_val(self, attr_name: str) -> float:
        min(player.getatrr(attr_name) for player in self.players)

    def max_attr_val(self, attr_name: str) -> float:
        max(player.getatrr(attr_name) for player in self.players)

    def mean_attr_val(self, attr_name: str) -> float:
        mean(player.getatrr(attr_name) for player in self.players)

    def _min_phrase_idx(self) -> int:
        return min(player.phrase_idx for player in self.players)

    def _max_phrase_idx(self) -> int:
        return max(player.phrase_idx for player in self.players)

    def _phrase_idx_range(self) -> int:
        return self._max_phrase_idx() - self._max_phrase_idx()

    def _reached_unison(self) -> bool:
        return self._unison_count >= len(self)
