# Copyright 2020 Mark S. Weiss

from pathlib import Path
from typing import Any, Optional, Sequence

from mido.midifiles.midifiles import Message, MidiFile, MidiTrack
from omnisound.utils.validation_utils import validate_optional_types, validate_type

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.song import Song
from omnisound.player.midi_player import MidiEventType, MidiPlayerEvent, MidiPlayerAppendMode
from omnisound.player.player import Writer


class MidiWriter(Writer):
    def __init__(self,
                 song: Optional[Song] = None,
                 append_mode: MidiPlayerAppendMode = None,
                 midi_file_path: Path = None):
        validate_type('append_mode', append_mode, MidiPlayerAppendMode)
        validate_optional_types(('song', song, Song), ('midi_file_path', midi_file_path, Path))
        self._song = song
        self.midi_file_path = midi_file_path
        # Type 1 - multiple synchronous tracks, all starting at the same time
        # https://mido.readthedocs.io/en/latest/midi_files.html
        self.midi_file = MidiFile(type=1)
        super(MidiWriter, self).__init__(song=song)

    # BasePlayer Properties
    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        validate_type('song', song, Song)
        self._song = song
    # /BasePlayer Properties

    # Writer API
    def write(self):
        self.midi_file.save(str(self.midi_file_path))

    def generate(self) -> Sequence[Any]:
        assert self._song
        event_list = []
        for track in self._song:
            midi_track = MidiTrack()
            midi_track.append(Message('program_change', program=track.instrument, time=0))
            self.midi_file.tracks.append(midi_track)

            # mido channels numbered 0..15 instead of MIDI standard 1..16
            channel = track.channel - 1
            for measure in track.measure_list:
                for note in measure:
                    # noinspection PyTypeChecker
                    event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_ON))
                    # noinspection PyTypeChecker
                    event_list.append(MidiPlayerEvent(note, measure, MidiEventType.NOTE_OFF))

                MidiPlayerEvent.set_tick_deltas(event_list)
                for event in event_list:
                    message = Message(event.event_type.value, time=event.tick_delta,
                                      velocity=ATTR_GET_TYPE_CAST_MAP['velocity'](event.note.amplitude),
                                      note=ATTR_GET_TYPE_CAST_MAP['pitch'](event.note.pitch),
                                      channel=channel)
                    midi_track.append(message)
        return event_list

    def generate_and_write(self) -> None:
        self.generate()
        self.write()
    # /Writer API
