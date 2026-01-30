import os
import time
from image_downloader import crawl_and_download, zip_images

DOWNLOAD_DIR = "downloaded_images"
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

def test_crawl_and_zip():
    # Test with a public website that has images
    test_url = "https://www.python.org/"  # Public site with images

    print("Starting crawl and download...")
    start = time.time()
    crawl_and_download(test_url, max_pages=2)  # Limit pages for test
    end = time.time()
    print(f"Crawl and download time: {end - start} seconds")

    files = os.listdir(DOWNLOAD_DIR)
    print(f"Downloaded files: {len([f for f in files if f != 'images.zip'])}")

    print("Starting zip creation...")
    start = time.time()
    zip_images()
    end = time.time()
    print(f"Zip creation time: {end - start} seconds")

    if os.path.exists(ZIP_PATH):
        print(f"Zip file size: {os.path.getsize(ZIP_PATH)} bytes")
    else:
        print("Zip file not created")

if __name__ == "__main__":
    test_crawl_and_zip()
