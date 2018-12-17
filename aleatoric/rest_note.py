# Copyright 2018 Mark S. Weiss

from typing import Any, Union

from aleatoric.note import (Note, PerformanceAttrs)
from aleatoric.scale_globals import (MajorKey, MinorKey)


class RestNote(Note):
    """Models the core attributes of a musical note common to multiple back ends
       with amplitude set to 0
    """

    REST_AMP = 0.0

    def __init__(self, instrument: Any = None,
                 start: float = None, dur: float = None, pitch: float = None,
                 name: str = None,
                 performance_attrs: PerformanceAttrs = None):
        super(RestNote, self).__init__(instrument=instrument,
                                       start=start, dur=dur, amp=RestNote.REST_AMP, pitch=pitch,
                                       name=name,
                                       performance_attrs=performance_attrs)

    @staticmethod
    def to_rest(note: Note):
        note.amp = RestNote.REST_AMP

    def get_pitch(self, key: Union[MajorKey, MinorKey], octave: int):
        raise NotImplemented('RestNote cannot meaningfully implement get_pitch()')
