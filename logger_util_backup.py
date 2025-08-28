"""
logger_util.py - Logging utility for GUI.
Purpose: Provide a simple logger that can attach a Text widget panel for live logs and also write logs to a file with timestamps. Supports debug level, colored text for important keywords, and independent tab logging.
"""

import os
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
import re

from i18n import I18N

class GuiLogger:
    def __init__(self, logs_tab_parent, i18n: Optional[I18N] = None):
        self.text_widgets = {}  # 改為字典，key 為標籤頁名稱
        self.debug_enabled = False
        self._init_logfile()
        self.i18n = i18n or I18N("EN")
        self._build_logs_tab(logs_tab_parent)
        self._setup_colors()

    def _setup_colors(self):
        """設定文字顏色標籤"""
        self.colors = {
            "SUCCESS": "#008000",      # 綠色 - 成功訊息
            "ERROR": "#FF0000",        # 紅色 - 錯誤訊息
            "WARNING": "#FF8C00",      # 橙色 - 警告訊息
            "INFO": "#0000FF",         # 藍色 - 一般資訊
            "DEBUG": "#808080",        # 灰色 - 除錯訊息
            "DEVICE": "#800080",       # 紫色 - 裝置相關
            "PORT": "#008080",         # 青色 - 埠口相關
            "ADB": "#FF4500",          # 橙紅色 - ADB 相關
            "USB": "#4B0082",          # 靛色 - USB 相關
            "FOTA": "#FF1493",         # 深粉紅色 - FOTA 相關
        }

    def _init_logfile(self):
        os.makedirs("logs", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join("logs", f"session_{timestamp}.log")
        self._fp = open(self.log_path, "a", encoding="utf-8", buffering=1)

    def _build_logs_tab(self, parent):
        self.toolbar = ttk.Frame(parent)
        self.toolbar.pack(fill=tk.X, padx=6, pady=4)
        self.btn_save = ttk.Button(self.toolbar, text=self.i18n.t("logs.save"), command=self.save_log)
        self.btn_save.pack(side=tk.LEFT)
        self.btn_clear = ttk.Button(self.toolbar, text=self.i18n.t("logs.clear"), command=self.clear_all)
        self.btn_clear.pack(side=tk.LEFT, padx=6)
        self.btn_scroll = ttk.Button(self.toolbar, text=self.i18n.t("logs.scroll_end"), command=self.scroll_to_end)
        self.btn_scroll.pack(side=tk.LEFT)
        self.debug_var = tk.BooleanVar(value=False)
        self.chk_debug = ttk.Checkbutton(self.toolbar, text=self.i18n.t("logs.debug"), variable=self.debug_var, command=self._on_debug_toggle)
        self.chk_debug.pack(side=tk.LEFT, padx=12)

        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        ybar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        xbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        self.main_text = tk.Text(text_frame, wrap=tk.NONE, height=20, xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        ybar.config(command=self.main_text.yview)
        xbar.config(command=self.main_text.xview)
        self.main_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        xbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widgets["logs"] = self.main_text

    def attach_log_panel(self, parent, tab_name: str = "default"):
        """建立獨立的日誌面板，每個標籤頁都有自己的日誌區域"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 日誌文字區域（簡化版，只保留文字區域）
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        ybar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        xbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        text = tk.Text(text_frame, wrap=tk.NONE, height=14, xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        ybar.config(command=text.yview)
        xbar.config(command=text.xview)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        xbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 將文字區域加入到對應的標籤頁
        self.text_widgets[tab_name] = text
        return text

    def refresh_texts(self):
        self.btn_save.config(text=self.i18n.t("logs.save"))
        self.btn_clear.config(text=self.i18n.t("logs.clear"))
        self.btn_scroll.config(text=self.i18n.t("logs.scroll_end"))
        self.chk_debug.config(text=self.i18n.t("logs.debug"))

    def _on_debug_toggle(self):
        self.debug_enabled = self.debug_var.get()

    def _timestamp(self):
        return time.strftime("%H:%M:%S")

    def _apply_colors(self, text_widget, message, level):
        """套用彩色文字到 Text widget"""
        try:
            # 插入時間戳記
            timestamp = f"[{self._timestamp()}] "
            text_widget.insert(tk.END, timestamp)
            
            # 插入等級標籤（帶顏色）
            level_text = f"{level}: "
            text_widget.insert(tk.END, level_text, level)
            
            # 插入訊息內容（帶關鍵字顏色）
            self._insert_colored_message(text_widget, message)
            
            # 插入換行
            text_widget.insert(tk.END, "\n")
            
            # 設定等級標籤的顏色
            text_widget.tag_config(level, foreground=self.colors.get(level, "black"))
            
            # 滾動到底部
            text_widget.see(tk.END)
            
        except tk.TclError:
            pass

    def _insert_colored_message(self, text_widget, message):
        """插入帶顏色的訊息，關鍵字會用不同顏色顯示"""
        try:
            # 定義關鍵字和對應顏色
            keywords = {
                r'\b(ADB|adb)\b': 'ADB',
                r'\b(USB|usb)\b': 'USB',
                r'\b(COM\d+)\b': 'PORT',
                r'\b(DM\s+PORT|DM_PORT)\b': 'PORT',
                r'\b(FOTA|fota)\b': 'FOTA',
                r'\b(device|Device|DEVICE)\b': 'DEVICE',
                r'\b(success|Success|SUCCESS)\b': 'SUCCESS',
                r'\b(error|Error|ERROR)\b': 'ERROR',
                r'\b(warning|Warning|WARNING)\b': 'WARNING',
                r'\b(failed|Failed|FAILED)\b': 'ERROR',
                r'\b(connected|Connected|CONNECTED)\b': 'SUCCESS',
                r'\b(disconnected|Disconnected|DISCONNECTED)\b': 'WARNING',
                r'\b(reboot|Reboot|REBOOT)\b': 'WARNING',
                r'\b(upgrade|Upgrade|UPGRADE)\b': 'FOTA',
                r'\b(firmware|Firmware|FIRMWARE)\b': 'FOTA',
            }
            
            # 分割訊息為關鍵字和一般文字
            remaining_text = message
            current_pos = 0
            
            for pattern, color_tag in keywords.items():
                matches = list(re.finditer(pattern, remaining_text, re.IGNORECASE))
                if matches:
                    for match in reversed(matches):  # 從後往前處理，避免位置偏移
                        start, end = match.span()
                        # 插入關鍵字前的文字
                        if start > current_pos:
                            text_widget.insert(tk.END, remaining_text[current_pos:start])
                        # 插入關鍵字（帶顏色）
                        keyword = remaining_text[start:end]
                        text_widget.insert(tk.END, keyword, color_tag)
                        text_widget.tag_config(color_tag, foreground=self.colors.get(color_tag, "black"))
                        current_pos = end
            
            # 插入剩餘文字
            if current_pos < len(remaining_text):
                text_widget.insert(tk.END, remaining_text[current_pos:])
                
        except Exception:
            # 如果彩色處理失敗，直接插入原始訊息
            text_widget.insert(tk.END, message)

    def log(self, message, *, level="INFO", tab_name: str = "all"):
        """記錄日誌到指定標籤頁或所有標籤頁"""
        line = f"[{self._timestamp()}] {level}: {message}\n"
        
        # 寫入檔案（純文字格式）
        try:
            self._fp.write(line)
        except Exception:
            pass
        
        # 顯示到 GUI（彩色格式）
        if tab_name == "all":
            # 顯示到所有標籤頁
            for w in self.text_widgets.values():
                try:
                    self._apply_colors(w, message, level)
                except Exception:
                    pass
        else:
            # 只顯示到指定標籤頁
            if tab_name in self.text_widgets:
                try:
                    self._apply_colors(self.text_widgets[tab_name], message, level)
                except Exception:
                    pass

    def debug(self, message, tab_name: str = "all"):
        """除錯訊息，只在 DEBUG 模式開啟時顯示"""
        if self.debug_enabled:
            self.log(message, level="DEBUG", tab_name=tab_name)

    def error(self, message, tab_name: str = "all"):
        self.log(message, level="ERROR", tab_name=tab_name)

    def warning(self, message, tab_name: str = "all"):
        self.log(message, level="WARNING", tab_name=tab_name)

    def success(self, message, tab_name: str = "all"):
        self.log(message, level="SUCCESS", tab_name=tab_name)

    def clear_all(self):
        """清空所有日誌顯示"""
        for w in self.text_widgets.values():
            try:
                w.delete("1.0", tk.END)
            except Exception:
                pass

    def clear_logs(self, tab_name: str = "all"):
        """清空指定標籤頁的日誌"""
        if tab_name == "all":
            # 清空所有標籤頁的日誌
            for text_widget in self.text_widgets.values():
                try:
                    text_widget.delete("1.0", tk.END)
                except Exception:
                    pass
        else:
            # 清空指定標籤頁的日誌
            if tab_name in self.text_widgets:
                try:
                    self.text_widgets[tab_name].delete("1.0", tk.END)
                except Exception:
                    pass

    def save_log(self):
        # Already saving to file in real-time; this is a no-op placeholder
        self.log("Log is continuously saved to: " + self.log_path, level="INFO")

    def scroll_to_end(self):
        for w in self.text_widgets.values():
            try:
                w.see(tk.END)
            except Exception:
                pass 