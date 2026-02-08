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

progress = {
    "status": "idle",   # idle | running | stopped | zipping | done | error
    "downloaded": 0,
    "message": ""
}


@app.context_processor
def inject_settings():
    return {
        "adsense_client": os.environ.get("ADSENSE_CLIENT", ""),
        "adsense_ad_slot": os.environ.get("ADSENSE_AD_SLOT", "")
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

        if not progress.get("downloaded"):
            progress["status"] = "error"
            progress["message"] = "No downloadable images found or access blocked."
            return

        progress["status"] = "zipping"
        progress["message"] = "Creating ZIP file..."

        zip_images()

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
    if request.method == "POST":
        # 🔒 Single-job lock
        if progress["status"] in ("running", "zipping"):
            progress["message"] = "Another download is already running. Please wait."
            return redirect(url_for("status"))

        url = request.form.get("url")
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            threading.Thread(target=background_job, args=(url,)).start()
            return redirect(url_for("status"))

    return render_template("index.html")


@app.route("/", methods=["GET"])
def landing():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Genki Image Downloader</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Minimal image downloader inspired by Japanese design. Download images from public websites respectfully.">
<meta name="robots" content="index,follow">

<style>
  :root {
    --glass-bg: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.18);
    --text-main: #f9fafb;
    --text-muted: #cbd5f5;
    --accent: #60a5fa;
    --accent-hover: #3b82f6;
  }

  * {
    box-sizing: border-box;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }

  body {
    margin: 0;
    min-height: 100vh;
    background:
      linear-gradient(rgba(15,23,42,0.75), rgba(15,23,42,0.85)),
      url("https://images.unsplash.com/photo-1549693578-d683be217e58?auto=format&fit=crop&w=1600&q=80");
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px;
    color: var(--text-main);
  }

  .glass {
    max-width: 720px;
    width: 100%;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    padding: 40px 42px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
  }

  h1 {
    font-size: 2.2rem;
    font-weight: 600;
    margin-bottom: 12px;
  }

  p {
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text-muted);
    margin-bottom: 18px;
  }

  .note {
    font-size: 0.95rem;
    opacity: 0.85;
  }

  .actions {
    margin-top: 28px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .btn {
    text-decoration: none;
    padding: 12px 22px;
    border-radius: 999px;
    font-size: 0.95rem;
    transition: all 0.25s ease;
  }

  .btn-primary {
    background: linear-gradient(135deg, var(--accent), var(--accent-hover));
    color: #0f172a;
  }

  .btn-secondary {
    color: var(--text-muted);
    border: 1px solid var(--glass-border);
    background: rgba(255,255,255,0.04);
  }

  .footer {
    margin-top: 26px;
    font-size: 0.85rem;
    opacity: 0.75;
  }

  @media (max-width: 640px) {
    h1 { font-size: 1.8rem; }
    .glass { padding: 28px; }
  }
</style>
</head>

<body>
  <main class="glass">
    <h1>Genki Image Downloader</h1>

    <p>
      A calm, minimal tool inspired by Japanese design.
      Download images from <strong>publicly accessible websites</strong>
      in a clean and respectful way.
    </p>

    <p class="note">
      Designed for designers, developers, and researchers.
      No accounts. No noise. Just utility.
    </p>

    <div class="actions">
      <a href="/app" class="btn btn-primary">Open the App</a>
      <a href="/privacy" class="btn btn-secondary">Privacy</a>
      <a href="/terms" class="btn btn-secondary">Terms</a>
    </div>

    <div class="footer">
      © Genki — respect creators & website policies.
    </div>
  </main>
</body>
</html>
"""


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


@app.route("/sitemap.xml")
def sitemap():
    from flask import Response
    base = request.url_root.rstrip("/")
    urls = [
        (f"{base}/", "daily", "1.0"),
        (f"{base}/app", "daily", "0.9"),
        (f"{base}/status", "hourly", "0.8"),
        (f"{base}/privacy", "monthly", "0.3"),
        (f"{base}/terms", "monthly", "0.3"),
        (f"{base}/contact", "monthly", "0.3"),
    ]

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    from datetime import datetime
    now = datetime.utcnow().date().isoformat()

    for u, freq, pr in urls:
        xml.append("<url>")
        xml.append(f"<loc>{u}</loc>")
        xml.append(f"<lastmod>{now}</lastmod>")
        xml.append(f"<changefreq>{freq}</changefreq>")
        xml.append(f"<priority>{pr}</priority>")
        xml.append("</url>")

    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


@app.route("/ads.txt")
def ads_txt():
    try:
        return send_file(os.path.join(app.root_path, "static", "ads.txt"), mimetype="text/plain")
    except Exception:
        return "", 404


if __name__ == "__main__":
    app.run(debug=True)
