# Current Task Report

- Date: 2026-07-20
- Objective: add common image formats and default-off all-file-types support.
- Scope: settings, SQLite, HTTP API, browser, tests, and RADS; no AI agent, cloud, or Internet features.
- Output: JFIF, AVIF, HEIF, ICO; all-types toggle; locked individual controls; frontend sync; server enforcement.
- Rules: migrate only legacy full allowlists; preserve custom subsets. Validate JPEG/JFIF, ISO Base Media brands, and ICO headers. SVG remains excluded.
- Boundary: all-types skips allowlist/signature checks but retains size, sanitization, unique naming, overwrite prevention, and records; it is not malware protection.
- Validation: diagnostics PASS, 32/32 tests, hidden GUI smoke test, migration and arbitrary/no-extension tests PASS. Existing upload, duplicate, path, and UTF-8 tests remained green.
- Remaining: physical uploads for new formats, firewall, EXE, and remote Actions.
