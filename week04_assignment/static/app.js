/**
 * app.js
 * Closest Pair of Points — 프론트엔드 로직
 *
 * 담당:
 *  - /generate API 호출 → 랜덤 점 생성
 *  - /closest-pair API 호출 → 두 알고리즘 실행 결과 수신
 *  - Canvas 2D 렌더링 (점, 강조선, 거리 라벨)
 *  - 결과 패널 업데이트
 */

// ── DOM refs ──────────────────────────────────────────────────────────────────
const canvas       = document.getElementById('canvas');
const ctx          = canvas.getContext('2d');
const numInput     = document.getElementById('numPoints');
const btnGenerate  = document.getElementById('btnGenerate');
const btnFind      = document.getElementById('btnFind');
const resultsPanel = document.getElementById('resultsPanel');
const hint         = document.getElementById('hint');

const bfDistEl  = document.getElementById('bfDist');
const bfTimeEl  = document.getElementById('bfTime');
const dcDistEl  = document.getElementById('dcDist');
const dcTimeEl  = document.getElementById('dcTime');
const speedupEl = document.getElementById('speedup');
const pairEl    = document.getElementById('pairCoords');

// ── State ─────────────────────────────────────────────────────────────────────
let points      = [];    // [[x, y], ...]
let closestPair = null;  // [[x1,y1],[x2,y2]]

// ── Canvas sizing ─────────────────────────────────────────────────────────────
function resizeCanvas() {
  const wrap = canvas.parentElement;
  const size = Math.min(wrap.clientWidth - 48, wrap.clientHeight - 48);
  canvas.width  = size;
  canvas.height = size * 0.75;
  redraw();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// ── Drawing ───────────────────────────────────────────────────────────────────

function redraw() {
  const W = canvas.width;
  const H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  if (points.length === 0) return;

  const scaleX = W / 800;
  const scaleY = H / 600;

  // 일반 점
  points.forEach(p => drawDot(p[0] * scaleX, p[1] * scaleY, 4, '#4f8ef7', 0.85));

  // 최근접 쌍 강조
  if (closestPair) {
    const [p1, p2] = closestPair;
    const x1 = p1[0] * scaleX, y1 = p1[1] * scaleY;
    const x2 = p2[0] * scaleX, y2 = p2[1] * scaleY;

    // 연결선 (점선)
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = '#f76f4f';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // 강조 점
    drawDot(x1, y1, 7, '#f76f4f', 1);
    drawDot(x2, y2, 7, '#f76f4f', 1);

    // 거리 라벨 (선 중간)
    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    const d  = Math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2).toFixed(2);
    ctx.font      = 'bold 12px monospace';
    ctx.fillStyle = '#f76f4f';
    ctx.textAlign = 'center';
    ctx.fillText('d = ' + d, mx, my - 10);
  }
}

function drawDot(x, y, r, color, alpha) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.restore();
}

// ── Button: Generate Random ───────────────────────────────────────────────────
btnGenerate.addEventListener('click', async () => {
  const n = parseInt(numInput.value, 10);
  if (isNaN(n) || n < 2) { alert('n은 2 이상이어야 합니다.'); return; }

  btnGenerate.disabled = true;
  btnGenerate.textContent = 'Generating...';

  try {
    const res  = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ n })
    });
    const data = await res.json();
    points      = data.points;
    closestPair = null;

    resultsPanel.classList.add('hidden');
    hint.textContent   = points.length + '개 점 생성 완료. Find Closest Pair를 실행하세요.';
    hint.style.display = 'block';

    redraw();
    btnFind.disabled = false;
  } catch (e) {
    alert('점 생성 중 오류 발생: ' + e.message);
  } finally {
    btnGenerate.disabled = false;
    btnGenerate.textContent = 'Generate Random';
  }
});

// ── Button: Find Closest Pair ─────────────────────────────────────────────────
btnFind.addEventListener('click', async () => {
  if (points.length < 2) return;

  btnFind.disabled = true;
  btnFind.textContent = 'Running...';

  try {
    const res  = await fetch('/closest-pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ points })
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }

    const bf = data.brute_force;
    const dc = data.divide_conquer;

    bfDistEl.textContent = bf.distance.toFixed(4);
    bfTimeEl.textContent = bf.time_ms.toFixed(4) + ' ms';
    dcDistEl.textContent = dc.distance.toFixed(4);
    dcTimeEl.textContent = dc.time_ms.toFixed(4) + ' ms';
    speedupEl.textContent = isFinite(data.speedup)
      ? data.speedup.toFixed(3) + 'x'
      : '∞x';

    // 좌표 표시 — textContent로 안전하게 삽입
    const [p1, p2] = dc.pair;
    const line1 = document.createElement('div');
    const line2 = document.createElement('div');
    line1.textContent = 'P1: (' + p1[0].toFixed(2) + ', ' + p1[1].toFixed(2) + ')';
    line2.textContent = 'P2: (' + p2[0].toFixed(2) + ', ' + p2[1].toFixed(2) + ')';
    pairEl.replaceChildren(line1, line2);

    closestPair = dc.pair;
    resultsPanel.classList.remove('hidden');
    hint.style.display = 'none';

    redraw();
  } catch (e) {
    alert('알고리즘 실행 중 오류 발생: ' + e.message);
  } finally {
    btnFind.disabled = false;
    btnFind.textContent = 'Find Closest Pair';
  }
});
