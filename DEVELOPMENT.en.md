# Development and running notes

[中文](DEVELOPMENT.md)

Technical information for contributors. Ordinary users should read [README](README.en.md) first.

## Running from source

macOS is tested; Windows desktop injection is beta. Python 3.9+ and Node.js 22+ are required; no npm install or frontend build is required. On Windows, double-click `Start Bubble Studio.cmd` or `Start Bubble Apps.cmd`, or run `py -3 app/server.py`.

```sh
git clone https://github.com/kaitongg-bit/DIYcodex-bubble.git
cd DIYcodex-bubble
python3 app/server.py
```

Open http://127.0.0.1:19329. `BUBBLE_STUDIO_DATA` sets a private data directory, `BUBBLE_STUDIO_NODE` overrides the Node path, and `--port` sets the studio port.

## Structure

- `app/server.py`: the local asset library, import, presets, recovery area, and system folder picker.
- `app/bridge.mjs`: connects to desktop apps, applies and removes user-message styling.
- `app/static/`: the visual editor, previews, and nine-slice canvas painting; `i18n.mjs` manages the Chinese/English UI, saved in the browser, and never changes bubble presets.
- `tests/`: service tests in isolated temporary directories.
- `.local/`: private assets, favorites, settings, recovery files, and logs; never committed.

## Parameters and connection

PNG supports 2–4096 px per axis; direct imports are limited to 2 MB per file, while connected folders have no such limit. New assets default to at most 240×98 page pixels; existing presets are not overwritten. Scale ranges 1%–200%; 100% is the original pixel size. Text size does not scale with the artwork.

Corner radius 0 keeps the original image; border width 0 disables the outline. The radius crops the canvas corners; the extra border strokes the canvas outline. Adjustments never rewrite the PNG.

Runtime styles are injected through the CDP port bound to `127.0.0.1:19327`; the official app bundle is never modified. Nine-slice is painted onto a single canvas to avoid seams. The match count is the number of currently mounted user messages and may be 0 during virtualization or page switches. The debug port is visible to local processes; fully quitting and restarting the desktop app closes it. Closing the studio does not auto-remove injected styles; restore first or fully restart the app.

Only macOS desktop builds are verified on real devices so far. Windows service and launcher paths have mocked tests, but Store paths, CDP flags, and page selectors still need Windows acceptance; app updates may require adaptation.

The Windows launcher is `scripts/windows-launch.py`, invoked by the two `.cmd` files. The server searches common installation paths and then Microsoft Store packages from expected publishers. `BUBBLE_STUDIO_CODEX_EXE` and `BUBBLE_STUDIO_DOUBAO_EXE` can point to the actual executable. An already running app is never force-quit; users are asked to exit it completely first.

`Start Bubble Apps.command` starts the local studio and calls `/api/launch-active`, launching each configured app with its own CDP port. The per-platform monitor then reconnects and reapplies the saved style. A normally launched app cannot gain a debugging port after startup, so the endpoint asks the user to quit it manually and never terminates the process itself.

## Verification

```sh
python3 -m unittest discover -s tests -v
node --check app/bridge.mjs
node --check app/static/app.js
```

Screenshots and local acceptance checks must use isolated demo data, without private assets, paths, or chats. Historical acceptance records stay in git history and are not published as end-user documentation.

## Static gallery and chat simulation

`codex-preview.mjs` and `codex-preview.css` provide a standalone DOM simulator sharing the nine-slice painting. It simulates only user messages with a background; assistant content keeps normal styling, with no real accounts, chats, or models.

`presets/manifest.json` manages the built-in PNGs and their authorized distribution configuration. On first read, the local library copies them to the private data directory without overwriting user settings; deleted presets are not rebuilt automatically and return only through an explicit restore.

`python3 scripts/export-gallery.py /tmp/bubble-gallery` exports the zero-backend site. The local `/gallery` uses local download counts; the static page reads public GitHub Releases PNG download statistics. PNG private previews use browser Blob URLs and upload nothing. Community inclusion rules are in [COMMUNITY.en.md](COMMUNITY.en.md).

Only the exported gallery files are published to the repo's `gh-pages` branch for GitHub Pages; they never enter the default `main` branch or source downloads. Clone `main` to develop the local studio. When publishing Pages, run the export script first, then commit the generated output on the deploy branch.

## Two-platform adaptation

`app/platforms.mjs` defines the Codex (19327) and Doubao (19326) ports, default user-message selectors, and page allowlists. The studio port stays 19329. `bridge.mjs <state> <action> <platform>` picks the platform explicitly; it tolerates per-page failures but reports `connected: false` when every page fails. Advanced overrides live in the private `platforms.<key>.userSelector` and never reuse the old top-level selector or heuristic scans.

Private state `platforms.codex.active` / `platforms.doubao.active` stores each app snapshot; the old top-level active migrates to Codex. Top-level active/debugPort remain a compatibility view of the selected platform and sync their snapshot on save. Original presets, favorites, and the asset library stay shared. Background monitors per platform use only their snapshot; the API rejects writes carrying a stale platform marker.

Extra bridge tests: `node --test tests/bridge.test.mjs`. Real-device launches must never force-quit any app; older standalone studios must not monitor simultaneously.

## Anonymous submission intake

See [community/DEPLOYMENT.md](community/DEPLOYMENT.md) for Worker secrets, Turnstile, the private queue, owner-only moderation, and the verified local acceptance boundary. Regression tests: `node --test tests/submissions.test.mjs`.
