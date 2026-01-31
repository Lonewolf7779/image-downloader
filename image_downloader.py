import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from hashlib import md5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_images")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 🔴 STOP FLAG (used by STOP button)
STOP_REQUESTED = False


def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def reset_stop_flag():
    global STOP_REQUESTED
    STOP_REQUESTED = False


def stop_now():
    global STOP_REQUESTED
    STOP_REQUESTED = True


def is_image_response(resp):
    content_type = resp.headers.get("Content-Type", "")
    return content_type.startswith("image/")


def safe_filename(url, content_type):
    ext = content_type.split("/")[-1].split(";")[0]
    name = md5(url.encode()).hexdigest()
    return f"{name}.{ext}"


def crawl_and_download(start_url, max_pages=30, max_images=200, progress=None):
    ensure_dirs()

    visited_pages = set()
    downloaded_images = set()
    to_visit = [start_url]
    image_count = 0

    while to_visit and not STOP_REQUESTED:
        page_url = to_visit.pop(0)

        if page_url in visited_pages:
            continue

        visited_pages.add(page_url)

        try:
            res = requests.get(page_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception:
            continue

        # 🖼️ IMAGES
        for img in soup.find_all("img"):
            if STOP_REQUESTED or image_count >= max_images:
                break

            src = img.get("src")
            if not src:
                continue

            img_url = urljoin(page_url, src)

            if img_url in downloaded_images:
                continue

            try:
                img_res = requests.get(img_url, headers=HEADERS, timeout=10)
                if not is_image_response(img_res):
                    continue

                filename = safe_filename(img_url, img_res.headers.get("Content-Type", "image"))
                with open(os.path.join(DOWNLOAD_DIR, filename), "wb") as f:
                    f.write(img_res.content)

                downloaded_images.add(img_url)
                image_count += 1

                if progress:
                    progress["downloaded"] = image_count
                    progress["message"] = f"Downloaded {image_count}/{max_images} images"

            except Exception:
                continue

        # 🔗 LINKS
        for a in soup.find_all("a", href=True):
            link = urljoin(page_url, a["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                if link not in visited_pages:
                    to_visit.append(link)

        if image_count >= max_images:
            break

    return image_count


def zip_images():
    ensure_dirs()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith(".zip"):
                continue
            zipf.write(
                os.path.join(DOWNLOAD_DIR, file),
                arcname=file
            )

    return ZIP_PATH
