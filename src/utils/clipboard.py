import subprocess
import platform
from ..utils.logger import logger


class ClipboardManager:
    """跨平台剪贴板管理器"""

    def __init__(self):
        system = platform.system()
        self.is_mac = system == "Darwin"
        self.is_windows = system == "Windows"
        self.is_linux = system == "Linux"

        platform_name = (
            "macOS" if self.is_mac else "Windows" if self.is_windows else "Linux"
        )
        logger.info(f"ClipboardManager 初始化: {platform_name}")

    def copy(self, text):
        """复制文本到剪贴板

        Args:
            text (str): 要复制的文本

        Returns:
            bool: 操作是否成功
        """
        if self.is_mac:
            return self._copy_macos(text)
        else:
            return self._copy_pyperclip(text)

    def paste(self):
        """从剪贴板粘贴文本

        Returns:
            str: 剪贴板中的文本内容，失败时返回空字符串
        """
        if self.is_mac:
            return self._paste_macos()
        else:
            return self._paste_pyperclip()

    def _copy_macos(self, text):
        try:
            cmd = ["osascript", "-e", f'set the clipboard to "{text}"']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _paste_macos(self):
        try:
            cmd = ["osascript", "-e", "get the clipboard"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    def _copy_pyperclip(self, text):
        try:
            import pyperclip

            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def _paste_pyperclip(self):
        try:
            import pyperclip

            return pyperclip.paste()
        except Exception:
            return ""


# 全局实例
clipboard_manager = ClipboardManager()


def copy_text(text):
    return clipboard_manager.copy(text)


def paste_text():
    return clipboard_manager.paste()


class ClipboardContext:
    """剪贴板上下文管理器，确保不污染用户原始剪贴板内容"""

    def __init__(self):
        self.original_content = None

    def __enter__(self):
        self.original_content = paste_text()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_content is not None:
            copy_text(self.original_content)
        return False

    def copy_and_paste(self, text):
        """复制文本并粘贴，不污染原始剪贴板"""
        copy_text(text)
        return text
