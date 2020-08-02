# Copyright 2019 Mark S. Weiss

from pathlib import Path
from typing import Sequence

from omnisound.note.container.song import Song
from omnisound.player.player import Writer
from omnisound.utils.validation_utils import validate_optional_type, validate_types


class CSoundWriter(Writer):
    # TODO MAKE MORE PLATFORM-NEUTRAL
    CSOUND_OSX_PATH = Path('/usr/local/bin/csound')

    def __init__(self, song: Song = None,
                 out_file_path: Path = None,
                 score_file_path: Path = None,
                 orchestra_file_path: Path = None,
                 csound_path: Path = None,
                 verbose: bool = False):
        validate_types(('song', song, Song),
                       ('out_file_path', out_file_path, Path),
                       ('score_file_path', score_file_path, Path),
                       ('orchestra_file_path', orchestra_file_path, Path),
                       ('verbose', verbose, bool))
        validate_optional_type('csound_path', csound_path, Path)
        super(CSoundWriter, self).__init__()

        self._song = song
        self.out_file_path = out_file_path
        self.score_file_path = score_file_path
        self.orchestra_file_path = orchestra_file_path
        self._score_file_lines = []
        self.csound_path = csound_path or CSoundWriter.CSOUND_OSX_PATH
        self.verbose = verbose
        self._include_file_names = []

    # PlayerBase Properties
    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        self._song = song
    # /PlayerBase Properties

    # Writer API
    def write(self) -> None:
        with open(str(self.score_file_path), 'w') as score_file:
            score_file.write('\n'.join(self._score_file_lines))

    def generate(self) -> Sequence[str]:
        if self._include_file_names:
            for include_file_name in self._include_file_names:
                self._score_file_lines.append(f'#include "{include_file_name}"\n')

        for track in self.song:
            for measure in track.measure_list:
                for note in measure:
                    self._score_file_lines.append(f'{str(note)}\n')

        return self._score_file_lines
    # /Writer API

    def get_csound_cli_command(self) -> str:
        # -m7 - message level includes `note amps`, `out-of-range` and `warnings`
        # -d - suppress all messages to stdout
        # -g - suppress all graphics
        # -s - short int sound samples
        # -W - .wav output file format
        # -o - rendered output file name
        cmd = (f'{CSoundWriter.CSOUND_OSX_PATH} -m7 -s -W -o{self.out_file_path} '
               f'{self.orchestra_file_path} {self.score_file_path}')
        print(f'{cmd}')

        # TODO GENERATES THE COMMAND STRING BUT ACTUALLY RUNNING IT FROM WITHIN PYTHON SILENTLY
        #  COMPLETES, RETURNS 255 (CSound return code for 'help'), AND DOES NOT WRITE *.WAV OUTPUT
        # subprocess.call(cmd.split(), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return cmd

    def add_score_include_file(self, include_file_name: str):
        self._include_file_names.append(include_file_name)
