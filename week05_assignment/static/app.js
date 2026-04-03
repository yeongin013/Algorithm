/* ── State ──────────────────────────────────────────────── */
let reservations = [];   // { id, name, start, end }
let nextId = 1;

const TL_START = 0;
const TL_END   = 24;

/* ── DOM refs ────────────────────────────────────────────── */
const addForm        = document.getElementById("add-form");
const inpName        = document.getElementById("inp-name");
const inpStart       = document.getElementById("inp-start");
const inpEnd         = document.getElementById("inp-end");
const resList        = document.getElementById("reservation-list");
const totalCount     = document.getElementById("total-count");
const btnSchedule    = document.getElementById("btn-schedule");
const btnGenerate    = document.getElementById("btn-generate");
const btnClear       = document.getElementById("btn-clear");
const resultStat     = document.getElementById("result-stat");
const timeline       = document.getElementById("timeline");
const timelineAxis   = document.getElementById("timeline-axis");
const traceList      = document.getElementById("trace-list");

/* ── Security: HTML escape ───────────────────────────────── */
function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ── Helpers ─────────────────────────────────────────────── */
function fmt(h) {
  const hh = Math.floor(h);
  const mm = Math.round((h - hh) * 60);
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function pct(h) {
  return ((h - TL_START) / (TL_END - TL_START)) * 100;
}

function updateCount() {
  totalCount.textContent = `${reservations.length} reservation${reservations.length !== 1 ? "s" : ""}`;
  btnSchedule.disabled = reservations.length === 0;
}

/* ── Render reservation list ─────────────────────────────── */
function renderList() {
  if (reservations.length === 0) {
    resList.innerHTML = '<p class="empty-msg">No reservations yet. Add one or click "Generate Random".</p>';
    updateCount();
    return;
  }
  resList.innerHTML = reservations
    .map(r => `
      <div class="res-item" data-id="${esc(r.id)}">
        <span class="res-name" title="${esc(r.name)}">${esc(r.name)}</span>
        <span class="res-time">${fmt(r.start)} &ndash; ${fmt(r.end)}</span>
        <button class="res-del secondary" data-del="${esc(r.id)}">&#10005;</button>
      </div>`)
    .join("");

  // attach delete handlers via event delegation (avoids inline onclick)
  resList.querySelectorAll("[data-del]").forEach(btn => {
    btn.addEventListener("click", () => deleteReservation(Number(btn.dataset.del)));
  });

  updateCount();
}

function deleteReservation(id) {
  reservations = reservations.filter(r => r.id !== id);
  renderList();
}

/* ── Add reservation ─────────────────────────────────────── */
addForm.addEventListener("submit", e => {
  e.preventDefault();
  const name  = inpName.value.trim();
  const start = parseFloat(inpStart.value);
  const end   = parseFloat(inpEnd.value);

  if (!name) return alert("이벤트 이름을 입력하세요.");
  if (isNaN(start) || isNaN(end)) return alert("시작/종료 시간을 입력하세요.");
  if (start >= end) return alert("시작 시간은 종료 시간보다 앞이어야 합니다.");
  if (start < 0 || end > 24) return alert("시간 범위는 0~24 사이여야 합니다.");

  reservations.push({ id: nextId++, name, start, end });
  renderList();
  inpName.value = inpStart.value = inpEnd.value = "";
  inpName.focus();
});

/* ── Generate random ─────────────────────────────────────── */
btnGenerate.addEventListener("click", async () => {
  btnGenerate.disabled = true;
  try {
    const res = await fetch("/generate", { method: "POST" });
    const data = await res.json();
    reservations = data.reservations.map(r => ({ ...r, id: nextId++ }));
    renderList();
    clearResults();
  } catch {
    alert("서버 오류가 발생했습니다.");
  } finally {
    btnGenerate.disabled = false;
  }
});

/* ── Clear ───────────────────────────────────────────────── */
btnClear.addEventListener("click", () => {
  reservations = [];
  renderList();
  clearResults();
});

/* ── Schedule ────────────────────────────────────────────── */
btnSchedule.addEventListener("click", async () => {
  if (reservations.length === 0) return;
  btnSchedule.disabled = true;
  btnSchedule.textContent = "Scheduling…";

  try {
    const res  = await fetch("/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reservations }),
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    renderResults(data);
  } catch {
    alert("서버 오류가 발생했습니다.");
  } finally {
    btnSchedule.disabled = false;
    btnSchedule.textContent = "Schedule ▶";
  }
});

/* ── Render results ──────────────────────────────────────── */
function clearResults() {
  resultStat.textContent = "";
  timeline.innerHTML     = '<p class="placeholder">Run "Schedule" to see the timeline.</p>';
  timelineAxis.innerHTML = "";
  traceList.innerHTML    = '<p class="placeholder">Run "Schedule" to see the step-by-step trace.</p>';
}

function renderResults({ selected, total, count, trace }) {
  /* stat */
  resultStat.textContent = `\u2713 ${count} selected / ${total} total`;

  /* timeline axis */
  const axisSteps = [0, 3, 6, 9, 12, 15, 18, 21, 24];
  timelineAxis.innerHTML = axisSteps.map(h => `<span>${fmt(h)}</span>`).join("");

  /* timeline bars */
  const selectedIds = new Set(selected.map(r => r.id));
  const sorted = [...reservations].sort((a, b) => a.start - b.start);

  timeline.innerHTML = sorted.map(r => {
    const left  = pct(r.start).toFixed(2);
    const width = Math.max(pct(r.end) - pct(r.start), 1).toFixed(2);
    const cls   = selectedIds.has(r.id) ? "selected" : "all";
    const label = `${esc(r.name)} (${fmt(r.start)}&ndash;${fmt(r.end)})`;
    return `
      <div class="tl-row">
        <div class="tl-bar ${cls}"
             style="left:${left}%; width:${width}%;"
             title="${esc(r.name)} (${fmt(r.start)}-${fmt(r.end)})">${label}</div>
      </div>`;
  }).join("");

  /* trace */
  traceList.innerHTML = trace.map(t => `
    <div class="trace-item">
      <div class="trace-step ${t.action}">${esc(t.step)}</div>
      <div class="trace-body">
        <div class="trace-event">
          ${esc(t.event.name)}
          <span class="t-time">${fmt(t.event.start)} &ndash; ${fmt(t.event.end)}</span>
          <span class="badge ${t.action === "selected" ? "selected" : "skipped"}">${t.action === "selected" ? "Selected" : "Skipped"}</span>
        </div>
        <div class="trace-reason">${esc(t.reason)}</div>
      </div>
    </div>`).join("");
}

/* ── Init ────────────────────────────────────────────────── */
clearResults();
updateCount();
