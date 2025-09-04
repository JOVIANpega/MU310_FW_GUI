"""
i18n.py - Internationalization support.
Purpose: Provide a simple runtime-switchable translator for English and Traditional Chinese.
"""

from typing import Dict


EN: Dict[str, str] = {
    "app.title": "MU310 Tools Center",
    "header.font": "Font",
    "header.lang": "Language",
    "header.help": "Help",

    # Common labels
    "common.idle": "Idle",
    "common.running": "Running",
    "common.error": "Error",
    "common.none": "None",
    "ui.current": "Current:",
    "ui.select_fw": "Select firmware file",

    # Common buttons
    "btn.clear_logs": "Clear Logs",
    "btn.run_upgrade": "Run Upgrade",
    "btn.list_com": "List COM Ports",
    "btn.auto_fix": "Run Auto Fix",

    # Tabs
    "tab.adb": "ADB Tools",
    "tab.fix": "Connection Fix",
    "tab.upgrade": "Firmware Upgrade",
    "tab.dm_check": "DM Port Check",
    "tab.help": "Help",

    # ADB tab
    "adb.check_env": "Check ADB Environment",
    "adb.restart": "Restart ADB Server",
    "adb.list": "List ADB Devices",
    "adb.check_interface": "Check ADB Interface",
    "adb.debug": "Debug Mode",

    # Fix tab
    "fix.at_port": "AT Port:",
    "fix.scan": "Scan",
    "fix.reboot_wait": "Reboot wait (s):",
    "fix.start": "Start Auto Fix",
    "fix.auto_check_adb": "Auto check ADB after fix",

    # Upgrade tab
    "upg.fw_file": "Firmware file:",
    "upg.browse": "Browse",
    "upg.verify": "Verify",
    "upg.check_adb": "Check ADB",
    "upg.check_dm": "Check DM PORT",
    "upg.test_write": "Test Write Access",
    "upg.opt.stop": "Stop services",
    "upg.opt.sync2": "Sync twice",
    "upg.opt.pushretry": "Retry push (x3)",
    "upg.opt.adbretry": "Retry ADB (x5)",
    "upg.target": "Target path:",
    "upg.at": "AT channel:",
    "upg.start": "Start Upgrade",

    # Logs toolbar
    "logs.save": "Save",
    "logs.clear": "Clear",
    "logs.scroll_end": "Scroll to End",
    "logs.debug": "Debug Mode",

    # Status bar
    "status.label": "Status: {status}",
    "status.device": "Device: {device}",
    "status.dmport": "DM PORT: {dm}",
    "status.version": "Version: {ver}",

    # Help
    "help.title": "Usage Guide",
    "help.text": (
        "1) ADB Tools: Check environment, restart server, list devices, check interface.\n"
        "2) Connection Fix: Scan/select AT Port, run Auto Fix to set usbcfg and reboot, then recheck ADB.\n"
        "3) Firmware Upgrade: Select firmware (supports any filename, version, location), pre-checks (ADB, DM PORT, write access), then Start Upgrade to push/sync/stop services/trigger FOTA.\n"
        "Notes: Enable Debug Mode for detailed logs. Logs auto-save in logs/ folder."
    ),

    # Keywords Editor
    "keywords.window_title": "Keywords Color Settings",
    "keywords.title": "Keywords Color Settings",
    "keywords.help_text": "Format: keyword=color_code (e.g., adb device=#FF0000)",
    "keywords.shortcuts": "Shortcuts: Ctrl+F Search | Ctrl+S Save | F3 Next | Shift+F3 Previous | Esc Clear",
    "keywords.search_label": "Search Keywords:",
    "keywords.search_btn": "Search",
    "keywords.clear_btn": "Clear",
    "keywords.reload_btn": "Reload",
    "keywords.save_btn": "Save",
    "keywords.cancel_btn": "Cancel",
    "keywords.save_success": "Keywords settings saved to:\n{path}\n\nColor settings are now active!",
    "keywords.save_error": "Failed to save keywords file: {error}",
    "keywords.load_error": "Failed to load keywords file: {error}",

    # Misc
    "common.info": "Info",
}


ZH: Dict[str, str] = {
    "app.title": "MU310 工具中心",
    "header.font": "字體",
    "header.lang": "語言",
    "header.help": "使用說明",

    # Common labels
    "common.idle": "待機中",
    "common.running": "執行中",
    "common.error": "錯誤",
    "common.none": "無",
    "ui.current": "執行檔案:",
    "ui.select_fw": "選擇韌體檔案",

    # Common buttons
    "btn.clear_logs": "清空日誌",
    "btn.run_upgrade": "執行韌體升級",
    "btn.list_com": "列出 COM 埠",
    "btn.auto_fix": "執行自動修復",

    # Tabs
    "tab.adb": "ADB 工具",
    "tab.fix": "連線修復",
    "tab.upgrade": "韌體升級",
    "tab.dm_check": "DM 埠檢查",
    "tab.help": "說明",

    # ADB tab
    "adb.check_env": "檢查 ADB 環境",
    "adb.restart": "重啟 ADB 伺服器",
    "adb.list": "列出 ADB 裝置",
    "adb.check_interface": "檢查 ADB 介面",
    "adb.debug": "除錯模式",

    # Fix tab
    "fix.at_port": "AT 埠:",
    "fix.scan": "掃描",
    "fix.reboot_wait": "重啟等待(秒):",
    "fix.start": "開始自動修復",
    "fix.auto_check_adb": "修復後自動檢查 ADB",

    # Upgrade tab
    "upg.fw_file": "韌體檔案:",
    "upg.browse": "瀏覽",
    "upg.verify": "校驗",
    "upg.check_adb": "檢查 ADB",
    "upg.check_dm": "檢查 DM PORT",
    "upg.test_write": "測試寫入權限",
    "upg.opt.stop": "停止服務",
    "upg.opt.sync2": "同步兩次",
    "upg.opt.pushretry": "push 失敗重試(3)",
    "upg.opt.adbretry": "ADB 重試(5)",
    "upg.target": "目標路徑:",
    "upg.at": "AT 通道:",
    "upg.start": "開始升級",

    # Logs toolbar
    "logs.save": "儲存",
    "logs.clear": "清除",
    "logs.scroll_end": "置底",
    "logs.debug": "除錯模式",

    # Status bar
    "status.label": "狀態: {status}",
    "status.device": "裝置: {device}",
    "status.dmport": "DM 埠: {dm}",
    "status.version": "版本: {ver}",

    # Help
    "help.title": "使用說明",
    "help.text": (
        "1) ADB 工具: 檢查環境、重啟服務、列出裝置、檢查介面。\n"
        "2) 連線修復: 掃描/選擇 AT 埠，執行 Auto Fix 設定 usbcfg 並重啟，之後檢查 ADB。\n"
        "3) 韌體升級: 選擇韌體（支援任何檔名、版本、位置），執行前置檢查(ADB、DM 埠、寫入權限)，按開始升級依序 push/sync/停服務/FOTA。\n"
        "備註: 勾選除錯模式可顯示詳細日誌。日誌會自動存到 logs/ 資料夾。"
    ),

    # Keywords Editor
    "keywords.window_title": "關鍵字顏色設定",
    "keywords.title": "關鍵字顏色設定",
    "keywords.help_text": "格式：關鍵字=顏色代碼 (如: adb device=#FF0000)",
    "keywords.shortcuts": "快捷鍵：Ctrl+F搜尋 | Ctrl+S儲存 | F3下一個 | Shift+F3上一個 | Esc清除",
    "keywords.search_label": "搜尋關鍵字：",
    "keywords.search_btn": "搜尋",
    "keywords.clear_btn": "清除",
    "keywords.reload_btn": "重新載入",
    "keywords.save_btn": "儲存",
    "keywords.cancel_btn": "取消",
    "keywords.save_success": "關鍵字設定已儲存到：\n{path}\n\n顏色設定已立即生效！",
    "keywords.save_error": "儲存關鍵字檔案失敗：{error}",
    "keywords.load_error": "載入關鍵字檔案失敗：{error}",

    # Misc
    "common.info": "資訊",
}


class I18N:
    def __init__(self, lang: str = "EN"):
        self.lang = lang.upper()
        self._dict = EN if self.lang == "EN" else ZH

    def set_lang(self, lang: str):
        self.lang = lang.upper()
        self._dict = EN if self.lang == "EN" else ZH

    def t(self, key: str, **kwargs) -> str:
        text = self._dict.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text