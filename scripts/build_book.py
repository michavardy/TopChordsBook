import json
from pathlib import Path
import pdfkit
from PyPDF2 import PdfMerger

song_contents = json.loads(Path('data/song_content.json').read_text())

# Temporary directory to store the PDF files
output_dir = Path('data/output_pdfs_temp')
output_dir.mkdir(exist_ok=True)
merged_pdf_path = 'data/TopChordsBook.pdf'

def write_pdf_files() -> list:
    global output_dir
    pdf_files = []
    for song_index, song in enumerate(song_contents):
        html = song['html'].replace("\\","")
        breakpoint()
        pdf_filename = output_dir / f'page_{song_index + 1}.pdf'
        pdfkit.from_string(html, str(pdf_filename), configuration=pdfkit.configuration(wkhtmltopdf="scripts/wkhtmltopdf.exe"))
        pdf_files.append(pdf_filename)
    return pdf_files

def merge_pdfs(pdf_files: list) -> None:
    global merged_pdf_path
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(str(pdf_file))
    merger.write(merged_pdf_path)
    merger.close()

def main():
    pdf_files = write_pdf_files()
    merge_pdfs(pdf_files)


if __name__ == "__main__":
    main()