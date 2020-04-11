# Copyright 2020 Mark S. Weiss

from typing import Optional

from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.note.generators.chord_globals import HarmonicChord
from omnisound.note.generators.scale_globals import HarmonicScale, MajorKey, MinorKey
from omnisound.note.modifiers.meter import Meter, NoteDur
from omnisound.note.modifiers.swing import Swing


class Sequencer(Song):

    DEFAULT_PATTERN_RESOLUTION = NoteDur.QUARTER

    def __init__(self,
                 name: str = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 num_measures: int = None,
                 pattern_resolution: NoteDur = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        # Sequencer wraps song but starts with no Tracks. It provides an alternate API for generating and adding Tracks.
        to_add = []
        super(Sequencer, self).__init__(to_add, name, meter, swing, performance_attrs)
        self.num_measures = num_measures
        self.pattern_resolution = pattern_resolution or Sequencer.DEFAULT_PATTERN_RESOLUTION

    def add_pattern_to_track(self, track: Track = None, pattern: str = None) -> None:
        pass

    def add_pattern_as_track(self, pattern: str) -> None:
        pass
