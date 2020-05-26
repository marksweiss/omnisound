# Copyright 2020 Mark S. Weiss

from typing import Optional

from mido.midifiles.midifiles import Message, MidiFile, MidiTrack
from omnisound.utils.utils import validate_optional_path, validate_optional_type, validate_type

from omnisound.note.adapters.midi_note import ATTR_GET_TYPE_CAST_MAP
from omnisound.note.containers.song import Song
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
        self._play()

    def play_each(self):
        self._play()

    def write_midi_file(self):
        self.midi_file.save(self.midi_file_path)

    def _play(self):
        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs
            midi_track = MidiTrack()
            midi_track.append(Message('program_change', program=track.instrument, time=0))
            self.midi_file.tracks.append (midi_track)

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
                    message = Message(event.event_type.value, time=event.tick_delta,
                                      velocity=ATTR_GET_TYPE_CAST_MAP['velocity'](event.note.amplitude),
                                      note=ATTR_GET_TYPE_CAST_MAP['pitch'](event.note.pitch),
                                      channel=channel)
                    midi_track.append(message)

    def improvise(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support improvising')

    def loop(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not support looping')
