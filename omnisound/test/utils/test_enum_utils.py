from enum import Enum

import pytest

from omnisound.src.utils.enum_utils import enum_to_dict, enum_to_dict_reverse_mapping, enum_to_str_key_dict


class TestEnum(Enum):
    A = 1
    B = 2


def test_enum_to_dict():
    expected_dict = {
        TestEnum.A: 1,
        TestEnum.B: 2
    }
    assert enum_to_dict(TestEnum) == expected_dict


def test_enum_to_dict_reverse_mapping():
    expected_dict = {
        1: TestEnum.A,
        2: TestEnum.B
    }
    assert enum_to_dict_reverse_mapping(TestEnum) == expected_dict


def test_enum_to_str_key_dict():
    expected_dict = {
        'A': TestEnum.A,
        'B': TestEnum.B
    }
    assert enum_to_str_key_dict(TestEnum) == expected_dict


if __name__ == '__main__':
    pytest.main(['-xrf'])
