#!/bin/bash

# MapleStoreM Auto Tool - Android Build Script
# This script builds the Android APK using Buildozer

echo "=== 冒险岛M自动助手 Android构建脚本 ==="
echo ""

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Buildozer未安装，正在安装..."
    pip install buildozer
fi

# Check if we're on Linux (required for Android builds)
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "警告: Android构建需要在Linux环境下进行"
    echo "请使用Ubuntu或其他Linux发行版，或者使用Docker容器"
    exit 1
fi

# Install system dependencies for Ubuntu/Debian
echo "安装系统依赖..."
sudo apt update
sudo apt install -y \
    git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev \
    libssl-dev build-essential ccache

# Install Python dependencies
echo "安装Python依赖..."
pip3 install --user buildozer cython

# Clean previous builds
echo "清理之前的构建..."
rm -rf .buildozer bin

# Initialize buildozer (download Android SDK/NDK if needed)
echo "初始化Buildozer..."
buildozer init

# Build the APK
echo "开始构建APK..."
buildozer android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=== 构建成功! ==="
    echo "APK文件位置: ./bin/"
    ls -la ./bin/*.apk
    echo ""
    echo "安装说明:"
    echo "1. 将APK文件复制到Android设备"
    echo "2. 在设备上启用'未知来源'应用安装"
    echo "3. 安装APK"
    echo "4. 启动应用后，点击'申请权限'按钮"
    echo "5. 在无障碍设置中启用本应用"
    echo "6. 选择任务类型并开始自动化"
    echo ""
else
    echo ""
    echo "=== 构建失败 ==="
    echo "请检查错误信息并重试"
    echo ""
fi