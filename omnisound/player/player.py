# Copyright 2018 Mark S. Weiss

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, List

from omnisound.note.containers.note_sequence import NoteSequence
from omnisound.utils.utils import validate_type


class PlayerNoNotesException(Exception):
    pass


class Player(metaclass=ABCMeta):
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

    @property
    @abstractmethod
    def song(self):
        """Player has a Song attribute that can be a source of notes to be played by the play*() methods"""
        raise NotImplementedError()

    def __init__(self):
        self.improvising = False
        self.pre_play_hooks: Dict[str, Callable] = {}
        self.pre_play_hooks_list: List[Callable] = []
        self.post_play_hooks: Dict[str, Callable] = {}
        self.post_play_hooks_list: List[Callable] = []

    # TODO REMOVE
    # @property
    # def notes(self):
    #     return self.note_sequence

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
