# Copyright 2020 Mark S. Weiss

from typing import Optional, Union

from omnisound.note.adapters.note import MakeNoteConfig, NoteValues, set_attr_vals_from_note_values
from omnisound.note.containers.measure import Measure
from omnisound.note.containers.section import Section
from omnisound.note.containers.song import Song
from omnisound.note.containers.track import Track
from omnisound.note.generators.chord import Chord
from omnisound.note.generators.chord_globals import HARMONIC_CHORD_DICT
from omnisound.note.generators.scale import Scale
from omnisound.note.generators.scale_globals import MAJOR_KEY_DICT, MINOR_KEY_DICT
from omnisound.note.modifiers.meter import Meter, NoteDur
from omnisound.note.modifiers.swing import Swing
from omnisound.utils.mingus_utils import get_chord_pitches
from omnisound.utils.utils import (validate_optional_type, validate_optional_type_choice, validate_optional_types,
                                   validate_type, validate_type_choice, validate_types)


class InvalidPatternException(Exception):
    pass


class InvalidAddPatternException(Exception):
    pass


# TODO FACTOR PARSING OF PATTERN LANGUAGE INTO A SEPARATE MODULE SO WE CAN USE IT FOR PLAYERS TOO
#  TRANSLATE 'IN C' TO PATTERN AND DO IT AGAIN
#  ADD MODULES FOR OTHER INPUTS LIKE MusicXML, LilyPond

# TODO USE IT!
# TODO TRANSPOSE SUPPORT
class Sequencer(Song):
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

    DEFAULT_PATTERN_RESOLUTION = NoteDur.QUARTER
    DEFAULT_TEMPO = 120
    DEFAULT_METER = Meter(beat_note_dur=NoteDur.QUARTER, beats_per_measure=4, tempo=DEFAULT_TEMPO)
    DEFAULT_NUM_MEASURES = 4

    MEASURE_TOKEN_DELIMITER = '|'
    REST_TOKEN = '.'
    NOTE_TOKEN_DELIMITER = ':'

    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 pattern_resolution: Optional[NoteDur] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 mn: MakeNoteConfig = None):
        validate_optional_types(('name', name, str),
                                ('swing', swing, Swing),
                                ('pattern_resolution', pattern_resolution, NoteDur))
        validate_type('num_measures', num_measures, int)

        # Sequencer wraps song but starts with no Tracks. It provides an alternate API for generating and adding Tracks.
        to_add = []
        meter = meter or Sequencer.DEFAULT_METER
        super(Sequencer, self).__init__(to_add, name=name, meter=meter, swing=swing)

        # self.make_note = n.make_note
        # self.get_pitch_for_key = n.get_pitch_for_key
        # self.num_attributes = n.num_attributes
        # self.attr_name_idx_map = n.attr_name_idx_map
        # self.attr_vals_defaults_map = n.attr_vals_defaults_map
        # self.attr_get_type_cast_map = n.attr_get_type_cast_map
        self.mn = mn

        self.num_measures = num_measures or Sequencer.DEFAULT_NUM_MEASURES
        # `pattern_resolution` allows creating patterns with more notes per measure than the meter.beats_per_measure
        # For example if we use the default Meter of 4/4 we would have 4 beats per measure and a beat would be
        #  a quarter note. With no pattern resolution argument, patterns are 4 notes per measure. But if
        #  pattern_resolution is passed in as an eighth note, then the patterns would have 4 * (1/4 / 1/8) == 8 notes.
        self.pattern_resolution = pattern_resolution or Sequencer.DEFAULT_PATTERN_RESOLUTION
        self.notes_per_measure = int(meter.beats_per_measure *
                                     (meter.beat_note_dur.value / self.pattern_resolution.value))
        self.note_duration = \
            self.mn.attr_get_type_cast_map['duration'](self.meter.measure_dur_secs / self.notes_per_measure)

        self.num_tracks = 0
        # Internal index to the next track to create when add_track() or add_pattern_as_track() are called
        self._next_track = 0
        self._track_name_idx_map = {}

    # TODO Validate instrument is int, MidiInstrument enum or a class (Foxdot)
    def add_track(self,
                  track_name: str = None,
                  instrument: Union[float, int] = None) -> str:
        validate_type('track_name', track_name, str)
        validate_type_choice('instrument', instrument, (float, int))

        track_name = track_name or str(self._next_track)
        track = Track(meter=self.meter,
                      swing=self.swing, name=track_name,
                      instrument=instrument)
        self.append(track)
        self.num_tracks += 1
        self._track_name_idx_map[track_name] = self._next_track
        self._next_track += 1
        return track_name

    def set_track_pattern(self,
                          track_name: str = None,
                          pattern: str = None,
                          instrument: Optional[Union[float, int]] = None,
                          swing: Optional[Swing] = None):
        """
        - Sets the pattern, a section of measures in the track named `track_name`.
        - If the track already has a pattern, it is replaced. If the track is empty, its pattern is set to `pattern`.
        - If `swing` is arg is supplied, then the track will have swing applied using it
        - If the `instrument` arg is supplied, this instrument will be bound to the track, replacing whatever
          instrument it previously was bound to
        - If the `apply_swing` arg is True and the class has `self.swing` then the class swing
          object will be used to apply swing
        """
        validate_types(('track_name', track_name, str), ('pattern', pattern, str))
        validate_optional_type('swing', swing, Swing)
        validate_optional_type_choice('instrument', instrument, (float, int))

        # Will raise if track_name is not valid
        track = self.track_list[self._track_name_idx_map[track_name]]
        if track.measure_list:
            track.remove((0, self.num_measures))
        instrument = instrument or track.instrument
        section = self._parse_pattern_to_section(pattern=pattern, instrument=instrument)
        if len(section) < self.num_measures:
            self._fill_section_to_track_length(section)
        track.extend(to_add=section)
        swing = swing or self.swing
        if swing and swing.is_swing_on():
            track.apply_swing()

    def add_pattern_as_new_track(self,
                                 track_name: Optional[str] = None,
                                 pattern: str = None,
                                 instrument: Union[float, int] = None,
                                 swing: Optional[Swing] = None):
        """
        - Sets the pattern, a section of measures in a new track named `track_name` or if no name is provided
          in a track with a default name of its track number.
        - Track is bound to `instrument`
        - If `track_name` is not supplied, a default name of `Track N`, where N is the index of the track, is assigned
        - If `swing` is arg is supplied and `is_swing_on()` is `True`, then the track will have swing applied using it
        - If `self.swing` `is_swing_on()` is `True` then the track will have swing applied using it
        """
        validate_type('pattern', pattern, str)
        validate_optional_types(('track_name', track_name, str), ('swing', swing, Swing))
        validate_type_choice('instrument', instrument, (float, int))

        # Set the measures in the section to add to the track
        section = self._parse_pattern_to_section(pattern=pattern, instrument=instrument)
        # If the section is shorter than num_measures, the length of all tracks, repeat it to fill the track
        if len(section) < self.num_measures:
            self._fill_section_to_track_length(section)

        # Create the track, add the section to it, apply quantize and swing according to the logic in the docstring
        track_name = track_name or str(self._next_track)
        self._track_name_idx_map[track_name] = self._next_track
        swing = swing or self.swing
        track = Track(name=track_name, meter=self.meter, swing=swing)
        track.extend(to_add=section)
        if swing and swing.is_swing_on():
            track.apply_swing()

        # Add the track to the sequencer, update bookkeeping
        self.append(track)
        self.num_tracks += 1
        self._next_track += 1

        return track_name

    def track_names(self):
        return '\n'.join(self._track_name_idx_map.keys())

    def _fill_section_to_track_length(self, section: Section):
        """
        Implements logic to repeat a pattern shorter than `self.num_measures` to fill out the measures in the track.
        The logic is simple `divmod()`, repeat as many times as needed and if the pattern doesn't fit evenly then
        the last repeat is partial and cuts off on whatever measure reaches `num_measures`.
        """
        # We already have a section of the length of the pattern, so subtract that
        quotient, remainder = divmod(self.num_measures - len(section), len(section))
        section_cpy = Section.copy(section)
        for i in range(quotient):
            # TODO REFACTOR TO RENAME EXTEND()
            section.extend(Section.copy(section_cpy).measure_list)
        section.extend(Section.copy(section_cpy).measure_list[0:remainder])

    # TODO MORE SOPHISTICATED PARSING IF WE EXTEND THE PATTERN LANGUAGE
    def _parse_pattern_to_section(self,
                                  pattern: str = None,
                                  instrument: Union[float, int] = None,
                                  swing: Swing = None) -> Section:
        section = Section([])
        swing = swing or self.swing

        def _make_note_val(_instrument, _start, _duration, _amplitude, _pitch):
            _note_vals = NoteValues(self.mn.attr_vals_defaults_map.keys ())
            _note_vals.instrument = _instrument
            _note_vals.start = _start
            _note_vals.duration = _duration
            _note_vals.amplitude = _amplitude
            _note_vals.pitch = _pitch
            return _note_vals

        measure_tokens = [t.strip() for t in pattern.split(Sequencer.MEASURE_TOKEN_DELIMITER)]
        for measure_token in measure_tokens:
            note_tokens = [t.strip() for t in measure_token.split()]
            if len(note_tokens) != self.notes_per_measure:
                raise InvalidPatternException(('Invalid pattern '
                                               f'\'{pattern.split(Sequencer.MEASURE_TOKEN_DELIMITER)[0]} | ...\' '
                                               f'has {len(note_tokens)} tokens per measure '
                                               f'but notes_per_measure is {self.notes_per_measure}'))

            next_start = 0
            note_vals_lst = []
            for i, note_token in enumerate(note_tokens):
                start = self.mn.attr_get_type_cast_map['start'](next_start)

                # It's a single sounding note or rest
                if note_token == Sequencer.REST_TOKEN:
                    # Dummy values
                    amplitude = self.mn.attr_get_type_cast_map['amplitude'](0)
                    pitch = self.mn.attr_get_type_cast_map['pitch'](1)
                    note_vals = _make_note_val(instrument, start, self.note_duration, amplitude, pitch)
                    note_vals_lst.append(note_vals)
                # It's a sounding note or chord
                else:
                    key, octave, chord, amplitude = note_token.split(Sequencer.NOTE_TOKEN_DELIMITER)

                    # Only major or minor notes supported
                    key = MAJOR_KEY_DICT.get(key) or MINOR_KEY_DICT.get(key)
                    if not key:
                        raise InvalidPatternException(f'Pattern \'{pattern}\' has invalid key {key} token')

                    octave = int(octave)
                    amplitude = self.mn.attr_get_type_cast_map['amplitude'](amplitude)

                    if chord:
                        # Chord can be empty, but if there is a token it must be valid
                        harmonic_chord = HARMONIC_CHORD_DICT.get(chord)
                        if not harmonic_chord:
                            raise InvalidPatternException(f'Pattern \'{pattern}\' has invalid chord {chord} token')

                        key_type = Chord.get_key_type(key, harmonic_chord)
                        mingus_key_to_key_enum_mapping = Scale.get_mingus_key_to_key_enum_mapping(key_type)
                        mingus_chord = Chord.get_mingus_chord_for_harmonic_chord(key, harmonic_chord)
                        chord_pitches = get_chord_pitches(mingus_keys=mingus_chord,
                                                          mingus_key_to_key_enum_mapping=mingus_key_to_key_enum_mapping,
                                                          get_pitch_for_key=self.mn.get_pitch_for_key,
                                                          octave=octave)
                        for pitch in chord_pitches:
                            note_vals = _make_note_val(instrument, start, self.note_duration, amplitude, pitch)
                            note_vals_lst.append(note_vals)
                    else:
                        pitch = self.mn.get_pitch_for_key(key, octave)
                        note_vals = _make_note_val(instrument, start, self.note_duration, amplitude, pitch)
                        note_vals_lst.append(note_vals)

                next_start += self.note_duration

            measure = Measure(num_notes=len(note_vals_lst),
                              meter=self.meter,
                              swing=swing,
                              mn=MakeNoteConfig.copy(self.mn))
            for i, note_vals in enumerate(note_vals_lst):
                note = measure.note(i)
                set_attr_vals_from_note_values(note, note_vals)

            section.append(measure)

        return section

    def track(self, track_name: str):
        return self.track_list[self._track_name_idx_map[track_name]]

    @property
    def tempo(self) -> int:
        return self.meter.tempo_qpm

    # TODO THIS HAS NO IMPACT BECAUSE METER DOESN'T REALLY SUPPORT TEMPO RIGHT NOW
    @tempo.setter
    def tempo(self, tempo: int) -> None:
        """
        Sets the meter.tempo_qpm to the tempo value provided. Also recursively traverses down to every measure
        in every section in every track, rebuilding the measures notes to adjust their start times to use the
        new meter with the new tempo.
        """
        validate_type('tempo', tempo, int)

        # Make a new meter object set to the new tempo and assign it to the sequencer
        self.meter = Meter(beat_note_dur=self.meter.beat_note_dur,
                           beats_per_measure=self.meter.beats_per_measure,
                           tempo=tempo)

        for track in self.track_list:
            self._set_tempo_for_track(track)

    # TODO THIS HAS NO IMPACT BECAUSE METER DOESN'T REALLY SUPPORT TEMPO RIGHT NOW
    def set_tempo_for_track(self, track_name: str = None, tempo: int = None):
        validate_types(('track_name', track_name, str), ('tempo', tempo, int))
        track = self.track_list[self._track_name_idx_map[track_name]]
        self._set_tempo_for_track(track)

    def _set_tempo_for_track(self, track: Track):
        for i, section in enumerate(track):
            new_section = section.copy(section)
            for j, measure in enumerate(section):
                # Make a shallow copy of the measure, with the new meter with the new tempo. This ctor will
                # allocate storage for new notes, but they won't have values set.
                new_measure = Measure(meter=self.meter,
                                      swing=self.swing,
                                      num_notes = measure.num_notes,
                                      mn=measure.mn)

                # For each note in the old measure, copy it to the new measure but let the Measure API
                # manage adding it at the correct start time calculated with the new meter using the new tempo.
                for k in range(len(measure)):
                    # Automatically increments start time of each note added
                    new_measure.add_notes_on_start(measure.note(k))

                # Now replace the old measure with the new one in the section
                # TODO Add swap() API to NoteSequence and it's children
                section.remove((j, j + 1))
                section.insert(j, new_measure)

            # TODO Add swap() API to NoteSequence and it's children
            track.remove((i, i + 1))
            track.insert(i, section)
