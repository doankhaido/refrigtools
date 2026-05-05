# Refrigerant Handling AU/NZ — offline field tool

A standalone Progressive Web App (PWA) for refrigerant handling per the
Australia and New Zealand Refrigerant Handling Code of Practice 2025 Edition.

Works fully offline once installed. No data leaves the device. No accounts.

## What's in the box

- `index.html` — main UI shell
- `app.js` — all data and logic
- `sw.js` — service worker (handles offline caching)
- `manifest.json` — install metadata
- `icon-192.png` / `icon-512.png` — home-screen icons

## Features

- **Refrigerant tab** — search 30 refrigerants (HFC, HCFC, blends, HFO, hydrocarbons, naturals). Type or use the dropdown. Shows GWP (AR4 for AU, AR5 for NZ), ODP, safety class, ADG transport class, fill ratio and LFL.
- **Calc tab** — Safe Fill Capacity, Leak inspection frequency (AS/NZS 5149.4 alongside EU F-Gas), drop test pass/fail, flare torque table.
- **Tools tab** — Minimum room area for A2L installs, temperature-corrected cylinder fill mass, tCO₂e calculator with F-Gas tier indicator.
- **Procedure tab** — step-by-step checklists for evacuation (deep + triple), leak tightness test, charging, recovery, decommissioning. Each has a **Copy checklist** and **Share** button that produces a fillable text form for job records.
- **Reference tab** — quick lookups for label fields, logbook entries, leak detection methods, prohibited charging rules, banned discharge practices, who can do the work.

## How to install and use

### Option 1 — Run on your own server (e.g. company intranet)

1. Copy all five files to any web server that serves over HTTPS (required for PWA install).
2. Visit the URL on a phone.
3. Browser will prompt to "Install app" or "Add to home screen".
4. Once installed, the app icon appears on the home screen and works without signal.

### Option 2 — Free static hosting

Drop the folder on any of these (all free, all support HTTPS):

- **Netlify Drop** — drag the folder to https://app.netlify.com/drop
- **Cloudflare Pages** — connect to a git repo
- **GitHub Pages** — push to a repo, enable Pages in settings
- **Vercel** — `vercel deploy` from the folder

### Option 3 — Local LAN (no internet)

Useful if your team works offline. Run a small HTTPS server on a workshop laptop:

```bash
# Python (needs a self-signed cert)
python -m http.server 8000
```

This won't trigger the install prompt over plain HTTP — service workers require HTTPS or `localhost`. For LAN use, look at `mkcert` to make a trusted local cert.

## Updating the data

All refrigerant data, GWPs, procedure steps, and reference content live in
`app.js`. To update:

1. Edit `app.js`.
2. Bump the cache version in `sw.js` (line 2: change `'refrig-v2'` to `'refrig-v3'`).
3. Redeploy.

Users' devices will fetch the new version next time they're online; the old version keeps working until then.

## What's still on the user

Some calculations are simplified estimates (clearly marked in the UI):

- The minimum room area calculation uses a simplified Annex GG-style formula. **The manufacturer's stated minimum floor area on the install instructions is the actual requirement** — this is for early-stage planning.
- Density values for temperature-corrected fill are typical values. For precise work, refer to NIST REFPROP.
- AR5 GWP values for NZ: a few values (R407F, R450A, R515B) are best-estimate. If you have official MfE values to substitute in, they go in `app.js` under `gwp_nz`.

## Disclaimer

This tool summarises requirements from the public Australia and New Zealand
Refrigerant Handling Code of Practice 2025 Edition for field reference. It
does not replace the code itself, manufacturer instructions, or applicable
legislation. Always cross-check critical values against the source documents
and the equipment nameplate.
