# Copyright 2019 Mark S. Weiss

from omnisound.note.adapters.csound_note import CSoundNote, FIELDS
from omnisound.note.adapters.note import NoteConfig
from omnisound.note.containers.measure import Measure
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.player.csound_player import CsoundPlayer

SONG_NAME = 'Your Song'
INSTRUMENT = 1
FUNC_TABLE = 1
DUR = 0.1
NUM_NOTES = 10
BASE_AMP = 10000
AMP_FACTOR = 5
AMP_CYCLE = 20
PITCH = 6.07


if __name__ == '__main__':
    performance_attrs = PerformanceAttrs()

    ostinato_notes = NoteSequence([])
    for i in range(NUM_NOTES):
        note_config = NoteConfig(FIELDS)
        note_config.instrument = INSTRUMENT
        note_config.start = (i % NUM_NOTES) * DUR
        note_config.duration = DUR
        note_config.amplitude = BASE_AMP
        # note_config.amplitude = int(BASE_AMP + (BASE_AMP * (((i % AMP_CYCLE) + 1) / NUM_NOTES) * AMP_FACTOR))
        note_config.pitch = PITCH
        note = CSoundNote(**note_config.as_dict())
        note.add_attr('func_table', FUNC_TABLE)
        ostinato_notes.append(note)

    ostinato_measure = Measure(ostinato_notes)
    track = Track(to_add=[ostinato_measure], name='ostinato', instrument=INSTRUMENT)
    song = Song(to_add=[track], name=SONG_NAME)
    player = CsoundPlayer(
        song=song,
        out_file_path='/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_example.wav',
        score_file_path='/Users/markweiss/Documents/projects/omnisound/omnisound/test/csound_example.sco',
        orchestra_file_path='/Users/markweiss/Documents/projects/omnisound/omnisound/test/markov_opt_1.orc')
    player.add_score_include_file (
        '/Users/markweiss/Documents/projects/omnisound/omnisound/test/oscil_sine_ftables_1.txt')
    player.play_all()
