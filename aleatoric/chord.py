# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from aleatoric.chord_globals import KeyChordCls, KeyScaleChordCls, ScaleChordCls

from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.note import PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.scale import Scale
from aleatoric.scale_globals import MajorKey, MinorKey, ScaleCls
from aleatoric.utils import (validate_optional_type, validate_optional_type_choice,
                             validate_type, validate_type_choice, validate_type_reference_choice)


# TODO init takes key and ChordCls and note_prototype, remove Scale
#  Constructs note_list of copies of prototype, for notes in Chord, which it gets from mingus
#  Construct NoteSeq from list
#  Staticmethod to return inversion of a Chord, take Chord as argument
#  Staticmethod to return the triad for a key and ScaleCls
#  Staticmethod to return all the triads in a key
class Chord(NoteSequence):

    CHORD_CLASS_ARG_MAPPING = {
        KeyChordCls.__name__: {'key'},
        KeyScaleChordCls.__name__: {'key', 'scale_type'},
        ScaleChordCls.__name__: {'scale_type'}
    }

    def __init__(self, chord_cls: Any = None,
                 note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote] = None,
                 note_cls: Any = None,
                 octave: int = None,
                 key: Union[MajorKey, MinorKey] = None,
                 scale_cls: ScaleCls = None,
                 performance_attrs: PerformanceAttrs = None):

        validate_type_choice('chord_cls', chord_cls, (KeyChordCls, KeyScaleChordCls, ScaleChordCls))
        validate_type_choice('note_prototype', note_prototype,
                             (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type_reference_choice('note_cls', note_cls, (CSoundNote, FoxDotSupercolliderNote, MidiNote))
        validate_type('octave', octave, int)
        validate_optional_type('scale', scale_cls, ScaleCls)

        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        # Note that this arg is not required so we may not be able to determine key type from it.
        # If we can't get key type from key, use the name of the Chord, which may be associated with
        # MinorKey. Otherwise default to MajorKey, because the mingus functions we use to return lists of string
        # names of keys return upper-case values valid for MajorKey
        matched, matched_key_type = validate_optional_type_choice('key', key, (MajorKey, MinorKey))
        if not matched:
            if chord_cls is KeyChordCls and chord_cls.name.startswith('Minor'):
                matched_key_type = MinorKey
            else:
                matched_key_type = MajorKey

        # Additional validation. It is valid to have either or both a `key` or `scale_type` arg, but you must have
        # at least one.
        if not key and not scale_cls:
            raise ValueError('At least one of args `key` and `scale` must be provided')

        # Assign attrs before completing validation because it's more convenient to check for required
        # attrs by using getattr(attr_name) after they have been assigned
        self.chord_type = chord_cls
        self.note_prototype = note_prototype
        self.note_type = note_cls
        self.octave = key
        self.key = key
        self.scale_type = scale_cls

        # Now complete validation. `chord_cls` arg maps to which args are required
        # because some chord_cls enums map to mingus function calls that require one
        # or the other or both arguments.
        required_attrs = Chord.CHORD_CLASS_ARG_MAPPING[chord_cls.__name__]
        if not all([getattr(self, attr_name) for attr_name in required_attrs]):
            raise ValueError((f'Required args: {required_attrs} not all present '
                              f'for `chord_type`: {self.chord_type}. '
                              f'Args passed in: key: {key} scale: {scale_cls}'))

        # Get the list of keys in the chord as string names from mingus
        mingus_keys = []
        if self.chord_type is KeyChordCls:
            mingus_keys = chord_cls.value(self.key.name)
        if self.chord_type is ScaleChordCls:
            mingus_keys = chord_cls.value(self.scale_type.name)
        if self.chord_type is KeyScaleChordCls:
            mingus_keys = chord_cls.value(self.key.name, self.scale_type.name)

        # Convert to Notes for this chord's note_type with pitch assigned for the key in the chord
        note_list = []
        mingus_key_to_key_enum_mapping = Scale.KEY_MAPS[matched_key_type]
        for mingus_key in mingus_keys:
            key = mingus_key_to_key_enum_mapping[mingus_key.upper()]
            new_note = self.note_type.copy(note_prototype)
            new_note.pitch = self.note_type.get_pitch_for_key(key, octave=self.octave)
            note_list.append(new_note)

        super(Chord, self).__init__(note_list, performance_attrs=performance_attrs)
