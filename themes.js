(() => {
  const names = ['dusk', 'midnight', 'forest', 'plum', 'light'];
  let theme = 'dusk';
  try { const saved = localStorage.getItem('topcit-theme'); if (names.includes(saved)) theme = saved; } catch {}
  const apply = name => {
    document.documentElement.dataset.theme = name;
    try { localStorage.setItem('topcit-theme', name); } catch {}
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', name === 'light' ? '#e8edf3' : name === 'midnight' ? '#10141e' : name === 'forest' ? '#13251f' : name === 'plum' ? '#251d32' : '#1c2639');
  };
  apply(theme);
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('themeSelect'); select.value = theme;
    select.addEventListener('change', () => apply(select.value));
  });
})();
