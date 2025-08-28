"""
main.py - MU310 Tools Center GUI entry point.
Purpose: Provide a Tkinter-based GUI with simplified tabs for ADB Tools, Connection Fix, Firmware Upgrade, and DM Port Check. 
Each tab contains only one main button that executes the corresponding BAT file. 
Includes a global font size control and shared log panels for all tabs. 
English/Chinese UI with runtime switching.
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

from utils_paths import get_resource_path
from logger_util import GuiLogger
from i18n import I18N
from subprocess_runner import run_bat_file, run_command
from version import __version__, __build__

APP_SIZE = "900x600"
DEFAULT_FONT_SIZE = 12
CONFIG_FILENAME = "config.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self._load_config()
        default_lang = self.config_data.get("lang", "ZH")
        self.i18n = I18N(default_lang)
        # Window geometry (size)
        w = int(self.config_data.get("win_w", 900))
        h = int(self.config_data.get("win_h", 600))
        self.geometry(f"{w}x{h}")
        self.minsize(900, 600)
        self.resizable(True, True)
        self.title(self._get_app_title_text())

        self.current_font_size = int(self.config_data.get("font_size", DEFAULT_FONT_SIZE))
        self._init_fonts(self.current_font_size)
        self._init_styles()

        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        # Persist window size on resize/close
        self._geom_save_after = None
        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _app_dir(self) -> str:
        try:
            base = sys._MEIPASS  # type: ignore[attr-defined]
        except Exception:
            base = os.path.abspath(".")
        return base

    def _config_path(self) -> str:
        return os.path.join(self._app_dir(), CONFIG_FILENAME)

    def _load_config(self):
        self.config_data = {}
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
        except Exception:
            self.config_data = {}

    def _save_config(self):
        try:
            with open(self._config_path(), "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _init_fonts(self, size: int):
        try:
            self.tk_default_font = tkfont.nametofont("TkDefaultFont")
            self.tk_text_font = tkfont.nametofont("TkTextFont")
            self.tk_fixed_font = tkfont.nametofont("TkFixedFont")
        except tk.TclError:
            self.tk_default_font = tkfont.Font(family="Segoe UI", size=size)
            self.tk_text_font = tkfont.Font(family="Segoe UI", size=size)
            self.tk_fixed_font = tkfont.Font(family="Consolas", size=size)
        for f in (self.tk_default_font, self.tk_text_font, self.tk_fixed_font):
            try:
                f.configure(size=size)
            except Exception:
                pass
        self.option_add("*Font", self.tk_default_font)

    def _init_styles(self):
        try:
            style = ttk.Style()
            style.theme_use("clam")  # 使用 clam 主題以支援自訂顏色
            style.configure("Accent.TButton", padding=6)

            # 路徑淺藍底樣式
            style.configure("Path.TLabel", background="#E6F2FF", foreground="#000000")

            # 抬頭列藍灰主題（更柔和）
            header_bg = "#F5F7FA"      # 淺藍灰
            header_btn = "#E5ECF6"     # 按鈕底
            header_btn_act = "#D7E3F3" # hover
            header_btn_down = "#C5D6EE"# pressed
            header_fg = "#1F2937"      # 深灰文字
            style.configure("Header.TFrame", background=header_bg)
            style.configure("Header.TLabel", background=header_bg, foreground=header_fg)
            style.configure("Header.TButton", background=header_btn, foreground=header_fg)
            style.map(
                "Header.TButton",
                background=[("active", header_btn_act), ("pressed", header_btn_down)],
                foreground=[("active", header_fg), ("pressed", header_fg)],
            )

            # Help 按鈕深綠色樣式
            help_bg = "#1f6f3e"       # 深綠
            help_hover = "#2a8f53"    # hover 綠
            help_pressed = "#176133"  # pressed 綠
            help_fg = "#ffffff"
            style.configure("Help.TButton", background=help_bg, foreground=help_fg)
            style.map(
                "Help.TButton",
                background=[("active", help_hover), ("pressed", help_pressed)],
                foreground=[("active", help_fg), ("pressed", help_fg)],
            )

            # Font +/- 按鈕使用同系深綠色樣式
            style.configure("FontCtl.TButton", background=help_bg, foreground=help_fg)
            style.map(
                "FontCtl.TButton",
                background=[("active", help_hover), ("pressed", help_pressed)],
                foreground=[("active", help_fg), ("pressed", help_fg)],
            )

            # 分頁字體固定 12
            self.tab_fixed_font = tkfont.Font(family="Segoe UI", size=12)
            style.configure("Custom.TNotebook", background="#f0f0f0")
            style.configure(
                "Custom.TNotebook.Tab",
                font=self.tab_fixed_font,
                padding=(12, 6),
                background="#e6e6e6",
                foreground="#000000",
            )
            # Hover 樣式
            style.configure(
                "Hover.TNotebook.Tab",
                font=self.tab_fixed_font,
                padding=(12, 6),
                background="#cfe8ff",
                foreground="#000000",
            )
            style.map(
                "Custom.TNotebook.Tab",
                background=[("selected", "#2b579a")],
                foreground=[("selected", "#ffffff")],
            )

            # 主標題樣式：大字＋淡黃色底
            self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
            style.configure("Title.TLabel", background="#FFF8DC", foreground="#000000")  # Cornsilk
        except Exception:
            pass

    def _fw_image_dir(self) -> str:
        """回傳打包/原始執行時的 FW_IMAGE 目錄路徑"""
        base = self._app_dir()
        return os.path.join(base, "FW_IMAGE")

    def _help_path(self) -> str:
        base = self._app_dir()
        return os.path.join(base, "assets", "help.html")

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        self.title_lbl = ttk.Label(header, text=self._get_app_title_text(), style="Title.TLabel")
        self.title_lbl.pack(side=tk.LEFT)
        try:
            self.title_lbl.configure(font=self.title_font)
        except Exception:
            pass

        header_spacer = ttk.Label(header, text="")
        header_spacer.pack(side=tk.LEFT, expand=True)

        self.lang_label = ttk.Label(header, text=self.i18n.t("header.lang"), style="Header.TLabel")
        self.lang_label.pack(side=tk.RIGHT, padx=(8, 4))
        self.lang_var = tk.StringVar(value=self.i18n.lang)
        self.lang_combo = ttk.Combobox(header, state="readonly", values=["EN", "ZH"], textvariable=self.lang_var, width=4)
        self.lang_combo.pack(side=tk.RIGHT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_change)

        # 使用說明按鈕（開啟內建HTML）
        self.help_btn = ttk.Button(header, text=self.i18n.t("header.help"), command=self.on_open_help, style="Help.TButton")
        self.help_btn.pack(side=tk.RIGHT, padx=(8, 8))

        font_box = ttk.Frame(header, style="Header.TFrame")
        font_box.pack(side=tk.RIGHT, padx=(16, 0))
        self.font_label = ttk.Label(font_box, text=self.i18n.t("header.font"), style="Header.TLabel")
        self.font_label.pack(side=tk.LEFT, padx=(0, 6))
        minus_btn = ttk.Button(font_box, text="-", width=3, command=self.on_font_decrease, style="FontCtl.TButton")
        minus_btn.pack(side=tk.LEFT)
        self.size_lbl = ttk.Label(font_box, text=str(self.current_font_size), style="Header.TLabel")
        self.size_lbl.pack(side=tk.LEFT)
        plus_btn = ttk.Button(font_box, text="+", width=3, command=self.on_font_increase, style="FontCtl.TButton")
        plus_btn.pack(side=tk.LEFT)

    def _build_tabs(self):
        self.container = ttk.Notebook(self, style="Custom.TNotebook")
        self.container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # 初始化 hover 狀態並綁定事件
        self._last_hover_tab = None
        self.container.bind("<Motion>", self._on_tab_motion)
        self.container.bind("<Leave>", self._on_tab_leave)

        self.tab_adb = ttk.Frame(self.container)
        self.tab_fix = ttk.Frame(self.container)
        self.tab_upgrade = ttk.Frame(self.container)
        self.tab_settings = ttk.Frame(self.container)
        # 移除 DM 檢查與 Help 分頁

        self.container.add(self.tab_adb, text=self.i18n.t("tab.adb"))
        self.container.add(self.tab_fix, text=self.i18n.t("tab.fix"))
        self.container.add(self.tab_upgrade, text=self.i18n.t("tab.upgrade"))
        self.container.add(self.tab_settings, text=self._s_text("tab"))
        # Help tab removed（僅保留按鈕開啟本機HTML）

        # 建立 logger 實例，但不附加到特定標籤頁
        self.logger = GuiLogger(self, i18n=self.i18n)

        self._build_tab_adb()
        self._build_tab_fix()
        self._build_tab_upgrade()
        self._build_tab_settings()
        # self._build_tab_dm_check()  # 已移除
        # Help tab removed

    def _clear_tab_hover(self):
        if getattr(self, "_last_hover_tab", None) is not None:
            try:
                self.container.tab(self._last_hover_tab, style="Custom.TNotebook.Tab")
            except Exception:
                pass
            self._last_hover_tab = None

    def _on_tab_leave(self, event):
        self._clear_tab_hover()

    def _on_tab_motion(self, event):
        try:
            idx = self.container.index(f"@{event.x},{event.y}")
        except Exception:
            idx = None

        if idx is None:
            self._clear_tab_hover()
            return

        if idx == self._last_hover_tab:
            return

        # 清理上一個 hover
        self._clear_tab_hover()

        # 當前選取不覆蓋，僅對非選取分頁套 hover 樣式
        try:
            current = self.container.index("current")
        except Exception:
            current = None

        if idx is not None and idx != current:
            try:
                self.container.tab(idx, style="Hover.TNotebook.Tab")
                self._last_hover_tab = idx
            except Exception:
                pass

    def _build_statusbar(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar(value=self.i18n.t("status.label", status=self.i18n.t("common.idle")))
        self.device_var = tk.StringVar(value=self.i18n.t("status.device", device="N/A"))
        self.dmport_var = tk.StringVar(value=self.i18n.t("status.dmport", dm="N/A"))
        self.version_var = tk.StringVar(value=self.i18n.t("status.version", ver=f"v{__version__}-{__build__}"))

        self.status_lbl = ttk.Label(status_frame, textvariable=self.status_var)
        self.device_lbl = ttk.Label(status_frame, textvariable=self.device_var)
        self.dmport_lbl = ttk.Label(status_frame, textvariable=self.dmport_var)
        self.version_lbl = ttk.Label(status_frame, textvariable=self.version_var)

        self.status_lbl.pack(side=tk.LEFT, padx=8)
        self.device_lbl.pack(side=tk.LEFT, padx=16)
        self.dmport_lbl.pack(side=tk.LEFT, padx=16)
        self.version_lbl.pack(side=tk.RIGHT, padx=8)

    # =============== Tab Builders ===============
    def _build_tab_adb(self):
        frame = ttk.Frame(self.tab_adb)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 狀態 LABEL
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_adb_status = ttk.Label(status_frame, text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}")
        self.lbl_adb_status.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_adb_bat = ttk.Label(status_frame, text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}", style="Path.TLabel")
        self.lbl_adb_bat.pack(side=tk.LEFT)
        
        # 按鈕框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(4, 10), anchor=tk.W)
        
        # ADB 環境檢查按鈕
        self.btn_adb_check = ttk.Button(
            button_frame, 
            text=self.i18n.t("adb.check_env"), 
            command=self.on_run_adb_check,
            style="Accent.TButton"
        )
        self.btn_adb_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # 列出 COM 埠按鈕
        self.btn_list_com = ttk.Button(
            button_frame, 
            text=self.i18n.t("btn.list_com"), 
            command=self.on_list_com_ports
        )
        self.btn_list_com.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按鈕
        self.btn_clear_adb = ttk.Button(
            button_frame, 
            text=self.i18n.t("btn.clear_logs"), 
            command=self.on_clear_adb_logs
        )
        self.btn_clear_adb.pack(side=tk.LEFT)
        
        # 日誌面板
        self.logger.attach_log_panel(parent=frame, tab_name="adb")

    def _build_tab_fix(self):
        frame = ttk.Frame(self.tab_fix)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 狀態 LABEL
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_fix_status = ttk.Label(status_frame, text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}")
        self.lbl_fix_status.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_fix_bat = ttk.Label(status_frame, text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}", style="Path.TLabel")
        self.lbl_fix_bat.pack(side=tk.LEFT)
        
        # 按鈕框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(4, 10), anchor=tk.W)
        
        # 只有一個主要按鈕
        self.btn_auto_fix = ttk.Button(
            button_frame, 
            text=self.i18n.t("btn.auto_fix"), 
            command=self.on_run_auto_fix,
            style="Accent.TButton"
        )
        self.btn_auto_fix.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按鈕
        self.btn_clear_fix = ttk.Button(
            button_frame, 
            text=self.i18n.t("btn.clear_logs"), 
            command=self.on_clear_fix_logs
        )
        self.btn_clear_fix.pack(side=tk.LEFT)
        
        # 日誌面板
        self.logger.attach_log_panel(parent=frame, tab_name="fix")

    def _build_tab_upgrade(self):
        frame = ttk.Frame(self.tab_upgrade)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 狀態 LABEL
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_upgrade_status = ttk.Label(status_frame, text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}")
        self.lbl_upgrade_status.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_upgrade_bat = ttk.Label(status_frame, text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}", style="Path.TLabel")
        self.lbl_upgrade_bat.pack(side=tk.LEFT)
        
        # 韌體檔案選擇
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_fw_prompt = ttk.Label(file_frame, text=self.i18n.t("upg.fw_file"))
        self.lbl_fw_prompt.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # 顯示與完整路徑分離的變數
        self.firmware_full = tk.StringVar()
        self.firmware_show = tk.StringVar()
        
        self.firmware_entry = ttk.Entry(file_frame, textvariable=self.firmware_show)
        self.firmware_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        self.btn_browse_firmware = ttk.Button(
            file_frame, 
            text=self.i18n.t("upg.browse"), 
            command=self.on_browse_firmware,
            width=8
        )
        self.btn_browse_firmware.grid(row=0, column=2, padx=(0, 10))
        
        # 與瀏覽同列的按鍵
        self.btn_upgrade = ttk.Button(
            file_frame, 
            text=self.i18n.t("btn.run_upgrade"), 
            command=self.on_run_upgrade,
            style="Accent.TButton",
            width=12
        )
        self.btn_upgrade.grid(row=0, column=3, padx=(0, 10))
        
        self.btn_clear_upgrade = ttk.Button(
            file_frame, 
            text=self.i18n.t("btn.clear_logs"), 
            command=self.on_clear_upgrade_logs,
            width=8
        )
        self.btn_clear_upgrade.grid(row=0, column=4)
        
        # 讓 Entry 自動撐滿
        file_frame.columnconfigure(1, weight=1)
        
        # 日誌面板
        self.logger.attach_log_panel(parent=frame, tab_name="upgrade")

    # Help tab removed（僅保留按鈕開啟本機HTML）

    def _build_tab_settings(self):
        frame = ttk.Frame(self.tab_settings)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        self.settings_title_label = ttk.Label(frame, text=self._s_text("title"))
        self.settings_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # EN 標題
        self.settings_lbl_en = ttk.Label(frame, text=self._s_text("label_en"))
        self.settings_lbl_en.grid(row=1, column=0, sticky="e", padx=(0, 8))
        self.title_en_var = tk.StringVar(value=self.config_data.get("title_en", ""))
        v_en = (self.register(self._validate_title_input), '%P')
        ent_en = ttk.Entry(frame, textvariable=self.title_en_var, width=30, validate='key', validatecommand=v_en)
        ent_en.grid(row=1, column=1, sticky="w", pady=2)

        # ZH 標題
        self.settings_lbl_zh = ttk.Label(frame, text=self._s_text("label_zh"))
        self.settings_lbl_zh.grid(row=2, column=0, sticky="e", padx=(0, 8))
        self.title_zh_var = tk.StringVar(value=self.config_data.get("title_zh", ""))
        v_zh = (self.register(self._validate_title_input), '%P')
        ent_zh = ttk.Entry(frame, textvariable=self.title_zh_var, width=30, validate='key', validatecommand=v_zh)
        ent_zh.grid(row=2, column=1, sticky="w", pady=2)

        # 若設定值空白，預設帶入 i18n 的標題（避免首次顯示為空）
        try:
            if not (self.title_en_var.get() or "").strip():
                self.title_en_var.set(I18N("EN").t("app.title"))
            if not (self.title_zh_var.get() or "").strip():
                self.title_zh_var.set(I18N("ZH").t("app.title"))
        except Exception:
            pass

        # 儲存按鈕
        self.settings_btn_save = ttk.Button(
            frame,
            text=self._s_text("save_btn"),
            style="Accent.TButton",
            command=self.on_save_settings,
        )
        self.settings_btn_save.grid(row=3, column=1, sticky="e", pady=(12, 0))

        # 固定欄寬顯示 30 字元，不需撐滿
        # frame.columnconfigure(1, weight=1)

    def _validate_title_input(self, proposed: str) -> bool:
        """限制標題輸入長度至 30 字元。"""
        try:
            return len(proposed) <= 30
        except Exception:
            return True

    def _get_app_title_text(self) -> str:
        """依目前語言回傳應顯示的應用標題，支援使用者覆寫。"""
        lang = getattr(self.i18n, "lang", "ZH")
        if lang == "EN":
            t = (self.config_data.get("title_en") or "").strip()
            if t:
                return t
        else:
            t = (self.config_data.get("title_zh") or "").strip()
            if t:
                return t
        # fallback 使用 i18n 預設標題
        return self.i18n.t("app.title")

    def _apply_title_override(self):
        """套用目前標題覆寫到視窗與抬頭 Label。"""
        txt = self._get_app_title_text()
        try:
            self.title(txt)
            self.title_lbl.config(text=txt)
        except Exception:
            pass

    def _s_text(self, key: str) -> str:
        """設定分頁文字（EN/ZH）不依賴 i18n 檔，避免破壞原有字典。"""
        lang = getattr(self.i18n, "lang", "ZH")
        zh = {
            "tab": "設定",
            "title": "設定（可自訂標題，立即生效）",
            "label_en": "英文標題",
            "label_zh": "中文標題",
            "save_btn": "儲存設定",
            "saved": "設定已儲存並立即生效",
        }
        en = {
            "tab": "Settings",
            "title": "Settings (custom title, apply immediately)",
            "label_en": "Title (EN)",
            "label_zh": "Title (ZH)",
            "save_btn": "Save Settings",
            "saved": "Settings saved and applied",
        }
        return (en if lang == "EN" else zh).get(key, key)

    # =============== Font & Language controls ===============
    def on_font_increase(self):
        self.current_font_size = min(self.current_font_size + 1, 24)
        for f in (self.tk_default_font, self.tk_text_font, self.tk_fixed_font):
            try:
                f.configure(size=self.current_font_size)
            except Exception:
                pass
        self.size_lbl.config(text=str(self.current_font_size))
        self.config_data["font_size"] = self.current_font_size
        self._save_config()

    def on_font_decrease(self):
        self.current_font_size = max(self.current_font_size - 1, 8)
        for f in (self.tk_default_font, self.tk_text_font, self.tk_fixed_font):
            try:
                f.configure(size=self.current_font_size)
            except Exception:
                pass
        self.size_lbl.config(text=str(self.current_font_size))
        self.config_data["font_size"] = self.current_font_size
        self._save_config()

    def on_lang_change(self, event=None):
        lang = self.lang_var.get()
        self.i18n.set_lang(lang)
        self.config_data["lang"] = lang
        self._save_config()
        # 改為呼叫簡化且與現況相符的語言刷新
        self._retranslate()

    def on_save_settings(self):
        """儲存設定：自訂標題（EN/ZH），並立即生效。"""
        try:
            self.config_data["title_en"] = self.title_en_var.get().strip()
            self.config_data["title_zh"] = self.title_zh_var.get().strip()
            self._save_config()
            self._apply_title_override()
            # 狀態列提示
            self.status_var.set(self._s_text("saved"))
        except Exception as e:
            try:
                messagebox.showerror("Error", f"Save settings failed: {e}")
            except Exception:
                pass

    def _retranslate(self):
        """更新所有可見文字，避免參照不存在的元件。"""
        self._update_lang()
        self.status_var.set(self.i18n.t("status.label", status=self.i18n.t("common.idle")))
        self.device_var.set(self.i18n.t("status.device", device="N/A"))
        self.dmport_var.set(self.i18n.t("status.dmport", dm="N/A"))
        self.version_var.set(self.i18n.t("status.version", ver=f"v{__version__}-{__build__}"))
        self.logger.i18n = self.i18n
        self.logger.refresh_texts()

    def _update_lang(self):
        """更新所有 UI 元素的語言"""
        self._apply_title_override()
        
        # 更新標籤頁標題
        self.container.tab(self.tab_adb, text=self.i18n.t("tab.adb"))
        self.container.tab(self.tab_fix, text=self.i18n.t("tab.fix"))
        self.container.tab(self.tab_upgrade, text=self.i18n.t("tab.upgrade"))
        self.container.tab(self.tab_settings, text=self._s_text("tab"))
        # DM 檢查分頁已移除
        # Help tab removed
        
        # 更新按鈕文字
        self.btn_adb_check.config(text=self.i18n.t("adb.check_env"))
        self.btn_list_com.config(text=self.i18n.t("btn.list_com"))
        self.btn_clear_adb.config(text=self.i18n.t("btn.clear_logs"))
        self.btn_auto_fix.config(text=self.i18n.t("btn.auto_fix"))
        self.btn_clear_fix.config(text=self.i18n.t("btn.clear_logs"))
        self.btn_upgrade.config(text=self.i18n.t("btn.run_upgrade"))
        self.btn_clear_upgrade.config(text=self.i18n.t("btn.clear_logs"))

        # 設定分頁文案
        try:
            self.settings_title_label.config(text=self._s_text("title"))
            self.settings_lbl_en.config(text=self._s_text("label_en"))
            self.settings_lbl_zh.config(text=self._s_text("label_zh"))
            self.settings_btn_save.config(text=self._s_text("save_btn"))
        except Exception:
            pass

        # 升級分頁標籤與狀態文字
        try:
            self.lbl_fw_prompt.config(text=self.i18n.t("upg.fw_file"))
            self.btn_browse_firmware.config(text=self.i18n.t("upg.browse"))
            self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}")
            # 若目前未選擇檔案，顯示 None
            current_text = self.firmware_full.get().strip()
            if current_text:
                self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} {os.path.basename(current_text)}")
            else:
                self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")
        except Exception:
            pass
        
        # Help tab removed

    # =============== Window events ===============
    def _on_configure(self, event):
        if event.widget is self and self.state() == "normal":
            self.config_data["win_w"] = self.winfo_width()
            self.config_data["win_h"] = self.winfo_height()
            # Debounce saving to avoid excessive disk writes
            if self._geom_save_after is not None:
                try:
                    self.after_cancel(self._geom_save_after)
                except Exception:
                    pass
            self._geom_save_after = self.after(500, self._save_config)

    def _on_close(self):
        # Save geometry immediately
        try:
            self.config_data["win_w"] = self.winfo_width()
            self.config_data["win_h"] = self.winfo_height()
            self._save_config()
        except Exception:
            pass
        self.destroy()

    def on_open_help(self):
        try:
            import webbrowser
            path = self._help_path()
            if os.path.exists(path):
                webbrowser.open_new_tab(path)
                self.logger.log(f"Open help: {path}")
            else:
                self.logger.error("找不到使用說明檔 (assets/help.html)")
        except Exception as e:
            self.logger.error(f"開啟使用說明失敗: {e}")

    # =============== Callbacks wired to BAT ===============
    def on_run_adb_check(self):
        """執行 ADB 環境檢查"""
        self.logger.log(self.i18n.t("adb.check_env") + "...", level="INFO", tab_name="adb")
        
        # 更新狀態 LABEL
        self.lbl_adb_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.running'))}")
        self.lbl_adb_bat.config(text=f"{self.i18n.t('ui.current')} ADB Environment Check.bat")
        
        bat = get_resource_path("ADB Environment Check.bat")
        if os.path.exists(bat):
            run_bat_file(bat, logger=self.logger, cwd=os.path.dirname(bat), tab_name="adb")
            # 執行完成後更新狀態
            self.after(1000, lambda: self.lbl_adb_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}"))
        else:
            self.logger.error("ADB Environment Check.bat not found", tab_name="adb")
            self.lbl_adb_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.error'))}")
            self.lbl_adb_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")

    def on_run_auto_fix(self):
        """執行自動修復"""
        self.logger.log(self.i18n.t("btn.auto_fix") + "...", level="INFO", tab_name="fix")
        
        # 更新狀態 LABEL
        self.lbl_fix_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.running'))}")
        self.lbl_fix_bat.config(text=f"{self.i18n.t('ui.current')} auto_fix_adb_ENG.bat")
        
        bat = get_resource_path("auto_fix_adb_ENG.bat")
        if os.path.exists(bat):
            run_bat_file(bat, logger=self.logger, cwd=os.path.dirname(bat), tab_name="fix")
            # 執行完成後更新狀態
            self.after(1000, lambda: self.lbl_fix_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}"))
        else:
            self.logger.error("auto_fix_adb_ENG.bat not found", tab_name="fix")
            self.lbl_fix_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.error'))}")
            self.lbl_fix_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")

    def on_run_upgrade(self):
        """執行韌體升級（必須選擇檔案）"""
        fw = self.firmware_full.get().strip()
        if not fw:
            self.logger.error("Please select firmware (*.bin) first", tab_name="upgrade")
            self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.error'))}")
            self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")
            return
        if not os.path.exists(fw):
            self.logger.error(f"Firmware file not found: {fw}", tab_name="upgrade")
            self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.error'))}")
            self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")
            return

        fw_abs = os.path.abspath(fw)
        bat = get_resource_path("Burn_in _611GT.bat")
        if not os.path.exists(bat):
            self.logger.error("Burn_in _611GT.bat not found", tab_name="upgrade")
            self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.error'))}")
            self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} {self.i18n.t('common.none')}")
            return

        self.logger.log(f"{self.i18n.t('btn.run_upgrade')} : {fw_abs}", tab_name="upgrade")
        self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.running'))}")
        self.lbl_upgrade_bat.config(text=f"{self.i18n.t('ui.current')} Burn_in _611GT.bat")

        cmd = f'cmd /c chcp 65001 > nul & call "{bat}" "{fw_abs}"'
        run_command(
            cmd,
            logger=self.logger,
            cwd=os.path.dirname(bat),
            shell=True,
            tab_name="upgrade",
        )
        self.after(1000, lambda: self.lbl_upgrade_status.config(text=f"{self.i18n.t('status.label', status=self.i18n.t('common.idle'))}"))

    # DM 檢查功能已移除

    def on_list_com_ports(self):
        """列出所有 COM 埠"""
        self.logger.log("Scan COM ports...", level="INFO", tab_name="adb")
        
        try:
            import serial.tools.list_ports as list_ports
            ports = list(list_ports.comports())
            if not ports:
                self.logger.warning("No COM ports found", tab_name="adb")
                return
            
            self.logger.log(f"Found {len(ports)} COM ports:", level="INFO", tab_name="adb")
            for p in ports:
                line = self._format_port_line(p)
                self.logger.log(f"  {line}", level="INFO", tab_name="adb")
                
        except Exception as e:
            self.logger.error(f"Scan COM ports failed: {e}", tab_name="adb")

    def _format_port_line(self, port_info):
        """格式化並清洗單一 COM 埠資訊，避免名稱重複顯示。

        Windows 上 pyserial 的 description 常見為「通訊連接埠 (COM3)」，
        若再與 device=COM3 拼接，容易出現類似『COM3 - 通訊連接埠 (COM3)』的重複。
        這裡統一規則：
        - 主要顯示 device（如 COM3）
        - 其次顯示描述（去除括號內重複的 device）
        - 若可取得 VID:PID，附加於末端
        """
        try:
            device = getattr(port_info, "device", "?") or "?"
            desc = getattr(port_info, "description", "") or ""

            # 去除描述中括號重複的 device，例："(COM3COM3" 或 "(COM3)" 只保留一次
            if device:
                desc = desc.replace(f"({device}{device}", f"({device}")
                # 若有重覆 device 無括號的怪異情形，一併清理
                while f"{device}{device}" in desc:
                    desc = desc.replace(f"{device}{device}", device)

            # 1) 以連續兩次出現的裝置名稱為界，保留到第二次裝置名稱結束
            try:
                lower_desc = desc.lower()
                lower_dev = device.lower()
                first_i = lower_desc.find(lower_dev)
                if first_i != -1:
                    second_i = lower_desc.find(lower_dev, first_i + len(device))
                    if second_i != -1:
                        desc = desc[: second_i + len(device)]
            except Exception:
                pass

            # 2) 若描述中有多段以 " - " 分隔（重複片段），僅保留到第二段開始前
            try:
                first_sep = desc.find(" - ")
                if first_sep != -1:
                    second_sep = desc.find(" - ", first_sep + 3)
                    if second_sep != -1:
                        desc = desc[:second_sep]
            except Exception:
                pass

            # 3) 若有右括號，僅保留第一個右括號前的內容（精簡顯示）
            if ")" in desc:
                desc = desc.split(")", 1)[0]

            # 組合基本字串
            parts = [device]
            if desc and desc.strip().upper() != device.upper():
                parts.append("- ")
                parts.append(desc.strip())

            # 附加 VID:PID（若有）
            vid = getattr(port_info, "vid", None)
            pid = getattr(port_info, "pid", None)
            if vid is not None and pid is not None:
                parts.append(f"  [VID:PID {vid:04X}:{pid:04X}]")

            return "".join(parts)
        except Exception:
            # 保底：直接回傳 device 與描述
            return f"{getattr(port_info, 'device', '?')} - {getattr(port_info, 'description', '')}"

    def on_clear_adb_logs(self):
        """清空 ADB 標籤頁日誌"""
        self.logger.clear_logs(tab_name="adb")

    def on_clear_fix_logs(self):
        """清空連線修復標籤頁日誌"""
        self.logger.clear_logs(tab_name="fix")

    def on_clear_upgrade_logs(self):
        """清空韌體升級標籤頁日誌"""
        self.logger.clear_logs(tab_name="upgrade")

    # DM 檢查分頁已移除

    def on_browse_firmware(self):
        """開啟檔案對話框選擇韌體檔案"""
        init_dir = self._fw_image_dir()
        try:
            os.makedirs(init_dir, exist_ok=True)
        except Exception:
            pass
        file_path = filedialog.askopenfilename(
            title=self.i18n.t("ui.select_fw"),
            filetypes=[("韌體檔案", "*.bin"), ("所有檔案", "*.*")],
            initialdir=init_dir
        )
        if file_path:
            self.firmware_full.set(file_path)
            self.firmware_show.set(self._shorten_middle(file_path))
            self.logger.log(f"{self.i18n.t('upg.fw_file')} {file_path}", tab_name="upgrade")

    def _shorten_middle(self, path: str, max_px: int = 520) -> str:
        """以 Entry 的字體測寬，超出寬度時中間省略顯示。"""
        try:
            f = self.firmware_entry.cget("font")
            font = tkfont.Font(font=f)
        except Exception:
            font = tkfont.Font(family="Segoe UI", size=12)
        txt = path.replace("\\", "/")
        if font.measure(txt) <= max_px:
            return txt
        import os
        base = os.path.basename(txt)
        dirn = os.path.dirname(txt)
        left = dirn
        right = base
        sep = "…"
        s = left + "/" + right
        # 迭代縮短左側與右側直到寬度符合
        while font.measure(s) > max_px and len(left) > 1:
            left = left[: max(1, len(left) // 2)]
            s = left + sep + "/" + right
            if font.measure(s) > max_px and len(right) > 8:
                right = right[-max(8, len(right) - 2) :]
                s = left + sep + "/" + right
        return s


if __name__ == "__main__":
    app = App()
    app.mainloop() 