# Copyright 2020 Mark S. Weiss

from typing import Optional, Sequence

from mido.midifiles.midifiles import Message, MidiFile, MidiTrack
from omnisound.utils.utils import validate_optional_path, validate_optional_type, validate_type

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import MidiTrack as OmnisoundMidiTrack
from omnisound.player.midi_player import MidiEventType, MidiPlayerBase, MidiPlayerEvent, MidiPlayerAppendMode


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

    def play(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def play_each(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def write_midi_file(self):
        self.midi_file.save(self.midi_file_path)

    @staticmethod
    def _get_midi_events_for_track(track: OmnisoundMidiTrack) -> Message:
        # mido channels numbered 0..15 instead of MIDI standard 1..16
        event_list = []
        for measure in track:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     performance_attrs = measure.performance_attrs
            # Build an ordered event list of the notes in the measure
            # NOTE: Assumes first note start on 0.0, because the first note of every measure is 0 offset
            #       i.e. it assumes it will occur exactly after the last note of the last measure
            # NOTE: Need to carry over last offset from previous measure, and then this will work :-)
            for note in measure:
                # noinspection PyTypeChecker
                event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_ON))
                # noinspection PyTypeChecker
                event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_OFF))

            # TODO DO WE NEED THIS? WORSE DO WE NEED IT ONLY FOR WRITER?
            MidiPlayerEvent.set_tick_deltas(event_list)
            # TODO Support Midi Performance Attrs
            # note_performance_attrs = note.performance_attrs
            # if op == PLAY_ALL:
            #     self._apply_performance_attrs(note, song_performance_attrs, track_performance_attrs,
            #                                   performance_attrs, note_performance_attrs)
            # else:
            #     self._apply_performance_attrs(note, note_performance_attrs)
            for event in event_list:
                # TODO DO WE NEED time= ATTR AT ALL? IF YES SHOULD IT BE tick OR tick_delta?
                yield Message(event.event_type.value, time=event.tick,
                              velocity=ATTR_GET_TYPE_CAST_MAP['velocity'](event.note.amplitude),
                              note=ATTR_GET_TYPE_CAST_MAP['pitch'](event.note.pitch),
                              channel=track.channel)

    def _play(self) -> Sequence[MidiTrack]:
        midi_tracks = []

        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs
            midi_track = MidiTrack()
            midi_track.append(Message('program_change', program=track.instrument, time=0))
            # Even though midi midi_track has an extend() method it does not work the same way. If we call
            # `midi_track.extend(messages)` mido does not honor the directive to append each note after the previous
            # note across calls to extend. For example, if you call extend on the *same* track 4 times, once for each
            # measure in a four-measure sequence, you get one measure's worth of notes in the track (presumably the last
            # one). If you loop over the events can call append() on each one, you get the behavior you expect, with
            # all notes in the midi_track. So, don't change this.
            # noinspection PyTypeChecker
            for message in MidiWriter._get_midi_events_for_track(track=track):
                midi_track.append(message)
            midi_tracks.append(midi_track)

        return midi_tracks

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support improvising')

    def loop(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support looping')
