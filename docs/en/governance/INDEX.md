# INDEX

## RADS

- `README.md`: purpose, architecture, operation, scope, and limitations.
- `AGENTS.md`: governance, permissions, engineering, and validation rules.
- `DECISIONS.md`: accepted CatDrop decisions.
- `STATE.md`: current task, stage, validation, and blockers.

## Code and Tests

- `app.py`: Windows control panel and service lifecycle.
- `server.py`: HTTP routes and uploads.
- `core.py`: database and file-safety rules.
- `ui_text.py`: Traditional Chinese and English UI strings.
- `web/`: browser upload interface.
- `tests/`: automated validation.
- Project submission documents: `DEMO_SCRIPT.md`, `DEVPOST_PROJECT_STORY.md`, and `SUBMISSION_CHECKLIST.md`.
- Runtime tools: `diagnostics.py`, `setup.bat`, `start.bat`, `start_debug.bat`, and `check.bat`.
- `.github/workflows/ci.yml`: push and pull-request validation.

## Bilingual Documentation

- `docs/zh-TW/governance/` and `docs/en/governance/`: README and RADS.
- `docs/zh-TW/project/` and `docs/en/project/`: demo, Devpost story, and submission checklist.
- `docs/zh-TW/reports/` and `docs/en/reports/`: current and immutable history reports.
- Root and `reports/` remain the canonical Traditional Chinese governance sources.

## Reports

`reports/current.md` is the only live report. `reports/history/` contains immutable reports for initial rebuild, path/runtime tooling, control-panel settings, image/all-types support, device LAN QR Code, Devpost/GitHub preparation, public release, CI validation, bilingual Markdown documentation, bilingual Draft PR CI evidence, the Devpost project sync, and the Devpost documentation GitHub publish.

## External Review Artifacts

- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Action_Checklist_2026-07-20.html`: interactive review checklist.
- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Update_Report_2026-07-20.html`: update and gap report.
- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Todo_State.json`: user-confirmed state prioritized by later tasks.
