import os
import time
import zipfile

DOWNLOAD_DIR = "downloaded_images"
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "images.zip")

def zip_images_test():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Create dummy files to simulate images
    for i in range(10):
        with open(os.path.join(DOWNLOAD_DIR, f"img_{i}.jpg"), "wb") as f:
            f.write(b"dummy image data" * 1000)  # ~14KB each

    start = time.time()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_STORED) as zipf:
        for file in os.listdir(DOWNLOAD_DIR):
            if file == "images.zip":
                continue
            zipf.write(
                os.path.join(DOWNLOAD_DIR, file),
                arcname=file
            )
    end = time.time()
    print(f"Zip creation time: {end - start} seconds")
    print(f"Zip size: {os.path.getsize(ZIP_PATH)} bytes")

if __name__ == "__main__":
    zip_images_test()
