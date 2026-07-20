# Current Task Report

- 日期：2026-07-19
- objective：將誤植的 `D:\Projects\CarDrop` 更正為 `D:\Projects\CatDrop`，並建立方便、可診斷且適合 GitHub 的建置與啟動流程。
- scope：路徑更名、Windows `.bat` 入口、PowerShell 執行層、`diagnostics.py`、輪替日誌、測試、GitHub Actions／issue template 與 RADS；不變更 CatDrop 產品功能邊界。
- output：正式路徑 `D:\Projects\CatDrop`；`setup.bat`、`start.bat`、`start_debug.bat`、`check.bat`、`build_launcher.bat`、`scripts/*.ps1`、`diagnostics.py`、應用程式日誌、18 項測試、GitHub CI 與錯誤回報表單。
- path evidence：更名前確認 `D:\Projects\CatDrop` 不存在；更名後 `D:\Projects\CarDrop` 不存在，`D:\Projects\CatDrop` 存在。
- environment behavior：自動尋找 Python 3.11/3.12；失效 `.venv` 先時間戳改名保留；安裝套件後強制執行完整診斷與測試；缺少 Python、網路、套件或檢查失敗時回傳非零結束碼與精確訊息。
- startup behavior：一般啟動前執行快速檢查並使用 `pythonw`；除錯啟動以前景 Python 顯示錯誤；打包前強制診斷與測試。
- diagnostics：檢查 Python、Tkinter、qrcode、Pillow、必要資源、寫入權限、SQLite、TCP 8080 與區網位址；最新報告寫入 `logs/diagnostic-latest.txt`。
- error reporting：應用程式啟動、Tkinter 回呼、HTTP 服務與未預期上傳錯誤寫入 `logs/catdrop.log`；1 MB 輪替並保留三份備份；GitHub issue template 包含隱私確認。
- validation：實際全新建立 Python 3.12.13 `.venv` 並安裝 requirements；完整診斷全項 PASS；18/18 自動化測試通過；JavaScript、9 個 Python 檔案與 5 個 PowerShell 腳本語法通過；繁中終端輸出通過；正式路徑另以隔離 `.venv` 完成相同診斷與測試。
- failure-path evidence：受限網路下套件安裝正確停止並回傳 exit code 1；解除網路限制後同一建置流程成功，未將 missing evidence 誤判為 PASS。
- GitHub：Windows `python-version: 3.11, 3.12` workflow 與結構化 bug report template 已建立。
- status：validation completed（驗證完成）。
- remaining：GitHub 尚未推送，Actions 未遠端執行；正式路徑尚未建立 `.venv`；實體裝置、防火牆、完整 GUI 與 EXE 打包仍未驗證。
