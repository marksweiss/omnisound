from itertools import chain
from time import sleep
from typing import List, Sequence, Tuple
from queue import Queue
import threading
import asyncio

# noinspection PyProtectedMember
from mido import Message, open_output
from mido.backends.rtmidi import Output
# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.container.measure import Measure
from omnisound.src.container.track import MidiTrack
from omnisound.src.generator.scale import HarmonicScale, MajorKey, MinorKey, Scale
from omnisound.src.note.adapter.note import as_dict, set_attr_vals_from_dict, NoteValues, MakeNoteConfig
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.player.midi.midi_player import get_midi_messages_and_notes_for_track
import omnisound.src.note.adapter.midi_note as midi_note

NOTE_DUR = NoteDur.QRTR
OCTAVE = 4
INSTRUMENT = midi_note.MidiInstrument.Acoustic_Grand_Piano.value

ATTR_VALS_DEFAULTS_MAP = NoteValues(midi_note.ATTR_NAMES)
ATTR_VALS_DEFAULTS_MAP.instrument = INSTRUMENT
ATTR_VALS_DEFAULTS_MAP.time = 0
ATTR_VALS_DEFAULTS_MAP.duration = NOTE_DUR.QUARTER.value
ATTR_VALS_DEFAULTS_MAP.velocity = midi_note.MIDI_PARAM_MAX_VAL  # 127
ATTR_VALS_DEFAULTS_MAP.pitch = midi_note.get_pitch_for_key(key=MajorKey.C, octave=OCTAVE)  # C4 "Middle C"
note_config = MakeNoteConfig.copy(midi_note.DEFAULT_NOTE_CONFIG)
note_config.attr_vals_defaults_map = ATTR_VALS_DEFAULTS_MAP.as_dict()

NUM_TRACKS = 1
NUM_MEASURES = 4
METER = Meter(beats_per_measure=4, beat_note_dur=NOTE_DUR, tempo=120, quantizing=True)
NOTES_PER_MEASURE = METER.quarter_notes_per_beat_note * METER.beats_per_measure
MEASURE = Measure(meter=METER, num_notes=NOTES_PER_MEASURE, mn=note_config)

HARMONIC_SCALE = HarmonicScale.Major
KEY = MajorKey
SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, mn=note_config)

TRACKS = []
LAYOUT = []
# Used by the window event loop thread to communicate captured note events from the GUI to the Midi playback thread
QUEUE = Queue()
PORT_NAME = 'omnisound_sequencer'


def generate_measures_and_buttons():
    for i in range(NUM_TRACKS):
        track = MidiTrack(meter=METER, channel=i + 1, instrument=INSTRUMENT)
        TRACKS.append(track)
        LAYOUT.append([])
        layout_measures = []
        for j in range(NUM_MEASURES):
            measure = Measure.copy(MEASURE)
            track.append(measure)
            layout_notes = []
            for k in range(NOTES_PER_MEASURE):
                # Set each note to the params of the root note in the Scale
                set_attr_vals_from_dict(measure[k], as_dict(SCALE[0]))
                # PySimpleGUI refers to UI objects by "key" and returns this key when events are trapped on the UI.
                # Key each button to it's offset (track, measure, note) index into the flattened Messages list.
                # Offset is track number * number of measures * notes per measure + note offset in measure.
                # Example: 2 tracks, 4 measures, 4 notes per measure,
                #  second note in second measure of track 2 == (1 * 4 * 4) + (1 * 4) + 1 = idx 21 in 0-based note list
                layout_notes.append(
                    sg.Checkbox(text=str(k + 1),
                                key=((i * NUM_MEASURES * NOTES_PER_MEASURE) + (j * NOTES_PER_MEASURE) + k)))
            layout_measures.append(sg.Frame(title=f'Measure {j + 1}', layout=[layout_notes]))
        LAYOUT[i].append(sg.Frame(title=f'Track {i + 1}', layout=[layout_measures]))


# noinspection PyBroadException
async def _loop_track(messages, durations, port):
    print('loop_track')

    with port:
        loop_duration = messages[-1].time
        j = 0
        while True:
            for i in range(0, len(messages), 2):
                messages[i].time += (j * loop_duration)
                try:
                    # Drain the queue and apply all note changes put their by the GUI thread
                    while i := QUEUE.get ():
                        messages[i].velocity = midi_note.MIDI_PARAM_MAX_VAL if messages[i].velocity == 0 else 0
                except Exception:
                    pass
                port.send(messages[i])
                await asyncio.sleep(durations[int(i / 2)])
                port.send(messages[i + 1])
            j += 1


async def _loop():
    print('_loop')
    messages_durations_list = [get_midi_messages_and_notes_for_track(track) for track in TRACKS]
    port: Output = open_output(PORT_NAME, True)  # flag is virtual=True to create a MIDI virtual port
    play_track_tasks = [asyncio.create_task(_loop_track(messages, durations, port))
                        for messages, durations in messages_durations_list]
    for task in play_track_tasks:
        await task


def loop():
    print('loop')
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    event_loop.run_until_complete(_loop())


# noinspection PyBroadException
def start():
    print('start')
    window = sg.Window('Omnisound Sequencer', LAYOUT)
    print('after window')
    # Create an event loop, necessary or the first event trapped closes the window
    while True:
        print('in event loop')
        # This is the framework mechanism for polling the window for events and status
        event, values = window.read()
        print('after window.read()')
        # Exit event loop if user closes window, going immediately to window.close()
        # Not following this pattern crashes the application.
        if event == sg.WIN_CLOSED:
            print('close event')
            break

        print('spawning player thread')
        threading.Thread(target=loop, daemon=True).start()

        if event:
            print('other event')
            try:
                QUEUE.put(event)
            except Exception:
                pass

    window.close()


if __name__ == '__main__':
    generate_measures_and_buttons()
    start()


# layout = [
#     [sg.Frame(
#             f'Track 1',
#             [
#                 [],
#             ],
#             title_color=None,
#             background_color=None,
#             title_location=None,
#             relief="groove",
#             size=(None, None),
#             font=None,
#             pad=None,
#             border_width=None,
#             key=None,
#             k=None,
#             tooltip=None,
#             right_click_menu=None,
#             visible=True,
#             element_justification="left",
#             metadata=None)
#     ]
# ]


# TODO NEXT
# Start a sequence looping here and then test that te loop below turns notes on and off
# Then add a Start button to trigger starting the sequence
# Then expose UI elements to choose note and change pitch by mapping UI index to SCALE index and using that pitch
# Then expose UI element for amplitude
# Then make UI element for note toggle element like radio button or checkbox
# Then expose Swing and apply to all notes
# Then expose reset to normalized
# Then expose chords instead of just notes in each position
# Then allow choosing duration of track
# Then allow choosing meter
# Then allow choosing instrument per track
# Then make event loop the async event loop from midiplayer so timing is controlled
