# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, Mapping, Sequence

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.utils.validation_utils import validate_sequence_of_type, validate_types


def set_note_pitch_to_mingus_key(mingus_key: str,
                                 mingus_key_to_key_enum_mapping: Mapping,
                                 note: Any,
                                 get_pitch_for_key: Any,
                                 octave: int,
                                 validate=True):
    if validate:
        validate_types(('mingus_key', mingus_key, str),
                       ('mingus_key_to_key_enum_mapping', mingus_key_to_key_enum_mapping, Mapping),
                       ('octave', octave, int))
    key = mingus_key_to_key_enum_mapping[mingus_key.upper()]
    note.pitch = get_pitch_for_key(key, octave=octave)


def set_notes_pitches_to_mingus_keys(mingus_keys: Sequence[str],
                                     mingus_key_to_key_enum_mapping: Mapping,
                                     notes: NoteSequence,
                                     get_pitch_for_key: Any,
                                     octave: int,
                                     validate=True):
    if validate:
        validate_sequence_of_type('mingus_key_list', mingus_keys, str)
        validate_types(('mingus_key_to_key_enum_mapping', mingus_key_to_key_enum_mapping, Dict),
                       ('notes', notes, NoteSequence), ('octave', octave, int))
        if len(mingus_keys) != len(notes):
            raise ValueError(('mingus_keys and notes must have same length. '
                              f'len(mingus_keys): {len(mingus_keys)} len(notes): {len(notes)}'))

    for i, mingus_key in enumerate(mingus_keys):
        set_note_pitch_to_mingus_key(mingus_key, mingus_key_to_key_enum_mapping,
                                     notes[i], get_pitch_for_key, octave, validate=False)


# TODO UNIT TEST
def get_chord_pitches(mingus_keys: Sequence[str],
                      mingus_key_to_key_enum_mapping: Mapping,
                      get_pitch_for_key: Any,
                      octave: int) -> Sequence[Any]:
    validate_types(('mingus_key_to_key_enum_mapping', mingus_key_to_key_enum_mapping, Mapping),
                   ('octave', octave, int))
    validate_sequence_of_type('mingus_keys', mingus_keys, str)
    return [get_pitch_for_key(mingus_key_to_key_enum_mapping[mingus_key.upper()], octave=octave)
            for mingus_key in mingus_keys]
