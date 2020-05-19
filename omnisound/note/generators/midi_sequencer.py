# Copyright 2020 Mark S. Weiss

from typing import Optional

from omnisound.note.adapters.note import MakeNoteConfig
from omnisound.note.adapters.midi_note import (ATTR_NAME_IDX_MAP, ATTR_GET_TYPE_CAST_MAP, CLASS_NAME,
                                               get_pitch_for_key, make_note, NUM_ATTRIBUTES)
from omnisound.note.generators.sequencer import Sequencer
from omnisound.note.modifiers.meter import Meter
from omnisound.note.modifiers.swing import Swing
from omnisound.player.midi_player import MidiInteractiveSingleTrackPlayer, MidiPlayerAppendMode
from omnisound.player.midi_writer import MidiWriter


class MidiSingleTrackSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 mn: MakeNoteConfig = None):
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                get_pitch_for_key=get_pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)
        super(MidiSingleTrackSequencer, self).__init__(
                name=name,
                num_measures=num_measures,
                meter=meter,
                swing=swing,
                player=MidiInteractiveSingleTrackPlayer(
                    append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote),
                mn=mn)


class MidiWriterSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 midi_file_path: str = None,
                 mn: MakeNoteConfig = None):
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                get_pitch_for_key=get_pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_get_type_cast_map=ATTR_GET_TYPE_CAST_MAP)
        super(MidiWriterSequencer, self).__init__(
                name=name,
                num_measures=num_measures,
                meter=meter,
                swing=swing,
                player=MidiWriter(
                        append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote,
                        midi_file_path=midi_file_path),
                mn=mn)
