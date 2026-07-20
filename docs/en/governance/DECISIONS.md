# DECISIONS

## 2026-07-19 Initial CatDrop Rebuild

- Rebuilt from the verified `D:\Projects\mobile_upload` baseline without copying runtime data, build products, virtual environments, or executables.
- Corrected the mistaken `D:\Projects\CarDrop` path to `D:\Projects\CatDrop`; product and executable names use CatDrop.
- Retained Python `http.server`, `sqlite3`, `tkinter`, HTML/CSS/JavaScript, qrcode, and Pillow. Removed every logo route, asset, conversion step, icon, and packaging dependency.
- Removed print-shop Wi-Fi, fixed-IP, hostname, and old-brand assumptions. LAN IPv4 is detected at startup with explicit `127.0.0.1` fallback.
- The desktop app owns the HTTP lifecycle and uses a Windows mutex. SQLite records, allowlist/signature checks, sanitization, unique names, and overwrite prevention remain.
- AI agents, classification, cloud, public Internet, text transfer, and downloads are outside the initial scope.

## 2026-07-19 Environment, Diagnostics, and Error Reporting

- `setup.bat` finds Python 3.11/3.12, creates or repairs `.venv`, installs dependencies, and runs diagnostics/tests. Broken environments are renamed and preserved.
- `start.bat` performs quick checks and uses `pythonw`; `start_debug.bat` keeps errors visible; `check.bat` runs full validation.
- `diagnostics.py` checks Python, packages, resources, write access, SQLite, TCP 8080, and LAN address, then writes `logs/diagnostic-latest.txt`.
- Rotating `logs/catdrop.log` records startup, Tkinter, HTTP, and unexpected upload errors; 1 MB with three backups.
- GitHub Actions validates Windows Python 3.11/3.12, diagnostics, tests, and JavaScript.

## 2026-07-20 Control Panel Settings and Receiver State

- Sorting uses raw SQLite values. Treeview keeps extended selection and adds drag range and select-all for batch operations.
- Settings remain in the existing SQLite settings table: `ui_language`, `enabled_extensions`, `upload_enabled`, and `show_upload_toggle`.
- Enabled types must be a subset of `ALLOWED_EXTENSIONS`; browser `accept` is only convenience and the server revalidates.
- Pausing keeps the site online, exposes `/api/config`, polls every three seconds, and rejects `/api/upload` with HTTP 503.
- The status button is shown/open by default. When shown it owns and locks the settings-page state. Traditional Chinese/English settings also define the browser default.

## 2026-07-20 Image Formats and All-File-Types Mode

- Added JFIF, AVIF, HEIF, and ICO with signature checks; SVG remains excluded because it may contain active content.
- Added `allow_all_file_types`, default `0`. Enabling it locks individual format controls but preserves selections.
- Legacy full allowlists migrate to the new full set; custom subsets remain unchanged.
- All-types mode accepts any/no extension and skips allowlist/signature validation, but retains size limits, sanitization, unique naming, overwrite prevention, and records. It is not malware protection.

## 2026-07-20 Device LAN URL and QR Code

- QR Codes are generated on demand, never automatically from a possible loopback fallback.
- Before QR generation or URL copying, CatDrop gathers RFC 1918 candidates and verifies an HTTP response. Stale addresses switch to a working candidate.
- Automatic repair only changes the selected application address, never Windows firewall, adapters, or routes.
- QR filenames include the device LAN IPv4. Stable errors are `CD-NET-001`, `CD-NET-002`, `CD-NET-003`, `CD-QR-001`, and `CD-CLIP-001`.

## 2026-07-20 Devpost and GitHub Preparation

- Devpost claims only implemented or evidenced behavior. Unimplemented AI-agent and executable-verification claims were removed.
- Codex/GPT-5.6 usage and human verification responsibility are documented.
- Unknown submitter, country, category, video, repository, and `/feedback` values are never inferred.
- `.gitignore` excludes environments, databases, received files, logs, QR Codes, executables, and build outputs.

## 2026-07-20 Public GitHub Release

- BOSS selected a Public repository and MIT License with `magicatJW` as the 2026 copyright holder.
- The repository uses `main`; the initial commit contains only reviewed project, governance, tests, and release documents.
- Public repository: `https://github.com/magicatJW/CatDrop`. A new repository has no base branch, so the initial release went directly to `main` without a meaningless PR.
- Official portable GitHub CLI 2.96.0 was SHA-256 verified and authenticated as `magicatJW`.
- Initial CI run `29727741928` failed because Windows `cp1252` could not print Traditional Chinese diagnostics. Explicit `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` fixed it without reducing checks.
- Run `29727962166` passed on Python 3.11 and 3.12. Stable `actions/checkout@v6` and `actions/setup-python@v6` were chosen over day-one v7 to remove Node.js 20 warnings.
- Publishing source code does not change CatDrop's trusted-private-LAN boundary.

## 2026-07-20 Bilingual Documentation

- Root README/RADS and `reports/` remain canonical Traditional Chinese sources to preserve restore priority and immutable paths.
- `docs/zh-TW/` and `docs/en/` mirror every canonical Markdown under governance, project, and reports.
- The originally English Devpost story also receives a complete Traditional Chinese translation.
- English files are translations, not an independent decision source. Canonical Traditional Chinese wins on conflict.
- Paths, identifiers, error codes, hashes, URLs, versions, and validation counts are not translated.
