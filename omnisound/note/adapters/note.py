# Copyright 2018 Mark S. Weiss

from typing import Any, Dict, List

from numpy import array

from omnisound.utils.utils import validate_type, validate_type_choice


INSTRUMENT_I = 0
START_I = 1
DUR_I = 2
AMP_I = 3
PITCH_I = 4

# TODO ALL NOTES MUST INCLUDE THIS 'BASE CLASS' SET OF NOTE ATTRIBUTE NAMES AND INDEXES
BASE_ATTR_NAME_IDX_MAP = {
    'instrument': INSTRUMENT_I,
    'start': START_I,
    'duration': DUR_I,
    'amplitude': AMP_I,
    'pitch': PITCH_I,
}
BASE_ATTR_NAMES = tuple(BASE_ATTR_NAME_IDX_MAP.keys())

DEFAULT_VAL = 0.0


def add_base_attr_name_indexes(attr_name_idx_map: Dict[str, int]):
    base_attr_names_to_add = set(BASE_ATTR_NAMES) - set(attr_name_idx_map.keys())
    attr_name_idx_map.update({attr_name: BASE_ATTR_NAME_IDX_MAP[attr_name] for attr_name in base_attr_names_to_add})
    return attr_name_idx_map


def getter(attr_name: str):
    """Prototype of generic Note-attribute accessor. This is parameterized by attr_name and dynamically
    created when the class is constructed for the specific Note type."""
    def _getter(self) -> Any:
        return self.attr_get_type_cast_map[attr_name](self.note_attr_vals[self.attr_name_idx_map[attr_name]])
    return _getter


def setter(attr_name: str):
    """Prototype of generic Note-attribute accessor. This is parameterized by attr_name and dynamically
    created when the class is constructed for the specific Note type."""
    def _setter(self, attr_val) -> None:
        if attr_name in self.attr_name_idx_map:
            validate_type('attr_name', attr_name, str)
            validate_type_choice('attr_val', attr_val, (float, int))
            self.note_attr_vals[self.attr_name_idx_map[attr_name]] = attr_val
        else:
            setattr(self, attr_name, attr_val)
    return _setter


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


def as_list(note) -> List[float]:
    return [note.note_attr_vals[i] for i in range(note.note_attr_vals.shape[0])]


def as_dict(note) -> Dict[str, float]:
    attr_names = list(note.attr_name_idx_map.keys())
    return {attr_names[i]: note.note_attr_vals[i] for i in range(note.note_attr_vals.shape[0])}


def make_rest_note(note, amplitude_attr_name):
    setattr(note, amplitude_attr_name, 0.0)


# TODO USE THIS IN NOTE SEQUENCE RATHER THAN THE MULTIPLE CHECKS AGAINST ARRAY DIRECTLY
def get_num_attributes(n):
    """Handles numpy semantics to return number of columns in the underlying ndarray for both individual Note
       which is one-dimensional and NoteSequence which is two-dimensional.
    """
    if len(n.note_attr_vals.shape) == 1:
        return n.note_attr_vals.shape[0]
    else:
        return n.note_attr_vals.shape[1]