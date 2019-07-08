# Copyright 2018 Mark S. Weiss

from enum import Enum

import mingus.core.scales as m_scales
from mingus.core.keys import major_keys, minor_keys

NUM_NOTES_IN_OCTAVE = 11


class MajorKey(Enum):
    C = major_keys[7].upper()
    C_s = major_keys[14].upper()
    D_f = major_keys[2].upper()
    D = major_keys[9].upper()
    # Special case. This key is validly part of Major triads and other Major scale chords
    # e.g. - E.G#.B. Of course this is equivalent to E.Ab.B, but it is returned as 'G#'
    # which it is not included in the Mingus major_keys. So add it manually.
    D_s = 'D#'
    E_f = major_keys[4].upper()
    E = major_keys[11].upper()
    F = major_keys[6].upper()
    F_s = major_keys[13].upper()
    G_f = major_keys[1].upper()
    G = major_keys[8].upper()
    # Another special case
    G_s = 'G#'
    A_f = major_keys[3].upper()
    A = major_keys[10].upper()
    A_s = 'A#'
    B_f = major_keys[5].upper()
    B = major_keys[12].upper()
    C_f = major_keys[0].upper()


class MinorKey(Enum):
    C = minor_keys[4].upper()
    C_S = minor_keys[11].upper()
    D = minor_keys[6].upper()
    D_S = minor_keys[13].upper()
    E_F = minor_keys[1].upper()
    E = minor_keys[8].upper()
    E_S = minor_keys[13].upper()
    F = minor_keys[3].upper()
    F_S = minor_keys[10].upper()
    G = minor_keys[5].upper()
    G_S = minor_keys[12].upper()
    A_F = minor_keys[0].upper()
    A = minor_keys[7].upper()
    A_S = minor_keys[14].upper()
    B_F = minor_keys[2].upper()
    B = minor_keys[9].upper()


class DiatonicWrapper(m_scales.Diatonic):
    def __init__(self, key, octave=None, semitones=None):
        """
        This mingus scale takes a tuple of semitone values indicating which intervals should be
        half-steps. (3, 7) is neutral and returns C-Major intervals. There isn't documentation as to why.
        This wrapper defaults to this neutral behavior and hides this additional arg so that all the types
        mapped in the HarmonicScale enum have the same signature.

        Clients can pass semitones as an additional argument to override this default behavior, but it requires
        manual work rather than having the Scale class below hydrate the notes in a NoteSequence automatically.
        """
        semitones = semitones or (3, 7)
        super(DiatonicWrapper, self).__init__(key, semitones, octaves=octave)


class HarmonicScale(Enum):
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
