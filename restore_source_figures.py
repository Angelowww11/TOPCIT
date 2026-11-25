"""Restore exact embedded examples that continue across PDF page boundaries.

Run this after source-figure-repairs.json changes. Original image bytes are used,
including image content that extends beyond a PDF page edge. No answers are added.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path('C:/TOPCIT/drive-download-20261118T161940Z-1-001/1. TOPCIT Reviewer - Software.pdf')


def load_repairs():
    return json.loads((ROOT/'source-figure-repairs.json').read_text(encoding='utf-8'))


def apply_repairs(questions):
    by_id = {question['id']: question for question in questions}
    for repair in load_repairs():
        question = by_id[repair['questionId']]
        question['exhibit'] = repair['image']
        question['exhibitPages'] = sorted({question['sourcePage'], *(region['page'] for region in repair['regions'])})
        question['exhibitNote'] = 'Original embedded source examples restored across the PDF page boundary.'


def restore():
    import io
    import pymupdf
    from PIL import Image
    source = pymupdf.open(SOURCE)
    for repair in load_repairs():
        regions = repair['regions']
        width = max(region['rect'][2]-region['rect'][0] for region in regions)
        height = sum(region['rect'][3]-region['rect'][1] for region in regions)
        assembled = pymupdf.open()
        page = assembled.new_page(width=width+20, height=height+16*(len(regions)+1))
        top = 16
        for region in regions:
            source_page = source[region['page']-1]
            target = pymupdf.Rect(region['rect'])
            matches = [image[0] for image in source_page.get_images(full=True)
                       if any(max(abs(rect[i]-target[i]) for i in range(4)) < .02
                              for rect in source_page.get_image_rects(image[0]))]
            assert matches, (repair['questionId'], region)
            image = source.extract_image(matches[0])['image']
            page.insert_image(pymupdf.Rect(10, top, 10+target.width, top+target.height), stream=image)
            top += target.height+16
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
        Image.open(io.BytesIO(pixmap.tobytes('png'))).save(ROOT/repair['image'], 'WEBP', quality=90, method=5)
        assembled.close()
    print(f'Restored original source examples for {len(load_repairs())} questions.')


if __name__ == '__main__':
    restore()
