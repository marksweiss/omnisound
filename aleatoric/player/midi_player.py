# Copyright 2018 Mark S. Weiss

# 960 ticks per qn
# 4 q per beat
# 60 bpm
# 240 qpm
# 240 * 960 / 60

# adjbpm = int (60.0 * 1000000.0 / tempo)
# 60 seconds * 1M (ticks per second) / beats per minute
# 1M (ticks per second) / beats per minute * 60
# 1M (ticks per second) / beats per second

from enum import Enum
from typing import List

from mido import Message, MidiFile, MidiTrack

from aleatoric.note.adapters.midi_note import MidiNote
from aleatoric.note.containers.measure import Measure
from aleatoric.note.containers.song import Song
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.player import Player
from aleatoric.utils.utils import validate_optional_path, validate_types

# TODO FILL OUT TYPE HINTS IN THIS CLASS
# TODO TESTS!!!


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
       time since the start of the elements in the sequence), and tick_delta, the offset of this
       event's tick to the event that preceded it in a sequence.
    """
    def __init__(self, note: MidiNote, measure: Measure, event_type: MidiEventType):
        validate_types(('note', note, MidiNote), ('event_type', event_type, MidiEventType))
        self.note = note
        self.measure = measure
        self.event_type = event_type
        self.event_time = self._event_time()
        self.tick = self._tick()
        self.tick_delta = 0

    def _event_time(self) -> float:
        if self.event_type == MidiEventType.NOTE_ON:
            return self.note.time
        elif self.event_type == MidiEventType.NOTE_OFF:
            return self.note.time + self.note.dur

    def _tick(self) -> int:
        return int(self.measure.meter.get_secs_for_note_time(note_time_val=self.event_time) *
            MidiPlayer.MIDI_TICKS_PER_SECOND)

    @staticmethod
    def order_event_list(event_list: List['MidiPlayerEvent']):
        event_list.sort(key=lambda event: event.tick)

    @staticmethod
    def set_tick_deltas(event_list: List['MidiPlayerEvent']):
        MidiPlayerEvent.order_event_list(event_list)
        for i, event in enumerate(event_list[1:]):
            j = i + 1
            event.tick_delta = event.tick - event_list[j - 1].tick


# TODO ONLY GARAGEBAND CAN OPEN THE FILES PRODUCED BY THIS, AND THEN ONLY FIRST TRACK
class MidiPlayer(Player):
    MIDI_TICKS_PER_QUARTER_NOTE = 960
    MIDI_QUARTER_NOTES_PER_BEAT = 4
    MIDI_BEATS_PER_MINUTE = 120
    MIDI_TICKS_PER_SECOND = int((MIDI_TICKS_PER_QUARTER_NOTE *
                                 MIDI_QUARTER_NOTES_PER_BEAT *
                                 MIDI_BEATS_PER_MINUTE)
                                / 60)

    DEFAULT_BEAT_DURATION = NoteDur.QUARTER
    PLAY_ALL = 'play_all'
    PLAY_EACH = 'play_each'

    def __init__(self, song: Song = None, append_mode: MidiPlayerAppendMode = None,
                 midi_file_path: str = None):
        # TODO REVSIT WHY SONG CANNOT BE A NOTE SEQUENCE. IT SHOULD BE AND PLAYER DESIGN IS BREAKING BECAUST IT ISN'T
        # MidiPlayer only can play a Song with one or more Tracks. Tracks may be bare NoteSequence collections
        # or Measures with Meter
        validate_types(('song', song, Song), ('append_mode', append_mode, MidiPlayerAppendMode))
        validate_optional_path('midi_file_path', midi_file_path)
        super(MidiPlayer, self).__init__()

        self.song = song
        self.append_mode = append_mode
        self.midi_file_path = midi_file_path
        self.midi_track_tick_relative = self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote
        # Type 1 - multiple synchronous tracks, all starting at the same time
        # https://mido.readthedocs.io/en/latest/midi_files.html
        self.midi_file = MidiFile(type=1)
        # TODO Support Midi Performance Attrs
        # song_performance_attrs = song.performance_attrs

    def write_midi_file(self):
        self.midi_file.save(self.midi_file_path)

    def play_all(self):
        self._play()  # MidiPlayer.PLAY_ALL)

    def play_each(self):
        self._play()  # MidiPlayer.PLAY_EACH)

    # TODO Support Midi Performance Attrs
    # def _apply_performance_attrs(self, note, *performance_attrs_list):
        # for pa 0in performance_attrs_list:
        #    apply pa to note

    def _play(self):  # , op: str): # TODO Support Midi Performance Attrs
        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs

            midi_track = MidiTrack()
            midi_track.append(Message('program_change', program=track.track_instrument, time=0))
            self.midi_file.tracks.append(midi_track)

            # mido channels numbered 0..15 instead of MIDI standard 1..16
            channel = track.channel - 1
            for measure in track.measure_list:
                # TODO Support Midi Performance Attrs
                # if op == PLAY_ALL
                #     measure_performance_attrs = measure.performance_attrsj
                # Build an ordered event list of the notes in the measure
                # NOTE: Assumes first note start on 0.0, because the first note of every measure is 0 offset
                #       i.e. it assumes it will occur exactly after the last note of the last measure
                # NOTE: Need to carry over last offset from previous measure, and then this will work :-)
                # TODO MAKE MEAURE ALWAYS FILL IN TRAILING (ALL?) RESTS SO THIS IS NOT AN ISSUE
                event_list = []
                for note in measure:
                    event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_ON))
                    event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_OFF))
                MidiPlayerEvent.set_tick_deltas(event_list)

                for event in event_list:
                    # TODO Support Midi Performance Attrs
                    # note_performance_attrs = note.performance_attrs
                    # if op == PLAY_ALL:
                    #     self._apply_performance_attrs(note, song_performance_attrs, track_performance_attrs,
                    #                                   measure_performance_attrs, note_performance_attrs)
                    # else:
                    #     self._apply_performance_attrs(note, note_performance_attrs)
                    message = Message(event.event_type.value, time=event.tick_delta, velocity=event.note.amp,
                                      note=event.note.pitch, channel=channel)
                    midi_track.append(message)

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')