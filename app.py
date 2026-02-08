from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from image_downloader import (
    crawl_and_download,
    zip_images,
    stop_now,
    reset_stop_flag,
    ZIP_PATH as ZIP_PATH
)
import threading
import os

app = Flask(__name__)

# ZIP_PATH imported from image_downloader gives an absolute path

progress = {
    "status": "idle",   # idle | running | stopped | zipping | done | error
    "downloaded": 0,
    "message": ""
}


@app.context_processor
def inject_settings():
    # allow deploying services to set ADSENSE_CLIENT as an env var (e.g. ca-pub-XXXXXXXX)
    return {
        'adsense_client': os.environ.get('ADSENSE_CLIENT', ''),
        'adsense_ad_slot': os.environ.get('ADSENSE_AD_SLOT', '')
    }


def background_job(url):
    global progress
    try:
        reset_stop_flag()
        progress.update({
            "status": "running",
            "downloaded": 0,
            "message": "Starting download..."
        })

        crawl_and_download(
            url,
            max_pages=30,
            max_images=200,
            progress=progress
        )

        if progress["status"] == "stopped":
            return

        # If nothing was downloaded, report and skip zipping
        if not progress.get("downloaded"):
            progress["status"] = "error"
            progress["message"] = "No downloadable images found or access blocked."
            return

        progress["status"] = "zipping"
        progress["message"] = "Creating ZIP file..."

        zip_images()

        # confirm zip exists before signalling done
        if os.path.exists(ZIP_PATH):
            progress["status"] = "done"
            progress["message"] = "ZIP ready! 🎉"
        else:
            progress["status"] = "error"
            progress["message"] = "Failed to create ZIP file."

    except Exception as e:
        progress["status"] = "error"
        progress["message"] = str(e)


@app.route("/app", methods=["GET", "POST"])
def index():
    # Interactive downloader app now lives at /app so the root can be a static landing page.
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            threading.Thread(target=background_job, args=(url,)).start()
            return redirect(url_for("status"))

    return render_template("index.html")


@app.route("/", methods=["GET"])
def landing():
    # Serve the static, content-rich landing page so root loads the publisher content.
    return render_template("landing.html")


@app.route("/status")
def status():
    return render_template("status.html")


@app.route("/progress")
def get_progress():
    return jsonify(progress)


@app.route("/stop", methods=["POST"])
def stop():
    stop_now()
    progress["status"] = "stopped"
    progress["message"] = "Download stopped by user"
    return jsonify({"stopped": True})


@app.route("/download")
def download():
    if os.path.exists(ZIP_PATH):
        return send_file(ZIP_PATH, as_attachment=True)
    return "ZIP not ready yet"


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/sitemap.xml')
def sitemap():
    # generate a simple sitemap for SEO
    from flask import Response
    base = request.url_root.rstrip('/')
    urls = [
        (f"{base}/", "daily", "1.0"),
        (f"{base}/app", "daily", "0.9"),
        (f"{base}/status", "hourly", "0.8"),
        (f"{base}/privacy", "monthly", "0.3"),
        (f"{base}/terms", "monthly", "0.3"),
        (f"{base}/contact", "monthly", "0.3"),
    ]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    from datetime import datetime
    now = datetime.utcnow().date().isoformat()
    for u, freq, pr in urls:
        xml.append('<url>')
        xml.append(f"  <loc>{u}</loc>")
        xml.append(f"  <lastmod>{now}</lastmod>")
        xml.append(f"  <changefreq>{freq}</changefreq>")
        xml.append(f"  <priority>{pr}</priority>")
        xml.append('</url>')
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype='application/xml')


@app.route('/ads.txt')
def ads_txt():
    # Serve ads.txt from the static folder so Google AdSense can find the publisher record
    try:
        return send_file(os.path.join(app.root_path, 'static', 'ads.txt'), mimetype='text/plain')
    except Exception:
        return "", 404


if __name__ == "__main__":
    app.run(debug=True)
