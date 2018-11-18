# Copyright 2018 Mark S. Weiss

from typing import Optional


class Note(object):
    """Models the core attributes of a musical note common to multiple back ends"""
    name: Optional[str]
    DEFAULT_NAME = 'note'

    def __init__(self, start: float = None, dur: float = None, amp: float = None, pitch: float = None,
                 name: str = None) -> object:
        if start is None or dur is None or amp is None or pitch is None:
            raise ValueError((f'Must provide value for required Note args: start {start} '
                              f'dur: {dur} amp: {amp} pitch: {pitch}'))
        self.start = start
        self.dur = dur
        self.amp = amp
        self.pitch = pitch
        self.name = name or Note.DEFAULT_NAME


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0
    """

    REST_AMP = 0.0

    def __init__(self, start: float = None, dur: float = None, amp: float = None, pitch: float = None,
                 name: str = None) -> object:
        super(RestNote, self).__init__(start=start, dur=dur, amp=amp, pitch=pitch, name=name)
        self.amp = RestNote.REST_AMP

    @staticmethod
    def to_rest(note: Note):
        note.amp = 0.0


class CSoundNote(Note):
    """Models a note with attributes aliased to and specific to CSound
       and with a str() that prints CSound formatted output.
    """

    def __init__(self, time: float = None, duration: float = None, velocity: float = None,
                 pitch: float = None, name: str = None, instrument: int = None) -> object:
        if instrument is None:
            raise ValueError(f'CSoundNote must provide value for required arg instrument: {instrument}')
        super(CSoundNote, self).__init__(start=time, dur=duration, amp=velocity, pitch=pitch, name=name)
        self.instrument = instrument

    @property
    def time(self):
        return self.start

    @time.setter
    def time(self, time: float):
        self.start = time

    @property
    def duration(self):
        return self.dur

    @duration.setter
    def duration(self, duration: float):
        self.dur = duration

    @property
    def velocity(self):
        return self.amp

    @velocity.setter
    def velocity(self, velocity: float):
        self.amp = velocity

    def __str__(self):
        return f'i {self.instrument} {self.start:.5f} {self.duration:.5f} {self.velocity} {self.pitch:.5f}'


class MidiNote(Note):
    """Models a note with attributes aliased to and specific to MIDI
       and with a str() that prints MIDI formatted output.
    """

    DEFAULT_CHANNEL = 1

    def __init__(self, start: float = None, dur: float = None, velocity: float = None,
                 pitch: float = None, name: str = None, instrument: int = None,
                 channel: int = None) -> object:
        if instrument is None:
            raise ValueError(f'MidiNote must provide value for required arg instrument: {instrument}')
        super(MidiNote, self).__init__(start=start, dur=dur, amp=velocity, pitch=pitch, name=name)
        self.instrument = instrument
        self.channel = channel or MidiNote.DEFAULT_CHANNEL

    @property
    def velocity(self):
        return self.amp

    @velocity.setter
    def velocity(self, velocity: float):
        self.amp = velocity

    def program_change(self, instrument: int):
        if instrument is None:
            raise ValueError(f'MidiNote must provide value for required arg instrument: {instrument}')
        self.instrument = instrument

    def __str__(self):
        """Used only for unit testing, to verify data in note is as expected. Not actually used
           to render MIDI file output
        """
        return f'{self.instrument} {self.start:.5f} {self.dur:.5f} {self.velocity} {self.pitch:.5f}'
