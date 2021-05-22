# Copyright 2021 Mark S. Weiss

ENSEMBLE_SETTINGS = {
    'num_players': 8,
    # Threshold number of phrases behind the furthest ahead any Player is allowed to slip.
    # If they are more than 3 behind the leader, they must advance.
    'phrases_idx_range_threshold': 3,
    # Prob that the Ensemble will seek to have all Players play the same phrase
    #  on any one iteration through the Players
    'unison_prob_factor': 0.2,
    # Threshold number of phrases apart within which all players
    #  must be for Ensemble to seek unison
    'max_phrases_idx_range_for_seeking_unison': 3,
    # Probability that the ensemble will de/crescendo in a unison (may be buggy)
    # TODO: bug is that code to build up crescendo over successive iterations isn't there
    #  and instead this just jumps the amplitude jarringly on one iteration
    'crescendo_prob_factor': 0.0,
    'diminuendo_prob_factor': 0.0,
    # Maximum de/increase in volume (in CSound scale) that notes can gain in crescendo
    #  pursued during a unison or in the final Conclusion
    'max_amp_range_for_seeking_crescendo': 1000,
    'max_amp_range_for_seeking_diminuendo': 1200,
    # Parameters governing the Conclusion
    # This is the ratio of steps in the Conclusion to the total steps before the Conclusion
    'conclusion_steps_ratio': 0.1,
    # This extends the duration of the repetition of the last phrase
    #  curing the final coda.  At the start of the coda each player
    #  has its start time pushed ahead to be closer to the maximum
    #  so that they arrive at the end closer together.  This factor offsets the Player from
    #  repeating the last phrase until exactly reaching the Conclusion
    'conclusion_cur_start_offset_factor': 0.05,
    # Maximum number of crescendo and decrescendo steps in the conclusion, supporting the
    #  Instruction indicating ensemble should de/crescendo 'several times'
    'max_number_concluding_crescendos': 4
}
