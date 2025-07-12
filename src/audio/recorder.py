import io
import queue
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

from ..utils.logger import logger


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        # self.temp_dir = tempfile.mkdtemp()
        self.current_device = None
        self.record_start_time = None
        self.min_record_duration = 1.0  # 最小录音时长（秒）
        self._check_audio_devices()
        # logger.info(f"初始化完成，临时文件目录: {self.temp_dir}")
        logger.info(f"初始化完成")

    def _list_audio_devices(self):
        """列出所有可用的音频输入设备"""
        devices = sd.query_devices()
        logger.info("\n=== 可用的音频输入设备 ===")
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:  # 只显示输入设备
                status = "默认设备 ✓" if device["name"] == self.current_device else ""
                logger.info(
                    f"{i}: {device['name']} "
                    f"(采样率: {int(device['default_samplerate'])}Hz, "
                    f"通道数: {device['max_input_channels']}) {status}"
                )
        logger.info("========================\n")

    def _check_audio_devices(self):
        """检查音频设备状态"""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind="input")
            self.current_device = default_input["name"]

            logger.info("\n=== 当前音频设备信息 ===")
            logger.info(f"默认输入设备: {self.current_device}")
            logger.info(f"支持的采样率: {int(default_input['default_samplerate'])}Hz")
            logger.info(f"最大输入通道数: {default_input['max_input_channels']}")
            logger.info("========================\n")

            # 如果默认采样率与我们的不同，使用设备的默认采样率
            if abs(default_input["default_samplerate"] - self.sample_rate) > 100:
                self.sample_rate = int(default_input["default_samplerate"])
                logger.info(f"调整采样率为: {self.sample_rate}Hz")

            # 列出所有可用设备
            self._list_audio_devices()

        except Exception as e:
            logger.error(f"检查音频设备时出错: {e}")
            raise RuntimeError("无法访问音频设备，请检查系统权限设置")

    def _check_device_changed(self):
        """检查默认音频设备是否发生变化"""
        try:
            default_input = sd.query_devices(kind="input")
            if default_input["name"] != self.current_device:
                logger.warning(f"\n音频设备已切换:")
                logger.warning(f"从: {self.current_device}")
                logger.warning(f"到: {default_input['name']}\n")
                self.current_device = default_input["name"]
                self._check_audio_devices()
                return True
            return False
        except Exception as e:
            logger.error(f"检查设备变化时出错: {e}")
            return False

    def start_recording(self):
        """开始录音"""
        if not self.recording:
            try:
                # 检查设备是否发生变化
                self._check_device_changed()

                logger.info("开始录音...")
                self.recording = True
                self.record_start_time = time.time()
                self.audio_data = []

                def audio_callback(indata, frames, time, status):
                    if status:
                        logger.warning(f"音频录制状态: {status}")
                    if self.recording:
                        self.audio_queue.put(indata.copy())

                self.stream = sd.InputStream(
                    channels=1,
                    samplerate=self.sample_rate,
                    callback=audio_callback,
                    device=None,  # 使用默认设备
                    latency="low",  # 使用低延迟模式
                )
                self.stream.start()
                logger.info(f"音频流已启动 (设备: {self.current_device})")
            except Exception as e:
                self.recording = False
                logger.error(f"启动录音失败: {e}")
                raise

    def stop_recording(self):
        """停止录音并返回音频数据"""
        if not self.recording:
            return None

        logger.info("停止录音...")
        self.recording = False
        self.stream.stop()
        self.stream.close()

        # 检查录音时长
        if self.record_start_time:
            record_duration = time.time() - self.record_start_time
            if record_duration < self.min_record_duration:
                logger.warning(
                    f"录音时长太短 ({record_duration:.1f}秒 < {self.min_record_duration}秒)"
                )
                return "TOO_SHORT"

        # 收集所有音频数据
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())

        if not audio_data:
            logger.warning("没有收集到音频数据")
            return None

        # 合并音频数据
        audio = np.concatenate(audio_data)
        logger.info(f"音频数据长度: {len(audio)} 采样点")

        # 将 numpy 数组转换为字节流
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio, self.sample_rate, format="WAV")
        audio_buffer.seek(0)  # 将缓冲区指针移动到开始位置

        return audio_buffer
