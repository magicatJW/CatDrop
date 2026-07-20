$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

try {
    # 正式打包前強制執行診斷與測試，避免產生已知失敗的 EXE。
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        throw "尚未建立 CatDrop 環境，請先執行 setup.bat。"
    }
    & $VenvPython diagnostics.py
    if ($LASTEXITCODE -ne 0) {
        throw "環境診斷失敗，停止打包。"
    }
    & $VenvPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "自動化測試失敗，停止打包。"
    }
    & $VenvPython -m PyInstaller --noconfirm --clean --onefile --windowed --name "CatDrop" --add-data "web;web" --hidden-import "PIL._tkinter_finder" app.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 打包失敗。"
    }
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "dist\CatDrop.exe") -Destination (Join-Path $ProjectRoot "CatDrop.exe") -Force
    Write-Host "[PASS] 啟動器已建立：CatDrop.exe" -ForegroundColor Green
    Read-Host "按 Enter 關閉視窗"
    exit 0
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按 Enter 關閉視窗"
    exit 1
}
