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

from itertools import chain, count
from time import sleep, time
import threading

# noinspection PyProtectedMember
from mido import open_output  # Message

# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.container.measure import Measure
from omnisound.src.container.track import MidiTrack
from omnisound.src.generator.scale import HarmonicScale, MajorKey, Scale
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
ATTR_VALS_DEFAULTS_MAP.velocity = 0
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
QUEUE = []
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
                # Key each button to it's index in the flattened Messages list.
                layout_notes.append(
                    sg.Checkbox(str(k + 1), default=False, enable_events=True,
                                key=((i * NUM_MEASURES * NOTES_PER_MEASURE) + (j * NOTES_PER_MEASURE) + k)))
            layout_measures.append(sg.Frame(title=f'Measure {j + 1}', layout=[layout_notes]))
        LAYOUT[i].append(sg.Frame(title=f'Track {i + 1}', layout=[layout_measures]))


def _loop_track():
    messages_durations_list = [get_midi_messages_and_notes_for_track(track) for track in TRACKS]
    messages = list(chain(*[messages for messages, _ in messages_durations_list]))
    loop_duration = messages[-1].time
    durations = list(chain(*[durations for _, durations in messages_durations_list]))

    port = open_output(PORT_NAME, True)  # flag is virtual=True to create a MIDI virtual port
    with port:
        for j in count():
            # Drain the queue and apply all note changes put their by the GUI thread
            # TODO See note below about replacing this terrible GUI framework. We have to update every note
            #  on every loop. OMG.
            i = 0
            while QUEUE and i < (NUM_MEASURES * NOTES_PER_MEASURE * 2):  # .not_empty:
                velocity = QUEUE.pop()
                messages[i].velocity = velocity
                i += 2

            for i in range(0, len(messages), 2):
                messages[i].time += (j * loop_duration)
                port.send(messages[i])
                sleep(durations[int(i / 2)])
                port.send(messages[i + 1])


# noinspection PyBroadException
def start():
    window = sg.Window('Omnisound Sequencer', LAYOUT)
    threading.Thread(target=_loop_track, daemon=True).start()

    # Create an event loop, necessary or the first event trapped closes the window
    while True:
        # This is the framework mechanism for polling the window for events and status
        # timeout arg is needed with Checkbox or the event loop stalls here, i.e. doesn't read any events
        event, values = window.read(timeout=5)  # timeout is in milliseconds
        # Exit event loop if user closes window, going immediately to window.close()
        # Not following this pattern crashes the application.
        if event == sg.WIN_CLOSED:
            break

        if event:
            # try:
            # TODO This GUI framework is terrible and must be replaced. Note that the event handling paradigm
            #  only returns two things, a single-value string indicating that some event has occurred in the
            #  timeout window (which one if more than one has occurred, who knows?), and the array of values
            #  which lets you access the current value for every object in the layout by index. Which means
            #  there is no way to support the use case for a Sequencer, which is to get the list of buttons
            #  which *changed state* in the last time window, i.e. get a *list of events by id*. This means
            #  we have to loop over all the buttons in every cycle and send all note ons to the queue. Which means
            #  latency scales with the length of the sequence, instead of being constant proportional to the number
            #  of buttons clicked, which since a human is doing it and the window is 50 ms is basically one or two.
            #  So, terrible and must be replaced. Also the documentation is really annoying, and the examples suck.
            notes_on_off = (midi_note.MIDI_PARAM_MAX_VAL if v else 0 for v in values.values())
            for velocity in notes_on_off:
                QUEUE.append(velocity)

    window.close()


if __name__ == '__main__':
    generate_measures_and_buttons()
    start()
