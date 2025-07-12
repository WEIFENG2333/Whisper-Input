#!/bin/bash

# Whisper Input 一键启动脚本
# 使用方式：双击运行或在终端执行 ./start_whisper.sh

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎤 启动 Whisper Input..."
echo "📁 项目目录: $SCRIPT_DIR"

# 检查 Python3 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    echo "请安装 Python3 后重试"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.deps_installed" ]; then
    echo "📦 安装依赖包..."
    python -m pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/.deps_installed
    echo "✅ 依赖安装完成"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请复制 .env.example 到 .env 并配置 API 密钥"
    echo "cp .env.example .env"
    echo "然后编辑 .env 文件添加您的 API 密钥"
    exit 1
fi

# 启动应用
echo "🚀 启动 Whisper Input..."
echo "按 Ctrl+C 停止应用"
echo "================================"

python main.py