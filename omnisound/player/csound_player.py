# Copyright 2020 Mark S. Weiss

from enum import Enum
from typing import Any, Optional, Sequence, Union

import ctcsound

from omnisound.note.adapters.note import as_list
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.player.player import Player
from omnisound.utils.utils import (validate_type, validate_types, validate_optional_type, validate_optional_types,
                                   validate_optional_sequence_of_type, validate_sequence_of_type,
                                   validate_sequence_of_type_choice)


class InvalidScoreError(Exception):
    pass


class InvalidOrchestraError(Exception):
    pass


class CSoundEventType(Enum):
    AdvanceScorePointer = 0
    EndScore = 1
    Instrument = 2
    FunctionTable = 3
    Quiet = 4


class CSoundScoreEvent:
    EVENT_TYPE_CODES: dict = {
        CSoundEventType.AdvanceScorePointer.name: 'a',
        CSoundEventType.EndScore.name: 'e',
        CSoundEventType.Instrument.name: 'i',
        CSoundEventType.FunctionTable.name: 'f',
        CSoundEventType.Quiet.name: 'q',
    }

    def __init__(self, event_type: CSoundEventType = None, event_data: Sequence[Union[float, int]] = None):
        validate_type('event_type', event_type, CSoundEventType)
        validate_sequence_of_type_choice('event_data', event_data, (float, int))
        self.event_type = event_type
        self.event_data = event_data

    @staticmethod
    def note_to_score_event(note: Any):
        return CSoundScoreEvent(CSoundEventType.Instrument, as_list(note))


# TODO SUPPORT CHANNELS - IN PART TO TAKE MULTITRACK OUTPUT FROM SEQUENCER
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
            # Number output channels (mono, stereo, quadraphonic)
            'nchnls': num_channels,
            # Value of 0 decibels, 1 means don't alert amp of output and is most compatible with plugins
            # Must be written as '0dbfs' in CSound output, but Py vars can't start with a number
            '0dbfs': zed_dbfs
        }

        self.instruments = instruments

    def __str__(self):
        return '''{GLOBAL_VARS}
        {INSTRUMENT}'''.format(
            GLOBAL_VARS='\n'.join(f'{k} = {v}' for k, v in self.global_vars.items()),
            INSTRUMENT='\n'.join(str(instrument) for instrument in self.instruments))


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
            GLOBAL_VARS='\n'.join(f'{k} = {v}' for k, v in self.csound_orchestra.global_vars.items()),
            INSTRUMENTS='\n'.join(str(instrument) for instrument in self.csound_orchestra.instruments),
            SCORE_LINES='\n'.join(str(score_line) for score_line in self.csound_score.score_lines)
        )


class CSoundCSDPlayer(Player):
    def __init__(self,
                 csound_orchestra: Optional[CSoundOrchestra] = None,
                 csound_score: Optional[CSoundScore] = None,
                 song: Optional[Song] = None):
        validate_types(('csound_orchestra', csound_orchestra, CSoundOrchestra),
                       ('csound_score', csound_score, CSoundScore),
                       ('song', song, Song))
        super(CSoundCSDPlayer, self).__init__()

        self.orchestra = csound_orchestra
        if csound_orchestra and csound_score:
            self._csd = CSD(csound_orchestra, csound_score)
        self._song = song

    # Properties
    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song, score_header_lines: Optional[Sequence[str]] = None):
        validate_type('song', song, Song)
        validate_optional_sequence_of_type('score_header_lines', score_header_lines, str)
        self._song = song
        self._set_csd_for_song(score_header_lines=score_header_lines)
    # /Properties

    def _set_csd_for_song(self, score_header_lines: Optional[Sequence[str]] = None):
        # TODO THIS IS BROKEN. It can't play multiple tracks simultaneously. Need to learn about Channels?
        #  Multithreaded interactive player?
        validate_optional_sequence_of_type('score_header_lines', score_header_lines, str)
        for track in self._song:
            self._set_csd_for_track(track, score_header_lines=score_header_lines)

    def _set_csd_for_track(self, track: Track, score_header_lines: Optional[Sequence[str]] = None):
        validate_type('track', track, Track)
        validate_optional_sequence_of_type('score_header_lines', score_header_lines, str)
        note_lines = []
        for measure in track.measure_list:
            for note in measure:
                note_lines.append(f'{str (note)}')
        score = CSoundScore(header_lines=score_header_lines or [''], note_lines=note_lines)
        self._csd = CSD(self.orchestra, score)

    def play(self) -> int:
        cs = ctcsound.Csound()
        rendered_script = self._csd.render()
        if cs.compileCsdText(rendered_script) == ctcsound.CSOUND_SUCCESS:
            cs.start()
            while cs.performKsmps() == ctcsound.CSOUND_SUCCESS:
                pass
            # NOTE: Must follow this order of operations for cleanup to avoid failing to close the CSound object,
            # holding the file handle open and leaking by continuing to write to that file.
            result: int = cs.cleanup()
            cs.reset()
            del cs
            return result
        else:
            raise InvalidScoreError('ctcsound.compileCsdTest() failed for rendered_script {}'.format(rendered_script))

    def play_each(self):
        raise NotImplementedError('CSoundCSDPlayer does not support play_each()')

    def improvise(self):
        raise NotImplementedError('CSoundCSDPlayer does not support improvising')


# TODO add a copy() method so that we can add an notes and then copy the object and change the orchestra
#  in the copy and thus play the same pattern on different instruments
class CSoundInteractivePlayer(Player):
    def __init__(self,
                 csound_orchestra: CSoundOrchestra = None,
                 song: Optional[Song] = None):
        validate_type('csound_orchestra', csound_orchestra, CSoundOrchestra)
        validate_optional_type('song', song, Song)

        super(CSoundInteractivePlayer, self).__init__()
        self._orchestra = csound_orchestra
        self._cs = ctcsound.Csound()
        self._cs.setOption('-d')
        self._cs.setOption('-odac')
        self._cs.setOption('-m0')
        if self._cs.compileOrc(str(self._orchestra)) != ctcsound.CSOUND_SUCCESS:
            raise InvalidOrchestraError('ctcsound.compileOrc() failed for {}'.format(self._orchestra))
        self._song = song

    def play(self) -> int:
        self._cs.start()
        while self._cs.performKsmps() == ctcsound.CSOUND_SUCCESS:
            pass
        # NOTE: Must follow this order of operations for cleanup to avoid failing to close the CSound object,
        # holding the file handle open and leaking by continuing to write to that file.
        result: int = self._cs.cleanup()
        self._cs.reset()
        return result

    def __del__(self):
        del self._cs

    # Properties
    @property
    def orchestra(self):
        return self._orchestra

    @orchestra.setter
    def orchestra(self, csound_orchestra: CSoundOrchestra):
        self._orchestra = csound_orchestra
        if self._cs.compileOrc(str(self._orchestra)) != ctcsound.CSOUND_SUCCESS:
            raise InvalidOrchestraError('ctcsound.compileOrc() failed for {}'.format(self._orchestra))

    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        validate_type('song', song, Song)
        self._song = song
        self.add_song_note_events()
    # /Properties

    def add_score_event(self, event: CSoundScoreEvent):
        validate_type('event', event, CSoundScoreEvent)
        self._cs.scoreEvent(CSoundScoreEvent.EVENT_TYPE_CODES[event.event_type.name], event.event_data)

    def add_score_events(self, events: Sequence[CSoundScoreEvent]):
        validate_sequence_of_type('events', events, CSoundScoreEvent)
        for event in events:
            self.add_score_event(event)

    def add_song_note_events(self, song: Optional[Song] = None):
        validate_optional_type('song', song, Song)
        song = song or self._song
        for track in song:
            self.add_track_note_events(track)

    def add_track_note_events(self, track: Track):
        validate_type('track', track, Track)
        for measure in track.measure_list:
            self.add_score_events([CSoundScoreEvent.note_to_score_event(note) for note in measure])

    def add_end_score_event(self, beats_to_wait: int = 0):
        validate_type('beats_to_wait', beats_to_wait, int)
        if beats_to_wait:
            self._cs.scoreEvent(CSoundScoreEvent.EVENT_TYPE_CODES[CSoundEventType.EndScore.name], (0, beats_to_wait))
        else:
            self._cs.scoreEvent(CSoundScoreEvent.EVENT_TYPE_CODES[CSoundEventType.EndScore.name], ())

    def play_each(self):
        raise NotImplementedError('CSoundInteractivePlayer does not support play_each()')

    def improvise(self):
        raise NotImplementedError('CSoundInteractivePlayer does not support improvising')
