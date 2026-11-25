"""Check every current question against source text, image positions, and Word media."""
import bisect
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from html import escape

import pymupdf
from PIL import Image

ROOT=Path(__file__).resolve().parent
SOURCES=Path('C:/TOPCIT/drive-download-20261118T161940Z-1-001')
PDF=SOURCES/'1. TOPCIT Reviewer - Software.pdf'


def normalize(text):
    return re.sub(r'[^a-z0-9]','',text.lower())


def lines(page):
    result=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            text=''.join(s['text'] for s in line['spans']).strip()
            if text:result.append({'text':text,'x':line['bbox'][0],'y':line['bbox'][1]})
    return sorted(result,key=lambda x:(round(x['y'],1),x['x']))


def fingerprint(data):
    image=Image.open(io.BytesIO(data)).convert('L')
    ratio=image.width/image.height
    values=list(image.resize((9,8)).get_flattened_data())
    return ratio,sum((values[y*9+x]>values[y*9+x+1])<<(y*8+x) for y in range(8) for x in range(8))


def audit():
    questions=json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
    repairs={r['questionId']:r for r in json.loads((ROOT/'source-figure-repairs.json').read_text(encoding='utf-8'))}
    doc=pymupdf.open(PDF)
    page_lines={n:lines(page) for n,page in enumerate(doc,1)}
    starts=[]
    for q in questions:
        candidates=[line for line in page_lines[q['sourcePage']] if
                    (line['x']<70 and re.match(rf'^{q["sourceNumber"]}\.(?:\s|$)',line['text']))
                    or (q['id']==242 and line['text'].startswith('What is the type of security weakness'))]
        assert len(candidates)==1,(q['id'],candidates)
        starts.append(((q['sourcePage'],candidates[0]['y']),q))
    starts.sort(key=lambda item:item[0]);positions=[x[0] for x in starts]
    images={q['id']:[] for q in questions};backgrounds=[];pdf_fingerprints=[]
    for pn,page in enumerate(doc,1):
        for image in page.get_images(full=True):
            data=doc.extract_image(image[0])['image']
            for rect in page.get_image_rects(image[0]):
                if abs(rect.width-page.rect.width)<1 and abs(rect.height-page.rect.height)<1:
                    backgrounds.append({'page':pn,'reason':'Full-page annotation/background layer; question text and individual images are checked separately.'});continue
                owner=starts[bisect.bisect_right(positions,(pn,rect.y0))-1][1]
                images[owner['id']].append({'page':pn,'rect':list(rect),'xref':image[0]})
                pdf_fingerprints.append(fingerprint(data))
    raw_boundaries=sorted(set(positions+[(pn,line['y']) for pn,entries in page_lines.items() for line in entries if line['x']<70 and re.match(r'^\d{1,3}\.(?:\s|$)',line['text'])]))
    findings=[];missing=[];text_issues=[];choice_issues=[]
    for i,(start,q) in enumerate(starts):
        at=bisect.bisect_right(raw_boundaries,start)
        end=raw_boundaries[at] if at<len(raw_boundaries) else (len(doc)+1,0)
        # The excluded repeated NFT question has no images. It remains documented as a duplicate.
        region=[(pn,line) for pn in range(start[0],min(end[0],len(doc))+1) for line in page_lines[pn]
                if start<=(pn,line['y'])<end]
        choices=[(pn,line) for pn,line in region if line['x']<95 and re.match(r'^[a-d]\.\s*$',line['text'],re.I)]
        first=choices[0] if choices else None
        prompt=[line['text'] for pn,line in region if first is None or (pn,line['y'])<(first[0],first[1]['y'])]
        if prompt:prompt[0]=re.sub(r'^\d+\.\s*','',prompt[0])
        raw=re.sub(r'\s*-\s*[A-D]\s*$','',' '.join(prompt))
        actual=' '.join([q['question'],*q.get('description',[])])
        native_match=normalize(raw)==normalize(actual)
        if not native_match:text_issues.append({'id':q['id'],'source':raw,'website':actual})
        native_choices=[]
        for pn,line in region:
            if line['x']<95 and re.match(r'^[a-d]\.(?:\s+|$)',line['text'],re.I):native_choices.append(re.sub(r'^[a-d]\.\s*','',line['text'],flags=re.I))
            elif native_choices and not line['text'].startswith('TOPCIT') and not(line['y']>750 and line['text'].isdigit()):native_choices[-1]+=' '+line['text']
        expected=q.get('sourceChoices',q['choices'])
        choices_match=len(native_choices)==len(expected) and all(normalize(a)==normalize(b) for a,b in zip(native_choices,expected))
        if not choices_match:choice_issues.append({'id':q['id'],'source':native_choices,'website':expected})
        coverage=[]
        for item in images[q['id']]:
            covered=False
            if q['id'] in repairs:
                covered=any(r['page']==item['page'] and max(abs(a-b) for a,b in zip(r['rect'],item['rect']))<.03
                            for r in repairs[q['id']]['regions'])
            elif q.get('exhibit') and first and first[0]==start[0] and item['page']==start[0]:
                clip=pymupdf.Rect(35,start[1]-3,doc[start[0]-1].rect.width-25,first[1]['y']-4)
                rect=pymupdf.Rect(item['rect']);intersection=clip & rect
                covered=intersection.get_area()/rect.get_area()>.995
            if not covered:missing.append({'questionId':q['id'],**item})
            coverage.append(covered)
        findings.append({'id':q['id'],'question':q['question'],'sourcePages':q.get('exhibitPages',[q['sourcePage']]),
                         'sourceImageCount':len(coverage),'includedImageCount':sum(coverage),'nativePromptMatches':native_match,'nativeChoicesMatch':choices_match,
                         'image':q.get('exhibit'),'restored':q['id'] in repairs})
    word_count=0;word_missing=[]
    for file in sorted((SOURCES/'TOPCIT MATERIALS II').glob('*.docx')):
        with zipfile.ZipFile(file) as archive:
            for name in archive.namelist():
                if not name.startswith('word/media/'):continue
                word_count+=1;ratio,fp=fingerprint(archive.read(name))
                distance=min(((fp^other).bit_count() for r,other in pdf_fingerprints if abs(r-ratio)/ratio<.12),default=999)
                if distance>10:word_missing.append({'file':file.name,'image':name,'distance':distance})
    output={'checkedOn':'2026-11-25','scope':'All 242 current questions, all 88 main reviewer pages, and the images from the six matching Word reviewers. Supplementary written exercises have a separate source inventory.',
            'source':PDF.name,'sourceSha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
            'counts':{'questions':len(questions),'pdfPages':len(doc),'sourceImages':len(pdf_fingerprints),'includedImages':sum(x['includedImageCount'] for x in findings),
                      'wordImages':word_count,'unmatchedWordImages':len(word_missing),'missingSourceImages':len(missing),'nativePromptMismatches':len(text_issues),'nativeChoiceMismatches':len(choice_issues)},
            'excludedLayers':backgrounds,'duplicateNote':'The repeated NFT question on PDF page 65 is represented by the matching retained item from page 64.',
            'originalSourceIssues':[{'id':35,'note':'The reviewer prints empty stereotype brackets in one UML choice.'},{'id':42,'note':'The reviewer provides a graph description, not a drawn graph.'},{'id':59,'note':'The source shows tables but omits the exact property the question asks you to select.'},{'id':131,'note':'The named improvement plan is absent from the supplied source example.'}],
            'questions':sorted(findings,key=lambda x:x['id']),'missingImages':missing,'textDifferences':text_issues,'choiceDifferences':choice_issues,'unmatchedWordImages':word_missing}
    (ROOT/'content-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output['counts']))
    if missing:print('MISSING IMAGES',json.dumps(missing))
    if text_issues:print('TEXT DIFFERENCES',json.dumps(text_issues,ensure_ascii=False))
    if choice_issues:print('CHOICE DIFFERENCES',json.dumps(choice_issues,ensure_ascii=False))
    return output


if __name__=='__main__':
    audit()
