# Copyright 2018 Mark S. Weiss

from typing import Union

import midi

from aleatoric.note.adapters.note import Note
from aleatoric.note.containers.note_sequence import NoteSequence
from aleatoric.note.modifiers.meter import NoteDur
from aleatoric.player.player import Player, PlayerNoNotesException
from aleatoric.utils.utils import validate_type_choice, validate_types


class MidiPlayer(Player):
    MIDI_TICKS_PER_QUARTER_NOTE = 960
    MIDI_QUARTER_NOTES_PER_BEAT = 4
    MIDI_BEATS_PER_MINUTE = 120
    MIDI_TICKS_PER_SECOND = int((MIDI_TICKS_PER_QUARTER_NOTE *
                                 MIDI_QUARTER_NOTES_PER_BEAT *
                                 MIDI_BEATS_PER_MINUTE)
                                / 60)

    DEFAULT_BEAT_DURATION = NoteDur.QUARTER

    def __init__(self, note_sequence: NoteSequence, beats_per_minute: int = None):
        super(MidiPlayer, self).__init__(note_sequence)
        self.beats_per_minute = beats_per_minute
        self.beat_duration = MidiPlayer.DEFAULT_BEAT_DURATION
        # TODO THIS IS A BASE CLASS ATTRIBUTE
        self.current_start = 0.0

    def play_each(self):
        if not self.notes:
            raise PlayerNoNotesException('No notes to play')
        # for note in self.notes:
        #     performance_attrs = note.pa.as_dict()
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def play_all(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        # for note in self.notes:
        #     performance_attrs = note.pa.as_dict()
        #     self.sc_player >> note.instrument([note.degree],
        #                                       dur=note.dur,
        #                                       amp=note.amp,
        #                                       **performance_attrs)
        #     sleep(note.dur)
        #     self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('MidiPlayer does not support improvising')

    def _note_duration_to_ticks(self, note: Note = None,
                           beats_per_measure: int = None,
                           beat_dur: NoteDur = None):
        validate_types(('note', note, Note), ('beats_per_measure', beats_per_measure, int),
                       ('beat_dur', beat_dur, NoteDur))
        return note.dur *


    @staticmethod
    def _seconds_to_ticks(duration_seconds: Union[float, int] = None) -> int:
        validate_type_choice('duration_seconds', duration_seconds, (float, int))
        return int(duration_seconds / MidiPlayer.MIDI_TICKS_PER_SECOND)

        # 960 ticks per qn
        # 4 q per beat
        # 60 bpm
        # 240 qpm
        # 240 * 960 / 60

        # adjbpm = int (60.0 * 1000000.0 / tempo)
        # 60 seconds * 1M (ticks per second) / beats per minute
        # 1M (ticks per second) / beats per minute * 60
        # 1M (ticks per second) / beats per second
