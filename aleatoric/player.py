# Copyright 2018 Mark S. Weiss

from time import sleep

from abc import abstractmethod, ABCMeta
from typing import List

from FoxDot import Player as SC_Player
# noinspection PyProtectedMember
from FoxDot.lib.SCLang._SynthDefs import pluck as sc_sd_pluck

from note import Note, NoteGroup, PerformanceAttrs, SupercolliderNoteAttrs


class PlayerNoNotesException(Exception):
    pass


class Player(metaclass=ABCMeta):

    # TODO ADD play_all() and figure out "note group" with one perf_attr_config for all note_attrs

    @abstractmethod
    def play_each(self):
        """Play each note. Each notes note_attrs are honored and
           separate performance_attrs with a matching index are applied
           to all notes in the batch if they are available.
        """
        raise NotImplementedError()

    @abstractmethod
    def play_all(self):
        """Play notes as a batch. Each notes note_attrs are honored but
           performance_attrs are applied to all notes in the batch.
        """
        raise NotImplementedError()

    def __init__(self, notes: List[Note] = None, note_group: NoteGroup = None):
        # Only validate if the list is not empty
        if notes is not None and notes:
            # All elements are a subclass of Note. This still allows heterogeneous Notes.
            for n in notes:
                if not isinstance(n, Note):
                    raise ValueError(f'arg `notes` must be None or empty list or type List[Note]')
            self.notes = notes
        if note_group is not None:
            if not isinstance(note_group, NoteGroup):
                raise ValueError(f'arg `note_group` must be type NoteGroup')
            self.note_group = note_group


class SupercolliderPlayer(Player):
    def __init__(self, notes: List[Note] = None, note_group: NoteGroup = None):
        super(SupercolliderPlayer, self).__init__(notes=notes, note_group=note_group)
        self.sc_player = SC_Player()

    def play_each(self):
        if not self.notes:
            raise PlayerNoNotesException('No notes to play')
        for n in self.notes:
            self.sc_player >> n.note_attrs.instrument([n.note_attrs.degree],
                                                      dur=n.note_attrs.dur,
                                                      amp=n.note_attrs.amp,
                                                      **n.performance_attrs.as_dict())
            sleep(n.note_attrs.dur)
            self.sc_player.stop()

    def play_all(self):
        if not self.note_group:
            raise PlayerNoNotesException('No note_group to play')
        for note_attrs in self.note_group.note_attrs_list:
            self.sc_player >> note_attrs.instrument([note_attrs.degree],
                                                    dur=note_attrs.dur,
                                                    amp=note_attrs.amp,
                                                    **note_group.performance_attrs.as_dict())
            sleep(note_attrs.dur)
            self.sc_player.stop()


if __name__ == '__main__':
    # This is a test
    note_attrs = SupercolliderNoteAttrs(synth_def=sc_sd_pluck,
                                        delay=0, dur=1.0, amp=1.0, degree=1,
                                        name='test_note',
                                        oct=4, scale='chromatic')
    performance_attrs = PerformanceAttrs()

    note = Note(note_attrs, performance_attrs)
    notes = [note]
    # Players with notes play each note separately, with its own note_attrs and performance_attrs
    player = SupercolliderPlayer(notes=notes)
    player.play_each()

    sleep(3)

    note_attrs = SupercolliderNoteAttrs(synth_def=sc_sd_pluck,
                                        delay=0, dur=1.0, amp=1.0, degree=2,
                                        name='test_note_group',
                                        oct=5, scale='chromatic')
    note_group = NoteGroup([note_attrs], performance_attrs)
    # Players with a note_group play each note in the group with its own note_attrs, applying
    # one performance_attrs to each note
    player.note_group = note_group
    player.play_all()
