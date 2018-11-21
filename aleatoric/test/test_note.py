# Copyright 2018 Mark S. Weiss

from copy import deepcopy
from typing import List

import pytest
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as sc_sd_pluck

from aleatoric.note import (CSoundNoteAttrs, MidiNoteAttrs, Note, NoteAttrs, NoteGroup, PerformanceAttrs,
                            RestNote, SupercolliderNoteAttrs)

INSTRUMENT = 1
STARTS: List[float] = [0.0, 0.5, 1.0]
START = STARTS[0]
DURS: List[float] = [0.0, 1.0, 2.5]
DUR = DURS[0]
AMPS: List[float] = [0.0, 0.5, 1.0]
AMP = AMPS[0]
PITCHES: List[float] = [0.0, 0.5, 1.0]
PITCH = PITCHES[0]

NOTE_ATTRS = NoteAttrs(instrument=INSTRUMENT, start=START, dur=DUR, amp=AMP, pitch=PITCH)
PERFORMANCE_ATTRS = PerformanceAttrs()
ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int


def test_note():
    note = Note(NOTE_ATTRS)
    assert note.note_attrs.amp == NOTE_ATTRS.amp
    assert note.na.amp == NOTE_ATTRS.amp

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = Note(None, None)
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = Note(object())
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = Note(NOTE_ATTRS, performance_attrs=object())
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = Note(object(), performance_attrs=object())


def test_rest():
    rest = RestNote(NOTE_ATTRS)
    assert rest.note_attrs.amp == RestNote.REST_AMP


def test_note_group():
    note_attrs_2 = deepcopy(NOTE_ATTRS)
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(attr_name=ATTR_NAME, val=ATTR_VAL, attr_type=ATTR_TYPE)
    note_group = NoteGroup([NOTE_ATTRS, note_attrs_2], perf_attrs)
    assert note_group
    # All the note_attrs in the note_group have the same performance_attr
    assert note_group.note_attrs_list == note_group.nal == [NOTE_ATTRS, note_attrs_2]
    assert note_group.performance_attrs == note_group.pa == perf_attrs
    assert note_group.pa.test_attr == ATTR_VAL


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_note_attrs(start, dur, amp, pitch):
    note_attrs = NoteAttrs(instrument=INSTRUMENT, start=start, dur=dur, amp=amp, pitch=pitch)
    assert note_attrs.instrument == INSTRUMENT
    assert note_attrs.start == start
    assert note_attrs.dur == dur
    assert note_attrs.amp == amp
    assert note_attrs.pitch == pitch


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amplitude', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_csound_note_attrs(start, duration, amplitude, pitch):
    note_attrs = CSoundNoteAttrs(instrument=INSTRUMENT, start=start, duration=duration,
                                 amplitude=int(amplitude), pitch=pitch)
    assert note_attrs.start == start
    assert note_attrs.duration == duration
    assert note_attrs.amplitude == int(amplitude)
    assert note_attrs.pitch == pitch
    assert f'i {INSTRUMENT} {start:.5f} {duration:.5f} {int(amplitude)} {pitch:.5f}' == str(note_attrs)


@pytest.mark.parametrize('degree', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('delay', STARTS)
def test_supercollider_note_attrs(delay, dur, amp, degree):
    synth_def = sc_sd_pluck
    octave = 4
    scale = 'chromatic'
    note_attrs = SupercolliderNoteAttrs(synth_def=synth_def, delay=delay, dur=dur,
                                        amp=amp, degree=degree, oct=octave, scale=scale)
    assert note_attrs.delay == delay
    assert note_attrs.dur == dur
    assert note_attrs.amp == amp
    assert note_attrs.degree == degree
    assert note_attrs.oct == octave
    assert note_attrs.scale == scale
    assert f'name:  start: {delay} dur: {dur} amp: {amp} degree: {degree} oct: {octave} scale: {scale}' \
           == str(note_attrs)

    with pytest.raises(ValueError):
        scale = 'NOT_A_VALID_SCALE'
        _ = SupercolliderNoteAttrs(synth_def=synth_def, delay=delay, dur=dur,
                                   amp=amp, degree=degree, oct=octave, scale=scale)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('velocity', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('time', STARTS)
def test_midi_note_attrs(time, duration, velocity, pitch):
    note_attrs = MidiNoteAttrs(instrument=INSTRUMENT, time=time, duration=duration,
                               velocity=velocity, pitch=pitch)
    assert note_attrs.time == time
    assert note_attrs.duration == duration
    assert note_attrs.velocity == velocity
    assert note_attrs.pitch == pitch
    assert (f'name:  instrument: {INSTRUMENT} time: {time} duration: {duration} '
            f'velocity: {velocity} pitch: {pitch} channel: {note_attrs.DEFAULT_CHANNEL}') == str(note_attrs)


def test_performance_attrs_freeze_unfreeze():
    # Initial state is not frozen. User must explicitly freeze()
    perf_attrs = PerformanceAttrs()
    assert not perf_attrs.is_frozen()
    perf_attrs.freeze()
    assert perf_attrs.is_frozen()
    perf_attrs.unfreeze()
    assert not perf_attrs.is_frozen()


def test_performance_attrs_add_attr_set_attr():
    # Initial state is not frozen. User must explicitly freeze()
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    assert perf_attrs.test_attr == ATTR_VAL
    assert isinstance(perf_attrs.test_attr, ATTR_TYPE)

    new_attr_val = 200
    perf_attrs.safe_set_attr(ATTR_NAME, new_attr_val)
    # ATTR_NAME = 'test_attr'
    assert perf_attrs.test_attr == new_attr_val

    with pytest.raises(ValueError):
        perf_attrs.safe_set_attr('NOT_AN_ATTR_NAME', ATTR_VAL)
    assert perf_attrs.test_attr == new_attr_val

    with pytest.raises(ValueError):
        perf_attrs.safe_set_attr(ATTR_NAME, float(ATTR_VAL))
    assert perf_attrs.test_attr == new_attr_val


def test_performance_attrs_str():
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    assert f'{ATTR_NAME}: {ATTR_VAL}' == str(perf_attrs)
    perf_attrs.add_attr(ATTR_NAME + '_2', ATTR_VAL + 100, ATTR_TYPE)
    assert f'{ATTR_NAME}: {ATTR_VAL} {ATTR_NAME}_2: {ATTR_VAL + 100}' == str(perf_attrs)


def test_performance_attrs_dict():
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    assert {ATTR_NAME: ATTR_VAL} == perf_attrs.as_dict()

    new_attr_name = ATTR_NAME + '_2'
    new_attr_val = ATTR_VAL + 100
    perf_attrs.add_attr(new_attr_name, new_attr_val, ATTR_TYPE)
    assert {ATTR_NAME: ATTR_VAL, new_attr_name: new_attr_val} == perf_attrs.as_dict()


if __name__ == '__main__':
    pytest.main(['-xrf'])
