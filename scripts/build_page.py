import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import  Tag, NavigableString
from chord_diagram_generator import generate_chord_svg
from tqdm import tqdm 
PYPPETEER_CHROMIUM_REVISION = '1263111'
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from pyppeteer import launch
import asyncio

Template = 'templates/page_template.html'
#template_soup = BeautifulSoup(Path(Template).read_text(), 'html.parser')
Data = 'data/song_content.json'
max_length = 3400 #px



# Function to read the song content JSON file as a generator
def read_song_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        for song in data:
            yield song

def add_title(soup: Tag, song_data: dict) -> Tag:
    title_div = soup.find('div', id='title')
    title_div.string = song_data['song']['song']
    return soup

def add_meta_data(soup: Tag, song_data: dict) -> Tag:
    metadata_div = soup.find('div', id='metadata')
    metadata_div.string = f"{song_data['song']['artist']} - {song_data['song']['decade']} - {song_data['song']['rating']} - {song_data['metadata']['Key']}"
    return soup

def add_chords(soup: Tag, song_data: dict) -> Tag:
    chord_diagrams_div = soup.find('div', id='chord-diagrams')
    for chord_name in tqdm(song_data['chords'].split(','), desc='iterating over chord names'):
        chord_name = chord_name.strip()
        chord_div = soup.new_tag('div')
        chord_div['class'] = 'chord-diagram' 
        svg_tag = generate_chord_svg(chord_name=chord_name, return_tag=True)
        if svg_tag:
            chord_div.append(svg_tag)  # Append SVG tag to the chord div
            chord_diagrams_div.append(chord_div)  # Append chord div to the chord diagrams div
    return soup

def add_lyrics(soup: Tag, song_data: dict) -> Tag:
    # Extract the content from the song_data dictionary
    lyrics_div = soup.find('div', id='lyrics-and-chords')
    lyrics_content_soup = BeautifulSoup(song_data.get('content', ''), 'html.parser')
    lyrics_div.clear()
    lyrics_div.append(lyrics_content_soup)
    return soup

def build_page_from_template(song_data: dict) -> str:
    template_soup = BeautifulSoup(Path(Template).read_text(), 'html.parser')
    template_soup = add_title(template_soup, song_data)
    template_soup = add_meta_data(template_soup, song_data)
    template_soup = add_chords(template_soup, song_data)
    template_soup = add_lyrics(template_soup, song_data)
    return str(template_soup).replace('\n','').replace('\r','').replace("\\","")

def main():
    data_generator = read_song_content(Data)
    for song_data in data_generator:
        build_page_from_template(song_data)

if __name__ == "__main__":
    main()