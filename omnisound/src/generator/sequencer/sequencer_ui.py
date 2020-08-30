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

# TO RUN:  python -m omnisound.src.generator.sequencer.sequencer_ui \
#               --num-tracks 2 --measures-per-track 4 --tempo 120 --meter 13/4

from itertools import chain, count
from optparse import OptionParser
from time import sleep
import threading

# noinspection PyProtectedMember
from mido import open_output
# noinspection PyPep8Naming
import PySimpleGUI as sg

from omnisound.src.container.measure import Measure
from omnisound.src.container.track import MidiTrack
# from omnisound.src.generator.sequencer.midi_sequencer import MidiMultitrackSequencer
from omnisound.src.generator.scale import HarmonicScale, MajorKey, Scale
from omnisound.src.note.adapter.note import as_dict, set_attr_vals_from_dict, NoteValues
from omnisound.src.modifier.meter import Meter, NoteDur
from omnisound.src.player.midi.midi_player import get_midi_messages_and_notes_for_track
import omnisound.src.note.adapter.midi_note as midi_note

# Note config
NOTE_DUR = NoteDur.QRTR
OCTAVE = 4
INSTRUMENT = midi_note.MidiInstrument.Acoustic_Grand_Piano.value
ATTR_VAL_DEFAULT_MAP = NoteValues(midi_note.ATTR_NAMES)
ATTR_VAL_DEFAULT_MAP.instrument = INSTRUMENT
ATTR_VAL_DEFAULT_MAP.time = 0
ATTR_VAL_DEFAULT_MAP.duration = NOTE_DUR.QUARTER.value
ATTR_VAL_DEFAULT_MAP.velocity = 0
ATTR_VAL_DEFAULT_MAP.pitch = midi_note.pitch_for_key(key=MajorKey.C, octave=OCTAVE)  # C4 60 "Middle C"
NOTE_CONFIG = midi_note.DEFAULT_NOTE_CONFIG()
NOTE_CONFIG.attr_val_default_map = ATTR_VAL_DEFAULT_MAP.as_dict()

# Scale config
HARMONIC_SCALE = HarmonicScale.Major
KEY = MajorKey
SCALE = Scale(key=KEY, octave=OCTAVE, harmonic_scale=HARMONIC_SCALE, mn=NOTE_CONFIG)

# Mido config
PORT_NAME = 'omnisound_sequencer'

# Globals
# SEQUENCER = None
TRACKS = []
LAYOUT = []
# Used by the window event loop thread to communicate captured note events to the Midi playback thread
CHANNELS = []


def generate_tracks_and_layout(num_tracks, measures_per_track, meter):
    # global SEQUENCER
    # SEQUENCER = MidiMultitrackSequencer(name='UI Sequencer', num_measures=num_tracks * measures_per_track,
    #                                     meter=meter, swing=None, arpeggiator_chord=None, mn=NOTE_CONFIG)

    for i in range(num_tracks):
        track = MidiTrack(meter=meter, channel=i + 1, instrument=INSTRUMENT)
        TRACKS.append(track)
        CHANNELS.append([])
        LAYOUT.append([])
        layout_measures = []
        for j in range(measures_per_track):
            measure = Measure(meter=meter, num_notes=meter.beats_per_measure, mn=NOTE_CONFIG)
            track.append(measure)

            layout_notes = []
            for k in range(meter.beats_per_measure):
                # Set each note to the params of the root note in the Scale
                set_attr_vals_from_dict(measure[k], as_dict(SCALE[0]))

                # PySimpleGUI refers to UI objects by "key" and returns this key when events are trapped on the UI.
                # Key each button to it's index in the flattened Messages list.
                # key * 2 because the index into Messages is even indexes, because Messages are note_on/note_off pairs.
                key = 2 * ((j * meter.beats_per_measure) + k)
                # Prepend key with track number, this is the channel for the queue of messages from the UI to this track
                key = f'{i}_{key}'
                layout_notes.append(sg.Checkbox(str(k + 1), default=False, enable_events=True, key=key))
            layout_measures.append(sg.Frame(title=f'Measure {j + 1}', layout=[layout_notes]))
        LAYOUT[i].append(sg.Frame(title=f'Track {i + 1}', layout=[layout_measures]))


def _loop_track(track, track_idx, port):
    with port:
        messages, durations = get_midi_messages_and_notes_for_track (track)
        loop_duration = messages[-1].time
        for j in count():
            while CHANNELS[track_idx]:
                i, velocity = CHANNELS[track_idx].pop()

                # TEMP DEBUG
                print(i)

                messages[i].velocity = velocity

            for i in range(0, len(messages), 2):
                messages[i].time += (j * loop_duration)
                # Only send midi messages if the note has positive volume(will make a sound)
                if messages[i].velocity:

                    # TEMP DEBUG
                    print(f'Sending velocity {messages[i].velocity} to track {track_idx} message {i}')

                    port.send(messages[i])
                    sleep(durations[int(i / 2)])
                    port.send(messages[i + 1])
                else:
                    sleep(durations[int(i / 2)])


# noinspection PyBroadException
def start():
    # This launches the parent thread / event loop
    window = sg.Window('Omnisound Sequencer', LAYOUT)
    # This launches a second thread running the calls write to the Midi output port in parallel to the UI thread
    # noinspection PyUnresolvedReferences
    # SEQUENCER.loop()
    port = open_output(PORT_NAME, True)  # flag is virtual=True to create a MIDI virtual port
    for i, track in enumerate(TRACKS):
        threading.Thread(target=_loop_track, args=(track, i, port), daemon=True).start()

    # Create an event loop, necessary or the first event trapped closes the window
    while True:
        # This is the framework mechanism for polling the window for events and status
        # Tune responsiveness with the timeout arg(in milliseconds), 0 means no timeout
        event, values = window.read(timeout=5)
        # Exit event loop if user closes window, going immediately to window.close(). Any other pattern crashes.
        if event == sg.WIN_CLOSED:
            break

        if event != '__TIMEOUT__':
            # event is the key value for the sg checkbox that changed state, which we set to the index into the
            # MIDI messages for the note being manipulated by the checkbox. values is a dict of {event: value}
            # for the state of all UI elements by key value. In this case, for checkboxes, values is a dict of
            # {event: True/False}. So if True, the checkbox is checked on and set the volume positive, else set to 0.
            # Parse the event for the track that generated it and the note idx into the measures for the track,
            # push (note_idx, note changes) onto the queue (channel) for the track
            track_idx, note_idx = event.split('_')

            # TEMP DEBUG
            print(f'channel {track_idx}, note {note_idx}')

            CHANNELS[int(track_idx)].append((int(note_idx), midi_note.MIDI_PARAM_MAX_VAL if values[event] else 0))

    window.close()


def _parse_args():
    parser = OptionParser()
    parser.add_option('-n', '--num-tracks', dest='num_tracks', type="int", help="Number of sequencer tracks")
    parser.add_option('-l', '--measures-per-track', dest='measures_per_track', type="int",
                      help="Number of measures per sequencer track")
    parser.add_option('-t', '--tempo', dest='tempo', type="int",
                      help="Tempo in beats per minute of all sequencer tracks")
    parser.add_option("-m", "--meter",
                      action="store", dest="meter", default='4/4', type="string",
                      help="Meter of sequencer tracks. Default is 4/4.")

    return parser.parse_args()


if __name__ == '__main__':
    options, _ = _parse_args()
    beats_per_measure, beat_note_dur = Meter.get_bpm_and_duration_from_meter_string(options.meter)
    generate_tracks_and_layout(options.num_tracks, options.measures_per_track,
                               Meter(beats_per_measure=beats_per_measure, beat_note_dur=beat_note_dur))
    start()
