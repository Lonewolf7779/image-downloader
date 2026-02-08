Short README snippet — update `static/index.html` to point to backend

1) Replace the "Open the App" anchor in `static/index.html` (default links to `/app`) with your backend subdomain URL. Example:

```html
<!-- Replace app.example.com with your backend service domain -->
<a href="https://app.example.com/app" class="primary" style="text-decoration:none;padding:10px 16px;background:#2b6cb0;color:#fff;border-radius:6px;">Open the App</a>
```

2) Commit and push the change so the static site serves the updated link:

```bash
git add static/index.html
git commit -m "Point landing page to backend app subdomain for production"
git push
```

3) Verification (recommended): after DNS/TLS provisioning on Render:

```bash
curl -I https://example.com/        # should return 200 and landing HTML
curl -I https://app.example.com/app # should return 200 and app HTML
```

Notes:
- Use your actual backend domain in place of `app.example.com`.
- Keep `https://example.com/` mapped to the Render Static Site for instant loading (no cold-start).
- This change optimizes the AdSense reviewer experience by ensuring the reviewer sees the static landing page instantly and can navigate to the interactive app.
