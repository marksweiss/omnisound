# Copyright 2018 Mark S. Weiss

from numpy import array, copy as np_copy
import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import MajorKey

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 1.01

HARMONIC_CHORD = HarmonicChord.MajorTriad

NOTE_CLS = CSoundNote
ATTR_NAME_IDX_MAP = NOTE_CLS.ATTR_NAME_IDX_MAP
ATTR_VALS = array([float(INSTRUMENT), START, DUR, AMP, PITCH])
NOTE_SEQUENCE_NUM = 0
OCTAVE = 4
KEY = MajorKey.C


@pytest.fixture
def note():
    # Must construct each test Note with a new instance of underlying storage to avoid aliasing bugs
    attr_vals = np_copy(ATTR_VALS)
    return CSoundNote(attr_vals=attr_vals, attr_name_idx_map=ATTR_NAME_IDX_MAP,
                      seq_idx=NOTE_SEQUENCE_NUM)


@pytest.fixture(scope='function')
def chord():
    harmonic_chord = HarmonicChord.MajorTriad
    return Chord(harmonic_chord=harmonic_chord,
                 note_cls=NOTE_CLS,
                 num_attributes=len(NOTE_CLS.ATTR_NAMES),
                 attr_name_idx_map=ATTR_NAME_IDX_MAP,
                 octave=OCTAVE,
                 key=KEY)


def _assert_expected_pitches(chord_for_test, expected_pitches):
    for i, note in enumerate(chord_for_test):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_chord(chord):
    assert chord.harmonic_chord == HARMONIC_CHORD
    assert chord.note_type is NOTE_CLS
    assert chord.octave == OCTAVE
    # noinspection PyCallingNonCallable
    # Assert the number of notes in the sequence constructed is the number of notes in the underlying mingus chord
    assert len(chord) == len(HARMONIC_CHORD.value(KEY.name))
    for i, note in enumerate(chord):
        chord_key = Scale.MAJOR_KEY_REVERSE_MAP[chord.mingus_chord[i]]
        assert note.pitch == pytest.approx(NOTE_CLS.get_pitch_for_key(chord_key, OCTAVE))


def test_chord_mod_first_inversion(chord):
    chord.mod_first_inversion()
    expected_pitches = [4.05, 4.08, 4.01]
    _assert_expected_pitches(chord, expected_pitches)


def test_chord_mod_second_inversion(chord):
    chord.mod_second_inversion()
    expected_pitches = [4.08, 4.01, 4.05]
    _assert_expected_pitches(chord, expected_pitches)


def test_chord_mod_third_inversion(chord):
    chord.mod_third_inversion()
    expected_pitches = [4.01, 4.05, 4.08]
    _assert_expected_pitches(chord, expected_pitches)


def test_chord_copy_first_inversion(chord):
    inverted_chord = Chord.copy_first_inversion(chord)
    expected_pitches = [4.05, 4.08, 4.01]
    _assert_expected_pitches(inverted_chord, expected_pitches)


def test_chord_copy_second_inversion(chord):
    inverted_chord = Chord.copy_second_inversion(chord)
    expected_pitches = [4.08, 4.01, 4.05]
    _assert_expected_pitches(inverted_chord, expected_pitches)


def test_chord_copy_third_inversion(chord):
    inverted_chord = Chord.copy_third_inversion(chord)
    expected_pitches = [4.01, 4.05, 4.08]
    _assert_expected_pitches(inverted_chord, expected_pitches)


def test_mod_transpose(chord):
    expected_pitches = [4.02, 4.06, 4.09]
    chord.mod_transpose(interval=1)
    _assert_expected_pitches(chord, expected_pitches)


def test_copy_transpose(chord):
    transposed_chord = Chord.copy_transpose(chord, interval=1)
    expected_pitches = [4.02, 4.06, 4.09]
    _assert_expected_pitches(transposed_chord, expected_pitches)


def test_mod_ostinato(chord):
    init_start_time = 0.0
    start_time_interval = 0.1
    chord.mod_ostinato(init_start_time=init_start_time, start_time_interval=start_time_interval)
    expected_start_times = [0.0, 0.1, 0.2]
    for i, note in enumerate(chord):
        assert expected_start_times[i] == pytest.approx(note.start)


def test_copy_ostinato(chord):
    init_start_time = 0.0
    start_time_interval = 0.1
    ostinato_chord = Chord.copy_ostinato(chord, init_start_time=init_start_time,
                                         start_time_interval=start_time_interval)
    expected_start_times = [0.0, 0.1, 0.2]
    for i, note in enumerate(ostinato_chord):
        assert expected_start_times[i] == pytest.approx(note.start)


if __name__ == '__main__':
    pytest.main(['-xrf'])
