# Current Task Report

- 日期：2026-07-20
- objective：為 CatDrop 增加常用影像格式與預設關閉的全格式支援。
- scope：桌面設定、SQLite settings、HTTP 設定／上傳 API、瀏覽器頁面、測試與 RADS；不加入 AI Agent、雲端或外網功能。
- output：白名單新增 JFIF、AVIF、HEIF、ICO；新增全格式開關、個別格式鎖定、前端同步與伺服器執行邊界。
- settings：新增 `allow_all_file_types`，預設 `0`；啟用後個別格式 checkbox disabled，既有勾選值保留，關閉後可繼續調整。
- migration：既有設定若仍是舊版完整白名單則自動加入新格式；任何自訂格式子集合均不覆寫。
- whitelist validation：JFIF 使用 JPEG 檔頭；AVIF／HEIF 檢查 ISO Base Media File Format 品牌；ICO 檢查標準檔頭。SVG 因可包含主動內容未納入。
- all-types boundary：啟用時接受任何副檔名或無副檔名，並略過白名單與檔案內容特徵驗證；仍執行大小限制、路徑清理、唯一檔名、防覆寫及 SQLite 紀錄。此模式不提供惡意檔案安全保證。
- web synchronization：`/api/config` 回傳 `allowAllFileTypes`；網頁顯示「全格式支援」、清除 `accept` 並停止前端副檔名篩選。
- automated validation：正式 `D:\Projects\CatDrop` 完整診斷全項 PASS，32/32 自動化測試通過；涵蓋升級遷移、任意副檔名與無副檔名，既有首頁、啟停、暫停、上傳、重名、路徑與 UTF-8 測試持續通過。
- GUI evidence：正式程式碼／正式 `.venv` 的隱藏 GUI smoke test PASS；確認預設關閉、啟用後鎖定個別格式並可保存。
- physical-device evidence：BOSS 回報實體手機的暫停與開放功能驗證通過；新增影像格式的實體檔案上傳尚無證據。
- data safety：部署只更新列出的原始碼、網頁、測試與 RADS；未覆寫或刪除既有資料庫、接收檔案、日誌與 QR Code。
- status：validation completed（驗證完成）。
- remaining：新增影像格式的實體手機上傳、Windows 防火牆、正式 EXE 與 GitHub Actions 遠端執行尚未驗證；missing evidence is not PASS。
