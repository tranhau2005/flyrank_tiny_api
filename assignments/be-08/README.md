# BE-08: Book PDF report generator

This project uses the 60 real books collected in `../be-05/output/books.json`, stores them in SQLite, aggregates the data, and prints an HTML report to PDF with Playwright Chromium. Install the browser with `python -m playwright install chromium`.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python seed.py
uvicorn main:app --port 8000
```

POST `/reports` returns 201 and a file link. A second request on the same UTC day returns the same ID with 200; `{"force":true}` generates a fresh report. GET `/reports/{id}` returns metadata and `/reports/{id}/file` serves the PDF. SQLite locks the generation transaction to prevent simultaneous requests producing duplicate daily reports. `CHROMIUM_EXECUTABLE` may point to an existing compatible Chromium binary.

Queries used:

```sql
SELECT COUNT(*), AVG(price) FROM books;
SELECT title, price FROM books ORDER BY price DESC, id LIMIT 5;
SELECT rating, COUNT(*) FROM books GROUP BY rating ORDER BY rating;
SELECT title, price, rating FROM books ORDER BY id;
```

The check protects against a double-click producing duplicate files; a similar missing check on a payment request can charge a customer twice. Move rendering to a background job when generation time makes clients wait too long or ties up too many server workers. A local run returned 201 on first generation, 200 with the same ID on the second request, and 200 for the PDF download. The generated PDF had three pages; the table header repeated and the rendered pages were inspected for page-break clipping. See [page 1](screenshots/report-page-1.png).

A separate two-thread check used a temporary seeded database and a real Chromium PDF renderer. Concurrent calls returned 201 and 200 with the same ID, leaving one report row and one PDF file. This exercises simultaneous calls in one process; it is not a distributed load test.
