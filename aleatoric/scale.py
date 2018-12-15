# Copyright 2018 Mark S. Weiss

"""
Key - a designated musical note with a name and degree (in some pitch system, e.g. Western Classical)
Octave - Keys may repeat in cycles, e.g. Western Classical piano keyboard. Octave is which cycle group the
  Key is in, e.g. (Key.C, 4) is the C starting the fourth cycle on the piano and is "Middle C"
Scale - a sequence of pitch intervals that together are recognized as harmonious
Pitch - a key translated to a (numerical) value that can be used by a back end. Each Note type owns a map
  of Key => Pitch for each tuple (Key, Octave)
"""

from enum import Enum
from typing import Union

from mingus.core.keys import major_keys, minor_keys
import mingus.core.scales as m_scales

from aleatoric.note import (CSoundNote, FoxDotSupercolliderNote, MidiNote, Note, NoteSequence, PerformanceAttrs)
from aleatoric.utils import (enum_to_dict_reverse_mapping, validate_type_choice, validate_types)


STEPS_IN_OCTAVE = 12


class MajorKey(Enum):
    C_f = major_keys[0]
    G_f = major_keys[1]
    D_f = major_keys[2]
    A_f = major_keys[3]
    E_f = major_keys[4]
    B_f = major_keys[5]
    F = major_keys[6]
    C = major_keys[7]
    G = major_keys[8]
    D = major_keys[9]
    A = major_keys[10]
    E = major_keys[11]
    B = major_keys[12]
    F_s = major_keys[13]
    C_s = major_keys[14]


class MinorKey(Enum):
    a_f = minor_keys[0]
    e_f = minor_keys[1]
    b_f = minor_keys[2]
    f = minor_keys[3]
    c = minor_keys[4]
    g = minor_keys[5]
    d = minor_keys[6]
    a = minor_keys[7]
    e = minor_keys[8]
    b = minor_keys[9]
    f_s = minor_keys[10]
    c_s = minor_keys[11]
    d_s = minor_keys[12]
    e_s = minor_keys[13]
    a_s = minor_keys[14]


class DiatonicWrapper(m_scales.Diatonic):
    def __init__(self, key, octave=None, semitones=None):
        """
        This mingus scale takes a tuple of semitone values indicating which intervals should be
        half-steps. (3, 7) is neutral and returns C-Major intervals. There isn't documentation as to why.
        This wrapper defaults to this neutral behavior and hides this additional arg so that all the types
        mapped in the ScaleCls enum have the same signature.

        Clients can pass semitones as an additional argument to override this default behavior, but it requires
        manual work rather than having the Scale class below hydrate the notes in a NoteSequenc automatically.
        """
        semitones = semitones or (3, 7)
        super(DiatonicWrapper, self).__init__(key, semitones, octaves=octave)


class ScaleCls(Enum):
    Aeolian = m_scales.Aeolian
    Bachian = m_scales.Bachian
    Chromatic = m_scales.Chromatic
    Diatonic = DiatonicWrapper
    Dorian = m_scales.Dorian
    HarmonicMajor = m_scales.HarmonicMajor
    HarmonicMinor = m_scales.HarmonicMinor
    Ionian = m_scales.Ionian
    Locrian = m_scales.Locrian
    Lydian = m_scales.Lydian
    Major = m_scales.Major
    MelodicMinor = m_scales.MelodicMinor
    MinorNeopolitican = m_scales.MinorNeapolitan
    Mixolydian = m_scales.Mixolydian
    NaturalMinor = m_scales.NaturalMinor
    Octatonic = m_scales.Octatonic
    Phrygian = m_scales.Phrygian
    WholeTone = m_scales.WholeTone


class Scale(NoteSequence):
    """Encapsualtes a musical Scale, which is a type of scale (an organization of intervals offset from a root key)
       and a root key. Uses mingus.scale to then retrieve the notes in the scale and provide methods to manage
       and generate Notes. Derives from NoteSequence so acts as a standard Note container.
    """
    MAJOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping('MajorKey', MajorKey)
    MINOR_KEY_REVERSE_MAP = enum_to_dict_reverse_mapping('MinorKey', MinorKey)
    KEY_MAPS = {MajorKey: MAJOR_KEY_REVERSE_MAP, MinorKey: MINOR_KEY_REVERSE_MAP}

    def __init__(self,
                 key: Union[MajorKey, MinorKey] = None,
                 octave: int = None,
                 scale_cls: ScaleCls = None,
                 note_cls: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote, Note] = None,
                 performance_attrs: PerformanceAttrs = None):
        # Use return value to detect which type of enum `key` is. Use this to determine which KEY_MAPPING
        # to use to convert the mingus key value (a string) to the enum key value (a member of MajorKey or MinorKey)
        _, matched_key_type = validate_type_choice('key', key, (MajorKey, MinorKey))
        # Validate args and set members
        validate_types(('octave', octave, int), ('scale_type', scale_cls, ScaleCls))
        validate_type_choice('note_type', note_cls, (CSoundNote, FoxDotSupercolliderNote, MidiNote, Note))
        self.key = key
        self.octave = octave
        self.scale_type = scale_cls
        self.note_type = note_cls
        self.is_major_key = matched_key_type == MajorKey
        self.is_minor_key = matched_key_type == MinorKey

        # Get the minus keys (pitches) for the musical scale (`scale_type`) with its root at `key` and
        # octave at `octave`. This returns a list of string values which match the `name`s of entries
        # in MajorKey and MinorKey enums.
        m_keys = scale_cls.value(key.name, octave=octave).ascending()

        # Construct a list of Notes from the mingus notes, setting their pitch to the pitch in the scale
        # converted to the value for the type of Note. Other attributes are set to Note defaults.
        # pitch logic is: convert string note from mingus string to pitch enum. The enum
        # and `octave` are args passed to `note_type.get_pitch()` for the note_type, which maps (key_enum, octave)
        # to pitch values for that note type.
        # e.g. CSoundNote.get_pitch(key=MajorKey.C, octave=4) -> 4.01: float
        key_mapping = Scale.KEY_MAPS[matched_key_type]
        note_list = [note_cls.get_pitch(key_mapping[m_key], self.octave) for m_key in m_keys]
        # Set this List[Note] in the base class for this NoteSequence
        super(Scale, self).__init__(note_list, performance_attrs=performance_attrs)