# Copyright 2018 Mark S. Weiss

from math import copysign
from random import random


def validate_type(arg_name, val, val_type):
    if not isinstance(val, val_type):
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` but must be type: `{val_type}`')


def validate_type_choice(arg_name, val, val_types):
    matched = False
    for val_type in val_types:
        if isinstance(val, val_type):
            matched = True
            break
    if not matched:
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` but must be one of the following types: `{val_types}`')


def validate_types(*val_type_tuples):
    for arg_name, val, val_type in val_type_tuples:
        validate_type(arg_name, val, val_type)


def validate_optional_type(arg_name, val, val_type):
    if val is None:
        return True
    validate_type(arg_name, val, val_type)


def validate_optional_types(*val_type_tuples):
    for arg_name, val, val_type in val_type_tuples:
        validate_optional_type(arg_name, val, val_type)


def validate_not_none(arg_name, val):
    if val is None:
        raise ValueError(f'`{arg_name}` must not be None')


def validate_sequence_of_types(arg_name, list_val, val_type):
    """Must be a valid collection type. Can be empty. If there are values they must match val_type."""
    validate_type_choice(arg_name, list_val, (list, tuple, set))
    for val in list_val:
        validate_type(arg_name, val, val_type)


def validate_optional_sequence_of_types(arg_name, list_val, val_type):
    """Can be None or an empty collection and return True. Else if not empty each value must match val_type."""
    if not list_val:
        return
    else:
        validate_type_choice(arg_name, list_val, (list, tuple, set))
        for val in list_val:
            validate_type(arg_name, val, val_type)


def sign():
    return copysign(1.0, random() - 0.5)

