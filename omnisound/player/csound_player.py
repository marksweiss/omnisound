# Copyright 2019 Mark S. Weiss

import subprocess

from omnisound.note.containers.song import Song
from omnisound.player.player import Player
from omnisound.utils.utils import validate_optional_type, validate_types


class CsoundPlayer(Player):
    CSOUND_OSX_PATH = '/usr/local/bin/csound'
    # PLAY_ALL = 'play_all'
    # PLAY_EACH = 'play_each'

    def __init__(self, song: Song = None, out_file_path: str = None,
                 score_file_path: str = None, orchestra_file_path: str = None,
                 csound_path: str = None):
        validate_types(('song', song, Song), ('out_file_path', out_file_path, str),
                       ('score_file_path', score_file_path, str), ('orchestra_file_path', orchestra_file_path, str))
        validate_optional_type('csound_path', csound_path, str)
        super(CsoundPlayer, self).__init__()

        self.song = song
        self.out_file_path = out_file_path
        self.score_file_path = score_file_path
        self.orchestra_file_path = orchestra_file_path
        # TODO MAKE MORE PLATFORM-NEUTRAL
        self.csound_path = csound_path or CsoundPlayer.CSOUND_OSX_PATH
        self._include_file_names = []

    # TODO FIX THIS HELPER FUNC
    def play_all(self):
        self._play()

    # TODO FIX THIS HELPER FUNC
    def play_each(self):
        self._play()

    def _play(self):
        with open(self.score_file_path, 'w') as score_file:
            if self._include_file_names:
                for include_file_name in self._include_file_names:
                    score_file.write(f'#include "{include_file_name}"\n')
                score_file.write('\n')

            for track in self.song:
                for measure in track.measure_list:
                    for note in measure:
                        score_file.write(f'{str(note)}\n')

            # -m7 - message level includes `note amps`, `out-of-range` and `warnings`
            # -d - suppress all messages to stdout
            # -g - suppress all graphics
            # -s - short int sound samples # TODO DO WE WANT THIS?
            # -W - .wav output file format
            # -o - rendered output file name
            cmd = (f'{CsoundPlayer.CSOUND_OSX_PATH} -m7 -d -g -s -W -o{self.out_file_path} '
                   f'{self.orchestra_file_path} {self.score_file_path}')
            print(f'Running Csound rendering command: {cmd}')
            subprocess.run(cmd.split())

    def improvise(self):
        raise NotImplementedError('CsoundPlayer does not support improvising')

    def add_score_include_file(self, include_file_name: str):
        self._include_file_names.append(include_file_name)
