import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_images")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def is_image(url):
    return url.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))


def crawl_and_download(start_url, max_pages=10):
    ensure_dirs()

    visited = set()
    to_visit = [start_url]
    img_count = 0

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        visited.add(url)

        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception:
            continue

        # Images
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue

            img_url = urljoin(url, src)
            if not is_image(img_url):
                continue

            try:
                img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                ext = os.path.splitext(img_url)[1].split("?")[0]
                filename = f"img_{img_count}{ext}"
                with open(os.path.join(DOWNLOAD_DIR, filename), "wb") as f:
                    f.write(img_data)
                img_count += 1
            except Exception:
                pass

        # Internal links
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                if link not in visited:
                    to_visit.append(link)


def zip_images():
    ensure_dirs()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(DOWNLOAD_DIR):
            if file == "images.zip":
                continue
            zipf.write(
                os.path.join(DOWNLOAD_DIR, file),
                arcname=file
            )

    return ZIP_PATH
