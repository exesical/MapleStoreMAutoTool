@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   冒险岛M自动助手 - 任务配置UI版本
echo ========================================
echo.
echo 正在启动任务配置界面...
echo.

python TaskConfigUI.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查：
    echo 1. 是否安装了Python
    echo 2. 是否安装了tkinter库
    echo 3. 检查错误信息
    echo.
    pause
)