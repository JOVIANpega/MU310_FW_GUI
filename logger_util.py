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
        # self._build_logs_tab(logs_tab_parent)  # 已移除
        self._setup_colors()
        self.custom_keywords = {}  # 存放自訂關鍵字
        self._load_keywords_from_file()  # 載入自訂關鍵字

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

    def _load_keywords_from_file(self):
        """從 keywords.txt 檔案載入自訂關鍵字"""
        try:
            # 優先使用當前目錄的 keywords.txt
            keywords_file = os.path.join(os.getcwd(), "keywords.txt")
            if not os.path.exists(keywords_file):
                # 如果當前目錄沒有，嘗試使用資源路徑
                try:
                    from utils_paths import get_resource_path
                    keywords_file = get_resource_path("keywords.txt")
                except:
                    return
            
            if not os.path.exists(keywords_file):
                return
                
            with open(keywords_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.custom_keywords = {}
            for line in lines:
                line = line.strip()
                # 跳過註解和空行
                if not line or line.startswith('#'):
                    continue
                
                # 解析 關鍵字=顏色 格式
                if '=' in line:
                    try:
                        keyword, color = line.split('=', 1)
                        keyword = keyword.strip()
                        color = color.strip()
                        
                        # 驗證顏色格式（必須是 #RRGGBB 格式）
                        if re.match(r'^#[0-9A-Fa-f]{6}$', color):
                            self.custom_keywords[keyword] = color
                        else:
                            print(f"警告：無效的顏色代碼 '{color}' for keyword '{keyword}'")
                    except Exception as e:
                        print(f"警告：無法解析關鍵字設定 '{line}': {e}")
            
            print(f"已載入 {len(self.custom_keywords)} 個自訂關鍵字")
            
        except Exception as e:
            print(f"載入關鍵字檔案失敗：{e}")

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
        text = tk.Text(text_frame, wrap=tk.NONE, height=18, xscrollcommand=xbar.set, yscrollcommand=ybar.set)
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
            # 建立所有關鍵字的列表（自訂關鍵字 + 系統預設關鍵字）
            all_keywords = []
            
            # 1. 加入自訂關鍵字（優先處理，因為使用者定義的更精確）
            for keyword, color in self.custom_keywords.items():
                # 為每個自訂關鍵字建立 tag
                tag_name = f"custom_{keyword}"
                all_keywords.append((keyword, tag_name, color))
            
            # 2. 加入系統預設關鍵字
            default_keywords = {
                r'\b(ADB|adb)\b': ('ADB', self.colors.get('ADB', '#FF4500')),
                r'\b(USB|usb)\b': ('USB', self.colors.get('USB', '#4B0082')),
                r'\b(COM\d+)\b': ('PORT', self.colors.get('PORT', '#008080')),
                r'\b(DM\s+PORT|DM_PORT)\b': ('PORT', self.colors.get('PORT', '#008080')),
                r'\b(FOTA|fota)\b': ('FOTA', self.colors.get('FOTA', '#FF1493')),
                r'\b(device|Device|DEVICE)\b': ('DEVICE', self.colors.get('DEVICE', '#800080')),
                r'\b(success|Success|SUCCESS)\b': ('SUCCESS', self.colors.get('SUCCESS', '#008000')),
                r'\b(error|Error|ERROR)\b': ('ERROR', self.colors.get('ERROR', '#FF0000')),
                r'\b(warning|Warning|WARNING)\b': ('WARNING', self.colors.get('WARNING', '#FF8C00')),
                r'\b(failed|Failed|FAILED)\b': ('ERROR', self.colors.get('ERROR', '#FF0000')),
                r'\b(connected|Connected|CONNECTED)\b': ('SUCCESS', self.colors.get('SUCCESS', '#008000')),
                r'\b(disconnected|Disconnected|DISCONNECTED)\b': ('WARNING', self.colors.get('WARNING', '#FF8C00')),
                r'\b(reboot|Reboot|REBOOT)\b': ('WARNING', self.colors.get('WARNING', '#FF8C00')),
                r'\b(upgrade|Upgrade|UPGRADE)\b': ('FOTA', self.colors.get('FOTA', '#FF1493')),
                r'\b(firmware|Firmware|FIRMWARE)\b': ('FOTA', self.colors.get('FOTA', '#FF1493')),
            }
            
            # 按關鍵字長度排序，較長的優先處理（避免短關鍵字覆蓋長關鍵字）
            all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
            
            # 使用簡單的字串替換方式
            processed_text = message
            replacements = []  # 儲存 (start_pos, end_pos, tag_name, color)
            
            # 先處理自訂關鍵字
            for keyword, tag_name, color in all_keywords:
                # 找出所有匹配位置
                start = 0
                while True:
                    pos = processed_text.find(keyword, start)
                    if pos == -1:
                        break
                    replacements.append((pos, pos + len(keyword), tag_name, color))
                    start = pos + 1
            
            # 再處理系統預設關鍵字（regex）
            for pattern, (tag_name, color) in default_keywords.items():
                matches = list(re.finditer(pattern, processed_text, re.IGNORECASE))
                for match in matches:
                    start, end = match.span()
                    # 檢查是否與自訂關鍵字重疊，如果重疊則跳過
                    overlaps = False
                    for r_start, r_end, _, _ in replacements:
                        if not (end <= r_start or start >= r_end):  # 有重疊
                            overlaps = True
                            break
                    if not overlaps:
                        replacements.append((start, end, tag_name, color))
            
            # 按位置排序
            replacements.sort(key=lambda x: x[0])
            
            # 插入文字並套用顏色
            current_pos = 0
            for start, end, tag_name, color in replacements:
                # 插入關鍵字前的普通文字
                if start > current_pos:
                    text_widget.insert(tk.END, processed_text[current_pos:start])
                
                # 插入關鍵字（帶顏色）
                keyword_text = processed_text[start:end]
                text_widget.insert(tk.END, keyword_text, tag_name)
                text_widget.tag_config(tag_name, foreground=color)
                
                current_pos = end
            
            # 插入剩餘的普通文字
            if current_pos < len(processed_text):
                text_widget.insert(tk.END, processed_text[current_pos:])
                
        except Exception as e:
            # 如果彩色處理失敗，直接插入原始訊息
            print(f"顏色處理失敗：{e}")
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