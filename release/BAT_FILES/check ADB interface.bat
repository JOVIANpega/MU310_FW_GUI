@echo off
chcp 65001 >nul
echo ============================================
echo   Check Android ADB Interface
echo ============================================

set "FOUND="

REM 用 PowerShell 查找 ADB 介面
for /f "delims=" %%A in (
    'powershell -NoProfile -Command "Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like \"*ADB*\" } | ForEach-Object { $_.Name }"'
) do (
    echo [FOUND] %%A
    set FOUND=1
)

if not defined FOUND (
    echo [NOT FOUND] No ADB interface detected.
)

pause


REM CHECK ADB INTERFACE