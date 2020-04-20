# Copyright 2018 Mark S. Weiss

from enum import Enum

import mingus.core.chords as m_chords

from omnisound.utils.utils import enum_to_str_key_dict


class Caller(object):
    """Hack function wrapper required because of Python behavior with Enum. If you assign an Enum name
       to a function name, and then reference the enum later, you get back a reference to the function
       pointer directly, not a reference to an enum member with a `name` and `value` property.
       This breaks usage of the enum that expects to have, well, a valid enum reference to a member
       declared with valid enum syntax and using valid types in the language. It seems like a "bug."

       Example:

       class HarmonicChord(Enum):
           MajorTriad = m_chords.major_triad

       x = HarmonicChord.MajorTriad
       type(x) => <function ...>

       class HarmonicChord(Enum):
           MajorTriad = Caller(m_chords.major_triad)

       x = HarmonicChord.MajorTriad
       type(x) => <Enum ...>
       x.name => 'MajorTriad'
       x.value => <Caller ...>
    """

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        return self.f(*args)


class HarmonicChord(Enum):
    """Chords based on intervals from a root key (note). These chords apply to any key with the exception
       that Major* chords are only musically "valid" for Major scales and Minor* chords are only
       musically "valid" for minor scales.
    """
    MajorTriad = Caller(m_chords.major_triad)
    MajorSixth = Caller(m_chords.major_sixth)
    MajorSeventh = Caller(m_chords.major_seventh)
    MajorNinth = Caller(m_chords.major_ninth)
    MajorThirteenth = Caller(m_chords.major_thirteenth)

    MinorTriad = Caller(m_chords.minor_triad)
    MinorSixth = Caller(m_chords.minor_sixth)
    MinorSeventh = Caller(m_chords.minor_seventh)
    MinorSeventhFlatFive = Caller(m_chords.minor_seventh_flat_five)
    MinorNinth = Caller(m_chords.minor_ninth)
    MinorEleventh = Caller(m_chords.minor_thirteenth)

    AugmentedTriad = Caller(m_chords.augmented_triad)
    AugmentedMajorSeventh = Caller(m_chords.augmented_major_seventh)
    AugmentedMinorSeventh = Caller(m_chords.augmented_minor_seventh)

    DiminishedTriad = Caller(m_chords.diminished_triad)
    DiminishedSeventh = Caller(m_chords.diminished_seventh)

    DominantFlatFive = Caller(m_chords.dominant_flat_five)
    DominantSixth = Caller(m_chords.dominant_sixth)
    DominantSeventh = Caller(m_chords.dominant_seventh)
    DominantNinth = Caller(m_chords.dominant_ninth)
    DominantFlatNinth = Caller(m_chords.dominant_flat_ninth)
    DominantSharpNinth = Caller(m_chords.dominant_sharp_ninth)
    DominantThirteenth = Caller(m_chords.dominant_thirteenth)

    SuspendedTriad = Caller(m_chords.suspended_triad)
    SuspendedSeventh = Caller(m_chords.suspended_seventh)
    SuspendedSecondTriad = Caller(m_chords.suspended_second_triad)
    SuspendedFourthTriad = Caller(m_chords.suspended_fourth_triad)
    SuspendedFourthNinth = Caller(m_chords.suspended_fourth_ninth)

    SixthNinth = Caller(m_chords.sixth_ninth)
    LydianDominantSeventh = Caller(m_chords.lydian_dominant_seventh)
    Eleventh = Caller(m_chords.eleventh)
    HendrixChord = Caller(m_chords.hendrix_chord)


HARMONIC_CHORD_DICT = enum_to_str_key_dict(HarmonicChord)
