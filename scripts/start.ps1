param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvPythonw = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"

try {
    # 第一次啟動時自動完成環境建置，避免使用者手動串接多個步驟。
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        Write-Host "[INFO] 尚未建立環境，現在執行 setup.bat。"
        & (Join-Path $ProjectRoot "scripts\setup.ps1") -NoPause
        if ($LASTEXITCODE -ne 0) {
            exit 1
        }
    }

    & $VenvPython diagnostics.py --quick
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] 啟動前檢查失敗，請查看 logs\diagnostic-latest.txt。" -ForegroundColor Red
        Read-Host "按 Enter 關閉視窗"
        exit 1
    }

    if ($DebugMode) {
        # 前景模式保留 Python 錯誤輸出，供無法啟動時直接診斷。
        & $VenvPython app.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] CatDrop 異常結束，請查看 logs\catdrop.log。" -ForegroundColor Red
            Read-Host "按 Enter 關閉視窗"
            exit 1
        }
        exit 0
    }

    # 一般模式隱藏命令視窗；啟動初期失敗時仍能由日誌追查。
    $Process = Start-Process -FilePath $VenvPythonw -ArgumentList @("app.py") -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 1
    if ($Process.HasExited -and $Process.ExitCode -ne 0) {
        Write-Host "[FAIL] CatDrop 啟動失敗，請改用 start_debug.bat 或查看 logs\catdrop.log。" -ForegroundColor Red
        Read-Host "按 Enter 關閉視窗"
        exit 1
    }
    Write-Host "[PASS] CatDrop 已啟動。"
    exit 0
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "請改用 start_debug.bat 或查看 logs\catdrop.log。"
    Read-Host "按 Enter 關閉視窗"
    exit 1
}
