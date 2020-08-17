# Copyright 2020 Mark S. Weiss

import pytest

from omnisound.src.generator.chord_globals import HarmonicChord
from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.modifier.swing import Swing
from omnisound.src.generator.sequencer.sequencer import Sequencer
import omnisound.src.note.adapter.csound_note as csound_note

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
ATTR_VAL_CAST_MAP = csound_note.ATTR_VAL_CAST_MAP
NUM_NOTES = 4
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SECS_PER_MINUTE = 60
DEFAULT_IS_QUANTIZING = False
SWING_RANGE = 0.1

SEQUENCER_NAME = 'Sequencer'
NUM_MEASURES = 4
PATTERN_RESOLUTION = NoteDur.QUARTER
ARPEGGIATOR_CHORD = HarmonicChord.MinorTriad

TRACK_NAME = 'Track 1'
PATTERN = ('C:4::100: D:4::100: E:4::100: F:4::100:|C:4::100: D:4::100: E:4::100: F:4::100:|'
           'C:4::100: D:4::100: E:4::100: F:4::100:|C:4::100: D:4::100: E:4::100: F:4::100:')


@pytest.fixture
def make_note_config():
    # Don't pass attr_vals_default_map to Sequencer, because it constructs all its notes from patterns
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_get_type_cast_map=ATTR_VAL_CAST_MAP)


@pytest.fixture
def meter():
    return Meter(beat_note_dur=BEAT_DUR, beats_per_measure=BEATS_PER_MEASURE, tempo=TEMPO_QPM,
                 quantizing=DEFAULT_IS_QUANTIZING)


@pytest.fixture
def swing():
    return Swing(swing_range=SWING_RANGE)


def _sequencer(mn, meter, swing):
    return Sequencer(name=SEQUENCER_NAME,
                     num_measures=NUM_MEASURES,
                     meter=meter,
                     swing=swing,
                     mn=mn)


@pytest.fixture
def sequencer(make_note_config, meter, swing):
    return _sequencer(make_note_config, meter, swing)


def test_init(sequencer):
    assert isinstance(sequencer, Sequencer)


def test_add_track(sequencer):
    ret = sequencer.add_track(track_name=TRACK_NAME, instrument=INSTRUMENT)
    assert ret.name == TRACK_NAME
    assert len(sequencer) == 1


def test_set_pattern_for_track(sequencer):
    sequencer.add_track(track_name=TRACK_NAME, instrument=INSTRUMENT)

    # Use instrument associated with track
    sequencer.set_track_pattern(track_name=TRACK_NAME, pattern=PATTERN)
    assert len(sequencer.track_list) == 1
    assert sequencer.track_list[0].name == TRACK_NAME
    assert len(sequencer.track_list[0].measure_list) == NUM_MEASURES

    # Reassign instrument associated with track when changing pattern
    new_instrument = INSTRUMENT + 1
    sequencer.set_track_pattern(track_name=TRACK_NAME, pattern=PATTERN, instrument=new_instrument)
    assert len(sequencer.track_list) == 1
    assert sequencer.track_list[0].name == TRACK_NAME
    assert len(sequencer.track_list[0].measure_list) == NUM_MEASURES
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    first_note = first_measure[0]
    assert first_note.instrument == new_instrument


def test_add_pattern_as_new_track(make_note_config, sequencer, meter, swing):
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT)
    track = sequencer.track(TRACK_NAME)

    # Defaults for fixtures have swing off
    expected_starts = [0.0, DUR, 2 * DUR, 3 * DUR]
    first_measure = track.measure_list[0]
    for i, note in enumerate(first_measure):
        assert expected_starts[i] == note.start

    # Make a new sequencer with swing on and verify the start times are adjusted from being on the beat
    swing.set_swing_on()
    swing.swing_direction = Swing.SwingDirection.Forward
    new_sequencer = _sequencer(make_note_config, meter, swing)
    new_sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT)
    first_measure = new_sequencer.track(TRACK_NAME).measure_list[0]
    for i, note in enumerate(first_measure):
        assert expected_starts[i] < note.start


def test_add_pattern_wth_chords_as_new_track(sequencer, meter, swing):
    chord_pattern = ('C:4::100: C:4:MajorTriad:100: C:4::100: C:4:MajorTriad:100:|'
                     'C:4::100: C:4:MajorTriad:100: C:4::100: C:4:MajorTriad:100:|'
                     'C:4::100: C:4:MajorTriad:100: C:4::100: C:4:MajorTriad:100:|'
                     'C:4::100: C:4:MajorTriad:100: C:4::100: C:4:MajorTriad:100:')
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=chord_pattern, instrument=INSTRUMENT)
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    # Assert that there are notes in the measure for each single note and each note that is part of a chord
    assert len(first_measure) == 8
    # Assert that the second, third and fourth notes all have the same start time and are the three notes of C Major
    first_chord_notes = first_measure[1:4]
    # CSound C4, E4 and G4, all at the same start time
    assert first_chord_notes[0].pitch == 4.01
    assert first_chord_notes[1].pitch == 4.05
    assert first_chord_notes[2].pitch == 4.08
    assert first_chord_notes[0].start == first_chord_notes[1].start == first_chord_notes[2].start


def test_fill_pattern_to_track_length(sequencer):
    # Make a pattern that is one measure long, load into sequencer set to have 4-measure tracks, verify the length
    #  of the track and that notes in it. There should be four measures identical to the one defined by `short_pattern`
    short_pattern = 'C:4::100: D:4::100: E:4::100: F:4::100:'
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=short_pattern, instrument=INSTRUMENT)
    assert NUM_MEASURES == len(sequencer.track(TRACK_NAME))
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    assert pytest.approx(first_measure[0].pitch, 4.01)
    assert pytest.approx(first_measure[1].pitch, 4.03)
    assert pytest.approx(first_measure[2].pitch, 4.05)
    assert pytest.approx(first_measure[3].pitch, 4.06)

    # TODO THIS CASE IS UNTESTED BUT SHOULD PASS
    # Test the case where the pattern does not divide the track length evenly
    # Three-measure pattern into 4-measure track, so the first measure should repeat in the fourth measure
    new_track_name = 'new track'
    three_measure_pattern = ('C:4::100: D:4::100: E:4::100: F:4::100:|'
                             'C:5::100: D:5::100: E:5::100: F:5::100:|'
                             'C:6::100: D:6::100: E:6::100: F:6::100:')
    sequencer.add_pattern_as_new_track(track_name=new_track_name, pattern=three_measure_pattern, instrument=INSTRUMENT)
    assert NUM_MEASURES == len(sequencer.track(new_track_name))
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    last_measure = sequencer.track(TRACK_NAME).measure_list[3]
    assert first_measure == last_measure


def test_pattern_with_varying_durations(sequencer):
    pattern = 'C:4::100:0.5 D:4::100:0.125 E:4::100:0.125 F:4::100:0.25'
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=pattern, instrument=INSTRUMENT)
    measure = sequencer.track(TRACK_NAME).measure_list[0]
    assert measure[0].duration == pytest.approx(NoteDur.HALF.value)
    assert measure[1].duration == pytest.approx(NoteDur.EIGHTH.value)
    assert measure[2].duration == pytest.approx(NoteDur.EIGHTH.value)
    assert measure[3].duration == pytest.approx(NoteDur.QUARTER.value)


def test_pattern_with_arpeggiation(sequencer):
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT,
                                       arpeggiate=True)
    track = sequencer.track(TRACK_NAME)
    # Defaults for fixtures have swing off
    # Each arpeggio has three notes, because the default arpeggio chord is MajorTriad
    second_note_offset = DUR * (1 / 3)
    third_note_offset = DUR * (2 / 3)
    expected_starts = [0.0, second_note_offset, third_note_offset,
                       DUR, DUR + second_note_offset, DUR + third_note_offset,
                       2 * DUR, (2 * DUR) + second_note_offset, (2 * DUR) + third_note_offset,
                       3 * DUR, (3 * DUR) + DUR * (1 / 3), (3 * DUR) + DUR * (2 / 3)]
    first_measure = track.measure_list[0]
    for i, note in enumerate(first_measure):
        assert expected_starts[i] == pytest.approx(note.start)

    expected_chord_pitches = [4.01, 4.05, 4.08]
    first_chord = first_measure[:3]
    first_chord_pitches = [note.pitch for note in first_chord]
    assert expected_chord_pitches == pytest.approx(first_chord_pitches)


def test_pattern_with_arpeggiation_custom_chord(sequencer):
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT,
                                       arpeggiate=True)
    track = sequencer.track(TRACK_NAME)
    sequencer.arpeggiator_chord = ARPEGGIATOR_CHORD
    first_measure = track.measure_list[0]
    # Default pitches are from class default chord, MajorTriad
    expected_chord_pitches = [4.01, 4.05, 4.08]
    first_chord = first_measure[:3]
    first_chord_pitches = [note.pitch for note in first_chord]
    assert expected_chord_pitches == pytest.approx(first_chord_pitches)

    # Now override the default MajorTriad with MinorTriad and add another track
    sequencer.arpeggiator_chord = ARPEGGIATOR_CHORD
    track_name = TRACK_NAME + '_2'
    sequencer.add_pattern_as_new_track(track_name=track_name, pattern=PATTERN, instrument=INSTRUMENT,
                                       arpeggiate=True)
    track = sequencer.track(track_name)
    sequencer.arpeggiator_chord = ARPEGGIATOR_CHORD
    first_measure = track.measure_list[0]
    expected_chord_pitches = [4.01, 4.04, 4.08]
    first_chord = first_measure[:3]
    first_chord_pitches = [note.pitch for note in first_chord]
    assert expected_chord_pitches == pytest.approx(first_chord_pitches)

    # Now pass in arpeggiator_chord to the method and override the current instance value
    track_name = TRACK_NAME + '_3'
    arpeggiator_chord = HarmonicChord.MajorSeventh
    sequencer.add_pattern_as_new_track(track_name=track_name, pattern=PATTERN, instrument=INSTRUMENT,
                                       arpeggiate=True, arpeggiator_chord=arpeggiator_chord)
    track = sequencer.track(track_name)
    first_measure = track.measure_list[0]
    expected_chord_pitches = [4.01, 4.05, 4.08, 4.12]
    first_chord = first_measure[:4]
    first_chord_pitches = [note.pitch for note in first_chord]
    assert expected_chord_pitches == pytest.approx(first_chord_pitches)


def test_set_tempo(sequencer):
    expected_duration_secs = SECS_PER_MINUTE / TEMPO_QPM
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT)
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    first_note = first_measure[0]
    assert first_note.duration == expected_duration_secs

    # Slower tempo should reset all the notes in the measure to be longer duration
    new_tempo = int(TEMPO_QPM / 2)
    new_expected_duration_secs = expected_duration_secs * 2
    sequencer.set_tempo_for_track(track_name=TRACK_NAME, tempo=new_tempo)
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    first_note = first_measure[0]
    assert first_note.duration == new_expected_duration_secs


def test_transpose(sequencer):
    expected_pitch = 4.01
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT)
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    first_note = first_measure[0]
    assert expected_pitch == first_note.pitch
    interval = 3
    sequencer.transpose(interval)
    assert first_note.pitch == 4.04
