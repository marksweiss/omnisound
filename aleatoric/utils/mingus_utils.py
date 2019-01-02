# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, List, Union

from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.adapters.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.note.adapters.midi_note import MidiNote
from aleatoric.note.generators.scale_globals import MajorKey, MinorKey
from aleatoric.utils.utils import (validate_types, validate_type_choice,
                                   validate_type_reference_choice, validate_sequence_of_type)


def get_note_for_mingus_key(matched_key_type: Any,
                            mingus_key: str,
                            mingus_key_to_key_enum_mapping: Dict,
                            note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote],
                            note_type: Any,
                            octave: int,
                            validate=True):
    if validate:
        validate_type_reference_choice('matched_key_type', matched_key_type, (MajorKey, MinorKey))
        validate_types(('mingus_key', mingus_key, str),
                       ('mingus_key_to_key_enum_mapping', mingus_key_to_key_enum_mapping, Dict),
                       ('octave', octave, int))
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_type', note_type, (CSoundNote, FoxDotSupercolliderNote, MidiNote))

    key = mingus_key_to_key_enum_mapping[mingus_key.upper()]
    new_note = note_type.copy(note_prototype)
    new_note.pitch = note_type.get_pitch_for_key(key, octave=octave)

    return new_note


def get_notes_for_mingus_keys(matched_key_type: Any,
                              mingus_key_list: List[str],
                              mingus_key_to_key_enum_mapping: Dict,
                              note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote],
                              note_type: Any,
                              octave: int,
                              validate=True):
    if validate:
        validate_type_reference_choice('matched_key_type', matched_key_type, (MajorKey, MinorKey))
        validate_sequence_of_type('mingus_key_list', mingus_key_list, str)
        validate_types(('mingus_key_to_key_enum_mapping', mingus_key_to_key_enum_mapping, Dict),
                       ('octave', octave, int))
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_type', note_type, (CSoundNote, FoxDotSupercolliderNote, MidiNote))

    note_list = [get_note_for_mingus_key(matched_key_type, mingus_key, mingus_key_to_key_enum_mapping,
                                         note_prototype, note_type, octave, validate=False)
                 for mingus_key in mingus_key_list]

    return note_list
