# 🎮 冒险岛M自动助手 - Android版本转换完成

## 📋 项目概述

我已成功将您的Windows版冒险岛M自动化脚本转换为Android APK版本，主要技术栈为：
- **UI框架**: Kivy (Python GUI框架)
- **图像处理**: OpenCV
- **Android交互**: PyJNIus + Android Shell Commands
- **构建工具**: Buildozer + Python-for-Android

## 📁 项目结构

```
MapleStoreMAutoTool/
├── 📱 Android核心文件
│   ├── main.py                    # Kivy主应用界面
│   ├── android_state.py           # Android状态管理类
│   ├── buildozer.spec             # Android构建配置
│   └── requirements.txt           # Python依赖包
│
├── 🔧 构建脚本
│   ├── build_android.sh           # Linux构建脚本
│   ├── build_android.bat          # Windows构建指导
│   └── .github/workflows/build.yml # GitHub自动构建
│
├── 📋 模板文件
│   └── templates/
│       ├── AndroidManifest.tmpl.xml
│       └── accessibility_service_config.xml
│
├── 📚 文档
│   ├── README_ANDROID.md          # Android版使用说明
│   └── DEPLOYMENT.md              # 本文件
│
└── 📂 原项目文件
    ├── Data/                      # 游戏配置和模板图片
    ├── MSmState.py               # 原Windows状态类
    ├── DoScreenHit.py            # 原Windows屏幕交互
    └── MSmAuto.py                # 原Windows主程序
```

## 🚀 构建和部署选项

### 方案1: GitHub Actions自动构建 (推荐)
1. 将代码推送到GitHub仓库
2. GitHub Actions会自动构建APK
3. 从Actions页面下载构建好的APK

### 方案2: WSL2本地构建
```bash
# 在Windows上启用WSL2
# 安装Ubuntu发行版
# 在WSL2中执行:
sudo apt update && sudo apt install -y python3-pip git
pip3 install buildozer
cd /mnt/c/path/to/project
chmod +x build_android.sh
./build_android.sh
```

### 方案3: Docker构建
```bash
docker run --rm -v ${PWD}:/home/user/hostcwd kivy/buildozer android debug
```

### 方案4: Linux服务器构建
在任何Linux服务器上直接运行 `build_android.sh`

## 📱 Android功能特性

### ✅ 已实现功能
- 🎨 现代化Kivy图形界面
- 🤖 多种自动化任务类型
- 👥 多角色支持
- 📊 实时进度显示和日志
- 🔐 权限管理系统
- 📱 Android原生集成

### 🎯 核心任务类型
1. **日常副本** - 自动完成日常任务
2. **材料副本** - 刷取制作材料
3. **精英副本** - 挑战高级副本
4. **怪物公园** - 自动化经验获取
5. **快速副本** - 高效率刷副本
6. **完整流程** - 一键执行所有任务

### 🔧 技术亮点
- **跨平台兼容**: 同一套Python代码运行在Android上
- **图像识别**: 保留原有的OpenCV图像匹配逻辑
- **触摸模拟**: 使用Android Shell命令模拟点击
- **权限管理**: 完整的Android权限申请流程

## ⚠️ 重要说明

### 🔒 权限要求
- **无障碍服务**: 用于模拟触摸和滑动
- **悬浮窗权限**: 用于覆盖显示
- **存储权限**: 用于保存配置和截图

### 📋 使用步骤
1. 安装APK文件
2. 启动应用，点击"申请权限"
3. 在系统设置中开启无障碍服务
4. 选择任务类型和角色数量
5. 开始自动化

### ⚡ 性能优化
- 异步任务处理避免UI冻结
- 图像缓存减少重复计算
- 智能等待机制提高稳定性

## 🛠️ 开发和自定义

### 修改任务逻辑
编辑 `android_state.py` 中的对应方法：
```python
def run_daily_tasks(self):
    # 在这里添加您的日常任务逻辑
    pass
```

### 更新UI界面
修改 `main.py` 中的Kivy布局：
```python
def build(self):
    # 自定义UI布局
    pass
```

### 添加新的图像模板
1. 将新的PNG模板文件放入 `Data/` 相应目录
2. 更新配置JSON文件
3. 重新构建APK

## 📊 与原版对比

| 功能 | Windows版 | Android版 |
|------|-----------|-----------|
| 图形界面 | ❌ 命令行 | ✅ 现代化GUI |
| 屏幕操作 | Win32 API | Android Shell |
| 图像识别 | ✅ OpenCV | ✅ OpenCV |
| 多角色 | ✅ 支持 | ✅ 支持 |
| 便携性 | ❌ 需要电脑 | ✅ 手机即可 |
| 权限管理 | ❌ 无需特殊权限 | ⚠️ 需要无障碍权限 |

## 🔮 未来改进方向

### 短期目标
- [ ] 添加更多游戏模式支持
- [ ] 优化图像识别精度
- [ ] 增加任务调度功能
- [ ] 完善错误处理机制

### 长期规划
- [ ] 云端配置同步
- [ ] 多游戏支持
- [ ] AI智能识别
- [ ] 社区共享功能

## 🆘 技术支持

### 常见问题
1. **构建失败**: 检查Java环境和依赖安装
2. **权限被拒**: 手动在系统设置中开启
3. **识别不准**: 更新模板图片或调整阈值
4. **应用崩溃**: 查看日志输出定位问题

### 调试方法
- 使用 `adb logcat` 查看Android日志
- 在代码中添加更多Logger输出
- 使用模拟器进行测试调试

## 📄 许可证和免责声明

本项目基于原项目许可证条款，仅供学习和研究使用。使用自动化工具可能违反游戏服务条款，请谨慎使用并自行承担风险。

---

**项目转换完成时间**: 2026年3月17日  
**技术支持**: 通过GitHub Issues提交问题  
**版本**: v1.0.0 Android Beta