@echo off
echo 正在打包 Launcher.py 为独立exe文件（包含所有Python文件）...
echo.

REM 检查是否安装了PyInstaller
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 未找到PyInstaller，正在安装...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo 安装PyInstaller失败！请检查Python环境。
        pause
        exit /b 1
    )
)

REM 清理之前的构建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo 开始打包...
pyinstaller --clean Launcher.spec

if exist "dist\Launcher.exe" (
    echo.
    echo ================================================
    echo 打包成功！
    echo exe文件位置: dist\Launcher.exe
    echo.
    echo 功能说明：
    echo • 包含所有Python文件（TaskConfigUI.py, MSmAuto.py等）
    echo • 包含所有数据文件（Data文件夹, templates文件夹等）
    echo • 可在任何Windows电脑上运行，无需Python环境
    echo • 真正的独立exe，不依赖外部文件
    echo.
    echo 使用方法：
    echo 1. 将整个dist目录复制到目标电脑
    echo 2. 双击Launcher.exe启动
    echo 3. 点击"配置任务"或"直接启动"
    echo ================================================
) else (
    echo.
    echo 打包失败！请检查错误信息。
)

pause
