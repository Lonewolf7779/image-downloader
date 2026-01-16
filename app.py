from flask import Flask, render_template, request, send_file, redirect, url_for
from image_downloader import crawl_and_download, zip_images
import os
import threading

app = Flask(__name__)

ZIP_PATH = "downloaded_images/images.zip"
DOWNLOAD_FOLDER = "downloaded_images"

def background_job(url):
    try:
        crawl_and_download(url, folder=DOWNLOAD_FOLDER, depth=2)
        zip_images(folder=DOWNLOAD_FOLDER)
    except Exception as e:
        print("Background error:", e)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            thread = threading.Thread(target=background_job, args=(url,))
            thread.start()
            return redirect(url_for("status"))

    return render_template("index.html")

@app.route("/status")
def status():
    return """
    <h3>⏳ Download started</h3>
    <p>Wait 30–60 seconds, then click below:</p>
    <a href="/download">Download ZIP</a>
    """

@app.route("/download")
def download():
    if os.path.exists(ZIP_PATH):
        return send_file(ZIP_PATH, as_attachment=True)
    return "ZIP not ready yet. Refresh after 30 seconds."
