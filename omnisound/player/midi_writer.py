# Copyright 2020 Mark S. Weiss

from typing import Optional, Sequence

from mido.midifiles.midifiles import Message, MidiFile, MidiTrack
from omnisound.utils.utils import validate_optional_path, validate_optional_type, validate_type

from omnisound.note.containers.song import Song
from omnisound.player.midi_player import MidiPlayerBase, MidiPlayerAppendMode


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
            for message in MidiPlayerBase._get_midi_events_for_track(track=track):
                midi_track.append(message)
            midi_tracks.append(midi_track)

        return midi_tracks

    def play(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def play_each(self):
        midi_tracks = self._play()
        for midi_track in midi_tracks:
            self.midi_file.tracks.append(midi_track)

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support improvising')

    def loop(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support looping')
