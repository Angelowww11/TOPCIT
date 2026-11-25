"""Import all 45 supplementary exercises and all 28 original images without guessing choices."""
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf
from PIL import Image
from written_notes import LINKED, COMPANIONS, MC_IDS, OVERRIDES, SOURCE_MARKED_MC

ROOT=Path(__file__).resolve().parent
SOURCE=Path('C:/TOPCIT/drive-download-20261118T161940Z-1-001')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
W='{'+NS['w']+'}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def paragraph_text(paragraph):
    return ''.join(node.text or '' if node.tag==W+'t' else '\n' if node.tag==W+'br' else '\t' if node.tag==W+'tab' else '' for node in paragraph.iter()).strip()


def image_hash(data):
    image=Image.open(io.BytesIO(data)).convert('L');v=list(image.resize((9,8)).get_flattened_data())
    return image.width/image.height,sum((v[y*9+x]>v[y*9+x+1])<<(8*y+x) for y in range(8) for x in range(8))


def build():
    main=json.loads((ROOT/'questions.json').read_text(encoding='utf-8'));by_id={q['id']:q for q in main}
    pdf=pymupdf.open(SOURCE/'TOPCIT_Reviewer.pdf');starts={};pdf_images=[]
    for page_num,page in enumerate(pdf,1):
        for match in re.finditer(r'^\s*(\d{1,2})\.\s',page.get_text(),re.M):starts[int(match[1])]=page_num
        for image in page.get_images(full=True):pdf_images.append((page_num,*image_hash(pdf.extract_image(image[0])['image'])))
    assert set(starts)==set(range(1,46))
    target=ROOT/'assets'/'written';target.mkdir(exist_ok=True)
    exercises=[];current=None;phase='prompt';all_paragraphs=[];image_inventory=[]
    with zipfile.ZipFile(SOURCE/'TOPCIT_ (2).docx') as archive:
        relationships={node.get('Id'):'word/'+node.get('Target') for node in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
        document=ET.fromstring(archive.read('word/document.xml'))
        for paragraph_num,paragraph in enumerate(document.findall('.//w:body/w:p',NS)):
            text=paragraph_text(paragraph)
            level=paragraph.find('w:pPr/w:numPr/w:ilvl',NS)
            level=level.get(W+'val') if level is not None else None
            drawings=paragraph.findall('.//a:blip',NS)
            if level=='0':
                current={'id':len(exercises)+1,'prompt':[],'responses':[],'images':[],'sourceParagraphs':[],'sourcePages':[]}
                exercises.append(current);phase='prompt'
            if not current or not(text or drawings):continue
            current['sourceParagraphs'].append(paragraph_num);all_paragraphs.append(paragraph_num)
            if level=='1':phase='response'
            elif level is None and re.match(r'(?i)\(?sub question|explain the reason|describe three',text):phase='prompt'
            if text:current['prompt' if phase=='prompt' else 'responses'].append(text)
            for drawing in drawings:
                rid=drawing.get(R+'embed');original=relationships[rid];data=archive.read(original)
                filename=f'original-{rid}{Path(original).suffix.lower()}';(target/filename).write_bytes(data)
                ratio,fp=image_hash(data);matches=[((fp^other).bit_count(),page) for page,r,other in pdf_images if abs(r-ratio)/ratio<.12]
                distance,page=min(matches)
                assert distance<=10,(rid,distance)
                width,height=Image.open(io.BytesIO(data)).size
                item={'src':'assets/written/'+filename,'width':width,'height':height,'source':'TOPCIT_ (2).docx','sourcePage':page,'originalRelationship':rid,'sha256':hashlib.sha256(data).hexdigest()}
                current['images'].append(item);image_inventory.append(item)
    assert len(exercises)==45 and len(image_inventory)==28
    for exercise in exercises:
        number=exercise['id'];exercise['sourcePages']=sorted({starts[number],*(image['sourcePage'] for image in exercise['images'])})
        exercise['sourceFile']='TOPCIT_Reviewer.pdf / TOPCIT_ (2).docx'
        exercise['givenChoices']=exercise['responses'][:] if number in MC_IDS else []
        if number in MC_IDS:
            exercise['modelChoice']=by_id[LINKED[number]]['answerIndex']
            exercise['sourceKeyIndex']=SOURCE_MARKED_MC[number]
        exercise['isMultipleChoice']=number in MC_IDS
        if not exercise['prompt']:
            exercise['prompt']=[by_id[LINKED[number]]['question'] if number in LINKED else 'Refer to the functional specification and fill in blanks (a), (b), and (c) with HTML statements.']
            exercise['promptNote']='The heading is restored from the matching main question or transcribed from the source image.'
        exercise['title']=exercise['prompt'][0].split('\n')[0]
        if number in LINKED:
            question=by_id[LINKED[number]]
            exercise['relatedQuestion']=question['id']
            exercise['model']={'answer':question['choices'][question['answerIndex']], 'basis':'reviewer' if question['reviewStatus']=='source' else 'checked',
                               'reason':question.get('reviewNote','This is the reviewed answer to the matching main-reviewer question.'),'references':question.get('reviewReferences',[])}
        if number in OVERRIDES:exercise['model']=OVERRIDES[number]
        assert 'model' in exercise,number
        if number in MC_IDS:
            exercise['model']['originalMarkedAnswer']=exercise['givenChoices'][exercise['sourceKeyIndex']]
            if exercise['sourceKeyIndex']!=exercise['modelChoice']:
                exercise['model']['reason']='The supplementary reviewer marks a different response. '+exercise['model']['reason']
                if exercise['model']['basis']=='checked':exercise['model']['basis']='corrected'
        if number in COMPANIONS:
            question=by_id[COMPANIONS[number]]
            width,height=Image.open(ROOT/question['exhibit']).size
            exercise['companion']={'src':question['exhibit'],'width':width,'height':height,'questionId':question['id'],'sourcePages':question.get('exhibitPages',[question['sourcePage']]),'caption':'Additional matching figure from the main reviewer'}
        if number==6:
            exercise['sharedImages']=[{**exercises[4]['images'][1],'caption':'Shared Employee table from exercise 5'}]
        if number in [14,20,24,28,41,45]:
            exercise['imageNote']='The original photograph is already cropped in the supplied files. Every original image byte is retained here.'
        exercise['model']['sourceResponses']=exercise['responses']
    output={'source':'TOPCIT_Reviewer.pdf and TOPCIT_ (2).docx','sourcePages':17,'counts':{'exercises':45,'originalImages':28,'sourceParagraphs':len(all_paragraphs)},'exercises':exercises,'originalImages':image_inventory}
    (ROOT/'written-exercises.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output['counts']))


if __name__=='__main__':build()
