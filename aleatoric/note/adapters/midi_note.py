# Copyright 2018 Mark S. Weiss

from enum import Enum
from typing import Union

from aleatoric.note.adapters.note import Note
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                     MajorKey, MinorKey)
from aleatoric.utils.utils import (validate_optional_types,
                                   validate_optional_type_choice,
                                   validate_type, validate_type_choice,
                                   validate_types)

FIELDS = ('instrument', 'time', 'duration', 'velocity', 'pitch', 'name', 'channel')


class MidiInstrument(Enum):
    Acoustic_Grand_Piano = 0
    Bright_Acoustic_Piano = 1
    Electric_Grand_Piano = 2
    Honky_tonk_Piano = 3
    Electric_Piano_1 = 4
    Electric_Piano_2 = 5
    Harpsichord = 6
    Clavi = 7
    Celesta = 8
    Glockenspiel = 9
    Music_Box = 10
    Vibraphone = 11
    Marimba = 12
    Xylophone = 13
    Tubular_Bells = 14
    Dulcimer = 15
    Drawbar_Organ = 16
    Percussive_Organ = 17
    Rock_Organ = 18
    Church_Organ = 19
    Reed_Organ = 20
    Accordion = 21
    Harmonica = 22
    Tango_Accordion = 23
    Acoustic_Guitar_nylon = 24
    Acoustic_Guitar_steel = 25
    Electric_Guitar_jazz = 26
    Electric_Guitar_clean = 27
    Electric_Guitar_muted = 28
    Overdriven_Guitar = 29
    Distortion_Guitar = 30
    Guitar_harmonics = 31
    Acoustic_Bass = 32
    Electric_Bass_finger = 33
    Electric_Bass_pick = 34
    Fretless_Bass = 35
    Slap_Bass_1 = 36
    Slap_Bass_2 = 37
    Synth_Bass_1 = 38
    Synth_Bass_2 = 39
    Violin = 40
    Viola = 41
    Cello = 42
    Contrabass = 43
    Tremolo_Strings = 44
    Pizzicato_Strings = 45
    Orchestral_Harp = 46
    Timpani = 47
    String_Ensemble_1 = 48
    String_Ensemble_2 = 49
    SynthStrings_1 = 50
    SynthStrings_2 = 51
    Choir_Aahs = 52
    Voice_Oohs = 53
    Synth_Voice = 54
    Orchestra_Hit = 55
    Trumpet = 56
    Trombone = 57
    Tuba = 58
    Muted_Trumpet = 59
    French_Horn = 60
    Brass_Section = 61
    SynthBrass_1 = 62
    SynthBrass_2 = 63
    Soprano_Sax = 64
    Alto_Sax = 65
    Tenor_Sax = 66
    Baritone_Sax = 67
    Oboe = 68
    English_Horn = 69
    Bassoon = 70
    Clarinet = 71
    Piccolo = 72
    Flute = 73
    Recorder = 74
    Pan_Flute = 75
    Blown_Bottle = 76
    Shakuhachi = 77
    Whistle = 78
    Ocarina = 79
    Lead_1_square = 80
    Lead_2_sawtooth = 81
    Lead_3_calliope = 82
    Lead_4_chiff = 83
    Lead_5_charang = 84
    Lead_6_voice = 85
    Lead_7_fifths = 86
    Lead_8_bass_plus_lead = 87
    Pad_1_new_age = 88
    Pad_2_warm = 89
    Pad_3_polysynth = 90
    Pad_4_choir = 91
    Pad_5_bowed = 92
    Pad_6_metallic = 93
    Pad_7_halo = 94
    Pad_8_sweep = 95
    FX_1_rain = 96
    FX_2_soundtrack = 97
    FX_3_crystal = 98
    FX_4_atmosphere = 99
    FX_5_brightness = 100
    FX_6_goblins = 101
    FX_7_echoes = 102
    FX_8_sci_fi = 103
    Sitar = 104
    Banjo = 105
    Shamisen = 106
    Koto = 107
    Kalimba = 108
    Bag_pipe = 109
    Fiddle = 110
    Shanai = 111
    Tinkle_Bell = 112
    Agogo = 113
    Steel_Drums = 114
    Woodblock = 115
    Taiko_Drum = 116
    Melodic_Tom = 117
    Synth_Drum = 118
    Reverse_Cymbal = 119
    Guitar_Fret_Noise = 120
    Breath_Noise = 121
    Seashore = 122
    Bird_Tweet = 123
    Telephone_Ring = 124
    Helicopter = 125
    Applause = 126
    Gunshot = 127
    # Program Change Channel 10 Drum Program Change Values
    Acoustic_Bass_Drum = 35
    Bass_Drum_1 = 36
    Side_Stick = 37
    Acoustic_Snare = 38
    Hand_Clap = 39
    Electric_Snare = 40
    Low_Floor_Tom = 41
    Closed_Hi_Hat = 42
    High_Floor_Tom = 43
    Pedal_Hi_Hat = 44
    Low_Tom = 45
    Open_Hi_Hat = 46
    Low_Mid_Tom = 47
    Hi_Mid_Tom = 48
    Crash_Cymbal_1 = 49
    High_Tom = 50
    Ride_Cymbal_1 = 51
    Chinese_Cymbal = 52
    Ride_Bell = 53
    Tambourine = 54
    Splash_Cymbal = 55
    Cowbell = 56
    Crash_Cymbal_2 = 57
    Vibraslap = 58
    Ride_Cymbal_2 = 59
    Hi_Bongo = 60
    Low_Bongo = 61
    Mute_Hi_Conga = 62
    Open_Hi_Conga = 63
    Low_Conga = 64
    High_Timbale = 65
    Low_Timbale = 66
    High_Agogo = 67
    Low_Agogo = 68
    Cabasa = 69
    Maracas = 70
    Short_Whistle = 71
    Long_Whistle = 72
    Short_Guiro = 73
    Long_Guiro = 74
    Claves = 75
    Hi_Wood_Block = 76
    Low_Wood_Block = 77
    Mute_Cuica = 78
    Open_Cuica = 79
    Mute_Triangle = 80
    Open_Triangle = 81


class MidiNote(Note):
    """Models a note with attributes aliased to and specific to MIDI
       and with a str() that prints MIDI formatted output.
    """

    PITCH_MAP = {
        MajorKey.C: 24,
        MajorKey.C_s: 25,
        MajorKey.D_f: 25,
        MajorKey.D: 26,
        MajorKey.D_s: 27,
        MajorKey.E_f: 27,
        MajorKey.E: 28,
        MajorKey.F: 29,
        MajorKey.F_s: 30,
        MajorKey.G_f: 30,
        MajorKey.G: 31,
        MajorKey.G_s: 32,
        MajorKey.A_f: 32,
        MajorKey.A: 33,
        MajorKey.A_s: 34,
        MajorKey.B_f: 34,
        MajorKey.B: 35,
        MajorKey.C_f: 35,

        MinorKey.C: 24,
        MinorKey.C_S: 25,
        MinorKey.D: 26,
        MinorKey.D_S: 27,
        MinorKey.E_F: 27,
        MinorKey.E: 28,
        MinorKey.E_S: 29,
        MinorKey.F: 29,
        MinorKey.F_S: 30,
        MinorKey.G: 31,
        MinorKey.A_F: 32,
        MinorKey.A: 33,
        MinorKey.A_S: 34,
        MinorKey.B_F: 34,
        MinorKey.B: 35
    }

    MIN_OCTAVE = 0
    MAX_OCTAVE = 7
    KEYS_IN_MIN_OCTAVE = frozenset([MajorKey.A, MajorKey.B_f, MajorKey.B,
                                    MinorKey.A, MinorKey.B_F, MinorKey.B])
    MIN_PITCH = 21
    MAX_PITCH = 108
    DEFAULT_CHANNEL = 1

    def __init__(self, instrument: Union[int, MidiInstrument] = None,
                 time: float = None, duration: float = None, velocity: int = None, pitch: int = None,
                 name: str = None,
                 channel: int = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('start', time, float), ('duration', duration, float), ('velocity', velocity, int),
                       ('pitch', pitch, int))
        validate_optional_types(('channel', channel, int), ('name', name, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        validate_optional_type_choice('instrument', instrument, (int, MidiInstrument))
        super(MidiNote, self).__init__(name=name)
        self._instrument = instrument
        if instrument in MidiInstrument:
            self._instrument = instrument.value
        self._time = time
        self._duration = duration
        self._velocity = velocity
        self._pitch = pitch
        self._performance_attrs = performance_attrs
        self._channel = channel or MidiNote.DEFAULT_CHANNEL

    # Custom Interface
    def program_change(self, instrument: int):
        validate_type('instrument', instrument, int)
        self._instrument = instrument

    @property
    def channel(self) -> int:
        return self._channel

    @channel.setter
    def channel(self, channel: int):
        validate_type('channel', channel, int)
        self._channel = channel

    # Base Note Interface
    @property
    def instrument(self) -> int:
        return self._instrument

    @instrument.setter
    def instrument(self, instrument: int):
        validate_type('instrument', instrument, int)
        self._instrument = instrument

    def i(self, instrument: int = None) -> Union['MidiNote', int]:
        if instrument is not None:
            validate_type('instrument', instrument, int)
            self._instrument = instrument
            return self
        else:
            return self._instrument

    @property
    def start(self) -> float:
        return self._time

    @start.setter
    def start(self, start: float):
        validate_type('start', start, float)
        self._time = start

    def s(self, start: float = None) -> Union['MidiNote', float]:
        if start is not None:
            validate_type('start', start, float)
            self._time = start
            return self
        else:
            return self._time

    @property
    def time(self) -> float:
        return self._time

    @time.setter
    def time(self, time: float):
        validate_type('time', time, float)
        self._time = time

    @property
    def dur(self) -> float:
        return self._duration

    @dur.setter
    def dur(self, dur: float):
        validate_type('dur', dur, float)
        self._duration = dur

    def d(self, dur: float = None) -> Union['MidiNote', float]:
        if dur is not None:
            validate_type('dur', dur, float)
            self._duration = dur
            return self
        else:
            return self._duration

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        validate_type('duration', duration, float)
        self._duration = duration

    @property
    def amp(self) -> int:
        return self._velocity

    @amp.setter
    def amp(self, amp: int):
        validate_type('amp', amp, int)
        self._velocity = amp

    def a(self, amp: int = None) -> Union['MidiNote', int]:
        if amp is not None:
            validate_type('amp', amp, int)
            self._velocity = amp
            return self
        else:
            return self._velocity

    @property
    def velocity(self) -> int:
        return self._velocity

    @velocity.setter
    def velocity(self, velocity: int):
        validate_type('velocity', velocity, int)
        self._velocity = velocity

    @property
    def pitch(self) -> int:
        return self._pitch

    @pitch.setter
    def pitch(self, pitch: int):
        validate_type('pitch', pitch, int)
        self._pitch = pitch

    def transpose(self, interval: int):
        """Midi pitches are ints in the range MIN
        """
        validate_type('interval', interval, int)
        new_pitch = self.pitch + interval
        if new_pitch < MidiNote.MIN_PITCH or new_pitch > MidiNote.MAX_PITCH:
            raise ValueError(f'Arg `interval` creates invalid pitch value: {new_pitch}')
        self._pitch = new_pitch

    def p(self, pitch: int = None) -> Union['MidiNote', int]:
        if pitch is not None:
            validate_type('pitch', pitch, int)
            self._pitch = pitch
            return self
        else:
            return self._pitch

    @property
    def performance_attrs(self) -> PerformanceAttrs:
        return self._performance_attrs

    @performance_attrs.setter
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        validate_type('performance_attrs', performance_attrs, int)
        self._performance_attrs = performance_attrs

    @property
    def pa(self) -> PerformanceAttrs:
        return self._performance_attrs

    @pa.setter
    def pa(self, performance_attrs: PerformanceAttrs):
        validate_type('performance_attrs', performance_attrs, int)
        self._performance_attrs = performance_attrs

    @classmethod
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> int:
        """MIDI pitches sequence from 21 A0 to 127, the 3 highest notes below C1 to the last note of C7.
           The algorithm is that we store the values for C1-12 as ints in the PITCH_MAP
           and thus increment by + 12 for every octave > 1, handle the special case for the 3 notes < C1 and
           validate that the (key, octave) combination is a valid MIDI pitch.
        """
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if not (cls.MIN_OCTAVE < octave < cls.MAX_OCTAVE):
            raise ValueError(f'Arg `octave` must be in range {cls.MIN_OCTAVE} <= octave <= {cls.MAX_OCTAVE}')

        if octave == cls.MIN_OCTAVE:
            # Handle edge case of only 3 notes being valid when `octave` == 0
            if key not in cls.KEYS_IN_MIN_OCTAVE:
                raise ValueError(('If arg `octave` == 0 then `key` must be in '
                                  f'{cls.KEYS_IN_MIN_OCTAVE}'))
            return cls.PITCH_MAP[key] - NUM_INTERVALS_IN_OCTAVE
        else:
            interval_offset = (octave - 1) * NUM_INTERVALS_IN_OCTAVE
            return cls.PITCH_MAP[key] + interval_offset

    @staticmethod
    def copy(source_note: 'MidiNote') -> 'MidiNote':
        return MidiNote(instrument=source_note._instrument,
                        time=source_note._time, duration=source_note._duration,
                        velocity=source_note._velocity, pitch=source_note._pitch,
                        name=source_note._name,
                        channel=source_note._channel,
                        performance_attrs=source_note._performance_attrs)

    def __eq__(self, other: 'MidiNote') -> bool:
        """NOTE: Equality ignores Note.name and Note.peformance_attrs. Two CSountNotes are considered equal
           if they have the same note attributes.
        """
        return self._instrument == other._instrument and self._time == other._time and \
            self._duration == other.duration and self._velocity == other._velocity and \
            self._pitch == other._pitch and self._channel == other._channel

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} time: {self.time} '
                f'duration: {self.duration} velocity: {self.velocity} pitch: {self.pitch} channel: {self.channel}')
