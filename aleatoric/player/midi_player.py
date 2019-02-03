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

import midi

from aleatoric.note.containers.song import Song
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.player import Player
from aleatoric.utils.utils import validate_optional_path, validate_types


class MidiPlayerAppendMode(Enum):
    AppendAfterPreviousNote = 1
    AppendAtAbsoluteTime = 2


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
        self.midi_track_tick_relative = self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote
        # TODO Support Midi Performance Attrs
        # song_performance_attrs = song.performance_attrs
        self.midi_file_path = midi_file_path
        self.midi_pattern = midi.Pattern()

    def write_midi_file(self):
        midi.write_midifile(self.midi_file_path, self.midi_pattern)

    def play_all(self):
        self._play()  # MidiPlayer.PLAY_ALL)

    def play_each(self):
        self._play()  # MidiPlayer.PLAY_EACH)

    # TODO Support Midi Performance Attrs
    # def _apply_performance_attrs(self, note, *performance_attrs_list):
        # for pa in performance_attrs_list:
        #    apply pa to note

    def _play(self):  # , op: str): # TODO Support Midi Performance Attrs
        def _get_note_start_tick(note, measure, track_tick_offset) -> int:
            """Helper to compute a note start time in ticks depending on whether we are automatically
               appending notes after the previous node or adding notes to the current track at their
               absolute offset since the start of the track.
            """
            note_start_secs = measure.meter.get_secs_for_note_time(note_time_val=note.time)
            if self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote:
                return int(note_start_secs * MidiPlayer.MIDI_TICKS_PER_SECOND) - track_tick_offset
            else:  # if self.append_mode == MidiPlayerAppendMode.AppendAtAbsoluteTime
                return track_tick_offset + int(note_start_secs * MidiPlayer.MIDI_TICKS_PER_SECOND)

        def _get_note_stop_tick(note, measure, track_tick_offset) -> int:
            note_dur_secs = measure.meter.get_secs_for_note_time(note_time_val=note.dur)
            return track_tick_offset + int(note_dur_secs * MidiPlayer.MIDI_TICKS_PER_SECOND)

        def _reset_track_tick_offset_for_measure(track_tick_offset):
            """Encapsulates the logic about what level we are restting the tick offset. If the mode is 'relative',
               i.e. we are appending each note after the previous note, then we reset the offset at the start of
               each measure. If the mode is 'absolute', i.e. we are appending each note at it's absolute start time
               relative to the start of the track, then we do not reset the start_tick.
            """
            if self.append_mode == MidiPlayerAppendMode.AppendAfterPreviousNote:
                return 0
            else:  # if self.append_mode == MidiPlayerAppendMode.AppendAtAbsoluteTime
                return track_tick_offset

        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs

            track_tick_offset = 0
            midi_track = midi.Track(tick_relative=self.midi_track_tick_relative)
            self.midi_pattern.append(midi_track)
            channel = track.channel
            midi_track.append(midi.ProgramChangeEvent(tick=track_tick_offset, channel=channel, data=[track.track_instrument]))

            for measure in track.measure_list:
                # TODO Support Midi Performance Attrs
                # if op == PLAY_ALL
                #     measure_performance_attrs = measure.performance_attrs
                track_tick_offset = _reset_track_tick_offset_for_measure(track_tick_offset)
                for note in measure:
                    # TODO Support Midi Performance Attrs
                    # note_performance_attrs = note.performance_attrs
                    # if op == PLAY_ALL:
                    #     self._apply_performance_attrs(note, song_performance_attrs, track_performance_attrs,
                    #                                   measure_performance_attrs, note_performance_attrs)
                    # else:
                    #     self._apply_performance_attrs(note, note_performance_attrs)

                    start_tick = _get_note_start_tick(note, measure, track_tick_offset)
                    note_on = midi.NoteOnEvent(tick=start_tick, channel=channel, velocity=note.velocity,
                                               pitch=note.pitch)
                    midi_track.append(note_on)

                    stop_tick = _get_note_stop_tick(note, measure, start_tick)
                    note_off = midi.NoteOffEvent(tick=stop_tick, channel=channel, pitch=note.pitch)
                    midi_track.append(note_off)

            if self.append_mode == MidiPlayerAppendMode.AppendAtAbsoluteTime:
                midi_track.make_ticks_rel()
            midi_track.append(midi.EndOfTrackEvent(tick=1, data=[]))

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')