# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.chord import Chord
from aleatoric.chord_globals import KeyChord, KeyScaleChord, ScaleChord
from aleatoric.csound_note import CSoundNote
from aleatoric.scale_globals import HarmonicScale
from aleatoric.scale_globals import MajorKey


INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100
PITCH = 9.01

NOTE_CLS = CSoundNote
OCTAVE = 4
KEY = MajorKey.C
HARMONIC_SCALE = HarmonicScale.Major


@pytest.fixture
def note():
    return CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)


# note_prototype: Union[CSoundNote, FoxDotSupercolliderNote, MidiNote] = None,
# note_cls: Any = None,
# octave: int = None,
# key: Union[MajorKey, MinorKey] = None,
# scale_cls: HarmonicScale = None,
# performance_attrs: PerformanceAttrs = None):
@pytest.mark.parametrize('harmonic_chord', [KeyChord.MajorTriad, KeyScaleChord.Triad, ScaleChord.Tonic])
def test_chord(note, harmonic_chord):
    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE,
                  key=KEY, harmonic_scale=HARMONIC_SCALE)
    assert chord.harmonic_chord == harmonic_chord
    assert chord.note_prototype == note
    assert chord.note_type is NOTE_CLS
    assert chord.octave == OCTAVE
    assert chord.harmonic_scale is HARMONIC_SCALE


if __name__ == '__main__':
    pytest.main(['-xrf'])