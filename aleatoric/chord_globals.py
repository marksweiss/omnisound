# Copyright 2018 Mark S. Weiss

from enum import Enum

import mingus.core.chords as m_chords


class Caller(object):
    """Hack function wrapper required because of Python behavior with Enum. If you assign an Enum name
       to a function name, and then reference the enum later, you get back a reference to the function
       pointer directly, not a reference to an enum member with a `name` and `value` property.
       This breaks usage of the enum that expects to have, well, a valid enum reference to a member
       declared with valid enum syntax and using valid types in the language. It seems like a "bug."

       Example:

       class KeyChord(Enum):
           MajorTriad = m_chords.major_triad

       x = KeyChord.MajorTriad
       type(x) => <function ...>

       class KeyChord(Enum):
           MajorTriad = Caller(m_chords.major_triad)

       x = KeyChord.MajorTriad
       type(x) => <Enum ...>
       x.name => 'MajorTriad'
       x.value => <Caller ...>
    """

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        return self.f(*args)


class KeyChord(Enum):
    """Chords based on intervals from a root key (note). These chords apply to any key with the exception
       that Major* chords are only musicall "valid" for Major scales and Minor* chords are only
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


class ScaleChord(Enum):
    Dominant = Caller(m_chords.dominant)
    Dominant7 = Caller(m_chords.dominant7)
    Mediant = Caller(m_chords.mediant)
    Mediant7 = Caller(m_chords.mediant7)
    Sevenths = Caller(m_chords.sevenths)
    Subdominant = Caller(m_chords.subdominant)
    Subdominant7 = Caller(m_chords.subdominant7)
    Submediant = Caller(m_chords.submediant)
    Submediant7 = Caller(m_chords.submediant7)
    Subtonic = Caller(m_chords.subtonic)
    Subtonic7 = Caller(m_chords.subtonic7)
    Supertonic = Caller(m_chords.supertonic)
    Supertonic7 = Caller(m_chords.supertonic7)
    Tonic = Caller(m_chords.tonic)
    Triads = Caller(m_chords.triads)


class KeyScaleChord(Enum):
    Seventh = Caller(m_chords.seventh)
    Triad = Caller(m_chords.triad)
