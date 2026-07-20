# Current Task Report

- 日期：2026-07-20
- objective：為 CatDrop 檔案接收控制台加入欄位排序、多檔選取、獨立設定頁面與可同步至網頁的接收控制。
- scope：桌面控制台、SQLite settings、HTTP 設定／上傳 API、瀏覽器頁面、診斷、測試與 RADS；不加入 AI Agent、雲端或外網功能。
- output：五欄排序、Ctrl／Shift／拖曳／全選、多筆操作、中英控制台、設定頁面、動態檔案類型、接收開放／暫停、可隱藏的控制台狀態按鈕、網頁三秒同步與 HTTP 503 防線。
- settings：新增 `ui_language`、`enabled_extensions`、`upload_enabled`、`show_upload_toggle`，沿用既有 SQLite settings 表並保留舊資料。
- control rule：狀態按鈕預設顯示且預設開放；顯示時設定頁面狀態選項 disabled，隱藏後才可更動；暫停只拒絕上傳，不停止網站。
- file types：設定值只能取固定安全白名單子集合；網頁動態顯示並設定 accept，伺服器仍重新檢查動態白名單與檔頭。
- validation：正式 `setup.bat --no-pause` 通過；完整診斷全項 PASS；29/29 自動化測試通過；11 個 Python 檔案與 JavaScript 語法通過。
- GUI evidence：正式程式碼／正式 `.venv` 的隱藏 GUI smoke test 通過，實際驗證狀態排序、多選、設定鎖定、中英切換、按鈕隱藏／顯示與接收狀態切換。
- server evidence：設定 API 回傳動態格式、語言與狀態；暫停上傳回傳 HTTP 503 且不寫入；取消勾選的格式不接受；既有上傳、UTF-8、路徑清理與重名保留測試持續通過。
- data safety：部署只更新原始碼、網頁、測試與 RADS；未覆寫或刪除既有資料庫、接收檔案、日誌與 QR Code。
- status：validation completed（驗證完成）。
- remaining：實體裝置即時同步、防火牆、正式 EXE 與 GitHub Actions 遠端執行尚未驗證；missing evidence is not PASS。
