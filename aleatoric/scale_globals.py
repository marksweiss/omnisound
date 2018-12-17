# Copyright 2018 Mark S. Weiss

from enum import Enum

from mingus.core.keys import (major_keys, minor_keys)
import mingus.core.scales as m_scales


STEPS_IN_OCTAVE = 12


class MajorKey(Enum):
    C = major_keys[7]
    C_s = major_keys[14]
    D_f = major_keys[2]
    D = major_keys[9]
    E_f = major_keys[4]
    E = major_keys[11]
    F = major_keys[6]
    F_s = major_keys[13]
    G_f = major_keys[1]
    G = major_keys[8]
    A_f = major_keys[3]
    A = major_keys[10]
    B_f = major_keys[5]
    B = major_keys[12]
    C_f = major_keys[0]


class MinorKey(Enum):
    c = minor_keys[4]
    c_s = minor_keys[11]
    d = minor_keys[6]
    d_s = minor_keys[12]
    e_f = minor_keys[1]
    e = minor_keys[8]
    e_s = minor_keys[13]
    f = minor_keys[3]
    f_s = minor_keys[10]
    g = minor_keys[5]
    a_f = minor_keys[0]
    a = minor_keys[7]
    a_s = minor_keys[14]
    b_f = minor_keys[2]
    b = minor_keys[9]


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