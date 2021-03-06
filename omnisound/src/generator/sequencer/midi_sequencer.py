# Copyright 2020 Mark S. Weiss

from pathlib import Path
from typing import Optional

from omnisound.src.note.adapter.note import MakeNoteConfig
from omnisound.src.note.adapter.midi_note import (ATTR_NAME_IDX_MAP, ATTR_VAL_CAST_MAP, CLASS_NAME,
                                                  pitch_for_key, make_note, NUM_ATTRIBUTES)
from omnisound.src.generator.chord import Chord
from omnisound.src.generator.sequencer.sequencer import Sequencer
from omnisound.src.modifier.meter import Meter
from omnisound.src.modifier.swing import Swing
from omnisound.src.player.midi.midi_player import (MidiInteractiveSingleTrackPlayer, MidiInteractiveMultitrackPlayer,
                                                   MidiPlayerAppendMode)
from omnisound.src.player.midi.midi_writer import MidiWriter


class MidiSingleTrackSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 arpeggiator_chord: Optional[Chord] = None,
                 mn: MakeNoteConfig = None):
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                pitch_for_key=pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_val_cast_map=ATTR_VAL_CAST_MAP)
        super(MidiSingleTrackSequencer, self).__init__(
                name=name,
                num_measures=num_measures,
                meter=meter,
                swing=swing,
                arpeggiator_chord=arpeggiator_chord,
                player=MidiInteractiveSingleTrackPlayer(append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote),
                mn=mn)


class MidiMultitrackSequencer(Sequencer):
    def __init__(self,
                 name: Optional[str] = None,
                 num_measures: int = None,
                 meter: Optional[Meter] = None,
                 swing: Optional[Swing] = None,
                 arpeggiator_chord: Optional[Chord] = None,
                 mn: MakeNoteConfig = None):
        if not mn:
            mn = MakeNoteConfig(cls_name=CLASS_NAME,
                                num_attributes=NUM_ATTRIBUTES,
                                make_note=make_note,
                                pitch_for_key=pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_val_cast_map=ATTR_VAL_CAST_MAP)
        super(MidiMultitrackSequencer, self).__init__(
              name=name,
              num_measures=num_measures,
              meter=meter,
              swing=swing,
              arpeggiator_chord=arpeggiator_chord,
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
                                pitch_for_key=pitch_for_key,
                                attr_name_idx_map=ATTR_NAME_IDX_MAP,
                                attr_val_cast_map=ATTR_VAL_CAST_MAP)
        super(MidiWriterSequencer, self).__init__(
              name=name,
              num_measures=num_measures,
              meter=meter,
              swing=swing,
              player=MidiWriter(append_mode=MidiPlayerAppendMode.AppendAfterPreviousNote,
                                midi_file_path=midi_file_path),
              mn=mn)
