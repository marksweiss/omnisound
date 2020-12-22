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
# Then make event loop the async event loop from midi player so timing is controlled

# TO RUN:  python3 -m omnisound.src.generator.sequencer.sequencer_ui \
#               --num-tracks 2 --measures-per-track 4 --tempo 120 --meter 13/4

from collections import defaultdict
from itertools import count
from optparse import OptionParser
from time import sleep
import threading

# noinspection PyProtectedMember
from mido import open_output
# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.container.measure import Measure
from omnisound.src.container.track import MidiTrack
from omnisound.src.generator.chord import Chord
from omnisound.src.generator.chord_globals import HarmonicChord
from omnisound.src.generator.scale import HarmonicScale, MajorKey, Scale
from omnisound.src.generator.scale_globals import MAJOR_KEY_DICT
from omnisound.src.note.adapter.note import as_dict, set_attr_vals_from_dict, NoteValues
from omnisound.src.note.adapter.midi_note import pitch_for_key
from omnisound.src.modifier.meter import Meter
from omnisound.src.player.midi.midi_player import get_midi_messages_and_notes_for_track
from omnisound.src.utils.mingus_utils import get_chord_pitches
import omnisound.src.note.adapter.midi_note as midi_note

# Note config
# TODO Make configurable in the UI
OCTAVE = 4
# TODO Make configurable in the UI
INSTRUMENT = midi_note.MidiInstrument.Acoustic_Grand_Piano.value

# Scale config
# TODO Make configurable in the UI
HARMONIC_SCALE = HarmonicScale.Major
HARMONIC_CHORD = HarmonicChord.MajorTriad
# TODO Make configurable in the UI
KEY = MajorKey
KEY_PITCH = KEY.C
KEY_DICT = MAJOR_KEY_DICT

# Mido config
# TODO Make configurable in the UI
PORT_NAME = 'omnisound_sequencer'

# Globals
TRACKS = []
LAYOUT = []
# Used by the window event loop thread to communicate captured note events to the Midi playback thread
CHANNELS = []
# Used by the window event loop to hightligh current playing note
NOTE_ELEMENTS = defaultdict(list)
THREAD_COUNTER = []

def _get_note_config_and_scale(meter):
    attr_val_default_map = NoteValues(midi_note.ATTR_NAMES)
    # TODO Make configurable from UI
    attr_val_default_map.instrument = INSTRUMENT
    attr_val_default_map.time = 0
    # We can use beat_note_dur_secs because sequencer currently supports only all notes being beat duration
    # If we allow note duration to be configured we would use `meter.get_secs_for_note_time(note_dur)`
    attr_val_default_map.duration = meter.beat_note_dur_secs
    # TODO Make configurable from UI
    attr_val_default_map.velocity = 0
    # TODO Make configurable from UI
    attr_val_default_map.pitch = midi_note.pitch_for_key(key=KEY_PITCH, octave=OCTAVE)  # C4 60 "Middle C"
    note_config = midi_note.DEFAULT_NOTE_CONFIG()
    note_config.attr_val_default_map = attr_val_default_map.as_dict()
    # TODO Make Scale configurable in the UI
    scale = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, mn=note_config)
    return note_config, scale


# TODO Swing support in UI
def _generate_tracks_and_layout(num_tracks, measures_per_track, meter):
    note_config, scale = _get_note_config_and_scale(meter)

    for track_idx in range(num_tracks):
        track = MidiTrack(meter=meter, channel=track_idx, instrument=INSTRUMENT)
        TRACKS.append(track)

        CHANNELS.append([])
        LAYOUT.append([])
        layout_measures_row = []

        mingus_keys = Chord.get_mingus_chord_for_harmonic_chord(key=KEY_PITCH, harmonic_chord=HarmonicChord.MajorTriad)
        mingus_key_to_enum_mapping = Scale.get_mingus_key_to_key_enum_mapping(KEY)

        chord_label = \
            f'{KEY_PITCH.name}.{HARMONIC_CHORD.name}:.{"-".join(mingus_key_to_enum_mapping[mingus_key].name for mingus_key in mingus_keys)}'
        chord_pitches = '_'.join(str(pitch) for pitch in
                                 get_chord_pitches(mingus_keys=mingus_keys,
                                                   mingus_key_to_key_enum_mapping=mingus_key_to_enum_mapping,
                                                   pitch_for_key=pitch_for_key,
                                                   octave=OCTAVE))

        for measure_idx in range(measures_per_track):
            measure = Measure(meter=meter, num_notes=meter.beats_per_measure, mn=note_config)
            track.append(measure)

            layout_notes = []
            for k in range(meter.beats_per_measure):
                # Initialize each note to the params of the root note in the Scale
                set_attr_vals_from_dict(measure[k], as_dict(scale[0]))

                # PySimpleGUI refers to UI objects by "key" and returns this key when events are trapped on the UI.
                # Prepend key with track num, this is the channel for the queue of messages from the UI to this track.
                # Key each button to it's index in the flattened Messages list, key * 2 because the
                # index into Messages is even indexes, because Messages are note_on/note_off pairs.
                # NOTE: 'key' is overloaded and here means unique id referring to PySimpleGUI object.
                # key must be unique. For note on_off the value is unique on each iteration so don't need key
                event_id = f'{track_idx}_{2 * ((measure_idx * meter.beats_per_measure) + k)}'
                start_key = f'note_on_off|{event_id}|{event_id}'
                chord_key = f'chord|{event_id}|{str(chord_pitches)}'

                note_checkbox = sg.Checkbox(str (k + 1), default=False, enable_events=True, key=start_key)
                layout_notes.append(note_checkbox)
                NOTE_ELEMENTS[track_idx].append(note_checkbox)
                # chord_key needs a unique key id and a value, because values (i.e. which chord a note is) can repeat
                layout_notes.append(sg.DropDown(values=str(chord_label), key=chord_key,
                                                enable_events=True, size=(15, 15)))
            layout_measures_row.append(sg.Frame(title=f'Measure {measure_idx + 1}', layout=[layout_notes]))
        LAYOUT[track_idx].append(sg.Frame(title=f'Track {track_idx + 1}', layout=[layout_measures_row]))


# noinspection PyUnresolvedReferences
def _loop_track(track, track_idx, num_notes, port):
    # sourcery skip: hoist-statement-from-loop
    with port:
        messages_0, durations_0 = get_midi_messages_and_notes_for_track(track)
        messages_1, durations_1 = get_midi_messages_and_notes_for_track(track)
        messages_2, durations_2 = get_midi_messages_and_notes_for_track(track)
        messages_list = (messages_0, messages_1, messages_2)
        durations_list = (durations_0, durations_1, durations_2)
        loop_duration = messages_0[-1].time
        for j in count():
            while CHANNELS[track_idx]:
                note_idx, event_type, event_data = CHANNELS[track_idx].pop()

                if event_type == 'note_on_off':
                    for messages in messages_list:
                        messages[note_idx].velocity = event_data
                elif event_type == 'chord':
                    for chord_note_idx, messages in enumerate(messages_list):
                        messages[note_idx].note = event_data[chord_note_idx]

            for i in range(0, len(messages_0), 2):
                for duration_list_idx, messages in enumerate(messages_list):
                    messages[i].time += (j * loop_duration)
                    if messages[i].velocity:
                        port.send(messages[i])
                        # Sleep for note duration: this essentially controls tempo
                        sleep(durations_list[duration_list_idx][int(i / 2)])
                        port.send(messages[i + 1])
                    else:
                        sleep(durations_list[duration_list_idx][int(i / 2)])

                    # Update current note indicator by changing text color. Should be its own function but not for performance.
                    last_counter = THREAD_COUNTER[track_idx]
                    NOTE_ELEMENTS[track_idx][last_counter].update(text_color='black')
                    counter = last_counter + 1 if last_counter + 1 < num_notes else 0
                    NOTE_ELEMENTS[track_idx][counter].update(text_color='red')
                    THREAD_COUNTER[track_idx] = counter


# noinspection PyBroadException
def start(notes_per_measure, measures_per_track):
    # This launches the parent thread / event loop
    window = sg.Window('Omnisound Sequencer', LAYOUT)
    port = open_output(PORT_NAME, True)  # flag is virtual=True to create a MIDI virtual port

    # Init state for updating display in the track event handler loops
    notes_per_track = notes_per_measure * measures_per_track
    for track_idx, track in enumerate(TRACKS):
        THREAD_COUNTER.append(0)  # per-thread counter
        # This binds a thread per track to handle events (interactive, not timing events) to function _loop_track()
        threading.Thread(target=_loop_track,
                         args=(track, track_idx, notes_per_track, port),
                         daemon=True).start()

    # Create an event loop, necessary or the first event trapped closes the window
    while True:
        # This is the framework mechanism for polling the window for events and status
        # Tune responsiveness with the timeout arg (in milliseconds), 0 means no timeout but can be unstable
        event, values = window.read(timeout=5)
        # Exit event loop if user closes window, going immediately to window.close(). Any other pattern crashes.
        if event == sg.WIN_CLOSED:
            break

        if event != '__TIMEOUT__':
            event_type, event_id, event_data = event.split('|')
            track_idx, note_idx = event_id.split('_')

            if event_type == 'note_on_off':
                # event is the key value for the sg checkbox that changed state, which we set to the index into the
                # MIDI messages for the note being manipulated by the checkbox. values is a dict of {event: value}
                # for the state of all UI elements by key value. In this case, for checkboxes, values is a dict of
                # {event: True/False}. So if True, the checkbox is checked on and set the volume positive, else set to 0.
                # Parse the event for the track that generated it and the note idx into the measures for the track,
                # push (note_idx, note changes) onto the queue (channel) for the track
                CHANNELS[int(track_idx)].append(
                    (int(note_idx),
                     event_type,
                     midi_note.MIDI_PARAM_MAX_VAL if values[event] else 0)
                )
            elif event_type == 'chord':
                chord_pitches = [int(pitch) for pitch in event_data.split('_')]
                CHANNELS[int(track_idx)].append(
                        (int(note_idx),
                         event_type,
                         [int(p) for p in chord_pitches] if values[event] else (0, 0, 0))
                )

    window.close()


def _parse_args():
    parser = OptionParser()
    parser.add_option('-n', '--num-tracks', dest='num_tracks', type='int', help='Number of sequencer tracks')
    parser.add_option('-l', '--measures-per-track', dest='measures_per_track', type='int',
                      help='Number of measures per sequencer track')
    parser.add_option('-t', '--tempo', dest='tempo', type='int',
                      help='Tempo in beats per minute of all sequencer tracks')
    parser.add_option('-m', '--meter',
                      action='store', dest='meter', default='4/4', type='string',
                      help='Meter of sequencer tracks. Default is 4/4.')

    return parser.parse_args()


if __name__ == '__main__':
    options, _ = _parse_args()
    beats_per_measure, beat_note_dur = Meter.get_bpm_and_duration_from_meter_string(options.meter)
    _generate_tracks_and_layout(options.num_tracks, options.measures_per_track,
                                Meter(beats_per_measure=beats_per_measure, beat_note_dur=beat_note_dur,
                                      tempo=options.tempo))
    start(beats_per_measure, options.measures_per_track)
