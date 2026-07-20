# INDEX

## RADS

- `README.md`：目的、架構、操作方式、範圍與已知限制。
- `AGENTS.md`：治理、權限、工程與驗證規範。
- `DECISIONS.md`：CatDrop 已採用的重要技術決策。
- `STATE.md`：目前任務、階段、驗證與阻塞。

## 程式與測試

- `app.py`：Windows 桌面後台與服務生命週期。
- `server.py`：HTTP 路由與檔案接收。
- `core.py`：資料庫與檔案安全規則。
- `ui_text.py`：控制台與設定頁面的繁中／英文文字表。
- `web/`：瀏覽器上傳介面。
- `tests/`：自動化驗證。
- `DEVPOST_PROJECT_STORY.md`：與目前實作一致的 Devpost Project Story。
- `DEMO_SCRIPT.md`：三分鐘內 demo 影片的分鏡、旁白與錄製檢查。
- `SUBMISSION_CHECKLIST.md`：OpenAI Build Week 必填資料與提交前檢查。
- `LICENSE`：MIT License；2026 年著作權人暫記 GitHub 帳號 `magicatJW`。
- `diagnostics.py`：環境、資源、寫入、SQLite、通訊埠與網路診斷。
- `setup.bat`：首次建置、失效環境保留與自動驗證。
- `start.bat`：一般啟動；`start_debug.bat`：前景除錯啟動。
- `check.bat`：完整診斷與測試。
- `.github/workflows/ci.yml`：GitHub push／pull request 驗證。

## 雙語文件

- `docs/zh-TW/governance/`：README 與 RADS 繁中分類鏡像。
- `docs/en/governance/`：README 與 RADS 英文翻譯。
- `docs/zh-TW/project/`、`docs/en/project/`：demo、Devpost Project Story 與 submission checklist。
- `docs/zh-TW/reports/`、`docs/en/reports/`：current 與不可變 history reports 的雙語鏡像。
- 根目錄與 `reports/` 仍是繁中治理正本；英文文件不得取代治理來源。

## 任務報告

- `reports/current.md`：目前任務唯一即時報告。
- `reports/history/`：完成任務後的不可變歷史報告。
- `reports/history/2026-07-19-catdrop-initial-rebuild.md`：CatDrop 初始重建、差異與驗證結果。
- `reports/history/2026-07-19-catdrop-path-and-runtime-tooling.md`：路徑更正、環境建置、自檢、日誌與 GitHub 整備。
- `reports/history/2026-07-20-control-panel-settings.md`：排序、多選、設定頁面與接收狀態同步。
- `reports/history/2026-07-20-all-file-types-and-image-formats.md`：影像格式擴充、全格式支援與安全邊界。
- `reports/history/2026-07-20-device-lan-qrcode.md`：設備區網網址驗證、自動修復、QR Code 與網址複製。
- `reports/history/2026-07-20-devpost-github-preparation.md`：Devpost 文案校正、GitHub 發布準備與提交缺口。
- `reports/history/2026-07-20-github-public-local-preparation.md`：Public repository、MIT License、本機 Git 初始化、納管檢查與推送前阻塞。
- `reports/history/2026-07-20-github-public-release.md`：GitHub CLI 驗證、Public repository 建立、main 推送、遠端一致性與 CI 結果。
- `reports/history/2026-07-20-github-ci-validation.md`：首次 CI 編碼失敗、UTF-8 根因修正、Python 3.11／3.12 PASS 與 Actions 版本治理。
- `reports/history/2026-07-20-bilingual-markdown-docs.md`：所有 Markdown 的繁中／英文分類、翻譯、完整性驗證與 GitHub 推送。
- `reports/history/2026-07-20-bilingual-markdown-ci.md`：雙語文件分支、Draft PR #1 與 Windows Python 3.11／3.12 遠端 CI 證據。
- `reports/history/2026-07-20-devpost-project-sync.md`：Devpost version 6、repository URL、活動要求、桌面互動頁／JSON 與未提交邊界。
- `reports/history/2026-07-20-devpost-docs-github-publish.md`：文件發布分支、Draft PR #3、本機測試與遠端雙版本 CI。
- `reports/history/2026-07-21-devpost-video-update.md`：YouTube demo、Devpost version 7、桌面 JSON 同步與剩餘提交缺口。
- `reports/history/2026-07-21-final-submission-github-publish.md`：正式提交、公開頁與影片稽核、GitHub 文件發布及 Session ID 證據邊界。

## 外部 review 產物

- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Action_Checklist_2026-07-20.html`：可互動待辦確認頁。
- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Update_Report_2026-07-20.html`：本次更新與缺口報告。
- `C:\Users\CatPc\Desktop\CatDrop_Devpost_Todo_State.json`：後續任務優先檢索的人工確認狀態。
