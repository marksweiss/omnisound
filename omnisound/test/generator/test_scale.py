
import pytest

from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.container.note_sequence import NoteSequence
from omnisound.src.generator.scale import Scale
from omnisound.src.generator.scale_globals import HarmonicScale, MajorKey, MinorKey
import omnisound.src.note.adapter.csound_note as csound_note
import omnisound.src.note.adapter.midi_note as midi_note

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100.0
PITCH = 9.01

KEY = MajorKey
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major

ATTR_VAL_DEFAULT_MAP = {'instrument': float(INSTRUMENT),
                        'start': START,
                        'duration': DUR,
                        'amplitude': AMP,
                        'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 2
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          pitch_for_key=csound_note.pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_val_default_map=ATTR_VAL_DEFAULT_MAP,
                          attr_val_cast_map={})


def _note_sequence(mn=None, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VAL_DEFAULT_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence(num_notes=NUM_NOTES, mn=mn)


@pytest.fixture
def note_sequence(make_note_config):
    return _note_sequence(mn=make_note_config)


def _note(mn, attr_name_idx_map=None, attr_val_default_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_val_default_map = attr_val_default_map or ATTR_VAL_DEFAULT_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.new_note(mn)


@pytest.fixture
def note(make_note_config):
    return _note(mn=make_note_config)


def _scale(mn=None, key=None, octave=None, harmonic_scale=None):
    key = key or KEY
    octave = octave or OCTAVE
    harmonic_scale = harmonic_scale or HARMONIC_SCALE
    return Scale(key=key,
                 octave=octave,
                 harmonic_scale=harmonic_scale,
                 mn=mn)


@pytest.fixture
def scale(make_note_config):
    return _scale(mn=make_note_config)


def test_scale(note, scale):
    assert scale.key == KEY
    assert scale.octave == OCTAVE
    assert scale.harmonic_scale is HARMONIC_SCALE
    assert scale.keys == [MajorKey.C, MajorKey.D, MajorKey.E, MajorKey.F, MajorKey.G,
                          MajorKey.A, MajorKey.B]


def test_is_major_key_is_minor_key(make_note_config, note, scale):
    # Default note is C Major
    assert scale.is_major_key
    assert (not scale.is_minor_key)
    # MinorKey case
    scale_minor = _scale(mn=make_note_config, key=MinorKey)
    assert not scale_minor.is_major_key
    assert scale_minor.is_minor_key


def test_pitch_for_key_csound(make_note_config, note, scale):
    # Expect that Scale.__init__() will populate the underlying NoteSequence with the notes for the `scale_cls`
    # and `key` (type of scale and root key), starting at the value of `octave` arg passed to Scale.__init__()
    expected_pitches = (4.01, 4.03, 4.05, 4.06, 4.08, 4.10, 4.12)
    pitches = [n.pitch for n in scale]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])

    # MinorKey case, HarmonicMinor class in Mingus
    scale_minor = _scale(mn=make_note_config, key=MinorKey, harmonic_scale=HarmonicScale.HarmonicMinor)
    expected_pitches = (4.01, 4.03, 4.04, 4.06, 4.08, 4.09, 4.12)
    pitches = [n.pitch for n in scale_minor]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])


def test_pitch_for_key_midi(make_note_config):
    key = MajorKey
    make_note_config.cls_name = midi_note.CLASS_NAME
    make_note_config.make_note = midi_note.make_note
    make_note_config.pitch_for_key = midi_note.pitch_for_key
    scale_major = _scale(mn=make_note_config, key=key)
    expected_pitches = (60, 62, 64, 65, 67, 69, 71)
    pitches = [n.pitch for n in scale_major]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]

    key = MinorKey
    scale_minor = _scale(mn=make_note_config, key=key, harmonic_scale=HarmonicScale.HarmonicMinor)
    expected_pitches = (60, 62, 63, 65, 67, 68, 71)
    pitches = [n.pitch for n in scale_minor]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]


if __name__ == '__main__':
    pytest.main(['-xrf'])
