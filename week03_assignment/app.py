from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import time
import random

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


# ── Models ────────────────────────────────────────────────────────────────────

class Song(BaseModel):
    id: int
    title: str
    artist: str
    duration: int       # seconds
    play_count: int


class SortRequest(BaseModel):
    songs: List[Song]
    algorithm: str      # "selection" | "insertion" | "merge"
    criterion: str      # "title" | "artist" | "duration" | "play_count"


class GenerateRequest(BaseModel):
    n: int


# ── Sorting Algorithms ────────────────────────────────────────────────────────

def _key(song: dict, criterion: str):
    val = song[criterion]
    return val.lower() if isinstance(val, str) else val


def selection_sort(arr: list, criterion: str):
    arr = [s.copy() for s in arr]
    n = len(arr)
    comparisons = swaps = 0
    t0 = time.perf_counter()

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if _key(arr[j], criterion) < _key(arr[min_idx], criterion):
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1

    elapsed = (time.perf_counter() - t0) * 1000
    return arr, comparisons, swaps, elapsed


def insertion_sort(arr: list, criterion: str):
    arr = [s.copy() for s in arr]
    n = len(arr)
    comparisons = swaps = 0
    t0 = time.perf_counter()

    for i in range(1, n):
        key_song = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if _key(arr[j], criterion) > _key(key_song, criterion):
                arr[j + 1] = arr[j]
                swaps += 1
                j -= 1
            else:
                break
        arr[j + 1] = key_song

    elapsed = (time.perf_counter() - t0) * 1000
    return arr, comparisons, swaps, elapsed


def merge_sort(arr: list, criterion: str):
    arr = [s.copy() for s in arr]
    stats = {"comparisons": 0, "swaps": 0}

    def merge(left, right):
        result, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            stats["comparisons"] += 1
            if _key(left[i], criterion) <= _key(right[j], criterion):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
            stats["swaps"] += 1
        remaining = left[i:] + right[j:]
        stats["swaps"] += len(remaining)
        return result + remaining

    def _sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        return merge(_sort(a[:mid]), _sort(a[mid:]))

    t0 = time.perf_counter()
    result = _sort(arr)
    elapsed = (time.perf_counter() - t0) * 1000
    return result, stats["comparisons"], stats["swaps"], elapsed


ALGORITHMS = {
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge":     merge_sort,
}


# ── Song Generator ────────────────────────────────────────────────────────────

ADJECTIVES = [
    "Electric", "Silent", "Golden", "Neon", "Cosmic", "Broken", "Burning",
    "Crystal", "Digital", "Faded", "Frozen", "Hollow", "Lonely", "Midnight",
    "Painted", "Runaway", "Sacred", "Shining", "Silver", "Velvet",
    "Ancient", "Arctic", "Blazing", "Blazing", "Blinding", "Blissful",
    "Boundless", "Brilliant", "Calm", "Celestial", "Chaotic", "Colorful",
    "Crimson", "Dazzling", "Distant", "Divine", "Dreamy", "Dusky",
    "Echoing", "Endless", "Eternal", "Ethereal", "Fearless", "Fierce",
    "Fleeting", "Floating", "Glowing", "Graceful", "Haunting", "Heavy",
    "Hidden", "Infinite", "Invisible", "Jade", "Jealous", "Joyful",
    "Lazy", "Liquid", "Lost", "Luminous", "Magnetic", "Mellow",
    "Misty", "Mystic", "Nameless", "Obscure", "Pale", "Peaceful",
    "Phantom", "Quiet", "Radiant", "Restless", "Rising", "Rustic",
    "Scattered", "Serene", "Shadowy", "Sleepy", "Smoky", "Soft",
    "Solemn", "Spinning", "Stormy", "Strange", "Surreal", "Tender",
    "Timeless", "Twilight", "Twisted", "Vibrant", "Violent", "Wandering",
    "Warm", "Wild", "Winding", "Withered", "Wondrous",
]
ADJECTIVES = list(dict.fromkeys(ADJECTIVES))  # deduplicate, preserve order

NOUNS = [
    "Heart", "Dream", "Fire", "Rain", "Sky", "Road", "Night", "Soul", "Wave",
    "Star", "Wind", "Light", "Storm", "River", "City", "Shadow", "Voice",
    "Moon", "Echo", "Sunset",
    "Arrow", "Ash", "Aurora", "Abyss", "Beacon", "Bell", "Blade", "Bloom",
    "Bone", "Bridge", "Cage", "Canyon", "Chain", "Clock", "Cloud", "Code",
    "Comet", "Crown", "Cure", "Curse", "Dagger", "Dance", "Dark", "Dawn",
    "Decay", "Desire", "Dust", "Edge", "Ember", "Empire", "End", "Exile",
    "Eye", "Fable", "Fall", "Fate", "Fault", "Feather", "Field", "Flame",
    "Flood", "Flower", "Fog", "Forest", "Gate", "Ghost", "Glass", "Glory",
    "Gold", "Ground", "Harbor", "Heaven", "Hill", "Hope", "Hour", "Ice",
    "Island", "Journey", "Key", "Kingdom", "Knife", "Lake", "Leaf", "Legacy",
    "Lie", "Map", "Mark", "Memory", "Mirror", "Mist", "Mountain", "Myth",
    "Name", "Ocean", "Path", "Peak", "Petal", "Place", "Plea", "Pride",
    "Promise", "Pulse", "Ruin", "Scar", "Sea", "Secret", "Seed", "Shore",
    "Signal", "Silence", "Smoke", "Snow", "Song", "Space", "Spark", "Spell",
    "Spirit", "Spring", "Stone", "Tear", "Thunder", "Tide", "Time", "Tower",
    "Trail", "Truth", "Valley", "Veil", "Void", "Walls", "War", "Water",
]
NOUNS = list(dict.fromkeys(NOUNS))
FIRST_NAMES = [
    "Alex", "Blake", "Casey", "Dana", "Evan", "Finn", "Grace", "Harper",
    "Iris", "Jordan", "Kai", "Luna", "Morgan", "Nova", "Owen", "Phoenix",
    "Quinn", "River", "Sage", "Taylor",
]
LAST_NAMES = [
    "Smith", "Novak", "Rivera", "Chen", "Park", "Patel", "Kim", "Jones",
    "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris",
]


def generate_songs(n: int) -> list:
    songs = []
    used_titles: set = set()
    for i in range(n):
        while True:
            title = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
            if title not in used_titles:
                used_titles.add(title)
                break
        artist     = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        duration   = random.randint(120, 360)
        play_count = random.randint(0, 1_000_000)
        songs.append({
            "id": i + 1,
            "title": title,
            "artist": artist,
            "duration": duration,
            "play_count": play_count,
        })
    return songs


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/generate")
def generate(req: GenerateRequest):
    n = max(1, min(req.n, 5_000))
    return {"songs": generate_songs(n)}


@app.post("/sort")
def sort_playlist(req: SortRequest):
    songs = [s.model_dump() for s in req.songs]
    fn = ALGORITHMS.get(req.algorithm)
    if fn is None:
        return {"error": "Unknown algorithm"}
    sorted_songs, comparisons, swaps, elapsed = fn(songs, req.criterion)
    return {
        "sorted":      sorted_songs,
        "comparisons": comparisons,
        "swaps":       swaps,
        "time_ms":     round(elapsed, 4),
        "algorithm":   req.algorithm,
        "criterion":   req.criterion,
    }


@app.post("/compare")
def compare_all(req: SortRequest):
    songs = [s.model_dump() for s in req.songs]
    results = {}
    for name, fn in ALGORITHMS.items():
        _, comparisons, swaps, elapsed = fn(songs, req.criterion)
        results[name] = {
            "comparisons": comparisons,
            "swaps":       swaps,
            "time_ms":     round(elapsed, 4),
        }
    return results
