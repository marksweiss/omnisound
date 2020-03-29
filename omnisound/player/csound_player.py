# Copyright 2020 Mark S. Weiss

import ctcsound

from omnisound.note.containers.song import Song
from omnisound.player.player import Player
from omnisound.utils.utils import validate_types


class CSoundPlayer(Player):
    def __init__(self, song: Song = None, verbose: bool = False):
        validate_types(('song', song, Song), ('verbose', verbose, bool))
        super(CSoundPlayer, self).__init__()

        self.song = song
        self.verbose = verbose
        self._cs = ctcsound.Csound()

    # TODO FIX THIS HELPER FUNC
    def play_all(self):
        self._play()

    # TODO FIX THIS HELPER FUNC TO YIELD OR USE PERFORMANCE THREAD PER CTCSOUND EXAMPLES
    def play_each(self):
        self._play()

    def _play(self):
        ret = self._cs.compileCsdText(self._to_csd_text())
        if ret == ctcsound.CSOUND_SUCCESS:
            self._cs.start()
            self._cs.perform()
            self._cs.reset()

    # TODO TEMPLATE AND PROPERTIES REQUIRED TO BUILD CSD STR WITH INSTRUMENTS INLINE
    def _to_csd_text(self) -> str:
        score_lines = []
        for track in self.song:
            for measure in track.measure_list:
                for note in measure:
                    score_lines.append(f'{str(note)}\n')
        return '\n'.join(score_lines)

    def improvise(self):
        raise NotImplementedError('CsoundPlayer does not support improvising')
