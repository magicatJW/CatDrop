# CatDrop

## Documentation Languages

- Traditional Chinese canonical documentation: [`../../../README.md`](../../../README.md) and [`../../zh-TW/`](../../zh-TW/)
- English documentation: [`../`](../)
- Categories: `governance`, `project`, and `reports`

CatDrop is a private LAN file receiver for a primary Windows computer. Any browser-equipped device on the same trusted network can send files directly to the computer without an external cloud service.

## Architecture and Scope

- `app.py`: Tkinter control panel, service lifecycle, settings, records, and QR Codes.
- `server.py`: local HTTP service, static page, and uploads.
- `core.py`: SQLite, name sanitization, file-format rules, and unique filenames.
- `web/`: Traditional Chinese and English browser interface.
- `tests/`: core, frontend, and real HTTP integration tests.

CatDrop is limited to trusted private LANs. It does not include AI agents, automatic classification, cloud synchronization, or public-Internet exposure.

## OpenAI Build Week Development

Codex with GPT-5.6 was used to inspect the reference architecture, split work into verifiable tasks, implement and review features, create regression tests, diagnose Windows behavior, and maintain persistent RADS documentation. Results were checked in the real Windows environment with automated tests, GUI smoke tests, or physical-device evidence. Missing evidence is never reported as PASS.

## Control Panel and Settings

The receiver console supports sortable columns, Ctrl/Shift/drag multi-selection, batch processing, on-demand verified QR Code generation, URL copying, and a separate settings window.

Settings cover Traditional Chinese/English, storage location, per-file size limit, Windows sign-in startup, enabled file types, optional all-file-types mode, upload open/pause state, and visibility of the console status button. When the status button is shown, it owns the upload state and locks that setting in the settings window. Pausing keeps the status page online, disables browser upload controls, and makes the server reject uploads with HTTP 503.

## Installation and Startup

1. Install Python 3.11 or 3.12 and add it to PATH.
2. Run `setup.bat` to create `.venv`, install packages, diagnose the environment, and run all tests.
3. Run `start.bat`; it invokes setup automatically if needed.
4. If other devices cannot connect, run `configure_firewall.bat` as administrator to allow private-network TCP 8080.

Daily tools:

- `start.bat`: quick check and background startup.
- `start_debug.bat`: foreground startup with visible errors.
- `check.bat`: full diagnostics and tests.
- `logs/catdrop.log`: rotating application and HTTP log, 1 MB with three backups.
- `logs/diagnostic-latest.txt`: latest environment report.

Before filing a public issue, redact personal paths and device names. Never upload `data/uploads.db` or `received_files`.

The console detects the current private IPv4 address but does not pre-generate a potentially stale QR Code. Generate QR Code and Copy URL re-read route and adapter candidates, verify that the homepage responds through the address, and update stale addresses automatically. Repairs only select another local address; they never change Windows firewall, adapters, or routes.

Stable error codes are `CD-NET-001`, `CD-NET-002`, `CD-NET-003`, `CD-QR-001`, and `CD-CLIP-001`.

## Standalone Windows Application

Run `build_launcher.bat` to create `CatDrop.exe`. Packaging is blocked unless diagnostics and tests pass. The one-file build has no console window and does not require Python on the target computer. Keep it in the project root to reuse `data`, `received_files`, and `qrcodes`. The project contains no custom logo or application icon.

## Supported Formats and Security Boundary

Allowlist mode supports PDF, DOC, DOCX, XLS, XLSX, CSV, JPG, JPEG, JFIF, PNG, GIF, BMP, WEBP, TIF, TIFF, HEIC, HEIF, AVIF, and ICO. It checks the extension and basic signature, defaults to 100 MB per file, sanitizes source names and filenames, prevents traversal, and stores every upload under a unique non-overwriting name. Records and settings are stored in `data/uploads.db`.

All-file-types mode is opt-in. It accepts any extension or no extension and skips allowlist/signature validation, while size limits, path sanitization, unique naming, overwrite prevention, and records remain active. It is not malware protection and is only appropriate on a trusted LAN.

## Known Limitations

- HTTP is unencrypted and suitable only for trusted private LANs.
- There is no authentication or access code.
- Windows Firewall and full cross-device reachability require physical testing.
- `127.0.0.1` does not provide cross-device access.
- A successful local homepage check does not prove firewall reachability from another device.

## GitHub Validation

`.github/workflows/ci.yml` runs on push and pull request with Windows Python 3.11 and 3.12. It installs dependencies, runs full diagnostics and Python tests, and checks JavaScript syntax. The structured issue form requests reproduction steps, errors, diagnostics, and privacy confirmation.

## License

CatDrop is available under the [MIT License](../../../LICENSE), copyright `magicatJW`.
