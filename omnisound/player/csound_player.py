# Copyright 2020 Mark S. Weiss

from typing import Optional, Sequence

import ctcsound

from omnisound.player.player import Player
from omnisound.utils.utils import (validate_types, validate_optional_type, validate_optional_types,
                                   validate_optional_sequence_of_type, validate_sequence_of_type)

class InvalidScoreError(Exception):
    pass


# TODO MOVE TO OWN SOURCE FILE
class CSoundScore:
    def __init__(self, note_lines: Sequence[str] = None,
                 include_lines: Optional[Sequence[str]] = None,
                 header_lines: Optional[Sequence[str]] = None):
        validate_sequence_of_type('note_lines', note_lines, str)
        validate_optional_sequence_of_type('include_lines', include_lines, str)
        validate_optional_sequence_of_type('header_lines', header_lines, str)

        self.score_lines = []
        if include_lines:
            self.score_lines.extend(include_lines)
        if header_lines:
            self.score_lines.extend(header_lines)
        self.score_lines.extend(note_lines)


# TODO MOVE TO OWN SOURCE FILE
class CSoundOrchestra:
    def __init__(self,
                 instruments: Sequence[str] = None,
                 sampling_rate: int = 44100,
                 ksmps: int = 100,
                 num_channels: int = 1,
                 zed_dbfs: int = 1):
        validate_sequence_of_type('instruments', instruments, str)
        validate_optional_types(('sampling_rate', sampling_rate, int), ('ksmps', ksmps, int),
                                ('num_channels', num_channels, int), ('zed_dbfs', zed_dbfs, int))

        # These keys should always be defined. Their values are sensible CSound defaults that can be set
        #  to other values if you know what you are doing.
        self.global_vars = {
            # Output sampling rate
            'sr': sampling_rate,
            # Ratio of output sampling rate to control rate (actual samples per control period)
            'ksmps': ksmps,
            # Number output channels (mono, stereo, quadrophonic)
            'nchnls': num_channels,
            # Value of 0 decibels, 1 means don't alert amp of output and is most compatible with plugins
            # Must be written as '0dbfs' in CSound output, but Py vars can't start with a number
            '0dbfs': zed_dbfs
        }

        self.instruments = instruments


# TODO MOVE TO OWN SOURCE FILE?
class CSD:
    def __init__(self, csound_orchestra: CSoundOrchestra, csound_score: CSoundScore):
        self.csound_orchestra = csound_orchestra
        self.csound_score = csound_score

    # -d - suppress output
    # -odac - send output to device audio output
    # -m0 - raw amplitude with no highlighting in display for out of bound values
    DEFAULT_FLAGS = '-d -odac -m0'

    TEMPLATE = '''
    <CsoundSynthesizer>

    <CsOptions>
        {DEFAULT_FLAGS} 
    </CsOptions>

    <CsInstruments>
        {GLOBAL_VARS}
        
        {INSTRUMENTS}
    </CsInstruments>

    <CsScore>
        {SCORE_LINES}
    </CsScore>
    </CsoundSynthesizer>
    '''

    def render(self):
        return CSD.TEMPLATE.format(
            DEFAULT_FLAGS=CSD.DEFAULT_FLAGS,
            GLOBAL_VARS='\n'.join('{} = {}'.format(k, v) for k, v in self.csound_orchestra.global_vars),
            INSTRUMENTS='\n'.join(str(instrument) for instrument in self.csound_orchestra.instruments),
            SCORE_LINES='\n'.join(str(score_line) for score_line in self.csound_score.score_lines)
        )


class CSoundPlayer(Player):
    def __init__(self,
                 csound_orchestra: CSoundOrchestra = None,
                 csound_score: CSoundScore = None):
        validate_types(('csound_orchestra', csound_orchestra, CSoundOrchestra),
                       ('csound_score', csound_score, CSoundScore))
        super(CSoundPlayer, self).__init__()

        self._csd = CSD(csound_orchestra, csound_score)
        self._cs = ctcsound.Csound()

    # TODO FIX THIS HELPER FUNC
    def play_all(self):
        self._play()

    # TODO FIX THIS HELPER FUNC TO YIELD OR USE PERFORMANCE THREAD PER CTCSOUND EXAMPLES
    def play_each(self):
        self._play()

    def _play(self):
        rendered_script = self._csd.render()
        if self._cs.compileCsdText(rendered_script) == ctcsound.CSOUND_SUCCESS:
            self._cs.start()
            self._cs.perform()
            self._cs.reset()
        else:
            raise InvalidScoreError('ctcsound.compileCsdTest() failed for rendered_script {}'.format(rendered_script))

    def improvise(self):
        raise NotImplementedError('CsoundPlayer does not support improvising')
