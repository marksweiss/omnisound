# Copyright 2019 Mark S. Weiss

import sys

from omnisound.note.containers.measure import (Measure,
                                               Meter, NoteDur,
                                               Swing)
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.player.csound_player import (CSoundCSDPlayer, CSoundEventType, CSoundInteractivePlayer, CSoundOrchestra,
                                            CSoundScore, CSoundScoreEvent)
import omnisound.note.adapters.csound_note as csound_note

# Song Params
SONG_NAME = 'Your Song'

# Note Params
INSTRUMENT_1_ID = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01
ATTR_NAME_IDX_MAP = csound_note.ATTR_NAME_IDX_MAP
NUM_ATTRIBUTES = len(csound_note.ATTR_NAMES)
#
BASE_AMP = 10000
AMP_FACTOR = 5
AMP_CYCLE = 20

# Measure Params
NUM_NOTES = 4
BEATS_PER_MEASURE = 4
BEAT_DUR = NoteDur.QRTR
TEMPO_QPM = 240
SWING_RANGE = 0.1

# Score Params
SR = 44100
KSMPS = 100
NCHNLS = 2
#
INSTRUMENT_1 = f'''instr {INSTRUMENT_1_ID} 
    ; Initialize variables
    ; Envelope shape
    iRiseFctr = .02
    iDecayFctr = .02
    iDur1 = p3
    iRise1 = iDur1 * iRiseFctr
    iDec1 = iDur1 * iDecayFctr
    ; Amp
    iAmp = p4
    iNumOuts = 2
    ; Other note params
    iPitch = cpspch(p5)  ; Convert from std. Western notation to frequency
    iFuncNum = 1 

    ; Envelope
    ;     Opcode    Amplitude   Rise      Duration    Decay
    ; -------------------------------------------------------
    ar1   linen     iAmp,       iRise1,   iDur1,      iDec1
    ar2   linen     iAmp,       iRise1,   iDur1,      iDec1

    ; Source sound, sine opcode
    ;     Opcode,   Amplitude,  Frequency,  Function#
    ; -------------------------------------------------------
    a1    oscil     ar1,        iPitch,     iFuncNum
    a2    oscil     ar2,        iPitch,     iFuncNum
        outs a1, a2
endin'''
INSTRUMENTS = [INSTRUMENT_1]
#
SCORE_HEADER = '''; Function 1
; GEN10 Parameters: 
;	- str1, str2, str3 ... where str is a fixed harmonic partial
;		- the value of str# is the relative strength of the partial in the final mixed timbre
;		- partials to be skipped are given value 0
;
; Func # 	Loadtm 	TblSize GEN   Parameters ...
; First partial variations
f 1		    0		    8193		10		1'''
SCORE_HEADER_LINES = [SCORE_HEADER]


if __name__ == '__main__':
    meter = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)
    swing = Swing(swing_range=SWING_RANGE)
    measure = Measure(meter=meter,
                      swing=swing,
                      make_note=csound_note.make_note,
                      num_notes=NUM_NOTES,
                      num_attributes=NUM_ATTRIBUTES,
                      attr_name_idx_map=ATTR_NAME_IDX_MAP)
    for i in range(NUM_NOTES):
        measure[i].instrument = INSTRUMENT_1_ID
        measure[i].start = (i % NUM_NOTES) * DUR
        measure[i].duration = DUR
        measure[i].amplitude = BASE_AMP
        measure[i].pitch = PITCH
    measure.apply_swing()
    track = Track(to_add=[measure], name='ostinato', instrument=INSTRUMENT_1_ID)
    song = Song(to_add=[track], name=SONG_NAME)

    orchestra = CSoundOrchestra(instruments=INSTRUMENTS,
                                sampling_rate=SR, ksmps=KSMPS, num_channels=NCHNLS)

    # TODO MOVE THIS Song INSIDE CSoundInteractivePlayer AND IT WILL HAVE EQUIVALENT API AS MidiPlayer:
    #  input is a Song of Tracks =>
    #  Player converts to stream of note events for that back-end =>
    #  Player writes data for that back-end to file OR plays back interactively
    #  ```
    #  player = XYZPlayer(song)
    #  player.play_all()
    #  ```
    note_lines = []
    for track in song:
        for measure in track.measure_list:
            for note in measure:
                note_lines.append(f'{str (note)}')
    score = CSoundScore(header_lines=SCORE_HEADER_LINES, note_lines=note_lines)
    player = CSoundCSDPlayer(csound_orchestra=orchestra, csound_score=score)
    ret = player.play_all()

    # Create the player
    player = CSoundInteractivePlayer(csound_orchestra=orchestra)
    # Add a function table with 0th arg == 1, this defines data referred to by 'instrument 1'
    # in the Orchestra bound to the Player
    player.add_score_event(CSoundScoreEvent(event_type=CSoundEventType.FunctionTable,
                                            event_data=(1, 0, 8193, 10, 1)))
    # Now add score events of type 'i', these are instrument events, that play the instrument with
    # start_time, amplitude and pitch
    for track in song:
        for measure in track.measure_list:
            player.add_score_events([CSoundScoreEvent.note_to_score_event(note) for note in measure])
    # Now add an end event event of type 'e' that stops the performance and closes writing the output
    player.add_end_score_event(beats_to_wait=10)
    # Perform the score events on the Orchestra bound to the Player
    ret = player.play_all()
    # NOTE: Must explicitly call sys.exit or CSound interactive Py API doesn't close the file handle on the file it's
    # writing and just leaks by writing more and more to the file until you manually kill the parent process.
    sys.exit(ret)
