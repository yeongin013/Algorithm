/* ── State ──────────────────────────────────────────────────── */
let activeMethod = 'id'; // 'id' | 'name'

/* ── DOM refs ───────────────────────────────────────────────── */
const searchInput   = document.getElementById('search-input');
const searchBtn     = document.getElementById('search-btn');
const dupBtn        = document.getElementById('dup-btn');
const tabs          = document.querySelectorAll('.tab');
const statsBar      = document.getElementById('stats-bar');
const statMethod    = document.getElementById('stat-method');
const statTime      = document.getElementById('stat-time');
const statCount     = document.getElementById('stat-count');
const resultsGrid   = document.getElementById('results-grid');
const noResults     = document.getElementById('no-results');
const spinner       = document.getElementById('spinner');

/* ── Tab switching ──────────────────────────────────────────── */
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    activeMethod = tab.dataset.method;

    searchInput.placeholder =
      activeMethod === 'id' ? 'Enter product ID (1–1000)…' : 'Enter product name keyword…';
    searchInput.value = '';
    clearResults();
  });
});

/* ── Search button ──────────────────────────────────────────── */
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleSearch(); });

async function handleSearch() {
  const query = searchInput.value.trim();
  if (!query) return;

  const url = activeMethod === 'id'
    ? `/search/id?id=${encodeURIComponent(query)}`
    : `/search/name?q=${encodeURIComponent(query)}`;

  await fetchAndRender(url, false);
}

/* ── Duplicates button ──────────────────────────────────────── */
dupBtn.addEventListener('click', () => fetchAndRender('/search/duplicates', true));

/* ── Core fetch + render ────────────────────────────────────── */
async function fetchAndRender(url, isDuplicate) {
  setLoading(true);
  clearResults();

  try {
    const res  = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    showStats(data.method, data.time_ms, data.count);
    renderCards(data.results, isDuplicate);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

/* ── Render product cards ───────────────────────────────────── */
function renderCards(products, isDuplicate) {
  if (!products || products.length === 0) {
    noResults.classList.remove('hidden');
    return;
  }

  const fragment = document.createDocumentFragment();

  products.forEach(p => {
    const card = document.createElement('div');
    card.className = 'product-card' + (isDuplicate ? ' dup-card' : '');
    card.innerHTML = `
      <div class="pid">#${p.id}</div>
      <div class="pname">${escHtml(p.name)}</div>
      <span class="pcategory">${escHtml(p.category)}</span>
      <div class="pprice">$${p.price.toFixed(2)}</div>
    `;
    fragment.appendChild(card);
  });

  resultsGrid.appendChild(fragment);
}

/* ── Stats bar ──────────────────────────────────────────────── */
function showStats(method, timeMs, count) {
  statMethod.textContent = method;
  statTime.textContent   = `${timeMs.toFixed(3)} ms`;
  statCount.textContent  = `${count} result${count !== 1 ? 's' : ''}`;
  statsBar.classList.remove('hidden');
}

/* ── Helpers ────────────────────────────────────────────────── */
function setLoading(on) {
  spinner.classList.toggle('hidden', !on);
  searchBtn.disabled = on;
  dupBtn.disabled    = on;
}

function clearResults() {
  resultsGrid.innerHTML = '';
  noResults.classList.add('hidden');
  statsBar.classList.add('hidden');
}

function showError(msg) {
  noResults.textContent = `Error: ${msg}`;
  noResults.classList.remove('hidden');
}

function escHtml(str) {
  return str.replace(/[&<>"']/g, c =>
    ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])
  );
}
