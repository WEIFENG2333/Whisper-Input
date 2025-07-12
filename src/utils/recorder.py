import datetime
from pathlib import Path


FILE_NAME = "history.md"

class TranscriptionRecord:
    """转录记录数据类"""

    def __init__(self, text, is_translation=False, timestamp=None):
        self.text = text
        self.is_translation = is_translation
        self.timestamp = timestamp or datetime.datetime.now()

    def to_markdown(self):
        """转换为Markdown格式"""
        datetime_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        record_type = "翻译" if self.is_translation else "转录"
        return f"**{datetime_str}** [{record_type}] {self.text}\n"


class TranscriptionRecorder:
    """转录记录器"""

    def __init__(self, filename=FILE_NAME):
        self.file_path = Path(filename)
        self._init_file()

    def record(self, text, is_translation=False):
        """记录转录结果"""
        if not text or not text.strip():
            return

        record = TranscriptionRecord(text.strip(), is_translation)
        self._write_to_file(record)

    def _init_file(self):
        """初始化文件"""
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("# Whisper Input 转录历史\n\n")

    def _write_to_file(self, record):
        """写入文件"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(record.to_markdown())

    def get_file_path(self):
        """获取记录文件路径"""
        return self.file_path


# 全局实例
transcription_recorder = TranscriptionRecorder()
