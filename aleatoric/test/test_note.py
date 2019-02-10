# Copyright 2018 Mark S. Weiss

from typing import Any, List

import pytest
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as fd_sc_synth

from aleatoric.note.adapters.csound_note import FIELDS as csound_fields
from aleatoric.note.adapters.csound_note import CSoundNote
from aleatoric.note.adapters.foxdot_supercollider_note import \
    FIELDS as foxdot_fields
from aleatoric.note.adapters.foxdot_supercollider_note import \
    FoxDotSupercolliderNote
from aleatoric.note.adapters.midi_note import FIELDS as midi_fields
from aleatoric.note.adapters.midi_note import MidiInstrument, MidiNote
from aleatoric.note.adapters.note import NoteConfig
from aleatoric.note.adapters.performance_attrs import PerformanceAttrs
from aleatoric.note.adapters.rest_note import RestNote

INSTRUMENT = 1
FOX_DOT_INSTRUMENT = fd_sc_synth
MIDI_INSTRUMENT = MidiInstrument.Accordion
STARTS: List[float] = [0.0, 0.5, 1.0]
INT_STARTS: List[int] = [0, 5, 10]
START = STARTS[0]
INT_START = INT_STARTS[0]
DURS: List[float] = [0.0, 1.0, 2.5]
DUR = DURS[0]
AMPS: List[int] = [0, 1, 2]
AMP = AMPS[0]
PITCHES: List[float] = [0.0, 0.5, 1.0]
PITCH = PITCHES[0]
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

SCALE = 'chromatic'
OCTAVE = 4


def _setup_note_config(note_type: Any):
    note_config = None
    if note_type == CSoundNote:
        note_config = NoteConfig(csound_fields)
        note_config.instrument = INSTRUMENT
        note_config.start = START
        note_config.duration = DUR
        note_config.amplitude = int(AMP)
        note_config.pitch = PITCH
    if note_type == MidiNote:
        note_config = NoteConfig(midi_fields)
        note_config.instrument = MIDI_INSTRUMENT
        note_config.time = START
        note_config.duration = DUR
        note_config.velocity = int(AMP)
        note_config.pitch = int(PITCH)
    if note_type == FoxDotSupercolliderNote:
        note_config = NoteConfig(foxdot_fields)
        note_config.synth_def = FOX_DOT_INSTRUMENT
        note_config.delay = INT_START
        note_config.dur = DUR
        note_config.amp = float(AMP)
        note_config.degree = PITCH
    return note_config


def test_note():
    assert NOTE.instrument == INSTRUMENT
    assert NOTE.start == START
    assert NOTE.amp == AMP
    assert NOTE.dur == DUR
    assert NOTE.pitch == PITCH

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = CSoundNote(None, None, None, None, None)
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = CSoundNote(object(), object(), object(), object(), object())
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = CSoundNote(INSTRUMENT, START, DUR, AMP, PITCH, performance_attrs=object())


def test_note_eq_copy():
    note_2 = CSoundNote.copy(NOTE)
    assert NOTE == note_2

    octave = OCTAVE
    scale = SCALE
    fox_dot_note = FoxDotSupercolliderNote(synth_def=FOX_DOT_INSTRUMENT, delay=int(START), dur=DUR,
                                           amp=float(AMP), degree=PITCH, octave=octave, scale=scale)
    fox_dot_note_2 = FoxDotSupercolliderNote.copy(fox_dot_note)
    assert fox_dot_note == fox_dot_note_2


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs(start, duration, amplitude, pitch):
    note = CSoundNote(instrument=INSTRUMENT, start=start, duration=duration,
                      amplitude=int(amplitude), pitch=pitch)
    assert note.start == note.s() == start
    assert note.duration == note.dur == note.d() == duration
    assert note.amplitude == note.amp == note.a() == int(amplitude)
    assert note.pitch == note.p() == pitch
    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {int(amplitude)} {pitch:.2f}' == str(note)

    note = CSoundNote(instrument=INSTRUMENT, start=start, duration=duration,
                      amplitude=int(amplitude), pitch=pitch)
    note.s(start + 1).d(duration + 1).a(amplitude + 1).p(pitch + 1)
    assert note.s() == start + 1
    assert note.d() == duration + 1
    assert note.a() == amplitude + 1
    assert note.p() == pitch + 1


def test_csound_note_pitch_precision():
    note = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR,
                      amplitude=int(AMP), pitch=PITCH)
    assert note.pitch_precision == CSoundNote.SCALE_PITCH_PRECISION
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {int(AMP)} {PITCH:.2f}' == str(note)

    note.pitch_precision = 5
    assert note.pitch_precision == 5
    assert f'i {INSTRUMENT} {START:.5f} {DUR:.5f} {int(AMP)} {PITCH:.5f}' == str(note)


@pytest.mark.parametrize('degree', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('delay', INT_STARTS)
def test_foxdot_supercollider_note_attrs(delay, dur, amp, degree):
    synth_def = fd_sc_synth
    octave = OCTAVE
    scale = SCALE
    note = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
                                   amp=float(amp), degree=degree, octave=octave, scale=scale)
    assert note.delay == note.start == note.s() == delay
    assert note.dur == note.d() == dur
    assert note.amp == note.a() == float(amp)
    assert note.degree == note.pitch == note.p() == degree
    assert note.octave == octave
    assert note.scale == scale
    assert f'name: Note delay: {delay} dur: {dur} amp: {float(amp)} degree: {degree} octave: {octave} scale: {scale}' \
           == str(note)

    with pytest.raises(ValueError):
        scale = 'NOT_A_VALID_SCALE'
        _ = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
                                    amp=amp, degree=degree, octave=octave, scale=scale)

    scale = SCALE
    note = FoxDotSupercolliderNote(synth_def=synth_def, delay=delay, dur=dur,
                                   amp=float(amp), degree=degree, octave=octave, scale=scale)
    note.s(delay + 1).d(dur + 1).a(float(amp + 1)).p(degree + 1)
    assert note.s() == delay + 1
    assert note.d() == dur + 1
    assert note.a() == amp + 1
    assert note.p() == degree + 1


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('velocity', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('time', STARTS)
def test_midi_note_attrs(time, duration, velocity, pitch):
    note = MidiNote(instrument=INSTRUMENT, time=time, duration=duration,
                    velocity=int(velocity), pitch=int(pitch))
    assert note.time == note.start == note.s() == time
    assert note.duration == note.dur == note.d() == duration
    assert note.velocity == note.amp == note.a() == int(velocity)
    assert note.pitch == note.p() == int(pitch)
    expected_str_note = (f'name: Note instrument: {INSTRUMENT} time: {time} duration: {duration} '
                         f'velocity: {int(velocity)} pitch: {int(pitch)} channel: 1')
    assert expected_str_note == str(note)

    note = MidiNote(instrument=INSTRUMENT, time=time, duration=duration,
                    velocity=int(velocity), pitch=int(pitch))
    new_pitch = int(pitch + 1.0)
    note.s(time + 1).d(duration + 1).a(velocity + 1).p(new_pitch)
    assert note.s() == time + 1
    assert note.d() == duration + 1
    assert note.a() == velocity + 1
    assert note.p() == new_pitch


def test_note_config():
    note_config = _setup_note_config(CSoundNote)
    note = CSoundNote(**note_config.as_dict())
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(CSoundNote)
    note = CSoundNote(*note_config.as_list())
    assert note.instrument == INSTRUMENT
    assert note.start == START
    assert note.amplitude == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(MidiNote)
    note = MidiNote(**note_config.as_dict())
    assert note.instrument == MIDI_INSTRUMENT.value
    assert note.time == START
    assert note.velocity == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(MidiNote)
    note = MidiNote(*note_config.as_list())
    assert note.instrument == MIDI_INSTRUMENT.value
    assert note.time == START
    assert note.velocity == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(FoxDotSupercolliderNote)
    note = FoxDotSupercolliderNote(**note_config.as_dict())
    assert note.synth_def == FOX_DOT_INSTRUMENT
    assert note.degree == START
    assert note.amp == AMP
    assert note.delay == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(FoxDotSupercolliderNote)
    note = FoxDotSupercolliderNote(*note_config.as_list())
    assert note.synth_def == FOX_DOT_INSTRUMENT
    assert note.degree == START
    assert note.amp == AMP
    assert note.delay == DUR
    assert note.pitch == PITCH


def test_rest():
    rest_note = RestNote(instrument=INSTRUMENT, start=START, dur=DUR, pitch=PITCH)
    assert rest_note.amp == 0.0


if __name__ == '__main__':
    pytest.main(['-xrf'])
