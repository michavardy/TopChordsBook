

# Top Chords Book Scraper

```
  _______           _____ _                   _ ____              _    
 |__   __|         / ____| |                 | |  _ \            | |   
    | | ___  _ __ | |    | |__   ___  _ __ __| | |_) | ___   ___ | | __
    | |/ _ \| '_ \| |    | '_ \ / _ \| '__/ _` |  _ < / _ \ / _ \| |/ /
    | | (_) | |_) | |____| | | | (_) | | | (_| | |_) | (_) | (_) |   < 
    |_|\___/| .__/ \_____|_| |_|\___/|_|  \__,_|____/ \___/ \___/|_|\_\
            | |                                                        
            |_|                                                        
```

This project is a Python-based web scraper that fetches data on the top 100 songs for each decade from the Ultimate Guitar website and compiles it into PDF format.

## Dependencies
- BeautifulSoup
- pdfkit
- asyncio
- os
- dataclasses
- tqdm
- pyppeteer

## Setup
1. Install dependencies: `pip install beautifulsoup4 pdfkit tqdm pyppeteer`
2. Set the `PYPPETEER_CHROMIUM_REVISION` environment variable to '1263111'.
3. install the Guitar Chord Generator package using pip:

```bash
pip install git+https://github.com/michavardy/ChordDiagramGenerator.git
```

## Usage
1. Run the `scraper.py` script.
2. The script will scrape the top 100 songs for each decade (1970s, 1980s, 1990s, 2000s, 2010s, 2020s) from the Ultimate Guitar website.
3. For each decade, the script will compile the song data into a PDF file named '{decade}s_Top_100_Songs.pdf'.

## Project Structure
- `scraper.py`: Main script containing the scraper logic.
- `Song_Data`: Dataclass representing song data.
- `fetch_content`: Asynchronous function to fetch HTML content from a URL using Pyppeteer.
- `generate_pdf`: Asynchronous function to generate a PDF from HTML content using Pyppeteer.
- `scrape_songs`: Asynchronous function to scrape top songs for a given decade.
- `compile_pdf`: Function to compile song data into a PDF.
- `main`: Main function to scrape and compile songs for all decades.

## CLI
```bash
"C:\Program Files\Inkscape\bin\inkscapecom" --export-filename="output.svg" --export-type="svg" "output.pdf"
C&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Em&nbsp;&nbsp;  this will preserve the spacing
```