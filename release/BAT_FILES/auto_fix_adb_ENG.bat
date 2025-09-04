@echo off
chcp 65001 > nul

setlocal enabledelayedexpansion


echo [STEP 1] Checking ADB device connection...

adb devices > adb_check.txt

:: ===== Summary (Count + Serial list) =====
for /f %%C in ('findstr /R /C:"device$" adb_check.txt ^| find /v /c ""') do set COUNT=%%C
echo === ADB devices: %COUNT% ===
for /f "tokens=1" %%S in ('findstr /R /C:"device$" adb_check.txt') do echo - %%S

findstr /R /C:"device$" adb_check.txt > nul



if %errorlevel%==0 (
    echo ADB is connected, no fix needed.
    del adb_check.txt
    if not defined NO_PAUSE pause
    exit /b

)


echo No ADB device detected. Attempting to fix...


echo [STEP 2] Sending AT command to set USB mode...

python "%~dp0..\fix_usbcfg.py"



if %errorlevel% NEQ 0 (
    echo Failed to send AT command. Cannot proceed with fix.
    if not defined NO_PAUSE pause
    exit /b
)


echo AT command sent successfully. Waiting 90 seconds for reboot...

timeout /t 90 /nobreak > nul


echo [STEP 3] Rechecking ADB device connection...

adb devices > adb_check.txt

:: ===== Summary (Count + Serial list) =====
for /f %%C in ('findstr /R /C:"device$" adb_check.txt ^| find /v /c ""') do set COUNT=%%C
echo === ADB devices: %COUNT% ===
for /f "tokens=1" %%S in ('findstr /R /C:"device$" adb_check.txt') do echo - %%S

findstr /R /C:"device$" adb_check.txt > nul



if %errorlevel%==0 (
    echo ADB connection restored successfully!
) else (
    echo ADB still not connected after fix. Please check the device manually.
)



del adb_check.txt

if not defined NO_PAUSE pause
exit /b









::: ------------------------------

::: Notes (comments section below)

::: ------------------------------

::: chcp 65001 > nul       ??Set code page to UTF-8

::: adb devices > adb_check.txt  ??List ADB devices and save result

::: findstr /R /C:"device$" adb_check.txt > nul  ??Check if device is connected

::: del adb_check.txt       ??Delete temp file

::: python " %~dp0..\fix_usbcfg.py\    ??Run Python script to fix USB config

::: timeout /t 90 /nobreak > nul  ??Wait 90 seconds for reboot

::: (Repeat adb check steps after waiting)

