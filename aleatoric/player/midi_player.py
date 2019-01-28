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

import midi

from aleatoric.note.containers.song import Song
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.player import Player
from aleatoric.utils.utils import validate_optional_type, validate_type


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

    def __init__(self, song: Song = None, midi_file_path: str = None):
        # TODO REVSIT WHY SONG CANNOT BE A NOTE SEQUENCE. IT SHOULD BE AND PLAYER DESIGN IS BREAKING BECAUST IT ISN'T
        # MidiPlayer only can play a Song with one or more Tracks. Tracks may be bare NoteSequence collections
        # or Measures with Meter
        validate_type('song', song, Song)
        # TODO Real path validation in utils
        validate_optional_type('midi_file_path', midi_file_path, str)
        super(MidiPlayer, self).__init__()

        self.song = song
        # TODO Support Midi Performance Attrs
        # song_performance_attrs = song.performance_attrs
        self.midi_file_path = midi_file_path
        self.midi_pattern = midi.Pattern()
        self.current_tick = 0

    # TODO ADD TYPE HINTS, esp. for returned function, takes an Any return a Float
    # TODO Don't need this if only supporting Song->Track->Measure
    # @staticmethod
    # def _get_duration_secs_func_for_sequence(note_sequence):
    #     # NOTE: Currently only MidiTrack is supported, which is a list of Measures/Section
    #     # If the note_sequence passed in is a Measure, use its Meter attr to get the duration of each note
    #     # because each note will be a NoteDur with an actual duration in secs depending on the Tempo of the Meter.
    #     # Else assume durations are in seconds value already and use as is. In both cases convert seconds to ticks
    #     # for MIDI, which sets start as an offset in ticks from 0, and implicitly defines the duration of the note
    #     # as the number of ticks from a NoteOn event to the following NoteOff event.
    #     if isinstance(note_sequence, Measure):
    #         return lambda x: int(note_sequence.meter.get_duration_secs_for_note(x) * MidiPlayer.MIDI_TICKS_PER_SECOND)
    #     else:
    #         return lambda x: int(x * MidiPlayer.MIDI_TICKS_PER_SECOND)

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

    def _play(self):  # , op: str):
        for track in self.song:
            # TODO Support Midi Performance Attrs
            # if op == PLAY_ALL
            #     track_performance_attrs = track.performance_attrs

            midi_track = midi.Track()
            self.midi_pattern.append(midi_track)
            channel = track.channel
            midi_track.append(midi.ProgramChangeEvent(tick=0, channel=channel, data=[track.track_instrument]))

            for measure in track.measure_list:
                # TODO Support Midi Performance Attrs
                # if op == PLAY_ALL
                #     measure_performance_attrs = measure.performance_attrs

                for note in measure:
                    # TODO Support Midi Performance Attrs
                    # note_performance_attrs = note.performance_attrs
                    # if op == PLAY_ALL:
                    #     self._apply_performance_attrs(note, song_performance_attrs, track_performance_attrs,
                    #                                   measure_performance_attrs, note_performance_attrs)
                    # else:
                    #     self._apply_performance_attrs(note, note_performance_attrs)

                    # NOTE: midi library maps C4 to 48, most documentation and the midi standard map this to 60
                    # Some systems even map it to 72. We maintian C4 == 60 in MidiNote and pass it here as an
                    # int mapped that way. So our values are 1 octave higher than midi library enums.
                    midi_note_on = midi.NoteOnEvent(tick=self.current_tick, channel=channel,
                                                    velocity=note.velocity, pitch=note.pitch)
                    midi_track.append(midi_note_on)

                    self.current_tick += \
                        int(MidiPlayer.MIDI_TICKS_PER_SECOND *
                            measure.meter.get_duration_secs_for_note(note.dur))

                    midi_note_off = midi.NoteOffEvent(tick=self.current_tick, channel=channel,
                                                      pitch=note.pitch)
                    midi_track.append(midi_note_off)

            midi_track.append(midi.EndOfTrackEvent(tick=1, data=[]))

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')
