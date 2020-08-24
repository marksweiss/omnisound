# Copyright 2018 Mark S. Weiss

from abc import abstractmethod
from typing import Any, Callable, Dict, List, Sequence

from omnisound.src.container.song import Song
from omnisound.src.utils.validation_utils import validate_type


class PlayerNoNotesException(Exception):
    pass


class PlayerBase:
    def __init__(self, song: Song = None):
        self._song = song
        self.improvising = False
        self.pre_play_hooks: Dict[str, Callable] = {}
        self.pre_play_hooks_list: List[Callable] = []
        self.post_play_hooks: Dict[str, Callable] = {}
        self.post_play_hooks_list: List[Callable] = []

    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        validate_type('song', song, Song)
        self._song = song

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


class Player(PlayerBase):
    def __init__(self, song: Song = None):
        super(Player, self).__init__(song=song)

    @abstractmethod
    def play_each(self) -> Any:
        """Play each note. Each notes note_attr_vals are honored and
           separate performance_attrs with a matching index are applied
           to all notes in the batch if they are available.

           Implementers can choose to use pre-play or post-play hooks as they wish.
        """
        raise NotImplementedError()

    @abstractmethod
    def play(self) -> Any:
        """Play notes as a batch. Each notes note_attr_vals are honored but
           performance_attrs are applied to all notes in the batch.
           Implementers can choose to use pre-play or post-play hooks as they wish.
        """
        raise NotImplementedError()

    @abstractmethod
    def improvise(self) -> Any:
        """Player generates notes according to the concrete class implementation and plays them.
           Implementers should handle checking the state of self.improvising == False.
        """
        raise NotImplementedError()

    @abstractmethod
    def loop(self) -> Any:
        """Player generates notes according to the concrete class implementation and plays them. When the sequence
        end is reached, the player plays the sequence again from the beginning. This should be implemented to
        repeat until a KeyboardInterrupt exception is raised.
        """
        raise NotImplementedError()


class Writer(PlayerBase):
    def __init__(self, song: Song = None):
        super(Writer, self).__init__(song=song)

    @abstractmethod
    def generate(self) -> Sequence[Any]:
        """Generates note events in a form compatible with a particular back end, in memory, from an Omnisound Song.
        For MidiWriter this would be a sequence of MIDI note events using the MIDI backend library mido. For CSound
        it is the text of a CSound *.sco score file, as a string.
        """
        raise NotImplementedError()

    @abstractmethod
    def write(self) -> None:
        """Writes notes generated by the instance to a file of a type matching a back end. For the MidiWriter
        this is a MIDI file, for the CSoundWriter its a CSound CSD file, etc.
        """
        raise NotImplementedError()

    @abstractmethod
    def generate_and_write(self) -> None:
        """Intended as a convenience method that simply calls generate() and then write(). Implementers are free
        to include other logic or side effects etc. as desired, but they should preserve the semantics of providing
        a single call that performs both steps, to simplify the API."""
        raise NotImplementedError()