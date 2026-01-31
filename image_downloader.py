import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
import hashlib
import time

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_images")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

TIMEOUT = 12

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

ALLOWED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".webp",
    ".gif", ".bmp", ".tiff", ".svg"
)

# ================= STOP FLAG =================

_stop_event = threading.Event()

def stop_now():
    _stop_event.set()

def reset_stop_flag():
    _stop_event.clear()

def should_stop():
    return _stop_event.is_set()

# ================= HELPERS =================

def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_image(url):
    return urlparse(url).path.lower().endswith(ALLOWED_EXTENSIONS)

def get_with_retry(url, headers, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except Exception:
            time.sleep(1)
    raise Exception(f"Failed to fetch {url}")

def best_image_url(img, base_url):
    # Prefer high quality attributes
    for attr in ["data-original", "data-src", "data-lazy", "data-img"]:
        if img.get(attr):
            return urljoin(base_url, img.get(attr))

    if img.get("srcset"):
        srcset = img.get("srcset").split(",")
        return urljoin(base_url, srcset[-1].split()[0])

    if img.get("src"):
        return urljoin(base_url, img.get("src"))

    return None

# ================= MAIN LOGIC =================

def crawl_and_download(start_url, max_pages=10, max_images=200, progress=None):
    ensure_dirs()

    visited = set()
    to_visit = [start_url]
    downloaded_hashes = set()
    img_count = 0

    while to_visit and len(visited) < max_pages and img_count < max_images:
        if should_stop():
            if progress:
                progress["status"] = "stopped"
            return

        url = to_visit.pop(0)
        if url in visited:
            continue

        visited.add(url)

        try:
            res = get_with_retry(url, HEADERS.copy())
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception:
            continue

        # ---------- IMAGES ----------
        for img in soup.find_all("img"):
            if img_count >= max_images or should_stop():
                break

            img_url = best_image_url(img, url)
            if not img_url or not is_image(img_url):
                continue

            try:
                img_data = get_with_retry(img_url, HEADERS.copy()).content

                # Remove duplicates using hash
                img_hash = hashlib.md5(img_data).hexdigest()
                if img_hash in downloaded_hashes:
                    continue
                downloaded_hashes.add(img_hash)

                ext = os.path.splitext(img_url)[1].split("?")[0] or ".jpg"
                filename = f"img_{img_count}{ext}"

                with open(os.path.join(DOWNLOAD_DIR, filename), "wb") as f:
                    f.write(img_data)

                img_count += 1

                if progress:
                    progress["downloaded"] = img_count
                    progress["message"] = f"Downloaded {img_count} images"

            except Exception:
                continue

        # ---------- INTERNAL LINKS ----------
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                if link not in visited:
                    to_visit.append(link)

    if progress:
        progress["message"] = "Download completed"

# ================= ZIP =================

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
