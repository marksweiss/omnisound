# Copyright 2021 Mark S. Weiss

from omnisound.src.composition.in_c.player_settings import PlayerSettings as ps
from omnisound.src.player.midi.midi_writer import MidiWriter
from omnisound.src.player.ensemble import Ensemble

from typing import Callable, Union

class InCPlayer(MidiWriter):
    def __init__(self, ensemble: Ensemble):
        super ().__init__ ()
        self.phrase_idx = 0
        self.cur_measure_start = 0.0
        self.adjusted_phase_count = 0.0
        self.is_at_rest = False
        self.has_advanced = False
        self.ensemble = ensemble

    def reached_last_phrase(self) -> bool:
        return self.phrase_idx == ps.NUM_PHRASES

    def playing_next_phrase(self) -> bool:
        has_advanced = self.reached_last_phrase() or self.advance_phrase_idx()
        self._check_has_advanced(has_advanced)
        return self.has_advanced

    def playing_next_phrase_too_far_behind(self) -> bool:
        if not self.has_advanced and not self.reached_last_phrase():
            self._check_has_advanced(self.is_too_far_behind())
        return self.has_advanced

    def is_too_far_behind(self) -> bool:
        return self.ensemble.is_too_far_behind(self.phrase_idx)

    @staticmethod
    def advance_phrase_idx():
        return ps.meets_condition(ps.PHRASE_ADVANCE_PROB)

    def _check_has_advanced(self, has_advanced: Union[bool, Callable]) -> None:
        if isinstance(has_advanced, bool) and has_advanced:
            self.has_advanced = has_advanced
            self.phrase_idx += 1
        else:
            has_advanced_ret = has_advanced()
            if has_advanced_ret:
                self.has_advanced = has_advanced_ret
                self.phrase_idx += 1

