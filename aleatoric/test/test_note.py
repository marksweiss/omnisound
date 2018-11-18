# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from aleatoric.note import CSoundNote, Note, RestNote

STARTS: List[float] = [0.0, 0.5, 1.0]
DURS: List[float] = [0.0, 1.0, 2.5]
AMPS: List[float] = [0.0, 0.5, 1.0]
PITCHES: List[float] = [0.0, 0.5, 1.0]
INSTRUMENT = 1


def test_note_no_args():
    with pytest.raises(ValueError) as excinfo:
        _ = Note()
        print(excinfo.value)


def test_note_invalid_args():
    with pytest.raises(ValueError) as excinfo:
        _ = Note(start=None, dur=None, amp=None, pitch=None)
        print(excinfo.value)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_note(start, dur, amp, pitch):
    note = Note(start=start, dur=dur, amp=amp, pitch=pitch)
    assert note.start == start
    assert note.dur == dur
    assert note.amp == amp
    assert note.pitch == pitch


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_rest(start, dur, amp, pitch):
    rest = RestNote(start=start, dur=dur, amp=amp, pitch=pitch)
    assert rest.amp == RestNote.REST_AMP


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('velocity', AMPS)
@pytest.mark.parametrize('duration', DURS)
@pytest.mark.parametrize('time', STARTS)
def test_csound_note(time, duration, velocity, pitch):
    note = CSoundNote(time=time, duration=duration, velocity=velocity, pitch=pitch, instrument=INSTRUMENT)
    assert note.time == note.start == time
    assert note.duration == note.dur == duration
    assert note.velocity == note.amp == velocity
    assert note.pitch == pitch
    assert f'i {INSTRUMENT} {time:.5f} {duration:.5f} {velocity} {pitch:.5f}' == str(note)


if __name__ == '__main__':
    pytest.main(['-xrf'])
