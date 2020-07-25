# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from omnisound.note.adapter.note import MakeNoteConfig
from omnisound.note.container.note_sequence import NoteSequence
from omnisound.note.generator.chord import Chord
from omnisound.note.generator.chord_globals import HarmonicChord
from omnisound.note.generator.scale import Scale
from omnisound.note.generator.scale_globals import HarmonicScale, MajorKey
import omnisound.note.adapter.csound_note as csound_note

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
ATTR_GET_TYPE_CAST_MAP = csound_note.ATTR_GET_TYPE_CAST_MAP

NOTE_SEQUENCE_IDX = 0

ATTR_NAMES = csound_note.ATTR_NAMES
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)


def _note_sequence(mn=None, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(num_notes=NUM_NOTES, mn=mn)
    return note_sequence


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


@pytest.fixture(scope='function')
def chord(make_note_config):
    harmonic_chord = HarmonicChord.MajorTriad
    return Chord(harmonic_chord=harmonic_chord,
                 octave=OCTAVE,
                 key=KEY,
                 mn=make_note_config)


def _assert_expected_pitches(chord_for_test, expected_pitches):
    for i, note in enumerate(chord_for_test):
        assert expected_pitches[i] == pytest.approx(note.pitch)


def test_chord(make_note_config, chord):
    assert chord.harmonic_chord == HARMONIC_CHORD
    assert chord.octave == OCTAVE
    # noinspection PyCallingNonCallable
    # Assert the number of notes in the sequence constructed is the number of notes in the underlying mingus chord
    assert len(chord) == len(HARMONIC_CHORD.value(KEY.name))
    for i, note in enumerate(chord):
        chord_key = Scale.MAJOR_KEY_REVERSE_MAP[chord.mingus_chord[i]]
        assert note.pitch == pytest.approx(make_note_config.get_pitch_for_key(chord_key, OCTAVE))


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
