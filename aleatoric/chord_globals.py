# Copyright 2018 Mark S. Weiss

from enum import Enum

import mingus.core.chords as m_chords


class ChordCls(Enum):
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
    Seventh = m_chords.seventh
    LydianDominantSeventh = m_chords.lydian_dominant_seventh
    Eleventh = m_chords.eleventh
    HendrixChord = m_chords.hendrix_chord

