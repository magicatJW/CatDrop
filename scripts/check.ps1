param(
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

try {
    # 完整自檢固定使用專案虛擬環境，避免誤用全域套件。
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        throw "尚未建立 CatDrop 環境，請先執行 setup.bat。"
    }
    & $VenvPython diagnostics.py
    if ($LASTEXITCODE -ne 0) {
        throw "環境診斷失敗，請查看 logs\diagnostic-latest.txt。"
    }
    & $VenvPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "自動化測試失敗。"
    }
    Write-Host "[PASS] CatDrop 完整自檢通過。" -ForegroundColor Green
    if (-not $NoPause) {
        Read-Host "按 Enter 關閉視窗"
    }
    exit 0
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    if (-not $NoPause) {
        Read-Host "按 Enter 關閉視窗"
    }
    exit 1
}
