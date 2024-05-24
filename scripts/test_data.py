import json
from bs4 import BeautifulSoup
from pathlib import Path
Data = 'data/song_content.json'


# Function to read the song content JSON file as a generator
def read_song_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        for song in data:
            yield song


def main():
    data_generator = read_song_content(Data)
    for song_data in data_generator:
        soup = BeautifulSoup(song_data['html'], 'html.parser')
        Path(f"test/{song_data['song']['song']}.html").write_text(str(soup.prettify()))

if __name__ == "__main__":
    main()