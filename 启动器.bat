@echo off
chcp 65001 >nul
echo.
echo ========================================
echo     冒险岛M自动助手启动器
echo ========================================
echo.
echo 正在启动选择界面...
echo.

python Launcher.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查：
    echo 1. 是否安装了Python
    echo 2. 是否安装了tkinter库
    echo 3. 检查错误信息
    echo.
    pause
)