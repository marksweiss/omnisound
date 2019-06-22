# Copyright 2019 Mark S. Weiss

from omnisound.note.adapters.csound_note import CSoundNote, FIELDS
from omnisound.note.adapters.note import NoteValues
from omnisound.note.containers.measure import Measure
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.player.csound_player import CsoundPlayer

SONG_NAME = 'Your Song'
INSTRUMENT_1 = 1
INSTRUMENT_2 = 2
FUNC_TABLE = 1
DUR = 0.1
NUM_NOTES = 10
BASE_AMP = 10000
AMP_FACTOR = 5
AMP_CYCLE = 20
PITCH = 6.07
OUT_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.wav'
SCORE_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.sco'
ORCHESTRA_FILE_PATH = '/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_player_example.orc'
SCORE_INCLUDE_FILE_PATH = ('/Users/markweiss/Documents/projects/omnisound/omnisound/test/'
                           'csound_player_example_ftables.txt')

if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    notes = NoteSequence([])
    for i in range(NUM_NOTES):
        note_config = NoteValues(FIELDS)
        note_config.instrument = INSTRUMENT_1
        note_config.start = (i % NUM_NOTES) * DUR
        note_config.duration = DUR
        note_config.amplitude = BASE_AMP
        note_config.pitch = PITCH
        note_1 = CSoundNote(**note_config.as_dict())
        note_1.set_to_str_for_attr ('func_table')
        notes.append(note_1)
        note_2 = CSoundNote.copy(note_1)
        note_2.instrument = INSTRUMENT_2
        notes.append(note_2)

    measure = Measure(notes)
    track = Track(to_add=[measure], name='ostinato', instrument=INSTRUMENT_1)
    song = Song(to_add=[track], name=SONG_NAME)
    player = CsoundPlayer(song=song, out_file_path=OUT_FILE_PATH,
                          score_file_path=SCORE_FILE_PATH, orchestra_file_path=ORCHESTRA_FILE_PATH)
    player.add_score_include_file(SCORE_INCLUDE_FILE_PATH)
    player.play_all()
