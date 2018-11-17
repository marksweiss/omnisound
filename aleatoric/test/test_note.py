# Copyright 2018 Mark S. Weiss

from typing import List

import pytest

from aleatoric.note import Note

STARTS: List[float] = [0.0, 0.5, 1.0]
DURS: List[float] = [0.0, 1.0, 2.5]
AMPS: List[float] = [0.0, 0.5, 1.0]
PITCHES: List[float] = [0.0, 0.5, 1.0]


def test_note_no_args():
    with pytest.raises(ValueError) as excinfo:
        note = Note()
        print(excinfo.value)


def test_note_invalid_args():
    with pytest.raises(ValueError) as excinfo:
        note = Note(start=None, dur=None, amp=None, pitch=None)
        print(excinfo.value)


@pytest.mark.parametrize('pitch', PITCHES)
@pytest.mark.parametrize('amp', AMPS)
@pytest.mark.parametrize('dur', DURS)
@pytest.mark.parametrize('start', STARTS)
def test_note(start, dur, amp, pitch):
    note = Note(start=start, dur=dur, amp=amp, pitch=pitch)
    assert note.start == start


if __name__ == '__main__':
    pytest.main(['-xrf'])
