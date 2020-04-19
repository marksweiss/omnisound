# Copyright 2018 Mark S. Weiss

from collections import KeysView, ValuesView
from math import copysign
from os import access, W_OK
from os.path import dirname
from random import random
from typing import Any, Dict, Optional, Tuple


def validate_type(arg_name, val, val_type) -> bool:
    if not isinstance(val, val_type):
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` and type: {type(val)} but must be type: `{val_type}`')
    return True


def validate_type_choice(arg_name, val, val_types) -> Tuple[bool, Optional[Any]]:
    matched = False
    matched_type = None
    for val_type in val_types:
        if isinstance(val, val_type):
            matched = True
            matched_type = val_type
            break
    if not matched:
        raise ValueError((f'arg: `{arg_name}` has val: `{val}` and type: {type(val)} but '
                          f'must be one of the following types: `{val_types}`'))
    return matched, matched_type


def validate_optional_type_choice(arg_name, val, val_types) -> Tuple[bool, Optional[Any]]:
    if val is None:
        return True, type(None)
    return validate_type_choice(arg_name, val, val_types)


def validate_types(*val_type_tuples) -> bool:
    for arg_name, val, val_type in val_type_tuples:
        validate_type(arg_name, val, val_type)
    return True


def validate_optional_type(arg_name, val, val_type) -> bool:
    if val is None:
        return True
    return validate_type(arg_name, val, val_type)


def validate_optional_types(*val_type_tuples) -> bool:
    matched = False
    for arg_name, val, val_type in val_type_tuples:
        ret = validate_optional_type(arg_name, val, val_type)
        matched = matched or ret
    return matched


def validate_not_none(arg_name, val) -> bool:
    if val is None:
        raise ValueError(f'`{arg_name}` must not be None')
    return True


def validate_not_falsey(arg_name, val) -> bool:
    if not val:
        raise ValueError(f'`{arg_name}` must not be falsey')
    return True


def validate_sequence_of_type(arg_name, seq_val, val_type) -> bool:
    """Must be a valid collection type. Can be empty. If there are values they must match val_type."""
    validate_type_choice(arg_name, seq_val, (KeysView, ValuesView, list, tuple, set))
    for val in seq_val:
        validate_type(arg_name, val, val_type)
    return True


def validate_sequence_of_type_choice(arg_name, seq_val, val_types) -> bool:
    """Must be a valid collection type. Can be empty. If there ave values all must be in val_types."""
    validate_type_choice(arg_name, seq_val, (KeysView, ValuesView, list, tuple, set))
    for val in seq_val:
        validate_type_choice(arg_name, val, val_types)
    return True


def validate_optional_sequence_of_type(arg_name, seq_val, val_type) -> bool:
    """Can be None or an empty collection and return True. Else if not empty each value must match val_type."""
    if not seq_val:
        return True
    else:
        validate_type_choice(arg_name, seq_val, (KeysView, ValuesView, list, tuple, set))
        for val in seq_val:
            validate_type(arg_name, val, val_type)
    return True


def validate_type_reference(arg_name, type_ref_val, val_type):
    """Validates that type_ref_val is a type that is a direct alias of a type.
       NOTE: the `is` operator does not match subtypes. isinstance() using the instantiated object of the type
       of the variable that is a reference to a type, compared to either the type or its base class type, succeeds.
    """
    if not isinstance(type_ref_val.__call__(), val_type):
        raise ValueError((f'arg: `{arg_name}` has val: `{type_ref_val}` and type: {type(type_ref_val.__call__())} '
                          f'but must be alias to type: `{val_type}`'))
    return True


def validate_type_reference_choice(arg_name, type_ref_val, val_types) -> Tuple[bool, Optional[Any]]:
    matched = False
    matched_type = None
    for val_type in val_types:
        if type_ref_val is val_type:
            matched = True
            matched_type = val_type
            break
    if not matched:
        raise ValueError((f'arg: `{arg_name}` has val: `{type_ref_val}` and type: {type(type_ref_val.__call__())}'
                          f'but must be one of the following types: `{val_types}`'))
    return matched, matched_type


# TODO UNIT TEST
def validate_path(arg_name, val):
    if not isinstance(val, str):
        raise ValueError(f'arg: `{arg_name}` must be type `str` but is type: `{type(val)}`')
    if not access(dirname(val), W_OK):
        raise ValueError(f'arg: `{val}` is not a valid path')
    return True


# TODO UNIT TEST
def validate_optional_path(arg_name, val):
    if not val:
        return True
    return validate_path(arg_name, val)


def sign() -> float:
    return copysign(1.0, random() - 0.5)


def enum_to_dict(enum_cls: Any) -> Dict:
    return {e: e.value for e in enum_cls}


def enum_to_str_key_dict(enum_cls: Any) -> Dict:
    return {e.name: e for e in enum_cls}


def enum_to_dict_reverse_mapping(enum_cls) -> Dict:
    return {e.value: e for e in enum_cls}
