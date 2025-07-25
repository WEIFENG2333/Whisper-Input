import subprocess
import platform


class ClipboardManager:
    """跨平台剪贴板管理器"""

    def __init__(self):
        system = platform.system()
        self.is_mac = system == "Darwin"
        self.is_windows = system == "Windows"
        self.is_linux = system == "Linux"

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
            cmd = [
                "osascript",
                "-e",
                'tell application "System Events" to keystroke "v" using command down',
            ]
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


if __name__ == "__main__":
    clipboard_manager = ClipboardManager()
    clipboard_manager.copy("Hello, World!")
    print(clipboard_manager.paste())
