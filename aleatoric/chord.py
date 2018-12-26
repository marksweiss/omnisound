# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from mingus.core.chords import (first_inversion as m_first_inversion,
                                second_inversion as m_second_inversion,
                                third_inversion as m_third_inversion)

from aleatoric.chord_globals import KeyChordCls, KeyScaleChordCls, ScaleChordCls
from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.note import PerformanceAttrs
from aleatoric.mingus_utils import get_note_for_mingus_key, get_notes_for_mingus_keys
from aleatoric.note_sequence import NoteSequence
from aleatoric.scale_globals import MajorKey, MinorKey, ScaleCls
from aleatoric.utils import (validate_optional_type, validate_optional_type_choice,
                             validate_type, validate_type_choice, validate_type_reference_choice)


class Chord(NoteSequence):

    CHORD_CLASS_ARG_MAPPING = {
        KeyChordCls.__name__: {'key'},
        KeyScaleChordCls.__name__: {'key', 'scale_type'},
        ScaleChordCls.__name__: {'scale_type'}
    }

    def __init__(self,
                 chord_cls: Any = None,
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
        matched, self.matched_key_type = validate_optional_type_choice('key', key, (MajorKey, MinorKey))
        if not matched:
            if chord_cls is KeyChordCls and chord_cls.name.startswith('Minor'):
                self.matched_key_type = MinorKey
            else:
                self.matched_key_type = MajorKey

        # Additional validation. It is valid to have either or both a `key` or `scale_type` arg, but you must have
        # at least one.
        if not key and not scale_cls:
            raise ValueError('At least one of args `key` and `scale` must be provided')

        # Assign attrs before completing validation because it's more convenient to check for required
        # attrs by using getattr(attr_name) after they have been assigned
        self.chord_type = chord_cls
        self.note_prototype = note_prototype
        self.note_type = note_cls
        self.octave = octave
        self.key = key
        self.scale_type = scale_cls
        self.performance_attrs = performance_attrs

        # Now complete validation. `chord_cls` arg maps to which args are required
        # because some chord_cls enums map to mingus function calls that require one
        # or the other or both arguments.
        required_attrs = Chord.CHORD_CLASS_ARG_MAPPING[chord_cls.__name__]
        if not all([getattr(self, attr_name) for attr_name in required_attrs]):
            raise ValueError((f'Required args: {required_attrs} not all present '
                              f'for `chord_type`: {self.chord_type}. '
                              f'Args passed in: key: {key} scale: {scale_cls}'))

        # Get the list of keys in the chord as string names from mingus
        self._mingus_chord = []
        if self.chord_type is KeyChordCls:
            self._mingus_chord = chord_cls.value(self.key.name)
        if self.chord_type is ScaleChordCls:
            self._mingus_chord = chord_cls.value(self.scale_type.name)
        if self.chord_type is KeyScaleChordCls:
            self._mingus_chord = chord_cls.value(self.key.name, self.scale_type.name)

        # Convert to Notes for this chord's note_type with pitch assigned for the key in the chord
        note_list = get_notes_for_mingus_keys(self.matched_key_type, self._mingus_chord,
                                              self.note_prototype, self.note_type, self.octave,
                                              validate=False)
        super(Chord, self).__init__(note_list, performance_attrs=performance_attrs)

    def invert_first_inversion(self):
        """Modifies this Chord's note_list to its first inversion. Leaves all other attributes unchanged."""
        self._mingus_chord = m_first_inversion(self._mingus_chord)
        self.note_list = get_notes_for_mingus_keys(self.matched_key_type, self._mingus_chord,
                                                   self.note_prototype, self.note_type, self.octave,
                                                   validate=False)

    def invert_second_inversion(self):
        """Modifies this Chord's note_list to its second inversion. Leaves all other attributes unchanged."""
        self._mingus_chord = m_second_inversion(self._mingus_chord)
        self.note_list = get_notes_for_mingus_keys(self.matched_key_type, self._mingus_chord,
                                                   self.note_prototype, self.note_type, self.octave,
                                                   validate=False)

    def invert_third_inversion(self):
        """Modifies this Chord's note_list to its third inversion. Leaves all other attributes unchanged."""
        self._mingus_chord = m_third_inversion(self._mingus_chord)
        self.note_list = get_notes_for_mingus_keys(self.matched_key_type, self._mingus_chord,
                                                   self.note_prototype, self.note_type, self.octave,
                                                   validate=False)

    @staticmethod
    def copy(source_chord: 'Chord') -> 'Chord':
        return Chord(chord_cls=source_chord.chord_type,
                     note_prototype=source_chord.note_prototype,
                     note_cls=source_chord.note_type,
                     octave=source_chord.octave,
                     key=source_chord.key,
                     scale_cls=source_chord.scale_type,
                     performance_attrs=source_chord.performance_attrs)

    @staticmethod
    def copy_first_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            first inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        # noinspection PyProtectedMember
        mingus_chord = m_first_inversion(source_chord._mingus_chord)
        chord.note_list = get_notes_for_mingus_keys(source_chord.matched_key_type, mingus_chord,
                                                    source_chord.note_prototype, source_chord.note_type,
                                                    source_chord.octave, validate=False)
        return chord

    @staticmethod
    def copy_second_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            second inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        # noinspection PyProtectedMember
        mingus_chord = m_second_inversion(source_chord._mingus_chord)
        chord.note_list = get_notes_for_mingus_keys(source_chord.matched_key_type, mingus_chord,
                                                    source_chord.note_prototype, source_chord.note_type,
                                                    source_chord.octave, validate=False)
        return chord

    @staticmethod
    def copy_third_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            third inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        # noinspection PyProtectedMember
        mingus_chord = m_third_inversion(source_chord._mingus_chord)
        chord.note_list = get_notes_for_mingus_keys(source_chord.matched_key_type, mingus_chord,
                                                    source_chord.note_prototype, source_chord.note_type,
                                                    source_chord.octave, validate=False)
        return chord

    def transpose(self, interval: int):
        # Don't validate because Note.transpose() validates
        for note in self.note_list:
            note.transpose(interval)

    @staticmethod
    def copy_transpose(source_chord: 'Chord', interval: int) -> 'Chord':
        chord = Chord.copy(source_chord)
        chord.transpose(interval)
        return chord

    def make_ostinato(self, init_start_time: Union[float, int], start_time_interval: Union[float, int]):
        # Don't validate because Note.start() validates
        self.note_list[0].start = init_start_time
        last_start = init_start_time
        for note in self.note_list[1:]:
            note.start = last_start + start_time_interval
            last_start = note.start

    @staticmethod
    def copy_ostinato(source_chord: 'Chord', init_start_time: Union[float, int],
                      start_time_interval: Union[float, int]) -> 'Chord':
        # Don't validate because Note.start() validates
        chord = Chord.copy(source_chord)
        chord.make_ostinato(init_start_time, start_time_interval)
        return chord
