# Copyright 2020 Mark S. Weiss

from typing import Optional, Union

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.adapters.csound_note import ATTR_NAME_IDX_MAP, ATTR_GET_TYPE_CAST_MAP, NUM_ATTRIBUTES
from omnisound.note.generators.sequencer import Sequencer
from omnisound.note.modifiers.meter import Meter, NoteDur
from omnisound.note.modifiers.swing import Swing
from omnisound.player.csound_player import CSoundCSDPlayer, CSoundInteractivePlayer


class CSoundSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 pattern_resolution: Optional[NoteDur] = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 player: Optional[Union[CSoundCSDPlayer, CSoundInteractivePlayer]] = None,
                 mn: MakeNoteConfig = None):
        mn.num_attributes = mn.num_attributes or NUM_ATTRIBUTES
        mn.attr_name_idx_map = mn.attr_name_idx_map or ATTR_NAME_IDX_MAP
        mn.attr_get_type_cast_map = mn.attr_get_type_cast_map or ATTR_GET_TYPE_CAST_MAP
        super(CSoundSequencer, self).__init__(name=name,
                                              num_measures=num_measures,
                                              pattern_resolution=pattern_resolution,
                                              meter=meter,
                                              swing=swing,
                                              player=player,
                                              mn=mn)
