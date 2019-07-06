# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, List

from numpy import array

from omnisound.utils.utils import validate_type, validate_type_choice


INSTRUMENT_I = 0
START_I = 1
DUR_I = 2
AMP_I = 3
PITCH_I = 4

BASE_ATTR_NAME_IDX_MAP = {
    'instrument': INSTRUMENT_I,
    'start': START_I,
    'dur': DUR_I,
    'amp': AMP_I,
    'pitch': PITCH_I,
}
BASE_ATTR_NAMES = tuple(BASE_ATTR_NAME_IDX_MAP.keys())

DEFAULT_VAL = 0.0


# Prototypes of generic Note-attribute accessors. These are parameterized by attr_name and dynamically
# created when the class is constructed for the Note.
def getter(attr_name: str):
    def _getter(self) -> Any:
        return self.attr_get_type_cast_map[attr_name](self.note_attr_vals[self.attr_name_idx_map[attr_name]])
    return _getter


def setter(attr_name: str):
    def _setter(self, attr_val) -> None:
        if attr_name in self.attr_name_idx_map:
            validate_type('attr_name', attr_name, str)
            validate_type_choice('attr_val', attr_val, (float, int))
            self.note_attr_vals[self.attr_name_idx_map[attr_name]] = attr_val
        else:
            setattr(self, attr_name, attr_val)
    return _setter


# TODO UNIT TEST
class NoteValues(object):
    """Convenience class to dynamically create, manipulate and retrieve collections of note attributes."""
    def __init__(self, attr_names):
        self._attr_names = attr_names
        for attr_name in attr_names:
            setattr(self, attr_name, None)

    def as_dict(self) -> Dict:
        return {field: getattr(self, field) or DEFAULT_VAL for field in self._attr_names}

    def as_list(self) -> List:
        return [getattr(self, field) for field in self._attr_names]

    def as_array(self) -> array:
        return array(self.as_list())


# TODO UNIT TEST
def as_list(self) -> List[float]:
    return [self.note_attr_vals[i] for i in range(self.note_attr_vals.shape[0])]


# TODO UNIT TEST
def as_dict(self) -> Dict[str, float]:
    attr_names = self.attr_name_idx_map.keys()
    return {attr_names[i]: self.note_attr_vals[i] for i in range(self.note_attr_vals.shape[0])}
