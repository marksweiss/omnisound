# Copyright 2018 Mark S. Weiss

from enum import Enum
from typing import Any, Dict, List, Optional

from aleatoric.utils import (validate_list_of_types, validate_optional_type, validate_optional_types,
                             validate_not_none, validate_type, validate_types)


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

    def is_frozen(self):
        return self.frozen

    def __str__(self):
        return ' '.join([f'{attr_name}: {getattr(self, attr_name)}' for attr_name in self.attr_type_map.keys()])

    def as_dict(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.attr_type_map.keys()}


class Note(object):
    """Models the core attributes of a musical note common to multiple back ends"""

    name: Optional[str]
    DEFAULT_NAME = 'Note'

    def __init__(self, instrument: Any = None,
                 start: float = None, dur: float = None, amp: float = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None,
                 validate=True):
        if validate:
            validate_types(('start', start, float), ('dur', dur, float), ('amp', amp, float),
                           ('pitch', pitch, float))
            validate_optional_types(('name', name, str), ('performance_attrs', performance_attrs, PerformanceAttrs))

        self.instrument = instrument
        self.start = start
        self.dur = dur
        self.amp = amp
        self.pitch = pitch
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
    def get_config():
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
    def get_config():
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
    def get_config():
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

    @staticmethod
    def copy(source_note):
        return CSoundNote(instrument=source_note.instrument,
                          start=source_note.start, duration=source_note.dur,
                          amplitude=source_note.amp, pitch=source_note.pitch,
                          name=source_note.name,
                          performance_attrs=source_note.performance_attrs)

    def __str__(self):
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
    def get_config():
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
        validate_list_of_types('note_list', note_list, Note)
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

    def append(self, note: Note):
        validate_type('note', note, Note)
        self.note_list.append(note)

    def extend(self, new_note_list: List[Note]):
        validate_list_of_types('new_note_list', new_note_list, Note)
        self.note_list.extend(new_note_list)

    def __len__(self):
        return len(self.note_list)

    def __add__(self, to_add: Any):
        """Overloads operator + to support appending either single notes or sequences
           Tries to treat `to_add` as a Note and then as a NoteSequence. If both
           fail then it raises the last exception handled. If either succeeds
           then the operation is a success and the Note or NoteList are appended.
        """
        added = False
        # Try to add as a single Note
        try:
            validate_type('to_add', to_add, Note)
            # If validation did not throw, to add is a single note, append(note)
            self.append(to_add)
            added = True
        except ValueError:
            pass
        # If we didn't add as a single note, try to add as a NoteList
        if not added:
            try:
                validate_list_of_types('to_add', to_add, Note)
                # If validation did not throw, to add is a list of notes, extend(note_list)
                self.extend(to_add)
                added = True
            except ValueError:
                pass
        # If not added as a single Note or a NoteList, raise
        if not added:
            raise ValueError(f'Arg `to_add` to __add__() must be a Note or NoteList, arg: {to_add}')

        # Return self supports += without any additional code
        return self

    def __lshift__(self, to_add: Any):
        """Support `note_seq << note` syntax for appending notes to a sequence as well as `a + b`"""
        return self.__add__(to_add)

    def insert(self, index: int, note: Note):
        validate_types(('index', index, int), ('note', note, Note))
        self.note_list.insert(index, note)

    def remove(self, note: Note):
        validate_type('note', note, Note)
        # Swallow exception if the item to be removed is not present in note_list
        try:
            self.note_list.remove(note)
        except ValueError:
            pass

    def __getitem__(self, index):
        validate_type('index', index, int)
        if index < 0 or index >= len(self.note_list):
            raise ValueError(f'`index` out of range index: {index} len(note_list): {len(self.note_list)}')
        return self.note_list[index]

    def __iter__(self):
        """Reset iter position. This behavior complements __next__ to make the
           container support being iterated multiple times.
        """
        self.index = 0
        return self

    def __next__(self):
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

    @staticmethod
    def dup(source_note_sequence):
        # Call the dup() for the subclass of this note type
        new_note_list = [(note.__class__.copy(note)) for note in source_note_sequence.note_list]
        new_note_sequence = NoteSequence(new_note_list,
                                         source_note_sequence.performance_attrs)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence