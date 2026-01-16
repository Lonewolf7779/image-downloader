import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


DOWNLOAD_DIR = "downloaded_images"


def ensure_download_dir():
    """Create download directory if it doesn't exist"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_images_from_url(page_url):
    ensure_download_dir()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(page_url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    downloaded_files = []

    for img in img_tags:
        src = img.get("src")
        if not src:
            continue

        img_url = urljoin(page_url, src)

        try:
            img_data = requests.get(img_url, headers=headers, timeout=10).content
        except Exception:
            continue

        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            continue

        file_path = os.path.join(DOWNLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(img_data)

        downloaded_files.append(file_path)

    return downloaded_files


def zip_images():
    ensure_download_dir()

    zip_path = os.path.join(DOWNLOAD_DIR, "images.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                zipf.write(
                    os.path.join(DOWNLOAD_DIR, file),
                    arcname=file
                )

    return zip_path
