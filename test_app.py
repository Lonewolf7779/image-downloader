import os
import time
from image_downloader import crawl_and_download, zip_images

DOWNLOAD_DIR = "downloaded_images"
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

def test_crawl_and_zip(test_url=None):
    if not test_url:
        test_url = input("Enter the URL to test: ").strip()
        if not test_url:
            print("No URL provided. Exiting.")
            return

    if not test_url.startswith(('http://', 'https://')):
        test_url = 'https://' + test_url

    # Clear previous downloads
    for file in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

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
