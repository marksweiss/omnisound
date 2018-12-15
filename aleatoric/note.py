# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from aleatoric.utils import (validate_sequence_of_types, validate_optional_type, validate_optional_types,
                             validate_not_none, validate_type, validate_type_choice, validate_types)
from aleatoric.scale import (MajorKey, MinorKey, STEPS_IN_OCTAVE)


class PerformanceAttrsFrozenException(Exception):
    pass


class PerformanceAttrs(object):
    """Open container for dynamically adding performance attributes to a Note. These attributes
       govern the behavior of the Instrument playing the Note, and not attributes of the Note itself.
       So for example they might parameterize `vibrato` or `tremolo` in a SupercolliderNote.

       Different instruments on different platforms expose different parameters, so this class has no
       fixed attributes. So instead it is just an API for adding attributes in a type-safe way.
       The API lets the caller add an attribute by name and type, and dynamically adds the attribute
       and a validator for it.

       Usage:
       - call add_attr(name, type) for each attribute you want to add
       - call freeze() when you want to make the object read-only
    """
    DEFAULT_NAME = 'PERF_ATTRS'

    def __init__(self, name: str = None):
        self.attr_type_map: Dict[str, Any] = {}
        self.name: str = name or PerformanceAttrs.DEFAULT_NAME
        self.frozen: bool = False

    def add_attr(self, attr_name: str = None, val: Any = None, attr_type: Any = None):
        validate_type('attr_name', attr_name, str)
        validate_not_none('attr_type', attr_type)
        if self.frozen:
            raise PerformanceAttrsFrozenException((f'Attempt to set attribute: {attr_name} '
                                                   f'on frozen PerformanceConfigFactory: {self.name}'))
        self.attr_type_map[attr_name] = attr_type
        setattr(self, attr_name, val)

    def safe_set_attr(self, attr_name, val):
        if attr_name not in self.attr_type_map:
            raise ValueError('Invalid attribute name')
        # noinspection PyTypeHints
        if not isinstance(val, self.attr_type_map[attr_name]):
            raise ValueError(f'val: {val} must be of type: {self.attr_type_map[attr_name]}')
        setattr(self, attr_name, val)

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def is_frozen(self) -> bool:
        return self.frozen

    def __str__(self):
        return ' '.join([f'{attr_name}: {getattr(self, attr_name)}' for attr_name in self.attr_type_map.keys()])

    def as_dict(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.attr_type_map.keys()}


class Note(ABC):
    """Models the core attributes of a musical note common to multiple back ends"""

    name: Optional[str]
    DEFAULT_INSTRUMENT = '1'
    DEFAULT_START = 0.0
    DEFAULT_DUR = 0.0
    DEFAULT_AMP = 0.0
    DEFAULT_PITCH = 0.0
    DEFAULT_NAME = 'Note'

    def __init__(self, instrument: Any = None,
                 start: float = None, dur: float = None, amp: float = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None,
                 validate=True):
        if validate:
            validate_optional_types(('start', start, float), ('dur', dur, float), ('amp', amp, float),
                                    ('pitch', pitch, float), ('name', name, str),
                                    ('performance_attrs', performance_attrs, PerformanceAttrs))

        self.instrument = instrument or Note.DEFAULT_INSTRUMENT
        self.start = start or Note.DEFAULT_START
        self.dur = dur or Note.DEFAULT_DUR
        self.amp = amp or Note.DEFAULT_AMP
        self.pitch = pitch or Note.DEFAULT_PITCH
        self.name = name or Note.DEFAULT_NAME
        self.performance_attrs = performance_attrs or PerformanceAttrs()

    class NoteConfig(object):
        def __init__(self):
            self.instrument = None
            self.start = None
            self.dur = None
            self.amp = None
            self.pitch = None
            self.name = None

        def as_dict(self):
            return {
                'instrument': self.instrument,
                'start': self.start,
                'dur': self.dur,
                'amp': self.amp,
                'pitch': self.pitch,
                'name': self.name
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return Note.NoteConfig()

    @staticmethod
    def copy(source_note):
        validate_types(('start', source_note.start, float), ('dur', source_note.dur, float),
                       ('amp', source_note.amp, float), ('pitch', source_note.pitch, float))
        validate_optional_types(('name', source_note.name, str),
                                ('performance_attrs', source_note.performance_attrs, PerformanceAttrs))

        return Note(instrument=source_note.instrument,
                    start=source_note.start, dur=source_note.dur, amp=source_note.amp, pitch=source_note.pitch,
                    name=source_note.name,
                    performance_attrs=source_note.performance_attrs)

    def __eq__(self, other):
        """NOTE: equality of Notes is defined for note attributes only, not for performance attributes."""
        validate_types(('start', other.start, float), ('dur', other.dur, float),
                       ('amp', other.amp, float), ('pitch', other.pitch, float))
        return self.instrument == other.instrument and \
            self.start == other.start and \
            self.dur == other.dur and \
            self.amp == other.amp and \
            self.pitch == other.pitch

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} delay: {self.start:.5f} '
                f'dur: {self.dur:.5f} amp: {self.amp} pitch: {self.pitch:.5f}')

    @property
    def pa(self):
        """Get the underlying performance_attrs.
           Alias to something shorter for client code convenience.
        """
        return self.performance_attrs

    @abstractmethod
    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
        raise NotImplemented('Note subtypes must implement get_pitch() and return valid pitch values for their type')


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0
    """

    REST_AMP = 0.0

    def __init__(self, instrument: Any = None,
                 start: float = None, dur: float = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        super(RestNote, self).__init__(instrument=instrument,
                                       start=start, dur=dur, amp=RestNote.REST_AMP, pitch=pitch,
                                       name=name,
                                       performance_attrs=performance_attrs)

    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
        raise NotImplemented('RestNote cannot meaningfully implement get_pitch()')


class FoxDotSupercolliderNote(Note):

    SCALES = {'aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian', 'dorian2',
              'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian', 'justMajor', 'justMinor',
              'locrian', 'locrianMajor', 'lydian', 'lydianMinor', 'major', 'majorPentatonic', 'melodicMajor',
              'melodicMinor', 'minor', 'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus',
              'romanianMinor', 'yu', 'zhi'}

    # noinspection PyShadowingBuiltins
    def __init__(self, synth_def: Any = None,
                 delay: int = None, dur: float = None, amp: float = None, degree: float = None,
                 name: str = None,
                 oct: int = None, scale: str = None,
                 performance_attrs: PerformanceAttrs = None):
        # start not meaningful for Supercollider
        # Note: cast float(degree). Ints will work with FoxDot for degree so handle this.
        # TODO Change validation for types that support either int or float to be validate_types('x', x, (int, float))
        validate_types(('delay', delay, int), ('dur', dur, float), ('amp', amp, float),
                       ('degree', float(degree), float))
        validate_optional_types(('name', name, str), ('performance_attrs', performance_attrs, PerformanceAttrs),
                                ('oct', oct, int), ('scale', scale, str))
        if scale and scale not in FoxDotSupercolliderNote.SCALES:
            raise ValueError(f'arg `scale` must be None or a string in FoxDotSuperColliderNote.SCALES, scale: {scale}')
        super(FoxDotSupercolliderNote, self).__init__(instrument=synth_def,
                                                      start=delay, dur=dur, amp=amp, pitch=degree,
                                                      name=name,
                                                      performance_attrs=performance_attrs,
                                                      validate=False)
        if oct:
            self.oct = oct
        if scale:
            self.scale = scale

    class NoteConfig(object):
        def __init__(self):
            self.synth_def = None
            self.delay = None
            self.dur = None
            self.amp = None
            self.degree = None
            self.oct = None
            self.scale = None
            self.name = None

        def as_dict(self):
            return {
                'synth_def': self.synth_def,
                'delay': self.delay,
                'dur': self.dur,
                'amp': self.amp,
                'degree': self.degree,
                'scale': self.scale,
                'oct': self.oct,
                'name': self.name
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return FoxDotSupercolliderNote.NoteConfig()

    @property
    def synth_def(self):
        return self.instrument

    @synth_def.setter
    def synth_def(self, synth_def: Any):
        # noinspection PyAttributeOutsideInit
        self.instrument = synth_def

    @property
    def delay(self):
        return self.start

    @delay.setter
    def delay(self, delay: int):
        # noinspection PyAttributeOutsideInit
        self.start = delay

    @property
    def degree(self):
        return self.pitch

    @degree.setter
    def degree(self, degree: float):
        # noinspection PyAttributeOutsideInit
        self.pitch = degree

    @staticmethod
    def copy(source_note):
        return FoxDotSupercolliderNote(synth_def=source_note.synth_def,
                                       delay=source_note.delay, dur=source_note.dur,
                                       amp=source_note.amp, degree=source_note.degree,
                                       name=source_note.name,
                                       oct=source_note.oct, scale=source_note.scale,
                                       performance_attrs=source_note.performance_attrs)

    def __eq__(self, other):
        if not super(FoxDotSupercolliderNote).__eq__(other):
            return False
        return ((self.oct is None and other.oct is None or self.oct == other.oct) and
                (self.scale is None and other.scale is None or self.scale == other.scale))

    def __str__(self):
        s = (f'name: {self.name} delay: {self.delay} '
             f'dur: {self.dur} amp: {self.amp} degree: {self.degree}')
        if hasattr(self, 'oct'):
            s += f' oct: {self.oct}'
        if hasattr(self, 'scale'):
            s += f' scale: {self.scale}'
        return s


class CSoundNote(Note):
    """Models a note with attributes aliased to and specific to CSound
       and with a str() that prints CSound formatted output.
    """

    PITCH_MAP = {
        MajorKey.C: 1.01,
        MajorKey.C_s: 1.02,
        MajorKey.D_f: 1.02,
        MajorKey.D: 1.03,
        MajorKey.E_f: 1.04,
        MajorKey.E: 1.05,
        MajorKey.F: 1.06,
        MajorKey.F_s: 1.07,
        MajorKey.G_f: 1.07,
        MajorKey.G: 1.08,
        MajorKey.A_f: 1.09,
        MajorKey.A: 1.10,
        MajorKey.B_f: 1.10,
        MajorKey.B: 1.11,
        MajorKey.C_f: 1.11,

        MinorKey.c: 1.01,
        MinorKey.c_s: 1.02,
        MinorKey.d_f: 1.02,
        MinorKey.d: 1.03,
        MinorKey.e_f: 1.04,
        MinorKey.e: 1.05,
        MinorKey.f: 1.06,
        MinorKey.f_s: 1.07,
        MinorKey.g_f: 1.07,
        MinorKey.g: 1.08,
        MinorKey.a_f: 1.09,
        MinorKey.a: 1.10,
        MinorKey.b_f: 1.10,
        MinorKey.b: 1.11,
        MinorKey.c_f: 1.11,
    }

    MIN_OCTAVE = 1.0
    MAX_OCTAVE = 12.0

    def __init__(self, instrument: Any = None,
                 start: float = None, duration: float = None, amplitude: int = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('start', start, float), ('duration', duration, float), ('amplitude', amplitude, int),
                       ('pitch', pitch, float))
        validate_optional_types(('name', name, str), ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(CSoundNote, self).__init__(instrument=instrument,
                                         start=start, dur=duration, amp=amplitude, pitch=pitch,
                                         name=name,
                                         performance_attrs=performance_attrs,
                                         validate=False)

    class NoteConfig(object):
        def __init__(self):
            self.instrument = None
            self.start = None
            self.duration = None
            self.amplitude = None
            self.pitch = None
            self.name = None

        def as_dict(self):
            return {
                'instrument': self.instrument,
                'start': self.start,
                'duration': self.duration,
                'amplitude': self.amplitude,
                'pitch': self.pitch,
                'name': self.name
            }

    @staticmethod
    def get_config() -> NoteConfig:
        return CSoundNote.NoteConfig()

    @property
    def duration(self):
        return self.dur

    @duration.setter
    def duration(self, duration: float):
        # noinspection PyAttributeOutsideInit
        self.dur = duration

    @property
    def amplitude(self):
        return self.amp

    @amplitude.setter
    def amplitude(self, amplitude: int):
        # noinspection PyAttributeOutsideInit
        self.amp = amplitude

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
        validate_type_choice('key', key, (MajorKey, MinorKey))
        validate_type('octave', octave, int)
        if CSoundNote.MIN_OCTAVE < octave < CSoundNote.MAX_OCTAVE:
            raise ValueError((f'Arg `octave` must be in range '
                             f'{CSoundNote.MIN_OCTAVE} <= octave <= {CSoundNote.MAX_OCTAVE}'))
        return CSoundNote.PITCH_MAP[key] + (float(octave) - 1.0)

    @staticmethod
    def copy(source_note):
        return CSoundNote(instrument=source_note.instrument,
                          start=source_note.start, duration=source_note.dur,
                          amplitude=source_note.amp, pitch=source_note.pitch,
                          name=source_note.name,
                          performance_attrs=source_note.performance_attrs)

    def __str__(self):
        # TODO HANDLE FLOAT ROUNDING ON PITCH BY CHANGING PRECISION TO .2, FIX TESTS
        return f'i {self.instrument} {self.start:.5f} {self.dur:.5f} {self.amp} {self.pitch:.5f}'


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
        MinorKey.d_f: 25,
        MinorKey.d: 26,
        MinorKey.e_f: 27,
        MinorKey.e: 28,
        MinorKey.f: 29,
        MinorKey.f_s: 30,
        MinorKey.g_f: 30,
        MinorKey.g: 31,
        MinorKey.a_f: 32,
        MinorKey.a: 33,
        MinorKey.b_f: 34,
        MinorKey.c_f: 35,
    }

    MIN_OCTAVE = 0
    MAX_OCTAVE = 7
    KEYS_IN_OCTAVE_MIN_MIDI_OCTAVE = {MajorKey.A, MajorKey.B_f, MajorKey.B,
                                      MinorKey.a, MinorKey.b_f, MinorKey.b}

    def __init__(self, instrument: Any = None,
                 time: float = None, duration: float = None, velocity: int = None, pitch: float = None,
                 name: str = None,
                 channel: int = None,
                 performance_attrs: PerformanceAttrs = None):
        validate_types(('start', time, float), ('duration', duration, float), ('velocity', velocity, int),
                       ('pitch', pitch, float))
        validate_optional_types(('channel', channel, int), ('name', name, str),
                                ('performance_attrs', performance_attrs, PerformanceAttrs))
        super(MidiNote, self).__init__(instrument=instrument,
                                       start=time, dur=duration, amp=velocity, pitch=pitch,
                                       name=name,
                                       performance_attrs=performance_attrs,
                                       validate=False)
        self.channel = channel or MidiNote.DEFAULT_CHANNEL

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
    def time(self):
        return self.start

    @time.setter
    def time(self, time: float):
        # noinspection PyAttributeOutsideInit
        self.start = time

    @property
    def duration(self):
        return self.dur

    @duration.setter
    def duration(self, duration: float):
        # noinspection PyAttributeOutsideInit
        self.dur = duration

    @property
    def velocity(self):
        return self.amp

    @velocity.setter
    def velocity(self, velocity: float):
        # noinspection PyAttributeOutsideInit
        self.amp = velocity

    def program_change(self, instrument: int):
        validate_type('instrument', instrument, int)
        # noinspection PyAttributeOutsideInit
        self.instrument = instrument

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
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
    def copy(source_note):
        return MidiNote(instrument=source_note.instrument,
                        time=source_note.time, duration=source_note.duration,
                        velocity=source_note.velocity, pitch=source_note.pitch,
                        name=source_note.name,
                        channel=source_note.channel,
                        performance_attrs=source_note.performance_attrs)

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} time: {self.time} '
                f'duration: {self.duration} velocity: {self.velocity} pitch: {self.pitch} channel: {self.channel}')


class NoteSequence(object):
    """Provides an iterator abstraction over a collection of Notes. If performance_attrs
       are provided, they will be applied to all Notes in the sequence if the notes are
       retrieved through the iterator. Otherwise performance_attrs that are an attribute
       of the note will be used.

       Thus, this lets clients create either type of sequence and transparently just consume
       through the iterator Notes with correct note_attrs and perf_attrs.
    """
    def __init__(self, note_list: List[Note], performance_attrs: PerformanceAttrs = None):
        validate_sequence_of_types('note_list', note_list, Note)
        validate_optional_type('performance_attrs', performance_attrs, PerformanceAttrs)

        self.index = 0
        self.note_list = note_list
        self.performance_attrs = performance_attrs

    @property
    def nl(self):
        """Get the underlying note_list.
           Alias to something shorter for client code convenience.
        """
        return self.note_list

    @property
    def pa(self):
        """Get the underlying performance_attrs.
           Alias to something shorter for client code convenience.
        """
        return self.performance_attrs

    # noinspection PyUnresolvedReferences
    def append(self, note: Note) -> NoteSequence:
        validate_type('note', note, Note)
        self.note_list.append(note)
        return self

    # noinspection PyUnresolvedReferences
    def extend(self, to_add: Union[Note, NoteSequence, List[Note]]) -> NoteSequence:
        new_note_list = None
        # Support either NoteSequence or a List[Note]
        try:
            validate_type('to_add', to_add, NoteSequence)
            new_note_list = to_add.note_list
        except ValueError:
            pass
        if not new_note_list:
            validate_sequence_of_types('to_add', to_add, Note)
            new_note_list = to_add
        self.note_list.extend(new_note_list)

        return self

    def __len__(self):
        return len(self.note_list)

    # noinspection PyUnresolvedReferences
    def __add__(self, to_add: Union[Note, NoteSequence, List[Note]]) -> NoteSequence:
        """Overloads operator + to support appending either single notes or sequences
           Tries to treat `to_add` as a Note and then as a NoteSequence. If both
           fail then it raises the last exception handled. If either succeeds
           then the operation is a success and the Note or NoteList are appended.
        """
        # Try to add as a single Note
        try:
            validate_type('to_add', to_add, Note)
            # If validation did not throw, to add is a single note, append(note)
            self.append(to_add)
            # Return self supports += without any additional code
            return self
        except ValueError:
            pass
        # If we didn't add as a single note, try to add as a NoteSequence
        # NOTE: This is crucial to the design, because any specialized sequence derived from NoteSequence, such
        # as Measure and Chord, can add its notes to any other NoteSequence
        try:
            validate_type('to_add', to_add, NoteSequence)
            # Don't need to validate NoteList because that is validated when NoteSequence constructed
            self.extend(to_add.note_list)
            return self
        except ValueError:
            pass
        # If we didn't add as a single note or NoteSequence, try to add as a List[Note]
        try:
            validate_sequence_of_types('to_add', to_add, Note)
            # If validation did not throw, to add is a list of notes, extend(note_list)
            self.extend(to_add)
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to __add__() must be a Note, NoteSequence or List[Note], arg: {to_add}')

    # noinspection PyUnresolvedReferences
    def __lshift__(self, to_add: Union[Note, NoteSequence, List[Note]]) -> NoteSequence:
        """Support `note_seq << note` syntax for appending notes to a sequence as well as `a + b`"""
        return self.__add__(to_add)

    # noinspection PyUnresolvedReferences
    def insert(self, index: int, to_add: Union[Note, NoteSequence, List[Note]]) -> NoteSequence:
        """Inserts a single note, all notes in a List[Note] or all notes in a NoteSequence.
           in stack order, i.e. reverse order of the input
        """
        validate_type('index', index, int)

        try:
            validate_type_choice('to_add', to_add, (Note, NoteSequence))
            if isinstance(to_add, Note):
                self.note_list.insert(index, to_add)
            else:
                for note in to_add.note_list:
                    self.note_list.insert(index, note)
                    # Necessary to insert in the same order as input, rather than reverse order from the input
                    index += 1
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_types('to_add', to_add, Note)
            for note in to_add:
                self.note_list.insert(index, note)
                # Necessary to insert in the same order as input, rather than reverse order from the input
                index += 1
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to insert() must be a Note, NoteSequence or List[Note], arg: {to_add}')

    # noinspection PyUnresolvedReferences
    def remove(self, to_remove: Union[Note, NoteSequence, List[Note]]):
        """Removes a single note, all notes in a List[Note] or all notes in a NoteSequence
        """

        # Swallow exception if the item to be removed is not present in note_list
        def _remove(note):
            try:
                self.note_list.remove(note)
            except ValueError:
                pass

        try:
            validate_type_choice('to_add', to_remove, (Note, NoteSequence))
            if isinstance(to_remove, Note):
                _remove(to_remove)
            else:
                for note in to_remove.note_list:
                    _remove(note)
            return self
        except ValueError:
            pass

        try:
            validate_sequence_of_types('to_add', to_remove, Note)
            for note in to_remove:
                _remove(note)
            return self
        except ValueError:
            pass

        raise ValueError(f'Arg `to_add` to remove() must be a Note, NoteSequence or List[Note], arg: {to_remove}')

    def __getitem__(self, index: int) -> Note:
        validate_type('index', index, int)
        if abs(index) >= len(self.note_list):
            raise ValueError(f'`index` out of range index: {index} len(note_list): {len(self.note_list)}')
        return self.note_list[index]

    # noinspection PyUnresolvedReferences
    def __iter__(self) -> NoteSequence:
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    def __next__(self) -> Note:
        """Always return a Note object with note_attrs and perf_attrs populated.
           This is the contract clients can expect, and thus this iterator hides
           where perf_attrs came from and always returns a Note ready for use.
           Also this deep copy prevents altering the sequence by reference so
           it can be used and reused.
        """
        if self.index == len(self.note_list):
            raise StopIteration
        note = self.note_list[self.index]
        # perf_attrs comes from the NoteSequence if present, otherwise from the Note
        self.index += 1
        return note.__class__.copy(note)

    def __eq__(self, other):
        if not other or len(self) != len(other):
            return False
        return all([self.note_list[i] == other.note_list[i] for i in range(len(self.note_list))])

    # noinspection PyUnresolvedReferences
    @staticmethod
    def copy(source_note_sequence: NoteSequence) -> NoteSequence:
        # Call the copy() for the subclass of this note type
        new_note_list = [(note.__class__.copy(note)) for note in source_note_sequence.note_list]
        new_note_sequence = NoteSequence(new_note_list,
                                         source_note_sequence.performance_attrs)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence