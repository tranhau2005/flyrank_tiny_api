# BE-05: Polite book scraper

Target classification: Books to Scrape is explicitly described by its creator as a scraping sandbox at https://toscrape.com/. This script limits itself to the first three catalogue pages and their 60 book detail pages, collecting title, URL, price, stock, rating and description with provenance. This is appropriate for the site's stated practice purpose. On inspection, https://books.toscrape.com/robots.txt returned 404 (no robots file found); this fact alone is not permission. I will not reuse this code on another site without checking its rules and terms first.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scrape.py
```

The client identifies its repository, uses timeouts, waits at least half a second between real requests, caches pages, retries a timeout or 5xx once, and does not retry 403/404. It validates each result with Pydantic and saves good records, errors and a run report to `output/`. Cache files are ignored by Git. A repeat run replaces the output rather than appending duplicates.

An isolated failure check redirected one detail fetch to a nonexistent sandbox URL that returned HTTP 404. The run recorded one failed page, preserved the other 59 cached records and returned a nonzero exit status. Its output was written to a temporary directory.
