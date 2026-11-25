/* Untimed source-order practice. Progress is independent from scored rounds. */
(() => {
  const allowedStatuses = new Set(['correct', 'wrong', 'revealed', 'viewed', 'skipped']);
  let pool = [];
  let ready = false;

  function progress() { return state.practicePath; }
  function current() { return pool[progress().index]; }
  function recordFor(q) { return progress().entries[q.id]; }
  function reviewed(record) { return record && record.status !== 'skipped'; }
  function save() { persist(); updateHome(); }
  function init() {
    if (!questions.length) return;
    pool = [...questions].sort((a, b) => a.id - b.id);
    if (!state.practicePath || typeof state.practicePath !== 'object' || Array.isArray(state.practicePath)) state.practicePath = {};
    const p = progress();
    p.index = Number.isInteger(p.index) ? Math.max(0, Math.min(pool.length - 1, p.index)) : 0;
    p.shuffleChoices = p.shuffleChoices === true;
    p.correctFirst = p.correctFirst === true;
    p.explanations = p.explanations !== false;
    p.keyIdea = p.keyIdea !== false;
    p.orders = p.orders && typeof p.orders === 'object' && !Array.isArray(p.orders) ? p.orders : {};
    p.entries = p.entries && typeof p.entries === 'object' && !Array.isArray(p.entries) ? p.entries : {};
    for (const [id, record] of Object.entries(p.entries)) {
      const q = byId.get(Number(id));
      if (!q || !record || !allowedStatuses.has(record.status) || record.key !== q.answerIndex || record.keyText !== (q.choices[q.answerIndex] || null)) delete p.entries[id];
    }
    ready = true;
    save();
    if ($('path').classList.contains('active')) render();
    else if (location.hash === '#/path') show('path');
  }
  function updateHome() {
    if (!ready) return;
    const p = progress(), count = pool.filter(q => reviewed(recordFor(q))).length;
    $('pathHomeProgress').textContent = count || p.index ? `Continue at #${p.index + 1} ↗` : 'Open Practice path ↗';
    $('pathHomeCount').textContent = `${pool.length} questions · ${count} reviewed`;
  }
  function validOrder(order, q) {
    return Array.isArray(order) && order.length === q.choices.length && new Set(order).size === order.length && order.every(i => Number.isInteger(i) && i >= 0 && i < q.choices.length);
  }
  function orderFor(q) {
    const p = progress(), original = q.choices.map((_, i) => i);
    if (p.correctFirst && q.answerIndex !== null) return [q.answerIndex, ...original.filter(i => i !== q.answerIndex)];
    if (!p.shuffleChoices) return original;
    if (!validOrder(p.orders[q.id], q)) { p.orders[q.id] = shuffle(original); persist(); }
    return p.orders[q.id];
  }
  function keepPosition(render) {
    const x = scrollX, y = scrollY;
    $('path').style.overflowAnchor = 'none';
    render();
    window.scrollTo({ left: x, top: y, behavior: 'instant' });
    requestAnimationFrame(() => { $('path').style.overflowAnchor = ''; });
  }
  function render() {
    if (!ready) return;
    const p = progress(), q = current(), record = recordFor(q), done = reviewed(record), studyOnly = q.answerIndex === null;
    const counts = { correct: 0, wrong: 0, skipped: 0, revealed: 0, viewed: 0 };
    for (const question of pool) { const entry = recordFor(question); if (entry) counts[entry.status]++; }
    const count = counts.correct + counts.wrong + counts.revealed + counts.viewed;
    $('pathSummary').textContent = `${count} / ${pool.length} reviewed · ${counts.correct} correct · ${counts.wrong} to retry · ${counts.skipped} skipped`;
    $('pathPosition').textContent = `Question ${p.index + 1} of ${pool.length}`;
    $('pathProgress').style.width = `${pct(count, pool.length)}%`;
    $('pathDomain').textContent = q.domain;
    $('pathSource').textContent = `PDF page ${q.sourcePage} · ${studyOnly ? 'Study only' : 'Checked question'}`;
    $('pathQuestionTitle').textContent = q.question;
    $('pathExhibit').innerHTML = q.exhibit ? `<img src="${esc(q.exhibit)}" alt="Original source figure for question ${p.index + 1}">` : '';
    $('pathChoices').innerHTML = orderFor(q).map((index, position) => {
      const correct = done && !studyOnly && index === q.answerIndex;
      const wrong = done && record.status === 'wrong' && index === record.selected;
      return `<button type="button" data-path-choice="${index}" class="${correct ? 'correct' : ''} ${wrong ? 'wrong' : ''}" ${done || studyOnly ? 'disabled' : ''}><span>${position + 1}</span>${esc(q.choices[index] || `Diagram choice ${String.fromCharCode(65 + index)} — see source figure`)}</button>`;
    }).join('');
    $('pathShuffle').checked = p.shuffleChoices;
    $('pathCorrectFirst').checked = p.correctFirst;
    $('pathExplanations').checked = p.explanations;
    $('pathKeyIdea').checked = p.keyIdea;
    $('pathOrderNote').textContent = p.correctFirst ? 'The checked answer appears first. Study-only items keep their source order or your shuffle setting.' : p.shuffleChoices ? 'The choices are shuffled. Each question keeps its choice order when you return.' : 'The questions and choices keep their source order.';
    $('pathPrevious').disabled = p.index === 0;
    $('pathNext').disabled = p.index === pool.length - 1;
    document.querySelectorAll('[data-path-step]').forEach(button => { button.disabled = Number(button.dataset.pathStep) < 0 ? p.index === 0 : p.index === pool.length - 1; });
    $('pathSkip').disabled = p.index === pool.length - 1;
    $('pathReveal').hidden = done;
    $('pathReveal').textContent = studyOnly ? 'Mark reviewed' : 'Reveal answer';
    $('pathRetry').hidden = !done || studyOnly;
    $('pathJump').max = pool.length;
    $('pathJump').placeholder = `1–${pool.length}`;
    $('pathMapCount').textContent = `${count} reviewed · ${pool.length - count} remaining`;
    $('pathNumbers').innerHTML = pool.map((question, index) => {
      const entry = recordFor(question), status = entry?.status || 'unseen';
      const label = `${index + 1}: ${status}${question.answerIndex === null ? ', study only' : ''}`;
      return `<button type="button" data-path-go="${index}" data-status="${status}" ${index === p.index ? 'aria-current="step"' : ''} aria-label="${label}">${index + 1}</button>`;
    }).join('');
    $('pathFeedback').hidden = !done && !studyOnly;
    if (done || studyOnly) {
      const message = studyOnly ? 'This source item has no single checked answer.' : record.status === 'correct' ? 'Correct — nicely done.' : record.status === 'wrong' ? 'Not quite. Review the idea, then try again.' : 'Answer revealed. Try it from memory next time.';
      const lesson = lessonFor(q);
      $('pathFeedback').className = `game-feedback path-feedback ${record?.status === 'wrong' ? 'wrong' : ''}`;
      $('pathFeedback').innerHTML = `<strong>${message}</strong>${studyOnly ? '<p>This item stays in the path for review. It does not receive a correct or wrong mark.</p>' : `<p><b>${esc(answerLabel(q))}:</b> ${esc(q.choices[q.answerIndex])}</p>`}<div class="path-explanation" ${p.explanations ? '' : 'hidden'}>${answerEvidence(q)}${explanationContent(q, false)}</div>${lesson && !studyOnly ? `<div class="path-key-idea" ${p.keyIdea ? '' : 'hidden'}><b>Key idea</b><p>${esc(lesson[3])}</p></div>` : ''}`;
    }
    updateHome();
  }
  function remember(status, selected = null) {
    const q = current();
    progress().entries[q.id] = { status, selected, key: q.answerIndex, keyText: q.choices[q.answerIndex] || null };
  }
  function choose(index) {
    const q = current();
    if (!q || q.answerIndex === null || reviewed(recordFor(q)) || !Number.isInteger(index) || index < 0 || index >= q.choices.length) return;
    const good = index === q.answerIndex;
    remember(good ? 'correct' : 'wrong', index);
    save(); keepPosition(render); playTone(good ? 'good' : 'bad'); burst(good ? 'good' : 'bad', $('pathChoices'));
  }
  function go(index) {
    if (!Number.isInteger(index) || index < 0 || index >= pool.length) { toast(`Choose a question from 1 to ${pool.length}.`); return; }
    progress().index = index; save(); keepPosition(render);
  }
  document.addEventListener('click', event => {
    if (!ready) return;
    const choice = event.target.closest('[data-path-choice]');
    if (choice) choose(Number(choice.dataset.pathChoice));
    const jump = event.target.closest('[data-path-go]');
    if (jump) go(Number(jump.dataset.pathGo));
    const step = event.target.closest('[data-path-step]');
    if (step) go(progress().index + Number(step.dataset.pathStep));
  });
  $('pathPrevious').addEventListener('click', () => go(progress().index - 1));
  $('pathNext').addEventListener('click', () => go(progress().index + 1));
  $('pathSkip').addEventListener('click', () => { if (!reviewed(recordFor(current()))) remember('skipped'); go(progress().index + 1); });
  $('pathReveal').addEventListener('click', () => { remember(current().answerIndex === null ? 'viewed' : 'revealed'); save(); keepPosition(render); });
  $('pathRetry').addEventListener('click', () => { delete progress().entries[current().id]; save(); keepPosition(render); });
  $('pathJumpForm').addEventListener('submit', event => { event.preventDefault(); go(Number($('pathJump').value) - 1); $('pathJump').blur(); });
  for (const [id, key] of [['pathShuffle', 'shuffleChoices'], ['pathCorrectFirst', 'correctFirst'], ['pathExplanations', 'explanations'], ['pathKeyIdea', 'keyIdea']]) {
    $(id).addEventListener('change', event => { progress()[key] = event.target.checked; if (key === 'shuffleChoices') progress().orders = {}; save(); keepPosition(render); });
  }
  $('pathReset').addEventListener('click', () => {
    if (!confirm('Reset all Practice path answers and return to question 1? Your other rounds and XP stay saved.')) return;
    const p = progress(); p.index = 0; p.entries = {}; p.orders = {};
    $('pathJump').value = ''; save(); keepPosition(render); toast('Practice path reset. Start again at question 1.');
  });
  document.addEventListener('keydown', event => {
    if (!ready || !$('path').classList.contains('active') || event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
    const target = event.target;
    if (target.isContentEditable || target.closest('input,select,textarea,summary') || target.closest('button') && !target.closest('[data-path-choice]')) return;
    const number = Number(event.key);
    if (number >= 1 && number <= 4) { event.preventDefault(); const index = orderFor(current())[number - 1]; if (index !== undefined) choose(index); }
    if (event.key === 'Backspace' || event.key === 'ArrowLeft') { event.preventDefault(); if (progress().index > 0) go(progress().index - 1); }
    if (event.key === 'Enter' || event.key === 'ArrowRight') { event.preventDefault(); if (progress().index < pool.length - 1) go(progress().index + 1); }
  });
  window.TOPCIT_PATH = { init, render, updateHome };
  if (questions.length) init();
})();
