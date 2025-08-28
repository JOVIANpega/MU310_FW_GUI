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
        self.text_widgets = {}  # �אּ�r��Akey �����ҭ��W��
        self.debug_enabled = False
        self._init_logfile()
        self.i18n = i18n or I18N("EN")
        # ���� _build_logs_tab ���I�s�A�]���ڭ̤��ݭn��
        self._setup_colors()

    def _setup_colors(self):
        """�]�w��r�C�����"""
        self.colors = {
            "SUCCESS": "#008000",      # ��� - ���\�T��
            "ERROR": "#FF0000",        # ���� - ���~�T��
            "WARNING": "#FF8C00",      # ��� - ĵ�i�T��
            "INFO": "#0000FF",         # �Ŧ� - �@���T
            "DEBUG": "#808080",        # �Ǧ� - �����T��
            "DEVICE": "#800080",       # ���� - �˸m����
            "PORT": "#008080",         # �C�� - ��f����
            "ADB": "#FF4500",          # ����� - ADB ����
            "USB": "#4B0082",          # �Q�� - USB ����
            "FOTA": "#FF1493",         # �`������ - FOTA ����
        }

    def _init_logfile(self):
        os.makedirs("logs", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join("logs", f"session_{timestamp}.log")
        self._fp = open(self.log_path, "a", encoding="utf-8", buffering=1)

    def attach_log_panel(self, parent, tab_name: str = "default"):
        """�إ߿W�ߪ���x���O�A�C�Ӽ��ҭ������ۤv����x�ϰ�"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ��x��r�ϰ�]²�ƪ��A�u�O�d��r�ϰ�^
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        ybar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        xbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        text = tk.Text(text_frame, wrap=tk.NONE, height=14, xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        ybar.config(command=text.yview)
        xbar.config(command=text.yview)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        xbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # �N��r�ϰ�[�J����������ҭ�
        self.text_widgets[tab_name] = text
        return text

    def clear_logs(self, tab_name: str = "all"):
        """�M�ū��w���ҭ�����x"""
        if tab_name == "all":
            # �M�ũҦ����ҭ�����x
            for text_widget in self.text_widgets.values():
                try:
                    text_widget.delete("1.0", tk.END)
                except Exception:
                    pass
        else:
            # �M�ū��w���ҭ�����x
            if tab_name in self.text_widgets:
                try:
                    self.text_widgets[tab_name].delete("1.0", tk.END)
                except Exception:
                    pass

    def _timestamp(self):
        return time.strftime("%H:%M:%S")

    def _apply_colors(self, text_widget, message, level):
        """�M�αm���r�� Text widget"""
        try:
            # ���J�ɶ��W�O
            timestamp = f"[{self._timestamp()}] "
            text_widget.insert(tk.END, timestamp)
            
            # ���J���ż��ҡ]�a�C��^
            level_text = f"{level}: "
            text_widget.insert(tk.END, level_text, level)
            
            # ���J�T�����e�]�a����r�C��^
            self._insert_colored_message(text_widget, message)
            
            # ���J����
            text_widget.insert(tk.END, "\n")
            
            # �]�w���ż��Ҫ��C��
            text_widget.tag_config(level, foreground=self.colors.get(level, "black"))
            
            # �u�ʨ쩳��
            text_widget.see(tk.END)
            
        except tk.TclError:
            pass

    def _insert_colored_message(self, text_widget, message):
        """���J�a�C�⪺�T���A����r�|�Τ��P�C��Х�"""
        try:
            # �w�q����r�M�����C��
            keywords = {
                r"\b(ADB|adb)\b": "ADB",
                r"\b(USB|usb)\b": "USB",
                r"\b(COM\d+)\b": "PORT",
                r"\b(DM\s+PORT|DM_PORT)\b": "PORT",
                r"\b(FOTA|fota)\b": "FOTA",
                r"\b(device|Device|DEVICE)\b": "DEVICE",
                r"\b(success|Success|SUCCESS)\b": "SUCCESS",
                r"\b(error|Error|ERROR)\b": "ERROR",
                r"\b(warning|Warning|WARNING)\b": "WARNING",
                r"\b(failed|Failed|FAILED)\b": "ERROR",
                r"\b(connected|Connected|CONNECTED)\b": "SUCCESS",
                r"\b(disconnected|Disconnected|DISCONNECTED)\b": "WARNING",
                r"\b(reboot|Reboot|REBOOT)\b": "WARNING",
                r"\b(upgrade|Upgrade|UPGRADE)\b": "FOTA",
                r"\b(firmware|Firmware|FIRMWARE)\b": "FOTA",
            }
            
            # ���ΰT��������r�M�@���r
            remaining_text = message
            current_pos = 0
            
            for pattern, color_tag in keywords.items():
                matches = list(re.finditer(pattern, remaining_text, re.IGNORECASE))
                for match in reversed(matches):
                    start, end = match.span()
                    # ���J����r�e����r
                    if start > current_pos:
                        text_widget.insert(tk.END, remaining_text[current_pos:start])
                    # ���J����r�]�a�C��^
                    text_widget.insert(tk.END, match.group(), color_tag)
                    current_pos = end
            
            # ���J�Ѿl����r
            if current_pos < len(remaining_text):
                text_widget.insert(tk.END, remaining_text[current_pos:])
                
        except Exception:
            # �p�G�m��B�z���ѡA�������J��l�T��
            text_widget.insert(tk.END, message)

    def log(self, message: str, level: str = "INFO", tab_name: str = "all"):
        """�O���@���x�T��"""
        # �g�J�ɮ�
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        try:
            self._fp.write(log_entry)
            self._fp.flush()
        except Exception:
            pass
        
        # ��ܨ� GUI�]�m��榡�^
        if tab_name == "all":
            # ��ܨ�Ҧ����ҭ�
            for text_widget in self.text_widgets.values():
                try:
                    self._apply_colors(text_widget, message, level)
                except Exception:
                    pass
        else:
            # ��ܨ���w���ҭ�
            if tab_name in self.text_widgets:
                try:
                    self._apply_colors(self.text_widgets[tab_name], message, level)
                except Exception:
                    pass

    def debug(self, message, tab_name: str = "all"):
        """�����T���A�u�b DEBUG �Ҧ��}�Ү����"""
        if self.debug_enabled:
            self.log(message, "DEBUG", tab_name)

    def error(self, message, tab_name: str = "all"):
        """���~�T��"""
        self.log(message, "ERROR", tab_name)

    def warning(self, message, tab_name: str = "all"):
        """ĵ�i�T��"""
        self.log(message, "WARNING", tab_name)

    def success(self, message, tab_name: str = "all"):
        """���\�T��"""
        self.log(message, "SUCCESS", tab_name)

    def close(self):
        """������x�ɮ�"""
        try:
            if hasattr(self, "_fp") and self._fp:
                self._fp.close()
        except Exception:
            pass
