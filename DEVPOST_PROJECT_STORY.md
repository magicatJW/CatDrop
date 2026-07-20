## Inspiration

I regularly move files between phones, tablets, development boards, laptops, and my main Windows computer. The usual options add friction: uploading to cloud storage, sending files through a messaging app, finding a cable, installing another client, or configuring shared folders on every device.

The idea for **CatDrop** grew from a local file-receiving workflow I had built for a print-shop environment. I realized the useful part was more general:

> Any device already connected to my private network should be able to send a file directly to my main computer through a browser.

CatDrop turns that idea into a small personal productivity tool. I can run it only when I need a temporary receiving endpoint, or leave it available as a private-network inbox.

## What it does

CatDrop runs a local HTTP file receiver on a Windows computer. Any device on the same trusted LAN can open the upload page, select one or more files, and send them directly to the computer without an external cloud service or device-specific client.

The desktop control panel provides:

- A verified LAN URL, one-click URL copying, and on-demand QR Code generation
- Automatic LAN-address recovery when the current address becomes stale
- Upload open/pause control that synchronizes with the browser page
- Sortable upload records and multi-record operations
- Traditional Chinese and English interfaces
- Configurable storage, file-size limits, startup behavior, and supported file types

In the default allowlist mode, CatDrop validates both file extensions and basic file signatures. It sanitizes source names and filenames, prevents directory traversal, and creates unique stored names rather than overwriting existing files. An optional all-file-types mode is available for trusted environments, with an explicit warning that it disables signature validation.

## How we built it

CatDrop deliberately uses a small architecture:

- Python `http.server` for the local HTTP service
- `sqlite3` for settings and upload records
- `tkinter` for the Windows control panel
- HTML, CSS, and JavaScript for the browser interface
- `qrcode` and Pillow for offline QR Code generation
- PyInstaller build scripts for a future standalone Windows executable

The desktop application owns the server lifecycle. Starting CatDrop starts the receiver; closing it shuts the service down. A Windows mutex prevents duplicate instances from competing for the same port.

The browser polls a configuration endpoint so supported formats, language defaults, and upload availability stay synchronized. Pausing uploads leaves the status page available but makes the server reject new uploads with HTTP 503.

For LAN discovery, CatDrop gathers RFC 1918 IPv4 candidates from the default route and Windows network adapters. Before generating a QR Code or copying the URL, it verifies that the CatDrop homepage responds through a candidate address. If the displayed address is stale, the control panel switches to a working candidate. Failures include stable error codes and are written to a rotating log.

I used **Codex with GPT-5.6** throughout Build Week to inspect the reference architecture, break changes into small verifiable tasks, implement features, review security boundaries, generate regression tests, diagnose Windows-specific behavior, and maintain the project's persistent RADS documentation. I reviewed the resulting changes and verified them in the real Windows environment instead of treating generated code as automatically correct.

## Challenges we ran into

Local networking created the most important edge cases. A hostname such as `upload.local` is not reliable unless the router or local DNS environment supports it. A URL can also become stale when a laptop changes networks or adapters. CatDrop therefore uses direct private IPv4 addresses and verifies the actual HTTP endpoint before producing a QR Code.

Windows Firewall is a separate boundary. A server may work on the receiving computer while remaining unreachable from a phone until a private-network firewall rule is installed. CatDrop reports what it can verify locally without claiming that local verification proves external-device reachability.

Multipart form-data also required explicit UTF-8 handling for Traditional Chinese source names and filenames. Packaging introduced another separation: temporary bundled resources and persistent databases, logs, received files, and QR Codes cannot share the same storage assumptions.

The all-file-types option required a clear security decision. Convenience does not make arbitrary files safe, so the default remains a validated allowlist and the broader mode is opt-in with an explicit warning.

## Accomplishments that we're proud of

- A sending device only needs a browser
- Files remain on the trusted local network
- The receiving service has an explicit lifecycle and pause control
- Duplicate names never silently overwrite existing files
- Traditional Chinese names and filenames work correctly
- LAN URLs are verified before QR Code generation
- Environment diagnostics, rotating logs, setup scripts, and CI configuration are included
- The current Windows source build passes 37 automated tests, GUI smoke testing, and a real LAN URL/QR Code runtime check
- The public GitHub repository includes an MIT License and complete Traditional Chinese and English documentation
- GitHub Actions passes on Windows with Python 3.11 and Python 3.12

The source, setup instructions, and validation workflow are available in the [public CatDrop repository](https://github.com/magicatJW/CatDrop).

The core workflow remains simple:

> Start CatDrop, share or scan the verified LAN address, send the files, and close CatDrop when finished.

## What we learned

The upload request itself is only one part of a usable transfer tool. Address discovery, server state, firewall behavior, duplicate handling, filename encoding, storage visibility, and useful error evidence all affect whether the workflow feels reliable.

I also learned that lightweight software still benefits from explicit trust boundaries, persistent decisions, automated regression tests, and honest reporting of missing evidence. A local HTTP check can verify the application and address, but only a physical device can prove the complete LAN and firewall path.

Codex was most useful when paired with small scopes and concrete validation. Keeping README, decisions, current state, indexes, and immutable task reports made it possible to resume work without losing why a feature or boundary existed.

## What's next for CatDrop

- Complete physical-device testing of the newest QR Code flow and image formats
- Validate the packaged standalone Windows executable
- Add an optional temporary access code
- Improve transfer progress and recent-transfer history
- Continue improving the public documentation and reproducible setup workflow

CatDrop is not intended to become another cloud storage platform. It will remain focused on direct, understandable file transfer inside a trusted private network.
