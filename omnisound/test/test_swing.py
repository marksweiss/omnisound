# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.containers.measure import NoteDur, Swing
from omnisound.note.containers.note_sequence import NoteSequence
import omnisound.note.adapters.csound_note as csound_note


INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

SWING_FACTOR = 0.5

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 4
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
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)
    expected_swing_note_starts = [0.0, 0.375, 0.75, 1.125]
    swing.swing_on().apply_swing(note_sequence, Swing.SwingDirection.Forward)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_reverse(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)
    expected_swing_note_starts = [0.0, .125, 0.25, 0.375]
    swing.swing_on().apply_swing(note_sequence, Swing.SwingDirection.Reverse)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == actual_note_starts


def test_swing_both(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)
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
