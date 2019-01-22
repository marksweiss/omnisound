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

from typing import Union

import midi

from aleatoric.note.adapters.note import Note
from aleatoric.note.containers.measure import Measure
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.containers.song import Song
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.player import Player, PlayerNoNotesException
from aleatoric.utils.utils import validate_type_choice, validate_optional_type, validate_type


class MidiPlayer(Player):
    MIDI_TICKS_PER_QUARTER_NOTE = 960
    MIDI_QUARTER_NOTES_PER_BEAT = 4
    MIDI_BEATS_PER_MINUTE = 120
    MIDI_TICKS_PER_SECOND = int((MIDI_TICKS_PER_QUARTER_NOTE *
                                 MIDI_QUARTER_NOTES_PER_BEAT *
                                 MIDI_BEATS_PER_MINUTE)
                                / 60)

    DEFAULT_BEAT_DURATION = NoteDur.QUARTER

    def __init__(self, song: Song = None, midi_file_path: str = None):
        # TODO REVSIT WHY SONG CANNOT BE A NOTE SEQUENCE. IT SHOULD BE AND PLAYER DESIGN IS BREAKING BECAUST IT ISN'T
        # MidiPlayer only can play a Song with one or more Tracks. Tracks may be bare NoteSequence collections
        # or Measures with Meter
        validate_type('song', song, Song)
        # TODO Real path validation in utils
        validate_optional_type('midi_file_path', midi_file_path, str)
        super(MidiPlayer, self).__init__()
        self.song = song
        self.midi_file_path = midi_file_path
        self.midi_pattern = midi.Pattern()
        self.current_tick = 0

    # TODO ADD TYPE HINTS, esp. for returned function, takes an Any return a Float
    @staticmethod
    def _get_duration_secs_func_for_sequence(note_sequence):
        # NOTE: Currently only MidiTrack is supported, which is a list of Measures/Section
        # If the note_sequence passed in is a Measure, use its Meter attr to get the duration of each note
        # because each note will be a NoteDur with an actual duration in secs depending on the Tempo of the Meter.
        # Else assume durations are in seconds value already and use as is. In both cases convert seconds to ticks
        # for MIDI, which sets start as an offset in ticks from 0, and implicitly defines the duration of the note
        # as the number of ticks from a NoteOn event to the following NoteOff event.
        if isinstance(note_sequence, Measure):
            return lambda x: int(note_sequence.meter.get_duration_secs_for_note(x) * MidiPlayer.MIDI_TICKS_PER_SECOND)
        else:
            return lambda x: int(x * MidiPlayer.MIDI_TICKS_PER_SECOND)

    def write_midi_file(self):
        midi.write_midifile(self.midi_file_path, self.midi_pattern)

    def play_each(self):
        for track in self.song:
            for measure_list in track:
                for measure in measure_list:
                    midi_track = midi.Track()
                    self.midi_pattern.append(midi_track)
                    for note in measure:
                        # TODO USE THIS?
                        # performance_attrs = note.pa.as_dict()
                        # TODO NEED PITCH CONVERSION TO ENUMS USED BY THIS LIBRARY. OWNED BY THIS PLAYER
                        pitch = self.get_midi_pitch(note.pitch)
                        midi_note_on = midi.NoteOnEvent(tick=self.current_tick, velocity=note.velocity, pitch=pitch)
                        midi_track.append(midi_note_on)
                        self.current_tick += measure.meter.get_duration_secs_for_note(note.dur)
                        midi_note_off = midi.NoteOffEvent(tick=self.current_tick, pitch=pitch)
                        midi_track.append(midi_note_off)
                    midi_track.append(midi.EndOfTrackEvent(tick=self.current_tick))
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def play_all(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        # for note in self.notes:
        #     performance_attrs = note.pa.as_dict()
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')
