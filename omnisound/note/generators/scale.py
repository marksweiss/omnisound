# Copyright 2018 Mark S. Weiss

"""
Key - a designated musical note with a name and degree (in some pitch system, e.g. Western Classical)
Octave - Keys may repeat in cycles, e.g. Western Classical piano keyboard. Octave is which cycle group the
  Key is in, e.g. (Key.C, 4) is the C starting the fourth cycle on the piano and is "Middle C"
Scale - a sequence of pitch intervals that together are recognized as harmonious
Pitch - a key translated to a (numerical) value that can be used by a back end. Each Note type owns a map
  of Key => Pitch for each tuple (Key, Octave)
"""

from typing import Any, Mapping, Union

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.scale_globals import (HarmonicScale, MajorKey,
                                                     MinorKey)
from omnisound.utils.mingus_utils import set_notes_pitches_to_mingus_keys
from omnisound.utils.utils import (enum_to_dict_reverse_mapping,
                                   validate_type_choice,
                                   validate_type_reference_choice,
                                   validate_types)


class Scale(NoteSequence):
    """Encapsulates a musical Scale, which is a type of scale (an organization of intervals offset from a root key)
       and a root key. Uses mingus.scale to then retrieve the notes in the scale and provide methods to manage
       and generate Notes. Derives from NoteSequence so acts as a standard Note container.
    """
    MAJOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping(MajorKey)
    MINOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping(MinorKey)
    KEY_MAPS = {'MajorKey': MAJOR_KEY_REVERSE_MAP, 'MinorKey': MINOR_KEY_REVERSE_MAP}

    def __init__(self,
                 key: Union[MajorKey, MinorKey] = None,
                 octave: int = None,
                 harmonic_scale: HarmonicScale = None,
                 get_pitch_for_key: Any = None,
                 make_note: Any = None,
                 num_attributes: int = None,
                 attr_name_idx_map: Mapping[str, int] = None,
                 attr_vals_defaults_map: Mapping[str, float] = None,
                 attr_get_type_cast_map: Mapping[str, Any] = None):

        validate_types(('octave', octave, int), ('harmonic_scale', harmonic_scale, HarmonicScale))

        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        _, matched_key_type = validate_type_choice('key', key, (MajorKey, MinorKey))
        self.is_major_key = matched_key_type is MajorKey
        self.is_minor_key = matched_key_type is MinorKey

        self.key = key
        self.octave = octave
        self.harmonic_scale = harmonic_scale
        self.get_pitch_for_key = get_pitch_for_key

        # Get the mingus keys (pitches) for the musical scale (`scale_type`) with its root at `key`
        mingus_keys = harmonic_scale.value(key.name).ascending()
        # Trim the last element because mingus returns the first note in the next octave along with all the
        # notes in the scale of the octave requested. This behavior is observed and not exhaustively tested
        # so check and only remove if the first and last note returned are the same.
        if mingus_keys[0] == mingus_keys[-1]:
            mingus_keys = mingus_keys[:-1]
        mingus_key_to_key_enum_mapping = Scale.KEY_MAPS[matched_key_type.__name__]
        self.keys = [mingus_key_to_key_enum_mapping[mingus_key.upper()] for mingus_key in mingus_keys]

        # Construct the sequence of notes for the chord in the NoteSequence base class
        super(Scale, self).__init__(make_note=make_note,
                                    num_notes=len(mingus_keys),
                                    num_attributes=num_attributes,
                                    attr_name_idx_map=attr_name_idx_map,
                                    attr_vals_defaults_map=attr_vals_defaults_map,
                                    attr_get_type_cast_map=attr_get_type_cast_map)

        set_notes_pitches_to_mingus_keys(mingus_keys,
                                         mingus_key_to_key_enum_mapping,
                                         self,
                                         get_pitch_for_key,
                                         self.octave,
                                         validate=False)

    @staticmethod
    def get_mingus_key_to_key_enum_mapping(key_type: Union[MajorKey, MinorKey]):
        validate_type_reference_choice('key_type', key_type, (MajorKey, MinorKey))
        return Scale.KEY_MAPS[key_type.__name__]

