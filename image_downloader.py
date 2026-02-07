import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
import time
import re
from urllib import robotparser
import mimetypes
import hashlib
import tempfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded_images")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

ALLOWED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".webp", ".gif",
    ".bmp", ".tiff", ".svg"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

_stop_event = threading.Event()


def stop_now():
    _stop_event.set()


def reset_stop_flag():
    _stop_event.clear()


def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def is_image(url):
    return urlparse(url).path.lower().endswith(ALLOWED_EXTENSIONS)


def crawl_and_download(start_url, max_pages, max_images, progress):
    ensure_dirs()

    visited = set()
    to_visit = [start_url]
    img_count = 0
    downloaded_urls = set()
    seen_hashes = set()
    last_request = {}
    default_delay = 1.0

    # prepare robots.txt parser for the target site
    parsed_start = urlparse(start_url)
    robots_url = f"{parsed_start.scheme}://{parsed_start.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        # fetch robots.txt and parse crawl-delay if present
        rtxt = requests.get(robots_url, headers=HEADERS, timeout=8).text
        rp.parse(rtxt.splitlines())
        m = re.search(r"(?i)^\s*Crawl-delay\s*:\s*(\d+(?:\.\d+)?)", rtxt, flags=re.M)
        if m:
            try:
                default_delay = float(m.group(1))
            except Exception:
                default_delay = 1.0
    except Exception:
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception:
            pass

    while to_visit and len(visited) < max_pages and img_count < max_images:
        if _stop_event.is_set():
            progress["status"] = "stopped"
            return

        url = to_visit.pop(0)
        if url in visited:
            continue

        visited.add(url)

        # check robots.txt for permission
        try:
            if hasattr(rp, 'can_fetch') and not rp.can_fetch("*", url):
                continue
        except Exception:
            pass

        # polite rate limiting per host
        host = urlparse(url).netloc
        last = last_request.get(host)
        if last:
            waited = time.time() - last
            if waited < default_delay:
                time.sleep(default_delay - waited)

        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            last_request[host] = time.time()
            if res.status_code != 200 or not res.text:
                continue
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception:
            continue

        # Collect images from several common attributes
        for img in soup.find_all("img"):
            if img_count >= max_images or _stop_event.is_set():
                return

            # pick best candidate (prefer srcset largest width/density)
            def pick_best_src(img_tag, base_url):
                candidates = []
                src = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-original") or img_tag.get("data-lazy")
                if src:
                    candidates.append((src, 0))

                srcset = img_tag.get("srcset")
                if srcset:
                    parts = [p.strip() for p in srcset.split(",") if p.strip()]
                    for p in parts:
                        items = p.split()
                        u = items[0]
                        size = 0
                        if len(items) > 1:
                            token = items[1]
                            if token.endswith('w'):
                                try:
                                    size = int(token[:-1])
                                except Exception:
                                    size = 0
                            elif token.endswith('x'):
                                try:
                                    size = int(float(token[:-1]) * 100)
                                except Exception:
                                    size = 0
                        candidates.append((u, size))

                # sort by size desc and prefer larger
                candidates = [(urljoin(base_url, c[0]), c[1]) for c in candidates]
                if not candidates:
                    return None
                candidates.sort(key=lambda x: x[1], reverse=True)
                return candidates[0][0]

            img_url = pick_best_src(img, url)
            if not img_url:
                continue

            # avoid duplicate URL downloads
            norm_url = img_url.split('#')[0].split('?')[0]
            if norm_url in downloaded_urls:
                continue
            try:
                # check robots for image URL
                try:
                    if hasattr(rp, 'can_fetch') and not rp.can_fetch("*", img_url):
                        downloaded_urls.add(norm_url)
                        continue
                except Exception:
                    pass

                host_img = urlparse(img_url).netloc
                last = last_request.get(host_img)
                if last:
                    waited = time.time() - last
                    if waited < default_delay:
                        time.sleep(default_delay - waited)

                r = requests.get(img_url, headers=HEADERS, timeout=16, stream=True)
                last_request[host_img] = time.time()
                if r.status_code != 200:
                    r.close()
                    continue

                content_type = r.headers.get("content-type", "")
                if not content_type.startswith("image"):
                    r.close()
                    continue

                # write to temp file while hashing
                tmp = tempfile.NamedTemporaryFile(delete=False)
                h = hashlib.sha256()
                total = 0
                for chunk in r.iter_content(1024 * 16):
                    if chunk:
                        tmp.write(chunk)
                        h.update(chunk)
                        total += len(chunk)
                tmp.flush()
                tmp.close()
                r.close()

                # skip very small images (likely icons/thumbs)
                if total < 5 * 1024:
                    try:
                        os.remove(tmp.name)
                    except Exception:
                        pass
                    continue

                digest = h.hexdigest()
                if digest in seen_hashes:
                    try:
                        os.remove(tmp.name)
                    except Exception:
                        pass
                    downloaded_urls.add(norm_url)
                    continue

                # determine extension
                ext = os.path.splitext(urlparse(img_url).path)[1].split("?")[0]
                if not ext:
                    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
                    ext = guessed or ".jpg"

                final_name = os.path.join(DOWNLOAD_DIR, f"img_{img_count}{ext}")
                shutil.move(tmp.name, final_name)

                img_count += 1
                downloaded_urls.add(norm_url)
                seen_hashes.add(digest)
                progress["downloaded"] = img_count
                progress["message"] = f"Downloaded {img_count} / {max_images} images"

            except Exception:
                try:
                    r.close()
                except Exception:
                    pass
                try:
                    os.remove(tmp.name)
                except Exception:
                    pass
                continue

        # follow same-domain links
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)


def zip_images():
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in os.listdir(DOWNLOAD_DIR):
            if f != "images.zip":
                path = os.path.join(DOWNLOAD_DIR, f)
                if os.path.isfile(path):
                    zipf.write(path, f)
