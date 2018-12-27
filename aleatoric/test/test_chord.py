# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.chord import Chord
from aleatoric.chord_globals import HarmonicChord
from aleatoric.csound_note import CSoundNote
from aleatoric.scale_globals import HarmonicScale
from aleatoric.scale_globals import MajorKey


INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100
PITCH = 1.01

NOTE_CLS = CSoundNote
OCTAVE = 4
KEY = MajorKey.C
HARMONIC_SCALE = HarmonicScale.Major


@pytest.fixture
def note():
    return CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)


def test_chord(note):
    harmonic_chord = HarmonicChord.MajorTriad
    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    assert chord.harmonic_chord == harmonic_chord
    assert chord.note_prototype == note
    assert chord.note_type is NOTE_CLS
    assert chord.octave == OCTAVE


def test_chord_expected_pitches(note):
    harmonic_chord = HarmonicChord.MajorTriad
    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    expected_pitches = [4.01, 4.05, 4.08]
    assert len(chord)
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_chord_inversion(note):
    harmonic_chord = HarmonicChord.MajorTriad
    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    chord.mod_first_inversion()
    expected_pitches = [4.05, 4.08, 4.01]
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


if __name__ == '__main__':
    pytest.main(['-xrf'])