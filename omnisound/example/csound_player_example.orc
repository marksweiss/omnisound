; HEADER
sr      = 44100	 ; OPT - play with sampling rate, try lower rate
kr      = 441	 ; OPT - play with control rate, here its sr/10
ksmps   = 100
nchnls  = 2

instr 1
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
    iFuncNum = p6

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
endin

instr 2
    ; Initialize variables
    ; Envelope shape
    iRiseFctr = .04
    iDecayFctr = .04
    iDur1 = p3
    iRise1 = iDur1 * iRiseFctr
    iDec1 = iDur1 * iDecayFctr
    ; Amp
    iAmp = p4
    iNumOuts = 2
    ; Other note params
    iPitch = cpspch(p5)  ; Convert from std. Western notation to frequency
    iPitch *= 1.00001
    iFuncNum = p6

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
endin

