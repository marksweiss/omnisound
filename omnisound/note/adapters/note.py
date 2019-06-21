# Copyright 2018 Mark S. Weiss

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from numpy import float64, array, resize

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.generators.scale_globals import MajorKey, MinorKey
from omnisound.utils.utils import validate_type, validate_type_choice


INSTRUMENT_I = I = 0
START_I = S = 1
DUR_I = D = 2
AMP_I = A = 3
PITCH_I = P = 4


class NoteValues(object):
    def __init__(self, attr_names):
        self._attr_names = attr_names
        for attr_name in attr_names:
            setattr(self, attr_name, None)

    def as_dict(self) -> Dict:
        return {field: getattr(self, field) for field in self._attr_names}

    def as_list(self) -> List:
        return [getattr(self, field) for field in self._attr_names]

    def as_array(self) -> array:
        return array(self.as_list ())


# noinspection PyPep8Naming
class Note(ABC):
    """Models the core attributes of a musical note common to multiple back ends.
       Core properties are defined here that are the property interface for Notes in derived classes, which are
       note_attrs that define the attributes for a specific back end, e.g. `CSoundNote`, `MidiNote`, etc. The core
       properties are `instrument`, `start`, `duration`, `amplitude` and `pitch`. The interface here is abstract so
       types aren't specified, but derived classes are expected to define types and enforce them with validation in
       `__init__()` and all setters. Derived note_attrs may also create aliased properties for these core properties that
       match the conventions of their backend, and of course they may define additional properties specific to that
       backend.
       In addition, each derived type is expected to define equality, a `copy()` constructor, and `str`. Note that
       `str` may be meaningful output, as in the case of `CSoundNote`, which produces a string that can be inserted
       into a CSound score file which CSound uses to render audio. Or it may be merely a string representation of
       the information in the note, as is the case for Midi.
       Finally, each note is responsible for being able to translate a musical key (pitch on a scale) to a valid
       pitch value for that Note's backend, in the `get_pitch_for_key()` method.
       It is is strongly preferred that all getter properties return self in derived classes
       to support fluid interfaces for defining and modifying note_attrs most easily in the least number of lines.
       NOTE: Standard pattern for extending Note to add custom attributes:
       In MyNote.__init__():
       1) Call Note.add_attr_name() for each attribute that you want to add AND map to an existing attribute,
          e.g. MidiNote maps the alias property name 'time' to the property 'start'
       2) Call Note.__setattr__() for each attribute that is both a new name (not in Note base) and also does not
          map to an existing Note attribute. e.g. FoxdotSupercolliderNote has 'octave', which is not represented
          in the underlying Note
       3) Call Note.__setattr__() for each attribute that is reused in the underlying Note
       Add additional methods:
       4) For each attribute that aliases a new name in the derived note to an attribute in the underlying
          Note, e.g. 'time' to 'start' in MidiNote, the derived note needs to declare explicit @property get/set
          methods which call super(MyNote, self).__getattr__('my_attribute_name'), the explicit overridden getattr()
          in the derived Note
       5) For each attribute that uses the same name as the underlying attribute but changes the input/output value,
          applies validation, or otherwise needs logic (typical case is casting the return value from float to int
          because all Note values are stored as numpy.float64), write overriding property methods as in 4)
    """
    # noinspection SpellCheckingInspection
    BASE_NAME_INDEX_MAP = {
        'instrument': INSTRUMENT_I,
        'i': INSTRUMENT_I,
        'start': START_I,
        's': START_I,
        'dur': DUR_I,
        'd': DUR_I,
        'amp': AMP_I,
        'a': AMP_I,
        'pitch': PITCH_I,
        'p': PITCH_I,
    }

    def __init__(self,
                 attrs: array = None,
                 attr_name_idx_map: Dict[str, int] = None,
                 attr_vals_map: Dict[str, float] = None,
                 note_num: int = None):
        """
        The Note is a view over a row of a 2D numpy array storing data for one Note. Each row in the array represents
        a Note in a NoteSequence. The NoteSequence class constructs the storage and manages a sequence of notes. It
        constructs objects of types derived from Note to provide an OO API with properties and methods to read and
        write the attributes of a Note (a row of data in the underlying NoteSequence numpy array).
        `attrs` - numpy array of Note data. Columns are note attributes, values are values for each attribute.
        `attr_name_idx_map` - map of attribute names to array index storing the value for that attribute. Set by
          the NoteSequence creating the storage for this Note
        `attr_vals_map` - a set of values to assign to the attributes of the Note
        `note_num` - the position of the Note in the NoteSequence it is in. Required for NoteSequence.delete(), but it
         also serves as the unique_id of the Note in the sequence it is in
        Any base attributes for which no value is provided are initialized to 0.0. All values are stored internally
        as `numpy.float64` and returned as that type. Derived types wishing to cast values can do so by wrapping
        individual attributes. An example of this is `CsoundNote.instrument`, which must be `int`.
        """
        self.__dict__['_attrs'] = attrs
        self.__dict__['_attr_name_idx_map'] = attr_name_idx_map

        if attr_vals_map:
            # The user provided attributes and values. For any of them that match BASE_ATTR_NAMES, simply
            # set the value for that attribute from the value provided. For any that are new attributes, append
            # those attributes to `self.__dict__['_attrs']` and `self.__dict__['_attr_name_idx_map']`
            # and set the value for that attribute.
            for attr_name, attr_val in attr_vals_map.items():
                if not attr_val:
                    continue
                if attr_name in {'instrument', 'i'}:
                    validate_type_choice(attr_name, attr_val, (float, int))
                else:
                    validate_type(attr_name, attr_val, float)
            # For every attr_name, if it is in kwargs then assign attrs to the value passed in in kwargs
            for attr_name in attr_name_idx_map.keys():
                self.__dict__['_attrs'][attr_name_idx_map[attr_name]] = attr_vals_map[attr_name]

    # TODO THIS SHOULD GO AWAY AND MOVE TO INIT
    # TODO REMOVE DERIVED CLASS CALLS TO THIS
    def add_attr_name(self, attr_name: str, attr_idx: int):
        """Let's the user create more than one attribute that maps to the same attr index. So, for example,
           it supports aliasing multiple attribute names to one index. This should be called before assigning
           attributes with __setattr__() in derived class __init__() calls. This way the attributes are already
           in the attr_name_idx_map and get their value assigned correctly."""
        self.__dict__['_attr_name_idx_map'][attr_name] = attr_idx
        self.__dict__[attr_name] = None

    def __getattr__(self, attr_name: str) -> float64:
        """Handle returning note_attr from _attrs array or any other attr a derived Note class might define"""
        validate_type('attr_name', attr_name, str)
        if attr_name in self.__dict__['_attr_name_idx_map']:
            return self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map'][attr_name]]
        else:
            # noinspection PyTypeChecker
            return None

    # TODO SETTING WITH PROPERTIES MUST BE BROKEN AND UNTESTED
    def __setattr__(self, attr_name: str, attr_val: Any):
        """Handle setting note_attr from _attrs array or any other attr a derived Note class might define.
           Returns self to support chained fluent interface style calls."""
        if attr_name in {'pa', 'performance_attrs'}:
            self.__dict__['_performance_attrs'] = attr_val
            return
        validate_type('attr_name', attr_name, str)
        if attr_name in self.__dict__['_attr_name_idx_map']:
            self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map'][attr_name]] = attr_val
        # TODO THIS ENTIRE BLOCK GOES AWAY
        else:
            # It's a new attribute name, so:
            # - map this attribute name to the next index in attr_name_idx_map
            # - resize the numpy array storing the values, _attrs, up by 1
            # - add the attr_name without a value to the object's self.__dict__. This means the object's __getattr__
            #   will respond to get calls on this attribute, and __getattr__() will intercept these and return
            #   the value from the correct index of _attrs, because it is defined to do that
            attr_idx = len(self.__dict__['_attrs'])
            self.__dict__['_attr_name_idx_map'][attr_name] = attr_idx
            self.__dict__['_attrs'] = resize(self.__dict__['_attrs'], attr_idx + 1)
            self.__dict__['_attrs'][attr_idx] = float(attr_val)
            self.__dict__[attr_name] = None

    # These standard methods are provided without the ability to override names, etc., to provide API for fluent
    # chaining calls to set all common Note attributes on one line
    # e.g. - note.I(1).S(1.0).D(2.5).A(400).P(440)
    def I(self, instrument: [float, int]):
        self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map']['instrument']] = instrument
        return self

    def S(self, start: [float, int]):
        self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map']['start']] = start
        return self

    def D(self, dur: [float, int]):
        self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map']['dur']] = dur
        return self

    def A(self, amp: [float, int]):
        self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map']['amp']] = amp
        return self

    def P(self, pitch: [float, int]):
        self.__dict__['_attrs'][self.__dict__['_attr_name_idx_map']['pitch']] = pitch
        return self

    @abstractmethod
    def transpose(self, interval: int):
        raise NotImplemented('Derived type must implement Note.transpose -> Note')

    @property
    @abstractmethod
    def performance_attrs(self) -> PerformanceAttrs:
        raise NotImplemented('Derived type must implement Note.performance_attrs -> PerformanceAttrs')

    @performance_attrs.setter
    @abstractmethod
    def performance_attrs(self, performance_attrs: PerformanceAttrs):
        raise NotImplemented('Derived type must implement Note.performance_attrs')

    @property
    @abstractmethod
    def pa(self) -> PerformanceAttrs:
        """Alias to something shorter for client code convenience."""
        raise NotImplemented('Derived type must implement Note.pa -> PerformanceAttrs')

    @pa.setter
    @abstractmethod
    def pa(self, performance_attrs: PerformanceAttrs):
        """Alias to something shorter for client code convenience."""
        raise NotImplemented('Derived type must implement Note.pa')

    @classmethod
    @abstractmethod
    def get_pitch_for_key(cls, key: Union[MajorKey, MinorKey], octave: int) -> Any:
        raise NotImplemented('Note subtypes must implement get_pitch() and return a valid pitch value for their type')

    @abstractmethod
    def __eq__(self, other: 'Note') -> bool:
        raise NotImplemented('Derived type must implement Note.__eq__() -> bool')

    @abstractmethod
    def __str__(self):
        raise NotImplemented('Derived type must implement Note.__str__()')
