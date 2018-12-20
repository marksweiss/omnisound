# Copyright 2018 Mark S. Weiss

"""
Key - a designated musical note with a name and degree (in some pitch system, e.g. Western Classical)
Octave - Keys may repeat in cycles, e.g. Western Classical piano keyboard. Octave is which cycle group the
  Key is in, e.g. (Key.C, 4) is the C starting the fourth cycle on the piano and is "Middle C"
Scale - a sequence of pitch intervals that together are recognized as harmonious
Pitch - a key translated to a (numerical) value that can be used by a back end. Each Note type owns a map
  of Key => Pitch for each tuple (Key, Octave)
"""

from typing import Any

from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.note import Note, PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.utils import validate_type_choice, validate_types
from aleatoric.scale_globals import MajorKey, MinorKey, ScaleCls


MAJOR_KEY_REVERSE_MAP = {eval(f'MajorKey.{enum_member}.value'): getattr(MajorKey, enum_member)
                         for enum_member in MajorKey.__members__}
MINOR_KEY_REVERSE_MAP = {eval(f'MinorKey.{enum_member}.value'): getattr(MinorKey, enum_member)
                         for enum_member in MinorKey.__members__}


class Scale(NoteSequence):
    """Encapsualtes a musical Scale, which is a type of scale (an organization of intervals offset from a root key)
       and a root key. Uses mingus.scale to then retrieve the notes in the scale and provide methods to manage
       and generate Notes. Derives from NoteSequence so acts as a standard Note container.
    """
    KEY_MAPS = {'MajorKey': MAJOR_KEY_REVERSE_MAP, 'MinorKey': MINOR_KEY_REVERSE_MAP}

    def __init__(self,
                 key: Any = None,
                 octave: int = None,
                 scale_cls: ScaleCls = None,
                 note_cls: Any = None,
                 note_prototype: Any = None,
                 performance_attrs: PerformanceAttrs = None):
        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        _, matched_key_type = validate_type_choice('key', key, (MajorKey, MinorKey))
        # Validate args and set members
        validate_types(('octave', octave, int), ('scale_type', scale_cls, ScaleCls))
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote, Note))
        # validate_type_choice() failing when passed class names. Note sure why. isinstance() not working when
        # comparing class references to each other.
        # TODO ADD THIS TO UTILS AS TEST FOR A REFERENCE TO A TYPE
        if note_cls not in {CSoundNote, FoxDotSupercolliderNote, MidiNote, Note}:
            raise ValueError('arg `note_cls` must be in {CSoundNote, FoxDotSupercolliderNote, MidiNote, Note}')
        self.key = key
        self.octave = octave
        self.scale_type = scale_cls
        self.note_type = note_cls
        self.note_prototype = note_prototype
        self.is_major_key = matched_key_type == MajorKey
        self.is_minor_key = matched_key_type == MinorKey

        # Get the mingus keys (pitches) for the musical scale (`scale_type`) with its root at `key` and
        # octave at `octave`. This returns a list of string values which match the `name`s of entries
        # in MajorKey and MinorKey enums.

        # TODO MINOR KEYS ARE BROKEN
        #  NEED TO UNDERSTAND ACTUAL THEORY BETTER
        #  NEED TO UNDERSTAND MINGUS BETTER
        # NOTE: mingus expects key names in upper case (or it raises) but it returns them in lower for minor keys
        m_keys = scale_cls.value(key.name.upper(), octaves=octave).ascending()

        # Construct a list of Notes from the mingus notes, setting their pitch to the pitch in the scale
        # converted to the value for the type of Note. Other attributes are set to Note defaults.
        # pitch logic is: convert string note from mingus string to pitch enum. The enum
        # and `octave` are args passed to `note_type.get_pitch()` for the note_type, which maps (key_enum, octave)
        # to pitch values for that note type.
        # e.g. CSoundNote.get_pitch(key=MajorKey.C, octave=4) -> 4.01: float
        self.key_mapping = Scale.KEY_MAPS[matched_key_type.__name__]
        note_list = []
        for m_key in m_keys:
            new_note = self.note_type.copy(note_prototype)
            new_note.pitch = self.note_type.get_pitch_for_key(self.key_mapping[m_key], octave=self.octave)
            note_list.append(new_note)
        # Set this List[Note] in the base class for this NoteSequence
        super(Scale, self).__init__(note_list, performance_attrs=performance_attrs)