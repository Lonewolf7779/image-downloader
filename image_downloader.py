import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}

def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def download_images_from_page(url, folder):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return 0

    soup = BeautifulSoup(response.text, "html.parser")
    images = soup.find_all("img")
    count = 0

    for i, img in enumerate(images, start=1):
        src = img.get("src")
        if not src:
            continue

        img_url = urljoin(url, src)

        try:
            img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
        except:
            continue

        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            filename = f"image_{i}.jpg"

        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(img_data)
            count += 1

    return count

def crawl_and_download(url, folder="downloaded_images", depth=2, visited=None):
    if visited is None:
        visited = set()

    if depth == 0 or url in visited:
        return 0

    visited.add(url)
    total = download_images_from_page(url, folder)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
    except:
        return total

    for link in soup.find_all("a", href=True):
        next_url = urljoin(url, link["href"])
        if is_same_domain(url, next_url):
            total += crawl_and_download(
                next_url,
                folder,
                depth=depth - 1,
                visited=visited
            )

    return total

def zip_images(folder="downloaded_images", zip_name="images.zip"):
    zip_path = os.path.join(folder, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".zip"):
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)

    return zip_path
