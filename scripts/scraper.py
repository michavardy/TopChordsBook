from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag, NavigableString
from pathlib import Path
import pdfkit
import json
import asyncio
import os
import re
import base64
from dataclasses import dataclass
from tqdm import tqdm
from typing import Optional
PYPPETEER_CHROMIUM_REVISION = '1263111'
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from pyppeteer import launch
from build_page import build_page_from_template
# C:\Users\micha.vardy\AppData\Local\pyppeteer\pyppeteer\local-chromium\1263111
SONG_CONTENT = 'data/song_content.json'
@dataclass
class Song_Data:
    artist: str
    song: str
    decade: str
    rating: str
    type: str
    url: str

@dataclass
class Meta_Data:
    Difficulty: Optional[str] = None
    Tuning: Optional[str] = None
    Key: Optional[str] = None
    Capo: Optional[str] = None


@dataclass
class Song_Content:
    song: Song_Data
    metadata: Meta_Data
    chords: list[str]
    content: str
    html: str
    

async def fetch_content(url:str, selector:str) -> str:
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url, timeout=60000)
    await page.waitForSelector(selector)
    html_content = await page.content()
    await browser.close()
    return html_content

def parse_songs(song_divs: ResultSet, decade:str, page:int, total_songs: int) -> list[Song_Data]:
    songs = []
    for song_div in tqdm(song_divs, desc=f"Scraping songs for decade: {decade}, page: {page}, total_songs: {total_songs}"):
        try:
            songs.append(Song_Data(
                artist = song_div.find('div', class_='lIKMM lz4gy').text.strip(),
                song = re.sub(r'\(ver.*\)', '', song_div.find('div', class_='lIKMM g7KZB').text.strip()),
                url = song_div.find('div', class_='lIKMM g7KZB').find('a')['href'].strip(),
                rating = song_div.find('div', class_='djFV9').text.strip(),
                type = song_div.find('div', class_='lIKMM PdXKy').text.strip(),
                decade=decade,
            ))
        except AttributeError:
            continue   
    return songs

# Function to scrape top 100 songs for a decade
async def get_songs(decade: str, page: int = 1) -> list[Song_Data]:
    songs = []
    while len(songs) < 500:
        url = f"https://www.ultimate-guitar.com/explore?decade[]={decade}&page={page}"
        html = await fetch_content(url,'div.LRSRs')
        song_divs = BeautifulSoup(html, 'html.parser').find_all('div', class_='LQUZJ')
        parsed_songs = parse_songs(song_divs, decade, page, len(songs))
        if not parsed_songs:
            break
        songs.extend(parsed_songs)
        page += 1
    return songs

async def get_all_songs() -> None:
    songs = []
    decades = ['1960', '1970','1980','1990','2000','2010']  # Update with proper decades
    for decade in decades:
        decade_songs = await get_songs(decade)
        songs.extend(decade_songs)
    Path('songs.json').write_text(json.dumps([song.__dict__ for song in songs], indent=4))

def extract_meta_data(table: Tag) -> Meta_Data:
    table_dict = dict(zip(
        [header.text.strip()[:-1] for header in table.find_all('th')], 
        [data.text.strip() for data in table.find_all('td')
         ]))
    return Meta_Data(**table_dict)

def extract_pdf_b64(article_div: Tag) -> str:
    file_path = 'output.pdf'
    page = article_div.find('section', class_='OnD3d kmZt1')
    options = {'page-size': 'Letter', 'margin-top': '0.75in', 'margin-right': '0.75in', 'margin-bottom': '0.75in', 'margin-left': '0.75in',}
    pdfkit.from_string(str(page), file_path, options=options)
    with open(file_path, "rb") as pdf_file:
        encoded = base64.b64encode(pdf_file.read())
    #with open("test_decoded_pdf.pdf", "wb") as pdf_file:
    #    pdf_file.write(base64.b64decode(encoded))
    Path(file_path).unlink()
    pdf_b64_str = encoded.decode('utf-8')  # Decode bytes to string
    pdf_b64_json_serializable = base64.b64encode(pdf_b64_str.encode('utf-8')).decode('utf-8')  # Encode string to base64
    return pdf_b64_json_serializable


async def capture_screenshot(html_content: str, selector:Tag) -> None:
    output_file_path = 'screenshot.png'
    browser = await launch()
    page = await browser.newPage()

    await page.setContent(str(html_content))
    chord_div = await page.querySelector(selector)
    if chord_div:
        await chord_div.screenshot({'path': output_file_path})


def extract_chords(article_div: Tag) -> list[str]:
    chord_spans = article_div.find_all('span', attrs={'data-name': True})
    chords_set = {span['data-name'] for span in chord_spans}
    return [chord for chord in chords_set]

def extract_lyrics_and_chords(article_div:Tag) -> str:
    song = article_div.find('pre', class_="tK8GG Ty_RP")
    song = article_div.get_text()
    song = re.sub(r'\n+','<br>', song)
    song = song.replace('\'','').replace('|',"")
    return "<pre>" + song + "</pre>"

def get_song_data(html, song) -> dict:
        article_div = BeautifulSoup(html, 'html.parser').find("article", class_="o2tA_ JJ8_m")
        content_text = extract_lyrics_and_chords(article_div)
        #pdf_b64 = extract_pdf_b64(article_div)
        metadata= extract_meta_data(article_div.find('div', class_='P5g5A _PZAs'))
        chords=extract_chords(article_div)
        song_data =  {
            "song": song.__dict__,
            "metadata": metadata.__dict__,
            "chords": ", ".join(chords),
            "content":content_text
        }
        song_data['html'] = build_page_from_template(song_data)
        return song_data
async def fetch_song_content(song):
    try:
        return await fetch_content(song.url, 'div.BDmSP')
    except:
        print(f'skipping song: {song.song}')
        return 

def read_existing_song_data():
    try:
        with open('data/song_content.json', 'r') as json_file:
            return json.load(json_file)
    except:
        return []
    
def dump_song_data(song_content_dicts) -> None:
    with open('data/song_content.json', 'w') as json_file:
        json.dump(song_content_dicts, json_file, indent=4)

async def get_song_content(songs: list[Song_Data]) -> None:
    song_content_dicts = []
    for song in tqdm(songs, desc=f"extracting song content"):
        ## song is already in file
        #if song.song in [sng['song']['song'] for sng in song_content_dicts]:
        #    print(f'{song.song} already in file, skipping')
        #    continue
        ## song is not yet in file
        #else:
        #song_content_dicts = read_existing_song_data()
        print(f'fetching song content for {song.song}')
        try:
            html = await fetch_song_content(song)
            if html:
                song_data = get_song_data(html, song)
                song_content_dicts.append(song_data)
                #dump_song_data(song_content_dicts)
        except:
            continue
    breakpoint()
    dump_song_data(song_content_dicts)


# Main function to scrape and compile for all decades
async def main():
    #await get_all_songs()
    songs = [Song_Data(**song) for song in json.loads(Path('data/songs.json').read_text())][:3]
    await get_song_content(songs)
    
if __name__ == "__main__":
    asyncio.run(main())