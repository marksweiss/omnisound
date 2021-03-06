# Copyright 2020 Mark S. Weiss

from typing import Optional, Union

from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.note.adapter.csound_note import (ATTR_NAME_IDX_MAP, ATTR_VAL_CAST_MAP, CLASS_NAME,
                                                    pitch_for_key, make_note, NUM_ATTRIBUTES)
from omnisound.src.generator.sequencer.sequencer import Sequencer
from omnisound.src.modifier.meter import Meter
from omnisound.src.modifier.swing import Swing
from omnisound.src.player.csound.csound_player import CSoundCSDPlayer, CSoundInteractivePlayer


class CSoundSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 player: Optional[Union[CSoundCSDPlayer, CSoundInteractivePlayer]] = None,
                 mn: MakeNoteConfig = None):
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                pitch_for_key=pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_val_cast_map=ATTR_VAL_CAST_MAP)
        super(CSoundSequencer, self).__init__(name=name,
                                              num_measures=num_measures,
                                              meter=meter,
                                              swing=swing,
                                              player=player,
                                              mn=mn)
