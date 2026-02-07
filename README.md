cd D:\image_tester
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Genki Image Downloader

Genki is a lightweight Flask app to crawl a website and bundle images into a ZIP. The UI is mobile-first and anime-inspired.

## Quick start

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Run locally:

```bash
python app.py
# or
.venv\Scripts\gunicorn.exe -w 2 -b 0.0.0.0:8000 app:app
```

3. Open http://127.0.0.1:5000 (or port 8000 for gunicorn)

## Preparing for Google AdSense

- Add your AdSense client script into `templates/base.html` where the placeholder comment is.
- Verify site ownership in Google Search Console and replace the `google-site-verification` meta tag in `templates/base.html`.
- Make sure your domain serves pages over HTTPS and contains original content.

## Deployment

- Use a WSGI server like Gunicorn or host on platforms that support Flask apps.
- Set environment variables for production (e.g., `FLASK_ENV=production`).

## Notes

- Respect copyright and robots.txt of target sites when crawling.
- This app is provided as-is. Test downloads responsibly.

# IMAGE_TESTER — simple image analysis & comparison

## Usage:

- Analyze: `python image_tester.py analyze path/to/image.png`
- Compare: `python image_tester.py compare a.png b.png`

Outputs JSON with basic stats (format, size, per-channel mean/std) and simple comparison metrics (MSE, percent pixels different).
