/* ── State ─────────────────────────────────────────────────────────────────── */
let playlist = [];

/* ── DOM refs ──────────────────────────────────────────────────────────────── */
const nSongsInput    = document.getElementById('nSongs');
const btnGenerate    = document.getElementById('btnGenerate');
const btnSort        = document.getElementById('btnSort');
const btnCompare     = document.getElementById('btnCompare');
const criterionSel   = document.getElementById('criterion');
const algorithmSel   = document.getElementById('algorithm');
const playlistBody   = document.getElementById('playlistBody');
const songCountBadge = document.getElementById('songCount');
const sortMetrics    = document.getElementById('sortMetrics');
const compareMetrics = document.getElementById('compareMetrics');

/* ── Helpers ───────────────────────────────────────────────────────────────── */
function formatDuration(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function formatNum(n) {
  return n.toLocaleString();
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function setLoading(btn, loading) {
  if (loading) {
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span>Loading…';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.orig || btn.innerHTML;
    btn.disabled = false;
  }
}

function algorithmLabel(name) {
  return {
    selection: 'Selection Sort',
    insertion: 'Insertion Sort',
    merge:     'Merge Sort',
  }[name] || name;
}

function algorithmComplexity(name) {
  return {
    selection: 'O(n²)',
    insertion: 'O(n²)',
    merge:     'O(n log n)',
  }[name] || '—';
}

function criterionLabel(name) {
  return {
    title:      'Title',
    artist:     'Artist',
    duration:   'Duration',
    play_count: 'Play Count',
  }[name] || name;
}

/* ── Render playlist ───────────────────────────────────────────────────────── */
function renderPlaylist(songs) {
  playlist = songs;
  songCountBadge.textContent = `${songs.length} song${songs.length !== 1 ? 's' : ''}`;

  if (songs.length === 0) {
    playlistBody.innerHTML =
      '<tr><td colspan="5" class="empty">No songs yet — generate a playlist to get started.</td></tr>';
    return;
  }

  playlistBody.innerHTML = songs
    .map((s, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${escHtml(s.title)}</td>
        <td>${escHtml(s.artist)}</td>
        <td>${formatDuration(s.duration)}</td>
        <td>${formatNum(s.play_count)}</td>
      </tr>`)
    .join('');
}

/* ── Generate ──────────────────────────────────────────────────────────────── */
btnGenerate.addEventListener('click', async () => {
  let n = Math.max(1, parseInt(nSongsInput.value, 10) || 20);
  if (n > 5000) {
    n = 5000;
    nSongsInput.value = 5000;
  }
  setLoading(btnGenerate, true);
  try {
    const res  = await fetch('/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ n }),
    });
    const data = await res.json();
    renderPlaylist(data.songs);
    sortMetrics.classList.add('hidden');
    compareMetrics.classList.add('hidden');
  } catch (e) {
    alert('Error generating playlist: ' + e.message);
  } finally {
    setLoading(btnGenerate, false);
  }
});

/* ── Sort ──────────────────────────────────────────────────────────────────── */
btnSort.addEventListener('click', async () => {
  if (playlist.length === 0) { alert('Generate a playlist first!'); return; }
  setLoading(btnSort, true);
  try {
    const res  = await fetch('/sort', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        songs:     playlist,
        algorithm: algorithmSel.value,
        criterion: criterionSel.value,
      }),
    });
    const data = await res.json();

    renderPlaylist(data.sorted);

    document.getElementById('mAlgorithm').textContent   = algorithmLabel(data.algorithm);
    document.getElementById('mCriterion').textContent   = criterionLabel(data.criterion);
    document.getElementById('mComparisons').textContent = formatNum(data.comparisons);
    document.getElementById('mSwaps').textContent       = formatNum(data.swaps);
    document.getElementById('mTime').textContent        = data.time_ms.toFixed(4);

    sortMetrics.classList.remove('hidden');
    compareMetrics.classList.add('hidden');
  } catch (e) {
    alert('Error sorting: ' + e.message);
  } finally {
    setLoading(btnSort, false);
  }
});

/* ── Compare All ───────────────────────────────────────────────────────────── */
btnCompare.addEventListener('click', async () => {
  if (playlist.length === 0) { alert('Generate a playlist first!'); return; }
  setLoading(btnCompare, true);
  try {
    const res  = await fetch('/compare', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        songs:     playlist,
        algorithm: algorithmSel.value,   // required by schema, ignored server-side
        criterion: criterionSel.value,
      }),
    });
    const data = await res.json();
    renderCompareTable(data);

    sortMetrics.classList.add('hidden');
    compareMetrics.classList.remove('hidden');
  } catch (e) {
    alert('Error comparing: ' + e.message);
  } finally {
    setLoading(btnCompare, false);
  }
});

/* ── Compare table renderer ────────────────────────────────────────────────── */
function renderCompareTable(data) {
  const names   = Object.keys(data);
  const minTime = Math.min(...names.map(n => data[n].time_ms));
  const minCmp  = Math.min(...names.map(n => data[n].comparisons));
  const minSwap = Math.min(...names.map(n => data[n].swaps));

  document.getElementById('compareBody').innerHTML = names
    .map(name => {
      const d = data[name];
      const cmpClass  = d.comparisons === minCmp  ? ' class="best"' : '';
      const swapClass = d.swaps       === minSwap ? ' class="best"' : '';
      const timeClass = d.time_ms     === minTime ? ' class="best"' : '';
      return `
        <tr>
          <td>${algorithmLabel(name)}</td>
          <td><span class="complexity">${algorithmComplexity(name)}</span></td>
          <td${cmpClass}>${formatNum(d.comparisons)}</td>
          <td${swapClass}>${formatNum(d.swaps)}</td>
          <td${timeClass}>${d.time_ms.toFixed(4)}</td>
        </tr>`;
    })
    .join('');
}
