# Copyright 2020 Mark S. Weiss

from enum import Enum
from typing import Any, List, Optional, Sequence

# noinspection PyProtectedMember
from mido import Message, MidiFile, MidiTrack, open_output

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import MidiTrack as OmnisoundMidiTrack
from omnisound.note.modifiers.meter import NoteDur
from omnisound.player.player import Player
from omnisound.utils.utils import validate_optional_path, validate_optional_type, validate_type, validate_types

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
        # MidiPlayer only can play a Song with one or more Tracks. Tracks may be bare NoteSequence collections
        # or Measures with Meter
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

    # TODO MAKE A GENERATOR SO INTERACTIVE PLAYER CAN STREAM
    @staticmethod
    def _get_midi_events_for_track(track: OmnisoundMidiTrack) -> Sequence[Message]:
        messages = []

        # mido channels numbered 0..15 instead of MIDI standard 1..16
        channel = track.channel - 1
        for measure in track.measure_list:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     performance_attrs = measure.performance_attrs
            # Build an ordered event list of the notes in the measure
            # NOTE: Assumes first note start on 0.0, because the first note of every measure is 0 offset
            #       i.e. it assumes it will occur exactly after the last note of the last measure
            # NOTE: Need to carry over last offset from previous measure, and then this will work :-)
            # TODO MAKE MEASURE ALWAYS FILL IN TRAILING (ALL?) RESTS SO THIS IS NOT AN ISSUE
            event_list = []
            for note in measure:
                # noinspection PyTypeChecker
                event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_ON))
                # noinspection PyTypeChecker
                event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_OFF))

            MidiPlayerEvent.set_tick_deltas(event_list)
            for event in event_list:
                # TODO Support Midi Performance Attrs
                # note_performance_attrs = note.performance_attrs
                # if op == PLAY_ALL:
                #     self._apply_performance_attrs(note, song_performance_attrs, track_performance_attrs,
                #                                   performance_attrs, note_performance_attrs)
                # else:
                #     self._apply_performance_attrs(note, note_performance_attrs)
                messages.append(Message(event.event_type.value, time=event.tick_delta,
                                velocity=ATTR_GET_TYPE_CAST_MAP['velocity'](event.note.amplitude),
                                note=ATTR_GET_TYPE_CAST_MAP['pitch'](event.note.pitch),
                                channel=channel))

            return messages

    def _play(self) -> Sequence[MidiTrack]:
        midi_tracks = []

        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs
            midi_track = MidiTrack()
            midi_track.append(Message('program_change', program=track.instrument, time=0))
            messages = MidiPlayerBase._get_midi_events_for_track(track=track)
            for message in messages:
                midi_track.append(message)
            midi_tracks.append(midi_track)

        return midi_tracks

    def play(self):
        raise NotImplementedError('MidiPlayerBase.play should not be instantiated')

    def play_each(self):
        raise NotImplementedError('MidiPlayerBase.play_each should not be instantiated')

    def improvise(self):
        raise NotImplementedError('MidiPlayerBase.improvise should not be instantiated')


class MidiWriter(MidiPlayerBase):
    def __init__(self,
                 song: Optional[Song] = None,
                 append_mode: MidiPlayerAppendMode = None,
                 midi_file_path: str = None):
        validate_type('append_mode', append_mode, MidiPlayerAppendMode)
        validate_optional_type('song', song, Song)
        validate_optional_path('midi_file_path', midi_file_path)
        super(MidiWriter, self).__init__(song=song, append_mode=append_mode)
        self.midi_file_path = midi_file_path
        # Type 1 - multiple synchronous tracks, all starting at the same time
        # https://mido.readthedocs.io/en/latest/midi_files.html
        self.midi_file = MidiFile(type=1)

    def write_midi_file(self):
        self.midi_file.save(self.midi_file_path)

    def play(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def play_each(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')


# TODO SUPPORT MULTIPLE CHANNELS
class MidiInteractivePlayer(MidiPlayerBase):
    def __init__(self,
                 song: Optional[Song] = None,
                 append_mode: MidiPlayerAppendMode = None,
                 port_name: str = None):
        validate_types(('port_name', port_name, str), ('append_mode', append_mode, MidiPlayerAppendMode))
        validate_optional_type('song', song, Song)
        super(MidiInteractivePlayer, self).__init__(song=song, append_mode=append_mode)
        # Second arg creates a virtual port that other listening applications can bind to
        self.port = open_output(port_name, True)

    # TODO MAKE A STREAMING PLAYER
    def play(self):
        for track in self.song:
            # TODO GENERATOR
            for message in self._get_midi_events_for_track(track=track):
                self.port.send(message)

    # TODO MAKE A STREAMING PLAYER
    def play_each(self):
        for track in self.song:
            # TODO GENERATOR
            for message in self._get_midi_events_for_track(track=track):
                self.port.send(message)

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')
