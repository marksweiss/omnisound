
import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.adapters.midi_note import MidiNote
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import (HarmonicScale, MajorKey,
                                                     MinorKey)

INSTRUMENT = 1
START = 0.0
DUR = 1.0
AMP = 100
PITCH = 9.01

KEY = MajorKey.C
OCTAVE = 4
HARMONIC_SCALE = HarmonicScale.Major
NOTE_CLS = CSoundNote


@pytest.fixture
def note():
    return CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=float(AMP), pitch=PITCH)


@pytest.fixture
def scale(note):
    return Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, note_cls=NOTE_CLS, note_prototype=note)


def test_scale(note, scale):
    assert scale.key == KEY
    assert scale.octave == OCTAVE
    assert scale.note_type is NOTE_CLS
    assert scale.harmonic_scale is HARMONIC_SCALE
    assert scale.note_prototype == note
    assert scale.keys == [MajorKey.C, MajorKey.D, MajorKey.E, MajorKey.F, MajorKey.G,
                          MajorKey.A, MajorKey.B]


def test_is_major_key_is_minor_key(note, scale):
    # Default note is C Major
    assert scale.is_major_key
    assert not scale.is_minor_key

    # MinorKey case
    scale_minor = Scale(key=MinorKey.C, octave=OCTAVE, harmonic_scale=HarmonicScale.HarmonicMinor, note_cls=NOTE_CLS,
                        note_prototype=note)
    assert not scale_minor.is_major_key
    assert scale_minor.is_minor_key


def test_get_pitch_for_key_csound(note, scale):
    # Expect that Scale.__init__() will populate the underlying NoteSequence with the notes for the `scale_cls`
    # and `key` (type of scale and root key), starting at the value of `octave` arg passed to Scale.__init__()
    expected_pitches = (4.01, 4.03, 4.05, 4.06, 4.08, 4.10, 4.12)
    pitches = [n.pitch for n in scale.note_list]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])

    # MinorKey case, HarmonicMinor class in Mingus
    scale_minor = Scale(key=MinorKey.C, octave=OCTAVE, harmonic_scale=HarmonicScale.HarmonicMinor, note_cls=NOTE_CLS,
                        note_prototype=note)
    expected_pitches = (4.01, 4.03, 4.04, 4.06, 4.08, 4.09, 4.12)
    pitches = [n.pitch for n in scale_minor.note_list]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pytest.approx(pitches[i])


def test_get_pitch_for_key_midi():
    key = MajorKey.C
    octave = OCTAVE  # 4
    pitch_c4 = 48
    note_prototype = MidiNote(instrument=INSTRUMENT, time=START, duration=DUR, velocity=AMP,
                              pitch=pitch_c4)
    scale_major = Scale(key=key, octave=octave, harmonic_scale=HARMONIC_SCALE, note_cls=MidiNote,
                        note_prototype=note_prototype)
    expected_pitches = (60, 62, 64, 65, 67, 69, 71)
    pitches = [n.pitch for n in scale_major.note_list]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]

    key = MinorKey.C
    scale_minor = Scale(key=key, octave=octave, harmonic_scale=HarmonicScale.HarmonicMinor, note_cls=MidiNote,
                        note_prototype=note_prototype)
    expected_pitches = (60, 62, 63, 65, 67, 68, 71)
    pitches = [n.pitch for n in scale_minor.note_list]
    for i, expected_pitch in enumerate(expected_pitches):
        assert expected_pitch == pitches[i]


if __name__ == '__main__':
    pytest.main(['-xrf'])
