from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from image_downloader import crawl_and_download, zip_images, stop_now, reset_stop_flag
import threading
import os

app = Flask(__name__)

ZIP_PATH = "downloaded_images/images.zip"

progress = {
    "status": "idle",       # idle | running | stopped | zipping | done | error
    "downloaded": 0,
    "message": ""
}


def background_job(url):
    global progress
    try:
        reset_stop_flag()
        progress["status"] = "running"
        progress["downloaded"] = 0
        progress["message"] = "Starting download..."

        crawl_and_download(
            url,
            max_pages=30,
            max_images=200,      # 🔥 DEFAULT LIMIT
            progress=progress
        )

        if progress["status"] == "stopped":
            return

        progress["status"] = "zipping"
        progress["message"] = "Creating ZIP..."

        zip_images()

        progress["status"] = "done"
        progress["message"] = "ZIP ready!"

    except Exception as e:
        progress["status"] = "error"
        progress["message"] = str(e)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            thread = threading.Thread(target=background_job, args=(url,))
            thread.start()
            return redirect(url_for("status"))

    return render_template("index.html")


@app.route("/status")
def status():
    return render_template("status.html")


@app.route("/progress")
def get_progress():
    return jsonify(progress)


@app.route("/stop", methods=["POST"])
def stop():
    progress["status"] = "stopped"
    progress["message"] = "Download stopped by user"
    stop_now()
    return jsonify({"stopped": True})


@app.route("/download")
def download():
    if os.path.exists(ZIP_PATH):
        return send_file(ZIP_PATH, as_attachment=True)
    return "ZIP not ready yet"

if __name__ == "__main__":
    app.run()

