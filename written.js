/* Source exercises keep original responses beside the reviewed study answer. */
(() => {
  let data=null, loading=null, saveTimer;
  if (!state.writtenLab || typeof state.writtenLab!=='object' || Array.isArray(state.writtenLab)) state.writtenLab={};
  const lab=state.writtenLab;
  lab.index=Number.isInteger(lab.index)&&lab.index>=1&&lab.index<=45?lab.index:1;
  for (const key of ['drafts','marks','answers','revealed']) if(!lab[key]||typeof lab[key]!=='object'||Array.isArray(lab[key]))lab[key]={};
  lab.correctFirst=lab.correctFirst===true;
  const labels={checked:'Checked answer',corrected:'Corrected answer',reviewer:'Reviewer answer',suggested:'Suggested answer'};
  function save(){persist();}
  function current(){return data?.exercises.find(item=>item.id===lab.index);}
  function filtered(){const query=$('writtenSearch').value.trim().toLowerCase(),filter=$('writtenFilter').value;return data.exercises.filter(item=>(!query||[...item.prompt,...item.givenChoices].join(' ').toLowerCase().includes(query))&&(filter==='all'||filter==='again'&&lab.marks[item.id]==='again'||filter==='gap'&&item.model.sourceIssue||filter==='done'&&lab.marks[item.id]==='done'));}
  function figure(image,caption){return `<figure class="source-figure"><a href="${esc(image.src)}" target="_blank" rel="noopener" aria-label="Open original source figure"><img src="${esc(image.src)}" ${image.width?`width="${image.width}" height="${image.height}"`:''} alt="${esc(caption)}"></a><figcaption><a href="${esc(image.src)}" target="_blank" rel="noopener">${esc(caption)} · Tap to enlarge ↗</a></figcaption></figure>`;}
  function preserve(render){const x=scrollX,y=scrollY;$('written').style.overflowAnchor='none';render();scrollTo({left:x,top:y,behavior:'instant'});requestAnimationFrame(()=>$('written').style.overflowAnchor='');}
  async function open(){
    if(data){render();return;}
    if(loading)return loading;
    $('writtenCard').innerHTML='<p class="written-loading" role="status">Loading the source exercises…</p>';
    loading=(async()=>{try{const response=await fetch('written-exercises.json',{cache:'no-store'});if(!response.ok)throw Error();data=await response.json();render();}catch{$('writtenCard').innerHTML='<p>Could not load the source exercises.</p><button type="button" class="secondary" data-written-load>Try again</button>';loading=null;}})();
    return loading;
  }
  function render(){
    if(!data)return;
    const list=filtered();
    if(!list.some(item=>item.id===lab.index)&&list.length)lab.index=list[0].id;
    const item=current(),at=list.findIndex(q=>q.id===lab.index);
    $('writtenReviewed').textContent=`${data.exercises.filter(q=>lab.marks[q.id]==='done').length} / 45 reviewed · ${data.exercises.filter(q=>lab.marks[q.id]==='again').length} to retry`;
    $('writtenChoose').innerHTML=list.map(q=>`<option value="${q.id}" ${q.id===lab.index?'selected':''}>${q.id}. ${esc(q.title.replace(/\s+/g,' ').slice(0,72))}</option>`).join('');
    $('writtenFirst').checked=lab.correctFirst;
    document.querySelectorAll('[data-written-step]').forEach(button=>button.disabled=!list.length||(Number(button.dataset.writtenStep)<0?at<=0:at>=list.length-1));
    if(!list.length){$('writtenCard').innerHTML='<p>No exercises match these filters.</p>';return;}
    const answer=lab.answers[item.id],selected=Number.isInteger(answer?.selected)?answer.selected:null;
    const shown=!!lab.revealed[item.id];
    const order=item.givenChoices.map((_,index)=>index);
    if(lab.correctFirst&&item.isMultipleChoice)order.splice(0,order.length,item.modelChoice,...order.filter(index=>index!==item.modelChoice));
    const correct=selected===item.modelChoice;
    const images=item.companion?figure(item.companion,`Main reviewer question ${item.companion.questionId} · PDF pages ${item.companion.sourcePages.join(', ')}`)+(item.images.length?`<details class="written-originals"><summary>Original supplementary photos (${item.images.length})</summary>${item.images.map(image=>figure(image,`Original written reviewer · PDF page ${image.sourcePage}`)).join('')}${item.imageNote?`<p>${esc(item.imageNote)}</p>`:''}</details>`:''):item.images.map(image=>figure(image,`Original written reviewer · PDF page ${image.sourcePage}`)).join('');
    const choices=item.isMultipleChoice?`<div class="game-choices written-choices">${order.map((index,position)=>`<button type="button" data-written-choice="${index}" ${selected!==null?'disabled':''} class="${selected!==null&&index===item.modelChoice?'correct':''} ${index===selected&&!correct?'wrong':''}"><span>${position+1}</span>${esc(item.givenChoices[index])}</button>`).join('')}</div>`:'';
    const feedback=selected===null?'':`<p class="written-choice-feedback ${correct?'is-correct':'is-wrong'}" role="status">${item.model.basis==='reviewer'?(correct?'Matches the reviewer key.':'Different from the reviewer key.'):(correct?'Correct — nicely done.':'Not quite. Compare the answer below.')} <button type="button" class="text-link" data-written-retry>Try again ↻</button></p>`;
    const refs=(item.model.references||[]).map((url,i)=>`<a href="${esc(url)}" target="_blank" rel="noopener">Reference ${i+1} ↗</a>`).join(' ');
    $('writtenCard').innerHTML=`<div class="question-meta"><span>EXERCISE ${item.id} / 45</span><span>SUPPLEMENTARY PDF ${item.sourcePages.length>1?'PAGES':'PAGE'} ${item.sourcePages.join(', ')}</span></div><h2>${esc(item.prompt[0])}</h2>${item.prompt.slice(1).map(text=>`<p class="written-prompt">${esc(text)}</p>`).join('')}${item.model.sourceIssue?`<p class="written-source-gap"><b>Source gap:</b> ${esc(item.model.sourceIssue)} The provided response remains below.</p>`:''}${images}${(item.sharedImages||[]).map(image=>figure(image,image.caption)).join('')}${!item.companion&&item.imageNote?`<p class="written-image-note">${esc(item.imageNote)}</p>`:''}${choices}${feedback}<label class="written-draft-label" for="writtenDraft">${item.isMultipleChoice?'Your reasoning or notes':'Write your answer before you reveal it'}</label><textarea id="writtenDraft" rows="5" maxlength="12000" placeholder="Your answer saves on this device.">${esc(typeof lab.drafts[item.id]==='string'?lab.drafts[item.id]:'')}</textarea><div class="written-answer-actions"><button type="button" class="primary" data-written-reveal>${shown?'Hide':'Reveal'} study answer</button><span>Saved automatically · No timer</span></div><div class="written-model answer-evidence" data-status="${esc(item.model.basis==='reviewer'?'source':item.model.basis)}" ${shown?'':'hidden'}><span class="evidence-label">${labels[item.model.basis]}</span><pre>${esc(item.model.answer)}</pre><p>${esc(item.model.reason)}</p>${refs?`<div class="source-links">${refs}</div>`:''}<details class="written-response"><summary>Compare the original ${item.isMultipleChoice?'source choices':'reviewer response'}</summary>${item.model.originalMarkedAnswer?`<p><b>Original marked response:</b> ${esc(item.model.originalMarkedAnswer)}</p>`:''}${item.responses.map(text=>`<pre>${esc(text)}</pre>`).join('')||'<p>The source leaves its answer blank.</p>'}</details><div class="written-mark-actions"><button type="button" class="secondary ${lab.marks[item.id]==='done'?'is-active':''}" data-written-mark="done">✓ I understand this</button><button type="button" class="secondary ${lab.marks[item.id]==='again'?'is-active':''}" data-written-mark="again">↻ Review again</button></div></div><div class="path-bottom-navigation"><button type="button" class="secondary" data-written-step="-1" ${at<=0?'disabled':''}>← Previous</button><button type="button" class="primary" data-written-step="1" ${at>=list.length-1?'disabled':''}>Next →</button></div>`;
    save();
  }
  function step(direction){const list=filtered(),at=list.findIndex(q=>q.id===lab.index);if(list[at+direction]){lab.index=list[at+direction].id;preserve(render);}}
  function choose(index){const item=current();if(!item?.isMultipleChoice||lab.answers[item.id]||!Number.isInteger(index)||index<0||index>=item.givenChoices.length)return;lab.answers[item.id]={selected:index};lab.revealed[item.id]=true;lab.marks[item.id]=index===item.modelChoice?'done':'again';preserve(render);playTone(index===item.modelChoice?'good':'bad');burst(index===item.modelChoice?'good':'bad',$('writtenCard'));}
  $('writtenChoose').addEventListener('change',event=>{lab.index=Number(event.target.value);preserve(render);});
  $('writtenSearch').addEventListener('input',()=>preserve(render));
  $('writtenFilter').addEventListener('change',()=>preserve(render));
  $('writtenFirst').addEventListener('change',event=>{lab.correctFirst=event.target.checked;preserve(render);});
  $('writtenCard').addEventListener('input',event=>{if(event.target.id!=='writtenDraft'||!data)return;lab.drafts[current().id]=event.target.value;clearTimeout(saveTimer);saveTimer=setTimeout(save,250);});
  document.addEventListener('click',event=>{
    if(event.target.closest('[data-written-load]'))open();
    if(!data)return;
    const stepButton=event.target.closest('[data-written-step]');if(stepButton)step(Number(stepButton.dataset.writtenStep));
    const choice=event.target.closest('[data-written-choice]');if(choice)choose(Number(choice.dataset.writtenChoice));
    if(event.target.closest('[data-written-reveal]')){lab.revealed[current().id]=!lab.revealed[current().id];preserve(render);}
    if(event.target.closest('[data-written-retry]')){delete lab.answers[current().id];lab.revealed[current().id]=false;preserve(render);}
    const mark=event.target.closest('[data-written-mark]');if(mark){lab.marks[current().id]=mark.dataset.writtenMark;preserve(render);}
  });
  $('writtenReset').addEventListener('click',()=>{if(!confirm('Clear the written exercise answers, notes, and review marks? Your other progress stays saved.'))return;lab.index=1;lab.drafts={};lab.marks={};lab.answers={};lab.revealed={};$('writtenSearch').value='';$('writtenFilter').value='all';preserve(render);});
  document.addEventListener('keydown',event=>{
    if(!data||!$('written').classList.contains('active')||event.repeat||event.ctrlKey||event.metaKey||event.altKey||event.target.isContentEditable||event.target.closest('input,select,textarea,summary'))return;
    if(event.target.closest('button')&&!event.target.closest('[data-written-choice]'))return;
    const number=Number(event.key);
    if(number>=1&&number<=4){const button=$('writtenCard').querySelectorAll('[data-written-choice]')[number-1];if(button){event.preventDefault();choose(Number(button.dataset.writtenChoice));}}
    if(event.key==='Enter'||event.key==='ArrowRight'){event.preventDefault();step(1);}
    if(event.key==='Backspace'||event.key==='ArrowLeft'){event.preventDefault();step(-1);}
  });
  window.addEventListener('pagehide',save);
  window.TOPCIT_WRITTEN={open,render};
  if(location.hash==='#/written')show('written');
})();
