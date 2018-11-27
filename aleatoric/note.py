# Copyright 2018 Mark S. Weiss

from copy import copy
from typing import Any, Dict, List, Optional


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
        if not isinstance(attr_name, str) or not attr_type:
            raise ValueError((f'type: {attr_type} must be a type '
                              f'and name: {name} must be a string'))
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
                 performance_attrs: PerformanceAttrs = None):
        self.__validate(instrument, start, dur, amp, pitch, performance_attrs)
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
    def dup(source_note):
        Note.__validate(source_note.instrument,
                        source_note.start, source_note.dur, source_note.amp, source_note.pitch,
                        source_note.performance_attrs)
        return Note(instrument=source_note.instrument,
                    start=source_note.start, dur=source_note.dur, amp=source_note.amp, pitch=source_note.pitch,
                    name=source_note.name,
                    performance_attrs=source_note.performance_attrs)

    @staticmethod
    def __validate(instrument, start, dur, amp, pitch, performance_attrs):
        if not instrument or \
                (not isinstance(start, float) and not isinstance(start, int)) or \
                not isinstance(dur, float) or \
                (not isinstance(amp, float) and not isinstance(amp, int)) or \
                (not isinstance(pitch, int) and not isinstance(pitch, float)):
            raise ValueError((f'Must provide value for required NoteAttrs args: '
                              f'instrument: {instrument} start {start} dur: {dur} amp: {amp} pitch: {pitch}'))
        if performance_attrs and not isinstance(performance_attrs, PerformanceAttrs):
            raise ValueError((f'`performance_attrs` must be None or of type `PerformanceAttrs` '
                              f'performance_attrs: {performance_attrs}'))

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
        super(FoxDotSupercolliderNote, self).__init__(instrument=synth_def,
                                                      start=delay, dur=dur, amp=amp, pitch=degree,
                                                      name=name,
                                                      performance_attrs=performance_attrs)
        if oct:
            if not isinstance(oct, int):
                raise ValueError(f'oct: {oct} must must be type int')
            self.oct = oct
        if scale:
            if scale not in FoxDotSupercolliderNote.SCALES:
                raise ValueError((f'scale: {scale} must must be in '
                                  f'allowed scales {FoxDotSupercolliderNote.SCALES}'))
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
    def dup(source_note):
        return FoxDotSupercolliderNote(synth_def=source_note.synth_def,
                                       delay=source_note.delay, dur=source_note.dur,
                                       amp=source_note.amp, degree=source_note.degree,
                                       name=source_note.name,
                                       oct=source_note.oct, scale=source_note.scale,
                                       performance_attrs=source_note.performance_attrs)

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
        super(CSoundNote, self).__init__(instrument=instrument,
                                         start=start, dur=duration, amp=amplitude, pitch=pitch,
                                         name=name,
                                         performance_attrs=performance_attrs)

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
    def dup(source_note):
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

    def __init__(self, instrument: Any = None,
                 time: float = None, duration: float = None, velocity: float = None, pitch: float = None,
                 name: str = None,
                 channel: int = None,
                 performance_attrs: PerformanceAttrs = None):
        super(MidiNote, self).__init__(instrument=instrument,
                                       start=time, dur=duration, amp=velocity, pitch=pitch,
                                       name=name,
                                       performance_attrs=performance_attrs)
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
        if instrument is None:
            raise ValueError(f'MidiNote must provide value for required arg instrument: {instrument}')
        # noinspection PyAttributeOutsideInit
        self.instrument = instrument

    @staticmethod
    def dup(source_note):
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
        NoteSequence._validate_note_list(note_list)
        if performance_attrs and not isinstance(performance_attrs, PerformanceAttrs):
            raise ValueError((f'Must provide valid `performance_attrs` '
                              f'performance_attrs: {performance_attrs}'))
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
        NoteSequence._validate_note(note)
        self.note_list.append(note)

    def extend(self, new_note_list: List[Note]):
        NoteSequence._validate_note_list(new_note_list)
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
            NoteSequence._validate_note(to_add)
            # If validation did not throw, to add is a single note, append(note)
            self.append(to_add)
            added = True
        except ValueError:
            pass
        # If we didn't add as a single note, try to add as a NoteList
        if not added:
            try:
                NoteSequence._validate_note_list(to_add)
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
        NoteSequence._validate_note(note)
        NoteSequence._validate_index(index)
        self.note_list.insert(index, note)

    def remove(self, note: Note):
        NoteSequence._validate_note(note)
        # Swallow exception if the item to be removed is not present in note_list
        try:
            self.note_list.remove(note)
        except ValueError:
            pass

    def __getitem__(self, index):
        NoteSequence._validate_index(index)
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
        return note.__class__.dup(note)

    @staticmethod
    def dup(source_note_sequence):
        # Call the dup() for the subclass of this note type
        new_note_list = [(note.__class__.dup(note)) for note in source_note_sequence.note_list]
        new_note_sequence = NoteSequence(new_note_list,
                                         source_note_sequence.performance_attrs)
        new_note_sequence.index = source_note_sequence.index
        return new_note_sequence

    @staticmethod
    def _validate_note(note):
        if not isinstance(note, Note):
            raise ValueError((f'Each element in `note_list` must be a valid `Note` '
                              f'note: {note}'))

    @staticmethod
    def _validate_note_list(note_list: List[Note]):
        if not note_list or not isinstance(note_list, list):
            raise ValueError(f'`note_list` must be a non-empty list note_list: {note_list}')
        for note in note_list:
            NoteSequence._validate_note(note)

    @staticmethod
    def _validate_index(index: int):
        if not isinstance(index, int):
            raise ValueError(f'`index` must be an int, index: {index}')
