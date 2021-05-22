# Copyright 2021 Mark S. Weiss

from random import random

class PlayerSettings:
    # The most important factor governing advance of Players through phrases this is simply
    #  the percentage prob that they advance on any given iteration
    PHRASE_ADVANCE_PROB = 0.28

    # Player Phrase Phase
    # Tunable parms for shifting playing of current phrase out of its current
    #  phase and also to shift it more in alignment.  Shift simple pre-pends
    #  a rest Note to current phrase before writing it to Score.  Supports
    #  score directive to adjust phase and another to move in and out of phase
    #  during a performance
    # Percentage prob that a Player will adjust phase on any given iteration
    ADJ_PHASE_PROB_FACTOR = 0.07
    # Supports Instruction that Player this is too often in alignment should favor
    #  trying to be out of phase a bit more. If Player hasnt adjusted phase
    #  this many times or more then adj_phase_prob_increase_factor will be applied
    ADJ_PHASE_COUNT_THRESHOLD = 1
    ADJ_PHASE_PROB_INCREASE_FACTOR = 2.0
    # The length of the rest Note (in seconds) inserted if a Player is adjusting its phase
    PHASE_ADJ_DUR = 0.55
    # Prob that a Player will seek unison on any given iteration.  The idea is that
    #  to seek unison the Ensemble and all the Players must seek unison
    UNISON_PROB_FACTOR = 0.95

    # Player Rest/Play
    # Tunable parms for probability that Player will rest rather than playing a note.
    # Supports score directive to listen as well as play and not always play
    # Prob that a Player will try to rest on a given iteration (not play)
    REST_PROB_FACTOR = 0.1
    # Factor multiplied by rest_prob_factor if the Player is already at rest
    STAY_AT_REST_PROB_FACTOR = 1.5

    # Player Volume Adjusment De/Crescendo
    # Tunable parms for adjusting volume up and down and prob of making
    #  an amp adjustment. Supports score directive to have crescendos and
    #  decrescendos in the performance
    # Threshold for the ratio of this Players average amp for its current phrase
    #  to the max average amp among all the Players. Ratio above/below this means the Player
    #  will raise/lower its amp by amp_de/crescendo_adj_factor
    AMP_ADJ_CRESCENDO_RATIO_THRESHOLD = 0.8
    AMP_CRESCENDO_ADJ_FACTOR = 1.1
    AMP_ADJ_DIMINUENDO_RATIO_THRESHOLD = 1.2
    AMP_DIMINUENDO_ADJ_FACTOR = 0.9
    # Prob that a Player is seeking de/crescendo
    CRESCENDO_PROB_FACTOR = 0.5
    DIMINUENDO_PROB_FACTOR = 0.5

    # Player Transpose
    # Tunable parms for transposing the playing of a phrase.  Suppports score directive
    #  to transpose as desired.
    # Prob that a Player will seek to transpose its current phrase
    TRANSPOSE_PROB_FACTOR = 0.2
    # Number of octaves to transpose if the Player does do so
    # Amount that represents an octave in backend being used to render notes (1.0 in CSound 12 in MIDI)
    TRANSPOSE_SHIFT = 1.0
    # Sadly we need this also because CSound is float type and MIDI is int type (0.0 or 0)
    TRANSPOSE_NO_SHIFT = 0.0
    # Factor for shift down likewise (1.0 in CSound 1 in MIDI)
    TRANSPOSE_SHIFT_DOWN_FACTOR = -1.0
    # Factor for shift up likewise (1.0 in CSound 1 in MIDI)
    TRANSPOSE_SHIFT_UP_FACTOR = 1.0
    # From the Instructions = Transposing down by octaves works best on the patterns containing notes of long durations.
    # Minimum average duration of notes in a phrase for that phrase to be more likely
    #  to transpose down rather than up
    TRANSPOSE_DOWN_PROB_FACTOR = 0.5
    # Minimum average duration of notes in a phrase for that phrase to be more likely
    #  to transpose down rather than up
    TRANSPOSE_DOWN_DUR_THRESHOLD = 2.0

    # Misc
    # Give notes a bit of variance in start time and duration. If not overdone
    #  gives a more human feel.  A tiny bit goes a long long way ...
    # Use standard Aleatoric implementation in lib/util.rb
    # swing(base_val num_steps swing_step)
    #  returns a factor to multiply note.duration and note.start by
    #  base_val - the smallest possible swing factor
    #  num_steps - the number of values incremented up from the base_val
    #  swing_step - the size of each step value increment
    # So example = swing(0.98 5 0.01) -> swing range with the discrete values [0.98 0.99 1.0 1.01 1.02]
    SWING_BASE_VAL = 0.999
    SWING_NUM_STEPS = 3
    SWING_STEP_SIZE = 0.001

    # Convenience for In_C_Players
    NUM_PHRASES = 53

    @staticmethod
    def meets_condition(threshold: float) -> bool:
        return random() < threshold
