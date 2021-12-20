# Copyright 2021 Mark S. Weiss

from enum import Enum
from random import randint
from typing import Callable, Generic, Optional, Sequence, Tuple, TypeVar

from omnisound.src.composition.in_c.ensemble_settings import EnsembleSettings as es
from omnisound.src.container.note_sequence import NoteSequence
from omnisound.src.modifier.meter import NoteDur
from omnisound.src.player.play_hook import PlayHook
import omnisound.src.note.adapter.midi_note as midi_note

# Constructed with T = InCPlayer, typed this way to avoid a circular dependency
T = TypeVar('T')


class CrescendoDirection(Enum):
    CRESCENDO = 1,
    DECRESCENDO = -1


class InCEnsemble(PlayHook, Generic[T]):
    def __init__(self, to_add: Optional[Sequence[T]], pulse_player: T):
        super().__init__()
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
        self.pulse_player = pulse_player

    def is_too_far_behind(self, phrase_idx: int) -> bool:
        return self._max_phrase_idx() - phrase_idx >= es.PHRASES_IDX_RANGE_THRESHOLD

    def is_seeking_unison(self) -> bool:
        return not self._reached_unison() and \
               self._phrase_idx_range() <= es.MAX_PHRASES_IDX_RANGE_FOR_SEEKING_UNISON and \
               es.meets_condition(es.UNISON_PROB)

    def has_reached_concluding_unison(self) -> bool:
        if not self._reached_concluding_unison:
            self._reached_concluding_unison = all(player.reached_last_phrase for player in self.players)
        return self._reached_concluding_unison

    def has_reached_conclusion(self) -> bool:

        # TEMP DEBUG
        print(f'\n\n{self._unison_count = } {len(self.players) = }\n\n')

        return self._unison_count >= len(self.players)

    def is_seeking_crescendo(self) -> bool:
        return not self.in_crescendo_decrescendo and es.meets_condition(es.CRESCENDO_PROB)

    def is_seeking_decrescendo(self) -> bool:
        return not self.in_crescendo_decrescendo and es.meets_condition(es.DECRESCENDO_PROB)

    def is_in_crescendo_or_decrescendo(self) -> bool:
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
        self.max_crescendo_step_count = es.MIN_CRESCENDO_NUM_STEPS + \
            randint(1, (es.MAX_CRESCENDO_NUM_STEPS - es.MIN_CRESCENDO_NUM_STEPS) + 1)
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

    # TODO Can we simplify all this code to just be "in crescendo" and "crescendo direction"
    def increment_crescendo(self) -> None:
        # Test increment step_count and test for boundary transitions
        #  from crescendo to decrescendo and exit from de/crescendo
        if self.in_crescendo_decrescendo:
            self.in_crescendo, self.in_decrescendo = self._increment_crescendo(self.in_crescendo, self.in_decrescendo)
        elif self.in_decrescendo_crescendo:
            self.in_decrescendo, self.in_crescendo = self._increment_crescendo(self.in_decrescendo, self.in_crescendo)

    def _increment_crescendo(self, crescendo_flag: bool, other_crescendo_flag: bool) -> Tuple[bool, bool]:
        # Case 1: In crescendo but not finished, no switch, just increment step count
        if crescendo_flag and self.crescendo_step_count <= self.max_crescendo_step_count:
            self.crescendo_step_count += 1
        # Case 2: In descrescendo but not finished, no switch, just decrement step count
        elif other_crescendo_flag and self.crescendo_step_count > 0:
            self.crescendo_step_count -= 1
        # Case 3: Just finished crescendo, switch to decrescendo to come back down
        elif crescendo_flag:
            other_crescendo_flag = True
            crescendo_flag = False
            self.crescendo_step_count -= 1
        # Case 4: Finished crescendo and then decrescendo, done with entire cycle, no amp adjustment
        elif other_crescendo_flag:
            self.in_crescendo_decrescendo = False
            other_crescendo_flag = False
            crescendo_flag = False
            self.crescendo_step_count = 0

        return crescendo_flag, other_crescendo_flag

    def get_crescendo_amp_adjustment(self) -> float:
        if self.is_in_crescendo_or_decrescendo():
            return self.crescendo_sign * self.crescendo_step_count * self.crescendo_amp_adj
        return 0.0

    def output_pulse_phrase(self):
        """
        Implement Instruction 7, one player emits a repeating eighth-note pulse, precisely in time.
        In order to always have this "backing" all other output, we get the longest phrase that any
        player is current positioned at, and output that length in eighth notes.
        """
        longest_phrase_dur = max(player.phrase_aggregate_attr_val('duration', sum) for player in self.players)
        # 8 1/8 notes per whole note
        num_pulse_notes = int((1. / NoteDur.EIGHTH.value) * longest_phrase_dur)
        for _ in range(num_pulse_notes):
            pulse_note = NoteSequence.new_note(midi_note.DEFAULT_MAKE_NOTE_CONFIG)
            pulse_note.duration = NoteDur.EIGHTH.value
            pulse_note.volume = es.PULSE_AMPLITUDE
            self.pulse_player.append_note_to_output(pulse_note)

    def max_amp(self) -> float:
        return max(player.amplitude for player in self.players)

    def aggregate_attr_val(self, attr_name: str, agg_func: Callable) -> float:
        agg_func(player.getatrr(attr_name) for player in self.players)

    def _min_phrase_idx(self) -> int:
        return min(player.phrase_idx for player in self.players)

    def _max_phrase_idx(self) -> int:
        return max(player.phrase_idx for player in self.players)

    def _phrase_idx_range(self) -> int:
        return self._max_phrase_idx() - self._min_phrase_idx()

    def _reached_unison(self) -> bool:
        return self._unison_count >= len(self)

    def __str__(self):
        return (f'{self.players = } '
                f'{self._unison_count = } '
                f'{self.perform_steps_count = } '
                f'{self._reached_concluding_unison = } '
                f'{self.crescendo_amp_adj = } '
                f'{self.in_crescendo = } '
                f'{self.in_decrescendo = } '
                f'{self.crescendo_step_count = } '
                f'{self.max_crescendo_step_count = } '
                f'{self.in_crescendo_decrescendo = } '
                f'{self.in_decrescendo_crescendo = } '
                f'{self.crescendo_sign = } '
                f'{self.pulse_player = }\n\n')
