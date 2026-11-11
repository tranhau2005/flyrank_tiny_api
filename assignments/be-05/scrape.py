"""Collect the first three catalogue pages of the Books to Scrape sandbox."""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl, ValidationError

BASE = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "FlyRankInternship-BE05/1.0 (+https://github.com/tranhau2005/flyrank_tiny_api)"}
ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
OUTPUT = ROOT / "output"


class Book(BaseModel):
    title: str = Field(min_length=1)
    product_url: HttpUrl
    price_text: str
    price_gbp: float = Field(ge=0)
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime


class Fetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.fetched = 0
        self.cache_hits = 0
        self.last_request = 0.0

    def get(self, url):
        if urlparse(url).scheme != "https" or urlparse(url).hostname != "books.toscrape.com":
            raise ValueError("Only HTTPS pages on books.toscrape.com are allowed")
        CACHE.mkdir(exist_ok=True)
        key = hashlib.sha256(url.encode()).hexdigest()
        cached = CACHE / f"{key}.json"
        if cached.exists():
            self.cache_hits += 1
            saved = json.loads(cached.read_text(encoding="utf-8"))
            print(f"CACHE HIT {url} ({len(saved['html'])} characters)")
            return saved["html"], saved["fetched_at"]
        for attempt in range(2):
            elapsed = time.monotonic() - self.last_request
            if elapsed < 0.5:
                time.sleep(0.5 - elapsed)
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, timeout=10, allow_redirects=False)
                if response.status_code >= 500 and attempt == 0:
                    time.sleep(1)
                    continue
                response.raise_for_status()
                if response.status_code != 200:
                    raise requests.HTTPError(f"Unexpected status {response.status_code}")
                response.encoding = "utf-8"
                fetched_at = datetime.now(timezone.utc).isoformat()
                saved = {"url": url, "fetched_at": fetched_at, "html": response.text}
                cached.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
                self.fetched += 1
                print(f"FETCH {url} ({len(response.content)} bytes)")
                return response.text, fetched_at
            except (requests.Timeout, requests.ConnectionError):
                if attempt:
                    raise
                time.sleep(1)
        raise RuntimeError(f"Failed to fetch {url}")


def parse_detail(html, url, source, fetched_at):
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("article.product_page")
    if product is None:
        raise ValueError("Missing product page")
    rating = product.select_one("p.star-rating")
    marker = product.select_one("#product_description")
    description = marker.find_next_sibling("p").get_text(" ", strip=True) if marker and marker.find_next_sibling("p") else None
    price = product.select_one(".product_main .price_color").get_text(strip=True)
    return Book(title=product.select_one("h1").get_text(strip=True), product_url=url,
                price_text=price, price_gbp=float(price.replace("£", "").strip()),
                availability_text=product.select_one(".product_main .availability").get_text(" ", strip=True),
                rating_text=next(x for x in rating.get("class", []) if x != "star-rating"),
                description=description, source_page=source, fetched_at=fetched_at)


def run():
    start = datetime.now(timezone.utc)
    clock = time.monotonic()
    fetcher = Fetcher()
    errors, books, links = [], [], {}
    catalogue_pages = 0
    page = BASE
    for _ in range(3):
        try:
            html, _ = fetcher.get(page)
            soup = BeautifulSoup(html, "html.parser")
            catalogue_pages += 1
            for anchor in soup.select("article.product_pod h3 a"):
                links.setdefault(urljoin(page, anchor["href"]), page)
            next_link = soup.select_one("li.next a")
            page = urljoin(page, next_link["href"]) if next_link else None
            if not page:
                break
        except (requests.RequestException, ValueError, KeyError) as exc:
            errors.append({"url": page, "kind": "failed_page", "error": str(exc)})
            break
    for url, source in links.items():
        try:
            html, fetched_at = fetcher.get(url)
            book = parse_detail(html, url, source, fetched_at)
            books.append(book.model_dump(mode="json"))
        except requests.RequestException as exc:
            errors.append({"url": url, "kind": "failed_page", "error": str(exc)})
        except (ValidationError, ValueError, AttributeError, StopIteration, KeyError) as exc:
            errors.append({"url": url, "kind": "invalid_record", "error": str(exc)})
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "books.json").write_text(json.dumps(books, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"started_at": start.isoformat(), "duration_seconds": round(time.monotonic() - clock, 2), "pages_fetched": fetcher.fetched, "cache_hits": fetcher.cache_hits, "catalogue_pages": catalogue_pages, "discovered": len(links), "valid_records": len(books), "invalid_records": sum(e["kind"] == "invalid_record" for e in errors), "failed_pages": sum(e["kind"] == "failed_page" for e in errors)}
    (OUTPUT / "run-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if len(books) == 60 and not errors else 1


if __name__ == "__main__":
    raise SystemExit(run())
