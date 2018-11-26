# Copyright 2018 Mark S. Weiss

from time import sleep

from abc import abstractmethod, ABCMeta
from typing import Any, Dict, List

from FoxDot import Player as FD_SC_Player
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import sinepad as fd_sc_synth

from aleatoric.note import Note, NoteSequence, PerformanceAttrs, FoxDotSupercolliderNote


class PlayerNoNotesException(Exception):
    pass


class Player(metaclass=ABCMeta):
    @abstractmethod
    def play_each(self):
        """Play each note. Each notes note_attrs are honored and
           separate performance_attrs with a matching index are applied
           to all notes in the batch if they are available.

           Implementers can choose to use pre-play or post-play hooks as they wish.
        """
        raise NotImplementedError()

    @abstractmethod
    def play_all(self):
        """Play notes as a batch. Each notes note_attrs are honored but
           performance_attrs are applied to all notes in the batch.

           Implementers can choose to use pre-play or post-play hooks as they wish.
        """
        raise NotImplementedError()

    @abstractmethod
    def improvise(self):
        """Player generates notes according to the concrete class implementation and plays them.

           Implementers should handle checking the state of self.improvising == False.
        """
        raise NotImplementedError()

    def __init__(self, note_sequence: NoteSequence):
        if not isinstance(note_sequence, NoteSequence):
            raise ValueError(f'arg `note_sequence` must be type `NoteSequence`, note_sequence: {note_sequence}')
        self.note_sequence = note_sequence
        self.improvising = False
        self.pre_play_hooks: Dict[str, Any] = {}
        self.pre_play_hooks_list: List[Any] = []
        self.post_play_hooks: Dict[str, int] = {}
        self.post_play_hooks_list: List[Any] = []

    @property
    def notes(self):
        return self.note_sequence

    def add_pre_play_hook(self, name: str, hook: Any):
        self._add_hook(name, hook, self.pre_play_hooks, self.pre_play_hooks_list)

    def add_post_play_hook(self, name: str, hook: Any):
        self._add_hook(name, hook, self.post_play_hooks, self.post_play_hooks_list)

    @staticmethod
    def _add_hook(name, hook, hooks, hooks_list):
        if not name or not isinstance(name, str) or not hook or '__call__' not in dir(hook):
            raise ValueError(f'args `name` must be a non-empty string and `hook` must be a callable')
        hooks[name] = hook
        hooks_list.append(hook)

    def remove_pre_play_hook(self, name: str):
        self._remove_hook(name, self.pre_play_hooks, self.pre_play_hooks_list)

    def remove_post_play_hook(self, name: str):
        self._remove_hook(name, self.post_play_hooks, self.post_play_hooks_list)

    @staticmethod
    def _remove_hook(name, hooks, hooks_list):
        if not name or not isinstance(name, str):
            raise ValueError(f'arg `name` must be a non-empty string')
        hook = hooks.get(name)
        if hook:
            hooks_list.remove(hook)
            del hooks[name]


class FoxDotSupercolliderPlayer(Player):
    def __init__(self, note_sequence: NoteSequence):
        super(FoxDotSupercolliderPlayer, self).__init__(note_sequence)
        self.sc_player = FD_SC_Player()

    def play_each(self):
        if not self.notes:
            raise PlayerNoNotesException('No notes to play')
        for note in self.notes:
            performance_attrs = self.notes.pa or note.pa.as_dict()
            self.sc_player >> note.instrument([note.degree],
                                              dur=note.dur,
                                              amp=note.amp,
                                              **performance_attrs)
            sleep(note.dur)
            self.sc_player.stop()

    def play_all(self):
        if not self.notes:
            raise PlayerNoNotesException('No note_group to play')
        for note in self.notes:
            performance_attrs = self.notes.pa or note.pa.as_dict()
            self.sc_player >> note.instrument([note.degree],
                                              dur=note.dur,
                                              amp=note.amp,
                                              **performance_attrs)
            sleep(note.dur)
            self.sc_player.stop()

    def improvise(self):
        raise NotImplementedError('SupercolliderPlayer does not support improvising')


if __name__ == '__main__':
    # This is a test
    performance_attrs = PerformanceAttrs()

    notes = []
    idur = 1.0
    iamp = 1.0
    delay = 0.0
    for i in range(15):
        amp = iamp  # - ((i + 1) * 0.05)
        dur = round(idur - ((i + 1) * 0.05), 5)
        note = FoxDotSupercolliderNote(synth_def=fd_sc_synth,
                                       delay=round(delay, 5), dur=dur, amp=amp, degree=i % 5,
                                       name='test_note',
                                       oct=2, scale='lydian',
                                       performance_attrs=performance_attrs)
        notes.append(note)
        delay += dur

    # Players with notes play each note separately, with its own note_attrs and performance_attrs
    note_sequence = NoteSequence(notes)
    player = FoxDotSupercolliderPlayer(note_sequence)
    player.play_each()

    sleep(3)

    notes = []
    idur = 1.0
    iamp = 1.0
    delay = 0.0
    for i in range(15):
        amp = iamp  # - ((i + 1) * 0.05)
        dur = round(idur - ((i + 1) * 0.05), 5)
        note = FoxDotSupercolliderNote(synth_def=fd_sc_synth,
                                       delay=round(delay, 5), dur=dur * 0.5, amp=amp, degree=(i % 5) + 1,
                                       name='test_note',
                                       oct=5, scale='lydian',
                                       performance_attrs=performance_attrs)
        notes.append(note)
        delay += dur

    # Players with notes play each note separately, with its own note_attrs and performance_attrs
    note_sequence = NoteSequence(notes)
    player = FoxDotSupercolliderPlayer(note_sequence)
    player.play_all()