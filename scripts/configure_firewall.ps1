$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

try {
    # 防火牆規則需要系統管理員權限；不足時只提升目前這個明確腳本。
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = New-Object Security.Principal.WindowsPrincipal($Identity)
    $IsAdmin = $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $IsAdmin) {
        Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"") -Verb RunAs -WorkingDirectory $ProjectRoot
        exit 0
    }

    Get-NetFirewallRule -DisplayName "CatDrop TCP 8080" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -DisplayName "CatDrop TCP 8080" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8080 -Profile Private | Out-Null
    Write-Host "[PASS] 已建立 CatDrop 私人網路 TCP 8080 入站規則。" -ForegroundColor Green
    Read-Host "按 Enter 關閉視窗"
    exit 0
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按 Enter 關閉視窗"
    exit 1
}
