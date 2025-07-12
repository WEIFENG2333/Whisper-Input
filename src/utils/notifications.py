import subprocess
import platform
import threading


class NotificationManager:
    """精简的macOS通知管理器"""

    def __init__(self):
        self.is_mac = platform.system() == "Darwin"

    def show_notification(self, title, message):
        """显示通知（异步）"""
        if not self.is_mac:
            return

        def _show():
            try:
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(
                    ["osascript", "-e", script], capture_output=True, timeout=3
                )
            except Exception:
                pass

        # 异步执行，不阻塞主线程
        threading.Thread(target=_show, daemon=True).start()

    def play_sound(self, sound_name="Glass"):
        """播放系统声音（异步）"""
        if not self.is_mac:
            return

        def _play():
            try:
                script = (
                    f'do shell script "afplay /System/Library/Sounds/{sound_name}.aiff"'
                )
                subprocess.run(
                    ["osascript", "-e", script], capture_output=True, timeout=3
                )
            except Exception:
                pass

        # 异步执行，不阻塞主线程
        threading.Thread(target=_play, daemon=True).start()


class VoiceAssistantNotifications:
    """语音助手通知"""

    def __init__(self):
        self.notification_manager = NotificationManager()

    def notify_recording_started(self, is_translation=False):
        """录音开始"""
        if is_translation:
            self.notification_manager.show_notification(
                "Whisper Input", "🎤 录音中（翻译）"
            )
        else:
            self.notification_manager.show_notification("Whisper Input", "🎤 录音中")
        self.notification_manager.play_sound("Pop")

    def notify_processing(self, is_translation=False):
        """处理中"""
        if is_translation:
            self.notification_manager.show_notification("Whisper Input", "🔄 翻译中...")
        else:
            self.notification_manager.show_notification("Whisper Input", "🔄 转录中...")

    def notify_completed(self, text, is_translation=False):
        """完成"""
        action = "翻译" if is_translation else "转录"
        display_text = text[:20] + "..." if len(text) > 20 else text
        self.notification_manager.show_notification(
            "Whisper Input", f"✅ {action}: {display_text}"
        )
        self.notification_manager.play_sound("Glass")

    def notify_error(self, error_message):
        """错误"""
        self.notification_manager.show_notification(
            "Whisper Input", f"❌ {error_message}"
        )
        self.notification_manager.play_sound("Basso")

    def notify_warning(self, warning_message):
        """警告"""
        self.notification_manager.show_notification(
            "Whisper Input", f"⚠️ {warning_message}"
        )


# 全局实例
voice_notifications = VoiceAssistantNotifications()
