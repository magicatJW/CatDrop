# CatDrop Demo Script

目標長度：2 分 30 秒至 2 分 50 秒。影片需公開上傳至 YouTube，並包含語音。

## 0:00–0:20 — 問題與定位

畫面：手機、平板與 Windows 電腦，接著顯示 CatDrop 控制台。

旁白：

> I often need to move files from phones, tablets, and development devices to my main computer. CatDrop gives every device on my trusted local network a simple browser-based file drop, without routing personal files through an external cloud service.

## 0:20–0:50 — 啟動與連線

畫面：啟動 CatDrop，顯示區網網址，按下「產生 QR Code」，再按「複製網址」。

旁白：

> Starting the Windows control panel starts the local receiving service. Before generating a QR Code or copying the URL, CatDrop rechecks the computer's private LAN addresses and verifies that the homepage responds. If the computer changed networks, it can replace a stale address automatically.

## 0:50–1:25 — 手機上傳

畫面：手機掃描 QR Code、開啟網頁、輸入來源名稱、選擇多個檔案並上傳。

旁白：

> The sending device only needs a browser. I can select multiple files, confirm the source name, and upload directly to the computer. Traditional Chinese names and filenames are handled as UTF-8, and duplicate filenames never overwrite earlier files.

## 1:25–1:55 — 控制台與暫停

畫面：控制台出現新紀錄；依狀態排序、多選、標記已處理；切換暫停接收並展示手機頁面同步。

旁白：

> The control panel keeps local upload records, supports sorting and multi-selection, and lets me pause new uploads without taking down the status page. The browser synchronizes the state, while the server independently rejects uploads when paused.

## 1:55–2:20 — 設定與安全邊界

畫面：開啟設定，展示語言、檔案類型、大小限制與全格式支援警告。

旁白：

> By default, CatDrop uses an extension allowlist plus basic file-signature validation. It also sanitizes paths and generates unique stored names. An optional all-file-types mode is available for trusted environments, but it clearly warns that signature validation is disabled.

## 2:20–2:45 — Codex 與 GPT-5.6

畫面：README、測試輸出、RADS 文件與 37 tests PASS。

旁白：

> I used Codex with GPT-5.6 to inspect the original architecture, plan incremental changes, implement and review features, build regression tests, diagnose Windows behavior, and maintain persistent project decisions. I validated the result with 37 automated tests, GUI smoke tests, and a real LAN QR Code runtime check.

## 2:45–2:55 — 結尾

畫面：手機成功上傳、控制台收到檔案、CatDrop 標題。

旁白：

> CatDrop keeps one job simple: start it, send files across your private network, and close it when you're done.

## 錄製檢查

- 不顯示私人檔案內容、使用者路徑、電子郵件或真實資料庫。
- 使用測試檔案與不具識別性的來源名稱。
- YouTube 設為 Public，不可設為 Private 或 Unlisted。
- 總長不得超過 3 分鐘。
- 必須清楚說明 Codex 與 GPT-5.6 的使用方式。
