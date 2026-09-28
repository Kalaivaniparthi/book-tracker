import sys
import os
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Add project root to path so we can import src.db and src.ai
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import upsert_book
from src.ai import summarize

# ==========================================
# CONFIG
# ==========================================
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/page-{}.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Kalaivaniparthi/book-tracker)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 10
DELAY = 0.5
PAGES_TO_SCRAPE = 3


def fetch(url):
    """Fetch a URL politely."""
    time.sleep(DELAY)
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def get_book_links(html, page_url):
    """Extract absolute book URLs from a catalogue page."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for h3 in soup.select("h3"):
        a = h3.find("a")
        if a and a.get("href"):
            links.append(urljoin(page_url, a["href"]))
    return links


def get_next_page(html, page_url):
    """Return the absolute URL of the 'next' page, or None."""
    soup = BeautifulSoup(html, "html.parser")
    btn = soup.select_one("li.next a")
    if btn and btn.get("href"):
        return urljoin(page_url, btn["href"])
    return None


def extract_book(html, product_url):
    """Extract raw book fields from a detail page."""
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one("div.product_main")

    title = main.select_one("h1").get_text(strip=True) if main else None
    price_el = main.select_one("p.price_color") if main else None
    price_text = price_el.get_text(strip=True) if price_el else None

    rating_el = main.select_one("p.star-rating") if main else None
    rating_text = None
    if rating_el:
        for c in rating_el.get("class", []):
            if c != "star-rating":
                rating_text = c
                break

    desc_el = soup.select_one("div#product_description ~ p")
    description = desc_el.get_text(strip=True) if desc_el else None

    # "£51.77" -> 51.77
    price_gbp = None
    if price_text:
        m = re.search(r"[\d.]+", price_text)
        if m:
            price_gbp = float(m.group())

    return {
        "title": title,
        "product_url": product_url,
        "price_gbp": price_gbp,
        "rating_text": rating_text,
        "description": description,
    }


def main():
    print("=" * 60)
    print("Seeding books from Books to Scrape")
    print("=" * 60)

    # ---- Step 1: Discover all book URLs ----
    all_urls = []
    next_url = CATALOGUE_URL.format(1)
    page_num = 1

    while next_url and page_num <= PAGES_TO_SCRAPE:
        print(f"Fetching catalogue page {page_num}...")
        html = fetch(next_url)
        for u in get_book_links(html, next_url):
            if u not in all_urls:
                all_urls.append(u)
        next_url = get_next_page(html, next_url)
        page_num += 1

    print(f"Found {len(all_urls)} books")

    # ---- Step 2: Extract, summarize, store ----
    for i, url in enumerate(all_urls, start=1):
        try:
            print(f"[{i}/{len(all_urls)}] {url.split('/')[-2][:40]}...")
            html = fetch(url)
            book = extract_book(html, url)

            # AI summary (only if we have a description)
            book["ai_summary"] = summarize(book.get("description") or "")

            upsert_book(book)
        except Exception as e:
            print(f"  FAILED: {e}")
            continue

    print("=" * 60)
    print(f"Done. {len(all_urls)} books seeded.")
    print("=" * 60)


if __name__ == "__main__":
    main()
