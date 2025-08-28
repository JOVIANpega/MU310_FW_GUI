"""
utils_paths.py - Resource path utilities.
Purpose: Provide get_resource_path() for accessing files both in development and PyInstaller bundles.
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) 