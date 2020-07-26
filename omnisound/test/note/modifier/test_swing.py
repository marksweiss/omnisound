# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapter.note import MakeNoteConfig
from omnisound.note.container.measure import NoteDur, Swing
from omnisound.note.container.note_sequence import NoteSequence
import omnisound.note.adapter.csound_note as csound_note


INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

SWING_RANGE = 0.1

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_NOTES = 4
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map={})


@pytest.fixture
def note_sequence(make_note_config):
    return NoteSequence(num_notes=NUM_NOTES, mn=make_note_config)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE)


def test_swing_on_off(swing):
    # Default is swing off
    assert not swing.is_swing_on()
    # Can override default
    swing_2 = Swing(swing_on=True, swing_range=SWING_RANGE, swing_direction=Swing.SwingDirection.Forward)
    assert swing_2.is_swing_on()
    # Can toggle with methods
    swing_2.set_swing_off()
    assert not swing_2.is_swing_on()
    swing_2.set_swing_on()
    assert swing_2.is_swing_on()


def test_swing_forward_fixed(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)

    expected_swing_note_starts = [note_sequence[0].start + SWING_RANGE,
                                  note_sequence[1].start + SWING_RANGE,
                                  note_sequence[2].start + SWING_RANGE,
                                  note_sequence[3].start + SWING_RANGE]
    swing.set_swing_on().apply_swing(note_sequence,
                                     Swing.SwingDirection.Forward,
                                     Swing.SwingJitterType.Fixed)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == pytest.approx(actual_note_starts)


def test_swing_forward_random(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)

    expected_swing_note_starts = [note_sequence[0].start + SWING_RANGE,
                                  note_sequence[1].start + SWING_RANGE,
                                  note_sequence[2].start + SWING_RANGE,
                                  note_sequence[3].start + SWING_RANGE]
    swing.set_swing_on().apply_swing(note_sequence,
                                     Swing.SwingDirection.Forward,
                                     Swing.SwingJitterType.Random)
    actual_note_starts = [note.start for note in note_sequence]
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values
    for i, actual_note_start in enumerate(actual_note_starts):
        assert actual_note_start <= expected_swing_note_starts[i]


def test_swing_reverse_fixed(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)

    # Note that the first note is expected to be 0.0 and not negative because apply_swing() catches this case
    # and assigns any negative note.start value to 0.0
    expected_swing_note_starts = [0.0,
                                  note_sequence[1].start - SWING_RANGE,
                                  note_sequence[2].start - SWING_RANGE,
                                  note_sequence[3].start - SWING_RANGE]
    swing.set_swing_on().apply_swing(note_sequence,
                                     Swing.SwingDirection.Reverse,
                                     Swing.SwingJitterType.Fixed)
    actual_note_starts = [note.start for note in note_sequence]
    assert expected_swing_note_starts == pytest.approx(actual_note_starts)


def test_swing_reverse_random(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)

    expected_swing_note_starts = [note_sequence[0].start - SWING_RANGE,
                                  note_sequence[1].start - SWING_RANGE,
                                  note_sequence[2].start - SWING_RANGE,
                                  note_sequence[3].start - SWING_RANGE]
    swing.set_swing_on().apply_swing(note_sequence,
                                     Swing.SwingDirection.Reverse,
                                     Swing.SwingJitterType.Random)
    actual_note_starts = [note.start for note in note_sequence]
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values
    for i, actual_note_start in enumerate(actual_note_starts):
        assert actual_note_start >= expected_swing_note_starts[i]


def test_swing_both_random(note_sequence, swing):
    note_sequence[1].start += DUR
    note_sequence[2].start += (2 * DUR)
    note_sequence[3].start += (3 * DUR)

    expected_swing_reverse_note_starts = [note_sequence[0].start - SWING_RANGE,
                                          note_sequence[1].start - SWING_RANGE,
                                          note_sequence[2].start - SWING_RANGE,
                                          note_sequence[3].start - SWING_RANGE]
    expected_swing_forward_note_starts = [note_sequence[0].start + SWING_RANGE,
                                          note_sequence[1].start + SWING_RANGE,
                                          note_sequence[2].start + SWING_RANGE,
                                          note_sequence[3].start + SWING_RANGE]
    expected_swing_note_starts = list(zip(expected_swing_reverse_note_starts,
                                          expected_swing_forward_note_starts))
    swing.set_swing_on().apply_swing(note_sequence,
                                     Swing.SwingDirection.Both,
                                     Swing.SwingJitterType.Random)
    actual_note_starts = [note.start for note in note_sequence]
    # For this test case, swing applied to each note to change its start time may be forward or reverse
    # so test each note for being one of the two possible values
    for i, actual_note_start in enumerate(actual_note_starts):
        assert expected_swing_note_starts[i][0] <= actual_note_start <= expected_swing_note_starts[i][1]


if __name__ == '__main__':
    pytest.main(['-xrf'])
