# Copyright 2018 Mark S. Weiss

from typing import Any, List, Union

from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.scale import Scale
from aleatoric.scale_globals import MajorKey, MinorKey
from aleatoric.utils import (validate_type, validate_type_choice,
                             validate_type_reference_choice, validate_sequence_of_types)


def get_note_for_mingus_key(matched_key_type: Any,
                            mingus_key: str,
                            note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote],
                            note_type: Any,
                            octave: int,
                            validate=True):
    if validate:
        validate_type_reference_choice('matched_key_type', matched_key_type, (MajorKey, MinorKey))
        validate_type('mingus_key', mingus_key, str)
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_type', note_type, (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type('octave', octave, int)

    mingus_key_to_key_enum_mapping = Scale.KEY_MAPS[matched_key_type]
    key = mingus_key_to_key_enum_mapping[mingus_key.upper()]
    new_note = note_type.copy(note_prototype)
    new_note.pitch = note_type.get_pitch_for_key(key, octave=octave)

    return new_note


def get_notes_for_mingus_keys(matched_key_type: Any,
                              mingus_key_list: List[str],
                              note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote],
                              note_type: Any,
                              octave: int,
                              validate=True):
    if validate:
        validate_type_reference_choice('matched_key_type', matched_key_type, (MajorKey, MinorKey))
        validate_sequence_of_types('mingus_key_list', mingus_key_list, str)
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_type', note_type, (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type('octave', octave, int)

    note_list = [get_note_for_mingus_key(matched_key_type, mingus_key, note_prototype, note_type, octave, validate=False)
                 for mingus_key in mingus_key_list]

    return note_list
