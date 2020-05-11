# Copyright 2020 Mark S. Weiss

from typing import Optional, Union

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.adapters.csound_note import (ATTR_NAME_IDX_MAP, ATTR_GET_TYPE_CAST_MAP, CLASS_NAME,
                                                 get_pitch_for_key, make_note, NUM_ATTRIBUTES)
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
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                get_pitch_for_key=get_pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)
        super(CSoundSequencer, self).__init__(name=name,
                                              num_measures=num_measures,
                                              pattern_resolution=pattern_resolution,
                                              meter=meter,
                                              swing=swing,
                                              player=player,
                                              mn=mn)
