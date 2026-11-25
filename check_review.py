"""Check independent calculations behind repaired reviewer keys."""
import itertools
import json
import sqlite3
from pathlib import Path

questions=json.loads((Path(__file__).parent/'questions.json').read_text(encoding='utf-8'))
by_id={q['id']:q for q in questions}
assert len(questions)==242 and len(by_id)==242
assert not any(q['reviewStatus']=='source' for q in questions)
assert all(q['answerIndex'] is None for q in questions if q['reviewStatus']=='unresolved')
for q in questions:
    if q['answerIndex'] is not None:
        assert q['choices'][q['answerIndex']].strip(),q['id']
    assert 'sourceAnswerIndex' in q

# The restored pairwise table must cover every pair, not merely agree with a source letter.
rows=[row.split('/') for row in by_id[8]['choices'][by_id[8]['answerIndex']].split('; ')]
values=[{'On','Off'},{'Play','Stop'},{'Up','Down'}]
for a,b in itertools.combinations(range(3),2):
    assert {(row[a],row[b]) for row in rows}==set(itertools.product(values[a],values[b]))
assert len(rows)==4

s='Topcit_2020_Software_Topcit'
assert (s.count('Topcit'),s.find('Topcit',2),s.rindex('2020'),s.startswith('Topcit'))==(2,21,7,True)
assert by_id[39]['answerIndex']==3

con=sqlite3.connect(':memory:')
con.execute('CREATE TABLE Project(Department TEXT, Project TEXT, NoOfStudents INT, NoOfReports INT)')
con.executemany('INSERT INTO Project VALUES(?,?,?,?)',[
 ('Computer Science','Drone',10,10),('Business Administration','Data Mining',20,20),
 ('Security','Blockchain',5,8),('Statistics','Drone',5,10),
 ('Computer Science','Data Mining',15,20),('Security','Machine Learning',5,10),
 ('Computer Science','Machine Learning',20,20),('Statistics','Data Mining',15,15)])
result=dict(con.execute(by_id[75]['choices'][by_id[75]['answerIndex']]))
assert result=={'Business Administration':20,'Computer Science':50,'Statistics':15}

relation={('s1','p1'),('s1','p2'),('s1','p3'),('s1','p4'),('s2','p1'),('s2','p2'),('s3','p2'),('s4','p2'),('s4','p4')}
division={s for s,_ in relation if all((s,p) in relation for p in {'p1','p2','p4'})}
assert division=={'s1'} and by_id[85]['answerIndex']==0
assert (2**(28-24),2**(32-28)-2)==(16,14) and by_id[113]['answerIndex']==2
assert (8+4*10+18)/6==11 and by_id[230]['answerIndex']==1
print('Verified pairwise coverage, Python outputs, SQL execution, relational division, subnet arithmetic, and PERT arithmetic.')
