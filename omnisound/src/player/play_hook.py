# Copyright 2021 Mark S. Weiss

from copy import deepcopy

from typing import Any, Callable, Dict, List

from omnisound.src.utils.validation_utils import validate_type


class PlayHook:
    def __init__(self):
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

    def call_pre_play_hook(self, name: str) -> Callable:
        return self.pre_play_hooks[name]

    def call_post_play_hook(self, name: str) -> Callable:
        return self.post_play_hooks[name]

    @staticmethod
    def _remove_hook(name, hooks, hooks_list):
        if not (name and isinstance(name, str)):
            raise ValueError(f'arg `name` must be a non-empty string')
        hook = hooks.get(name)
        if hook:
            hooks_list.remove(hook)
            del hooks[name]

    @staticmethod
    def copy(source: 'PlayHook') -> 'PlayHook':
        validate_type('source', source, PlayHook)
        copy = PlayHook()
        copy.pre_play_hooks = deepcopy(source.pre_play_hooks)
        copy.pre_play_hooks_list = deepcopy(source.pre_play_hooks_list)
        copy.post_play_hooks = deepcopy(source.post_play_hooks)
        copy.post_play_hooks_list = deepcopy(source.post_play_hooks_list)
        return copy
