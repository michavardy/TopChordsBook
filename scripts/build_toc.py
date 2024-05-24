import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import  Tag, NavigableString
from chord_diagram_generator import generate_chord_svg
from tqdm import tqdm 
PYPPETEER_CHROMIUM_REVISION = '1263111'
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from pyppeteer import launch
import asyncio

Template = 'templates/TOC_template.html'
Data = 'data/songs.json'
max_length = 3400 #px