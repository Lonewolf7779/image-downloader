# Deploying Genki Image Downloader

This file describes quick steps to deploy the app and configure AdSense safely.

## Environment variables
- `ADSENSE_CLIENT` — your publisher id, e.g. `ca-pub-1328727126151207`.
- `ADSENSE_AD_SLOT` — the numeric ad unit id (the `data-ad-slot` value), e.g. `1234567890`.

## Local testing

Set env vars and run locally:

PowerShell:
```powershell
$env:ADSENSE_CLIENT="ca-pub-1328727126151207"
$env:ADSENSE_AD_SLOT="REPLACE_WITH_YOUR_AD_SLOT"
python app.py
```

bash / WSL:
```bash
export ADSENSE_CLIENT="ca-pub-1328727126151207"
export ADSENSE_AD_SLOT="REPLACE_WITH_YOUR_AD_SLOT"
python app.py
```

## Deploy to Render
1. Recommended: use a two-service setup so the root `/` is served instantly by a static site (no backend cold start).

	 - Commit the included `render.yaml` in this repository. It defines two services:
		 - `genki-static` — a Render Static Site that publishes the `static/` folder (this will serve `/` immediately).
		 - `genki-backend` — a Python Web Service that runs the interactive backend at its own URL (keeps heavy work off the static front page).

	 - Push the `render.yaml` to your repo, then on Render choose **New → Web Service from Render.yaml** (or similar) to create both services from the manifest.

2. After both services are created:
	 - Assign your primary custom domain (e.g. `example.com`) to the **static** service (`genki-static`). This makes `https://example.com/` serve the static landing page instantly.
	 - Assign a subdomain for the backend (e.g. `app.example.com`) to the **backend** service (`genki-backend`). This will be the interactive app URL.

3. Update `static/index.html` to point the "Open the App" link at your backend host (for example `https://app.example.com/app`). By default the file links to `/app` — update it to the backend subdomain after you map domains on Render.

4. Environment variables and ads:
	 - Do not commit your AdSense secrets. In Render → your service → **Environment** add:
		 - `ADSENSE_CLIENT` = `ca-pub-XXXXXXXX` (your publisher id)
		 - `ADSENSE_AD_SLOT` = `1234567890` (your ad unit id)
	 - Add these to the **backend** service; the static site does not need them.

5. Verify `ads.txt` is served from the static site at `https://example.com/ads.txt` (the repo already contains `static/ads.txt`).

### Why this helps

- Serving the landing page as a static site eliminates Render cold-start delays for `/`, which removes the wake screen Google reviewers often encounter.
- Keeping the interactive downloader on a separate backend service prevents the static front page from depending on the backend to load.

### Notes & options

- If you prefer the interactive experience at the same domain path (`/app`) instead of a subdomain, you can either:
	- Update the static site to redirect `/app` to your backend subdomain, or
	- Configure a proxy/rewrite (if using a CDN or reverse proxy) to forward `/app` to the backend service. (Render static sites do not automatically proxy arbitrary paths to a secondary service.)
- After DNS and domain mapping changes, trigger redeploys or wait for Render to finish certificate provisioning.

### Render checklist for AdSense (quick)

1. Ensure `static/ads.txt` is committed and publicly reachable at your root domain.
2. Confirm `Privacy`, `Terms`, and `Contact` pages are linked from the landing page footer.
3. Verify the landing page loads instantly and the interactive app is reachable from the link you configured.
4. Request AdSense review once verification and `ads.txt` are in place.

## Verify with Google

1. Add and verify your site in Google Search Console (use the exact domain you added to AdSense).
2. In Google AdSense → Sites, add your site URL and wait for status updates. AdSense will check for `ads.txt`, site availability, and the ad code.

## ads.txt example
Place this exact line in `static/ads.txt` (already added in this repo):

```
google.com, pub-1328727126151207, DIRECT, f08c47fec0942fa0
```

Do not include the publisher id in source code; use the environment variables described above.

## Privacy, consent and policy

- Keep a visible `Privacy` page (present in this repo) and maintain a cookie/consent flow. The app includes a consent banner that controls when the AdSense script is loaded.
- Ensure your site does not host or promote copyrighted or disallowed content; AdSense will reject sites that violate policies.

## Request review

After `ads.txt` is served and Search Console verification is complete, request an AdSense review in the AdSense dashboard. Approval can take several days.

## Quick commands

PowerShell:
```powershell
git add static/ads.txt DEPLOY.md
git commit -m "Add ads.txt & deploy notes for AdSense"
git push
```

Bash:
```bash
git add static/ads.txt DEPLOY.md
git commit -m "Add ads.txt & deploy notes for AdSense"
git push
```

## Deploy to Heroku
```bash
heroku create my-genki-app
heroku config:set ADSENSE_CLIENT="ca-pub-1328727126151207"
heroku config:set ADSENSE_AD_SLOT="REPLACE_WITH_YOUR_AD_SLOT"
git push heroku main
heroku ps:scale web=1
```

## Notes
- Do NOT embed your AdSense script or client id directly in committed source if you want to keep configuration flexible; use environment variables.
- Replace the `ADSENSE_AD_SLOT` placeholder with your ad unit id.
- AdSense requires site verification and policy compliance — ensure your site meets AdSense policies before enabling ads.
