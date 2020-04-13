# Copyright 2020 Mark S. Weiss

from typing import Any, Mapping, Optional

from omnisound.note.adapters.note import NoteValues
from omnisound.note.adapters.performance_attrs import PerformanceAttrs
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.note.containers.section import Section
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HARMONIC_CHORD_DICT
from omnisound.note.generators.scale_globals import MajorKey, MAJOR_KEY_DICT, MINOR_KEY_DICT
from omnisound.note.modifiers.meter import Meter, NoteDur
from omnisound.note.modifiers.swing import Swing


class InvalidPatternException(Exception):
    pass


# TODO Transpose support
class Sequencer(Song):

    DEFAULT_PATTERN_RESOLUTION = NoteDur.QUARTER
    DEFAULT_TEMPO = 120
    DEFAULT_METER = Meter(beat_note_dur=NoteDur.QUARTER, beats_per_measure=4, tempo=DEFAULT_TEMPO)
    DEFAULT_PITCH = MajorKey.C
    DEFAULT_OCTAVE = 4
    DEFAULT_NUM_MEASURES = 4

    MEASURE_TOKEN = '|'
    REST_TOKEN = '.'
    NOTE_TOKEN_DELIMITER = ':'

    def __init__(self,
                 name: str = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 make_note: Any = None,
                 _pitch_for_key_cb: Any = None,
                 num_attributes: int = None,
                 num_notes: int = None,
                 attr_name_idx_map: Mapping[str, int] = None,
                 attr_vals_defaults_map: Mapping[str, float] = None,
                 attr_get_type_cast_map: Mapping[str, Any] = None,
                 num_measures: int = None,
                 pattern_resolution: NoteDur = None,
                 performance_attrs: Optional[PerformanceAttrs] = None):
        # Sequencer wraps song but starts with no Tracks. It provides an alternate API for generating and adding Tracks.
        to_add = []
        meter = meter or Sequencer.DEFAULT_METER
        super(Sequencer, self).__init__(to_add, name, meter, swing, performance_attrs)

        self.num_tracks = 0
        # Internal index to the next track to create when add_track() or add_pattern_as_track() are called
        self._next_track = 0

        self._make_note = make_note
        self._pitch_for_key_cb = _pitch_for_key_cb
        self.num_notes = num_notes
        self.num_attributes = num_attributes
        self.attr_name_idx_map = attr_name_idx_map
        self.attr_vals_defaults_map = attr_vals_defaults_map
        self.attr_get_type_cast_map = attr_get_type_cast_map

        self.num_measures = num_measures = num_measures or Sequencer.DEFAULT_NUM_MEASURES
        # `pattern_resolution` allows creating patterns with more notes per measure than the meter.beats_per_measure
        # For example if we use the default Meter of 4/4 we would have 4 beats per measure and a beat would be
        #  a quarter note. With no pattern resolution argument, patterns are 4 notes per measure. But if
        #  pattern_resolution is passed in as an eighth note, then the patterns would have 4 * (1/4 / 1/8) == 8 notes.
        self.pattern_resolution = pattern_resolution or Sequencer.DEFAULT_PATTERN_RESOLUTION
        self.notes_per_measure = meter.beats_per_measure * (meter.beat_note_dur / self.pattern_resolution)

    def add_track(self) -> int:
        track = Track(meter=self.meter, swing=self.swing, name=str(self._next_track))
        self.append(track)
        self.num_tracks += 1
        track_id = self._next_track
        self._next_track += 1
        return track_id

    # TODO CSound version of this class that just takes pitch and amplitude as floats, so no chord or octave support.
    def add_pattern_to_track(self,
                             track_id: int = None,
                             pattern: str = None,
                             quantize: bool = False,
                             apply_swing: bool = False) -> None:
        """
        Pattern language:
          - Notes have 4 elements: Pitch:Octave:Chord:Amplitude
          - Chord is optional. Optional elements are simply no characters long.
          - Elements in a Note entry are delimited with colons
          - Rests are '.' entries
          - Measures are '|'
          - If the pattern has more measures than self.num_measures an Exception is raised
          - If the pattern has fewer measures than self.num_measures then it is repeated to generate the measures.
            - The number of measures in pattern does not need to evenly divide self.num_measures.
        C:4:MajorSeventh:100 . . .|. . E:5::110 .
        """
        self.track_list[track_id].extend(to_add=self._parse_pattern_to_section(pattern=pattern,
                                                                               quantize=quantize,
                                                                               apply_swing=apply_swing))

    def add_pattern_as_track(self, pattern: str, quantize: bool = False, apply_swing: bool = False) -> int:
        """
        Adds the pattern as a new track of measures constructed from the pattern. Increments the internal count
        of tracks.
        """
        track_id = self.add_track()
        self.track_list[track_id].extend(to_add=self._parse_pattern_to_section(pattern=pattern,
                                                                               quantize=quantize,
                                                                               apply_swing=apply_swing))
        return track_id

    def _parse_pattern_to_section(self, pattern: str, quantize: bool = False, apply_swing: bool = False) -> Section:
        section = Section([])

        measure_tokens = [t.strip() for t in pattern.split(Sequencer.MEASURE_TOKEN)]
        for measure_token in measure_tokens:
            note_tokens = [t.strip() for t in measure_token.split(' ')]
            if len(note_tokens) != self.notes_per_measure:
                raise InvalidPatternException((f'Invalid pattern \'{pattern}\' has {len(note_tokens)} tokens '
                                               f'but notes_per_measure is {self.notes_per_measure}'))

            measure = Measure(meter=self.meter, swing=self.swing)

            # Counter of actual number of notes to allocate for the Measure. This might be > than the number of
            #  note tokens because we support chords. Each chord adds 3-5 notes to the measure, not 1.
            next_start = 0
            duration = self.attr_get_type_cast_map['duration'](self.pattern_resolution.value)
            for i, note_token in enumerate(note_tokens):
                start = self.attr_get_type_cast_map['start'](next_start)

                # It's a single sounding note or rest
                if note_token == Sequencer.REST_TOKEN:
                    note_vals = NoteValues(self.attr_vals_defaults_map.keys())
                    note_vals.start = start
                    note_vals.duration = duration
                    note_vals.amplitude = self.attr_get_type_cast_map['amplitude'](0)
                    # Dummy pitch value
                    note_vals.pitch = self.attr_get_type_cast_map['pitch'](1)
                    note = NoteSequence.make_note(make_note=self._make_note,
                                                  num_attributes=self.num_attributes,
                                                  attr_name_idx_map=self.attr_name_idx_map,
                                                  attr_vals_defaults_map=note_vals.as_dict())
                    measure.append(note)
                # It's a sounding note or chord
                else:
                    key, octave, chord, amplitude = note_token.split (Sequencer.NOTE_TOKEN_DELIMITER)
                    # Only major or minor notes supported
                    key = MAJOR_KEY_DICT.get(key) or MINOR_KEY_DICT.get(key)
                    if not key:
                        raise InvalidPatternException (f'Pattern \'{pattern}\' has invalid key {key} token')
                    octave = int(octave)
                    amplitude = self.attr_get_type_cast_map['amplitude'](amplitude)

                    if chord:
                        # Chord can be empty, but if there is a token it must be valid
                        harmonic_chord = HARMONIC_CHORD_DICT.get(chord)
                        if not harmonic_chord:
                            raise InvalidPatternException (f'Pattern \'{pattern}\' has invalid chord {chord} token')
                        chord = Chord(harmonic_chord=harmonic_chord,
                                      octave=octave,
                                      key=key,
                                      get_pitch_for_key=self._pitch_for_key_cb,
                                      make_note=self._make_note,
                                      num_attributes=self.num_attributes,
                                      attr_name_idx_map=self.attr_name_idx_map,
                                      attr_vals_defaults_map=self.attr_vals_defaults_map,
                                      attr_get_type_cast_map=self.attr_get_type_cast_map)
                        measure.extend(to_add=chord)
                    else:
                        note_vals = NoteValues(self.attr_vals_defaults_map.keys ())
                        note_vals.start = start
                        note_vals.duration = duration
                        note_vals.amplitude = amplitude
                        note_vals.pitch = self._pitch_for_key_cb(key, octave)
                        note = NoteSequence.make_note(make_note=self._make_note,
                                                      num_attributes=self.num_attributes,
                                                      attr_name_idx_map=self.attr_name_idx_map,
                                                      attr_vals_defaults_map=note_vals.as_dict())
                        measure.append (note)

            next_start += self.pattern_resolution.value
            if quantize:
                measure.quantize()
            if apply_swing:
                measure.apply_swing()

            section.append(measure)

        return section

    @property
    def tempo(self) -> int:
        return self.meter.tempo_qpm

    @tempo.setter
    def tempo(self, tempo: int) -> None:
        self.meter = Meter(beat_note_dur=self.meter.beat_note_dur,
                           beats_per_measure=self.meter.beats_per_measure,
                           tempo=tempo)
