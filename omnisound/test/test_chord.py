# Copyright 2018 Mark S. Weiss

from numpy import array, copy as np_copy
import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale_globals import MajorKey

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 1.01

ATTR_VALS = array([float(INSTRUMENT), START, DUR, AMP, PITCH])
ATTR_NAME_IDX_MAP = {'instrument': 0, 'start': 1, 'dur': 2, 'amp': 3, 'pitch': 4}
NOTE_SEQUENCE_NUM = 0

NOTE_CLS = CSoundNote
OCTAVE = 4
KEY = MajorKey.C


@pytest.fixture
def note():
    # Must construct each test Note with a new instance of underlying storage to avoid aliasing bugs
    attr_vals = np_copy(ATTR_VALS)
    return CSoundNote(attr_vals=attr_vals, attr_name_idx_map=ATTR_NAME_IDX_MAP,
                      note_sequence_num=NOTE_SEQUENCE_NUM)


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


def test_chord_mod_inversion(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    chord.mod_first_inversion()
    expected_pitches = [4.05, 4.08, 4.01]
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    chord.mod_second_inversion()
    expected_pitches = [4.08, 4.01, 4.05]
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    chord.mod_third_inversion()
    expected_pitches = [4.01, 4.05, 4.08]
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_chord_copy_inversion(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    inverted_chord = Chord.copy_first_inversion(chord)
    expected_pitches = [4.05, 4.08, 4.01]
    for i, note in enumerate(inverted_chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    inverted_chord = Chord.copy_second_inversion(chord)
    expected_pitches = [4.08, 4.01, 4.05]
    for i, note in enumerate(inverted_chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    inverted_chord = Chord.copy_third_inversion(chord)
    expected_pitches = [4.01, 4.05, 4.08]
    for i, note in enumerate(inverted_chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_mod_transpose(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    expected_pitches = [4.02, 4.06, 4.09]
    chord.mod_transpose(interval=1)
    for i, note in enumerate(chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_copy_transpose(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    transposed_chord = Chord.copy_transpose(chord, interval=1)
    expected_pitches = [4.02, 4.06, 4.09]
    for i, note in enumerate(transposed_chord):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_mod_ostinato(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    init_start_time = 0.0
    start_time_interval = 0.1
    chord.mod_ostinato(init_start_time=init_start_time, start_time_interval=start_time_interval)
    expected_start_times = [0.0, 0.1, 0.2]
    for i, note in enumerate(chord):
        assert expected_start_times[i] == pytest.approx(note.start)


def test_copy_ostinato(note):
    harmonic_chord = HarmonicChord.MajorTriad

    chord = Chord(harmonic_chord=harmonic_chord, note_prototype=note, note_cls=NOTE_CLS, octave=OCTAVE, key=KEY)
    init_start_time = 0.0
    start_time_interval = 0.1
    ostinato_chord = Chord.copy_ostinato(chord, init_start_time=init_start_time,
                                         start_time_interval=start_time_interval)
    expected_start_times = [0.0, 0.1, 0.2]
    for i, note in enumerate(ostinato_chord):
        assert expected_start_times[i] == pytest.approx(note.start)


if __name__ == '__main__':
    pytest.main(['-xrf'])
