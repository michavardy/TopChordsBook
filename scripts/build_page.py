import json
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import  Tag, NavigableString
from chord_diagram_generator import generate_chord_svg
from tqdm import tqdm 

Template = 'templates/page_template.html'
#template_soup = BeautifulSoup(Path(Template).read_text(), 'html.parser')
Data = 'data/song_content.json'



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
        #svg_path = chords.get_guitar_chord_path(chord_name=chord_name)  # Assuming you have a function to get SVG path
        chord_div = soup.new_tag('div')
        #chord_div['class'] = 'chord-diagram'  # You can add a class for styling if needed
        #svg_tag = soup.new_tag('svg', width="125", height="150", attrs={
        #    "xmlns": "http://www.w3.org/2000/svg",
        #    "xmlns:xlink": "http://www.w3.org/1999/xlink",
        #    "xmlns:ev": "http://www.w3.org/2001/xml-events",
        #    "baseProfile": "full",
        #    "version": "1.1"
        #})
        #svg_content = Path(svg_path).read_text()
        #svg_tag.append(BeautifulSoup(svg_content, 'html.parser'))  # Parse the SVG content and append it to the SVG tag
        svg_tag = generate_chord_svg(chord_name=chord_name, return_tag=True)
        chord_div.append(svg_tag)  # Append SVG tag to the chord div
        chord_diagrams_div.append(chord_div)  # Append chord div to the chord diagrams div
    return soup

def add_lyrics(soup: Tag, song_data: dict) -> Tag:
    # Extract the content from the song_data dictionary
    lyrics_content = song_data.get('content', '')

    # Parse the HTML content of the lyrics separately
    lyrics_soup = BeautifulSoup(lyrics_content, 'html.parser',  preserve_whitespace_tags=['span'])


    # Find the div element with id "lyrics-and-chords"
    div_lyrics = soup.find('div', id='lyrics-and-chords')

    # Check if the div element is found
    if div_lyrics:
        # Append the parsed lyrics content to the div's existing content
        div_lyrics.append(lyrics_soup)

    return soup

def build_page_from_template(song_data: dict):
    template_soup = BeautifulSoup(Path(Template).read_text(), 'html.parser')
    template_soup = add_title(template_soup, song_data)
    template_soup = add_meta_data(template_soup, song_data)
    template_soup = add_chords(template_soup, song_data)
    template_soup = add_lyrics(template_soup, song_data)

    Path(f"test/{song_data['song']['song']}.html").write_text(str(template_soup.prettify()))

def main():
    data_generator = read_song_content(Data)
    for song_data in data_generator:
        build_page_from_template(song_data)

if __name__ == "__main__":
    main()