# MU310 Tools Center - 說明文件

本專案提供以 Tkinter 實作的工具整合 GUI，協助進行 ADB 環境檢查、連線修復（AT/USB 配置）、與韌體升級流程。UI 支援英/中切換、全域字體大小調整、內建日誌面板，適合打包為單一 EXE 提供給一般使用者。

## 功能總覽
- ADB Tools（ADB 工具）
  - 檢查 ADB 環境與版本
  - 重啟 ADB Server
  - 列出 ADB 裝置
  - 檢查「Android ADB Interface」(裝置管理員)
  - 掃描 COM 埠列表
- Connection Fix（連線修復）
  - 掃描/選擇 AT 埠
  - 自動修復：查詢/設定 `AT+QCFG="usbcfg"`，成功則 `AT+CFUN=1,1` 重啟，並可自動複檢 ADB
  - 可調重啟等待秒數（預設 90 秒）
- Firmware Upgrade（韌體升級）
  - 韌體檔選擇/瀏覽、基本校驗（存在/大小）
  - 前置檢查：檢查 ADB、檢查 DM PORT、測試目標路徑寫入權限
  - 選項：停止服務、同步兩次、push 失敗重試、ADB 重試
  - 一鍵升級：push → sync → stop services → 透過 `/dev/smd7` 發送 `AT+QFOTADL="/usrdata/cache/ufs/update.zip"`
- Logs（日誌）
  - 內建日誌面板（多頁共享），支援 Debug Mode、清除、置底、即時存檔到 `logs/` 資料夾
  - **新增：彩色日誌顯示** - 重要關鍵字用不同顏色標示，提升可讀性
  - **新增：狀態標籤** - 顯示執行狀態、進度、裝置狀態、當前執行的 BAT 檔案、最後更新時間
  - **新增：標籤頁獨立日誌** - 每個標籤頁都有自己的日誌區域，互不干擾
  - **新增：連續性日誌** - 日誌連續累加，不清空舊訊息，方便查看完整執行歷史
- 語系
  - English / 繁體中文 即時切換
- 字體
  - 全域字體大小 +/- 聯動（包含按鈕、標籤、Text、彈出視窗）

## 新增功能詳細說明

### 彩色日誌顯示
- **SUCCESS（綠色）**: 成功訊息
- **ERROR（紅色）**: 錯誤訊息  
- **WARNING（橙色）**: 警告訊息
- **INFO（藍色）**: 一般資訊
- **DEBUG（灰色）**: 除錯訊息
- **DEVICE（紫色）**: 裝置相關
- **PORT（青色）**: 埠口相關
- **ADB（橙紅色）**: ADB 相關
- **USB（靛色）**: USB 相關
- **FOTA（深粉紅色）**: FOTA 相關

### 狀態標籤系統
每個標籤頁的日誌區域下方都有狀態標籤：
- **狀態**: 顯示當前操作狀態（待機中、執行中、完成、錯誤）
- **進度**: 顯示操作進度百分比
- **裝置**: 顯示 ADB 裝置連線狀態
- **執行檔案**: 顯示當前正在執行的 BAT 檔案名稱
- **更新**: 顯示最後一次狀態更新的時間

### 標籤頁獨立日誌
- 每個標籤頁都有獨立的日誌區域
- 支援的標籤頁：`"adb"`、`"fix"`、`"upgrade"`、`"logs"`
- 日誌訊息可以指定顯示到特定標籤頁或所有標籤頁
- 狀態標籤會根據日誌訊息自動更新

### DEBUG 模式增強
- 開啟除錯模式時顯示詳細的執行資訊
- 包含命令執行詳細資訊、工作目錄、環境變數、程序返回碼
- STDOUT/STDERR 的原始輸出會標示來源

## 專案結構
```
GUI_ADB_tools/
  main.py            # 入口，建立視窗、分頁、語言與字體控制、狀態列
  logger_util.py     # GUI 日誌工具：Text 附掛、多處面板共用、即時寫檔、Debug 切換、彩色顯示、狀態標籤
  utils_paths.py     # get_resource_path() 支援 PyInstaller 打包後路徑
  i18n.py            # 簡易 i18n：EN/ZH 字典、即時切換 API
  subprocess_runner.py # 外部命令執行工具：支援 DEBUG 模式、標籤頁獨立日誌
  *.bat              # 既有批次腳本（ADB 檢查、燒錄流程、介面檢查等）
  fix_usbcfg.py      # 既有 AT/USB 組態修正腳本（pyserial）
  assets/            # 圖示/資源（icon.ico 等）
  logs/              # 執行時自動產生日誌檔案
```

## 執行流程（Flow）
```mermaid
graph TD
  A[User clicks a button] --> B[Callback (on_* function)]
  B --> C{Run task}
  C -->|Python subprocess / pyserial| D[Capture stdout/stderr]
  C -->|Future: call BAT if kept| D
  D --> E[GuiLogger.log -> Logs tab & file]
  E --> F[UI updates: progress/status/current_bat]
  F --> G[Color-coded keywords in logs]
```

## 執行架構（BAT vs Python）
- 目前狀態：GUI 骨架已完成，功能按鈕已綁定實際動作，支援呼叫 BAT 檔案和 Python 命令
- 新增功能：
  - 彩色日誌顯示，重要關鍵字用不同顏色標示
  - 狀態標籤系統，即時顯示執行狀態和進度
  - 標籤頁獨立日誌，每個功能區域互不干擾
  - 連續性日誌，累加顯示完整執行歷史
  - 增強的 DEBUG 模式，顯示詳細執行資訊
- 目標：提供完整的 GUI 工具，支援既有 BAT 腳本，同時具備豐富的狀態顯示和日誌功能

## 主要模組說明
- `main.py`
  - 建立 Tkinter 主視窗（固定 900x600）與 `ttk.Notebook` 分頁：ADB Tools / Connection Fix / Firmware Upgrade / Logs / Help
  - 右上角：Language(EN/ZH) 下拉、Font +/- 大小調整（Tk 命名字體：`TkDefaultFont`、`TkTextFont`、`TkFixedFont`）
  - 狀態列顯示：Status / Device / DM PORT / Version
  - Callback 命名：全部以 `on_` 開頭，便於維護與檢索
  - **新增：每個標籤頁都有獨立的日誌區域和狀態標籤**
- `logger_util.py`
  - `GuiLogger`：在 Logs 分頁與功能分頁附掛 Text 作為即時日誌
  - `log()/debug()/error()/warning()/success()`：自動時間戳，同步寫入 `logs/session_YYYYMMDD_HHMMSS.log`
  - **新增：彩色文字顯示，關鍵字自動標色**
  - **新增：狀態標籤系統，自動更新執行狀態**
  - **新增：標籤頁獨立日誌支援**
  - 工具列支援 i18n 即時刷新
- `subprocess_runner.py`
  - **新增：支援 DEBUG 模式和標籤頁獨立日誌**
  - **新增：自動更新狀態標籤，顯示當前執行的 BAT 檔案**
  - 安全的外部命令執行，支援串流輸出到 GUI
- `i18n.py`
  - EN/ZH 字典與 `I18N.t(key, **kwargs)` 取文案；`set_lang()` 即時切換
  - 所有 UI 文案（分頁、按鈕、標籤、狀態列、說明）皆透過 i18n key 管理
- `utils_paths.py`
  - `get_resource_path(relative_path)`：在開發與 PyInstaller 打包後皆能正確存取資源

## Callback 介面清單（已實作）
- ADB Tools
  - `on_check_adb_env()`：檢查 adb 路徑/版本、重啟 server（可選）
  - `on_restart_adb()`：`adb kill-server` → `adb start-server`
  - `on_list_adb_devices()`：`adb devices` 串流到日誌
  - `on_check_adb_interface()`：PowerShell 取得 Win32_PnPEntity 中 *ADB* 名稱
  - `on_list_com_ports()`：掃描並列出所有 COM 埠
- Connection Fix
  - `on_scan_at_ports()`：列出可回應 `AT` 的埠（待實作 Python 版本）
  - `on_start_auto_fix()`：執行自動修復流程
- Firmware Upgrade
  - `on_browse_fw()`：選擇韌體檔
  - `on_verify_fw()`：基本校驗（存在/大小/可選 MD5）
  - `on_check_adb_connection()` / `on_check_dm_port()` / `on_test_write_access()`：對應前置檢查
  - `on_start_upgrade()`：執行韌體升級流程

## 執行與打包
- 本機執行
  - Windows PowerShell 進入專案資料夾後執行：
    ```powershell
    python main.py
    ```
- 打包為單一 EXE（發佈建議）
  - 建議直接執行根目錄的 `build.bat`，會自動：
    - 準備 `assets/icon.ico`（由現有 ico 複製）
    - 產生 `version_info.txt`（寫入 `__version__-__build__`）
    - 打包並輸出至 `release/`
  - 若需手動執行 PyInstaller：
    ```powershell
    pyinstaller --onefile --noconsole --icon=assets/icon.ico main.py
    ```

## 使用說明
1. **啟動程式**：執行 `main.py` 或打包後的 EXE 檔案
2. **選擇功能**：點擊對應的標籤頁（ADB 工具、連線修復、韌體升級、設定）
3. **執行操作**：點擊功能按鈕，觀察狀態標籤的即時更新
4. **查看日誌**：在對應標籤頁的日誌區域查看詳細執行記錄
5. **除錯模式**：勾選除錯模式可查看更詳細的執行資訊
6. **語言切換**：右上角可即時切換中英文介面
7. **字體調整**：右上角可調整全域字體大小
8. **設定分頁**：可自訂 GUI 標題（中/英），按「儲存設定」立即生效並寫入 `config.json`

## 注意事項
- 日誌會連續累加，不會自動清空，方便查看完整執行歷史
- 如需清空日誌，可使用各標籤頁的清除按鈕
- 狀態標籤會根據日誌訊息自動更新
- 執行 BAT 檔案時，狀態標籤會顯示當前執行的檔案名稱
- 所有日誌都會自動存檔到 `logs/` 資料夾 