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

KEY = MajorKey.C
OCTAVE = 4
SCALE_CLS = ScaleCls.Major
NOTE_CLS = CSoundNote


@pytest.fixture('module')
def note():
    return CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)


@pytest.fixture(scope='module')
def scale(note):
    return Scale(key=KEY, octave=OCTAVE, scale_cls=SCALE_CLS, note_cls=NOTE_CLS, note_prototype=note)


def test_is_major_key_is_minor_key(note, scale):
    # Default note is C Major
    assert scale.is_major_key
    assert not scale.is_minor_key

    # MinorKey case
    scale_minor = Scale(key=MinorKey.C, octave=OCTAVE, scale_cls=ScaleCls.HarmonicMinor, note_cls=NOTE_CLS,
                        note_prototype=note)
    assert not scale_minor.is_major_key
    assert scale_minor.is_minor_key


# TODO TEST GET EXPECTED NOTES
def test_get_pitch_for_key(scale):
    pass


if __name__ == '__main__':
    pytest.main(['-xrf'])

