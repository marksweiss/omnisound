# Copyright 2018 Mark S. Weiss

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, List


class PlayerNoNotesException(Exception):
    pass


class PlayerBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def song(self):
        """Player has a Song attribute that can be a source of notes to be played by the play*() methods"""
        raise NotImplementedError()

    @song.setter
    @abstractmethod
    def song(self, song):
        raise NotImplementedError()


class Player(PlayerBase):
    def __init__(self):
        self.improvising = False
        self.pre_play_hooks: Dict[str, Callable] = {}
        self.pre_play_hooks_list: List[Callable] = []
        self.post_play_hooks: Dict[str, Callable] = {}
        self.post_play_hooks_list: List[Callable] = []

    def add_pre_play_hook(self, name: str, hook: Any):
        self._add_hook(name, hook, self.pre_play_hooks, self.pre_play_hooks_list)

    def add_post_play_hook(self, name: str, hook: Any):
        self._add_hook(name, hook, self.post_play_hooks, self.post_play_hooks_list)

    @staticmethod
    def _add_hook(name, hook, hooks, hooks_list):
        if not (
                name and isinstance(name, str) and hook and '__call__' in dir(hook)
        ):
            raise ValueError(f'args `name` must be a non-empty string and `hook` must be a callable')
        hooks[name] = hook
        hooks_list.append(hook)

    def remove_pre_play_hook(self, name: str):
        self._remove_hook(name, self.pre_play_hooks, self.pre_play_hooks_list)

    def remove_post_play_hook(self, name: str):
        self._remove_hook(name, self.post_play_hooks, self.post_play_hooks_list)

    @staticmethod
    def _remove_hook(name, hooks, hooks_list):
        if not (name and isinstance(name, str)):
            raise ValueError(f'arg `name` must be a non-empty string')
        hook = hooks.get(name)
        if hook:
            hooks_list.remove(hook)
            del hooks[name]

    @abstractmethod
    def play_each(self):
        """Play each note. Each notes note_attr_vals are honored and
           separate performance_attrs with a matching index are applied
           to all notes in the batch if they are available.

           Implementers can choose to use pre-play or post-play hooks as they wish.
        """
        raise NotImplementedError()

    @abstractmethod
    def play(self):
        """Play notes as a batch. Each notes note_attr_vals are honored but
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

    @abstractmethod
    def loop(self):
        """Player generates notes according to the concrete class implementation and plays them. When the sequence
        end is reached, the player plays the sequence again from the beginning. This should be implemented to
        repeat until a KeyboardInterrupt exception is raised.
        """
        raise NotImplementedError()


class Writer(PlayerBase):
    @abstractmethod
    def generate(self):
        """Generates note events in a form compatible with a particular back end, in memory, from an Omnisound Song.
        For MidiWriter this would be a sequence of MIDI note events using the MIDI backend library mido. For CSound
        it is the text of a CSound *.sco score file, as a string.
        """
        raise NotImplementedError()

    @abstractmethod
    def write(self):
        """Writes notes generated by the instance to a file of a type matching a back end. For the MidiWriter
        this is a MIDI file, for the CSoundWriter its a CSound CSD file, etc.
        """
        raise NotImplementedError()
