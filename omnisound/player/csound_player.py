# Copyright 2019 Mark S. Weiss

import os
import subprocess

from omnisound.note.containers.measure import Measure
from omnisound.note.containers.song import Song
from omnisound.note.modifiers.meter import NoteDur
from omnisound.player.player import Player
from omnisound.utils.utils import validate_optional_type, validate_types


class CsoundPlayer(Player):
    DEFAULT_BEAT_DURATION = NoteDur.QUARTER
    CSOUND_OSX_PATH = '/usr/local/bin/csound'
    # PLAY_ALL = 'play_all'
    # PLAY_EACH = 'play_each'

    def __init__(self, song: Song = None, out_file_name: str = None,
                 score_file_name: str = None, score_path: str = None,
                 orchestra:  str = None, csound_path: str = None):
        validate_types(('song', song, Song), ('out_file_name', out_file_name, str),
                       ('score_file_name', score_file_name, str), ('score_path', score_path, str),
                       ('orchestra', orchestra, str))
        validate_optional_type('csound_path', csound_path, str)
        super(CsoundPlayer, self).__init__()

        self.song = song
        self.out_file_name = out_file_name
        self.score_file_name = score_file_name
        self.score_path_name = score_path
        self.score_file_path = os.path.join(self.score_path_name, self.score_file_name)
        self.orchestra = orchestra
        # TODO MAKE MORE PLATFORM-NEUTRAL
        self.csound_path = csound_path or CsoundPlayer.CSOUND_OSX_PATH

    # TODO FIX THIS HELPER FUNC
    def play_all(self):
        self._play()

    # TODO FIX THIS HELPER FUNC
    def play_each(self):
        self._play()

    def _play(self):

        # TODO NEED TO SUPPORT WRITING INCLUDES FOR SCORE INCLUDES
        # Example: "#include \"#{$csound_score_include_file_name}\""

        with open(self.score_file_path, 'w') as score_file:
            for track in self.song:
                for measure in track.measure_list:
                    for note in measure:
                        score_file.write(str(note))

            # -m7 - message level includes `note amps`, `out-of-range` and `warnings`
            # -d - suppress all messages to stdout
            # -g - suppress all graphics
            # -s - short int sound samples # TODO DO WE WANT THIS?
            # -W - .wav output file format
            # -o - rendered output file name
            args = (f'{CsoundPlayer.CSOUND_OSX_PATH} -m7 -d -g -s -W -o{self.out_file_name} '
                    f'{self.orchestra} {self.score_file_path}').split()
            subprocess.run(args)

    def improvise(self):
        raise NotImplementedError('CsoundPlayer does not support improvising')