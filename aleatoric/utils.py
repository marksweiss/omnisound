# Copyright 2018 Mark S. Weiss

from math import copysign
from random import random


def validate_type(arg_name, val, val_type):
    if not isinstance(val, val_type):
        raise ValueError(f'arg: `{arg_name}` has val: `{val}` but must be type: `{val_type}`')


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


def validate_list_of_types(arg_name, list_val, val_type):
    if not list_val:
        raise ValueError(f'`{arg_name}` must not be False-y or None')
    validate_type(arg_name, list_val, list)
    for val in list_val:
        validate_type(arg_name, val, val_type)


def validate_optional_list_of_types(arg_name, list_val, val_type):
    if not list_val:
        return
    else:
        validate_list_of_types(arg_name, list_val, val_type)

def sign():
    return copysign(1.0, random() - 0.5)

