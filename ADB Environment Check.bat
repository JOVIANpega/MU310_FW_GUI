:: =========================================================
:: MU310 Step 0: ADB Environment Check
:: Features:
::   1. Check if adb.exe exists
::   2. Prevent using wrong System32 version
::   3. Display and confirm ADB can run
::   4. Restart ADB server to ensure a clean connection
::   5. List connected devices
::   6. Display the path of the adb executable being used
:: =========================================================

echo === Step 0: Check ADB Environment ===

:: --- Check if adb.exe exists ---
:: Command: where adb
where adb >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] ADB not found! Please install Android SDK Platform-tools and add to PATH.
    pause
    exit /b 1
)

:: --- Prevent using System32 adb ---
:: Command: where adb | findstr /i "System32"
where adb | findstr /i "System32" >nul
if %errorlevel%==0 (
    echo [ERROR] Detected ADB in System32 folder!
    echo Please remove/rename it and use C:\platform-tools\adb.exe instead.
    pause
    exit /b 1
)

:: --- Display the path of the adb executable being used ---
:: Command: where adb
echo Current adb path:
where adb
echo.

:: --- Display ADB version and confirm executable ---
:: Command: adb version
adb version
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run adb. Please check if Platform-tools is correctly installed.
    pause
    exit /b 1
)

:: --- Restart ADB server to ensure clean connection ---
:: Commands:
::   adb kill-server
::   adb start-server
adb kill-server
adb start-server
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start ADB server. Please check USB drivers.
    pause
    exit /b 1
)

:: --- List connected devices ---
:: Command: adb devices
adb devices
echo.
