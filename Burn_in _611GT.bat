
@echo off
chcp 65001 >nul
cd /d %~dp0

REM =========================================================
REM Features:
REM  1. Check if ADB tool is available
REM  2. Verify DUT is connected via ADB
REM  3. Confirm firmware file exists (from FW_IMAGE directory)
REM  4. Test if DUT target directory is writable
REM  5. Push firmware file to DUT
REM  6. Sync the file system
REM  7. Stop related system services
REM  8. Check /dev/smd7 status
REM  9. Send AT command to trigger firmware upgrade
REM =========================================================

setlocal enabledelayedexpansion

set "FW_DIR=%~dp0FW_IMAGE"
if not exist "%FW_DIR%" (
    echo [ERROR] FW_IMAGE folder not found: "%FW_DIR%"
    pause
    exit /b 1
)

rem ==== FW selection (robust, no nested blocks) ====
set "FW="
set "FW_NAME=%~1"

rem If argument given and is existing file (full path) -> use it
if not "%~1"=="" if exist "%~f1" (
    set "FW=%~f1"
    goto FW_OK
)

rem If argument given as plain name under FW_IMAGE -> use it
if not "%FW_NAME%"=="" if exist "%FW_DIR%\%FW_NAME%" (
    set "FW=%FW_DIR%\%FW_NAME%"
    goto FW_OK
)

rem No (valid) argument -> interactive selection
set /a COUNT=0
for %%F in ("%FW_DIR%\*.bin") do (
    set /a COUNT+=1
    set "ITEM!COUNT!=%%~nxF"
)
if "!COUNT!"=="0" (
    echo [ERROR] No .bin file found in "%FW_DIR%"
    pause
    exit /b 1
)
if "!COUNT!"=="1" (
    set "FW=%FW_DIR%\!ITEM1!"
    echo Found 1 firmware: "!ITEM1!"
    set /p CONF=Use this file? (Y/N): 
    if /I not "!CONF!"=="Y" (
        echo Aborted.
        exit /b 1
    )
    goto FW_OK
)

echo Available firmware files in "%FW_DIR%":
for /L %%I in (1,1,!COUNT!) do echo %%I) !ITEM%%I!
set /p CH=Enter number to select: 
set "FW="
for /L %%I in (1,1,!COUNT!) do (
    if "%CH%"=="%%I" set "FW=%FW_DIR%\!ITEM%%I!"
)
if "%FW%"=="" (
    echo Invalid selection.
    exit /b 1
)

:FW_OK
if not exist "%FW%" (
    echo [ERROR] Firmware file not found: "%FW%"
    exit /b 1
)
echo [INFO] Firmware selected: "%FW%"
rem ==== FW selection end ====


echo ===============================================
echo    MU310 Firmware Flashing Tool v1.1
echo ===============================================

::: === Step 0: Check ADB version and restart server if needed ===
echo === Step 0: Check ADB version ===
adb version
if %errorlevel% neq 0 (
    echo [ERROR] ADB not found! Please install ADB and ensure it is in PATH.
    pause
    exit /b 1
)
adb kill-server
adb start-server

echo.

::: === Step 1: Check ADB connection state ===
echo === Step 1: Check ADB connection ===
set "DEVICE_FOUND="
set /a RETRY=0
:check_adb
adb devices > adb_list.txt
for /f "skip=1 tokens=*" %%A in (adb_list.txt) do (
    if not "%%A"=="" (
        set "DEVICE_FOUND=1"
        echo Found device: %%A
        goto device_check_done
    )
)
set /a RETRY+=1
if %RETRY% LSS 5 (
    echo [INFO] No ADB device found, retrying in 3 seconds... (%RETRY%/5)
    timeout /t 3 >nul
    goto check_adb
)

:device_check_done
if not defined DEVICE_FOUND (
    echo [ERROR] No ADB device connected!
    pause
    exit /b 1
)
echo [SUCCESS] ADB device connection normal
echo.

::: === Step 2: Check if firmware file exists ===
echo === Step 2: Check firmware file ===
if not exist "%FW%" (
    echo [ERROR] Firmware file not found: "%FW%"!
    pause
    exit /b 1
)
echo [SUCCESS] Firmware file exists: "%FW%"
echo.

::: === Step 3: Test write permission to target directory ===
echo === Step 3: Test write permission ===
adb shell "echo test > /usrdata/cache/ufs/test.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot write to /usrdata/cache/ufs!
    pause
    exit /b 1
)
adb shell "rm /usrdata/cache/ufs/test.txt"
echo [SUCCESS] Target directory writable
echo.

::: === Step 4: Upload firmware with retry ===
echo === Step 4: Upload firmware ===
set /a RETRY=0
:push_retry
echo [4.1] Uploading firmware to device...
adb push "%FW%" /usrdata/cache/ufs/update.zip
if %errorlevel% neq 0 (
    set /a RETRY+=1
    if %RETRY% LSS 3 (
        echo [INFO] Retry push... attempt %RETRY%
        timeout /t 2 >nul
        goto push_retry
    ) else (
        echo [ERROR] Firmware upload failed after 3 attempts!
        pause
        exit /b 1
    )
)
echo [SUCCESS] Firmware upload completed
echo.

::: === Step 5: Sync ===
echo [4.2] Executing sync operation...
adb shell sync
adb shell sync
echo [SUCCESS] Sync operation completed
echo.

::: === Step 6: Stop system services ===
echo [4.3] Stopping related system services...
adb shell systemctl stop pega-5GNR-init
adb shell systemctl stop pega-framework-init
adb shell systemctl stop pega-atcmder-init
echo [SUCCESS] System services stopped
echo.

::: === Step 7: Check /dev/smd7 ===
echo [4.4] Checking /dev/smd7...
adb shell fuser /dev/smd7
echo [SUCCESS] /dev/smd7 status check completed
echo.

::: === Step 8: Send firmware update command ===
echo [4.5] Sending firmware update command...
adb shell "printf 'at\r\n' > /dev/smd7"
timeout /t 2 >nul
adb shell "printf 'AT+QFOTADL=\"/usrdata/cache/ufs/update.zip\"\r\n' > /dev/smd7"
echo [SUCCESS] Firmware flashing command sent!
echo.

echo ===============================================
echo Notes:
echo 1. Please wait for device to complete firmware update
echo 2. Do not disconnect during update process
echo 3. Device may restart automatically
echo 4. The entire process may take several minutes
echo ===============================================
echo.
echo MU310 burn in PASS and please wait 4 mins for update.
pause
