from flask import Flask, render_template, request, send_file
from image_downloader import crawl_and_download, zip_images
import os

app = Flask(__name__)

ZIP_PATH = "downloaded_images/images.zip"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    show_download = False

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            crawl_and_download(url, depth=2)
            zip_images()
            message = "✅ Images downloaded & zipped"
            show_download = True

    return render_template(
        "index.html",
        message=message,
        show_download=show_download
    )

@app.route("/download")
def download():
    if os.path.exists(ZIP_PATH):
        return send_file(ZIP_PATH, as_attachment=True)
    return "No ZIP found", 404

# 👇 THIS IS THE LOCAL-RUN FIX
if __name__ == "__main__":
    app.run(debug=True)
