
from typing import Any, Mapping

import pytest

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import (HarmonicScale, MajorKey,
                                                     MinorKey)
import omnisound.note.adapters.csound_note as csound_note
import omnisound.note.adapters.midi_note as midi_note

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 9.01

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


def _note_sequence(attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    num_attributes = num_attributes or NUM_ATTRIBUTES
    note_sequence = NoteSequence(make_note=csound_note.make_note,
                                 num_notes=NUM_NOTES,
                                 num_attributes=num_attributes,
                                 attr_name_idx_map=attr_name_idx_map,
                                 attr_vals_defaults_map=attr_vals_defaults_map)
    return note_sequence


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note(attr_name_idx_map=None, attr_vals_defaults_map=None,
          attr_get_type_cast_map=None, num_attributes=None):
    attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    return csound_note.make_note(
            _note_sequence(
                    attr_name_idx_map=attr_name_idx_map,
                    attr_vals_defaults_map=attr_vals_defaults_map,
                    num_attributes=num_attributes).note_attr_vals[NOTE_SEQUENCE_IDX],
            attr_name_idx_map,
            attr_get_type_cast_map=attr_get_type_cast_map)


@pytest.fixture
def note():
    return _note()


def _scale(key=None, octave=None, harmonic_scale=None, note_type=None):
    key = key or KEY
    octave = octave or OCTAVE
    harmonic_scale = harmonic_scale or HARMONIC_SCALE
    note_type = note_type or csound_note
    return Scale(key=key, octave=octave, harmonic_scale=harmonic_scale,
                 get_pitch_for_key=note_type.get_pitch_for_key,
                 make_note=note_type.make_note,
                 num_attributes=NUM_ATTRIBUTES,
                 attr_name_idx_map=ATTR_NAME_IDX_MAP)


@pytest.fixture
def scale():
    return _scale()


def test_scale(note, scale):
    assert scale.key == KEY
    assert scale.octave == OCTAVE
    assert scale.harmonic_scale is HARMONIC_SCALE
    assert scale.keys == [MajorKey.C, MajorKey.D, MajorKey.E, MajorKey.F, MajorKey.G,
                          MajorKey.A, MajorKey.B]


def test_is_major_key_is_minor_key(note, scale):
    # Default note is C Major
    assert scale.is_major_key
    assert (not scale.is_minor_key)
    # MinorKey case
    scale_minor = _scale(key=MinorKey.C)
    assert not scale_minor.is_major_key
    assert scale_minor.is_minor_key


def test_get_pitch_for_key_csound(note, scale):
    # Expect that Scale.__init__() will populate the underlying NoteSequence with the notes for the `scale_cls`
    # and `key` (type of scale and root key), starting at the value of `octave` arg passed to Scale.__init__()
    expected_pitches = (4.01, 4.03, 4.05, 4.06, 4.08, 4.10, 4.12)
    pitches = [n.pitch for n in scale]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])

    # MinorKey case, HarmonicMinor class in Mingus
    scale_minor = _scale(key=MinorKey.C, harmonic_scale=HarmonicScale.HarmonicMinor)
    expected_pitches = (4.01, 4.03, 4.04, 4.06, 4.08, 4.09, 4.12)
    pitches = [n.pitch for n in scale_minor]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])


def test_get_pitch_for_key_midi():
    key = MajorKey.C
    scale_major = _scale(key=key, note_type=midi_note)
    expected_pitches = (60, 62, 64, 65, 67, 69, 71)
    pitches = [n.pitch for n in scale_major]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]

    key = MinorKey.C
    scale_minor = _scale(key=key, harmonic_scale=HarmonicScale.HarmonicMinor, note_type=midi_note)
    expected_pitches = (60, 62, 63, 65, 67, 68, 71)
    pitches = [n.pitch for n in scale_minor]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]


if __name__ == '__main__':
    pytest.main(['-xrf'])
