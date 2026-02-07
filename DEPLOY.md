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
