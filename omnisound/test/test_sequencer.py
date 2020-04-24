# Copyright 2020 Mark S. Weiss

import pytest

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.measure import Meter, NoteDur, Swing
from omnisound.note.generators.sequencer import Sequencer, InvalidPatternException
import omnisound.note.adapters.csound_note as csound_note

INSTRUMENT = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01

ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
ATTR_GET_TYPE_CAST_MAP = csound_note.ATTR_GET_TYPE_CAST_MAP
NUM_NOTES = 4
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
DEFAULT_IS_QUANTIZING = False
SWING_RANGE = 0.1

SEQUENCER_NAME = 'Sequencer'
NUM_MEASURES = 4
PATTERN_RESOLUTION = NoteDur.QUARTER

TRACK_NAME = 'Track 1'
PATTERN = ('C:4::100 D:4::100 E:4::100 F:4::100|C:4::100 D:4::100 E:4::100 F:4::100|'
           'C:4::100 D:4::100 E:4::100 F:4::100|C:4::100 D:4::100 E:4::100 F:4::100')


@pytest.fixture
def make_note_config():
    return MakeNoteConfig(cls_name=csound_note.CLASS_NAME,
                          num_attributes=NUM_ATTRIBUTES,
                          make_note=csound_note.make_note,
                          get_pitch_for_key=csound_note.get_pitch_for_key,
                          attr_name_idx_map=ATTR_NAME_IDX_MAP,
                          attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                          attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)


def _note_sequence(mn=None, attr_name_idx_map=None, attr_vals_defaults_map=None, num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence(mn=mn)


@pytest.fixture
def note_sequence():
    return _note_sequence()


def _note(mn=None, attr_name_idx_map=None, attr_vals_defaults_map=None,
          num_attributes=None):
    mn.attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
    mn.attr_vals_defaults_map = attr_vals_defaults_map or ATTR_VALS_DEFAULTS_MAP
    mn.num_attributes = num_attributes or NUM_ATTRIBUTES
    return NoteSequence.make_note(mn)


@pytest.fixture
def note():
    return _note()


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
                     pattern_resolution=PATTERN_RESOLUTION,
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
    assert ret == TRACK_NAME
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
    chord_pattern = ('C:4::100 C:4:MajorTriad:100 C:4::100 C:4:MajorTriad:100|'
                     'C:4::100 C:4:MajorTriad:100 C:4::100 C:4:MajorTriad:100|'
                     'C:4::100 C:4:MajorTriad:100 C:4::100 C:4:MajorTriad:100|'
                     'C:4::100 C:4:MajorTriad:100 C:4::100 C:4:MajorTriad:100')
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


def test_pattern_resolution(make_note_config, meter, swing):
    new_pattern_resolution = NoteDur.EIGHTH
    sequencer = Sequencer(name=SEQUENCER_NAME,
                          num_measures=NUM_MEASURES,
                          pattern_resolution=new_pattern_resolution,
                          meter=meter,
                          swing=swing,
                          mn=make_note_config)

    # Fixture pattern raises because it has four notes per measure but we halved the pattern resolution
    # so there need to be 8 notes per measure
    with pytest.raises(InvalidPatternException):
        sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=PATTERN, instrument=INSTRUMENT)

    new_pattern = ('C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100|'
                   'C:4::100 D:4::100 E:4::100 F:4::100 C:4::100 D:4::100 E:4::100 F:4::100')
    sequencer.add_pattern_as_new_track(track_name=TRACK_NAME, pattern=new_pattern, instrument=INSTRUMENT)
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    new_dur = DUR / 2
    eighth_note_pattern_resolution_expected_starts = [0.0, new_dur, 2 * new_dur, 3 * new_dur,
                                                      4 * new_dur, 5 * new_dur, 6 * new_dur, 7 * new_dur]
    for i, note in enumerate(first_measure):
        assert eighth_note_pattern_resolution_expected_starts[i] == note.start


def test_fill_pattern_to_track_length(sequencer):
    # Make a pattern that is one measure long, load into sequencer set to have 4-measure tracks, verify the length
    #  of the track and that notes in it. There should be four measures identical to the one defined by `short_pattern`
    short_pattern = 'C:4::100 D:4::100 E:4::100 F:4::100'
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
    three_measure_pattern = ('C:4::100 D:4::100 E:4::100 F:4::100|'
                             'C:5::100 D:5::100 E:5::100 F:5::100|'
                             'C:6::100 D:6::100 E:6::100 F:6::100')
    sequencer.add_pattern_as_new_track(track_name=new_track_name, pattern=three_measure_pattern, instrument=INSTRUMENT)
    assert NUM_MEASURES == len(sequencer.track(new_track_name))
    first_measure = sequencer.track(TRACK_NAME).measure_list[0]
    last_measure = sequencer.track(TRACK_NAME).measure_list[3]
    assert first_measure == last_measure
