"""Check source completeness and execute the supplementary SQL/code examples."""
import hashlib
import json
import re
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from difflib import SequenceMatcher
from PIL import Image
from build_written import SOURCE, NS, R, paragraph_text

ROOT=Path(__file__).resolve().parent
audit=json.loads((ROOT/'content-audit.json').read_text(encoding='utf-8'))
c=audit['counts']
assert c==dict(questions=242,pdfPages=88,sourceImages=164,includedImages=164,wordImages=161,unmatchedWordImages=0,missingSourceImages=0,nativePromptMismatches=0,nativeChoiceMismatches=0),c
for item in audit['questions']:
    assert item['nativePromptMatches'] and item['nativeChoicesMatch']
    assert item['includedImageCount']==item['sourceImageCount']
    if item.get('image'):assert (ROOT/item['image']).is_file()
w=json.loads((ROOT/'written-exercises.json').read_text(encoding='utf-8'))
assert w['counts']==dict(exercises=45,originalImages=28,sourceParagraphs=157)
assert [x['id'] for x in w['exercises']]==list(range(1,46))
assert [x['id'] for x in w['exercises'] if x['model'].get('sourceIssue')]==[3,30,31]
assert len({i['src'] for i in w['originalImages']})==28
assert len([e for e in w['exercises'] if e['isMultipleChoice']])==20
with zipfile.ZipFile(SOURCE/'TOPCIT_ (2).docx') as archive:
    rel={n.get('Id'):'word/'+n.get('Target') for n in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
    body=ET.fromstring(archive.read('word/document.xml')).findall('.//w:body/w:p',NS)
    source_paragraphs={i for i,p in enumerate(body) if paragraph_text(p) or p.findall('.//a:blip',NS)}
    assert source_paragraphs=={i for e in w['exercises'] for i in e['sourceParagraphs']}
    assert sum(len(e['sourceParagraphs']) for e in w['exercises'])==len(source_paragraphs)
    for item in w['originalImages']:
        original=archive.read(rel[item['originalRelationship']])
        assert hashlib.sha256(original).hexdigest()==item['sha256']
        assert (ROOT/item['src']).read_bytes()==original
        assert Image.open(ROOT/item['src']).size==(item['width'],item['height'])
    for e in w['exercises']:
        assert e['prompt'] and e['model']['answer'] and e['model']['reason']
        original=[paragraph_text(body[i]) for i in e['sourceParagraphs'] if paragraph_text(body[i])]
        assert sorted(original)==sorted(e['prompt']+e['responses']) or not any(x not in e['prompt']+e['responses'] for x in original)
        for item in e['images']+e.get('sharedImages',[])+([e['companion']] if e.get('companion') else []):assert (ROOT/item['src']).exists()
        if e['isMultipleChoice']:
            assert len(e['givenChoices'])==4
            answer=e['givenChoices'][e['modelChoice']]
            normalize=lambda s:re.sub('[^a-z0-9]','',s.lower())
            if e['id']==39:assert answer.replace(' ','')=='<>,<>' and e['modelChoice']==3
            else:assert SequenceMatcher(None,normalize(answer),normalize(e['model']['answer'])).ratio()>.6,(e['id'],answer,e['model']['answer'])
            assert e['model']['originalMarkedAnswer']==e['givenChoices'][e['sourceKeyIndex']]

e={x['id']:x for x in w['exercises']}
db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
db.executescript('CREATE TABLE Department(Department_No INT,Department_Name TEXT); CREATE TABLE Employee(Employee_No INT,Department_No INT,Entry_Date TEXT);')
db.executemany('INSERT INTO Department VALUES(?,?)',[(101,'Sales'),(102,'Planning'),(103,'HR')])
db.executemany('INSERT INTO Employee VALUES(?,?,?)',[(1,101,'2017-01-01'),(2,101,'2018-01-01'),(3,102,'2018-12-31'),(4,102,'2019-07-01'),(5,103,'2019-01-01')])
assert list(db.execute(e[6]['model']['answer']))==[(101,2),(102,2)]
query='SELECT dept.Department_No FROM Department dept WHERE '+e[5]['model']['answer']+" (SELECT * FROM Employee emp WHERE emp.Entry_Date >= '2019-01-01' AND dept.Department_No=emp.Department_No) ORDER BY 1"
assert list(db.execute(query))==[(102,),(103,)]
db.executescript('CREATE TABLE Customer(Customer_No INT); CREATE TABLE "Order"(Order_No INT,Customer_No INT); INSERT INTO Customer VALUES(1),(2); INSERT INTO "Order" VALUES(9,1),(10,3);')
assert len(list(db.execute(e[2]['model']['answer'])))==3
db.executescript('CREATE TABLE Student(Student_No INT PRIMARY KEY); CREATE TABLE Course_Application_Form(Student_No INT, '+e[29]['model']['answer'].split('\n\n')[1]+'); INSERT INTO Student VALUES(1),(2); INSERT INTO Course_Application_Form VALUES(1),(2); DELETE FROM Student WHERE Student_No=1;')
assert list(db.execute('SELECT * FROM Course_Application_Form'))==[(2,)]
a,b=2,4;a,b=b,a
assert (a,b)==(4,2) and e[42]['model']['answer']=='a = 4, b = 2'
assert all((ROOT/path).exists() for path in ['written.js','content-audit.html'])
print('PASS: 242 source records; 164 pictures; all 157 written paragraphs and 28 exact original images; 45 exercises; SQL results, cascade behavior, and Python output.')
