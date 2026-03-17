# 冒险岛M自动助手 - Android版本

这是原本基于Windows的冒险岛M自动化脚本的Android移植版本，使用Python + Kivy开发。

## 功能特性

- ✅ 日常副本自动化
- ✅ 材料副本刷取
- ✅ 精英副本挑战
- ✅ 怪物公园自动化
- ✅ 快速副本功能
- ✅ 完整流程自动化
- ✅ 多角色支持
- ✅ 图形化界面操作

## 系统要求

- Android 5.0+ (API 21)
- 无障碍服务权限
- 存储权限
- 悬浮窗权限

## 安装说明

### 方法一：使用预编译APK（推荐）
1. 下载 `bin/` 目录中的APK文件
2. 在Android设备上启用"未知来源"应用安装
3. 安装APK文件

### 方法二：自行编译
需要在Linux环境下进行：

```bash
# 克隆项目
git clone <project_url>
cd MapleStoreMAutoTool

# 运行构建脚本
chmod +x build_android.sh
./build_android.sh
```

## 使用说明

### 1. 首次设置
1. 安装并启动应用
2. 点击"申请权限"按钮
3. 在系统设置中开启以下权限：
   - 无障碍服务权限
   - 悬浮窗权限
   - 存储权限

### 2. 权限说明
- **无障碍服务**: 用于模拟点击和滑动操作
- **悬浮窗权限**: 用于在其他应用上方显示操作界面
- **存储权限**: 用于保存截图和配置文件

### 3. 操作流程
1. 打开冒险岛M游戏
2. 切换到自动助手应用
3. 设置角色数量
4. 选择要执行的任务类型：
   - 日常副本
   - 材料副本
   - 精英副本
   - 怪物公园
   - 快速副本
   - 完整流程
5. 点击"开始自动化"

### 4. 任务类型说明

**日常副本**
- 自动完成日常任务
- 收集日常奖励

**材料副本**
- 自动刷取材料副本
- 收集制作材料

**精英副本**
- 挑战精英副本
- 获取高级装备

**怪物公园**
- 自动完成怪物公园
- 获取经验值奖励

**快速副本**
- 快速副本功能
- 高效率刷副本

**完整流程**
- 按顺序执行所有任务
- 一键完成所有日常

## 注意事项

### ⚠️ 重要提醒
1. 本工具仅供学习研究使用
2. 使用自动化工具可能违反游戏条款
3. 使用风险需自行承担
4. 建议不要长时间连续使用

### 🔒 安全建议
- 合理设置使用时间
- 避免异常操作模式
- 定期手动操作
- 注意游戏更新可能导致功能失效

### 🐛 故障排除

**应用无法启动**
- 检查Android版本是否兼容
- 确认已授予必要权限

**自动化不工作**
- 确认无障碍服务已启用
- 检查游戏界面是否匹配
- 重启应用重试

**点击位置不准确**
- 游戏分辨率可能不匹配
- 需要更新模板图片

## 技术架构

```
main.py              # 主程序入口 (Kivy UI)
android_state.py     # Android状态管理类
buildozer.spec      # Android构建配置
Data/               # 图片模板和配置文件
```

### 核心技术
- **UI框架**: Kivy
- **图像识别**: OpenCV
- **屏幕交互**: Android Shell Commands
- **构建工具**: Buildozer + Python-for-Android

## 开发说明

### 环境搭建
```bash
# 安装依赖
pip install -r requirements.txt

# Linux环境需要安装系统依赖
sudo apt install git zip unzip openjdk-8-jdk python3-pip autoconf libtool
```

### 项目结构
```
MapleStoreMAutoTool/
├── main.py                 # Kivy主应用
├── android_state.py        # Android状态管理
├── buildozer.spec         # 构建配置
├── requirements.txt       # Python依赖
├── build_android.sh       # 构建脚本
├── Data/                  # 游戏数据
│   ├── */                 # 各状态配置
│   ├── *.json            # 配置文件
│   └── *.png             # 模板图片
└── templates/             # Android模板
    └── AndroidManifest.tmpl.xml
```

### 自定义开发
1. 修改 `android_state.py` 中的任务逻辑
2. 更新 `Data/` 目录中的模板图片
3. 调整 `buildozer.spec` 中的配置
4. 重新构建APK

## 版本历史

- v1.0.0: 初始Android版本发布
  - 基础自动化功能
  - Kivy图形界面
  - 多任务类型支持

## 贡献指南

欢迎提交Issues和Pull Requests！

1. Fork本项目
2. 创建特性分支
3. 提交修改
4. 发起Pull Request

## 许可证

本项目遵循原项目的许可证条款。

---

**免责声明**: 本工具仅供教育和研究目的使用。使用自动化工具可能违反游戏服务条款，请谨慎使用并承担相应风险。