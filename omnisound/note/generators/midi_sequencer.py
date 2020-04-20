# Copyright 2020 Mark S. Weiss

from typing import Any, Mapping, Optional

from omnisound.note.adapters.midi_note import (get_pitch_for_key, make_note as midi_make_note, ATTR_NAME_IDX_MAP,
                                               ATTR_GET_TYPE_CAST_MAP, NUM_ATTRIBUTES)
from omnisound.note.generators.sequencer import Sequencer
from omnisound.note.modifiers.meter import Meter, NoteDur
from omnisound.note.modifiers.swing import Swing


class MidiSequencer(Sequencer):

    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 pattern_resolution: Optional[NoteDur] = None,
                 meter: Optional[Meter] = None,
                 num_attributes: Optional[int] = None,
                 attr_name_idx_map: Optional[Mapping[str, int]] = None,
                 attr_vals_defaults_map: Optional[Mapping[str, float]] = None,
                 attr_get_type_cast_map: Optional[Mapping[str, Any]] = None,
                 swing: Optional[Swing] = None):
        num_attributes = num_attributes or NUM_ATTRIBUTES
        attr_name_idx_map = attr_name_idx_map or ATTR_NAME_IDX_MAP
        attr_get_type_cast_map = attr_get_type_cast_map or ATTR_GET_TYPE_CAST_MAP
        super(MidiSequencer, self).__init__(name=name,
                                            num_measures=num_measures,
                                            pattern_resolution=pattern_resolution,
                                            meter=meter,
                                            make_note=midi_make_note,
                                            num_attributes=num_attributes,
                                            attr_name_idx_map=attr_name_idx_map,
                                            attr_vals_defaults_map=attr_vals_defaults_map,
                                            attr_get_type_cast_map=attr_get_type_cast_map,
                                            pitch_for_key_cb=get_pitch_for_key,
                                            swing=swing)
