from flask import Flask, request, jsonify, send_from_directory
import time
import bisect
import os

app = Flask(__name__, static_folder='static')

# ---------------------------------------------------------------------------
# Word list loading
# ---------------------------------------------------------------------------
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
WORD_FILE = os.path.join(BASE_DIR, 'words.txt')

def load_words(path: str) -> list[str]:
    """Load words (one per line, already sorted and lowercased)."""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

print("Loading word list...")
WORDS: list[str] = load_words(WORD_FILE)
print(f"Loaded {len(WORDS):,} words")

# ---------------------------------------------------------------------------
# Search algorithms
# ---------------------------------------------------------------------------
MAX_RESULTS = 20

def linear_search(words: list[str], prefix: str) -> tuple[list[str], float]:
    """
    Scan every word sequentially and collect those starting with *prefix*.
    Time complexity: O(n)
    """
    prefix = prefix.lower()
    start = time.perf_counter()

    results: list[str] = []
    for word in words:
        if word.startswith(prefix):
            results.append(word)
            if len(results) >= MAX_RESULTS:
                break

    elapsed_ms = (time.perf_counter() - start) * 1_000
    return results, elapsed_ms


def binary_search(words: list[str], prefix: str) -> tuple[list[str], float]:
    """
    Use binary search to find the range [lo, hi) of words that start with
    *prefix*, then slice at most MAX_RESULTS from that range.
    Time complexity: O(log n + k)  where k = number of matches returned
    """
    prefix = prefix.lower()
    start = time.perf_counter()

    # Left boundary: first word >= prefix
    lo = bisect.bisect_left(words, prefix)

    # Right boundary: first word >= prefix's "next sibling"
    # Increment the last character by 1 to get the exclusive upper bound
    if prefix:
        prefix_end = prefix[:-1] + chr(ord(prefix[-1]) + 1)
        hi = bisect.bisect_left(words, prefix_end)
    else:
        hi = len(words)

    results = words[lo : lo + MAX_RESULTS] if lo < hi else []

    elapsed_ms = (time.perf_counter() - start) * 1_000
    return results, elapsed_ms

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.route('/search/linear')
def search_linear():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'query': q, 'results': [], 'time_ms': 0, 'total_words': len(WORDS)})

    results, elapsed = linear_search(WORDS, q)
    return jsonify({
        'query': q,
        'results': results,
        'time_ms': round(elapsed, 4),
        'total_words': len(WORDS),
        'algorithm': 'Linear Search',
        'complexity': 'O(n)',
    })


@app.route('/search/binary')
def search_binary():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'query': q, 'results': [], 'time_ms': 0, 'total_words': len(WORDS)})

    results, elapsed = binary_search(WORDS, q)
    return jsonify({
        'query': q,
        'results': results,
        'time_ms': round(elapsed, 4),
        'total_words': len(WORDS),
        'algorithm': 'Binary Search',
        'complexity': 'O(log n)',
    })


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
