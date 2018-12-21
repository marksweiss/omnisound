# Copyright 2018 Mark S. Weiss

from math import copysign
from random import random
from typing import Any, Dict, Optional, Tuple

# Have to import these even though they aren't directly referred to because
# enum_to_dict() methods call eval() and are used with these enum types, and when eval() is called
# if fails if these types are not in module scope
# noinspection PyUnresolvedReferences
from aleatoric.scale_globals import MajorKey, MinorKey


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


def validate_type_reference(arg_name, type_ref_val, val_type):
    """Validates that type_ref_val is a type that is a direct alias of a type.
       Example:
           class A(object):
               pass

           # a is an alias of the type A
           a = A
           # isinstance returns False

           isinstnace(A, a)  # => False

           # a is an object of type A
           a = A()
           # isinstance returns True
           isinstance(A, a)  # => True

           # a is an alias of the type A
           a = A
           # use type operator to test to get valid result for a var that is a reference to a type
           a is A # => True
    """
    if not (type_ref_val is val_type):
        raise ValueError(f'arg: `{arg_name}` has val: `{type_ref_val}` but must be alias to type: `{val_type}`')
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
        raise ValueError((f'arg: `{arg_name}` has val: `{type_ref_val}` '
                          f'but must be one of the following types: `{val_types}`'))
    return matched, matched_type


def sign() -> float:
    return copysign(1.0, random() - 0.5)


def enum_to_dict(enum_class_name: str, enum_class) -> Dict:
    """Uses the fact that enum classes have a __members__
       method that returns an iterable of string names of the fields in the enum. For each one we then
       get a reference to the enum field itself with getattr() and get a reference to the value in the
       enum mapped to that field with, unfortunately, an eval()
    """
    validate_type('enum_class_name', enum_class_name, str)
    return {getattr(enum_class, enum_member): eval(f'{enum_class_name}.{enum_member}.value')
            for enum_member in enum_class.__members__}


def enum_to_dict_reverse_mapping(enum_class_name: str, enum_class) -> Dict:
    validate_type('enum_class_name', enum_class_name, str)
    return {eval(f'{enum_class_name}.{enum_member}.value'): getattr(enum_class, enum_member)
            for enum_member in enum_class.__members__}