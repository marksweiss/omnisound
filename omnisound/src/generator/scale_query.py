# Adapted from here:
# https://gist.githubusercontent.com/mvanga/62a9bd4b85abe37305537d7bf754d7e9/raw/ca7f7b1b42a0b85712c7339471ad6340346f9169/music_theory.py

# Original License:

# The code for my article with the same name. You can find it at the URL below:
# https://www.mvanga.com/blog/basic-music-theory-in-200-lines-of-python

# MIT License
#
# Copyright (c) 2021 Manohar Vanga
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from collections import defaultdict
from pprint import pprint


# The musical ALPHABET consists of seven letter from A through G
ALPHABET = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# The twelve NOTES in Western music, along with their enharmonic equivalents
NOTES = [
    ['B#', 'C', 'Dbb'],
    ['B##', 'C#', 'Db'],
    ['C##', 'D', 'Ebb'],
    ['D#', 'Eb', 'Fbb'],
    ['D##', 'E', 'Fb'],
    ['E#', 'F', 'Gbb'],
    ['E##', 'F#', 'Gb'],
    ['F##', 'G', 'Abb'],
    ['G#', 'Ab'],
    ['G##', 'A', 'Bbb'],
    ['A#', 'Bb', 'Cbb'],
    ['A##', 'B', 'Cb'],
]

KEYS = [
    'B#', 'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'Fb', 'E#', 'F',
    'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B', 'Cb',
]

INTERVAL_TYPES = ['standard', 'major']

# Interval names that specify the distance between two NOTES
INTERVALS = [
    ['P1', 'd2'],  # Perfect unison   Diminished second
    ['m2', 'A1'],  # Minor second     Augmented unison
    ['M2', 'd3'],  # Major second     Diminished third
    ['m3', 'A2'],  # Minor third      Augmented second
    ['M3', 'd4'],  # Major third      Diminished fourth
    ['P4', 'A3'],  # Perfect fourth   Augmented third
    ['d5', 'A4'],  # Diminished fifth Augmented fourth
    ['P5', 'd6'],  # Perfect fifth    Diminished sixth
    ['m6', 'A5'],  # Minor sixth      Augmented fifth
    ['M6', 'd7'],  # Major sixth      Diminished seventh
    ['m7', 'A6'],  # Minor seventh    Augmented sixth
    ['M7', 'd8'],  # Major seventh    Diminished octave
    ['P8', 'A7'],  # Perfect octave   Augmented seventh
]

# Interval names based off the NOTES of the major scale
INTERVALS_MAJOR = [
    ['1', 'bb2'],
    ['b2', '#1'],
    ['2', 'bb3', '9'],
    ['b3', '#2'],
    ['3', 'b4'],
    ['4', '#3', '11'],
    ['b5', '#4', '#11'],
    ['5', 'bb6'],
    ['b6', '#5'],
    ['6', 'bb7', '13'],
    ['b7', '#6'],
    ['7', 'b8'],
    ['8', '#7'],
]

FORMULAS = {
    # Scale formulas
    'scales': {
        # Basic chromatic scale
        'chromatic': '1,b2,2,b3,3,4,b5,5,b6,6,b7,7',
        # Major scale, its modes, and minor scale
        'major': '1,2,3,4,5,6,7',
        'minor': '1,2,b3,4,5,b6,b7',
        # Melodic minor and its modes
        'melodic_minor': '1,2,b3,4,5,6,7',
        # Harmonic minor and its modes
        'harmonic_minor': '1,2,b3,4,5,b6,7',
        # Blues scales
        'major_blues': '1,2,b3,3,5,6',
        'minor_blues': '1,b3,4,b5,5,b7',
        # Penatatonic scales
        'pentatonic_major': '1,2,3,5,6',
        'pentatonic_minor': '1,b3,4,5,b7',
        'pentatonic_blues': '1,b3,4,b5,5,b7',
    },
    'chords': {
        # Major
        'major': '1,3,5',
        'major_6': '1,3,5,6',
        'major_6_9': '1,3,5,6,9',
        'major_7': '1,3,5,7',
        'major_9': '1,3,5,7,9',
        'major_13': '1,3,5,7,9,11,13',
        'major_7_#11': '1,3,5,7,#11',
        # Minor
        'minor': '1,b3,5',
        'minor_6': '1,b3,5,6',
        'minor_6_9': '1,b3,5,6,9',
        'minor_7': '1,b3,5,b7',
        'minor_9': '1,b3,5,b7,9',
        'minor_11': '1,b3,5,b7,9,11',
        'minor_7_b5': '1,b3,b5,b7',
        # Dominant
        'dominant_7': '1,3,5,b7',
        'dominant_9': '1,3,5,b7,9',
        'dominant_11': '1,3,5,b7,9,11',
        'dominant_13': '1,3,5,b7,9,11,13',
        'dominant_7_#11': '1,3,5,b7,#11',
        # Diminished
        'diminished': '1,b3,b5',
        'diminished_7': '1,b3,b5,bb7',
        'diminished_7_half': '1,b3,b5,b7',
        # Augmented
        'augmented': '1,3,#5',
        # Suspended
        'sus2': '1,2,5',
        'sus4': '1,4,5',
        '7sus2': '1,2,5,b7',
        '7sus4': '1,4,5,b7',
    },
}

FORMULA_TO_INTERVAL_TYPES = {
    'chromatic': 'major',
    # Major scale, its modes, and minor scale
    'major': 'major',
    'minor': 'major',
    # Melodic minor and its modes
    'melodic_minor': 'major',
    # Harmonic minor and its modes
    'harmonic_minor': 'major',
    # Blues scales
    'major_blues': 'major',
    'minor_blues': 'major',
    # Penatatonic scales
    'pentatonic_major': 'major',
    'pentatonic_minor': 'major',
    'pentatonic_blues': 'major',
}

MAJOR_MODE_ROTATIONS = {
    'Ionian': 0,
    'Dorian': 1,
    'Phrygian': 2,
    'Lydian': 3,
    'Mixolydian': 4,
    'Aeolian': 5,
    'Locrian': 6,
}


class ScaleQuery:
    def __init__(self):  # sourcery skip: hoist-statement-from-if
        self.key_interval_note_maps = defaultdict(dict)
        self.scales = defaultdict(dict)
        self.modes = defaultdict(dict)

        for key in KEYS:
            for interval_type in INTERVAL_TYPES:
                self.key_interval_note_maps[key][interval_type] = self.make_interval_note_map(key, interval_type)

                for scale_type, formula in FORMULAS['scales'].items():
                    interval_maker = self.make_intervals_major \
                        if FORMULA_TO_INTERVAL_TYPES[scale_type] == 'major' else self.make_intervals
                    self.scales[key][scale_type] = self.make_formula(
                        formula,
                        interval_maker(key)
                    )

                    for mode_name, degree in MAJOR_MODE_ROTATIONS.items():
                        scale = self.scales[key][scale_type]
                        rotated_scale = self.mode(scale, degree)
                        self.modes[rotated_scale[0]][mode_name] = rotated_scale

    @staticmethod
    def find_note_index(scale, search_note):
        """ Given a scale, find the index of a particular note """
        for i, note in enumerate(scale):
            # Deal with situations where we have a list of enharmonic
            # equivalents, as well as just a single note as and str.
            if (type(note) == list and search_note in note or
                    type(note) != list and type(note) == str and search_note == note):
                return i

    @staticmethod
    def rotate(scale, n):
        """ Left-rotate a scale by n positions. """
        return scale[n:] + scale[:n]

    @staticmethod
    def mode(scale, degree):
        return ScaleQuery.rotate(scale, degree)

    @staticmethod
    def chromatic(key):
        """ Generate a chromatic scale in a given key. """
        # Figure out how much to rotate the NOTES list by and return
        # the rotated version.
        num_rotations = ScaleQuery.find_note_index(NOTES, key)
        return ScaleQuery.rotate(NOTES, num_rotations)

    @staticmethod
    def make_formula(formula, labeled):
        """
        Given a comma-separated interval formula, and a set of labeled
        NOTES in a key, return the NOTES of the formula.
        """
        return [labeled[x] for x in formula.split(',')]

    @staticmethod
    def find_note_by_root(notes, root):
        """
        Given a list of NOTES, find it's ALPHABET. Useful for figuring out which
        enharmonic equivalent we must use in a particular scale.
        """
        for note in notes:
            if note[0] == root:
                return note

    @staticmethod
    def make_intervals(root):
        labeled = {}
        c = ScaleQuery.chromatic(root)
        start_index = ScaleQuery.find_note_index(ALPHABET, root[0])
        for i, interval in enumerate(INTERVALS):
            for interval_name in interval:
                interval_index = int(interval_name[1]) - 1
                note = c[i % len (c)]
                note_root = ALPHABET[(start_index + interval_index) % len(ALPHABET)]
                if note_root is not None:
                    labeled[interval_name] = ScaleQuery.find_note_by_root(note, note_root)
        return labeled

    @staticmethod
    def make_intervals_major(root):
        labeled = {}
        c = ScaleQuery.chromatic(root)
        start_index = ScaleQuery.find_note_index(ALPHABET, root[0])
        for i, interval in enumerate(INTERVALS_MAJOR):
            for interval_name in interval:
                interval_index = int(re.sub ('[b#]', '', interval_name)) - 1
                note = c[i % len(c)]
                note_root = ALPHABET[(start_index + interval_index) % len(ALPHABET)]
                if note_root is not None:
                    labeled[interval_name] = ScaleQuery.find_note_by_root (note, note_root)
        return labeled

    def make_interval_note_map(self, key, interval_type='standard'):
        # Our labeled set of NOTES mapping interval names to NOTES
        labels = {}

        # Step 1: Generate a chromatic scale in our desired key
        chromatic_scale = self.chromatic(key)

        # The alphabets starting at provided key
        alphabet_key = self.rotate(ALPHABET, self.find_note_index(ALPHABET, key[0]))

        intervs = INTERVALS if interval_type == 'standard' else INTERVALS_MAJOR
        # Iterate through all intervals (list of lists)
        for index, interval_list in enumerate(intervs):

            # Step 2: Find the NOTES to search through based on degree
            notes_to_search = chromatic_scale[index % len(chromatic_scale)]

            degree = None
            for interval_name in interval_list:
                # Get the interval degree
                if interval_type == 'standard':
                    degree = int(interval_name[1]) - 1  # e.g. M3 --> 2, m7 --> 6
                elif interval_type == 'major':
                    degree = int(re.sub('[b#]', '', interval_name)) - 1

                # Get the ALPHABET to look for
                alphabet_to_search = alphabet_key[degree % len(alphabet_key)]

                # print('Interval {}, degree {}: looking for ALPHABET {} in NOTES {}'.format(interval_name, degree,
                #                                                                            alphabet_to_search,
                #                                                                            notes_to_search))
                # noinspection PyBroadException
                try:
                    note = [x for x in notes_to_search if x[0] == alphabet_to_search][0]
                except:
                    note = notes_to_search[0]

                labels[interval_name] = note

        return labels

    @staticmethod
    def dump(scale, separator=' '):
        """
        Pretty-print the NOTES of a scale. Replaces b and # characters
        for unicode flat and sharp symbols.
        """
        return separator.join(['{:<3s}'.format(x) for x in scale]) \
            .replace('b', '\u266d') \
            .replace('#', '\u266f')


if __name__ == '__main__':
    # load data for all intervals, scales and modes
    scale_query = ScaleQuery()
    # block on user input and process queries for key and either scale or mode
    while True:
        key = input("key: (wrap in double quotes)")
        query_type = input("scale ('s') or mode ('m') (wrap in double quotes): ")
        if query_type == '"s"':
            pprint(scale_query.scales[key[1:-1].strip().upper()])
        elif query_type == '"m"':
            pprint(scale_query.modes[key[1:-1].strip().upper()])
