# Copyright 2018 Mark S. Weiss

from typing import Any, Mapping, Union

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import MajorKey, MinorKey
from omnisound.utils.mingus_utils import set_notes_pitches_to_mingus_keys
from omnisound.utils.utils import (validate_type_choice,
                                   validate_types)
from mingus.core.chords import first_inversion as m_first_inversion
from mingus.core.chords import second_inversion as m_second_inversion
from mingus.core.chords import third_inversion as m_third_inversion


class Chord(NoteSequence):
    """Represents a musical Chord, that is a group of Notes that harmonically work together according to the rules
       of some harmonic system. It uses mingus-python to return lists of pitches as string names and
       sets Note pitches to the value for the `note_cls` for each key in the Chord.
       So a CMajor triad Chord for `note_cls` CSoundNote and `octave` = 4 will have three Notes
       with pitches 4.01, 4.05, and 4.08.
    """
    def __init__(self,
                 harmonic_chord: Any = None,
                 octave: int = None,
                 key: Union[MajorKey, MinorKey] = None,
                 get_pitch_for_key: Any = None,
                 make_note: Any = None,
                 num_attributes: int = None,
                 attr_name_idx_map: Mapping[str, int] = None,
                 attr_vals_defaults_map: Mapping[str, float] = None,
                 attr_get_type_cast_map: Mapping[str, Any] = None):
        validate_types(('harmonic_chord', harmonic_chord, HarmonicChord), ('octave', octave, int))

        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        # Note that this arg is not required so we may not be able to determine key type from it.
        # If we can't get key type from key, use the name of the Chord, which may be associated with
        # MinorKey. Otherwise default to MajorKey, because the mingus functions we use to return lists of string
        # names of keys return upper-case values valid for MajorKey
        matched, self.matched_key_type = validate_type_choice('key', key, (MajorKey, MinorKey))
        if not matched:
            if harmonic_chord is HarmonicChord and harmonic_chord.name.startswith('Minor'):
                self.matched_key_type = MinorKey
            else:
                self.matched_key_type = MajorKey

        # Assign attrs before completing validation because it's more convenient to check for required
        # attrs by using getattr(attr_name) after they have been assigned
        self.harmonic_chord = harmonic_chord
        self.octave = octave
        self.get_pitch_for_key = get_pitch_for_key
        self.num_attributes = num_attributes
        # Get the list of keys in the chord as string names from mingus
        self.key = key
        self.mingus_chord = harmonic_chord.value(self.key.name)

        # Construct the sequence of notes for the chord in the NoteSequence base class
        super(Chord, self).__init__(make_note=make_note,
                                    num_notes=len(self.mingus_chord),
                                    num_attributes=num_attributes,
                                    attr_name_idx_map=attr_name_idx_map,
                                    attr_vals_defaults_map=attr_vals_defaults_map,
                                    attr_get_type_cast_map=attr_get_type_cast_map)

        # Convert to Notes for this chord's note_type with pitch assigned for the key in the chord
        self._mingus_key_to_key_enum_mapping = Scale.KEY_MAPS[self.matched_key_type.__name__]
        set_notes_pitches_to_mingus_keys(self.matched_key_type,
                                         self.mingus_chord,
                                         self._mingus_key_to_key_enum_mapping,
                                         self,
                                         self.get_pitch_for_key,
                                         self.octave,
                                         validate=False)

    def mod_first_inversion(self):
        """Modifies this Chord's note_list to its first inversion. Leaves all other attributes unchanged."""
        self.mingus_chord = m_first_inversion(self.mingus_chord)
        set_notes_pitches_to_mingus_keys(self.matched_key_type,
                                         self.mingus_chord,
                                         self._mingus_key_to_key_enum_mapping,
                                         self,
                                         self.get_pitch_for_key,
                                         self.octave,
                                         validate=False)

    def mod_second_inversion(self):
        """Modifies this Chord's note_list to its second inversion. Leaves all other attributes unchanged."""
        self.mingus_chord = m_second_inversion(self.mingus_chord)
        set_notes_pitches_to_mingus_keys(self.matched_key_type,
                                         self.mingus_chord,
                                         self._mingus_key_to_key_enum_mapping,
                                         self,
                                         self.get_pitch_for_key,
                                         self.octave,
                                         validate=False)

    def mod_third_inversion(self):
        """Modifies this Chord's note_list to its third inversion. Leaves all other attributes unchanged."""
        self.mingus_chord = m_third_inversion(self.mingus_chord)
        set_notes_pitches_to_mingus_keys(self.matched_key_type,
                                         self.mingus_chord,
                                         self._mingus_key_to_key_enum_mapping,
                                         self,
                                         self.get_pitch_for_key,
                                         self.octave,
                                         validate=False)

    @staticmethod
    def copy_first_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            first inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        set_notes_pitches_to_mingus_keys(source_chord.matched_key_type,
                                         m_first_inversion(source_chord.mingus_chord),
                                         source_chord._mingus_key_to_key_enum_mapping,
                                         chord,
                                         source_chord.get_pitch_for_key,
                                         source_chord.octave,
                                         validate=False)
        return chord

    @staticmethod
    def copy_second_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            second inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        set_notes_pitches_to_mingus_keys(source_chord.matched_key_type,
                                         m_second_inversion(source_chord.mingus_chord),
                                         source_chord._mingus_key_to_key_enum_mapping,
                                         chord,
                                         source_chord.get_pitch_for_key,
                                         source_chord.octave,
                                         validate=False)
        return chord

    @staticmethod
    def copy_third_inversion(source_chord: 'Chord') -> 'Chord':
        """Copy constructor that creates a new Chord using the attributes of this Chord with a note_list
            that is generated from copies from this Chord's note_prototype, with pitches which are the
            third inversion of the keys in this Chord.
        """
        chord = Chord.copy(source_chord)
        set_notes_pitches_to_mingus_keys(source_chord.matched_key_type,
                                         m_third_inversion(source_chord.mingus_chord),
                                         source_chord._mingus_key_to_key_enum_mapping,
                                         chord,
                                         source_chord.get_pitch_for_key,
                                         source_chord.octave,
                                         validate=False)
        return chord

    def mod_transpose(self, interval: int):
        """Modifies this Chord's note_list to transpose all notes by `interval`.
           Leaves all other attributes unchanged.
        """
        # Don't validate because Note.transpose() validates
        for note in self:
            note.transpose(interval)

    @staticmethod
    def copy_transpose(source_chord: 'Chord', interval: int) -> 'Chord':
        """Copy constructor which returns a note copied from this Chord, with all pitches
           of all Notes in the Chord transposed by `interval`. Leaves all other attributes unchanged.
        """
        chord = Chord.copy(source_chord)
        chord.mod_transpose(interval)
        return chord

    def mod_ostinato(self, init_start_time: Union[float, int], start_time_interval: Union[float, int]):
        """Modifies the Notes in the note_list of this Chord so that their start_times are spaced out, transforming
           the Notes from being a Chord to being an ostinato. The first Note.start_time is set to
           arg `init_start_time`. Each subsequent note will have `init_start_time` + (n * `start_time_interval`)
        """
        # Don't validate because Note.start() validates
        self[0].start = init_start_time
        last_start = init_start_time
        # noinspection PyTypeChecker
        note_list = [note for note in self]
        for note in note_list[1:]:
            note.start = last_start + start_time_interval
            last_start = note.start

    @staticmethod
    def copy_ostinato(source_chord: 'Chord', init_start_time: Union[float, int],
                      start_time_interval: Union[float, int]) -> 'Chord':
        """Copy constructor which returns a copy of this Chord with Notes modified so that their start_times
           are spaced out, transforming the Notes from being a Chord to being an ostinato.
           The first Note.start_time is set to arg `init_start_time`. Each subsequent note will have
           `init_start_time` + (n * `start_time_interval`)
        """
        # Don't validate because Note.start() validates
        chord = Chord.copy(source_chord)
        chord.mod_ostinato(init_start_time, start_time_interval)
        return chord

    @staticmethod
    def copy(source_chord: 'Chord') -> 'Chord':
        return Chord(harmonic_chord=source_chord.harmonic_chord,
                     octave=source_chord.octave,
                     key=source_chord.key,
                     get_pitch_for_key=source_chord.get_pitch_for_key,
                     make_note=source_chord.make_note,
                     num_attributes=source_chord.num_attributes,
                     attr_name_idx_map=source_chord.attr_name_idx_map,
                     attr_vals_defaults_map=source_chord.attr_vals_defaults_map,
                     attr_get_type_cast_map=source_chord.attr_get_type_cast_map)
