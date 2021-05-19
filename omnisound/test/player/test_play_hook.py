# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.src.player.play_hook import PlayHook

PLAY_HOOK_NAME = 'foo'


def foo():
    pass


@pytest.fixture
def play_hook():
    return PlayHook()


def test_init_state(play_hook):
    assert not play_hook.pre_play_hooks
    assert not play_hook.pre_play_hooks_list
    assert not play_hook.post_play_hooks
    assert not play_hook.post_play_hooks_list


def test_add_hook(play_hook):
    expected_play_hooks = {PLAY_HOOK_NAME: foo}
    expected_play_hooks_list = [foo]

    play_hook.add_pre_play_hook (PLAY_HOOK_NAME, foo)
    assert play_hook.pre_play_hooks == expected_play_hooks
    assert play_hook.pre_play_hooks_list == expected_play_hooks_list
    play_hook.add_post_play_hook(PLAY_HOOK_NAME, foo)
    assert play_hook.post_play_hooks == expected_play_hooks
    assert play_hook.post_play_hooks_list == expected_play_hooks_list
