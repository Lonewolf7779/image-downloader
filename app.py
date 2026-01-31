from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from image_downloader import crawl_and_download, zip_images, stop_now, reset_stop_flag
import threading
import os

print("🔥 LOADED NEW app.py WITH PRIVACY ROUTES 🔥")

app = Flask(__name__)

# ===== ROUTES START HERE =====

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return render_template("status.html")

@app.route("/progress")
def get_progress():
    return jsonify({"ok": True})

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ===== ROUTES END HERE =====

if __name__ == "__main__":
    app.run()
