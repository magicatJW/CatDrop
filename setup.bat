@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if /i "%~1"=="--no-pause" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -NoPause
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
)
exit /b %errorlevel%
