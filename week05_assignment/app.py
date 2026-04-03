"""
Classroom Reservation System - Activity Selection Web Application
=================================================================

사용 방법:
  1. 의존성 설치:
       pip install -r requirements.txt

  2. 서버 실행:
       python app.py

  3. 브라우저에서 접속:
       http://localhost:8000

알고리즘 설명 (Greedy Activity Selection):
  - Input  : 예약 요청 목록 (각 요청은 start, end 시간을 가짐)
  - Step 1 : 종료 시간(finish time) 기준으로 오름차순 정렬
  - Step 2 : 첫 번째 이벤트를 선택
  - Step 3 : 이후 이벤트를 순서대로 탐색하며,
             현재까지 선택한 마지막 이벤트의 종료 시간 ≤ 현재 이벤트의 시작 시간
             이면 선택 (겹치지 않는 최대 이벤트 집합)
  - Output : 수용 가능한 최대 예약 집합

API Endpoints:
  GET  /
      - 프론트엔드 페이지(index.html) 제공

  POST /generate
      - 15개의 랜덤 예약 요청 생성
      - Request  JSON : {} (본문 불필요)
      - Response JSON : { "reservations": [ { "id", "name", "start", "end" }, ... ] }

  POST /schedule
      - Greedy Activity Selection 알고리즘으로 최대 비중복 예약 집합 계산
      - Request  JSON : { "reservations": [ { "id", "name", "start", "end" }, ... ] }
      - Response JSON :
          {
            "selected"  : [ { "id", "name", "start", "end" }, ... ],
            "total"     : <int>,
            "count"     : <int>,
            "trace"     : [
                            {
                              "step"     : <int>,
                              "event"    : { "id", "name", "start", "end" },
                              "action"   : "selected" | "skipped",
                              "reason"   : <str>
                            }, ...
                          ]
          }
"""

import random
import string
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# ──────────────────────────────────────────────
# Greedy Activity Selection Algorithm
# ──────────────────────────────────────────────

def activity_selection(reservations: list[dict]) -> dict:
    """
    Greedy Activity Selection 알고리즘.

    Args:
        reservations: [{"id": ..., "name": ..., "start": float, "end": float}, ...]

    Returns:
        {
          "selected": [...],   # 선택된 예약 목록
          "trace"   : [...],   # 단계별 선택 과정
        }
    """
    if not reservations:
        return {"selected": [], "trace": []}

    # 종료 시간 기준 정렬
    sorted_res = sorted(reservations, key=lambda r: (r["end"], r["start"]))

    selected = []
    trace = []
    last_end = -1  # 마지막으로 선택된 이벤트의 종료 시간

    for step, event in enumerate(sorted_res, start=1):
        if event["start"] >= last_end:
            action = "selected"
            if not selected:
                reason = f"첫 번째 이벤트 선택 (종료 시간: {event['end']})"
            else:
                reason = (
                    f"시작({event['start']}) ≥ 이전 종료({last_end}) → 선택 "
                    f"(종료 시간: {event['end']})"
                )
            selected.append(event)
            last_end = event["end"]
        else:
            action = "skipped"
            reason = (
                f"시작({event['start']}) < 이전 종료({last_end}) → 겹침으로 제외"
            )

        trace.append({
            "step"  : step,
            "event" : event,
            "action": action,
            "reason": reason,
        })

    return {"selected": selected, "trace": trace}


# ──────────────────────────────────────────────
# Random reservation generator
# ──────────────────────────────────────────────

_ROOM_NAMES = [
    "Team Meeting", "Workshop", "Lecture", "Seminar", "Interview",
    "Study Group", "Presentation", "Board Meeting", "Training", "Review",
    "Hackathon", "Code Review", "Sprint Planning", "Demo", "Standup",
]

def generate_reservations(n: int = 15) -> list[dict]:
    """0–24 시간 범위에서 n개의 랜덤 예약 요청을 생성한다."""
    reservations = []
    for i in range(n):
        start = round(random.uniform(0, 22), 1)
        duration = round(random.uniform(0.5, 3.0), 1)
        end = round(min(start + duration, 24.0), 1)
        name = random.choice(_ROOM_NAMES) + " " + "".join(
            random.choices(string.ascii_uppercase, k=1)
        )
        reservations.append({
            "id"   : i + 1,
            "name" : name,
            "start": start,
            "end"  : end,
        })
    return reservations


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    reservations = generate_reservations(15)
    return jsonify({"reservations": reservations})


@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.get_json(force=True)
    reservations = data.get("reservations", [])

    if not reservations:
        return jsonify({"error": "예약 목록이 비어 있습니다."}), 400

    result = activity_selection(reservations)
    return jsonify({
        "selected": result["selected"],
        "total"   : len(reservations),
        "count"   : len(result["selected"]),
        "trace"   : result["trace"],
    })


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=8000)
