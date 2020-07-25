# Copyright 2020 Mark S. Weiss

from pathlib import Path
from typing import Optional

from omnisound.note.adapter.note import MakeNoteConfig
from omnisound.note.adapter.midi_note import (ATTR_NAME_IDX_MAP, ATTR_GET_TYPE_CAST_MAP, CLASS_NAME,
                                              get_pitch_for_key, make_note, NUM_ATTRIBUTES)
from omnisound.note.generator.sequencer.sequencer import Sequencer
from omnisound.note.modifier.meter import Meter
from omnisound.note.modifier.swing import Swing
from omnisound.player.midi_player import (MidiInteractiveSingleTrackPlayer, MidiInteractiveMultitrackPlayer,
                                          MidiPlayerAppendMode)
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
                # TODO THIS IS WRONG - A SEQUENCER IS A SONG, DON'T PASS IN SONG
                player=MidiInteractiveSingleTrackPlayer(append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote),
                mn=mn)


class MidiMultitrackSequencer(Sequencer):
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
        super(MidiMultitrackSequencer, self).__init__(
                name=name,
                num_measures=num_measures,
                meter=meter,
                swing=swing,
                player=MidiInteractiveMultitrackPlayer(append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote),
                mn=mn)


class MidiWriterSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 midi_file_path: Path = None,
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
              player=MidiWriter(append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote,
                                midi_file_path=midi_file_path),
              mn=mn)
