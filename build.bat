@echo off
chcp 65001 >nul
echo ========================================
echo MU310 ADB Tools - 建置批次檔
echo ========================================
echo.

:: 1. 清理舊的建置檔案
echo [步驟 1] 清理舊的建置檔案...
if exist "build" (
    echo   移除 build/ 資料夾...
    rmdir /s /q "build"
)
if exist "*.spec" (
    echo   移除 .spec 檔案...
    del /q "*.spec"
)
if exist "dist" (
    echo   移除 dist/ 資料夾...
    rmdir /s /q "dist"
)
echo   清理完成！
echo.

:: 2. 建立 release 資料夾
echo [步驟 2] 建立 release 資料夾...
if not exist "release" mkdir "release"
echo   建立完成！
echo.

::: 2.0 準備 assets 與 icon（統一路徑 assets/icon.ico）
echo [步驟 2.0] 準備 assets 與 icon...
if not exist "assets" mkdir "assets"
if exist "34brh-v7ca1-001.ico" (
    copy /Y "34brh-v7ca1-001.ico" "assets\icon.ico" >nul
)
echo   assets 準備完成！
echo.

:: 2.1 產生構建編號並寫入 version.py 的 __build__
echo [步驟 2.1] 產生構建編號...
for /f "tokens=1-4 delims=/-: " %%a in ("%date% %time%") do set BUILD=%%a%%b%%c_%%d
set BUILD=%BUILD::=%
set BUILD=%BUILD:,=%
set BUILD=%BUILD%.%RANDOM%
echo   BUILD=%BUILD%

:: 讀出 __version__
for /f "usebackq tokens=2 delims== " %%v in (`findstr /r /c:"^__version__\s*=\s*\".*\"" version.py`) do set RAWVER=%%v
set RAWVER=%RAWVER: =%
set RAWVER=%RAWVER:\"=%
set RAWVER=%RAWVER:"=%
set VERSION=%RAWVER%
echo   VERSION=%VERSION%

:: 使用固定的版本號元組，避免解析錯誤
set VERSION_TUPLE=1,8,2,0
echo   VERSION_TUPLE=%VERSION_TUPLE%

:: 用 PowerShell 更新 __build__ 內容
powershell -NoProfile -Command "(Get-Content -Raw 'version.py') -replace '__build__\s*=\s*\".*\"', '__build__ = \"%BUILD%\"' | Set-Content 'version.py' -Encoding UTF8"

:: 2.2 產生 version_info.txt 供 PyInstaller 嵌入 EXE 資訊
echo [步驟 2.2] 產生 version_info.txt...
>version_info.txt echo # UTF-8 with BOM not required
>>version_info.txt echo VSVersionInfo(
>>version_info.txt echo   ffi=FixedFileInfo(
>>version_info.txt echo     filevers=(%VERSION_TUPLE%),
>>version_info.txt echo     prodvers=(%VERSION_TUPLE%),
>>version_info.txt echo     mask=0x3f,
>>version_info.txt echo     flags=0x0,
>>version_info.txt echo     OS=0x40004,
>>version_info.txt echo     fileType=0x1,
>>version_info.txt echo     subtype=0x0,
>>version_info.txt echo     date=(0, 0)
>>version_info.txt echo   ),
>>version_info.txt echo   kids=[
>>version_info.txt echo     StringFileInfo([
>>version_info.txt echo       StringTable(
>>version_info.txt echo         '040904B0',
>>version_info.txt echo         [
>>version_info.txt echo           StringStruct('CompanyName', 'MU310 Tools Center'),
>>version_info.txt echo           StringStruct('FileDescription', 'MU310 ADB Tools Center - GUI for ADB tools, connection fix, firmware upgrade, and keyword color settings'),
>>version_info.txt echo           StringStruct('FileVersion', '%VERSION%-%BUILD%'),
>>version_info.txt echo           StringStruct('InternalName', 'MU310_ADB_TOOLl'),
>>version_info.txt echo           StringStruct('LegalCopyright', '© 2025 MU310 Tools Center'),
>>version_info.txt echo           StringStruct('OriginalFilename', 'MU310_ADB_TOOLl.exe'),
>>version_info.txt echo           StringStruct('ProductName', 'MU310 ADB Tools Center'),
>>version_info.txt echo           StringStruct('ProductVersion', '%VERSION%-%BUILD%'),
>>version_info.txt echo           StringStruct('Comments', 'Build: %BUILD% - Includes ADB tools, connection fix, firmware upgrade, settings, and keyword color editor')
>>version_info.txt echo         ]
>>version_info.txt echo       )
>>version_info.txt echo     ]),
>>version_info.txt echo     VarFileInfo([VarStruct('Translation', [1033, 1200])])
>>version_info.txt echo   ]
>>version_info.txt echo )

echo.
:: 3. 使用 PyInstaller 打包
echo [步驟 3] 開始打包...
echo   使用 PyInstaller 打包成單一 EXE 檔案...
echo.

:: 基本打包指令 - 包含所有必要的 Python 檔案和資源
pyinstaller --onefile ^
    --noconsole ^
    --icon=assets/icon.ico ^
    --name=MU310_ADB_TOOLl ^
    --distpath=release ^
    --workpath=build ^
    --specpath=. ^
    --version-file version_info.txt ^
    --add-data "assets;assets" ^
    --add-data "config.json;." ^
    --add-data "i18n.py;." ^
    --add-data "logger_util.py;." ^
    --add-data "subprocess_runner.py;." ^
    --add-data "utils_paths.py;." ^
    --add-data "fix_usbcfg.py;." ^
    --add-data "README.md;." ^
    --add-data "BAT_FILES;BAT_FILES" ^
    --add-data "logs;logs" ^
    --add-data "version.py;." ^
    --add-data "keywords.txt;." ^
    --add-data "FW_IMAGE;FW_IMAGE" ^
    main.py

:: 檢查打包結果
if %errorlevel% equ 0 (
    echo.
    echo [成功] 打包完成！
    echo   輸出檔案: release\MU310_ADB_TOOLl.exe
    echo.
    echo 檔案大小:
    dir "release\MU310_ADB_TOOLl.exe" | findstr "MU310_ADB_TOOLl.exe"
) else (
    echo.
    echo [錯誤] 打包失敗！請檢查錯誤訊息。
    echo.
    pause
    exit /b 1
)

:: 4. 複製額外的批次檔到 release 資料夾（保持目錄結構）
echo.
echo [步驟 4] 複製額外檔案到 release 資料夾...
if not exist "release\BAT_FILES" mkdir "release\BAT_FILES"
copy "BAT_FILES\*.*" "release\BAT_FILES\" >nul
if not exist "release\FW_IMAGE" mkdir "release\FW_IMAGE"
xcopy /E /I /Y "FW_IMAGE\*" "release\FW_IMAGE\" >nul
copy "config.json" "release\" >nul
copy "README.md" "release\" >nul
copy "keywords.txt" "release\" >nul
copy "assets\icon.ico" "release\" >nul
echo   複製完成！
echo.

:: 5. 清理建置暫存檔案
echo [步驟 5] 清理建置暫存檔案...
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo   清理完成！
echo.

:: 6. 顯示完成訊息
echo ========================================
echo 建置完成！
echo ========================================
echo.
echo 輸出檔案位置: release\MU310_ADB_TOOLl.exe
echo.
echo 包含的檔案:
echo - MU310_ADB_TOOLl.exe (主程式)
echo - BAT_FILES/ 目錄 (所有批次檔)
echo - config.json (設定檔)
echo - README.md (說明檔)
echo - 圖示檔案 (.ico)
echo - logs 資料夾 (日誌資料夾)
echo - keywords.txt (關鍵字設定檔)
echo - 所有 Python 模組 (.py)
echo - assets 資料夾 (包含 help.html)
echo - FW_IMAGE 目錄 (韌體檔案)
echo.
echo 注意事項:
echo - 主程式已包含所有 Python 模組和資源檔
echo - 批次檔已複製到 release 資料夾，方便直接執行
echo - 如果未來需要加入 drivers\*.dll 等檔案，請在 --add-data 處加入
echo   例如: --add-data "drivers;drivers"
echo.
echo 按任意鍵關閉視窗...
pause >nul 