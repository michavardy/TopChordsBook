import fretboard
import requests
import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Strings:
    strings: str
    fingering: str
    chordName: str
    enharmonicChordName: str
    tones: str

class GenerateGuitarChords:

    CHORD_CACHE = {}

    def __init__(self):
        self.initialize_chord_cache()

    def initialize_chord_cache(self):
        self.CHORD_CACHE = {c.stem: str(c) for c in Path('chords').iterdir()}

    def generate_svg_image(self, strings: Strings, chord_name:str) -> str:
        if not strings:
            return None
        image_path = f'chords/{strings.chordName}.svg'
        chord = fretboard.Chord(positions=strings.strings, fingers=strings.fingering, title=strings.chordName)
        #chord = fretboard.Chord(positions=strings.strings, fingers=strings.fingering)
        chord.save(image_path)
        self.CHORD_CACHE[chord_name] = image_path
        return image_path

    def correct_chord_name(self, chord_name: str) -> str:
        if "m" in chord_name:
            chord_list = chord_name.split('m')
            chord_list[1] = 'm' + chord_list[1]
            return "_".join(chord_list)
        if "7" in chord_name:
            chord_list = chord_name.split('7')
            chord_list[1] = '7' + chord_list[1]
            return "_".join(chord_list)
        if "/" in chord_name:
            chord_list = chord_name.split('/')
            return "__".join(chord_list)
        else:
            return chord_name


    def get_strings_from_chord_name(self, chord_name:str) -> Strings:
        # Define the API endpoint and chord name
        chord_name = self.correct_chord_name(chord_name)
        base_endpoint = f"https://api.uberchord.com/v1/chords/{chord_name}"

        # Make the GET request
        response = requests.get(base_endpoint)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            try:
                data = response.json()[0]
                return Strings(
                    strings = data['strings'].replace(" ", ""),
                    fingering = data['fingering'].replace(" ", ""),
                    chordName = chord_name,
                    enharmonicChordName = data['enharmonicChordName'].replace(",",""),
                    tones = data['tones'].replace(",","")
                )
            except IndexError:
                return None
        else:
            return None

    def get_guitar_chord_path(self, chord_name:str) -> str:
        if chord_name in self.CHORD_CACHE.keys():
            return self.CHORD_CACHE[chord_name]
        else:
            strings = self.get_strings_from_chord_name(chord_name)
            return self.generate_svg_image(strings, chord_name)
        
if __name__ == "__main__":
    chord_gen = GenerateGuitarChords()
    chord = chord_gen.get_guitar_chord_path(chord_name="Em")
