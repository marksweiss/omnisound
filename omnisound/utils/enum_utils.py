from typing import Any, Dict


def enum_to_dict(enum_cls: Any) -> Dict:
    return {e: e.value for e in enum_cls}


def enum_to_str_key_dict(enum_cls: Any) -> Dict:
    return {e.name: e for e in enum_cls}


def enum_to_dict_reverse_mapping(enum_cls) -> Dict:
    return {e.value: e for e in enum_cls}