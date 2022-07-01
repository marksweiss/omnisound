# Copyright 2021 Mark S. Weiss

from typing import Iterator, Optional, Sequence, TypeVar, Union

from omnisound.src.player.play_hook import PlayHook

T = TypeVar('T')

class Ensemble(PlayHook):
    # Each composition defines its own Player class
    def __init__(self, to_add: Optional[Sequence[T]]):
        super().__init__()
        self.players = list(to_add)
        self.index = 0

    # Manage iter/slice
    def __len__(self) -> int:
        return len(self.players)

    def __getitem__(self, index: Union[int, slice]) -> T:
        if isinstance(index, int):
            return self.players.__getitem__(index)
        # This amazing hack from here: https://stackoverflow.com/questions/2936863/implementing-slicing-in-getitem
        if isinstance(index, slice):
            return [self.__getitem__(i) for i in range(*index.indices(len(self)))]

    def __iter__(self) -> Iterator[T]:
        self.index = 0
        return self

    def __next__(self) -> T:
        if self.index == len(self):
            raise StopIteration
        player = self.__getitem__(self.index)
        self.index += 1
        return player

    def append(self, to_add: T) -> 'Ensemble':
        self.players.append(to_add)
        return self

    def extend(self, to_add: Sequence[T]) -> 'Ensemble':
        for ta in to_add:
            self.players.append(ta)
        return self

    def __add__(self, to_add: T) -> 'Ensemble':
        if isinstance(to_add, Ensemble):
            return self.extend(to_add)
        else:
            return self.append(to_add)

    def __lshift__(self, to_add: T) -> 'Ensemble':
        return self.__add__(to_add)

    def insert(self, index: int, to_insert: T) -> 'Ensemble':
        self.players.insert(index, to_insert)
        return self

    def remove(self, to_remove: T) -> 'Ensemble':
        self.players.remove(to_remove)
        return self

    @staticmethod
    def copy(source: 'Ensemble') -> 'Ensemble':
        copy = Ensemble(to_add=source.players)
        copy.index = source.index
        copy_play_hook = PlayHook.copy(source)
        copy.pre_play_hooks = copy_play_hook.pre_play_hooks
        copy.pre_play_hooks_list = copy_play_hook.pre_play_hooks_list
        copy.post_play_hooks = copy_play_hook.post_play_hooks
        copy.post_play_hooks_list = copy_play_hook.post_play_hooks_list
        return copy
