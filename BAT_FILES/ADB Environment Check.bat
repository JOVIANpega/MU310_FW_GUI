@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

::: =========================================================
::: MU310 Step 0: ADB Environment Check
::: Features:
:::   1. Check if adb.exe exists
:::   2. Prevent using wrong System32 version
:::   3. Display and confirm ADB can run
:::   4. Restart ADB server to ensure a clean connection
:::   5. List connected devices
:::   6. Display the path of the adb executable being used
::: =========================================================

echo === Step 0: Check ADB Environment ===

::: --- Check if adb.exe exists ---
::: Command: where adb
where adb >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] ADB not found! Please install Android SDK Platform-tools and add to PATH.
    if not defined NO_PAUSE pause
    exit /b 1
)

::: --- Prevent using System32 adb ---
::: Command: where adb | findstr /i "System32"
where adb | findstr /i "System32" >nul
if %errorlevel%==0 (
    echo [ERROR] Detected ADB in System32 folder!
    echo Please remove/rename it and use C:\platform-tools\adb.exe instead.
    if not defined NO_PAUSE pause
    exit /b 1
)

::: --- Display the path of the adb executable being used ---
::: Command: where adb
echo Current adb path:
for /f "delims=" %%P in ('where adb') do set "ADB_PATH=%%P" & goto got_adb_path
:got_adb_path
echo !ADB_PATH!
echo.

::: --- Display ADB version and confirm executable ---
::: Command: adb version
adb version
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run adb. Please check if Platform-tools is correctly installed.
    if not defined NO_PAUSE pause
    exit /b 1
)

::: --- Restart ADB server to ensure clean connection ---
::: Commands:
:::   adb kill-server
:::   adb start-server
adb kill-server
adb start-server
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start ADB server. Please check USB drivers.
    if not defined NO_PAUSE pause
    exit /b 1
)

echo.

::: --- List connected devices ---
::: Command: adb devices
adb devices
echo.

::: ===== Summary (Count + Serial list) =====
adb devices > "%TEMP%\adb_devices_raw.txt"
findstr /R /C:"device$" "%TEMP%\adb_devices_raw.txt" > "%TEMP%\adb_devices_only.txt"

set COUNT=0
for /f %%C in ('find /v /c "" ^< "%TEMP%\adb_devices_only.txt"') do set COUNT=%%C
echo === ADB devices: %COUNT% ===

for /f "tokens=1" %%S in (%TEMP%\adb_devices_only.txt) do echo - %%S

del "%TEMP%\adb_devices_raw.txt" >nul 2>nul
del "%TEMP%\adb_devices_only.txt" >nul 2>nul
echo.

echo === Summary ===
echo ADB Path: !ADB_PATH!
echo Device Count: %COUNT%
echo ================
