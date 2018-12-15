# Copyright 2018 Mark S. Weiss

from math import copysign
from random import random
from typing import Any, Dict, Optional, Tuple


def validate_type(arg_name, val, val_type) -> bool:
    if not isinstance(val, val_type):
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` but must be type: `{val_type}`')
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
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` but must be one of the following types: `{val_types}`')
    return matched, matched_type


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


def validate_sequence_of_types(arg_name, list_val, val_type) -> bool:
    """Must be a valid collection type. Can be empty. If there are values they must match val_type."""
    validate_type_choice(arg_name, list_val, (list, tuple, set))
    for val in list_val:
        validate_type(arg_name, val, val_type)
    return True


def validate_optional_sequence_of_types(arg_name, list_val, val_type) -> bool:
    """Can be None or an empty collection and return True. Else if not empty each value must match val_type."""
    if not list_val:
        return True
    else:
        validate_type_choice(arg_name, list_val, (list, tuple, set))
        for val in list_val:
            validate_type(arg_name, val, val_type)
    return True


def sign() -> float:
    return copysign(1.0, random() - 0.5)


def enum_to_dict(enum_class_name: str, enum) -> Dict:
    validate_type('enum_class_name', enum_class_name, str)
    return {enum_member: eval(f'{enum_class_name}.{enum_member}.value')
            for enum_member in enum.__members__}


def enum_to_dict_reverse_mapping(enum_class_name: str, enum) -> Dict:
    validate_type('enum_class_name', enum_class_name, str)
    return {eval(f'{enum_class_name}.{enum_member}.value'): enum_member
            for enum_member in enum.__members__}