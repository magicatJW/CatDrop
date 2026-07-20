param(
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

function Wait-ForUser {
    # 由使用者雙擊執行時保留視窗；被啟動流程呼叫時不暫停。
    if (-not $NoPause) {
        Read-Host "按 Enter 關閉視窗"
    }
}

function Stop-WithError {
    param([string]$Message)
    # 統一錯誤格式與結束碼，讓上層腳本可可靠判斷失敗。
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    Wait-ForUser
    exit 1
}

function Invoke-BasePython {
    param(
        [hashtable]$Candidate,
        [string[]]$Arguments
    )
    # Python Launcher 需要額外版本參數，因此集中處理參數組合。
    $AllArguments = @($Candidate.Prefix) + $Arguments
    & $Candidate.File @AllArguments
}

try {
    # 優先採用官方 Python Launcher，再回退至 PATH 中的 python.exe。
    $Candidates = @(
        @{ File = "py.exe"; Prefix = @("-3.12") },
        @{ File = "py.exe"; Prefix = @("-3.11") },
        @{ File = "python.exe"; Prefix = @() }
    )
    $Selected = $null
    foreach ($Candidate in $Candidates) {
        if (-not (Get-Command $Candidate.File -ErrorAction SilentlyContinue)) {
            continue
        }
        Invoke-BasePython $Candidate @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)") *> $null
        if ($LASTEXITCODE -eq 0) {
            $Selected = $Candidate
            break
        }
    }
    if (-not $Selected) {
        Stop-WithError "找不到 Python 3.11 或 3.12。請安裝後勾選 Add Python to PATH。"
    }

    $VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $VenvPython) {
        & $VenvPython -c "import sys" *> $null
        if ($LASTEXITCODE -ne 0) {
            # 失效環境保留為時間戳備份，不直接刪除任何既有資料。
            $BackupName = ".venv_broken_{0}" -f (Get-Date -Format "yyyyMMdd_HHmmss")
            $BackupPath = Join-Path $ProjectRoot $BackupName
            Write-Host "[WARN] 既有 .venv 已失效，保留為 $BackupName 後重建。" -ForegroundColor Yellow
            Move-Item -LiteralPath (Join-Path $ProjectRoot ".venv") -Destination $BackupPath
        }
    }

    if (-not (Test-Path -LiteralPath $VenvPython)) {
        Write-Host "[INFO] 建立 CatDrop 虛擬環境..."
        Invoke-BasePython $Selected @("-m", "venv", ".venv")
        if ($LASTEXITCODE -ne 0) {
            Stop-WithError "無法建立 .venv。"
        }
    }

    Write-Host "[INFO] 安裝或更新相依套件..."
    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "pip 更新失敗，請檢查網路、Proxy 或憑證設定。"
    }
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "相依套件安裝失敗，請保留完整終端輸出。"
    }

    Write-Host "[INFO] 執行環境診斷與自動化測試..."
    & $VenvPython diagnostics.py
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "環境診斷失敗，請查看 logs\diagnostic-latest.txt。"
    }
    & $VenvPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "自動化測試失敗，請保留完整終端輸出。"
    }

    Write-Host "[PASS] CatDrop 環境已完成，可執行 start.bat。" -ForegroundColor Green
    Wait-ForUser
    exit 0
}
catch {
    Stop-WithError $_.Exception.Message
}
