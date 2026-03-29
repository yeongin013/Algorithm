/* ── DOM references ─────────────────────────────────────────── */
const searchInput    = document.getElementById('searchInput');
const wordCountEl    = document.getElementById('wordCount');
const statsBar       = document.getElementById('statsBar');
const linearTimeEl   = document.getElementById('linearTime');
const binaryTimeEl   = document.getElementById('binaryTime');
const speedupRatioEl = document.getElementById('speedupRatio');
const linearListEl   = document.getElementById('linearResults');
const binaryListEl   = document.getElementById('binaryResults');
const totalWordsLinearEl = document.getElementById('totalWordsLinear');

/* ── State ───────────────────────────────────────────────────── */
let debounceTimer = null;
let totalWords    = 0;

/* ── Helpers ─────────────────────────────────────────────────── */

/** Remove all child nodes from an element safely (no innerHTML). */
function clearElement(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

/**
 * Build a list item that bolds the matched prefix using safe DOM methods.
 * @param {string} word
 * @param {string} prefix
 * @param {string} highlightClass  CSS class for the bolded part
 */
function buildListItem(word, prefix, highlightClass) {
  const li = document.createElement('li');
  if (prefix && word.toLowerCase().startsWith(prefix.toLowerCase())) {
    const bold = document.createElement('span');
    bold.className = `highlight ${highlightClass}`;
    bold.textContent = word.slice(0, prefix.length);
    li.appendChild(bold);
    li.appendChild(document.createTextNode(word.slice(prefix.length)));
  } else {
    li.textContent = word;
  }
  return li;
}

function makePlaceholder(text, cssClass) {
  const li = document.createElement('li');
  li.className = cssClass;
  li.textContent = text;
  return li;
}

function renderResults(listEl, data, highlightClass) {
  clearElement(listEl);
  if (!data.results || data.results.length === 0) {
    listEl.appendChild(makePlaceholder('No results found.', 'no-results'));
    return;
  }
  const fragment = document.createDocumentFragment();
  data.results.forEach(word => {
    fragment.appendChild(buildListItem(word, data.query, highlightClass));
  });
  listEl.appendChild(fragment);
}

function formatMs(ms) {
  if (ms < 0.01) return '<0.01 ms';
  return ms.toFixed(3) + ' ms';
}

function updateStats(linearData, binaryData) {
  const lt = linearData.time_ms;
  const bt = binaryData.time_ms;

  linearTimeEl.textContent = formatMs(lt);
  binaryTimeEl.textContent = formatMs(bt);

  if (bt > 0) {
    const ratio = lt / bt;
    speedupRatioEl.textContent = ratio.toFixed(1) + '\u00d7';
  } else {
    speedupRatioEl.textContent = '\u2014';
  }

  statsBar.classList.remove('hidden');
}

/* ── Fetch both endpoints in parallel ───────────────────────── */
async function runSearch(query) {
  if (!query) {
    resetUI();
    return;
  }

  const [linearResp, binaryResp] = await Promise.all([
    fetch(`/search/linear?q=${encodeURIComponent(query)}`),
    fetch(`/search/binary?q=${encodeURIComponent(query)}`),
  ]);

  const [linearData, binaryData] = await Promise.all([
    linearResp.json(),
    binaryResp.json(),
  ]);

  // Update total word count once
  if (linearData.total_words && !totalWords) {
    totalWords = linearData.total_words;
    wordCountEl.textContent = `${totalWords.toLocaleString()} words loaded`;
    if (totalWordsLinearEl) totalWordsLinearEl.textContent = totalWords.toLocaleString();
  }

  renderResults(linearListEl, linearData, 'linear-highlight');
  renderResults(binaryListEl, binaryData, 'binary-highlight');
  updateStats(linearData, binaryData);
}

function resetUI() {
  statsBar.classList.add('hidden');

  clearElement(linearListEl);
  linearListEl.appendChild(makePlaceholder('Start typing to see results\u2026', 'placeholder'));

  clearElement(binaryListEl);
  binaryListEl.appendChild(makePlaceholder('Start typing to see results\u2026', 'placeholder'));
}

/* ── Input event with debounce (150 ms) ─────────────────────── */
searchInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  const query = searchInput.value.trim();
  debounceTimer = setTimeout(() => runSearch(query), 150);
});

/* ── Init: fetch word count ──────────────────────────────────── */
(async () => {
  try {
    const res  = await fetch('/search/linear?q=');
    const data = await res.json();
    if (data.total_words) {
      totalWords = data.total_words;
      wordCountEl.textContent = `${totalWords.toLocaleString()} words loaded`;
      if (totalWordsLinearEl) totalWordsLinearEl.textContent = totalWords.toLocaleString();
    }
  } catch (_) {
    wordCountEl.textContent = 'Word list ready';
  }
})();
