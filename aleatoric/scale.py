# Copyright 2018 Mark S. Weiss

"""
Key - a designated musical note with a name and degree (in some pitch system, e.g. Western Classical)
Octave - Keys may repeat in cycles, e.g. Western Classical piano keyboard. Octave is which cycle group the
  Key is in, e.g. (Key.C, 4) is the C starting the fourth cycle on the piano and is "Middle C"
Scale - a sequence of pitch intervals that together are recognized as harmonious
Pitch - a key translated to a (numerical) value that can be used by a back end. Each Note type owns a map
  of Key => Pitch for each tuple (Key, Octave)
"""

from typing import Any, Union

from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.mingus_utils import get_notes_for_mingus_keys
from aleatoric.note import PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.utils import (enum_to_dict_reverse_mapping, validate_types, validate_type_choice,\
                             validate_type_reference_choice)
from aleatoric.scale_globals import MajorKey, MinorKey, ScaleCls


class Scale(NoteSequence):
    """Encapsulates a musical Scale, which is a type of scale (an organization of intervals offset from a root key)
       and a root key. Uses mingus.scale to then retrieve the notes in the scale and provide methods to manage
       and generate Notes. Derives from NoteSequence so acts as a standard Note container.
    """
    MAJOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping('MajorKey', MajorKey)
    MINOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping('MinorKey', MinorKey)
    KEY_MAPS = {'MajorKey': MAJOR_KEY_REVERSE_MAP, 'MinorKey': MINOR_KEY_REVERSE_MAP}

    def __init__(self,
                 key: Any = None,
                 octave: int = None,
                 scale_cls: ScaleCls = None,
                 note_cls: Any = None,
                 note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote] = None,
                 performance_attrs: PerformanceAttrs = None):
        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        _, matched_key_type = validate_type_choice('key', key, (MajorKey, MinorKey))
        self.is_major_key = matched_key_type is MajorKey
        self.is_minor_key = matched_key_type is MinorKey

        validate_types(('octave', octave, int), ('scale_type', scale_cls, ScaleCls))
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_cls', note_cls, (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        self.key = key
        self.octave = octave
        self.scale_type = scale_cls
        self.note_type = note_cls
        self.note_prototype = note_prototype

        # Get the mingus keys (pitches) for the musical scale (`scale_type`) with its root at `key`
        mingus_keys = scale_cls.value(key.name).ascending()
        mingus_key_to_key_enum_mapping = Scale.KEY_MAPS[matched_key_type.__name__]
        note_list = get_notes_for_mingus_keys(matched_key_type, mingus_keys,
                                              mingus_key_to_key_enum_mapping,
                                              self.note_prototype, self.note_type, self.octave,
                                              validate=False)

        super(Scale, self).__init__(note_list, performance_attrs=performance_attrs)