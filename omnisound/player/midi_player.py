# Copyright 2020 Mark S. Weiss

from enum import Enum
from inspect import currentframe
from typing import Any, List, Optional, Sequence, Tuple, Union
import asyncio

# noinspection PyProtectedMember
from mido import Message, open_output

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.track import MidiTrack
from omnisound.note.modifiers.meter import NoteDur
from omnisound.player.player import Player
from omnisound.utils.utils import validate_optional_type, validate_type, validate_types

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
        return MidiPlayerEvent.get_tick(self.measure, self.event_time)

    @staticmethod
    def get_tick(measure: Measure, event_time: Union[float, int]):
        return int(measure.meter.get_secs_for_note_time(note_time_val=event_time) *
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


def get_midi_messages_and_notes_for_track(track: MidiTrack) -> Tuple[Sequence[Message], Sequence[int]]:
    messages = []
    tick = 0
    durations = []
    for measure in track.measure_list:
        for note in measure:
            amplitude = ATTR_GET_TYPE_CAST_MAP['velocity'](note.amplitude)
            pitch = ATTR_GET_TYPE_CAST_MAP['pitch'](note.pitch)
            durations.append(note.duration)
            messages.append(Message('note_on', time=tick,
                                    velocity=amplitude, note=pitch, channel=track.channel))
            # noinspection PyTypeChecker
            tick += MidiPlayerEvent.get_tick(measure, note.duration)
            messages.append(Message('note_off', time=tick,
                                    velocity=amplitude, note=pitch, channel=track.channel))

    return messages, durations


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

    def play(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._play())

    def play_each(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._play())

    async def _play(self):  # sourcery skip: for-index-replacement, for-index-underscore, hoist-statement-from-loop
        # Single-track player so only process the first track in the song
        track = self._song.track_list[0]
        messages, durations = get_midi_messages_and_notes_for_track(track)

        port = open_output(self.port_name, True)
        # TODO NEED SOME INTERACTIVE WAY TO PAUSE AND CONNECT TO VIRTUAL PORT IN LISTENING APP OR DO IT DYNAMICALLY
        # breakpoint()

        loop_duration = messages[-1].time
        with port:
            for i in range(0, len(messages), 2):
                messages[i].time += loop_duration
                port.send(messages[i])
                await asyncio.sleep(durations[int(i / 2)])
                port.send(messages[i + 1])

    def loop(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._loop())

    async def _loop(self):  # sourcery skip: move-assign
        track = self._song.track_list[0]
        messages, durations = get_midi_messages_and_notes_for_track(track)
        port = open_output(self.port_name, True)
        try:
            loop_duration = messages[-1].time
            with port:
                j = 0
                while True:
                    for i in range(0, len(messages), 2):
                        messages[i].time += (j * loop_duration)
                        port.send(messages[i])
                        await asyncio.sleep(durations[int(i / 2)])
                        port.send(messages[i + 1])
                    j += 1
        except KeyboardInterrupt:
            pass

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__}.{currentframe().f_code.co_name} not implemented')
    # /Player API


class MidiInteractiveMultitrackPlayer(Player):
    """Broadcasts messages from a single Omnisound Track to multiple Midi ports"""
    def __init__(self,
                 append_mode: MidiPlayerAppendMode = None,
                 port_name: Optional[str] = None):
        validate_type('append_mode', append_mode, MidiPlayerAppendMode)
        validate_optional_type('port_name', port_name, str)
        super(MidiInteractiveMultitrackPlayer, self).__init__()
        self.append_mode = append_mode
        self.midi_track_tick_relative = self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote
        self.port_name = port_name or f'{self.__class__.__name__}_port'

    def play(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._play())

    def play_each(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._play())

    async def _play(self):  # sourcery skip: for-index-replacement, for-index-underscore, hoist-statement-from-loop
        # Single-track player so only process the first track in the song

        # For each track we get back a tuple of two lists, one of mido MIDI Messages to sent to the output port
        #  and the other of durations for each Message.
        messages_durations_list: Sequence[Tuple[Sequence[Message], Sequence[int]]] = \
                [get_midi_messages_and_notes_for_track(track) for track in self._song]

        port = open_output(self.port_name, True)
        # TODO NEED SOME INTERACTIVE WAY TO PAUSE AND CONNECT TO VIRTUAL PORT IN LISTENING APP OR DO IT DYNAMICALLY
        # breakpoint()

        play_track_tasks = [asyncio.create_task(MidiInteractiveMultitrackPlayer._play_track(messages, durations, port))
                            for messages, durations in messages_durations_list]
        for task in play_track_tasks:
            await task

    @staticmethod
    async def _play_track(messages, durations, port):
        with port:
            loop_duration = messages[-1].time
            for i in range(0, len(messages), 2):
                messages[i].time += loop_duration
                port.send(messages[i])
                await asyncio.sleep(durations[int(i / 2)])
                port.send(messages[i + 1])

    def loop(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._loop())

    async def _loop(self):  # sourcery skip: move-assign
        messages_durations_list: Sequence[Tuple[Sequence[Message], Sequence[int]]] = \
            [get_midi_messages_and_notes_for_track(track) for track in self._song]

        port = open_output(self.port_name, True)
        # TODO NEED SOME INTERACTIVE WAY TO PAUSE AND CONNECT TO VIRTUAL PORT IN LISTENING APP OR DO IT DYNAMICALLY
        # breakpoint()

        play_track_tasks = [asyncio.create_task(MidiInteractiveMultitrackPlayer._loop_track(messages, durations, port))
                            for messages, durations in messages_durations_list]
        for task in play_track_tasks:
            await task

    @staticmethod
    async def _loop_track(messages, durations, port):
        try:
            with port:
                loop_duration = messages[-1].time
                j = 0
                while True:
                    for i in range(0, len(messages), 2):
                        messages[i].time += (j * loop_duration)
                        port.send(messages[i])
                        await asyncio.sleep(durations[int(i / 2)])
                        port.send(messages[i + 1])
                    j += 1
        except KeyboardInterrupt:
            pass

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__}.{currentframe().f_code.co_name} not implemented')
