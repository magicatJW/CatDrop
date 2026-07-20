# Current Task Report

- Date: 2026-07-19
- Objective: correct `CarDrop` to `D:\Projects\CatDrop` and create convenient, diagnosable, GitHub-ready setup/start tooling.
- Scope: rename, batch/PowerShell launchers, diagnostics, rotating logs, tests, GitHub Actions/issue form, and RADS; no product-scope change.
- Output: corrected path; setup/start/debug/check/build scripts; `diagnostics.py`; logs; 18 tests; CI and issue template.
- Behavior: find Python 3.11/3.12, preserve broken `.venv`, install dependencies, fail explicitly, run quick/full checks, use `pythonw` normally, and retain foreground debug output.
- Diagnostics: Python, Tkinter, qrcode, Pillow, resources, write access, SQLite, TCP 8080, and LAN address; report saved to `logs/diagnostic-latest.txt`.
- Validation: fresh Python 3.12.13 environment, diagnostics PASS, 18/18 tests, JavaScript, nine Python files, five PowerShell scripts, and Traditional Chinese console output PASS.
- Remaining at that time: remote Actions, formal-path environment, physical device, firewall, GUI, and EXE packaging.
