# Copyright 2020 Mark S. Weiss

from copy import deepcopy
from enum import Enum
from functools import partial
from inspect import currentframe
from sys import maxsize
from typing import Any, List, Optional, Sequence, Tuple, Union
import asyncio

# noinspection PyProtectedMember
from mido import Message, open_output
from mido.backends.rtmidi import Output
from mido.ports import MultiPort
from numpy import argmin

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import MidiTrack
from omnisound.note.modifiers.meter import NoteDur
from omnisound.player.player import Player
from omnisound.utils.utils import (validate_optional_type, validate_optional_types, validate_optional_sequence_of_type,
                                   validate_type, validate_types)

MIDI_TICKS_PER_QUARTER_NOTE = 960
MIDI_QUARTER_NOTES_PER_BEAT = 4
MIDI_BEATS_PER_MINUTE = 120
MIDI_TICKS_PER_SECOND = int((MIDI_TICKS_PER_QUARTER_NOTE *
                             MIDI_QUARTER_NOTES_PER_BEAT *
                             MIDI_BEATS_PER_MINUTE)
                            / 60)

DEFAULT_BEAT_DURATION = NoteDur.QUARTER


class MidiPlayerAppendMode(Enum):
    AppendAfterPreviousNote = 1
    AppendAtAbsoluteTime = 2


class MidiEventType(Enum):
    NOTE_ON = 'note_on'
    NOTE_OFF = 'note_off'


class MidiPlayerEvent(object):
    """Small type to handle the business logic of creating a sequence of ordered MIDI events,
       ordered by absolute time of the event, and annotated with their delta time (the offset
       time from the previous event in a sequence). Each object takes a note and an EventType
       and calculates its own event_time. `order_events()` orders a sequence of events.

       The object also includes properties for tick (the time converted to MIDI tick), in absolute
       time since the start of the elements in the sequence, and tick_delta, the offset of this
       event's tick to the event that preceded it in a sequence.
    """
    def __init__(self, note: Any,
                 measure: Measure,
                 event_type: MidiEventType):
        validate_types(('measure', measure, Measure), ('event_type', event_type, MidiEventType))
        self.note = note
        self.measure = measure
        self.event_type = event_type
        self.event_time = abs(self._event_time())
        self.tick = self._tick()
        self.tick_delta = 0

    def _event_time(self) -> float:
        if self.event_type == MidiEventType.NOTE_ON:
            return self.note.time
        elif self.event_type == MidiEventType.NOTE_OFF:
            return self.note.time + self.note.duration

    def _tick(self) -> int:
        return int(self.measure.meter.get_secs_for_note_time(note_time_val=self.event_time) *
                   MIDI_TICKS_PER_SECOND)

    @staticmethod
    def order_event_list(event_list: List['MidiPlayerEvent']):
        event_list.sort(key=lambda event: event.tick)

    @staticmethod
    def set_tick_deltas(event_list: List['MidiPlayerEvent']):
        MidiPlayerEvent.order_event_list(event_list)
        for i, event in enumerate(event_list[1:]):
            j = i + 1
            event.tick_delta = event.tick - event_list[j - 1].tick


def get_midi_messages_and_notes_for_track(track: MidiTrack) -> Tuple[Sequence[Message], Sequence[Any]]:
    notes = []
    messages = []
    for measure in track:
        for note in measure:
            notes.append(note)
            amplitude = ATTR_GET_TYPE_CAST_MAP['velocity'](note.amplitude)
            pitch = ATTR_GET_TYPE_CAST_MAP['pitch'](note.pitch)
            messages.append(Message('note_on', velocity=amplitude, note=pitch, channel=track.channel))
            messages.append(Message('note_off', velocity=amplitude, note=pitch, channel=track.channel))
    return messages, notes


async def _play_note_on_off(delay: float, messages: Tuple[Message, Message], port: Union[MultiPort, Output] = None):
    port.send(messages[0])
    await asyncio.sleep(delay)
    port.send(messages[1])


class MidiInteractiveSingleTrackPlayer(Player):
    def __init__(self,
                 append_mode: MidiPlayerAppendMode = None,
                 port_name: Optional[str] = None):
        validate_type('append_mode', append_mode, MidiPlayerAppendMode)
        validate_optional_type('port_name', port_name, str)
        super(MidiInteractiveSingleTrackPlayer, self).__init__()
        self.append_mode = append_mode
        self.midi_track_tick_relative = self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote
        self.port_name = port_name or f'{self.__class__.__name__}_port'

    # BasePlayer Properties
    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        validate_type('song', song, Song)
        self._song = song
    # /BasePlayer Properties

    # Player API
    # noinspection PyAsyncCall
    async def play(self):
        # Single-track player so only process the first track in the song
        track = self._song.track_list[0]
        messages, notes = get_midi_messages_and_notes_for_track(track)

        port = open_output(self.port_name, True)
        with port:
            for i in range(len(notes)):
                await _play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]), port)

    async def play_each(self):
        track = self._song.track_list[0]
        messages, notes = get_midi_messages_and_notes_for_track(track)

        port = open_output(self.port_name, True)
        with port:
            for i in range(len(notes)):
                await _play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]), port)

    def loop(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.__play_note_on_off())

    async def __play_note_on_off(self):
        track = self._song.track_list[0]
        messages, notes = get_midi_messages_and_notes_for_track(track)
        port = open_output(self.port_name, True)
        try:
            while True:
                with port:
                    for i in range(len(notes)):
                        await _play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]), port)
        except KeyboardInterrupt:
            pass

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__}.{currentframe().f_code.co_name} not implemented')
    # /Player API


# class MidiInteractiveMulticastPlayer(Player, MidiPlayerBase):
#     def __init__(self,
#                  song: Optional[Song] = None,
#                  append_mode: MidiPlayerAppendMode = None,
#                  num_ports: int = None,
#                  port_names: Optional[Sequence[str]] = None):
#         validate_types(('append_mode', append_mode, MidiPlayerAppendMode), ('num_ports', num_ports, int))
#         validate_optional_type('song', song, Song)
#         validate_optional_sequence_of_type('port_names', port_names, str)
#         if port_names:
#             assert num_ports == len(port_names)
#             self.port_names = deepcopy(port_names)
#         else:
#             self.port_names = [f'{self.__class__.__name__}_{i}'
#                                for i in range(num_ports)]
#         super(MidiInteractiveMulticastPlayer, self).__init__(song=song, append_mode=append_mode)
#         ports = [open_output(port_name) for port_name in self.port_names]
#         self._multi_port = MultiPort(ports)
#
#     # BasePlayer Properties
#     @property
#     def song(self):
#         return self._song
#
#     @song.setter
#     def song(self, song: Song):
#         validate_type('song', song, Song)
#         self._song = song
#     # /BasePlayer Properties
#
#     # Player API
#     async def play(self):
#         # Single-track multicast to multiple ports player so only process the first track in the song
#         track = self.song.track_list[0]
#         messages, notes = MidiPlayerBase.get_midi_messages_and_notes_for_track(track)
#         for i in range(len(notes)):
#             await MidiPlayerBase._play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]), self._multi_port)
#
#     async def play_each(self):
#         track = self.song.track_list[0]
#         messages, notes = MidiPlayerBase.get_midi_messages_and_notes_for_track(track)
#         for i in range(len(notes)):
#             await MidiPlayerBase._play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]), self._multi_port)
#
#     async def loop(self):
#         track = self.song.track_list[0]
#         messages, notes = MidiPlayerBase.get_midi_messages_and_notes_for_track(track)
#         try:
#             while True:
#                 for i in range(len(notes)):
#                     await MidiPlayerBase._play_note_on_off(notes[i].duration, (messages[i], messages[i + 1]),
#                                                            self._multi_port)
#         except KeyboardInterrupt:
#             pass
#
#     def improvise(self):
#         raise NotImplementedError(f'{self.__class__.__name__}.{currentframe().f_code.co_name} not implemented')
#
#
# class MidiInteractiveMultitrackPlayer(Player, MidiPlayerBase):
#     """Broadcasts messages from a single Omnisound Track to multiple Midi ports"""
#
#     DEFAULT_PORT_NAME = 'MidiInteractiveMultitrackPlayer_port'
#
#     def __init__(self,
#                  song: Optional[Song] = None,
#                  append_mode: MidiPlayerAppendMode = None,
#                  port_names: Optional[Sequence[str]] = None):
#         validate_type('append_mode', append_mode, MidiPlayerAppendMode)
#         validate_optional_type('song', song, Song)
#         validate_optional_sequence_of_type('port_names', port_names, str)
#         if port_names:
#             assert len(port_names) == len(song)
#             self.port_names = deepcopy(port_names)
#         else:
#             self.port_names = [(f'{song.name or "song"}_'
#                                 f'{song[i].name or MidiInteractiveMultitrackPlayer.DEFAULT_PORT_NAME}_{i}')
#                                for i in range(len(song))]
#         super(MidiInteractiveMultitrackPlayer, self).__init__(song=song, append_mode=append_mode)
#
#         ports = [open_output(port_name) for port_name in self.port_names]
#
#         # noinspection PyAsyncCall
#         async def _play_note_on_off(note, track=None, port=None):
#             note_on = Message('note_on', velocity=note.amplitude, note=note.pitch, channel=track.channel)
#             note_off = Message('note_off', velocity=note.amplitude, note=note.pitch, channel=track.channel)
#             port.send(note_on)
#             asyncio.sleep(note.duration)
#             port.send(note_off)
#         self._play_callbacks = [partial(_play_note_on_off, track=self.song[i], port=ports[i])
#                                 for i in range(len(self.song))]
#
#     # BasePlayer Properties
#     @property
#     def song(self):
#         return self._song
#
#     @song.setter
#     def song(self, song: Song):
#         validate_type('song', song, Song)
#         self._song = song
#     # /BasePlayer Properties
#
#     # Player API
#     async def play(self):
#         await self._play()
#
#     async def play_each(self):
#         await self._play()
#
#     async def loop(self):
#         while True:
#             await self._play()
#
#     def improvise(self):
#         raise NotImplementedError(f'{self.__class__.__name__}.{currentframe().f_code.co_name} not implemented')
#     # /Player API
#
#     async def _play(self):
#         # Loop until we have consumed all notes in all tracks in the song.
#         # On each iteration find the track whose current start position (sum of all note durations played for that
#         # track) is the minimum. Get the next note in that track, increment it's offset, and play that note. Each
#         # track has a dedicated partial which binds the play callback function to play notes to its own mido
#         # MIDI port. So this design combined with async tasks lets us concurrently send messages for each track to
#         # its own port, always sending the next one in order across all the tracks.
#         has_notes = [True] * len(self.song)
#         track_start_offsets = [0.0] * len(self.song)
#         while any(has_notes):
#             track_idx = int(argmin(track_start_offsets))
#             track = self.song.track_list[track_idx]
#             try:
#                 note = next(track.next_note())
#                 track_start_offsets[track_idx] += note.duration
#                 task = asyncio.create_task(self._play_callbacks[track_idx](note))
#                 await task
#             except StopIteration:
#                 has_notes[track_idx] = False
#                 # Finished playing track, ensure that this track isn't picked as having the minimum offset value
#                 track_start_offsets[track_idx] = maxsize
