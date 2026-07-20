# CatDrop

## 文件語言

- 繁體中文：根目錄 RADS 為治理正本；本分類位於 [`docs/zh-TW/`](../)。
- English: complete English documentation is organized under [`docs/en/`](../../en/).
- 文件分類：`governance`（治理）、`project`（專案與提交）、`reports`（任務報告）。

CatDrop 是在 Windows 主要電腦上執行的私人區網檔案接收工具。任何連接到相同私人網路、且具備瀏覽器的裝置，都可直接將檔案傳送至主要電腦，不經外部雲端服務。

## 架構與範圍

- `app.py`：Tkinter 後台、服務生命週期、設定、紀錄與 QR Code。
- `server.py`：本機 HTTP 服務、靜態頁面與檔案上傳。
- `core.py`：SQLite、檔名清理、檔案格式與唯一檔名規則。
- `web/`：繁體中文／英文瀏覽器上傳頁面。
- `tests/`：核心、前端與實際 HTTP 整合測試。

CatDrop 僅供可信任的私人區域網路使用，不包含 AI Agent、自動分類、雲端同步或外網公開功能。

## OpenAI Build Week 開發方式

本專案在 OpenAI Build Week 使用 Codex 與 GPT-5.6 協作開發。Codex 用於檢索參考架構、拆分小步任務、實作與審查功能、建立回歸測試、診斷 Windows 行為，以及維護 README、決策、狀態、索引與不可變任務報告。所有產出均以正式 Windows 環境、自動化測試、GUI smoke test 或實體裝置證據驗證；缺少證據的項目不標記為 PASS。

Devpost 專案故事草稿位於 `DEVPOST_PROJECT_STORY.md`，demo 分鏡位於 `DEMO_SCRIPT.md`，提交前檢查表位於 `SUBMISSION_CHECKLIST.md`。

## 控制台與設定

檔案接收控制台支援：

- 點擊狀態、來源名稱、原始檔名、大小或上傳時間欄位進行升冪／降冪排序。
- 使用 Ctrl、Shift、滑鼠按住拖曳或「全選」選取多筆檔案紀錄。
- 對多筆紀錄執行標記已處理、開啟或刪除。
- 以「產生 QR Code」重新偵測並驗證目前設備的區網網址，成功後才建立圖碼。
- 以「複製網址」將驗證後的區網網址寫入 Windows 剪貼簿。
- 由右上角「設定」開啟獨立設定頁面。

設定頁面可調整：

- 控制台語言：繁體中文或英文；同時作為網頁首次開啟的預設語言。
- 檔案儲存路徑與單檔大小上限。
- 登入 Windows 後自動啟動。
- 支援的檔案類型；預設只能從程式既有白名單勾選，網頁與伺服器會同步套用。
- 全格式支援；預設不啟用，啟用後個別格式選項會鎖定。
- 開放或暫停檔案上傳。
- 是否在控制台右上角顯示接收狀態按鈕，預設啟用。

接收狀態按鈕顯示時，設定頁面的開放／暫停選項會鎖定，狀態只能由控制台按鈕切換。隱藏按鈕後，才可在設定頁面調整。暫停接收不會停止 HTTP 網站；網頁每三秒同步狀態、顯示暫停訊息並停用上傳，伺服器也會以 HTTP 503 拒絕新的上傳請求。

## 安裝與啟動

### 第一次使用

1. 安裝 Python 3.11 或 3.12，並在安裝程式勾選 `Add Python to PATH`（將 Python 加入 PATH）。
2. 雙擊 `setup.bat`。腳本會建立隔離的 `.venv`、安裝套件、執行環境診斷與全部測試。
3. 雙擊 `start.bat`。若環境尚未建立，它會先自動呼叫 `setup.bat`。
4. 若其他裝置無法連線，以系統管理員身分執行 `configure_firewall.bat`，開放私人網路 TCP 8080。

### 日常使用與排錯

- `start.bat`：執行快速自檢後，以無命令視窗模式啟動。
- `start_debug.bat`：以前景模式啟動，直接保留錯誤輸出。
- `check.bat`：執行完整環境診斷與所有自動化測試。
- `logs/catdrop.log`：應用程式與 HTTP 服務的輪替錯誤日誌，單檔上限 1 MB，保留三份備份。
- `logs/diagnostic-latest.txt`：最近一次環境診斷報告。

若需要回報問題，請執行 `check.bat`，並附上以下資料：

1. `logs/diagnostic-latest.txt`
2. `logs/catdrop.log` 的相關時間段
3. 重現步驟與畫面顯示的錯誤訊息

診斷報告包含作業系統、Python、相依套件、必要資源、寫入權限、SQLite、TCP 8080 與區網位址檢查，不會收集上傳檔案內容。
公開提交 GitHub issue 前，仍應先檢查並遮蔽個人路徑或裝置名稱；不得上傳 `data/uploads.db` 或 `received_files`。

後台啟動時會偵測目前設備的區網 IPv4 並顯示網址，但不會預先建立可能已失效的 QR Code。按下「產生 QR Code」或「複製網址」時，CatDrop 會重新讀取預設路由與網卡候選位址，逐一確認首頁可透過該私人 IPv4 回應；位址變更時會自動更新控制台。QR Code 驗證成功後存入 `qrcodes`，檔名包含目前設備的區網 IPv4。

自動修復只會重新選擇可用的本機網卡位址，不會修改 Windows 網路、防火牆或路由設定。失敗時會顯示固定錯誤碼：

- `CD-NET-001`：找不到 RFC 1918 私人 IPv4。
- `CD-NET-002`：找到私人 IPv4，但 CatDrop 首頁無法透過候選位址回應。
- `CD-NET-003`：產生 QR Code 前發現網址格式或位址不正確。
- `CD-QR-001`：QR Code 無法寫入 `qrcodes`。
- `CD-CLIP-001`：無法寫入 Windows 剪貼簿。

## 單檔 Windows 應用程式

- 執行 `build_launcher.bat` 產生 `CatDrop.exe`。
- 打包前會先執行完整診斷與自動化測試，失敗時不產生正式執行檔。
- 單檔模式不顯示命令視窗，且不要求目標電腦另行安裝 Python。
- EXE 應留在專案根目錄，才能沿用 `data`、`received_files` 與 `qrcodes`。
- 專案不包含自訂 logo、圖像資產或應用程式圖示。

## 支援格式與安全邊界

白名單模式支援 PDF、DOC、DOCX、XLS、XLSX、CSV、JPG、JPEG、JFIF、PNG、GIF、BMP、WEBP、TIF、TIFF、HEIC、HEIF、AVIF、ICO。

- 同時檢查副檔名與基本檔案內容特徵。
- 單檔預設上限為 100 MB，可由後台調整。
- 來源名稱與檔名會先清理，阻擋目錄穿越與 Windows 禁用名稱。
- 每個檔案使用時間與隨機碼產生唯一儲存名稱，不覆寫既有檔案。
- 上傳紀錄保存在 `data/uploads.db`，檔案預設保存在 `received_files/來源名稱/`。
- 介面語言、支援格式與接收狀態等設定同樣保存在 `data/uploads.db` 的 settings 表。

「全格式支援」是由使用者明確啟用的寬鬆模式。啟用後可接收任何副檔名或無副檔名檔案，並略過副檔名白名單與檔案內容特徵驗證；檔案大小限制、路徑清理與唯一檔名規則仍會執行。此模式不代表任意檔案安全，只應在可信任的私人網路中使用。

升級既有資料庫時，若支援格式仍是舊版完整白名單，CatDrop 會自動加入新影像格式；若使用者曾自訂格式，原勾選內容會完整保留。

## 已知限制

- 服務使用未加密 HTTP，只適合可信任的私人區網。
- 未提供身分驗證或存取碼；常駐執行時，同網路裝置都可嘗試上傳。
- Windows 防火牆規則與實體跨裝置連線仍需在實際網路環境驗證。
- 自動偵測位址取決於 Windows 路由狀態；顯示 `127.0.0.1` 時不代表已具備跨裝置連線能力。
- 本機首頁驗證通過不代表 Windows 防火牆已允許其他實體裝置連線，仍需由實體裝置驗證。

## GitHub 驗證

`.github/workflows/ci.yml` 會在 push 與 pull request 時，於 Windows 的 Python 3.11、3.12 執行：

- 相依套件安裝
- 完整環境診斷
- Python 自動化測試
- JavaScript 語法檢查

GitHub 的錯誤回報表單位於 `.github/ISSUE_TEMPLATE/bug_report.yml`，會要求重現步驟、錯誤訊息、診斷報告與隱私確認。

## 授權

CatDrop 以 [MIT License](../../../LICENSE) 公開授權。著作權聲明使用 GitHub 帳號 `magicatJW`；完整條款請參閱 `LICENSE`。
