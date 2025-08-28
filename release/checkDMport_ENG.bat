@echo off
chcp 437 >nul  :: Use US-English code page to avoid encoding issues
cd /d %~dp0

echo ===============================================
echo    MU310 Firmware Flashing Tool v1.0
echo ===============================================

:: === Step 1: Check ADB Connection ===
echo === Step 1: Check ADB Connection ===
echo Running adb devices...

set "DEVICE_FOUND="
for /f "skip=1 tokens=*" %%A in ('adb devices 2^>nul') do (
    if not "%%A"=="" (
        echo Device found: %%A
        set "DEVICE_FOUND=1"
        goto :device_check_done
    )
)

:device_check_done
if not defined DEVICE_FOUND (
    echo.
    echo [ERROR] No ADB device detected!
    echo Please check:
    echo 1. USB cable is properly connected
    echo 2. USB debugging is enabled on the device
    echo 3. ADB drivers are correctly installed
    echo.
    pause
    exit /b 1
)

echo [OK] ADB device connected.
echo.

:: === Step 2: Check DM PORT ===
echo === Step 2: Check DM PORT ===
set "DM_PORT="

for /f "tokens=*" %%A in ('powershell -Command "Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like '*DM PORT*' -and $_.Name -like '*COM*' } | Select-Object -ExpandProperty Name" 2^>nul') do (
    for /f "tokens=2 delims=()" %%B in ("%%A") do (
        set "DM_PORT=%%B"
        echo Found DM PORT: %%A
    )
)

if not defined DM_PORT (
    echo.
    echo [ERROR] No DM PORT found!
    echo Please check:
    echo 1. Device driver is correctly installed
    echo 2. Device is properly connected
    echo 3. COM port is not occupied
    echo.
    pause
    exit /b 1
)

echo [OK] DM PORT found = %DM_PORT%
echo.

:: === Step 3: Check Firmware File ===
echo === Step 3: Check Firmware File ===
if not exist "tools\FW_IMAGE\MU310-Q612_V0.0.0.0_1_modem.bin" (
    echo [ERROR] Firmware file not found: MU310-Q612_V0.0.0.0_1_modem.bin
    echo Please ensure the firmware file exists in the correct path.
    pause
    exit /b 1
)

echo [OK] Firmware file found.
echo.

:: === Step 4: Start Firmware Flash Process ===
echo === Step 4: Start Firmware Flash Process ===
echo.

echo [4.1] Uploading firmware to device...
adb push "tools\FW_IMAGE\MU310-Q612_V0.0.0.0_1_modem.bin" /usrdata/cache/ufs/update.zip
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upload firmware!
    pause
    exit /b 1
)
echo [OK] Firmware uploaded.

echo.
echo [4.2] Syncing file system...
adb shell sync
adb shell sync
echo [OK] Sync completed.

echo.
echo [4.3] Stopping system services...
adb shell systemctl stop pega-5GNR-init
adb shell systemctl stop pega-framework-init
adb shell systemctl stop pega-atcmder-init
echo [OK] Services stopped.

echo.
echo [4.4] Checking /dev/smd7 status...
adb shell fuser /dev/smd7
echo [OK] Check completed.

echo.
echo [4.5] Sending firmware update command...
adb shell "printf 'at\r\n' > /dev/smd7"
timeout /t 2 /nobreak >nul
adb shell "printf 'AT+QFOTADL=\"/usrdata/cache/ufs/update.zip\"\r\n' > /dev/smd7"

echo.
echo ===============================================
echo [SUCCESS] Firmware update command sent!
echo.
echo IMPORTANT:
echo 1. Do not disconnect the device
echo 2. Wait for the update to complete
echo 3. Device may reboot automatically
echo 4. It may take several minutes
echo ===============================================
echo.
echo MU310 Burn-ing please wait 
