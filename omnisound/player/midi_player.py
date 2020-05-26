# Copyright 2020 Mark S. Weiss

from enum import Enum
from time import sleep
from typing import Any, List, Optional

# noinspection PyProtectedMember
from mido import Message, open_output

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.song import Song
from omnisound.note.modifiers.meter import NoteDur
from omnisound.player.player import Player
from omnisound.utils.utils import validate_optional_types, validate_type, validate_types

MIDI_TICKS_PER_QUARTER_NOTE = 960
MIDI_QUARTER_NOTES_PER_BEAT = 4
MIDI_BEATS_PER_MINUTE = 120
MIDI_TICKS_PER_SECOND = int((MIDI_TICKS_PER_QUARTER_NOTE *
                             MIDI_QUARTER_NOTES_PER_BEAT *
                             MIDI_BEATS_PER_MINUTE)
                            / 60)

DEFAULT_BEAT_DURATION = NoteDur.QUARTER
# PLAY_ALL = 'play_all'
# PLAY_EACH = 'play_each'


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


# TODO MAKE ABC
class MidiPlayerBase(Player):
    def __init__(self,
                 song: Optional[Song] = None,
                 append_mode: MidiPlayerAppendMode = None):
        super(MidiPlayerBase, self).__init__()
        self._song = song
        self.append_mode = append_mode
        self.midi_track_tick_relative = self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote
        # TODO Support Midi Performance Attrs
        # song_performance_attrs = song.performance_attrs

    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        validate_type('song', song, Song)
        self._song = song

    # TODO Support Midi Performance Attrs
    # def _apply_performance_attrs(self, note, *performance_attrs_list):
        # for pa 0in performance_attrs_list:
        #    apply pa to note

    def play(self):
        raise NotImplementedError('MidiPlayerBase.play should not be instantiated')

    def play_each(self):
        raise NotImplementedError('MidiPlayerBase.play_each should not be instantiated')

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support improvising')

    def loop(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support looping')


# TODO SUPPORT MULTIPLE CHANNELS
class MidiInteractiveSingleTrackPlayer(MidiPlayerBase):
    DEFAULT_PORT_NAME = 'MidiInteractiveSingleTrackPlayer_port'
    # TODO FIX THIS WTF!
    SLEEP_DELAY = 0.05

    def __init__(self,
                 song: Optional[Song] = None,
                 append_mode: MidiPlayerAppendMode = None,
                 port_name: Optional[str] = None):
        validate_type('append_mode', append_mode, MidiPlayerAppendMode)
        validate_optional_types(('port_name', port_name, str), ('song', song, Song))
        super(MidiInteractiveSingleTrackPlayer, self).__init__(song=song, append_mode=append_mode)
        self.port_name = port_name or MidiInteractiveSingleTrackPlayer.DEFAULT_PORT_NAME

    def play(self):
        # Single-track player so only process the first track in the song
        track = self.song.track_list[0]
        # Memoize materializing the list of notes since we loop forever over it
        notes = []
        messages = []
        for measure in track:
            for note in measure:
                notes.append(note)
                amplitude = ATTR_GET_TYPE_CAST_MAP['velocity'](note.amplitude)
                pitch = ATTR_GET_TYPE_CAST_MAP['pitch'](note.pitch)
                messages.append(Message('note_on', velocity=amplitude, note=pitch, channel=track.channel))
                messages.append(Message('note_off', velocity=amplitude, note=pitch, channel=track.channel))

        port = open_output(self.port_name, True)
        with port:
            for i in range(len(notes)):
                port.send(messages[i])
                sleep(notes[i].duration)
                port.send(messages[i + 1])

    def play_each(self):
        track = self.song.track_list[0]
        notes = []
        messages = []
        for measure in track:
            for note in measure:
                notes.append(note)
                amplitude = ATTR_GET_TYPE_CAST_MAP['velocity'](note.amplitude)
                pitch = ATTR_GET_TYPE_CAST_MAP['pitch'](note.pitch)
                messages.append(Message('note_on', velocity=amplitude, note=pitch, channel=track.channel))
                messages.append(Message('note_off', velocity=amplitude, note=pitch, channel=track.channel))

        port = open_output(self.port_name, True)
        with port:
            for i in range(len(notes)):
                port.send(messages[i])
                sleep(notes[i].duration)
                port.send(messages[i + 1])

    def loop(self):
        track = self.song.track_list[0]
        notes = []
        messages = []
        for measure in track:
            for note in measure:
                notes.append(note)
                amplitude = ATTR_GET_TYPE_CAST_MAP['velocity'](note.amplitude)
                pitch = ATTR_GET_TYPE_CAST_MAP['pitch'](note.pitch)
                messages.append(Message('note_on', velocity=amplitude, note=pitch, channel=track.channel))
                messages.append(Message('note_off', velocity=amplitude, note=pitch, channel=track.channel))

        port = open_output(self.port_name, True)
        try:
            with port:
                while True:
                    for i in range(len(notes)):
                        port.send(messages[i])
                        sleep(notes[i].duration)
                        port.send(messages[i + 1])
        except KeyboardInterrupt:
            pass

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')
