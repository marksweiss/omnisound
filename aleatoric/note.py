# Copyright 2018 Mark S. Weiss

from typing import Optional, Dict, Any


class NoteAttrs(object):
    """Models the core attributes of a musical note common to multiple back ends"""

    name: Optional[str]
    DEFAULT_NAME = ''

    def __init__(self, instrument: Any = None, start: float = None, dur: float = None,
                 amp: float = None, pitch: float = None, name: str = None):
        self.__validate(instrument, start, dur, amp, pitch)
        self.name = name or NoteAttrs.DEFAULT_NAME
        self.instrument = instrument
        self.start = start
        self.dur = dur
        self.amp = amp
        self.pitch = pitch

    @staticmethod
    def __validate(instrument, start, dur, amp, pitch):
        if not instrument or not isinstance(start, float) or not isinstance(dur, float) or \
                not isinstance(amp, float) or not isinstance(pitch, float):
            raise ValueError((f'Must provide value for required NoteAttrs args: '
                              f'instrument: {instrument} start {start} dur: {dur} amp: {amp} pitch: {pitch}'))

    def __str__(self):
        return (f'name: {self.name} instrument: {self.instrument} start: {self.start} '
                f'dur: {self.dur} amp: {self.amp} pitch: {self.pitch}')


class SupercolliderNoteAttrs(NoteAttrs):

    SCALES = {'aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian', 'dorian2',
              'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian', 'justMajor', 'justMinor',
              'locrian', 'locrianMajor', 'lydian', 'lydianMinor', 'major', 'majorPentatonic', 'melodicMajor',
              'melodicMinor', 'minor', 'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus',
              'romanianMinor', 'yu', 'zhi'}

    # noinspection PyShadowingBuiltins
    def __init__(self, synth_def: Any = None, dur: float = None,
                 amp: float = None, degree: float = None, name: str = None,
                 oct: int = None, scale: str = None):
        # start not meaningful for Supercollider
        start = 0.0
        self.__validate(oct, scale)
        super(SupercolliderNoteAttrs, self).__init__(instrument=synth_def, start=start, dur=dur,
                                                     amp=amp, pitch=degree, name=name)
        if oct:
            if not isinstance(oct, int):
                raise ValueError(f'oct: {oct} must must be type int')
            self.oct = oct
        if scale:
            if scale not in SupercolliderNoteAttrs.SCALES:
                raise ValueError(f'scale: {scale} must must be in allowed scales {SupercolliderNoteAttrs.SCALES}')
            self.scale = scale

    def __str__(self):
        s = (f'name: {self.name} synth_def: {self.instrument} start: {self.start} '
             f'dur: {self.dur} amp: {self.amp} degree: {self.pitch}')
        if hasattr(self, 'oct'):
            s += f' oct: {self.oct}'
        if hasattr(self, 'scale'):
            s += f' scale: {self.scale}'
        return s


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
    attr_type_map: Dict[str, Any]

    DEFAULT_NAME = ''

    def __init__(self, name):
        self.name: str = name or PerformanceAttrs.DEFAULT_NAME
        self.frozen: bool = False
        self.attr_type_map = {}
        self.config = PerformanceAttrs()

    def add_attr(self, attr_name: str = None, val=None, attr_type=None):
        if not isinstance(attr_name, str) or not attr_type:
            raise ValueError((f'type: {attr_type} must be a type '
                              f'and name: {name} must be a string'))
        if self.frozen:
            raise PerformanceAttrsFrozenException((f'Attempt to set attribute: {attr_name} '
                                                   f'on frozen PerformanceConfigFactory: {self.name}'))
        self.attr_type_map[attr_name] = type
        setattr(self, attr_name, val)

    def __setattr__(self, attr_name, val):
        if attr_name not in self.attr_type_map:
            raise ValueError('Invalid attribute name')
        if not isinstance(val, self.attr_type_map[attr_name]):
            raise ValueError(f'val: {val} must be of type: {self.attr_type_map[attr_name]}')
        super(PerformanceAttrs, self).__setattr__(attr_name, val)

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def is_frozen(self):
        return self.frozen

    def __str__(self):
        return ' '.join([f'{attr_name}: {getattr(self, attr_name)}' for attr_name in self.attr_type_map.keys()])

    def asdict(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.attr_type_map.keys()}


class Note(object):
    def __init__(self, note_attrs: NoteAttrs = None, performance_attrs: PerformanceAttrs = None):
        # performance_attrs is optional
        if not isinstance(note_attrs, NoteAttrs) or \
                performance_attrs and not isinstance(performance_attrs, PerformanceAttrs):
            raise ValueError((f'Must provide valid `note_attrs` and `performance_attrs`: '
                              f'note_attrs: {note_attrs} performance_attrs: {performance_attrs}'))
        self.note_attrs = note_attrs
        self.performance_attrs = performance_attrs


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0
    """

    REST_AMP = 0.0

    def __init__(self, note_attrs: NoteAttrs = None, performance_attrs: PerformanceAttrs = None):
        super(RestNote, self).__init__(note_attrs=note_attrs, performance_attrs=performance_attrs)
        self.amp = RestNote.REST_AMP

    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP


class SupercolliderNote(Note):
    """Models a note with attributes aliased to and specific to Supercollider
    """

    def __init__(self, note_attrs: SupercolliderNoteAttrs = None, performance_attrs: PerformanceAttrs = None):
        super(SupercolliderNote, self).__init__(note_attrs=note_attrs, performance_attrs=performance_attrs)

    @property
    def degree(self):
        return self.pitch

    @degree.setter
    def degree(self, degree: float):
        # noinspection PyAttributeOutsideInit
        self.pitch = degree


class CSoundNote(Note):
    """Models a note with attributes aliased to and specific to CSound
       and with a str() that prints CSound formatted output.
    """

    def __init__(self, note_attrs: NoteAttrs = None, performance_attrs: PerformanceAttrs = None):
        if not performance_attrs or not hasattr(performance_attrs, 'instrument'):
            raise ValueError(f'performance_attrs: {performance_attrs} must provide values for arg `instrument`')
        super(CSoundNote, self).__init__(note_attrs=note_attrs, performance_attrs=performance_attrs)

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


class MidiNote(Note):
    """Models a note with attributes aliased to and specific to MIDI
       and with a str() that prints MIDI formatted output.
    """

    DEFAULT_CHANNEL = 1

    def __init__(self, note_attrs: NoteAttrs = None, performance_attrs: PerformanceAttrs = None):
        if not hasattr(performance_attrs, 'channel'):
            performance_attrs.channel = MidiNote.DEFAULT_CHANNEL
        super(MidiNote, self).__init__(note_attrs=note_attrs, performance_attrs=performance_attrs)

    @property
    def velocity(self):
        return self.amp

    @velocity.setter
    def velocity(self, velocity: float):
        # noinspection PyAttributeOutsideInit
        self.amp = velocity

    def program_change(self, instrument: int):
        if instrument is None:
            raise ValueError(f'MidiNote must provide value for required arg instrument: {instrument}')
        # noinspection PyAttributeOutsideInit
        self.instrument = instrument
