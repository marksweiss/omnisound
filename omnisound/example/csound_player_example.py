# Copyright 2019 Mark S. Weiss

import sys

from omnisound.src.note.adapter.csound_note import (ATTR_GET_TYPE_CAST_MAP, ATTR_NAME_IDX_MAP, CLASS_NAME,
                                                    NUM_ATTRIBUTES, get_pitch_for_key, make_note)
from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.container.measure import Measure
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.modifier.swing import Swing
from omnisound.src.container.song import Song
from omnisound.src.container.track import Track
from omnisound.src.player.csound.csound_player import (CSoundCSDPlayer, CSoundEventType, CSoundInteractivePlayer,
                                                       CSoundOrchestra, CSoundScoreEvent)

# Song Params
SONG_NAME = 'Your Song'

# Note Params
INSTRUMENT_1_ID = 1
START = 0.0
DUR = float(NoteDur.QUARTER.value)
AMP = 100.0
PITCH = 9.01
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

NOTE_CONFIG = MakeNoteConfig(cls_name=CLASS_NAME,
                             num_attributes=NUM_ATTRIBUTES,
                             make_note=make_note,
                             get_pitch_for_key=get_pitch_for_key,
                             attr_name_idx_map=ATTR_NAME_IDX_MAP,
                             attr_val_cast_map=ATTR_GET_TYPE_CAST_MAP)

if __name__ == '__main__':
    meter = Meter(beats_per_measure=BEATS_PER_MEASURE, beat_note_dur=BEAT_DUR, tempo=TEMPO_QPM)
    swing = Swing(swing_range=SWING_RANGE)
    measure = Measure(num_notes=NUM_NOTES,
                      meter=meter,
                      swing=swing,
                      mn=NOTE_CONFIG)
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

    # Play song with CSD player
    player = CSoundCSDPlayer(csound_orchestra=orchestra, song=song)
    player.set_score_header_lines(SCORE_HEADER_LINES)
    player.play()
    # Comment this out to test code below it
    # player.loop()

    # Play song with interactive player
    player = CSoundInteractivePlayer(csound_orchestra=orchestra)
    # Add a function table with 0th arg == 1, this defines data referred to by 'instrument 1'
    # in the Orchestra bound to the Player
    player.add_score_event(CSoundScoreEvent(event_type=CSoundEventType.FunctionTable,
                                            event_data=(1, 0, 8193, 10, 1)))

    # Now add score events of type 'i', these are instrument events, that play the instrument with
    # start_time, amplitude and pitch
    player.add_song_note_events(song)

    # Now add an end event event of type 'e' that stops the performance and closes writing the output
    player.add_end_score_event(beats_to_wait=10)
    # Perform the score events on the Orchestra bound to the Player
    ret = player.play()
    print(f'Return code from play() {ret}')
    ret = player.cleanup()
    print(f'Return code from cleanup() {ret}')
    # NOTE: Must explicitly call sys.exit or CSound interactive Py API doesn't close the file handle on the file it's
    # writing and just leaks by writing more and more to the file until you manually kill the parent process.
    sys.exit(ret)
