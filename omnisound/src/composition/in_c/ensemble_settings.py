# Copyright 2021 Mark S. Weiss

from omnisound.src.composition.in_c.settings_base import SettingsBase

class EnsembleSettings(SettingsBase):
    NUM_PLAYERS = 16,
    NUM_PHRASES = 53,
    DEFAULT_AMP = 30,

    # Phrase Index Parameters
    # Threshold number of phrases behind the furthest ahead any Player is allowed to slip.
    # If they are more than 3 behind the leader, they must advance.
    PHRASES_IDX_RANGE_THRESHOLD = 3,
    # Prob that the Ensemble will seek to have all Players play the same phrase
    #  on any one iteration through the Players
    UNISON_PROB = 0.9,
    # Threshold number of phrases apart within which all players
    #  must be for Ensemble to seek unison
    MAX_PHRASES_IDX_RANGE_FOR_SEEKING_UNISON = 2,

    # Crescendo/Descrescendo Parameters
    # Probability that the ensemble will de/crescendo in a unison (may be buggy)
    # TODO: bug is that code to build up crescendo over successive iterations isn't there
    #  and instead this just jumps the amplitude jarringly on one iteration
    CRESCENDO_PROB = 0.0,
    DECRESCENDO_PROB = 0.0,
    # Maximum de/increase in volume (in CSound scale) that notes can gain in crescendo
    #  pursued during a unison or in the final Conclusion
    CRESCENDO_MAX_AMP_RANGE = 1000,
    DECRESCENDO_MAX_AMP_RANGE = 1200,
    # Minimum number of iterations over which a de/crescendo will take to de/increase volume by crescendo amount
    # NOTE: Must be < max_crescendo_num_steps
    MIN_CRESCENDO_NUM_STEPS = 50,
    # Maximum number of iterations over which a de/crescendo will take to de/increase volume by crescendo amount
    # NOTE: Must be >= de/crescendo_max_amp_range
    MAX_CRESCENDO_NUM_STEPS = 70,

    # Conslusion Parameters
    # This is the ratio of steps in the Conclusion to the total steps before the Conclusion
    CONCLUSION_STEPS_RATIO = 0.1,
    # This extends the duration of the repetition of the last phrase
    #  curing the final coda.  At the start of the coda each player
    #  has its start time pushed ahead to be closer to the maximum
    #  so that they arrive at the end closer together.  This factor offsets the Player from
    #  repeating the last phrase until exactly reaching the Conclusion
    CONCLUSION_CUR_START_OFFSET_FACTOR = 0.05,
    # Maximum number of crescendo and decrescendo steps in the conclusion, supporting the
    #  Instruction indicating ensemble should de/crescendo 'several times'
    MAX_NUMBER_CONCLUDING_CRESCENDOS = 4
