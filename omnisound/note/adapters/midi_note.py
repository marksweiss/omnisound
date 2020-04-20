# Copyright 2018 Mark S. Weiss

from enum import Enum
from typing import Any, Mapping, Union

# TODO SHOULD THIS BE numpy.array? THAT IS USED IN note.py
from numpy import ndarray

from omnisound.note.adapters.note import add_base_attr_name_indexes, getter, setter
from omnisound.note.generators.scale_globals import (NUM_INTERVALS_IN_OCTAVE,
                                                     MajorKey, MinorKey)
from omnisound.utils.utils import (validate_optional_type, validate_optional_sequence_of_type,
                                   validate_sequence_of_type, validate_type, validate_type_choice)


CLASS_NAME = 'MidiNote'

ATTR_NAMES = ('instrument', 'time', 'duration', 'velocity', 'pitch')
ATTR_NAME_IDX_MAP = add_base_attr_name_indexes({attr_name: i for i, attr_name in enumerate(ATTR_NAMES)})
ATTR_GET_TYPE_CAST_MAP = {
    'instrument': int,
    'time': int,
    'duration': int,
    'velocity': int,
    'pitch': int,
}
NUM_ATTRIBUTES = len(ATTR_NAMES)


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


def get_pitch_for_key(key: Union[MajorKey, MinorKey], octave: int) -> int:
    """MIDI pitches sequence from 21 A0 to 127, the 3 highest notes below C1 to the last note of C7.
       The algorithm is that we store the values for C1-12 as ints in the PITCH_MAP
       and thus increment by + 12 for every octave > 1, handle the special case for the 3 notes < C1 and
       validate that the (key, octave) combination is a valid MIDI pitch.
    """
    validate_type_choice('key', key, (MajorKey, MinorKey))
    validate_type('octave', octave, int)
    if not (MIN_OCTAVE < octave < MAX_OCTAVE):
        raise ValueError(f'Arg `octave` must be in range {MIN_OCTAVE} <= octave <= {MAX_OCTAVE}')

    if octave == MIN_OCTAVE:
        # Handle edge case of only 3 notes being valid when `octave` == 0
        if key not in KEYS_IN_MIN_OCTAVE:
            raise ValueError(('If arg `octave` == 0 then `key` must be in '
                              f'{KEYS_IN_MIN_OCTAVE}'))
        return PITCH_MAP[key] - NUM_INTERVALS_IN_OCTAVE
    else:
        interval_offset = (octave - 1) * NUM_INTERVALS_IN_OCTAVE
        return PITCH_MAP[key] + interval_offset


# TODO MODIFY AS MATRIX TRANSFORM GENERIC
# TODO TEST COVERAGE
def transpose(self, interval: int):
    """Midi pitches are ints in the range MIN_PITCH..MAX_PITCH"""
    validate_type('interval', interval, int)
    new_pitch = self.pitch + interval
    if new_pitch < MIN_PITCH or new_pitch > MAX_PITCH:
        raise ValueError(f'Arg `interval` creates invalid pitch value: {new_pitch}')
    self.pitch = new_pitch


def program_change(self, instrument: int):
    validate_type('instrument', instrument, int)
    self.instrument = float(instrument)


def g_channel():
    def _g_channel(self) -> int:
        return self.channel
    return _g_channel


def s_channel():
    def _s_channel(self, channel: int) -> None:
        validate_type('channel', channel, int)
        self.channel = channel
    return _s_channel


# Fluent getters setters for core core note attributes
# noinspection PyPep8Naming
def I(self, attr_val: int):
    validate_type('attr_val', attr_val, int)
    self.note_attr_vals[self.attr_name_idx_map['instrument']] = attr_val
    return self


# noinspection PyPep8Naming
def T(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['time']] = attr_val
    return self


# noinspection PyPep8Naming
def D(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['duration']] = attr_val
    return self


# noinspection PyPep8Naming
def V(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['velocity']] = attr_val
    return self


# noinspection PyPep8Naming
def P(self, attr_val: float):
    validate_type('attr_val', attr_val, float)
    self.note_attr_vals[self.attr_name_idx_map['pitch']] = attr_val
    return self


# Method implementations for dunder magic methods so the object supports `__eq__` and `__str__`, etc.
def eq(self, other) -> bool:
    return self._instrument == other.instrument and \
           self._time == other.time and \
           self._duration == other.duration and \
           self._velocity == other.velocity and \
           self._pitch == other.pitch and \
           self._channel == other.channel


def to_str(self):
    return (f'instrument: {self.instrument} time: {self.time} '
            f'duration: {self.duration} velocity: {self.velocity} pitch: {self.pitch} channel: {self.channel}')


class MidiNoteMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)

        # Attributes assigned by the caller
        cls.note_attr_vals = None
        cls.attr_name_idx_map = None
        cls.attr_get_type_cast_map = None
        cls.performance_attrs = None

        # Custom Midi attributes
        cls.channel = DEFAULT_CHANNEL

        return cls


def _make_cls(attr_name_idx_map):
    cls_bases = ()
    methods = {}
    # Create dynamically getters and setters for the note attributes for this instantiation of a CSoundNote class
    for attr_name in attr_name_idx_map.keys():
        get_func = getter(attr_name)
        methods[f'g_{attr_name}'] = get_func
        set_func = setter(attr_name)
        methods[f's_{attr_name}'] = set_func
        methods[attr_name] = property(get_func, set_func)
    # Standard Note fluent accessor methods
    methods['I'] = I
    methods['T'] = T
    methods['D'] = D
    methods['V'] = V
    methods['P'] = P
    # Standard Note API
    methods['transpose'] = transpose
    # Supported dunder methods
    methods['__eq__'] = eq
    methods['__str__'] = to_str
    # Custom MidiNote methods
    methods['program_change'] = program_change
    # noinspection PyTypeChecker
    methods['channel'] = property(g_channel, s_channel)

    cls = MidiNoteMeta(CLASS_NAME, cls_bases, methods)
    return cls


def make_note(note_attr_vals: ndarray,
              attr_name_idx_map: Mapping[str, int],
              attr_get_type_cast_map: Mapping[str, Any] = None):
    validate_type('note_attr_vals', note_attr_vals, ndarray)
    validate_type('attr_name_idx_map', attr_name_idx_map, Mapping)
    validate_sequence_of_type('attr_name_idx_map', attr_name_idx_map.keys(), str)
    validate_optional_type('attr_get_type_cast_map', attr_get_type_cast_map, Mapping)
    if attr_get_type_cast_map:
        validate_optional_sequence_of_type('attr_get_type_cast_map', attr_get_type_cast_map.keys(), str)

    cls = _make_cls(attr_name_idx_map)
    note = cls()

    # Assign core attributes
    note.note_attr_vals = note_attr_vals
    note.attr_name_idx_map = attr_name_idx_map

    # Set mapping of attribute names to functions that cast return type of get() calls, e.g. cast instrument to int
    note.attr_get_type_cast_map = attr_get_type_cast_map or {}
    for attr_name in note.attr_name_idx_map:
        if attr_name not in note.attr_get_type_cast_map:
            note.attr_get_type_cast_map[attr_name] = lambda x: x
    # These are always returned as an int
    note.attr_get_type_cast_map['instrument'] = int
    note.attr_get_type_cast_map['velocity'] = int
    note.attr_get_type_cast_map['pitch'] = int
    note.attr_get_type_cast_map['channel'] = int

    return note
