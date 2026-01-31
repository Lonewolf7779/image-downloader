# TODO List for Fixing Image Downloader Issue

- [x] Analyze the issue: User reports downloading "python images" instead of entered website
- [x] Read and understand app.py, image_downloader.py, and test_app.py
- [x] Identify root cause: URLs without protocol (e.g., "python.org") default to HTTP, but normalization to HTTPS improves reliability
- [x] Fix app.py: Add URL normalization to prepend "https://" if missing
- [x] Add logging to background_job in app.py for debugging
- [x] Fix test_app.py: Add URL normalization for consistency
- [ ] Test the fixes to ensure they work correctly
