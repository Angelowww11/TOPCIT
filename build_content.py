"""Extract color-keyed TOPCIT review questions and source illustrations from the supplied PDF."""
import collections, json, re, unicodedata
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'C:\TOPCIT\drive-download-20261118T161940Z-1-001\1. TOPCIT Reviewer - Software.pdf')
DOC=pymupdf.open(SOURCE)
RANGES=[(0,20,'Software development'),(20,35,'Understanding data'),(35,48,'System architecture'),(48,57,'Information security'),(57,74,'IT business and ethics'),(74,88,'Project management & communication')]
records=[];warnings=[]
for start,end,domain in RANGES:
    current=None
    for page_index in range(start,min(end,len(DOC))):
        page=DOC[page_index]
        lines=[]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                raw=''.join(s['text'] for s in line['spans']).strip()
                if not raw:continue
                lines.append({'x':line['bbox'][0],'y':line['bbox'][1],'text':raw,'red':any(s['color'] in (0xff0000,0xe60000) for s in line['spans']),'page':page_index})
        lines.sort(key=lambda l:(round(l['y'],1),l['x']))
        for i,line in enumerate(lines):
            raw=line['text'].strip()
            if raw.startswith('TOPCIT') and len(raw)<85:continue
            number=re.match(r'^(\d{1,3})\.\s*(.*)$',raw)
            # Page numbers and list numbers use different indents. Question starts
            # have a left gutter and are followed by question text.
            if number and line['x']<70 and int(number[1])<=90 and (number[2] or (i+1<len(lines) and lines[i+1]['y']-line['y']<3)):
                if current:records.append(current)
                current={'domain':domain,'number':int(number[1]),'page':page_index+1,'prompt':[],'choices':[],'answerIndex':None,'sourcePages':{page_index+1},'_startY':line['y'],'_lastPage':page_index}
                if number[2]:current['prompt'].append(number[2])
                continue
            if not current:continue
            current['sourcePages'].add(page_index+1)
            choice=re.match(r'^([a-d])\.\s*(.*)$',raw,re.I)
            if choice and line['x']<95:
                current['choices'].append({'letter':choice[1].lower(),'text':choice[2].strip(),'red':line['red'],'page':page_index+1,'y':line['y']})
                if line['red']:current['answerIndex']=len(current['choices'])-1
                continue
            # Attach continuation text to the last choice only when it is
            # positioned past the choice text indent; otherwise it is a prompt.
            if current['choices'] and line['x']>=70 and raw not in ('�','•'):
                current['choices'][-1]['text']+=' '+raw
                if line['red']:
                    current['choices'][-1]['red']=True
                    current['answerIndex']=len(current['choices'])-1
            elif not current['choices']:
                current['prompt'].append(raw)
        if current:current['_lastPage']=page_index
    if current:records.append(current)

def clean(s):return re.sub(r'\s+',' ',s.replace('�','').strip()).strip()
out=[];seen=set();image_dir=ROOT/'assets'/'source';image_dir.mkdir(parents=True,exist_ok=True)
for r in records:
    prompt=clean(' '.join(r['prompt']))
    choices=[clean(c['text']) for c in r['choices']]
    if r['domain']=='Information security' and r['number']==24 and len(choices)==8:
        r['choices']=r['choices'][:4];choices=choices[:4]
    if r['domain']=='IT business and ethics' and r['number']==10 and len(choices)==5:
        r['choices']=r['choices'][-4:];choices=choices[-4:]
        r['answerIndex']=next((i for i,c in enumerate(r['choices']) if c['red']),None)
    if not prompt or len(choices)!=4:
        warnings.append({'domain':r['domain'],'number':r['number'],'page':r['page'],'reason':'incomplete question or choices','choiceCount':len(choices)})
        continue
    key=(r['domain'],r['number'],prompt,tuple(choices))
    if key in seen:continue
    seen.add(key)
    answer=r['answerIndex']
    if answer is None or answer>=4:
        warnings.append({'domain':r['domain'],'number':r['number'],'page':r['page'],'reason':'answer color not found'})
    # Question prompt areas often include diagrams not present in extracted text.
    # Preserve the prompt area of the source page without showing colored answers.
    exhibit=None
    p=DOC[r['page']-1]
    first_choice=next((c for c in r['choices'] if c['page']==r['page']),None)
    if first_choice and first_choice['y']-r['_startY']>95:
        clip=pymupdf.Rect(35,r['_startY']-3,p.rect.width-25,first_choice['y']-4)
        if clip.height>40:
            filename=f"{r['domain'].split()[0].lower()}-{r['number']:02d}-p{r['page']}.webp"
            pix=p.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),clip=clip,alpha=False)
            from PIL import Image
            import io
            Image.open(io.BytesIO(pix.tobytes('png'))).save(image_dir/filename,'WEBP',quality=78,method=4)
            exhibit='assets/source/'+filename
    out.append({'id':len(out)+1,'domain':r['domain'],'sourceNumber':r['number'],'sourcePage':r['page'],'question':prompt,'choices':choices,'answerIndex':answer,'exhibit':exhibit})
# The security review has an unnumbered XSS item on page 55, immediately
# before its numbered cryptography question. It has no red source key.
out.append({'id':len(out)+1,'domain':'Information security','sourceNumber':'unnumbered','sourcePage':55,
 'question':'What is the type of security weakness described below? Malicious scripts are inserted into a web page and executed by a user’s browser; unverified external input can expose browser cookies.',
 'choices':['Web shell','SQL injection','Cross-site script','Memory Buffer Overflow'],'answerIndex':None,'exhibit':None})
# A visual/text review found some red marks in the supplied answer key that
# conflict with the actual question. Keep the original mark and a clear note.
corrections={
  2:(None,'Two choices repeat the same service-isolation benefit, and the other choices also describe plausible benefits of microservices. This NOT question has no defensible single answer.'),
  6:(2,'The source marks a valid Java lambda as incorrect. The brace-wrapped parameter list and bare return in choice C are not valid Java lambda syntax.'),
  35:(None,'The last answer choice lost the UML stereotype text during PDF extraction and appears only as two empty angle-bracket pairs. It cannot be scored accurately from the available choices.'),
  128:(1,'Certification improves assurance but cannot guarantee that an organization will never suffer an information security incident. The source marks a five-year validity claim that is inconsistent with the reviewer question.'),
  134:(2,'SSL/TLS secures application traffic over the transport layer; it does not run in the OSI network layer. HTTPS is HTTP carried over TLS, so the marked HTTPS description is not the incorrect one here.'),
  135:(0,'A compromised hypervisor can affect multiple hosted operating systems. That is a virtualization vulnerability, not specifically an insecure API.'),
  176:(2,'An NFT is non-fungible: tokens of the same collection are not necessarily interchangeable or equal in value. The red source mark points to the definition of a non-fungible token.'),
  181:(None,'A data lake holds varied source data for broad future use. The marked single repository description is plausible, while more than one other choice describes task-specific or already transformed data. This NOT item needs a clearer key.'),
  186:(1,'Critical Chain Method is a project scheduling approach. BPR, Process Innovation, and TQM are business process improvement approaches, so the source mark on Process Innovation is inconsistent.'),
  217:(2,'Both examples name the outcome the projects aim to achieve: product lifecycle management and faster integrated decisions. They illustrate defined objectives, not the gradual refinement of a plan.'),
  204:(0,'The source figure plots expectations against time through a peak and trough. That is Gartner’s Hype Cycle, not the four-quadrant Magic Quadrant.'),
  222:(2,'This is a request for information: it gathers supplier capabilities before a detailed proposal or project order. The source marked RFP.'),
  224:(None,'The description mixes distribution, correlation, and outlier language. The available choices do not contain a clear single chart that satisfies every part; the red Bar Chart mark is unsupported. Study only.'),
  231:(1,'Using the usual PERT three-point estimate, (optimistic + 4 × most likely + pessimistic) ÷ 6 = (8 + 40 + 18) ÷ 6 = 11 million. The source marks 10 million.'),
  236:(1,'Classifying problems, finding causes, and prioritizing causes are activities in the Analyze underlying causes phase, not implementation and feedback.')
}
for q in out:
    if q['id'] in corrections:
        q['sourceAnswerIndex']=q['answerIndex']
        q['answerIndex'],q['reviewNote']=corrections[q['id']]
# The source repeats the identical NFT item on pages 64 and 65. Diagram-based
# questions remain distinct even when OCR text and choices are identical.
unique=[];duplicate_keys=set()
for q in out:
    key=(q['domain'],q['question'],tuple(q['choices']),q['exhibit'] is None)
    if q['exhibit'] is None and key in duplicate_keys:continue
    duplicate_keys.add(key)
    unique.append(q)
out=unique
for i,q in enumerate(out,1):q['id']=i
(ROOT/'answer-audit.json').write_text(json.dumps({'corrections':[{'id':q['id'],'page':q['sourcePage'],'original':q['sourceAnswerIndex'],'reviewed':q['answerIndex'],'reason':q['reviewNote']} for q in out if 'reviewNote' in q], 'duplicateRemoved':'Repeated NFT item on page 65; first copy on page 64 retained'},ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'questions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'import-audit.json').write_text(json.dumps({'source':SOURCE.name,'pages':len(DOC),'candidateQuestions':len(records),'imported':len(out),'keyed':sum(q['answerIndex'] is not None for q in out),'warnings':warnings,'domains':dict(collections.Counter(q['domain'] for q in out))},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'candidates':len(records),'imported':len(out),'keyed':sum(q['answerIndex'] is not None for q in out),'warnings':len(warnings),'domains':dict(collections.Counter(q['domain'] for q in out))},indent=2))
