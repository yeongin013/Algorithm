import time
import random
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Shopping Mall API")

# ── Generate 1000+ products ───────────────────────────────────────────────────
CATEGORIES = ["Electronics", "Clothing", "Books", "Home & Garden",
               "Sports", "Toys", "Food", "Beauty"]

PRODUCT_NAMES = [
    "Laptop", "Phone", "Tablet", "Camera", "Headphones", "Speaker",
    "Smartwatch", "TV", "Monitor", "Keyboard", "Mouse", "Charger",
    "T-Shirt", "Jeans", "Dress", "Shoes", "Jacket", "Bag", "Hat", "Socks",
    "Python Book", "Algorithm Book", "Novel", "Magazine", "Textbook", "Comic",
    "Chair", "Desk", "Lamp", "Pillow", "Blanket", "Vase", "Clock", "Shelf",
    "Yoga Mat", "Dumbbell", "Tennis Racket", "Soccer Ball", "Bike", "Gloves",
    "Lego Set", "Doll", "Puzzle", "Board Game", "RC Car", "Kite",
    "Coffee", "Tea", "Chocolate", "Juice", "Snacks", "Cereal",
    "Perfume", "Shampoo", "Lotion", "Makeup", "Toothbrush", "Sunscreen",
]

random.seed(42)
products: list[dict] = []
product_dict: dict[int, dict] = {}

for pid in range(1, 1001):
    product = {
        "id": pid,
        "name": random.choice(PRODUCT_NAMES),
        "category": random.choice(CATEGORIES),
        "price": round(random.uniform(5.0, 2000.0), 2),
    }
    products.append(product)
    product_dict[pid] = product


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/search/id")
def search_by_id(id: int = Query(..., description="Product ID")):
    """O(1) – dict lookup by product ID."""
    start = time.perf_counter()
    result = product_dict.get(id)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "method": "O(1) Id Lookup",
        "time_ms": round(elapsed_ms, 4),
        "count": 1 if result else 0,
        "results": [result] if result else [],
    }


@app.get("/search/name")
def search_by_name(q: str = Query(..., description="Search keyword")):
    """O(n) – sequential scan of all products by name."""
    start = time.perf_counter()
    results = [p for p in products if q.lower() in p["name"].lower()]
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "method": "O(n) Name Search",
        "time_ms": round(elapsed_ms, 4),
        "count": len(results),
        "results": results,
    }


@app.get("/search/duplicates")
def find_duplicates():
    """O(n²) – nested loops to find products sharing the same name."""
    start = time.perf_counter()

    duplicate_names: set[str] = set()
    for i in range(len(products)):
        for j in range(i + 1, len(products)):
            if products[i]["name"] == products[j]["name"]:
                duplicate_names.add(products[i]["name"])

    results = [p for p in products if p["name"] in duplicate_names]
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "method": "O(n²) Duplicate Detection",
        "time_ms": round(elapsed_ms, 4),
        "count": len(results),
        "duplicate_names": sorted(duplicate_names),
        "results": results,
    }


# ── Static files & root ───────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
