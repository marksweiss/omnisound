# Copyright 2018 Mark S. Weiss

import pytest

from aleatoric.utils import *
from aleatoric.test.test_globals import ENUM_VAL, TestEnum


ARG_NAME = 'arg'


def test_enum_to_dict():
    expected_dict = {TestEnum.ENUM_NAME: ENUM_VAL}
    actual_dict = enum_to_dict('TestEnum', TestEnum)
    assert expected_dict == actual_dict


def test_enum_to_dict_reverse_mapping():
    expected_dict = {ENUM_VAL: TestEnum.ENUM_NAME}
    actual_dict = enum_to_dict_reverse_mapping('TestEnum', TestEnum)
    assert expected_dict == actual_dict


def test_sign():
    for _ in range(10):
        assert sign() in {1, -1}


def test_validate_not_none():
    val = None
    with pytest.raises(ValueError):
        validate_not_none(ARG_NAME, val)

    val = 'NOT_NONE'
    assert validate_not_none(ARG_NAME, val)


if __name__ == '__main__':
    pytest.main(['-xrf'])
