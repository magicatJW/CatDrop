# Project Execution Rules

- Make minimal changes and avoid unnecessary rewrites.
- Default UI language is Traditional Chinese; the frontend also provides English.
- Default uploads require an explicit allowlist and basic signature validation. Only BOSS-authorized all-file-types mode may bypass it, with a visible warning.
- Sanitize paths, filenames, and source names; prevent traversal and overwrites.
- Do not add AI agents, automatic classification, cloud sync, or Internet exposure without BOSS authorization.
- Do not add logo images, logo assets, or logo-only dependencies.
- Record architecture decisions in `DECISIONS.md` and progress, validation, and blockers in `STATE.md`.
- Update `reports/current.md` for every task and create a matching immutable history report when complete.
- All code comments must use Traditional Chinese.
- Root RADS and `reports/` are the canonical Traditional Chinese governance sources. `docs/zh-TW/` and `docs/en/` are categorized language mirrors. English translations must not change canonical decisions.
