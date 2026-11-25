"""Build the public, per-question source-content check from reproducible inventories."""
import json
from html import escape as esc
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def build():
    audit=json.loads((ROOT/'content-audit.json').read_text(encoding='utf-8'))
    written=json.loads((ROOT/'written-exercises.json').read_text(encoding='utf-8'))
    audit['written']={'source':written['source'],'pdfPages':17,**written['counts'],
                     'sourceGapExercises':[e['id'] for e in written['exercises'] if e['model'].get('sourceIssue')],
                     'originalPhotosAlreadyCropped':[e['id'] for e in written['exercises'] if e.get('imageNote')]}
    (ROOT/'content-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=[]
    for q in audit['questions']:
        asset=f'<a href="{esc(q["image"])}">Open source figure ↗</a>' if q.get('image') else 'Text only'
        rows.append(f'<tr><td>{q["id"]}</td><td>{esc(q["question"])}</td><td>{", ".join(map(str,q["sourcePages"]))}</td><td>Matches</td><td>{q["includedImageCount"]}/{q["sourceImageCount"]}</td><td>{asset}{" · Restored" if q["restored"] else ""}</td></tr>')
    gaps=''.join(f'<li><b>Exercise {e["id"]}:</b> {esc(e["model"]["sourceIssue"])}</li>' for e in written['exercises'] if e['model'].get('sourceIssue'))
    issues=''.join(f'<li><b>Question {e["id"]}:</b> {esc(e["note"])}</li>' for e in audit['originalSourceIssues'])
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TOPCIT source-content check</title><style>
    :root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#1c2639;color:#edf2fb;font:16px/1.8 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:42px 24px}h1{font-size:clamp(32px,5vw,52px);line-height:1.2}h2{margin-top:40px}p,li{max-width:85ch}a{color:#abc1ff}small{color:#b5c4dc}.counts{display:flex;flex-wrap:wrap;gap:16px}.counts p{flex:1;min-width:170px;background:#243148;border-radius:16px;padding:24px;margin:0}.counts b{display:block;font-size:32px}.notice{background:#463b2c;padding:16px 24px;border-radius:16px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px;min-width:760px}td,th{text-align:left;vertical-align:top;padding:13px;border-bottom:1px solid #43546f}th{background:#243148}td:nth-child(2){min-width:300px}input{display:block;width:100%;max-width:560px;background:#151d2c;color:#edf2fb;border:1px solid #43546f;border-radius:10px;padding:15px;font:inherit;margin:14px 0}summary{cursor:pointer;color:#abc1ff}@media(max-width:500px){main{padding:28px 18px}.counts p{min-width:130px;padding:18px}}
    </style></head><body><main><a href="index.html">← TOPCIT Study Lab</a><p><small>CHECKED 25 NOVEMBER 2026</small></p><h1>Every question.<br>Its original context.</h1>
    <p>This check covers the 242-question bank and the separate 45-exercise written reviewer.</p>
    <div class="counts"><p><b>242</b>Questions checked</p><p><b>164 / 164</b>Source images included</p><p><b>45</b>Written exercises</p><p><b>28 / 28</b>Original written images</p></div>
    <h2>The 242-question bank</h2><p>The check covers all 88 pages of <i>1. TOPCIT Reviewer - Software.pdf</i>. All 88 rendered pages received a visual check. The six matching Word reviewers contain 161 images; every image matches a PDF source picture.</p>
    <p>The check compares native question text and choices. It also checks each picture against its source position and size. The result has zero missing source images, zero native prompt differences, and zero native choice differences.</p>
    <p>The restored figures include tables, diagrams, code, picture choices, and descriptions. The current repair list covers 44 questions. Twenty-one earlier figures had clipped lower edges; their complete source images now replace them.</p>
    <p>The image count excludes three full-page annotation layers on PDF pages 55–57. The repeated NFT question on page 65 remains represented by its matching page 64 question.</p>
    <h2>The 45 written exercises</h2><p>The separate <i>TOPCIT_Reviewer.pdf</i> has 17 pages. All 17 rendered pages received a visual check. Its Word source supplies 157 substantive paragraphs and 28 pictures. The written lab retains every paragraph and all 28 original image files. Each original image has the same SHA-256 hash as the Word image.</p>
    <p>The written lab adds saved drafts, answer comparisons, instant choice feedback, review marks, and an answer-first option. Clearer matching figures from the main reviewer carry an additional-source label.</p>
    <p>Checked, corrected, reviewer, and suggested answers have separate labels. The original response remains available for comparison. These 45 exercises are source entries, not 45 new unique multiple-choice questions.</p>
    <div class="notice"><h2>Gaps in the supplied sources</h2><p>These gaps exist in the original files. The site marks them and keeps the available response.</p><ul>WRITTEN_GAPS</ul><p>Original photographs in exercises 14, 20, 24, 28, 41, and 45 already have cropped edges. The site retains their complete supplied image files. Matching main-reviewer figures supplement exercises 24 and 41.</p><ul>MAIN_ISSUES</ul></div>
    <h2>Scope of this check</h2><p>The six large TOPCIT textbooks remain learning references. This report does not claim a page-by-page audit of those textbooks. The answer audit remains separate from this content-completeness check.</p><p><a href="answer-review.html">Open the answer audit ↗</a> · <a href="index.html#/written">Open the written lab ↗</a> · <a href="content-audit.json">Download the check data</a></p>
    <h2>Question-by-question record</h2><label for="filter">Find a question or number</label><input id="filter" type="search" placeholder="Search the original wording"><p id="status" role="status">242 questions</p><div class="table-wrap" tabindex="0" aria-label="Scrollable question check table"><table><thead><tr><th>Question</th><th>Original question</th><th>PDF pages</th><th>Native text and choices</th><th>Images</th><th>Source figure</th></tr></thead><tbody>ROWS</tbody></table></div>
    <script>const rows=[...document.querySelectorAll('tbody tr')];document.getElementById('filter').addEventListener('input',event=>{let count=0;const query=event.target.value.toLowerCase().trim();for(const row of rows){row.hidden=!!query&&!row.textContent.toLowerCase().includes(query);if(!row.hidden)count++;}document.getElementById('status').textContent=count+' questions';});</script></main></body></html>'''
    html=html.replace('WRITTEN_GAPS',gaps).replace('MAIN_ISSUES',issues).replace('ROWS',''.join(rows))
    (ROOT/'content-audit.html').write_text(html,encoding='utf-8')
    print('Built public source-content report.')

if __name__=='__main__':build()
