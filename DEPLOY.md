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
1. Create a new Web Service on Render.
2. Connect the repository.
3. Set the `Start Command` to: `gunicorn app:app`.
4. Add environment variables in Render Dashboard: `ADSENSE_CLIENT` and `ADSENSE_AD_SLOT`.

### Render checklist for AdSense

1. In Render → your service → **Environment** add these variables:
	- `ADSENSE_CLIENT` = `ca-pub-XXXXXXXX` (your publisher id)
	- `ADSENSE_AD_SLOT` = `1234567890` (your ad unit id)
2. Commit and push `static/ads.txt` (this repo already has `static/ads.txt`). Ensure it is reachable at `https://<your-site>/ads.txt`.
3. Confirm the site serves `ads.txt` over HTTPS (open `https://<your-site>/ads.txt`).
4. If you changed environment variables, trigger a redeploy or wait for auto-deploy.

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
