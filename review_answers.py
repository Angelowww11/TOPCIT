"""Reproducible second-pass audit. Original PDF marks remain separate from study answers."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
questions = json.loads((ROOT / 'questions.json').read_text(encoding='utf-8'))
from restore_source_figures import apply_repairs
apply_repairs(questions)
URL = {
 'java':'https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html',
 'maven':'https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html',
 'mongo':'https://www.mongodb.com/docs/manual/core/transactions/',
 'tcp':'https://www.rfc-editor.org/rfc/rfc5681.html',
 'cidr':'https://www.rfc-editor.org/rfc/rfc4632.html',
 'k8s':'https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/',
 'hdfs':'https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html',
 'keys':'https://csrc.nist.gov/glossary/term/public_key',
 'isms':'https://pipc.go.kr/eng/user/lgp/bnp/certification.do',
 'ethics':'https://www.computer.org/education/code-of-ethics',
 'oauth':'https://openid.net/developers/how-connect-works/',
 'log4j':'https://logging.apache.org/log4j/2.x/security.html',
 'inspect':'https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/'
}
# Each entry follows an individual prompt/choice review. None means no safe single answer.
changes = {
9:(None,'Obfuscation makes code harder to understand and resists reverse engineering. None of these choices states that purpose. The source selects reverse engineering, which is the activity it obstructs.',[]),
27:(None,'Maven deploy copies a package to a remote repository, not the local repository. The compile wording also incorrectly assumes machine code for every project. More than one choice is defective.',['maven']),
60:(None,'The source treats NoSQL as excluding ACID transactions. Modern MongoDB supports multi-document ACID transactions. These blanket properties do not define all NoSQL products.',['mongo']),
66:(None,'CAP concerns the consistency/availability tradeoff during a network partition. Several choices oversimplify the model; no deployment-independent single answer is safe.',[]),
70:(2,'The example specifies record length and a physical index. These are internal storage details, not a user-specific external view.',[]),
71:(None,'Replication can increase storage, so the marked statement is a real tradeoff. Location transparency depends on whether the statement describes users or database administration. The question does not specify that perspective.',[]),
72:(2,'Grouping observations by similarity describes clustering, an unsupervised method. A classification tree learns from labeled categories and is supervised.',[]),
73:(3,'The source asks for recovery to the moment before failure. Archive or transaction logs support point-in-time recovery; incremental backups alone do not guarantee that recovery point.',[]),
76:(None,'Conceptual modeling can define subject areas and create a conceptual ERD. Detailed attributes and identifiers are often logical-model tasks. The choices do not specify a methodology with one unique answer.',[]),
97:(0,'Paging uses fixed-size pages and frames. It can waste space inside a frame, but it does not require contiguous frames and avoids external fragmentation.',[]),
113:(2,'A /24 divided into /28 networks gives 16 subnets and 14 usable host addresses per subnet. The mask is 255.255.255.240. A /27 gives only eight subnets.',['cidr']),
116:(None,'NameNodes manage metadata and DataNodes store blocks; that statement is correct. HDFS restricts updates but permits append and truncate operations. The other broad statements do not provide a defensible unique false answer.',['hdfs']),
117:(3,'The figure removes and replaces old service instances in stages. That is a rolling deployment. Blue-green deployment switches between two complete environments.',['k8s']),
123:(0,'Slow start increases the congestion window for acknowledgments and grows roughly exponentially per round-trip time. Linear growth describes congestion avoidance.',['tcp']),
127:(None,'Restricting write access to /etc/profile to root is valid hardening. The hosts.allow/hosts.deny choice incorrectly calls its entries users rather than hosts or services. The source mark is unsafe.',[]),
129:(0,'The combined information-security and personal-information certification is ISMS-P. PIPL is not the integrated certification described here.',['isms']),
136:(None,'Updating Log4j to a supported fixed release is a valid mitigation. The remaining choices describe real features or impacts of the vulnerability. The source does not supply a clear incorrect statement.',['log4j']),
140:(1,'The source table allows owner read/write, group read, and others read, with no execute permission. These bits are 6, 4, and 4. Use chmod 644 secret.txt.',[]),
143:(1,'Different encryption and decryption keys identify asymmetric, or public-key, encryption. Symmetric encryption uses a shared secret key.',['keys']),
145:(None,'OAuth provides delegated authorization. OpenID Connect adds an authentication layer for social sign-in. The exact authentication answer is absent from the choices.',['oauth']),
148:(2,'A valid digital signature supports integrity and origin authentication. It does not encrypt the message or prove that nobody read it during transmission.',['keys']),
150:(1,'The description uses quantum properties for key distribution. Quantum cryptography is the matching option. The yellow source highlight confirms it.',[]),
151:(3,'The permissions follow job functions and change with assigned roles. That is role-based access control.',[]),
152:(None,'The intended security warning concerns rooted or jailbroken devices. However, blocking every such device is a risk decision, not a universal security requirement. No unconditional answer is assigned.',[]),
153:(1,'A blanket claim that block ciphers are faster than stream ciphers is false. Performance depends on the algorithm, hardware, and mode.',[]),
154:(1,'The source figure signs with the sender private key and verifies with the sender public key. These keys correspond to choice B.',['keys']),
155:(0,'Threat modeling and architecture changes to address threats belong to secure design.',[]),
156:(1,'Passwords need salted, deliberately slow password hashing. Reversible encryption, even repeated, exposes passwords if the decryption key is stolen.',[]),
157:(2,'Source-code security review belongs to implementation. Requirements identification precedes it; dynamic testing and penetration testing usually assess running software.',[]),
171:(3,'In the source figure, a is information-environment analysis, b is business-process analysis, c defines requirements, and d establishes plans. Choice D matches those blanks.',[]),
172:(2,'The detailed system requirements and function-point-ready project scope describe an Information System Master Plan (ISMP). ISP establishes the broader information strategy.',[]),
174:(2,'Professional judgment must retain integrity and independence. Focusing only on stakeholder perspectives is not that principle. The marked requirement for high product standards is a valid ethical duty.',['ethics']),
184:(None,'This question depends on the jurisdiction and version of privacy rules. The source supplies neither a reliable effective date nor enough legal context for a current universal answer.',[]),
200:(0,'The source example shifts sales online, adopts an agile culture, and applies AI, IoT, and cloud across the enterprise. It describes digital transformation, not selling products as services.',[]),
201:(1,'The usual IT balanced-scorecard perspectives are corporate contribution, user orientation, operational excellence, and future orientation. Internal processes map to operational excellence, not a generic information-technology perspective.',[]),
212:(None,'The figure requires internal failure, external failure, and prevention costs, in that order. None of the four options gives that complete combination.',[]),
213:(2,'The source organization chart overlays projects across functional departments. Staff work within both structures, which identifies a matrix organization.',[]),
225:(None,'The purchase-date groups overlap. Other groups also have unclear or overlapping boundaries as written. The marked sales bands alone do not establish one uniquely incorrect classification.',[]),
226:(None,'The first bullet evaluates results (Check); the second decides a corrective action (Act). The combined prompt does not isolate one PDCA phase.',[]),
227:(0,'The statement that verbal content is unimportant misuses the 7/38/55 finding. That finding concerns inconsistent expressions of feelings or attitudes, not all communication.',[]),
234:(None,'An expected value is the anticipated result, so the marked statement is not inherently false. Case names in the figure repeat, but a unique ID distinguishes the cases. The wording does not provide a reliable single false choice.',[]),
240:(0,'A Gantt chart is a schedule representation. Planning packages, work packages, and a code of accounts belong to WBS organization and identification.',[]),
241:(2,'The source lists defect detection, a trained moderator, defined roles, checklists, and formal entry/exit rules. These are inspection characteristics, not an audit.',['inspect']),
242:(2,'Untrusted input that runs malicious script in a visitor browser is cross-site scripting (XSS). The yellow source highlight marks this choice.',[])
}
from remaining_audit import FINDINGS, REFERENCES, CHOICE_REPAIRS
from reviewer_fallbacks import FALLBACK_NOTES, BASE_CAVEATS, CHOICE_REPAIRS as FALLBACK_CHOICES
CHOICE_REPAIRS.update(FALLBACK_CHOICES)
for item_id,(answer,note,ref_names) in FINDINGS.items():
    names=ref_names.split() if ref_names else []
    for name in names: URL[name]=REFERENCES[name]
    changes[item_id]=(answer,note,names)
for item_id,note in BASE_CAVEATS.items():
    changes.setdefault(item_id,(None,note,[]))
# Straightforward text items that can be checked without an unseen diagram or local legal assumptions.
checked = {1,3,4,5,6,7,10,12,13,15,16,19,20,23,25,30,31,42,44,47,53,58,61,62,65,67,79,83,86,89,92,95,96,99,103,104,105,106,107,109,118,121,124,125,126,128,130,132,134,135,139,141,144,149,158,161,163,164,165,166,169,173,175,176,177,179,181,183,185,186,188,190,191,198,199,203,204,205,209,210,211,214,215,216,218,219,220,221,222,230,231,233,235,236,237,238,239}
ledger=[]
for q in questions:
    if q['id']==149:
        if 'Malicious scripts' in q['choices'][3]:
            q.setdefault('importedChoicesBeforeRepair',q['choices'][:])
        q['choices'][3]='Stop unnecessary services applying terminal services, anonymous FTP, SNMP, etc.'
        q['contentRepairNote']='Removed the next unnumbered XSS question that the importer appended to the final Windows-security choice.'
    if q['id']==167:
        if q['choices'][0]!='A.I. business model':
            q.setdefault('importedChoicesBeforeRepair',q['choices'][:])
        q['choices'][0]='A.I. business model'
        q['contentRepairNote']='Restored A.I.; the importer mistook the abbreviation for another answer-letter marker.'
    if q['id']==242:
        q['question']='What is the type of security weakness described below?'
        q['description']=[
            "Malicious scripts are inserted into a web page to be executed by a user's PC.",
            'When an unverified external input is used to create a dynamic web page, it launches malicious behavior with the access privilege of the person browsing the page.',
            'It leads to attacks such as leaks in browser cookies.'
        ]
        q['contentRepairNote']='Restored the complete three-point source description and its insecure-code example from PDF page 55.'
    q.pop('answerBasis',None)
    q.pop('reviewCaveat',None)
    source=q.get('sourceAnswerIndex',q['answerIndex'])
    if q['id'] in {39:3,64:3,69:2,75:2,85:1}:
        source={39:3,64:3,69:2,75:2,85:1}[q['id']]
        q['sourceMarkFormat']='answer letter printed beside the question, visually checked'
    if q['id'] in CHOICE_REPAIRS:
        q.setdefault('sourceChoices',q['choices'])
        q['choices']=CHOICE_REPAIRS[q['id']]
        q['choiceRepairNote']='Choices transcribed from the original PDF image; source wording is preserved separately.'
    if q['id'] in [39,64,69,75,85]:
        import re
        q.setdefault('sourceQuestion',q['question'])
        q['question']=re.sub(r'\s*-\s*[A-D]\s*$','',q['question'])
    yellow_keys={150:1,151:3,152:1,153:1,154:1,155:0,156:1,157:2,242:2}
    if q['id'] in yellow_keys:
        source=yellow_keys[q['id']]
        q['sourceMarkFormat']='yellow highlight, visually checked in the PDF'
    q['sourceAnswerIndex']=source
    if q['id'] in changes:
        answer,note,refs=changes[q['id']]
        q['answerIndex']=answer;q['reviewNote']=note;q['reviewReferences']=[URL[r] for r in refs]
    q['checkedAnswerIndex']=q['answerIndex']
    if q['answerIndex'] is None and q['id'] in FALLBACK_NOTES:
        assert isinstance(source,int) and 0 <= source < len(q['choices']),q['id']
        q['reviewCaveat']=q['reviewNote']
        q['answerIndex']=source
        q['reviewNote']=FALLBACK_NOTES[q['id']]
        q['answerBasis']='reviewer-key'
        q['resolution']='Uses the marked reviewer key at the learner request; the source ambiguity remains documented.'
    if q['answerIndex'] is None:
        status='unresolved'
        q.setdefault('reviewNote','The choices or source key are incomplete. No single answer is assigned for scoring.')
    elif q.get('answerBasis')=='reviewer-key':
        status='source'
    elif q['id'] in changes or q['id'] in checked or 'reviewNote' in q:
        status='corrected' if source is not None and source!=q['answerIndex'] else 'verified'
    else:
        status='source'
    q['reviewStatus']=status
    q['reviewedOn']='2026-11-25'
    if q['id'] in FINDINGS:
        q['reviewMethod']='Original PDF page visually inspected; source code, table, or diagram traced where applicable. External references are listed when used.'
    if status=='unresolved': q['resolution']='Confirmed source defect or insufficient context; no defensible single answer.'
    elif status!='source': q.pop('resolution',None)
    ledger.append({'id':q['id'],'page':q['sourcePage'],'status':status,'sourceAnswerIndex':source,'studyAnswerIndex':q['answerIndex'],'checkedAnswerIndex':q['checkedAnswerIndex'],'reason':q.get('reviewNote','Checked against the prompt and choices.' if status=='verified' else 'Source answer retained.'),'sourceCaveat':q.get('reviewCaveat'),'references':q.get('reviewReferences',[])})
(ROOT/'questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
from collections import Counter
counts={name:0 for name in ['verified','corrected','source','unresolved']}
counts.update(Counter(q['reviewStatus'] for q in questions))
(ROOT/'answer-review.json').write_text(json.dumps({'reviewedOn':'2026-11-25','scope':'All 242 prompts and choice sets reviewed. The final pass covers all 91 previously source-only items and revisits all 26 previously unresolved items. Original source keys remain separate. The 30 ambiguous items use labeled reviewer-key fallbacks for practice and scoring. checkedAnswerIndex remains null for those fallbacks.','counts':counts,'items':ledger},ensure_ascii=False,indent=2),encoding='utf-8')
print(counts)
from html import escape
def e(value): return escape(str(value))
labels={'verified':'Checked answer','corrected':'Corrected answer','source':'Reviewer answer — source ambiguity','unresolved':'Source defect — study only'}
rows=[]
for q,item in zip(questions,ledger):
    source=((q.get('sourceChoices') or q['choices'])[q['sourceAnswerIndex']] or f'Diagram choice {chr(65+q["sourceAnswerIndex"])} (see the source figure)') if q['sourceAnswerIndex'] is not None else 'No source mark found'
    answer=q['choices'][q['answerIndex']] if q['answerIndex'] is not None else 'No single answer assigned'
    rows.append(f'<tr data-status="{q["reviewStatus"]}"><td>#{q["id"]}<br>PDF p. {q["sourcePage"]}</td><td><b>{e(q["question"])}</b><p>{e(item["reason"])}</p></td><td>{e(source)}</td><td>{e(answer)}<p><strong>{e(labels[q["reviewStatus"]])}</strong></p>'+''.join(f'<a href="{e(url)}" target="_blank" rel="noopener">Reference ↗</a> ' for url in item['references'])+'</td></tr>')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TOPCIT answer review</title><style>body{margin:0;background:#1c2639;color:#edf2fb;font:15px/1.6 system-ui}main{max-width:1250px;margin:auto;padding:24px}a{color:#abc1ff}h1{line-height:1.2}p{color:#b5c4dc}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:16px;border-bottom:1px solid #43546f;vertical-align:top}td:first-child{min-width:75px}td:nth-child(2){width:40%}input,select{background:#243148;color:#edf2fb;padding:12px;border:1px solid #7183a1;border-radius:9px;font:inherit;max-width:100%;box-sizing:border-box}.filters{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0}tr[data-status=corrected] td:last-child strong,tr[data-status=unresolved] td:last-child strong{color:#ffd69b}a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #ffb095;outline-offset:4px}[hidden]{display:none!important}@media(max-width:650px){main{padding:16px}table,tbody,tr,td{display:block}thead{display:none}tr{margin-bottom:24px;background:#243148;border-radius:14px;padding:8px}td{width:auto!important;padding:10px;border:0}td:nth-child(3):before{content:'Reviewer key: ';font-weight:700}td:nth-child(4):before{content:'Study answer: ';font-weight:700}}</style><main><a href="./">← Return to TOPCIT</a><h1>Answer review</h1><p>All 242 prompts and choice sets were reviewed on 25 November 2026. The final pass covers all 91 previously source-only answers and revisits all 26 previously unresolved items. The 30 ambiguous items now use the marked reviewer key at the learner request. Their labels distinguish reviewer answers from checked answers. Each finding preserves the reviewer key and explains its source caveat.</p>'''
html+=f'<p>{counts["corrected"]} corrected · {counts["verified"]} checked · {counts["source"]} reviewer answers · {counts["unresolved"]} unresolved</p>'
html+='''<div class="filters"><input id="search" type="search" placeholder="Search the question or answer" aria-label="Search audit"><select id="status" aria-label="Filter status"><option value="all">All statuses</option><option value="corrected">Corrected</option><option value="verified">Checked</option><option value="source">Reviewer answers</option><option value="unresolved">Source defects / study only</option></select></div><table><thead><tr><th>Item</th><th>Question and review</th><th>Reviewer key</th><th>Study answer</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table><script>const search=document.getElementById('search'),status=document.getElementById('status');function filter(){for(const row of document.querySelectorAll('tbody tr'))row.hidden=!(row.textContent.toLowerCase().includes(search.value.toLowerCase())&&(status.value==='all'||row.dataset.status===status.value));}search.addEventListener('input',filter);status.addEventListener('change',filter);</script></main></html>'''
(ROOT/'answer-review.html').write_text(html,encoding='utf-8')
