# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.csound_note import CSoundNote
from aleatoric.foxdot_supercollider_note import FoxDotSupercolliderNote
from aleatoric.midi_note import MidiNote
from aleatoric.scale import Scale
from aleatoric.scale_globals import MajorKey, MinorKey, ScaleCls


INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100
PITCH = 10.1
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

KEY = MajorKey.C
OCTAVE = 4
SCALE_CLS = ScaleCls.Major
NOTE_CLS = CSoundNote
SCALE = Scale(key=KEY, octave=OCTAVE, scale_cls=SCALE_CLS, note_cls=NOTE_CLS, note_prototype=NOTE)


def test_is_major_key_is_minor_key():
    assert SCALE.is_major_key
    assert not SCALE.is_minor_key

    # TODO MINOR KEYS ARE BROKEN
    # scale_minor = Scale(key=MinorKey.c, octave=OCTAVE, scale_cls=ScaleCls.HarmonicMinor, note_cls=NOTE_CLS,
    #                     note_prototype=NOTE)
    # assert not scale_minor.is_major_key
    # assert scale_minor.is_minor_key


# TODO TEST GET EXPECTED NOTES
def test_get_pitch_for_key():
    pass


if __name__ == '__main__':
    pytest.main(['-xrf'])

