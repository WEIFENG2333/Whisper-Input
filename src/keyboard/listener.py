from pynput.keyboard import Controller, Key, Listener
from ..utils.logger import logger
import time
from .inputState import InputState
import os
import platform
from ..utils.clipboard import copy_text, paste_text
from ..utils.notifications import voice_notifications
from ..utils.recorder import transcription_recorder


class KeyboardManager:
    def __init__(
        self,
        on_record_start,
        on_record_stop,
        on_translate_start,
        on_translate_stop,
        on_reset_state,
    ):
        self.keyboard = Controller()
        self.option_pressed = False
        self.shift_pressed = False
        self.option_press_time = None  # 记录 Option 按下的时间戳
        self.PRESS_DURATION_THRESHOLD = 0.01  # 按键持续时间阈值（秒）
        self.is_checking_duration = False  # 用于控制定时器线程
        self.has_triggered = False  # 用于防止重复触发
        self._original_clipboard = None  # 保存原始剪贴板内容

        # 回调函数能不能查一下今天的天气怎么样？
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_translate_start = on_translate_start
        self.on_translate_stop = on_translate_stop
        self.on_reset_state = on_reset_state

        # 状态管理
        self._state = InputState.IDLE

        # 自动检测系统平台..
        system = platform.system()
        if system == "Windows":
            self.system_platform = Key.ctrl
            logger.info("KeyboardManager 配置到Windows平台")
        else:
            self.system_platform = Key.cmd
            logger.info("KeyboardManager 配置到Mac平台")

        # 获取转录和翻译按钮
        transcriptions_button = os.getenv("TRANSCRIPTIONS_BUTTON")
        try:
            self.transcriptions_button = Key[transcriptions_button]
            logger.info(f"配置到转录按钮：{transcriptions_button}")
        except KeyError:
            logger.error(f"无效的转录按钮配置：{transcriptions_button}")

        translations_button = os.getenv("TRANSLATIONS_BUTTON")
        try:
            self.translations_button = Key[translations_button]
            logger.info(f"配置到翻译按钮(与转录按钮组合)：{translations_button}")
        except KeyError:
            logger.error(f"无效的翻译按钮配置：{translations_button}")

        logger.info(f"按住 {transcriptions_button} 键：实时语音转录（保持原文）")
        logger.info(
            f"按住 {translations_button} + {transcriptions_button} 键：实时语音翻译（翻译成英文）"
        )

    @property
    def state(self):
        """获取当前状态"""
        return self._state

    @state.setter
    def state(self, new_state):
        """设置新状态并发送通知"""
        if new_state != self._state:
            self._state = new_state

            # 根据状态转换发送通知
            if new_state == InputState.RECORDING:
                voice_notifications.notify_recording_started(False)
                self.on_record_start()
            elif new_state == InputState.RECORDING_TRANSLATE:
                voice_notifications.notify_recording_started(True)
                self.on_translate_start()
            elif new_state == InputState.PROCESSING:
                voice_notifications.notify_processing(False)
                self.on_record_stop()
            elif new_state == InputState.TRANSLATING:
                voice_notifications.notify_processing(True)
                self.on_translate_stop()
            elif new_state == InputState.IDLE:
                pass

    def show_warning(self, warning_message):
        """显示警告消息"""
        voice_notifications.notify_warning(warning_message)

    def show_error(self, error_message):
        """显示错误消息"""
        voice_notifications.notify_error(error_message)

    def _save_clipboard(self):
        """保存当前剪贴板内容"""
        if self._original_clipboard is None:
            self._original_clipboard = paste_text()

    def _restore_clipboard(self):
        """恢复原始剪贴板内容"""
        if self._original_clipboard is not None:
            copy_text(self._original_clipboard)
            self._original_clipboard = None

    def type_text(self, text, error_message=None):
        """将文字输入到当前光标位置

        Args:
            text: 要输入的文本或包含文本和错误信息的元组
            error_message: 错误信息
        """
        # 如果text是元组，说明是从process_audio返回的结果
        if isinstance(text, tuple):
            text, error_message = text

        if error_message:
            self.show_error(error_message)
            return

        if not text:
            # 如果没有文本且不是错误，可能是录音时长不足
            if self.state in (InputState.PROCESSING, InputState.TRANSLATING):
                self.show_warning("录音时长过短，请至少录制1秒")
            return

        try:
            logger.info("正在输入转录文本...")

            # 直接输入文本，不再使用临时文本
            copy_text(text)
            paste_text()

            # 将转录结果复制到剪贴板
            if os.getenv("KEEP_ORIGINAL_CLIPBOARD", "true").lower() != "true":
                copy_text(text)
            else:
                # 恢复原始剪贴板内容
                self._restore_clipboard()

            # 发送完成通知
            is_translation = self.state == InputState.TRANSLATING
            voice_notifications.notify_completed(text, is_translation)

            # 记录转录结果
            transcription_recorder.record(text, is_translation)

            logger.info("文本输入完成")
            self.state = InputState.IDLE
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
            self.show_error(f"文本输入失败: {e}")

    def start_duration_check(self):
        """开始检查按键持续时间"""
        if self.is_checking_duration:
            return

        def check_duration():
            while self.is_checking_duration and self.option_pressed:
                current_time = time.time()
                if (
                    not self.has_triggered
                    and self.option_press_time
                    and (current_time - self.option_press_time)
                    >= self.PRESS_DURATION_THRESHOLD
                ):

                    # 达到阈值时触发相应功能
                    if (
                        self.option_pressed
                        and self.shift_pressed
                        and self.state.can_start_recording
                    ):
                        self.state = InputState.RECORDING_TRANSLATE
                        # self.on_translate_start()
                        self.has_triggered = True
                    elif (
                        self.option_pressed
                        and not self.shift_pressed
                        and self.state.can_start_recording
                    ):
                        self.state = InputState.RECORDING
                        # self.on_record_start()
                        self.has_triggered = True

                time.sleep(0.01)  # 短暂休眠以降低 CPU 使用率

        self.is_checking_duration = True
        import threading

        threading.Thread(target=check_duration, daemon=True).start()

    def on_press(self, key):
        """按键按下时的回调"""
        try:
            if key == self.transcriptions_button:  # Key.f8:  # Option 键按下
                # 在开始任何操作前保存剪贴板内容
                if self._original_clipboard is None:
                    self._original_clipboard = paste_text()

                self.option_pressed = True
                self.option_press_time = time.time()
                self.start_duration_check()
            elif key == self.translations_button:
                self.shift_pressed = True
        except AttributeError:
            pass

    def on_release(self, key):
        """按键释放时的回调"""
        try:
            if key == self.transcriptions_button:  # Key.f8:  # Option 键释放
                self.shift_pressed = False
                self.option_pressed = False
                self.option_press_time = None
                self.is_checking_duration = False

                if self.has_triggered:
                    if self.state == InputState.RECORDING_TRANSLATE:
                        self.state = InputState.TRANSLATING
                    elif self.state == InputState.RECORDING:
                        self.state = InputState.PROCESSING
                    self.has_triggered = False
            elif key == self.translations_button:  # Key.f7:
                self.shift_pressed = False
                if (
                    self.state == InputState.RECORDING_TRANSLATE
                    and not self.option_pressed
                    and self.has_triggered
                ):
                    self.state = InputState.TRANSLATING
                    self.has_triggered = False
        except AttributeError:
            pass

    def start_listening(self):
        """开始监听键盘事件"""
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def reset_state(self):
        """重置所有状态"""
        # 恢复剪贴板
        self._restore_clipboard()

        # 重置状态标志
        self.option_pressed = False
        self.shift_pressed = False
        self.option_press_time = None
        self.is_checking_duration = False
        self.has_triggered = False

        # 设置为空闲状态
        self.state = InputState.IDLE


def check_accessibility_permissions():
    """检查是否有辅助功能权限并提供指导"""
    logger.warning("\n=== macOS 辅助功能权限检查 ===")
    logger.warning("此应用需要辅助功能权限才能监听键盘事件。")
    logger.warning("\n请按照以下步骤授予权限：")
    logger.warning("1. 打开 系统偏好设置")
    logger.warning("2. 点击 隐私与安全性")
    logger.warning("3. 点击左侧的 辅助功能")
    logger.warning("4. 点击右下角的锁图标并输入密码")
    logger.warning("5. 在右侧列表中找到 Terminal（或者您使用的终端应用）并勾选")
    logger.warning("\n授权后，请重新运行此程序。")
    logger.warning("===============================\n")
