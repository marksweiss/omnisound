# Copyright 2018 Mark S. Weiss

from enum import Enum

import mingus.core.chords as m_chords


class KeyChordCls(Enum):
    """Chords based on intervals from a root key (note). Thes chords apply to any key with the exception
       that Major* chords are only musicall "valid" for Major scales and Minor* chords are only
       musically "valid" for minor scales.
    """
    MajorTriad = m_chords.major_triad
    MajorSixth = m_chords.major_sixth
    MajorNinth = m_chords.major_ninth
    MajorThirteenth = m_chords.major_thirteenth
    MajorSeventh = m_chords.major_seventh

    MinorTriad = m_chords.minor_triad
    MinorSixth = m_chords.minor_sixth
    MinorSeventh = m_chords.minor_seventh
    MinorSeventhFlatFive = m_chords.minor_seventh_flat_five
    MinorNinth = m_chords.minor_ninth
    MinorEleventh = m_chords.minor_thirteenth

    AugmentedTriad = m_chords.augmented_triad
    AugmentedMajorSeventh = m_chords.augmented_major_seventh
    AugmentedMinorSeventh = m_chords.augmented_minor_seventh

    DiminishedTriad = m_chords.diminished_triad
    DiminishedSeventh = m_chords.diminished_seventh

    DominantFlatFive = m_chords.dominant_flat_five
    DominantSixth = m_chords.dominant_sixth
    DominantSeventh = m_chords.dominant_seventh
    DominantNinth = m_chords.dominant_ninth
    DominantFlatNinth = m_chords.dominant_flat_ninth
    DominantSharpNinth = m_chords.dominant_sharp_ninth
    DominantThirteenth = m_chords.dominant_thirteenth

    SuspendedTriad = m_chords.suspended_triad
    SuspendedSeventh = m_chords.suspended_seventh
    SuspendedSecondTriad = m_chords.suspended_second_triad
    SuspendedFourthTriad = m_chords.suspended_fourth_triad
    SuspendedFourthNinth = m_chords.suspended_fourth_ninth

    SixNinth = m_chords.sixth_ninth
    LydianDominantSeventh = m_chords.lydian_dominant_seventh
    Eleventh = m_chords.eleventh
    HendrixChord = m_chords.hendrix_chord


class ScaleChordCls(Enum):
    Dominant = m_chords.dominant
    Dominant7 = m_chords.dominant7
    Mediant = m_chords.mediant
    Mediant7 = m_chords.mediant7
    Sevenths = m_chords.sevenths
    Subdominant = m_chords.subdominant
    Subdominant7 = m_chords.subdominant7
    Submediant = m_chords.submediant
    Submediant7 = m_chords.submediant7
    Subtonic = m_chords.subtonic
    Subtonic7 = m_chords.subtonic7
    Supertonic = m_chords.supertonic
    Supertonic7 = m_chords.supertonic7
    Tonic = m_chords.tonic
    Triads = m_chords.triads


class KeyScaleChordCls(Enum):
    Seventh = m_chords.seventh
    Triad = m_chords.triad
