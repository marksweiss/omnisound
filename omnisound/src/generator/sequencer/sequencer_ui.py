# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.note.adapter.note import as_dict, set_attr_vals_from_dict, MakeNoteConfig
from omnisound.src.container.measure import Measure
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.generator.scale import HarmonicScale, MajorKey, MinorKey, Scale
import omnisound.src.note.adapter.midi_note as midi_note

NUM_TRACKS = 1
NUM_MEASURES = 4
NOTE_DUR = NoteDur.QRTR
METER = Meter(beats_per_measure=4, beat_note_dur=NOTE_DUR, tempo=120, quantizing=True)
NOTES_PER_MEASURE = METER.quarter_notes_per_beat_note * METER.beats_per_measure
MEASURE_PROTOTYPE = Measure(meter=METER, num_notes=NOTES_PER_MEASURE)

# TODO ADD make_default_note() factory method to each note module to get rid of boilerplate
# TODO NEED a copy_note() so we can for example use a Scale as a note factory
MIDI_INSTRUMENT = midi_note.MidiInstrument.Acoustic_Grand_Piano
NUM_ATTRIBUTES = midi_note.NUM_ATTRIBUTES
ATTR_NAME_IDX_MAP = midi_note.ATTR_NAME_IDX_MAP
START = 0
DUR = NOTE_DUR.QUARTER.value
AMP = midi_note.MIDI_PARAM_MAX_VAL
OCTAVE = 4
PITCH = midi_note.get_pitch_for_key(MajorKey.C, OCTAVE)
ATTR_VALS_DEFAULTS_MAP = {'instrument': float(MIDI_INSTRUMENT.value),
                          'time': START,
                          'duration': DUR,
                          'velocity': AMP,
                          'pitch': PITCH}


HARMONIC_SCALE = HarmonicScale.Major
KEY = MajorKey
SCALE = Scale(KEY, OCTAVE, HARMONIC_SCALE,
              MakeNoteConfig(cls_name=midi_note.CLASS_NAME,
                             num_attributes=NUM_ATTRIBUTES,
                             make_note=midi_note.make_note,
                             get_pitch_for_key=midi_note.get_pitch_for_key,
                             attr_name_idx_map=ATTR_NAME_IDX_MAP,
                             attr_vals_defaults_map=ATTR_VALS_DEFAULTS_MAP,
                             attr_get_type_cast_map={}))

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
            measure = Measure.copy(MEASURE_PROTOTYPE)
            TRACKS[i].append(measure)
            layout_notes = []
            for k in range(NOTES_PER_MEASURE):
                set_attr_vals_from_dict(measure[k], as_dict(SCALE[0]))
                # Key each button to it's (track, measure, note) index into TRACKS list.
                # PySimpleGUI refers to UI objects by "key" and returns this key when events are trapped on the UI.
                layout_notes.append(sg.Button((i, j, k)))

            measure_frame = sg.Frame(f'Measure {j}', [layout_notes])
            layout_measures.append(measure_frame)
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
        note.amplitude = 0 if note.amplitude == midi_note.MIDI_PARAM_MAX_VAL else note.amplitude = 0

window.close()
