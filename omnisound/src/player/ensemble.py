# Copyright 2021 Mark S. Weiss

from typing import Iterator, Optional, Sequence, Union

from omnisound.src.player.player import Player
from omnisound.src.player.play_hook import PlayHook
from omnisound.src.utils.validation_utils import validate_sequence_of_type, validate_type


class Ensemble(PlayHook):
    def __init__(self, to_add: Optional[Sequence[Player]]):
        super().__init__()
        self._players = list(to_add)
        self.index = 0

    # Manage iter/slice
    def __len__(self) -> int:
        return len(self._players)

    def __getitem__(self, index: Union[int, slice]) -> Player:
        if isinstance(index, int):
            return self._players.__getitem__(index)
        # This amazing hack from here: https://stackoverflow.com/questions/2936863/implementing-slicing-in-getitem
        if isinstance(index, slice):
            return [self.__getitem__(i) for i in range(*index.indices(len(self)))]

    def __iter__(self) -> Iterator[Player]:
        self.index = 0
        return self

    def __next__(self) -> Player:
        if self.index == len(self):
            raise StopIteration
        player = self.__getitem__(self.index)
        self.index += 1
        return player

    def append(self, to_add: Player) -> 'Ensemble':
        validate_type('to_add', to_add, Player)
        self._players.append(to_add)

    def extend(self, to_add: Sequence[Player]) -> 'Ensemble':
        validate_sequence_of_type('to_add', to_add, Player)
        for ta in to_add:
            self._players.append(ta)

    def __add__(self, to_add: Player) -> 'Ensemble':
        validate_type('to_add', to_add, Player)
        if isinstance(to_add, Ensemble):
            return self.extend(to_add)
        else:
            return self.append(to_add)

    def __lshift__(self, to_add: Player) -> 'Ensemble':
        return self.__add__(to_add)

    def insert(self, index: int, to_insert: Player) -> 'Ensemble':
        validate_type('index', index, int)
        validate_type('to_insert', to_insert, Player)
        self._players.insert(index, to_insert)
        return self

    def remove(self, to_remove: Player) -> 'Ensemble':
        validate_type('to_remove', to_remove, Player)
        self._players.remove(to_remove)
        return self

    @staticmethod
    def copy(source: 'Ensemble') -> 'Ensemble':
        validate_type('source', source, Ensemble)
        copy = Ensemble(to_add=source._players)
        copy.index = source.index
        copy_play_hook = PlayHook.copy(source)
        copy.pre_play_hooks = copy_play_hook.pre_play_hooks
        copy.pre_play_hooks_list = copy_play_hook.pre_play_hooks_list
        copy.post_play_hooks = copy_play_hook.post_play_hooks
        copy.post_play_hooks_list = copy_play_hook.post_play_hooks_list
        return copy

