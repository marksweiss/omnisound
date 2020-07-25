# Copyright 2018 Mark S. Weiss

from enum import Enum

import pytest

from omnisound.utils.enum_utils import enum_to_dict, enum_to_dict_reverse_mapping, enum_to_str_key_dict
from omnisound.utils.math_utils import *
from omnisound.utils.validation_utils import validate_not_falsey, validate_not_none, validate_optional_sequence_of_type, \
    validate_optional_type, \
    validate_optional_types, \
    validate_sequence_of_type, validate_sequence_of_type_choice, validate_type_choice, validate_type_reference, \
    validate_type_reference_choice

ARG_NAME = 'arg'


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


def test_sign():
    for _ in range(10):
        assert sign() in {1, -1}


def test_validate_not_none():
    val = None
    with pytest.raises(ValueError):
        validate_not_none(ARG_NAME, val)

    val = 'NOT_NONE'
    assert validate_not_none(ARG_NAME, val)


def test_validate_optional_sequence_of_types():
    arg_name = 'arg'
    val_type = int

    # Case: None seq_val returns True because validator is *_optional_*()
    seq_val = None
    assert validate_optional_sequence_of_type(arg_name, seq_val, val_type)

    # Case: empty sequence returns True because validator is *_optional_*()
    seq_val = []
    assert validate_optional_sequence_of_type(arg_name, seq_val, val_type)
    seq_val = ()
    assert validate_optional_sequence_of_type(arg_name, seq_val, val_type)
    seq_val = set()
    assert validate_optional_sequence_of_type(arg_name, seq_val, val_type)

    # Case: non-empty sequence in which all elements are of type val_type returns True
    seq_val = [1, 2, 3]
    assert validate_optional_sequence_of_type(arg_name, seq_val, val_type)

    # Case: non-empty sequence in which not all elements are of type val_type raises
    seq_val = [1, 2, 3.0]
    with pytest.raises(ValueError):
        validate_optional_sequence_of_type(arg_name, seq_val, val_type)


def test_validate_sequence_of_types():
    arg_name = 'arg'
    val_type = int

    # Case: non-empty sequence in which all elements are of type val_type returns True
    seq_val = [1, 2, 3]
    assert validate_sequence_of_type(arg_name, seq_val, val_type)

    # Case: non-empty sequence in which not all elements are of type val_type raises
    seq_val = [1, 2, 3.0]
    with pytest.raises(ValueError):
        validate_sequence_of_type(arg_name, seq_val, val_type)


def test_validate_sequence_of_type_choice():
    arg_name = 'arg'
    val_types = {int, float}

    # Case: non-empty sequence in which all elements are of either type returns True
    seq_val = [1, 2, 3]
    assert validate_sequence_of_type_choice(arg_name, seq_val, val_types)
    seq_val = [1.0, 2.0, 3.0]
    assert validate_sequence_of_type_choice(arg_name, seq_val, val_types)
    seq_val = [1, 2, 3.0]
    assert validate_sequence_of_type_choice(arg_name, seq_val, val_types)

    # Case: non-empty sequence in which not all elements are of ether type val_type raises
    seq_val = [1, 2, '3']
    with pytest.raises(ValueError):
        validate_sequence_of_type_choice(arg_name, seq_val, val_types)


def test_validate_optional_type():
    arg_name = 'arg'
    val_type = int

    # Case: None val returns True because validator is *_optional_*()
    val = None
    assert validate_optional_type(arg_name, val, val_type)

    # Case: False-y but not None value of expected type returns True
    val = 0
    assert validate_optional_type(arg_name, val, val_type)

    # Case: Value of expected type returns True
    val = 1
    assert validate_optional_type(arg_name, val, val_type)

    # Case: Value not of expected type raises
    val = 1.0
    with pytest.raises(ValueError):
        validate_optional_type(arg_name, val, val_type)


def test_validate_optional_types():
    # Calls validate_optional_type(), so only test business logic specific to this function
    arg_name_1 = 'arg_1'
    val_type_1 = int
    arg_name_2 = 'arg_2'
    val_type_2 = str

    # Case: Two tuples, both with val of None, passes
    val_1 = None
    val_2 = None
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # Case: Two tuples, one with val type val_type, one with None, passes
    val_1 = 1
    val_2 = None
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # Case: Two tuples with False-y but not None value of expected type returns True
    val_1 = 0
    val_2 = ''
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # Case: Values of expected types returns True
    val_1 = 1
    val_2 = 'I got mad hits like I was Rod Carew'
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # # Case: At least one value not of expected type raises
    with pytest.raises(ValueError):
        val_1 = 1.0
        val_2 = 'I got mad hits like I was Rod Carew'
        assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))
        val_1 = 1
        val_2 = 1
        assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))


def test_validate_types():
    # Calls validate_optional_type(), so only test business logic specific to this function
    arg_name_1 = 'arg_1'
    val_type_1 = int
    arg_name_2 = 'arg_2'
    val_type_2 = str

    # Case: Two tuples with False-y but not None value of expected type returns True
    val_1 = 0
    val_2 = ''
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # Case: Values of expected types returns True
    val_1 = 1
    val_2 = 'I got mad hits like I was Rod Carew'
    assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))

    # # Case: At least one value not of expected type raises
    with pytest.raises(ValueError):
        val_1 = 1.0
        val_2 = 'I got mad hits like I was Rod Carew'
        assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))
        val_1 = 1
        val_2 = 1
        assert validate_optional_types((arg_name_1, val_1, val_type_1), (arg_name_2, val_2, val_type_2))


def test_validate_type_choice():
    arg_name = 'arg'
    val_types = (int, float)

    # Case: Match a type in the list of type choices
    val = 1
    expected_ret = (True, int)
    assert validate_type_choice(arg_name, val, val_types) == expected_ret
    val = 1.0
    expected_ret = (True, float)
    assert validate_type_choice(arg_name, val, val_types) == expected_ret

    # Case: No types in the list match val's type
    val = '1'
    with pytest.raises(ValueError):
        validate_type_choice(arg_name, val, val_types)


def test_validate_type_reference():
    # validate_type_reference(arg_name, type_ref_val, val_type)
    arg_name = 'arg'
    val_type = int

    # Case: variable aliasing a type matches val_type
    type_ref_val = int
    assert validate_type_reference(arg_name, type_ref_val, val_type)

    # Case: variable aliasing a type does not match val_type
    type_ref_val = float
    with pytest.raises(ValueError):
        validate_type_reference(arg_name, type_ref_val, val_type)


def test_validate_type_reference_choice():
    # validate_type_reference(arg_name, type_ref_val, val_type)
    arg_name = 'arg'
    val_types = (int, float)

    # Case: variable aliasing a type matches one of the types in val_types
    type_ref_val = int
    expected_ret = (True, int)
    assert validate_type_reference_choice(arg_name, type_ref_val, val_types) == expected_ret
    type_ref_val = float
    expected_ret = (True, float)
    assert validate_type_reference_choice(arg_name, type_ref_val, val_types) == expected_ret

    # Case: variable aliasing a type does not match any types in val_types
    type_ref_val = str
    with pytest.raises(ValueError):
        validate_type_reference_choice(arg_name, type_ref_val, val_types)


def test_validate_not_falsey():
    arg_name = 'arg'
    assert validate_not_falsey(arg_name, ' ')
    assert validate_not_falsey(arg_name, [' '])
    assert validate_not_falsey(arg_name, {' ': ''})
    assert validate_not_falsey(arg_name, {' '})

    with pytest.raises(ValueError):
        validate_not_falsey(arg_name, None)
        validate_not_falsey(arg_name, '')
        validate_not_falsey(arg_name, [])
        validate_not_falsey(arg_name, {})
        validate_not_falsey(arg_name, set())


if __name__ == '__main__':
    pytest.main(['-xrf'])
