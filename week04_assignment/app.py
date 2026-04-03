"""
Closest Pair of Points Web Application
=======================================

사용 방법:
  1. 의존성 설치:
       pip install -r requirements.txt

  2. 서버 실행:
       python app.py

  3. 브라우저에서 접속:
       http://localhost:8000

API Endpoints:
  GET  /
      - 프론트엔드 페이지(index.html) 제공

  POST /generate
      - n개의 랜덤 2D 점 생성
      - Request  JSON : { "n": <int> }          (2 ≤ n ≤ 1000)
      - Response JSON : { "points": [[x, y], ...] }

  POST /closest-pair
      - Brute Force(O(n²)) 와 Divide & Conquer(O(n log²n)) 두 알고리즘으로
        최근접 점쌍을 탐색하고 실행 시간을 비교하여 반환
      - Request  JSON : { "points": [[x, y], ...] }
      - Response JSON :
          {
            "brute_force"    : { "pair": [[x1,y1],[x2,y2]], "distance": float, "time_ms": float },
            "divide_conquer" : { "pair": [[x1,y1],[x2,y2]], "distance": float, "time_ms": float },
            "speedup"        : float   (brute_force_time / divide_conquer_time)
          }

알고리즘 설명:
  Brute Force
    - 모든 n(n-1)/2 쌍을 순회하여 최소 거리를 구함
    - 시간 복잡도: O(n²)

  Divide & Conquer
    1. 점들을 x좌표 기준으로 정렬
    2. 중앙을 기준으로 LEFT / RIGHT 두 집합으로 분할
    3. 각 집합에서 재귀적으로 최근접 쌍 탐색 → d = min(d_left, d_right)
    4. 분할선 좌우 거리 d 이내의 "strip" 구간에서 최근접 쌍 추가 탐색
    5. 전체 최솟값 반환
    - 시간 복잡도: O(n log²n)
"""

from flask import Flask, request, jsonify, send_from_directory
import random
import math
import time

app = Flask(__name__, static_folder='static')


# ── GET / : 프론트엔드 서빙 ──────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# ── POST /generate : 랜덤 점 생성 ───────────────────────────────────────────

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(force=True)
    n = int(data.get('n', 20))
    n = max(2, min(n, 1000))          # 범위 제한: 2 ~ 1000
    points = [
        [round(random.uniform(20, 780), 2),
         round(random.uniform(20, 580), 2)]
        for _ in range(n)
    ]
    return jsonify({'points': points})


# ── 거리 계산 헬퍼 ────────────────────────────────────────────────────────────

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# ── Brute Force: O(n²) ───────────────────────────────────────────────────────

def brute_force(points):
    min_d = float('inf')
    pair = None
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = dist(points[i], points[j])
            if d < min_d:
                min_d = d
                pair = [points[i], points[j]]
    return min_d, pair


# ── Divide & Conquer: O(n log²n) ─────────────────────────────────────────────

def _strip_closest(strip, d):
    """strip 내 점들(y좌표 정렬 상태) 중 거리 d 미만인 최근접 쌍 탐색"""
    min_d = d
    pair = None
    strip_sorted = sorted(strip, key=lambda p: p[1])
    n = len(strip_sorted)
    for i in range(n):
        j = i + 1
        while j < n and (strip_sorted[j][1] - strip_sorted[i][1]) < min_d:
            d_ij = dist(strip_sorted[i], strip_sorted[j])
            if d_ij < min_d:
                min_d = d_ij
                pair = [strip_sorted[i], strip_sorted[j]]
            j += 1
    return min_d, pair


def _dc_rec(pts):
    """x좌표 정렬된 pts 배열에 대해 재귀적으로 최근접 쌍 반환"""
    n = len(pts)
    if n <= 3:
        return brute_force(pts)

    mid = n // 2
    mid_x = pts[mid][0]

    d_l, p_l = _dc_rec(pts[:mid])
    d_r, p_r = _dc_rec(pts[mid:])

    if d_l <= d_r:
        d, pair = d_l, p_l
    else:
        d, pair = d_r, p_r

    # 분할선 기준 ±d 범위의 strip 구성 후 추가 탐색
    strip = [p for p in pts if abs(p[0] - mid_x) < d]
    d_s, p_s = _strip_closest(strip, d)

    if d_s < d:
        return d_s, p_s
    return d, pair


def divide_and_conquer(points):
    sorted_pts = sorted(points, key=lambda p: p[0])
    return _dc_rec(sorted_pts)


# ── POST /closest-pair : 두 알고리즘 실행 및 결과 반환 ───────────────────────

@app.route('/closest-pair', methods=['POST'])
def closest_pair():
    data = request.get_json(force=True)
    points = data.get('points', [])

    if len(points) < 2:
        return jsonify({'error': 'Need at least 2 points'}), 400

    # Brute Force 실행 시간 측정 (밀리초)
    t0 = time.perf_counter()
    bf_dist, bf_pair = brute_force(points)
    bf_time_ms = (time.perf_counter() - t0) * 1000

    # Divide & Conquer 실행 시간 측정 (밀리초)
    t0 = time.perf_counter()
    dc_dist, dc_pair = divide_and_conquer(points)
    dc_time_ms = (time.perf_counter() - t0) * 1000

    speedup = bf_time_ms / dc_time_ms if dc_time_ms > 0 else float('inf')

    return jsonify({
        'brute_force': {
            'pair':     bf_pair,
            'distance': round(bf_dist, 4),
            'time_ms':  round(bf_time_ms, 4)
        },
        'divide_conquer': {
            'pair':     dc_pair,
            'distance': round(dc_dist, 4),
            'time_ms':  round(dc_time_ms, 4)
        },
        'speedup': round(speedup, 4)
    })


if __name__ == '__main__':
    app.run(debug=True, port=8000)
