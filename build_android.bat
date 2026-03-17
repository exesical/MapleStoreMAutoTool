@echo off
REM 冒险岛M自动助手 - Windows构建辅助脚本
REM 由于Android APK构建需要Linux环境，此脚本提供构建指导

echo ========================================
echo   冒险岛M自动助手 Android版本构建指导
echo ========================================
echo.

echo 当前环境: Windows
echo Android APK构建需要Linux环境 (Ubuntu/Debian推荐)
echo.

echo 构建选项:
echo.
echo 1. 使用WSL2 (Windows Subsystem for Linux)
echo    - 安装WSL2和Ubuntu
echo    - 在WSL2中运行构建脚本
echo.
echo 2. 使用Docker容器
echo    - 使用预配置的Android构建环境
echo.
echo 3. 使用云服务器
echo    - 租用Linux云服务器进行构建
echo.
echo 4. 使用GitHub Actions
echo    - 自动化在线构建APK
echo.

echo ========================================
echo          WSL2构建方案 (推荐)
echo ========================================
echo.
echo 步骤:
echo 1. 启用WSL2功能
echo 2. 安装Ubuntu发行版
echo 3. 在WSL2中安装Python和依赖
echo 4. 运行构建脚本
echo.

echo 详细命令:
echo # 在WSL2 Ubuntu中执行
echo sudo apt update
echo sudo apt install -y git python3-pip
echo pip3 install buildozer
echo cd /mnt/c/path/to/your/project
echo chmod +x build_android.sh
echo ./build_android.sh
echo.

echo ========================================
echo           Docker构建方案
echo ========================================
echo.
echo 使用预配置的Docker镜像:
echo docker run --rm -v ${PWD}:/home/user/hostcwd \
echo   kivy/buildozer android debug
echo.

echo ========================================
echo         GitHub Actions构建
echo ========================================
echo.
echo 1. 将代码推送到GitHub
echo 2. 创建 .github/workflows/build.yml
echo 3. 自动构建并下载APK
echo.

echo 构建完成后，APK文件将位于 bin/ 目录中
echo.

pause