# Copyright 2018 Mark S. Weiss

from enum import Enum
from typing import Any, Union

from aleatoric.note import (Note, PerformanceAttrs)
from aleatoric.scale_globals import (MajorKey, MinorKey, STEPS_IN_OCTAVE)
from aleatoric.utils import (validate_optional_types, validate_type_choice, validate_type, validate_types)


class MidiNote(Note):
    """Models a note with attributes aliased to and specific to MIDI
       and with a str() that prints MIDI formatted output.
    """

    DEFAULT_CHANNEL = 1

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

    PITCH_MAP = {
        MajorKey.C: 24,
        MajorKey.C_s: 25,
        MajorKey.D_f: 25,
        MajorKey.D: 26,
        MajorKey.E_f: 27,
        MajorKey.E: 28,
        MajorKey.F: 29,
        MajorKey.F_s: 30,
        MajorKey.G_f: 30,
        MajorKey.G: 31,
        MajorKey.A_f: 32,
        MajorKey.A: 33,
        MajorKey.B_f: 34,
        MajorKey.B: 35,
        MajorKey.C_f: 35,

        MinorKey.c: 24,
        MinorKey.c_s: 25,
        MinorKey.d: 26,
        MinorKey.d_s: 27,
        MinorKey.e_f: 27,
        MinorKey.e: 28,
        MinorKey.e_s: 29,
        MinorKey.f: 29,
        MinorKey.f_s: 30,
        MinorKey.g: 31,
        MinorKey.a_f: 32,
        MinorKey.a: 33,
        MinorKey.a_s: 34,
        MinorKey.b_f: 34,
        MinorKey.b: 35
    }

    MIN_OCTAVE = 0
    MAX_OCTAVE = 7
    KEYS_IN_OCTAVE_MIN_MIDI_OCTAVE = frozenset([MajorKey.A, MajorKey.B_f, MajorKey.B,
                                                MinorKey.a, MinorKey.b_f, MinorKey.b])

    def __init__(self, instrument: Any = None,
                 time: float = None, duration: float = None, velocity: int = None, pitch: int = None,
                 name: str = None,
                 channel: int = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('start', time, float), ('duration', duration, float), ('velocity', velocity, int),
                       ('pitch', pitch, int))
        validate_optional_types(('channel', channel, int), ('name', name, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(MidiNote, self).__init__(instrument=instrument,
                                       start=time, dur=duration, amp=velocity, pitch=pitch,
                                       name=name,
                                       performance_attrs=performance_attrs,
                                       validate=False)
        self.channel = channel or MidiNote.DEFAULT_CHANNEL

        # TEMP DEBUG
        import pdb; pdb.set_trace()

    class NoteConfig(object):
        def __init__(self):
            self.instrument = None
            self.time = None
            self.duration = None
            self.velocity = None
            self.pitch = None
            self.name = None
            self.channel = None

        def as_dict(self):
            return {
                'instrument': self.instrument,
                'time': self.time,
                'duration': self.duration,
                'velocity': self.velocity,
                'pitch': self.pitch,
                'name': self.name,
                'channel': self.channel
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return MidiNote.NoteConfig()

    @property
    def time(self) -> float:
        return self.start

    @time.setter
    def time(self, time: float):
        # noinspection PyAttributeOutsideInit
        self.start = time

    @property
    def duration(self) -> float:
        return self.dur

    @duration.setter
    def duration(self, duration: float):
        # noinspection PyAttributeOutsideInit
        self.dur = duration

    @property
    def velocity(self) -> int:
        return int(self.amp)

    @velocity.setter
    def velocity(self, velocity: int):
        self.amp = velocity

    @property
    def pitch(self) -> int:
        return int(self.pitch)

    @pitch.setter
    def pitch(self, pitch: int):
        # https://stackoverflow.com/questions/1021464/how-to-call-a-property-of-the-base-class-if-this-property-is-being-overwritten-i/1021484
        # Need to access the parent setter as a property attached to parent class. Normal property syntax
        # means calling self.pitch, which results in infinite recursion

        # TEMP DEBUG
        import pdb; pdb.set_trace()
        super(MidiNote, self).pitch.fset(self, pitch)

    def program_change(self, instrument: int):
        validate_type('instrument', instrument, int)
        # noinspection PyAttributeOutsideInit
        self.instrument = instrument

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int) -> int:
        """MIDI pitches sequence from 21 A0 to 127, the 3 highest notes below C1 to the last note of C7.
           The algorithm is that we store the values for C1-12 as ints in the PITCH_MAP
           and thus increment by + 12 for every octave > 1, handle the special case for the 3 notes < C1 and
           validate that the (key, octave) combination is a valid MIDI pitch.
        """
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if MidiNote.MIN_OCTAVE < octave < MidiNote.MAX_OCTAVE:
            raise ValueError(f'Arg `octave` must be in range {MidiNote.MIN_OCTAVE} <= octave <= {MidiNote.MAX_OCTAVE}')

        if octave == MidiNote.MIN_OCTAVE:
            # Handle edge case of only 3 notes being valid when `octave` == 0
            if key not in MidiNote.KEYS_IN_OCTAVE_MIN_MIDI_OCTAVE:
                raise ValueError(('If arg `octave` == 0 then `key` must be in '
                                  f'{MidiNote.KEYS_IN_OCTAVE_MIN_MIDI_OCTAVE}'))
            return self.PITCH_MAP[key].value - STEPS_IN_OCTAVE
        else:
            return self.PITCH_MAP[key].value + ((octave - 1) * STEPS_IN_OCTAVE)

    @staticmethod
    def copy(source_note) -> 'MidiNote':
        return MidiNote(instrument=source_note.instrument,
                        time=source_note.time, duration=source_note.duration,
                        velocity=source_note.velocity, pitch=source_note.pitch,
                        name=source_note.name,
                        channel=source_note.channel,
                        performance_attrs=source_note.performance_attrs)

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} time: {self.time} '
                f'duration: {self.duration} velocity: {self.velocity} pitch: {self.pitch} channel: {self.channel}')