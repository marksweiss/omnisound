# Copyright 2018 Mark S. Weiss

from typing import Any, List

import pytest
from FoxDot.lib.SCLang._SynthDefs import pluck as fd_sc_synth

from aleatoric.csound_note import CSoundNote, FIELDS as csound_fields
from aleatoric.foxdot_supercollider_note import FIELDS as foxdot_fields, FoxDotSupercolliderNote
from aleatoric.midi_note import FIELDS as midi_fields,  MidiInstrument, MidiNote
from aleatoric.note import NoteConfig
from aleatoric.note_sequence import NoteSequence
from aleatoric.performance_attrs import PerformanceAttrs
from aleatoric.rest_note import RestNote

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


# TODO SEPARATE TESTS FOR NOTE SEQUENCE. BETTER COVERAGE
def _setup_note_sequence_args():
    note_1 = CSoundNote.copy(NOTE)
    note_2 = CSoundNote.copy(NOTE)
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(attr_name=ATTR_NAME, val=ATTR_VAL, attr_type=ATTR_TYPE)
    note_1.performance_attrs = perf_attrs
    note_2.performance_attrs = perf_attrs
    note_list = [note_1, note_2]
    return note_list, perf_attrs


def _setup_note_sequence():
    return NoteSequence(*_setup_note_sequence_args())


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


def test_note_sequence():
    note_list, perf_attrs = _setup_note_sequence_args()
    note_sequence = NoteSequence(note_list, perf_attrs)
    assert note_sequence
    # Assert all the note_attrs in the note_sequence have the same performance_attr
    assert note_sequence.note_list == note_sequence.nl == note_list
    assert note_sequence.performance_attrs == note_sequence.pa == perf_attrs


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
    assert note.instrument == MIDI_INSTRUMENT
    assert note.time == START
    assert note.velocity == AMP
    assert note.duration == DUR
    assert note.pitch == PITCH

    note_config = _setup_note_config(MidiNote)
    note = MidiNote(*note_config.as_list())
    assert note.instrument == MIDI_INSTRUMENT
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


def test_note_sequence_iter_note_attr_properties():
    note_sequence = _setup_note_sequence()
    # Iterate once and assert attributes of elements. This tests __iter__() and __next__()
    first_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        # noinspection PyUnresolvedReferences
        assert note.pa.test_attr == ATTR_VAL
        first_loop_count += 1
    # Iterate again. This tests that __iter__() resets the loop state
    second_loop_count = 0
    for note in note_sequence:
        assert note.start == START
        # noinspection PyUnresolvedReferences
        assert note.pa.test_attr == ATTR_VAL
        second_loop_count += 1
    assert first_loop_count == second_loop_count


def test_note_sequence_len_append_getitem():
    # Returns note_list with 2 Notes
    note_sequence = _setup_note_sequence()
    note_3 = CSoundNote.copy(NOTE)
    new_amp = NOTE.amp + 1
    note_3.amp = new_amp
    # Assert initial len() of note_list
    assert len(note_sequence) == 2
    # Append and check len again
    note_sequence.append(note_3)
    assert len(note_sequence) == 3
    # Check that last element has modified attribute, using NoteSequence[idx]
    # to access the note directly by index
    assert note_sequence[2].amp == new_amp


def test_note_sequence_add_lshift_extend():
    expected_len = 2
    note_sequence = _setup_note_sequence()
    assert len(note_sequence) == expected_len
    # Append/Add and check len again
    note_sequence += NOTE
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with lshift syntax
    note_sequence << NOTE
    expected_len += 1
    assert len(note_sequence) == expected_len
    # Append/Add with a List[Note]
    note_sequence += [NOTE, NOTE]
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Append/Add with a NoteSequence
    new_note_sequence = NoteSequence([NOTE, NOTE])
    note_sequence += new_note_sequence
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Extend with a List[Note]
    note_sequence.extend([NOTE, NOTE])
    expected_len += 2
    assert len(note_sequence) == expected_len
    # Extend with a NoteSequence
    new_note_sequence = NoteSequence([NOTE, NOTE])
    note_sequence.extend(new_note_sequence)
    expected_len += 2
    assert len(note_sequence) == expected_len


def test_note_sequence_insert_remove():
    note_sequence = _setup_note_sequence()
    note_front = note_sequence[0]
    assert note_front.amp == AMP

    # Insert a single note at the front of the list
    new_amp = AMP + 1
    new_note = CSoundNote.copy(note_front)
    new_note.amp = new_amp
    note_sequence.insert(0, new_note)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp

    # Insert a list of 2 notes at the front of the list
    new_amp_1 = AMP + 2
    new_note_1 = CSoundNote.copy(note_front)
    new_note_1.amp = new_amp_1
    new_amp_2 = AMP + 3
    new_note_2 = CSoundNote.copy(note_front)
    new_note_2.amp = new_amp_2
    new_note_list = [new_note_1, new_note_2]
    note_sequence.insert(0, new_note_list)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp_1
    note_front = note_sequence[1]
    assert note_front.amp == new_amp_2

    # Insert a NoteSequence with 2 notes at the front of the list
    new_amp_1 = AMP + 4
    new_note_1 = CSoundNote.copy(note_front)
    new_note_1.amp = new_amp_1
    new_amp_2 = AMP + 5
    new_note_2 = CSoundNote.copy(note_front)
    new_note_2.amp = new_amp_2
    new_note_list = [new_note_1, new_note_2]
    new_note_sequence = NoteSequence(new_note_list)
    note_sequence.insert(0, new_note_sequence)
    note_front = note_sequence[0]
    assert note_front.amp == new_amp_1
    note_front = note_sequence[1]
    assert note_front.amp == new_amp_2

    # Remove notes added as NoteSequence, List[Note] and Note
    # After removing a note, the new front note is the one added second to most recently
    expected_amp = note_sequence[1].amp
    note_to_remove = note_sequence[0]
    note_sequence.remove(note_to_remove)
    note_front = note_sequence[0]
    assert note_front.amp == expected_amp
    expected_amp = note_sequence[1].amp
    for i in range(4):
        note_to_remove = note_sequence[0]
        note_sequence.remove(note_to_remove)
        note_front = note_sequence[0]
        assert note_front.amp == expected_amp
        expected_amp = note_sequence[1].amp


if __name__ == '__main__':
    pytest.main(['-xrf'])
