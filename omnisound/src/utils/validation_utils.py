from typing import Any, KeysView, Optional, Tuple, ValuesView


def validate_not_none(arg_name, val) -> bool:
    if val is None:
        raise ValueError(f'`{arg_name}` must not be None')
    return True


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
