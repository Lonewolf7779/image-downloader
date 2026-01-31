import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_images")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

MAX_IMAGES = 200
TIMEOUT = 12

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

ALLOWED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"
)

def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_image(url):
    path = urlparse(url).path.lower()
    return path.endswith(ALLOWED_EXTENSIONS)

def get_best_image_src(img, base_url):
    # Priority: data-original > data-src > srcset > src
    for attr in ["data-original", "data-src", "data-lazy", "data-img"]:
        if img.get(attr):
            return urljoin(base_url, img.get(attr))

    if img.get("srcset"):
        # pick highest resolution from srcset
        srcset = img.get("srcset").split(",")
        return urljoin(base_url, srcset[-1].strip().split(" ")[0])

    if img.get("src"):
        return urljoin(base_url, img.get("src"))

    return None

def crawl_and_download(start_url, max_pages=10):
    ensure_dirs()

    visited_pages = set()
    visited_images = set()
    to_visit = [start_url]
    img_count = 0

    while to_visit and len(visited_pages) < max_pages and img_count < MAX_IMAGES:
        url = to_visit.pop(0)
        if url in visited_pages:
            continue

        visited_pages.add(url)

        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print(f"Page failed: {url} -> {e}")
            continue

        # 🔹 IMAGE SCRAPING
        for img in soup.find_all("img"):
            if img_count >= MAX_IMAGES:
                break

            img_url = get_best_image_src(img, url)
            if not img_url or not is_image(img_url):
                continue

            img_hash = hashlib.md5(img_url.encode()).hexdigest()
            if img_hash in visited_images:
                continue

            visited_images.add(img_hash)

            try:
                img_data = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT).content
                ext = os.path.splitext(urlparse(img_url).path)[1] or ".jpg"
                filename = f"img_{img_count}{ext}"

                with open(os.path.join(DOWNLOAD_DIR, filename), "wb") as f:
                    f.write(img_data)

                img_count += 1
            except Exception as e:
                print(f"Image failed: {img_url}")

        # 🔹 INTERNAL LINKS
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                if link not in visited_pages:
                    to_visit.append(link)

def zip_images():
    ensure_dirs()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(DOWNLOAD_DIR):
            if file != "images.zip":
                zipf.write(
                    os.path.join(DOWNLOAD_DIR, file),
                    arcname=file
                )

    return ZIP_PATH
