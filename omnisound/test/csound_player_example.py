# Copyright 2019 Mark S. Weiss

from omnisound.note.adapters.note import NoteValues
from omnisound.note.containers.measure import (Measure,
                                               Meter, NoteDur,
                                               Swing)
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.player.csound_player import CSoundPlayer
import omnisound.note.adapters.csound_note as csound_note

# OUT_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.wav'
# SCORE_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.sco'
# ORCHESTRA_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.orc'
# SCORE_INCLUDE_FILE_PATH = ('/Users/markweiss/Documents/projects/omnisound/omnisound/test/'
#                            'csound_player_example_ftables.txt')

SONG_NAME = 'Your Song'

NUM_NOTES = 4
INSTRUMENT_1 = 1
INSTRUMENT_2 = 2
START = 0.0
DUR = float(NoteDur.QUARTER.value)
FUNC_TABLE = 1
AMP = 100.0
PITCH = 9.01
ATTR_VALS_DEFAULTS_MAP = {'instrument': float(INSTRUMENT_1),
                          'start': START,
                          'duration': DUR,
                          'amplitude': AMP,
                          'pitch': PITCH}
NOTE_SEQUENCE_IDX = 0
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)

BASE_AMP = 10000
AMP_FACTOR = 5
AMP_CYCLE = 20

BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SWING_RANGE = 0.1


if __name__ == '__main__':
    meter = Meter (beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)
    swing = Swing (swing_range=SWING_RANGE)

    note_configs =[]
    for i in range(NUM_NOTES):
        note_config = NoteValues(csound_note.ATTR_NAMES)
        note_config.instrument = INSTRUMENT_1
        note_config.start = (i % NUM_NOTES) * DUR
        note_config.duration = DUR
        note_config.amplitude = BASE_AMP
        note_config.pitch = PITCH
        note_configs.append(note_config)

    measure = Measure(meter=meter,
                      swing=swing,
                      make_note=csound_note.make_note,
                      num_notes=NUM_NOTES,
                      num_attributes=NUM_ATTRIBUTES,
                      attr_name_idx_map=ATTR_NAME_IDX_MAP,
                      attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP)

    # TODO SET THE UNDERLYING NOTE ATTRS
    # note_1 = CSoundNote (**note_config.as_dict ())
    # note_1.set_to_str_for_attr ('func_table')
    # note_2 = CSoundNote.copy (note_1)
    # note_2.instrument = INSTRUMENT_2
    # notes.append(note_1)
    # notes.append(note_2)

    # TODO WHERE TO PUT THE OTHER PROPERTIES REQUIRED TO BUILD CSD STRING WITH INSTRUMENTS INLINE

    track = Track(to_add=[measure], name='ostinato', instrument=INSTRUMENT_1)
    song = Song(to_add=[track], name=SONG_NAME)
    player = CSoundPlayer(song=song)
    player.play_all()
