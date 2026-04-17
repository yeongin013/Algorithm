from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class CheckRequest(BaseModel):
    text_a: str
    text_b: str


def compute_lcs(a: str, b: str):
    """Build DP table and backtrack to find LCS."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find the LCS string
    lcs_chars = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            lcs_chars.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    lcs_str = "".join(reversed(lcs_chars))
    return dp, lcs_str


def build_diff(a: str, b: str, dp: list):
    """Generate diff tokens for text A and B using the DP table."""
    diff_a = []
    diff_b = []

    i, j = len(a), len(b)
    path = []

    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            path.append(("match", a[i - 1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            path.append(("added", b[j - 1]))
            j -= 1
        else:
            path.append(("removed", a[i - 1]))
            i -= 1

    path.reverse()

    for kind, ch in path:
        if kind == "match":
            diff_a.append({"type": "matched", "char": ch})
            diff_b.append({"type": "matched", "char": ch})
        elif kind == "removed":
            diff_a.append({"type": "removed", "char": ch})
        else:
            diff_b.append({"type": "added", "char": ch})

    return diff_a, diff_b


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.post("/check")
def check(req: CheckRequest):
    a, b = req.text_a, req.text_b

    if not a and not b:
        return {"similarity": 100.0, "lcs_length": 0, "lcs": "", "diff_a": [], "diff_b": []}

    dp, lcs_str = compute_lcs(a, b)
    lcs_length = len(lcs_str)
    max_len = max(len(a), len(b))
    similarity = round(lcs_length / max_len * 100, 2) if max_len > 0 else 100.0

    diff_a, diff_b = build_diff(a, b, dp)

    return {
        "similarity": similarity,
        "lcs_length": lcs_length,
        "lcs": lcs_str,
        "diff_a": diff_a,
        "diff_b": diff_b,
    }
