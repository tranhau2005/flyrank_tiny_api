"""Generate and serve a PDF report from SQLite book data."""
import html
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from seed import DB, ROOT

app = FastAPI(title="Book reports")
REPORTS = ROOT / "reports"


def report_data(db):
    count, average = db.execute("SELECT COUNT(*), AVG(price) FROM books").fetchone()
    top = db.execute("SELECT title, price FROM books ORDER BY price DESC, id LIMIT 5").fetchall()
    ratings = db.execute("SELECT rating, COUNT(*) FROM books GROUP BY rating ORDER BY rating").fetchall()
    books = db.execute("SELECT title, price, rating FROM books ORDER BY id").fetchall()
    return {"count": count, "average": average or 0, "top": top, "ratings": ratings, "books": books}


def render(data, destination):
    def rows(items):
        return "".join("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>" for row in items)
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
      @page{{size:A4;margin:14mm}} body{{font: 12px sans-serif;color:#172b3a}} h1{{color:#124c68}} table{{width:100%;border-collapse:collapse;margin-bottom:20px}}
      td,th{{border:1px solid #ccd9df;padding:7px;text-align:left}} th{{background:#e4f0f3}} thead{{display:table-header-group}} tr{{break-inside:avoid}}
      </style></head><body><h1>Book catalogue report</h1><p>Generated {datetime.now(timezone.utc).date()} UTC</p>
      <p>Books: {data['count']} · Average price: £{data['average']:.2f}</p>
      <h2>Five most expensive</h2><table><thead><tr><th>Title</th><th>Price (£)</th></tr></thead><tbody>{rows(data['top'])}</tbody></table>
      <h2>Books by rating</h2><table><thead><tr><th>Stars</th><th>Books</th></tr></thead><tbody>{rows(data['ratings'])}</tbody></table>
      <h2>Catalogue</h2><table><thead><tr><th>Title</th><th>Price (£)</th><th>Rating</th></tr></thead><tbody>{rows(data['books'])}</tbody></table></body></html>'''
    with sync_playwright() as playwright:
        executable = os.getenv("CHROMIUM_EXECUTABLE") or None
        browser = playwright.chromium.launch(headless=True, executable_path=executable)
        try:
            tab = browser.new_page()
            tab.set_content(page, wait_until="load")
            tab.pdf(path=str(destination), format="A4", print_background=True)
        finally:
            browser.close()


class Options(BaseModel):
    force: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports")
def create_report(options: Options = Options()):
    if not DB.exists():
        raise HTTPException(503, "Run python seed.py first")
    REPORTS.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    with sqlite3.connect(DB, timeout=30, isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        if not options.force:
            existing = db.execute("SELECT id FROM reports WHERE report_date=? ORDER BY created_at DESC LIMIT 1", (now.date().isoformat(),)).fetchone()
            if existing:
                db.commit()
                return JSONResponse({"id": existing[0], "file": f"/reports/{existing[0]}/file"}, status_code=200)
        report_id = uuid.uuid4().hex
        path = REPORTS / f"{report_id}.pdf"
        try:
            render(report_data(db), path)
            db.execute("INSERT INTO reports VALUES (?,?,?,?)", (report_id, path.name, now.isoformat(), now.date().isoformat()))
            db.commit()
        except Exception:
            db.rollback()
            path.unlink(missing_ok=True)
            raise
    return JSONResponse({"id": report_id, "file": f"/reports/{report_id}/file"}, status_code=201)


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    if not DB.exists():
        raise HTTPException(404, "Report not found")
    with sqlite3.connect(DB) as db:
        row = db.execute("SELECT id,created_at FROM reports WHERE id=?", (report_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Report not found")
    return {"id": row[0], "created_at": row[1], "file": f"/reports/{row[0]}/file"}


@app.get("/reports/{report_id}/file")
def download_report(report_id: str):
    get_report(report_id)
    path = REPORTS / f"{report_id}.pdf"
    if not path.is_file():
        raise HTTPException(404, "Report file not found")
    return FileResponse(path, media_type="application/pdf", filename="book-report.pdf")
