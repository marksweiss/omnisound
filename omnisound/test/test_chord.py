# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import HarmonicScale, MajorKey
import omnisound.note.adapters.csound_note as csound_note

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
HARMONIC_CHORD = HarmonicChord.MajorTriad

INSTRUMENT = 1
STARTS: List[float] = [1.0, 0.5, 1.5]
INT_STARTS: List[int] = [1, 5, 10]
START = STARTS[0]
INT_START = INT_STARTS[0]
DURS: List[float] = [1.0, 2.0, 2.5]
DUR = DURS[0]
AMPS: List[float] = [1.0, 2.0, 3.0]
AMP = AMPS[0]
PITCHES: List[float] = [1.0, 1.5, 2.0]
PITCH = PITCHES[0]

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0

NOTE_CLS = csound_note
ATTR_NAMES = csound_note.ATTR_NAMES
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(make_note=NOTE_CLS.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=num_attributes,
                                 attr_name_idx_map=attr_name_idx_map,
                                 attr_vals_defaults_map=attr_vals_defaults_map)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note(attr_name_idx_map=None, attr_vals_defaults_map=None,
          num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.make_note(make_note=csound_note.make_note,
                                  num_attributes=num_attributes,
                                  attr_name_idx_map=attr_name_idx_map,
                                  attr_vals_defaults_map=attr_vals_defaults_map)


@pytest.fixture
def note():
    return _note()


@pytest.fixture(scope='function')
def chord():
    harmonic_chord = HarmonicChord.MajorTriad
    return Chord(harmonic_chord=harmonic_chord,
                 octave=OCTAVE,
                 key=KEY,
                 get_pitch_for_key=NOTE_CLS.get_pitch_for_key,
                 make_note=NOTE_CLS.make_note,
                 num_attributes=len(NOTE_CLS.ATTR_NAMES),
                 attr_name_idx_map=ATTR_NAME_IDX_MAP)


def _assert_expected_pitches(chord_for_test, expected_pitches):
    for i, note in enumerate(chord_for_test):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_chord(chord):
    assert chord.harmonic_chord == HARMONIC_CHORD
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
