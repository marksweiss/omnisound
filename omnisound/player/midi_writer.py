from typing import Optional

from mido.midifiles.midifiles import MidiFile
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
