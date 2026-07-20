# CatDrop Demo Script

Target length: 2:30–2:50. The video must be public on YouTube and include narration.

## 0:00–0:20 — Problem and Positioning

Visual: phone, tablet, Windows computer, then the CatDrop console.

Narration:

> I often need to move files from phones, tablets, and development devices to my main computer. CatDrop gives every device on my trusted local network a simple browser-based file drop, without routing personal files through an external cloud service.

## 0:20–0:50 — Startup and Connection

Visual: start CatDrop, show the LAN URL, click Generate QR Code, then Copy URL.

> Starting the Windows control panel starts the local receiving service. Before generating a QR Code or copying the URL, CatDrop rechecks the computer's private LAN addresses and verifies that the homepage responds. If the computer changed networks, it can replace a stale address automatically.

## 0:50–1:25 — Phone Upload

Visual: scan QR Code, open page, enter source name, select multiple files, and upload.

> The sending device only needs a browser. I can select multiple files, confirm the source name, and upload directly to the computer. Traditional Chinese names and filenames are handled as UTF-8, and duplicate filenames never overwrite earlier files.

## 1:25–1:55 — Console and Pause

Visual: new record, status sorting, multi-select, mark processed, pause receiving, and show synchronized phone page.

> The control panel keeps local upload records, supports sorting and multi-selection, and lets me pause new uploads without taking down the status page. The browser synchronizes the state, while the server independently rejects uploads when paused.

## 1:55–2:20 — Settings and Security Boundary

Visual: language, formats, size limit, and all-file-types warning.

> By default, CatDrop uses an extension allowlist plus basic file-signature validation. It also sanitizes paths and generates unique stored names. An optional all-file-types mode is available for trusted environments, but it clearly warns that signature validation is disabled.

## 2:20–2:45 — Codex and GPT-5.6

Visual: README, test output, RADS, and 37 tests PASS.

> I used Codex with GPT-5.6 to inspect the original architecture, plan incremental changes, implement and review features, build regression tests, diagnose Windows behavior, and maintain persistent project decisions. I validated the result with 37 automated tests, GUI smoke tests, and a real LAN QR Code runtime check.

## 2:45–2:55 — Closing

Visual: successful phone upload, received record, CatDrop title.

> CatDrop keeps one job simple: start it, send files across your private network, and close it when you're done.

## Recording Checklist

- Do not show private file contents, user paths, email, or a real database.
- Use test files and non-identifying source names.
- YouTube must be Public, not Private or Unlisted.
- Total duration must stay under three minutes.
- Clearly explain how Codex and GPT-5.6 were used.
