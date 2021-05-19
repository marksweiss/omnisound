# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.src.player.ensemble import Ensemble
from omnisound.src.player.player import Player


PLAY_HOOK_NAME = 'foo'

def foo():
    pass


@pytest.fixture
def players():
    return [Player()]


@pytest.fixture
def ensemble(players):
    return Ensemble(to_add=players)


def test_init_state(players, ensemble):
    assert not ensemble.pre_play_hooks
    assert not ensemble.pre_play_hooks_list
    assert not ensemble.post_play_hooks
    assert not ensemble.post_play_hooks_list

    # len and getitem
    assert len(ensemble) == 1
    player = ensemble[0]
    assert player.improvising == players[0].improvising
    assert player.pre_play_hooks == players[0].pre_play_hooks


def test_container(players, ensemble):
    player = ensemble[0]

    # iter ane next
    assert ensemble.index == 0
    for player in ensemble:
        assert player
        assert player.improvising == players[0].improvising
        assert player.pre_play_hooks == players[0].pre_play_hooks
    assert ensemble.index == 1

    # append
    ensemble.append(to_add=player)
    assert len(ensemble) == 2
    ensemble << player
    assert len(ensemble) == 3

    # extend
    ensemble.extend(to_add=players)
    assert len(ensemble) == 4

    # remove
    new_player = Player()
    hooks = {PLAY_HOOK_NAME: foo}
    new_player.pre_play_hooks = hooks
    ensemble.append(new_player)
    assert any(player.pre_play_hooks == hooks for player in ensemble)
    ensemble.remove(new_player)
    for player in ensemble:
        assert player.pre_play_hooks != hooks