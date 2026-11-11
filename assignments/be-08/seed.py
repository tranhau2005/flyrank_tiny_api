"""Load the 60 books collected by BE-05 into a local reporting database."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "report.db"
SOURCE = ROOT.parent / "be-05" / "output" / "books.json"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def seed():
    books = json.loads(SOURCE.read_text(encoding="utf-8"))
    with sqlite3.connect(DB) as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, rating INTEGER NOT NULL, url TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, path TEXT NOT NULL, created_at TEXT NOT NULL, report_date TEXT NOT NULL);""")
        db.execute("DELETE FROM books")
        db.executemany("INSERT INTO books(title,price,rating,url) VALUES (?,?,?,?)", [(b["title"], b["price_gbp"], RATINGS[b["rating_text"]], str(b["product_url"])) for b in books])
        return db.execute("SELECT COUNT(*) FROM books").fetchone()[0]

if __name__ == "__main__":
    print(f"Seeded {seed()} books")
