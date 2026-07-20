# Current Task Report

- 日期：2026-07-20
- objective：修復 CatDrop 首次 GitHub Actions 失敗並建立可重現的遠端驗證證據。
- scope：`.github/workflows/ci.yml`、GitHub Actions runs `29727741928` 與 `29727962166`、RADS；不修改 CatDrop 應用程式功能。
- failure evidence：run `29727741928` 的 Python 3.11 diagnostics step 因 Windows runner stdout 使用 `cp1252`，輸出繁體中文時發生 `UnicodeEncodeError`；3.12 job 因 fail-fast 取消。
- root cause：本機 `check.ps1` 已設定 `PYTHONUTF8=1`，但 GitHub Actions workflow 未設定等價環境，造成執行環境差異。
- correction：CI job 新增 `PYTHONUTF8=1` 與 `PYTHONIOENCODING=utf-8`；不刪除中文輸出、不略過 diagnostics、不降低測試範圍。
- result：修正 commit `8a38ba42f4e306ac7eeeb2076f47471c6357eda2` 的 run `29727962166` 在 Python 3.11 與 3.12 均完成 dependencies、diagnostics、37 tests 與 JavaScript syntax check，全部 PASS。
- maintenance：run 仍回報 actions Node.js 20 淘汰警告，因此 workflow 後續採官方穩定的 `actions/checkout@v6` 與 `actions/setup-python@v6`；不採 2026-07-20 當日剛發布的 v7 major release。
- residual risk：GitHub-hosted `windows-latest` 映像與 actions 依賴會持續更新，若未來 runner 行為改變，應以 workflow run log 為準，missing evidence is not PASS。
