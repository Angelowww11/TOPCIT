const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const shuffle = array => { const a = [...array]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const STORAGE = 'topcit-study-lab-v1';
const load = () => { try { return JSON.parse(localStorage.getItem(STORAGE)) || {}; } catch { return {}; } };
const state = { stats: {}, saved: [], weak: [], session: null, ...load() };
const persist = () => { try { localStorage.setItem(STORAGE, JSON.stringify(state)); } catch {} };
let questions = [], byId = new Map(), domain = window.TOPCIT_LESSONS[0].domain, bankLimit = 24, selected = null, answered = false, timerHandle = null, toastHandle = null;
const correctBefore = Object.values(state.stats).reduce((n,s)=>n+(Number(s.correct)||0),0);
if (!Number.isFinite(state.xp)) state.xp = 30 + correctBefore * 10;
if (!Number.isFinite(state.lifetimeXp)) state.lifetimeXp = correctBefore * 10;
state.bestStreak ||= 0;
state.trainingClears ||= 0;
state.sound ??= false;
state.bests ||= {};
const RANKS = [[0,'Rookie'],[120,'Explorer'],[350,'Analyst'],[750,'Architect'],[1400,'TOPCIT Ace']];
const POWER_COST = {fifty:20,freeze:25,shield:30};
const MATCH_PAIRS = [
  {id:'backlog',domain:'Software development',term:'Product backlog',meaning:'Ordered product work managed by the Product Owner.'},
  {id:'stack',domain:'Software development',term:'Stack',meaning:'A last-in, first-out collection.'},
  {id:'3nf',domain:'Understanding data',term:'Third normal form',meaning:'Removes transitive dependencies between nonkey attributes.'},
  {id:'kmeans',domain:'Understanding data',term:'K-means',meaning:'Groups unlabeled observations by similarity.'},
  {id:'mmu',domain:'System architecture',term:'Memory Management Unit',meaning:'Translates virtual addresses into physical addresses.'},
  {id:'dns',domain:'System architecture',term:'DNS',meaning:'Maps domain names to address records.'},
  {id:'raid5',domain:'System architecture',term:'RAID 5',meaning:'Stripes data with distributed parity across drives.'},
  {id:'tls',domain:'Information security',term:'TLS',meaning:'Protects application traffic using a secure handshake.'},
  {id:'rbac',domain:'Information security',term:'Role-based access control',meaning:'Groups permissions by a person’s job role.'},
  {id:'erp',domain:'IT business and ethics',term:'ERP',meaning:'Integrates business functions around shared data.'},
  {id:'hype',domain:'IT business and ethics',term:'Hype Cycle',meaning:'Plots expectations for a technology over time.'},
  {id:'charter',domain:'Project management & communication',term:'Project charter',meaning:'Authorizes a project and grants the manager authority.'},
  {id:'pert',domain:'Project management & communication',term:'PERT estimate',meaning:'Weights the most likely estimate four times.'}
];
let audioContext;
let matchHandle;
function playTone(kind) {
  if (!state.sound) return;
  try {
    audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
    const notes = kind === 'good' ? [[620,0],[820,.08],[1040,.16]] : kind === 'bad' ? [[260,0],[190,.12]] : [[460,0],[690,.08]];
    notes.forEach(([frequency,delay]) => {
      const oscillator=audioContext.createOscillator(),gain=audioContext.createGain(),at=audioContext.currentTime+delay;
      oscillator.type=kind==='bad'?'triangle':'sine';oscillator.frequency.setValueAtTime(frequency,at);
      gain.gain.setValueAtTime(.0001,at);gain.gain.exponentialRampToValueAtTime(.11,at+.012);gain.gain.exponentialRampToValueAtTime(.0001,at+.16);
      oscillator.connect(gain).connect(audioContext.destination);oscillator.start(at);oscillator.stop(at+.17);
    });
  } catch {}
}
function burst(kind,target=$('gameAction')) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const layer=$('fxLayer'), center=target.getBoundingClientRect();
  const x=center.left+center.width/2,y=center.top+center.height/2;
  for(let i=0;i<12;i++){
    const spark=document.createElement('i'),angle=(Math.PI*2*i)/12,distance=55+Math.random()*95;
    spark.className=`spark ${kind}`;spark.style.left=`${x}px`;spark.style.top=`${y}px`;
    spark.style.setProperty('--dx',`${Math.cos(angle)*distance}px`);spark.style.setProperty('--dy',`${Math.sin(angle)*distance}px`);
    layer.append(spark);setTimeout(()=>spark.remove(),900);
  }
}
function rankInfo(){const i=Math.max(0,RANKS.findLastIndex(([points])=>state.lifetimeXp>=points));const next=RANKS[i+1];return {level:i+1,title:RANKS[i][1],next,progress:next?pct(state.lifetimeXp-RANKS[i][0],next[0]-RANKS[i][0]):100};}
const keyed = () => questions.filter(q => Number.isInteger(q.answerIndex) && q.answerIndex >= 0 && q.answerIndex < q.choices.length);
const domainQuestions = name => questions.filter(q => q.domain === name);
const pct = (a,b) => b ? Math.round(a * 100 / b) : 0;
function toast(message) { const el = $('toast'); el.textContent = message; el.classList.add('show'); clearTimeout(toastHandle); toastHandle = setTimeout(() => el.classList.remove('show'), 2500); }
function pauseSession(){const s=state.session;if(!s||s.paused)return;clearInterval(timerHandle);if(s.mode==='blitz'&&!s.checked)s.remainingTime=Math.max(0,s.deadline-Date.now());if(s.mode==='exam')s.pausedAt=Date.now();s.paused=true;persist();}
function show(view) { if(view!=='game'&&$('game').classList.contains('active'))pauseSession();if(view!=='match'&&$('match').classList.contains('active'))pauseMatch();document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === view)); document.querySelectorAll('.nav').forEach(el => el.classList.toggle('active', el.dataset.view === view)); if (view === 'progress') renderProgress(); if (view === 'bank') renderBank(); if (view === 'study') renderStudy(); if(view==='path')window.TOPCIT_PATH?.render();if(view==='home')window.TOPCIT_PATH?.updateHome(); history.replaceState(null,'',`#/${['game','finish','match'].includes(view) ? 'practice' : view}`); window.scrollTo({top:0,behavior:'instant'}); }
function sourceLocation(q) { const pages=q.exhibitPages||[q.sourcePage]; return `PDF ${pages.length>1?'pages':'page'} ${pages.length>1&&pages[pages.length-1]-pages[0]===pages.length-1?`${pages[0]}–${pages[pages.length-1]}`:pages.join(', ')}`; }
function sourceFigure(q, lazy=false) { return q.exhibit?`<figure class="source-figure"><a href="${esc(q.exhibit)}" target="_blank" rel="noopener" aria-label="Open the original example at full size"><img ${lazy?'loading="lazy"':''} src="${esc(q.exhibit)}" alt="Original question example from ${esc(sourceLocation(q))}"></a><figcaption><a href="${esc(q.exhibit)}" target="_blank" rel="noopener">${esc(sourceLocation(q))} · Tap to enlarge ↗</a></figcaption></figure>`:''; }
function subject(q) { return `${q.question} ${q.choices.join(' ')}`; }
function lessonFor(q) { const group = window.TOPCIT_LESSONS.find(x => x.domain === q.domain); if(!group)return null; const ranked=group.modules.map(m=>{const re=new RegExp(m[1],'gi');const promptHits=[...new Set([...q.question.matchAll(re)].map(x=>x[0].toLowerCase()))], answerHits=[...new Set([...String(q.choices[q.answerIndex]||'').matchAll(re)].map(x=>x[0].toLowerCase()))];return {m,score:promptHits.reduce((n,x)=>n+2+x.length/5,0)+answerHits.reduce((n,x)=>n+4+x.length/2,0)};}).sort((a,b)=>b.score-a.score);return ranked[0]?.score>0 ? ranked[0].m:null; }
function answerLabel(q) { return q.reviewStatus==='source'?'Reviewer answer':q.answerIndex===null?'No verified single answer':q.reviewStatus==='corrected'?'Corrected answer':'Checked answer'; }
function answerEvidence(q) {
  const label=answerLabel(q),source=(q.sourceChoices||q.choices)[q.sourceAnswerIndex] || (Number.isInteger(q.sourceAnswerIndex)?`Diagram choice ${String.fromCharCode(65+q.sourceAnswerIndex)} (see the source figure)`:'');
  return `<div class="answer-evidence" data-status="${esc(q.reviewStatus||'source')}"><span class="evidence-label">${esc(label)}</span><p>${q.reviewStatus==='source'?'This question uses the marked reviewer key for practice and scoring. The source has an ambiguity; the note below explains it.':q.reviewStatus==='unresolved'?'This item is study only. It does not enter scored rounds.':q.reviewStatus==='corrected'?'The study answer differs from the supplied reviewer key.':'The answer was checked against the question and choices.'}</p>${q.reviewNote?`<p>${esc(q.reviewNote)}</p>`:''}<details><summary>Compare the reviewer key · ${esc(sourceLocation(q))}</summary><p><b>Reviewer marked:</b> ${source?esc(source):'No answer mark found.'}</p><p><b>Study answer:</b> ${q.answerIndex===null?'No single answer assigned.':esc(q.choices[q.answerIndex])}</p><p>Review date: ${esc(q.reviewedOn||'2026-11-25')}</p></details>${q.reviewReferences?.length?`<div class="source-links">${q.reviewReferences.map((url,i)=>`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Reference ${i+1} ↗</a>`).join('')}</div>`:''}</div>`;
}
function explanation(q) { return answerEvidence(q)+explanationContent(q); }
function explanationContent(q, includeMemory=true) { const lesson = lessonFor(q), answer = q.choices[q.answerIndex]; if (!answer) return '';
  const memory = lesson && includeMemory ? `<p><b>Memory cue:</b> ${esc(lesson[3])}</p>` : '';
  if (q.reviewNote) return lesson?`<p><b>Related concept:</b> ${esc(lesson[2])}</p>${memory}`:'';
  if (lesson) return `<p><b>Why this works:</b> ${esc(lesson[2])}</p>${memory}<p class="source">Reviewer page ${q.sourcePage} · ${esc(lesson[0])}</p>`;
  return `<p><b>Read the question carefully:</b> the reviewer marks <b>${esc(answer)}</b>. Match the exact task and qualifiers in the prompt to that choice. Check each alternative against those same qualifiers, especially words like <b>NOT</b>, <b>best</b>, and <b>first</b>.</p><p class="source">Reviewer page ${q.sourcePage} · Source-marked answer</p>`;
}
function updateHeader() { const total = Object.values(state.stats).reduce((n,s) => n + s.seen, 0), rank=rankInfo(); $('topStat').textContent = `✦ ${state.xp} XP · ${total} answers`; $('heroCount').textContent = `${questions.length} source items · ${keyed().length} scored`; $('rankLevel').textContent=rank.level; $('rankTitle').textContent=rank.title; $('rankNext').textContent=rank.next?`${Math.max(0,rank.next[0]-state.lifetimeXp)} lifetime XP to ${rank.next[1]}`:'Highest rank reached · keep your streak alive'; $('levelFill').style.width=`${rank.progress}%`; $('homeXp').textContent=state.xp; $('homeBest').textContent=state.bestStreak; $('homeClears').textContent=state.trainingClears; $('soundToggle').setAttribute('aria-pressed',String(state.sound)); $('soundToggle').setAttribute('aria-label',state.sound?'Turn sound off':'Turn sound on'); $('soundToggle').title=state.sound?'Sound on':'Sound off'; $('soundToggle').classList.toggle('on',state.sound); }
function renderHome() { updateHeader(); $('heroPractice').innerHTML = state.session ? `Continue ${esc(modeName(state.session))} <span>↗</span>` : 'Start a practice round <span>↗</span>'; $('homeDomains').innerHTML = window.TOPCIT_LESSONS.map(d => { const qs = domainQuestions(d.domain), done = qs.filter(q => state.stats[q.id]?.seen).length; return `<button class="domain-card" style="--domain:${d.color}" data-domain="${esc(d.domain)}"><span class="domain-icon">${esc(d.icon)}</span><span><strong>${esc(d.domain)}</strong><small>${qs.length} items · ${done} visited</small></span><span class="domain-meter"><span style="width:${pct(done,qs.length)}%"></span></span></button>`; }).join(''); }
function renderStudy() { $('studyNav').innerHTML = window.TOPCIT_LESSONS.map(d => `<button class="${domain === d.domain ? 'active':''}" data-study-domain="${esc(d.domain)}">${esc(d.icon)} &nbsp;${esc(d.domain)}</button>`).join(''); const d = window.TOPCIT_LESSONS.find(x => x.domain === domain); $('lessonPanel').innerHTML = `<div class="lesson-intro"><span class="domain-icon" style="--domain:${d.color}">${esc(d.icon)}</span><div><h2>${esc(d.domain)}</h2><p>${domainQuestions(domain).length} reviewer questions · ${d.modules.length} learning notes</p></div></div><button class="primary" data-domain-round="${esc(domain)}">Practice this area ↗</button><p class="study-instruction">Read the idea, recall it from memory, then open a matching source example.</p>${d.modules.map((m,i) => {const pattern=new RegExp(m[1],'i');const related=domainQuestions(d.domain).filter(q=>pattern.test(q.question));const sample=related.find(q=>q.exhibit)||related[0];return `<article class="lesson-card"><span class="overline">CONCEPT ${i+1}</span><h3>${esc(m[0])}</h3><p>${esc(m[2])}</p><details class="recall-card"><summary>✦ Try to recall the key idea</summary><p>${esc(m[3])}</p></details>${sample?`<details class="source-example"><summary>${sample.exhibit?'▧ View source figure and question':'◉ Try a source question'} <small>${esc(sourceLocation(sample))}</small></summary><div class="source-example-body">${sourceFigure(sample,true)}<p><b>Source question:</b> ${esc(sample.question)}</p><details class="source-answer"><summary>Reveal source answer</summary><p>${sample.answerIndex===null?'The supplied answer key needs review for this item.':esc(sample.choices[sample.answerIndex])}</p>${answerEvidence(sample)}</details></div></details>`:''}<button data-topic="${esc(m[1])}">Find related questions ↗</button></article>`;}).join('')}`; }
function bankFiltered() { const search = $('bankSearch').value.trim().toLocaleLowerCase(), d = $('bankDomain').value, filter = $('bankKey').value; return questions.filter(q => (d === 'all' || d === q.domain) && (!search || subject(q).toLocaleLowerCase().includes(search)) && (filter === 'all' || (filter === 'keyed' && q.answerIndex !== null) || (filter === 'unkeyed' && q.answerIndex === null) || (filter === 'saved' && state.saved.includes(q.id)) || q.reviewStatus === filter)); }
function renderBank() { const list = bankFiltered(); $('bankStatus').textContent = `${list.length} matching ${list.length === 1 ? 'question' : 'questions'} · ${keyed().length} available for scored rounds`; $('bankResults').innerHTML = list.slice(0,bankLimit).map(q => `<article class="bank-card" id="bank-${q.id}"><div class="bank-meta"><span>#${q.sourceNumber}</span><span>${esc(q.domain)}</span><span>${esc(sourceLocation(q))}</span></div><button class="save" title="${state.saved.includes(q.id) ? 'Remove saved question':'Save question'}" aria-label="${state.saved.includes(q.id) ? 'Remove saved question':'Save question'}" data-save="${q.id}">${state.saved.includes(q.id) ? '★':'☆'}</button><h3>${esc(q.question)}</h3>${sourceFigure(q,true)}<ol class="bank-choices" type="A">${q.choices.map(c => `<li>${esc(c)}</li>`).join('')}</ol><button data-reveal="${q.id}">Show answer and explanation</button><div class="answer-detail" hidden></div></article>`).join('') || '<p>No questions match those filters.</p>'; $('bankMore').hidden = list.length <= bankLimit; }
function revealBank(id, button) { const q = byId.get(id), detail = button.nextElementSibling, open = detail.hidden; button.closest('.bank-card').querySelectorAll('.bank-choices li').forEach((li,i)=>li.classList.toggle('answer-highlight',open&&i===q.answerIndex)); detail.hidden = !open; button.textContent = open ? 'Hide answer and explanation' : 'Show answer and explanation'; if (open) detail.innerHTML = `<div class="answer ${q.answerIndex === null ? 'unkeyed':''}">${q.answerIndex === null ? 'Answer key needs review' : `✓ ${esc(q.choices[q.answerIndex])}`}</div><div class="bank-explanation">${explanation(q)}</div>`; }
function renderProgress() { const stats = Object.values(state.stats), seen = stats.reduce((n,s)=>n+s.seen,0), correct = stats.reduce((n,s)=>n+s.correct,0), unique = stats.length; $('progressGrid').innerHTML = `<article class="progress-tile"><b>${esc(rankInfo().title)}</b><span>Study rank · ${state.lifetimeXp} lifetime XP</span></article><article class="progress-tile"><b>${state.xp}</b><span>XP available for power-ups</span></article><article class="progress-tile"><b>${state.bestStreak}</b><span>Best streak</span></article><article class="progress-tile"><b>${state.trainingClears}</b><span>Training sets cleared</span></article><article class="progress-tile"><b>${state.bests.blitz||'—'}</b><span>Best Boss Blitz score</span></article><article class="progress-tile"><b>${state.matchBest?matchTimeText(state.matchBest*1000):'—'}</b><span>Best Match Maker time</span></article><article class="progress-tile"><b>${seen}</b><span>Total answers</span></article><article class="progress-tile"><b>${pct(correct,seen)}%</b><span>Accuracy</span></article><article class="progress-tile"><b>${unique}</b><span>Unique questions visited</span></article><article class="progress-tile"><b>${state.weak.length}</b><span>Questions to revisit</span></article><article class="progress-tile"><b>${state.saved.length}</b><span>Saved questions</span></article><article class="progress-tile"><b>${state.session ? state.session.index+1 : '—'}</b><span>${state.session ? 'Resume from question' : 'No unfinished round'}</span></article>${window.TOPCIT_LESSONS.map(d => { const ids=domainQuestions(d.domain).map(q=>q.id), done=ids.filter(id=>state.stats[id]?.seen).length; return `<article class="progress-tile domain-progress"><strong>${esc(d.icon)} ${esc(d.domain)}</strong><b>${pct(done,ids.length)}%</b><span>${done} of ${ids.length} visited</span><span class="domain-meter" style="--domain:${d.color}"><span style="width:${pct(done,ids.length)}%"></span></span></article>`; }).join('')}`; }
function makeSession(mode, specificDomain=null, size=null) { let pool = keyed(); if (mode === 'weak') { const weak = new Set(state.weak); pool = pool.filter(q => weak.has(q.id)); if (!pool.length) { toast('No misses yet — starting a quick practice round.'); mode = 'quick'; pool = keyed(); } } if (specificDomain) pool = pool.filter(q => q.domain === specificDomain); const count = mode === 'exam' ? 50 : mode === 'all' ? pool.length : mode === 'blitz' ? 15 : mode === 'training' ? Number(size)||20 : 20; const picked = shuffle(pool).slice(0,count); return { mode, domain: specificDomain, ids: picked.map(q => q.id), targetCount:picked.length, orders: Object.fromEntries(picked.map(q => [q.id,shuffle(q.choices.map((_,i)=>i))])), index:0, score:0, streak:0, bestStreak:0, wrong:[], allMisses:[], phase:1, attempts:0, hearts:mode==='blitz'?3:null, started:Date.now(), deadline:mode==='blitz'?Date.now()+22000:null, selected:null, checked:false, used:{}, eliminated:[], shield:false, awarded:[] }; }
function start(mode, specificDomain=null, size=null) { if (!questions.length) return; state.session = makeSession(mode,specificDomain,size); selected = null; answered = false; persist(); show('game'); renderGame(); }
function resume() { if (!state.session) return; const s=state.session;if(s.paused){if(s.mode==='blitz'&&!s.checked)s.deadline=Date.now()+(s.remainingTime??22000);if(s.mode==='exam'&&s.pausedAt)s.started+=Date.now()-s.pausedAt;s.paused=false;s.pausedAt=null;persist();} selected=s.selected; answered=s.checked; show('game'); renderGame(); }
function gameQuestion() { const s=state.session; return s && byId.get(s.ids[s.index]); }
function modeName(s) { return s.mode === 'exam' ? 'Exam sprint' : s.mode === 'weak' ? 'Missed questions' : s.mode === 'all' ? 'All questions' : s.mode === 'training' ? 'Training loop' : s.mode === 'blitz' ? 'Boss blitz' : 'Quick practice'; }
function powerMarkup(s,q){
  const disabled=(id,allowed=true)=>s.checked||s.used?.[id]||state.xp<POWER_COST[id]||!allowed;
  const item=(id,label,detail,allowed=true)=>`<button type="button" data-power="${id}" ${disabled(id,allowed)?'disabled':''} title="${esc(s.used?.[id]?'Used this round':state.xp<POWER_COST[id]?`Need ${POWER_COST[id]} XP`:detail)}"><b>${label}</b><small>${POWER_COST[id]} XP · ${esc(detail)}</small></button>`;
  return `<div class="power-heading"><strong>Power shelf</strong><span>Earn XP by answering · each item once per run</span></div><div class="power-row">${item('fifty','½ 50/50','Cross out two wrong choices')}${item('shield','◇ Shield',s.shield?'Shield ready for a miss':'Save your streak and a heart')}${item('freeze','❄ +7 seconds','Blitz only',s.mode==='blitz')}</div>`;
}
function renderGame() {
  const s=state.session,q=gameQuestion();if(!s||!q){finish();return;}
  selected=s.selected;answered=s.checked;
  $('game').dataset.gameMode=s.mode;
  $('gameMode').textContent=s.domain||modeName(s);
  $('gameCount').textContent=`${s.mode==='training'?`Round ${s.phase} · `:''}${s.index+1} / ${s.ids.length}`;
  $('gameScore').textContent=`${s.score} correct`;
  $('gameStreak').textContent=`✦ ${s.streak||0} streak`;
  $('gameXp').textContent=`${state.xp} XP`;
  $('gameHearts').hidden=s.mode!=='blitz';
  if(s.mode==='blitz'){$('gameHearts').textContent=`${'♥ '.repeat(s.hearts||0)}${'♡ '.repeat(3-(s.hearts||0))}`.trim();$('gameHearts').setAttribute('aria-label',`${s.hearts} hearts remaining`);}
  $('gameProgress').style.width=`${pct(s.index,s.ids.length)}%`;
  $('gameDomain').textContent=q.domain;$('gameSource').textContent=sourceLocation(q);$('gameTitle').textContent=q.question;
  $('gameExhibit').innerHTML=sourceFigure(q);
  $('gameChoices').innerHTML=s.orders[q.id].map((idx,pos)=>{const eliminated=(s.eliminated||[]).includes(idx);return `<button data-choice="${idx}" class="${idx===selected?'selected':''} ${s.checked&&idx===q.answerIndex?'correct':''} ${s.checked&&idx===selected&&idx!==q.answerIndex?'wrong':''} ${eliminated?'eliminated':''}" ${s.checked||eliminated?'disabled':''}><span>${pos+1}</span>${esc(q.choices[idx])}</button>`;}).join('');
  $('gamePowers').innerHTML=powerMarkup(s,q);
  const final=s.mode==='blitz'&&s.hearts<=0||s.index+1===s.ids.length&&!(s.mode==='training'&&s.wrong.length);
  $('gameAction').textContent=s.checked?(final?'See results ↗':s.mode==='training'&&s.index+1===s.ids.length?'Retry misses ↻':'Next question ↗'):'Choose an answer';
  $('gameAction').disabled=!s.checked&&selected===null;
  $('gameFeedback').hidden=!s.checked;
  $('gameFeedback').className=`game-feedback ${s.checked&&selected!==q.answerIndex?'wrong':''}`;
  if(s.checked)$('gameFeedback').innerHTML=`<strong>${s.timedOut?'Time is up.':selected===q.answerIndex?(q.reviewStatus==='source'?'Matches the reviewer key.':'Correct — nicely done.'):(q.reviewStatus==='source'?'Different from the reviewer key.':'Not quite. Try the idea again.')}</strong><p><b>${esc(answerLabel(q))}:</b> ${esc(q.choices[q.answerIndex])}</p>${s.lastEarned?`<p class="earned">+${s.lastEarned} XP${s.lastBonus?' · streak bonus!':''}</p>`:''}${s.lastShielded?'<p class="earned">Shield saved your streak and heart.</p>':''}${explanation(q)}`;
  updateTimer();
}
function choose(index) { const s=state.session; if (!s || s.checked || (s.eliminated||[]).includes(index)) return; selected=index; s.selected=index; gradeCurrent(false); }
function usePower(id){
  const s=state.session,q=gameQuestion();if(!s||!q||s.checked||s.used?.[id]||!POWER_COST[id]||state.xp<POWER_COST[id]||id==='freeze'&&s.mode!=='blitz')return;
  s.used ||= {};s.used[id]=true;state.xp-=POWER_COST[id];
  if(id==='fifty'){
    s.eliminated=shuffle(q.choices.map((_,i)=>i).filter(i=>i!==q.answerIndex)).slice(0,2);
    if(s.eliminated.includes(s.selected)){s.selected=null;selected=null;}
  }
  if(id==='shield')s.shield=true;
  if(id==='freeze')s.deadline+=7000;
  persist();renderGame();playTone('power');burst('power');
  toast(id==='fifty'?'Two wrong choices crossed out.':id==='shield'?'Shield armed for your next miss.':'Seven seconds added!');
}
function gradeCurrent(timedOut=false){
  const s=state.session,q=gameQuestion();if(!s||!q||s.checked||!timedOut&&s.selected===null)return;
  s.checked=true;s.timedOut=timedOut;s.attempts=(s.attempts||0)+1;s.lastEarned=0;s.lastBonus=false;s.lastShielded=false;
  const correct=!timedOut&&s.selected===q.answerIndex;
  if(correct){
    s.score++;s.streak=(s.streak||0)+1;s.bestStreak=Math.max(s.bestStreak||0,s.streak);state.bestStreak=Math.max(state.bestStreak||0,s.streak);
    state.weak=state.weak.filter(id=>id!==q.id);
    s.awarded ||= [];
    if(!s.awarded.includes(q.id)){
      s.awarded.push(q.id);const bonus=s.streak%5===0?10:0;
      s.lastEarned=10+Math.min(s.streak,5)*2+bonus;s.lastBonus=!!bonus;
      state.xp+=s.lastEarned;state.lifetimeXp+=s.lastEarned;s.xpEarned=(s.xpEarned||0)+s.lastEarned;
    }
    if(s.mode==='blitz'&&s.streak%4===0&&s.hearts<3){s.hearts++;toast('Four in a row — one heart restored!');}
  }else{
    if(!s.wrong.includes(q.id))s.wrong.push(q.id);
    s.allMisses ||= [];if(!s.allMisses.includes(q.id))s.allMisses.push(q.id);
    if(!state.weak.includes(q.id))state.weak.push(q.id);
    if(s.shield){s.shield=false;s.lastShielded=true;}else{s.streak=0;if(s.mode==='blitz')s.hearts=Math.max(0,s.hearts-1);}
  }
  const st=state.stats[q.id]||{seen:0,correct:0};st.seen++;if(correct)st.correct++;state.stats[q.id]=st;
  persist();renderGame();updateHeader();playTone(correct?'good':'bad');burst(correct?'good':'bad');
}
function advanceQuestion(){
  const s=state.session;if(!s)return;
  if(s.mode==='blitz'&&s.hearts<=0){finish();return;}
  if(s.index+1>=s.ids.length){
    if(s.mode==='training'&&s.wrong.length){
      s.ids=shuffle(s.wrong);s.phase++;s.wrong=[];s.index=0;
      s.ids.forEach(id=>s.orders[id]=shuffle(byId.get(id).choices.map((_,i)=>i)));
      toast(`Round ${s.phase}: ${s.ids.length} missed ${s.ids.length===1?'question':'questions'} to clear.`);
    }else{finish();return;}
  }else s.index++;
  s.selected=null;s.checked=false;s.timedOut=false;s.eliminated=[];s.lastEarned=0;s.lastShielded=false;selected=null;answered=false;
  if(s.mode==='blitz')s.deadline=Date.now()+Math.max(10,22-(s.attempts||0)*.8)*1000;
  persist();renderGame();
}
function checkOrNext(){const s=state.session;if(!s)return;if(s.checked)advanceQuestion();else gradeCurrent(false);}
function updateTimer(){
  clearInterval(timerHandle);$('gameTimer').textContent='';$('gameTimer').classList.remove('urgent');
  const s=state.session;if(!s||!['exam','blitz'].includes(s.mode))return;
  if(s.mode==='blitz'&&s.checked){$('gameTimer').textContent='Clock paused';return;}
  const tick=()=>{
    if(state.session!==s){clearInterval(timerHandle);return;}
    if(s.mode==='blitz'&&s.checked){clearInterval(timerHandle);return;}
    const left=s.mode==='exam'?Math.max(0,25*60-(Date.now()-s.started)/1000):Math.max(0,(s.deadline-Date.now())/1000);
    $('gameTimer').textContent=s.mode==='exam'?`${Math.floor(left/60)}:${String(Math.floor(left%60)).padStart(2,'0')} left`:`${left.toFixed(1)}s left`;
    $('gameTimer').classList.toggle('urgent',s.mode==='blitz'&&left<3);
    if(left<=0){clearInterval(timerHandle);if(s.mode==='exam')finish(true);else gradeCurrent(true);}
  };
  tick();timerHandle=setInterval(tick,s.mode==='blitz'?100:1000);
}
function finish(timeUp=false){
  const s=state.session;if(!s){show('home');return;}clearInterval(timerHandle);
  const completed=s.attempts??s.index+(s.checked?1:0), cleared=s.mode==='training'&&!timeUp&&!s.wrong.length;
  if(cleared){state.trainingClears++;state.xp+=25;state.lifetimeXp+=25;s.xpEarned=(s.xpEarned||0)+25;}
  state.bests[s.mode]=Math.max(state.bests[s.mode]||0,s.score);
  const missedIds=cleared?[]:s.allMisses||s.wrong, wrong=missedIds.map(id=>byId.get(id)).filter(Boolean);
  $('finishTitle').textContent=timeUp?'Time is up!':cleared?'Training cleared!':s.mode==='blitz'&&s.hearts<=0?'Boss run over':s.score===s.ids.length?'A perfect round!':'Another step forward.';
  $('finishText').textContent=cleared?`You mastered all ${s.targetCount} questions in ${s.phase} ${s.phase===1?'round':'rounds'}. ${s.allMisses.length} needed another try.`:`You answered ${s.score} of ${completed} correctly. ${wrong.length?'Review the misses below, then try again.':'Your next challenge is ready.'}`;
  $('finishStats').innerHTML=`<div class="finish-numbers"><span><b>${s.score}</b> correct</span><span><b>${pct(s.score,completed)}%</b> accuracy</span><span><b>${s.bestStreak||0}</b> best streak</span><span><b>+${s.xpEarned||0}</b> XP earned</span></div><p class="finish-rank">Current rank: <strong>${esc(rankInfo().title)}</strong></p>${wrong.length?`<div class="miss-review"><h2>What to review</h2>${wrong.slice(0,12).map(q=>`<article><b>${esc(q.domain)} · PDF p. ${q.sourcePage}</b><p>${esc(q.question)}</p><p><strong>${esc(answerLabel(q))}: ${esc(q.choices[q.answerIndex])}</strong></p>${explanation(q)}</article>`).join('')}${wrong.length>12?`<p>Plus ${wrong.length-12} more in Missed questions.</p>`:''}</div>`:''}`;
  const replay=document.querySelector('#finish .hero-actions button[data-mode]');replay.dataset.mode='quick';replay.textContent='Play another round ↗';
  state.session=null;persist();renderHome();show('finish');if(cleared)playTone('good');
}
function matchElapsed(s){return (s.elapsed||0)+(s.lastStart?Date.now()-s.lastStart:0);}
function matchTimeText(ms){const seconds=Math.floor(ms/1000);return `${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`;}
function pauseMatch(){const s=state.matchSession;if(!s||!s.lastStart)return;clearInterval(matchHandle);s.elapsed=matchElapsed(s);s.lastStart=null;persist();}
function startMatch(force=false){
  if(state.matchSession&&!force){resumeMatch();return;}
  const domains=[...new Set(MATCH_PAIRS.map(pair=>pair.domain))];
  const pairs=shuffle(domains.map(name=>shuffle(MATCH_PAIRS.filter(pair=>pair.domain===name))[0]));
  state.matchSession={pairs,termOrder:shuffle(pairs.map(x=>x.id)),definitionOrder:shuffle(pairs.map(x=>x.id)),solved:[],selected:null,mistakes:0,streak:0,earned:0,elapsed:0,lastStart:null,message:'Choose a concept to begin.'};
  persist();resumeMatch();
}
function resumeMatch(){const s=state.matchSession;if(!s)return;s.lastStart=Date.now();persist();show('match');renderMatch();clearInterval(matchHandle);matchHandle=setInterval(()=>{if(state.matchSession===s)$('matchClock').textContent=matchTimeText(matchElapsed(s));},1000);}
function renderMatch(){
  const s=state.matchSession;if(!s)return;const pairById=new Map(s.pairs.map(pair=>[pair.id,pair]));
  $('matchCount').textContent=`${s.solved.length} / ${s.pairs.length} pairs`;
  $('matchMistakes').textContent=`${s.mistakes} ${s.mistakes===1?'miss':'misses'} · ✦ ${s.streak} streak`;
  $('matchClock').textContent=matchTimeText(matchElapsed(s));
  $('matchTerms').innerHTML=s.termOrder.map(id=>{const pair=pairById.get(id);return `<button type="button" data-match-term="${id}" class="${s.selected===id?'selected':''} ${s.solved.includes(id)?'solved':''}" ${s.solved.includes(id)?'disabled':''} aria-pressed="${s.selected===id}"><strong>${esc(pair.term)}</strong><small>${esc(pair.domain)}</small></button>`;}).join('');
  $('matchDefinitions').innerHTML=s.definitionOrder.map(id=>{const pair=pairById.get(id);return `<button type="button" data-match-def="${id}" class="${s.solved.includes(id)?'solved':''} ${s.wrongDef===id?'match-wrong':''}" ${s.solved.includes(id)?'disabled':''}>${esc(pair.meaning)}</button>`;}).join('');
  $('matchFeedback').textContent=s.message;
}
function chooseMatchTerm(id){const s=state.matchSession;if(!s||s.solved.includes(id))return;s.selected=id;s.message='Now choose its meaning.';persist();renderMatch();}
function chooseMatchDefinition(id,button){
  const s=state.matchSession;if(!s||s.solved.includes(id))return;
  if(!s.selected){s.message='Choose a concept first.';renderMatch();return;}
  if(s.selected===id){
    s.solved.push(id);s.streak++;state.bestStreak=Math.max(state.bestStreak,s.streak);
    const earned=8+Math.min(s.streak,4)*2;s.earned+=earned;state.xp+=earned;state.lifetimeXp+=earned;
    s.selected=null;s.message=`Matched! +${earned} XP · ${s.solved.length} of ${s.pairs.length} pairs connected.`;
    playTone('good');burst('good',button);persist();updateHeader();renderMatch();
    if(s.solved.length===s.pairs.length)setTimeout(finishMatch,600);
  }else{
    s.mistakes++;s.streak=0;s.selected=null;s.wrongDef=id;s.message='Not that pair. Look for the concept behind the definition.';
    playTone('bad');persist();renderMatch();setTimeout(()=>{if(state.matchSession===s){s.wrongDef=null;renderMatch();}},450);
  }
}
function finishMatch(){
  const s=state.matchSession;if(!s||s.solved.length!==s.pairs.length)return;pauseMatch();
  const seconds=Math.ceil(s.elapsed/1000),bonus=s.mistakes===0?20:0;if(bonus){state.xp+=bonus;state.lifetimeXp+=bonus;s.earned+=bonus;}
  state.matchBest=state.matchBest?Math.min(state.matchBest,seconds):seconds;
  $('finishTitle').textContent=s.mistakes===0?'Flawless connections!':'All pairs connected!';
  $('finishText').textContent=`You linked all six TOPCIT ideas in ${matchTimeText(s.elapsed)}. ${s.mistakes===0?'Perfect run bonus earned.':'Another set will sharpen your recall.'}`;
  $('finishStats').innerHTML=`<div class="finish-numbers"><span><b>6</b> pairs</span><span><b>${s.mistakes}</b> misses</span><span><b>${matchTimeText(s.elapsed)}</b> time</span><span><b>+${s.earned}</b> XP earned</span></div><p class="finish-rank">Best time: <strong>${matchTimeText(state.matchBest*1000)}</strong></p>`;
  const replay=document.querySelector('#finish .hero-actions button[data-mode]');replay.dataset.mode='matching';replay.textContent='Match another set ↗';
  state.matchSession=null;persist();renderHome();show('finish');
}
document.addEventListener('click', e => { const view=e.target.closest('[data-view]'); if(view){e.preventDefault();show(view.dataset.view);return;} const setup=e.target.closest('[data-setup]');if(setup){$('trainingDialog').showModal();return;}const train=e.target.closest('[data-train-size]');if(train){$('trainingDialog').close();start('training',null,Number(train.dataset.trainSize));return;} const mode=e.target.closest('button[data-mode]'); if(mode){if(mode.dataset.mode==='matching')startMatch();else start(mode.dataset.mode);return;} const dc=e.target.closest('[data-domain]'); if(dc){domain=dc.dataset.domain;show('study');return;} const sd=e.target.closest('[data-study-domain]'); if(sd){domain=sd.dataset.studyDomain;renderStudy();return;} const dr=e.target.closest('[data-domain-round]'); if(dr){start('quick',dr.dataset.domainRound);return;} const topic=e.target.closest('[data-topic]'); if(topic){$('bankSearch').value=topic.dataset.topic.split('|')[0];$('bankDomain').value=domain;bankLimit=24;show('bank');return;} const save=e.target.closest('[data-save]'); if(save){const id=Number(save.dataset.save);state.saved=state.saved.includes(id)?state.saved.filter(x=>x!==id):[...state.saved,id];persist();renderBank();return;} const reveal=e.target.closest('[data-reveal]'); if(reveal){revealBank(Number(reveal.dataset.reveal),reveal);return;}const power=e.target.closest('[data-power]');if(power){usePower(power.dataset.power);return;} const choice=e.target.closest('[data-choice]'); if(choice){choose(Number(choice.dataset.choice));return;}const term=e.target.closest('[data-match-term]');if(term){chooseMatchTerm(term.dataset.matchTerm);return;}const definition=e.target.closest('[data-match-def]');if(definition){chooseMatchDefinition(definition.dataset.matchDef,definition);return;} });
document.addEventListener('keydown',e=>{if(!state.session||!$('game').classList.contains('active')||['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName))return; const n=Number(e.key); if(n>=1&&n<=4){const q=gameQuestion(),idx=state.session.orders[q.id][n-1];if(idx!==undefined)choose(idx);} if(e.key==='Enter'){e.preventDefault();checkOrNext();}});
['bankSearch','bankDomain','bankKey'].forEach(id=>$(id).addEventListener(id==='bankSearch'?'input':'change',()=>{bankLimit=24;renderBank();}));
$('bankMore').addEventListener('click',()=>{bankLimit+=24;renderBank();}); $('heroPractice').addEventListener('click',()=>state.session?resume():start('quick')); $('exitGame').addEventListener('click',()=>{clearInterval(timerHandle);show('home');renderHome();toast('Round saved. You can continue later.');}); $('gameAction').addEventListener('click',checkOrNext);
$('exitMatch').addEventListener('click',()=>{show('home');renderHome();toast('Matching set saved.');});$('restartMatch').addEventListener('click',()=>startMatch(true));
$('soundToggle').addEventListener('click',()=>{state.sound=!state.sound;persist();updateHeader();if(state.sound)playTone('power');});
window.addEventListener('pagehide',()=>{if($('game').classList.contains('active'))pauseSession();if($('match').classList.contains('active'))pauseMatch();});
async function init(){try{const response=await fetch('questions.json',{cache:'no-store'});if(!response.ok)throw new Error('Question bank unavailable');questions=await response.json();byId=new Map(questions.map(q=>[q.id,q]));if(state.session && (state.answerReviewVersion!=='2026-11-25-r2'||state.session.ids.some(id=>!byId.has(id)||byId.get(id).answerIndex===null)))state.session=null;state.answerReviewVersion='2026-11-25-r2';persist();if(state.session){const s=state.session;s.attempts??=s.index+(s.checked?1:0);s.allMisses??=[...s.wrong];s.targetCount??=s.ids.length;s.phase??=1;s.used??={};s.eliminated??=[];s.awarded??=[];s.paused=true;if(s.mode==='blitz'&&!s.checked)s.remainingTime??=Math.max(0,s.deadline-Date.now());if(s.mode==='exam')s.pausedAt??=Date.now();}if(state.matchSession)state.matchSession.lastStart=null; $('bankDomain').innerHTML='<option value="all">All six areas</option>'+window.TOPCIT_LESSONS.map(d=>`<option value="${esc(d.domain)}">${esc(d.domain)}</option>`).join('');renderHome();renderStudy();renderBank();renderProgress();window.TOPCIT_PATH?.init();}catch(error){$('heroCount').textContent='Could not load questions';toast(error.message);console.error(error);}} init();
if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));
