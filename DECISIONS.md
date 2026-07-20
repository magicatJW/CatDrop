# DECISIONS

## 2026-07-19 CatDrop 初始重建

- 來源基線為 `D:\Projects\mobile_upload`，依 2026-07-19 可讀取內容重建；不複製既有資料、建置產物、虛擬環境或執行檔。
- 初始建立時的 `D:\Projects\CarDrop` 為路徑誤植；依 BOSS 於 2026-07-19 的更正，正式路徑改為 `D:\Projects\CatDrop`，產品顯示名稱與執行檔名稱均使用 `CatDrop`。
- 保留 Python 標準函式庫 `http.server`、`sqlite3`、`tkinter` 與原有 HTML/CSS/JavaScript 架構，不引入網站框架。
- 保留 qrcode 與 Pillow，僅用於離線產生網站 QR Code；移除全部 logo 轉檔流程、logo 路由、logo 圖像、圖示與打包依賴。
- 移除店內固定 Wi-Fi、固定 IP 與 `upload.local` 假設；啟動時依目前路由自動偵測區網 IPv4 位址，失敗時明確回退至 `127.0.0.1`。
- 保留「後台啟動即啟動 HTTP 服務，關閉後台即停止服務」的生命週期與 Windows 命名 Mutex 單例控制。
- 保留來源名稱分層、SQLite 紀錄、格式白名單、檔頭驗證、路徑清理與唯一檔名；使用者可讓程式常駐，但目前不提供驗證機制。
- 初始版本不包含 AI Agent、自動分類、雲端、外網公開、文字傳送或下載功能。

## 2026-07-19 環境、自檢與錯誤回報

- `setup.bat` 負責尋找 Python 3.11/3.12、建立或修復 `.venv`、安裝相依套件、執行診斷與測試；失效的既有 `.venv` 先改名保留，不直接刪除。
- `start.bat` 執行快速自檢後使用 `pythonw` 啟動；`start_debug.bat` 提供可見終端輸出的除錯入口；`check.bat` 執行完整診斷與測試。
- `diagnostics.py` 僅使用 Python 標準函式庫，檢查版本、相依套件、必要資源、寫入權限、SQLite、TCP 8080 與區網位址，結果寫入 `logs/diagnostic-latest.txt`。
- 應用程式使用標準函式庫輪替日誌，寫入 `logs/catdrop.log`，單檔 1 MB 並保留三份備份；未處理的啟動、Tkinter 回呼與上傳錯誤皆記錄例外資訊。
- GitHub Actions 在 Windows 的 Python 3.11、3.12 執行診斷、Python 測試與 JavaScript 語法檢查。

## 2026-07-20 控制台設定與接收狀態

- 排序在控制台以 SQLite 原始欄位值執行，避免格式化後的檔案大小或顯示文字造成錯誤順序；點擊同欄位切換升降冪。
- Treeview 保留 `extended` 多選，另加入滑鼠拖曳範圍與全選；批次標記、開啟與刪除均使用目前全部選取項目。
- 設定沿用既有 SQLite settings 表，不建立新資料庫或額外設定檔；新增 `ui_language`、`enabled_extensions`、`upload_enabled`、`show_upload_toggle`。
- 可勾選格式只能是程式固定 `ALLOWED_EXTENSIONS` 的子集合；瀏覽器 `accept` 僅改善選檔體驗，伺服器仍以動態白名單與檔頭再次驗證。
- 暫停接收不關閉 HTTP 服務，確保網頁仍能顯示狀態；`/api/config` 提供動態設定，網頁每三秒輪詢，暫停時 `/api/upload` 回傳 HTTP 503。
- 控制台狀態按鈕預設顯示且預設開放；按鈕顯示時鎖定設定頁面的接收狀態，隱藏時才允許由設定頁面更動。
- 控制台語言保存為繁中或英文，並作為網頁初次載入的預設語言；網頁使用者仍可自行切換當次語言。

## 2026-07-20 影像格式與全格式支援

- 白名單新增 JFIF、AVIF、HEIF、ICO；分別使用 JPEG、ISO Base Media File Format 品牌與 ICO 檔頭驗證。SVG 因可包含主動內容，不納入本次「常用且安全性高」影像格式。
- 新增 `allow_all_file_types` SQLite 設定，預設值為 `0`；啟用後設定頁面的個別格式選項鎖定，既有個別勾選值保留。
- 既有 `enabled_extensions` 若等於舊版完整白名單，啟動時自動遷移為新版完整白名單；任何自訂子集合均不更動。
- 全格式模式會接受任意副檔名或無副檔名檔案，並略過副檔名白名單與檔案內容特徵驗證；仍執行大小限制、來源名稱／檔名清理、唯一檔名、防覆寫與本機紀錄。
- `/api/config` 新增 `allowAllFileTypes`，網頁同步顯示全格式狀態、取消 `accept` 限制並停止前端副檔名篩選；伺服器仍是最終執行邊界。
- 全格式模式明確降低檔案驗證強度，介面與 README 必須揭露風險；不將其描述為安全檔案掃描、惡意程式防護或內容安全保證。

## 2026-07-20 裝置區網網址與 QR Code

- QR Code 改為由控制台按鈕按需產生，不再於程式啟動時用可能回退為 `127.0.0.1` 的網址自動建立。
- 產生 QR Code 與複製網址前，重新收集預設路由及主機網卡的 RFC 1918 IPv4，並以 HTTP 首頁回應確認候選位址；目前網址失效時自動切換至可回應位址。
- 自動修復限定為應用程式內重新選址與更新顯示，不自動變更 Windows 防火牆、網卡或路由設定。
- QR Code 檔名包含接收設備的區網 IPv4，不覆寫不同位址的既有 QR Code。
- 網路、QR 寫入與剪貼簿錯誤使用固定錯誤碼 `CD-NET-001`、`CD-NET-002`、`CD-NET-003`、`CD-QR-001`、`CD-CLIP-001`，並寫入應用程式日誌。

## 2026-07-20 Devpost 與 GitHub 提交準備

- Devpost Project Story 只描述已實作或有證據的功能；移除未實作 AI Agent，並將正式 EXE、實體裝置與遠端 CI 保留為未驗證項目。
- Build Week 說明明確記錄 Codex 與 GPT-5.6 的用途，同時保留人工審查與正式環境驗證責任，不將生成內容視為自動正確。
- Devpost `Built with` 更新為實際技術棧與開發工具；未取得的影片、repository URL、提交者身分、居住國家及 `/feedback` Session ID 不自行填入。
- GitHub 發布前新增 Project Story、demo 腳本與 submission checklist；不初始化 repository、不發布遠端、不選擇開源授權，直到 BOSS 明確決定公開性與授權條款。
- `.gitignore` 持續排除資料庫、接收檔案、日誌、QR Code、虛擬環境、EXE 與建置產物，避免將執行資料帶入 repository。

## 2026-07-20 GitHub 公開發布設定

- BOSS 指定 GitHub repository 採 Public；本輪只完成本機發布準備，不建立遠端 repository、不設定 remote、不推送。
- 授權採 MIT License，以 GitHub 帳號 `magicatJW` 作為 2026 年著作權人；正式推送前可由 BOSS 更正著作權名稱。
- 本機 repository 使用 `main` 作為初始分支，首次提交只納入已辨識的專案、治理、測試與發布文件。
- `.venv`、`__pycache__`、`data`、`logs`、`qrcodes`、`received_files`、EXE 與建置產物維持排除，不得因公開發布而納入版本控制。
- 正式發布前必須再次確認 staged files、測試結果、GitHub CLI 登入狀態及 remote 目標；BOSS 完成 review 前禁止 push。

## 2026-07-20 GitHub Public 正式發布

- BOSS 完成最終確認後，建立 Public repository `magicatJW/CatDrop`，遠端網址為 `https://github.com/magicatJW/CatDrop`。
- 初始分支直接使用 `main`；這是全新 repository，沒有既有 base branch，因此不建立無意義的初始 pull request。
- 首次推送的 commit 為 `938b438b2a36d163c66830a988f7b1670a234cc4`，本機與 `origin/main` 雜湊一致。
- 正式發布使用官方 GitHub CLI 2.96.0 Windows amd64 portable ZIP，下載後依 GitHub release metadata 驗證 SHA-256，再以 BOSS 的 `magicatJW` 帳號登入。
- Public repository 仍維持私人 LAN 使用邊界；公開原始碼不代表服務可安全暴露至外網。
- 首次 GitHub Actions run `29727741928` 在 Windows runner 以 `cp1252` 輸出繁體中文診斷文字時失敗；CI job 明確設定 `PYTHONUTF8=1` 與 `PYTHONIOENCODING=utf-8`，不修改診斷內容或降低測試範圍。
