# Copyright 2018 Mark S. Weiss

from typing import List, Tuple

import pytest

from aleatoric.csound_note import CSoundNote
from aleatoric.measure import Measure, Meter, NoteDur, Swing
from aleatoric.note import PerformanceAttrs
from aleatoric.note_sequence import NoteSequence
from aleatoric.section import Section
from aleatoric.track import Track


INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 1
PITCH = 10.1
NOTE = CSoundNote(instrument=INSTRUMENT, start=START, duration=DUR, amplitude=AMP, pitch=PITCH)

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR

SWING_FACTOR = 0.5


@pytest.fixture
def note_list():
    note_1 = CSoundNote.copy(NOTE)
    note_2 = CSoundNote.copy(NOTE)
    note_2.start += DUR
    note_3 = CSoundNote.copy(NOTE)
    note_3.start += (DUR * 2)
    note_4 = CSoundNote.copy(NOTE)
    note_4.start += (DUR * 3)
    return [note_1, note_2, note_3, note_4]


@pytest.fixture
def performance_attrs():
    performance_attrs = PerformanceAttrs()
    performance_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    return performance_attrs


@pytest.fixture
def note_sequence(note_list):
    return NoteSequence(note_list)


@pytest.fixture
def meter():
    return Meter(beats_per_measure=BEATS_PER_MEASURE, beat_dur=BEAT_DUR)


@pytest.fixture
def swing():
    return Swing(swing_factor=SWING_FACTOR)


@pytest.fixture
def measure(note_list, meter, swing):
    return Measure(note_list, meter=meter, swing=swing)


@pytest.fixture
def measure_list(measure):
    measure_2 = Measure.copy(measure)
    measure_list = [measure, measure_2]
    return measure_list


@pytest.fixture
def section(measure_list, performance_attrs):
    return Section(measure_list=measure_list, performance_attrs=performance_attrs)


def test_track(performance_attrs, measure_list, section):
    # Test: List[Measure] and no instrument or performance_attrs
    # Expect a Track with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=measure_list)
    assert track.measure_list == measure_list
    assert track.track_instrument == Track.DEFAULT_INSTRUMENT
    assert track.performance_attrs is None

    # Test: Section and no instrument or performance_attrs
    # Expect a Track with measures, no track_instrument, no pa and Notes not having reassigned instrument or pa
    track = Track(to_add=section)
    assert track.measure_list == section.measure_list
    assert track.track_instrument == Track.DEFAULT_INSTRUMENT
    assert track.performance_attrs is None

    # Test: List[Measure] with instrument and performance_attrs
    # Expect a Track with measures, track_instrument, pa and Notes having reassigned instrument and pa
    track = Track(to_add=measure_list, instrument=INSTRUMENT, performance_attrs=performance_attrs)
    assert track.measure_list == measure_list
    assert track.track_instrument == INSTRUMENT
    assert track.performance_attrs == performance_attrs

    # Test: Section with instrument and performance_attrs
    # Expect a Track with measures, track_instrument, pa and Notes having reassigned instrument and pa
    track = Track(to_add=section, instrument=INSTRUMENT, performance_attrs=performance_attrs)
    assert track.measure_list == section.measure_list
    assert track.track_instrument == INSTRUMENT
    assert track.performance_attrs == performance_attrs


if __name__ == '__main__':
    pytest.main(['-xrf'])
