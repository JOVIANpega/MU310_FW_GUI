"""
subprocess_runner.py - Stream external commands to GUI logs.
Purpose: Provide utilities to run commands/BAT files in background threads and stream their output to GuiLogger safely. Supports debug mode and tab-specific logging.
"""

import os
import subprocess
import threading
from typing import List, Optional, Callable, Union

from logger_util import GuiLogger


def _reader_thread(proc: subprocess.Popen, logger: GuiLogger, prefix: str = "", tab_name: str = "all"):
    def _emit(line: str, level: str = "INFO"):
        text = f"{prefix}{line.rstrip()}"
        if level == "ERROR":
            logger.error(text, tab_name=tab_name)
        elif level == "DEBUG":
            logger.debug(text, tab_name=tab_name)
        else:
            logger.log(text, tab_name=tab_name)

    # Read stdout
    if proc.stdout is not None:
        for raw in iter(proc.stdout.readline, b""):
            if not raw:
                break
            try:
                decoded_line = raw.decode(errors="ignore")
                # 在 DEBUG 模式下，顯示更多詳細資訊
                if logger.debug_enabled:
                    logger.debug(f"STDOUT: {decoded_line}", tab_name=tab_name)
                _emit(decoded_line)
            except Exception:
                _emit(str(raw), level="ERROR")
    # Drain stderr
    if proc.stderr is not None:
        for raw in iter(proc.stderr.readline, b""):
            if not raw:
                break
            try:
                decoded_line = raw.decode(errors="ignore")
                # 在 DEBUG 模式下，顯示更多詳細資訊
                if logger.debug_enabled:
                    logger.debug(f"STDERR: {decoded_line}", tab_name=tab_name)
                _emit(decoded_line, level="ERROR")
            except Exception:
                _emit(str(raw), level="ERROR")


def run_command(
    command: Union[str, List[str]],
    logger: GuiLogger,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    shell: bool = False,
    on_complete: Optional[Callable[[int], None]] = None,
    tab_name: str = "all",
):
    try:
        if logger.debug_enabled:
            logger.debug(f"[DEBUG] 執行命令: {command}", tab_name=tab_name)
            if cwd:
                logger.debug(f"[DEBUG] 工作目錄: {cwd}", tab_name=tab_name)
            if env:
                logger.debug(f"[DEBUG] 環境變數: {env}", tab_name=tab_name)
        
        logger.log(f"[RUN] {command}", tab_name=tab_name)
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        logger.error(f"啟動命令失敗: {e}", tab_name=tab_name)
        if on_complete:
            on_complete(-1)
        return

    t = threading.Thread(target=_reader_thread, args=(proc, logger, "", tab_name), daemon=True)
    t.start()

    def _waiter():
        code = proc.wait()
        if logger.debug_enabled:
            logger.debug(f"[DEBUG] 程序結束，返回碼: {code}", tab_name=tab_name)
        logger.log(f"[EXIT] code={code}", tab_name=tab_name)
        if on_complete:
            on_complete(code)

    threading.Thread(target=_waiter, daemon=True).start()


def run_bat_file(bat_filename: str, logger: GuiLogger, cwd: Optional[str] = None, tab_name: str = "all"):
    # Ensure correct invocation with cmd /c and codepage
    if logger.debug_enabled:
        logger.debug(f"[DEBUG] 執行批次檔: {bat_filename}", tab_name=tab_name)
        if cwd:
            logger.debug(f"[DEBUG] 工作目錄: {cwd}", tab_name=tab_name)
    
    # 更新狀態標籤，顯示當前執行的 BAT 檔案
    # logger.update_current_bat(bat_filename, tab_name)  # 已移除
    # logger.update_status("執行中", tab_name)
    # logger.update_progress(25, tab_name)
    
    cmd = f'cmd /c chcp 65001 > nul & call "{bat_filename}"'
    run_command(cmd, logger=logger, cwd=cwd, shell=True, tab_name=tab_name) 