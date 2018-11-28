# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.measure import Measure, Meter, NoteDur
from aleatoric.note import Note, NoteSequence

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

INSTRUMENT = 1
START = 0
DUR = NoteDur.QUARTER.value
AMP = 1.0
PITCH = 10.1
NOTE = Note(instrument=INSTRUMENT, start=START, dur=DUR, amp=AMP, pitch=PITCH)


@pytest.fixture(scope='module')
def note_list():
    note_1 = Note.copy(NOTE)
    note_2 = Note.copy(NOTE)
    note_2.start += DUR
    note_3 = Note.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = Note.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


def test_quantize(note_list):
    # Simplest test case: Note durations sum to measure duration and no quantizing required
    note_sequence_before_quantization = NoteSequence(note_list)

    note_sequence = NoteSequence(note_list)
    meter = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_dur=BEAT_DUR, quantizing=True)
    measure = Measure(note_sequence=note_sequence, meter=meter)
    measure.quantize()
    # Relies on Note.__eq__
    assert note_sequence_before_quantization.note_list == note_sequence.note_list


if __name__ == '__main__':
    pytest.main(['-xrf'])

