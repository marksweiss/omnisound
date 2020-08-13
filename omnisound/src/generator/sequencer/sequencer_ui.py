# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.note.adapter.note import as_dict, set_attr_vals_from_dict, NoteValues, MakeNoteConfig
from omnisound.src.container.measure import Measure
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.generator.scale import HarmonicScale, MajorKey, MinorKey, Scale
import omnisound.src.note.adapter.midi_note as midi_note

NOTE_DUR = NoteDur.QRTR
OCTAVE = 4

ATTR_VALS_DEFAULTS_MAP = NoteValues(midi_note.ATTR_NAMES)
ATTR_VALS_DEFAULTS_MAP.instrument = midi_note.MidiInstrument.Acoustic_Grand_Piano.value
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


def generate_measures_and_buttons():
    for i in range(NUM_TRACKS):
        TRACKS.append([])
        layout_measures = []
        for j in range(NUM_MEASURES):
            measure = Measure.copy(MEASURE)
            TRACKS[i].append(measure)
            layout_notes = []
            for k in range(NOTES_PER_MEASURE):
                # Set each note to the params of the root note in the Scale
                set_attr_vals_from_dict(measure[k], as_dict(SCALE[0]))
                # Key each button to it's (track, measure, note) index into TRACKS list.
                # PySimpleGUI refers to UI objects by "key" and returns this key when events are trapped on the UI.
                # This scheme means each trapped button event will return as its key the index to the note to modify
                layout_notes.append(sg.Button((i, j, k)))
            layout_measures.append(sg.Frame(f'Measure {j}', [layout_notes]))
        LAYOUT[i].append(f'Track {i}', layout_measures)


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


# Create the window
window = sg.Window('Omnisound Sequencer', LAYOUT, size=(1200, 800))

# Create an event loop, necessary or the first event trapped closes the window
while True:
    # This is the framework mechanism for polling the window for events and status
    event, values = window.read()
    # print(event, values)

    # Exit event loop if user closes window, going immediately to window.close()
    # Not following this pattern crashes the application.
    if event == sg.WIN_CLOSED:
        break

    if event:
        note = TRACKS[event[0]][event[1]][event[2]]
        if note.amplitude == 0:
            note.amplitude = midi_note.MIDI_PARAM_MAX_VAL
        else:
            note.amplitude = 0

window.close()