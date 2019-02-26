# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapters.csound_note import CSoundNote
from omnisound.note.containers.measure import NoteDur, Swing
from omnisound.note.containers.note_sequence import NoteSequence

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1
SWING_FACTOR = 0.5


@pytest.fixture
def note_sequence():
    note = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)
    note_1 = CSoundNote.copy(note)
    note_2 = CSoundNote.copy(note)
    note_2.start += DUR
    note_3 = CSoundNote.copy(note)
    note_3.start += (DUR * 2)
    note_4 = CSoundNote.copy(note)
    note_4.start += (DUR * 3)
    note_list = [note_1, note_2, note_3, note_4]
    return NoteSequence(note_list)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR)


def test_swing_on_off(swing):
    # Default is swing off
    assert not swing.is_swing_on()
    # Can override default
    swing_2 = Swing(swing_on=True, swing_factor=SWING_FACTOR, swing_direction=Swing.SwingDirection.Forward)
    assert swing_2.is_swing_on()
    # Can toggle with methods
    swing_2.swing_off()
    assert not swing_2.is_swing_on()
    swing_2.swing_on()
    assert swing_2.is_swing_on()


def test_swing_forward(note_sequence, swing):
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    swing.swing_on().apply_swing(note_sequence, Swing.SwingDirection.Forward)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_reverse(note_sequence, swing):
    expected_swing_note_starts = [0.0, .125, 0.25, 0.375]
    swing.swing_on().apply_swing(note_sequence, Swing.SwingDirection.Reverse)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_both(note_sequence, swing):
    expected_swing_note_starts = [(0.0, 0.0), (0.125, 0.375), (0.25, 0.75), (0.375, 1.125)]
    swing.swing_on().apply_swing(note_sequence, Swing.SwingDirection.Both)
    actual_note_starts = [note.start for note in note_sequence]
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values, either start += (swing_factor * start) or
    # start -= (swing_factor * start)
    for i, actual_note_start in enumerate(actual_note_starts):
        assert actual_note_start in expected_swing_note_starts[i]


if __name__ == '__main__':
    pytest.main(['-xrf'])
