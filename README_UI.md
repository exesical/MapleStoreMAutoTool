# 冒险岛M自动助手 - 任务配置UI版本

## 🎯 新增功能

### ✨ 主要特性
- 🖥️ **图形化任务配置界面** - 可视化选择和配置每个角色的任务
- 💾 **配置文件保存** - 任务配置自动保存，下次启动自动加载
- 🎮 **启动器界面** - 提供友好的启动选择界面
- 👥 **分角色配置** - 支持主号、前五号、其他号分别配置不同任务
- 🔄 **实时应用** - 配置修改后可直接应用到游戏中

## 📁 文件结构

```
MapleStoreMAutoTool/
├── Launcher.py              # 启动器 - 选择配置或直接运行
├── TaskConfigUI.py          # 任务配置UI界面
├── MSmAuto.py               # 主程序（已修改支持配置文件）
├── MSmState.py              # 状态管理类（原文件）
├── DoScreenHit.py           # 屏幕交互类（原文件）
├── task_config.json         # 任务配置文件（自动生成）
└── Data/                    # 游戏数据目录
    ├── TaskGroup0-6/        # 任务组配置
    │   ├── TaskListMain.json    # 主号任务
    │   ├── TaskListFive.json    # 前五号任务
    │   └── TaskList.json        # 其他号任务
    └── ...其他游戏数据文件
```

## 🚀 快速开始

### 方法1: 使用启动器（推荐）
```bash
python Launcher.py
```
然后点击"📋 配置任务"按钮进入配置界面。

### 方法2: 直接打开配置界面
```bash
python TaskConfigUI.py
```

### 方法3: 直接运行游戏（使用已保存配置）
```bash
python MSmAuto.py
```

## 🖥️ 任务配置界面说明

### 界面布局
```
┌─────────────────────────────────────────────┐
│                任务配置管理                 │
├─────────────────────────────────────────────┤
│ TaskGroup: [0▼] 角色数: [5] 前五号: [0]      │
├─────────────────────────────────────────────┤
│ ┌主号任务配置┐ ┌前五号配置┐ ┌其他号配置┐    │
│ │[快速按钮]  │ │[快速按钮]│ │[快速按钮]│    │
│ │可用 >> 已选│ │可用 >> 已选│ │可用 >> 已选│    │
│ │任务    任务│ │任务    任务│ │任务    任务│    │
│ └───────────┘ └─────────┘ └─────────┘    │
├─────────────────────────────────────────────┤
│ [保存] [加载] [应用] [重置] [启动游戏]        │
├─────────────────────────────────────────────┤
│                操作日志                     │
└─────────────────────────────────────────────┘
```

### 配置区域说明

#### 1. 任务组选择
- **TaskGroup**: 选择要使用的任务组（0-6）
- **总角色数**: 设置要运行的角色总数
- **前五号角色数**: 设置使用TaskListFive.json配置的角色数量

#### 2. 任务配置区域
每个角色类型都有独立的配置区域：

- **主号任务配置** - 对应TaskListMain.json
- **前五号任务配置** - 对应TaskListFive.json  
- **其他号任务配置** - 对应TaskList.json

#### 3. 任务列表操作
- **>>**: 将选中的可用任务添加到已选列表
- **<<**: 将选中的已选任务移除
- **↑**: 上移已选任务的执行顺序
- **↓**: 下移已选任务的执行顺序

#### 4. 快速操作按钮
- **添加全部**: 添加所有可用任务
- **清空**: 清空已选任务列表
- **默认配置**: 加载对应角色类型的默认任务配置

### 可用任务列表

| 任务代码 | 中文名称 | 说明 |
|----------|----------|------|
| CharacterSelect | 角色选择 | 必须任务，角色切换 |
| GuildInfo | 公会信息 | 公会签到等 |
| Mail | 邮件 | 收取邮件奖励 |
| Material | 材料副本 | 刷取制作材料 |
| MonsterPark | 怪物公园 | 经验副本 |
| Elite | 精英副本 | 高级装备副本 |
| FastJump | 快速副本 | 快速刷副本 |
| Weekly | 周常副本 | 周常任务 |
| NitePyramid | 夜金字塔 | 团队副本 |
| Wulin | 武林道场 | 武林挑战 |
| Pirate | 海盗副本 | 海盗船副本 |
| PostProcess | 后处理 | 整理背包等后续操作 |

## 🔧 操作流程

### 首次使用
1. 运行 `python Launcher.py` 
2. 点击"📋 配置任务"
3. 选择TaskGroup和设置角色数量
4. 为每种角色类型配置任务列表
5. 点击"保存配置"
6. 点击"应用到TaskGroup"
7. 点击"启动游戏"

### 日常使用
1. 运行 `python Launcher.py`
2. 如需修改配置，点击"📋 配置任务"
3. 直接使用，点击"🚀 直接启动"

### 配置文件操作
- **保存配置**: 将当前配置保存到task_config.json
- **加载配置**: 从文件选择器加载其他配置文件
- **应用到TaskGroup**: 将配置写入对应的TaskGroup文件夹
- **重置配置**: 清空所有配置，恢复初始状态

## 📋 默认任务配置

### 主号 (TaskListMain.json)
```json
[
  "CharacterSelect",
  "GuildInfo", 
  "Mail",
  "Material",
  "MonsterPark",
  "Elite", 
  "Weekly",
  "PostProcess",
  "CharacterSelect"
]
```

### 前五号 (TaskListFive.json)
```json
[
  "CharacterSelect",
  "GuildInfo",
  "Mail", 
  "MonsterPark",
  "FastJump",
  "Material",
  "Weekly",
  "PostProcess",
  "CharacterSelect"
]
```

### 其他号 (TaskList.json)
```json
[
  "CharacterSelect",
  "GuildInfo",
  "Mail",
  "FastJump",
  "Material", 
  "Weekly",
  "PostProcess",
  "CharacterSelect"
]
```

## ⚙️ 高级设置

### 配置文件格式 (task_config.json)
```json
{
  "main_character_tasks": ["CharacterSelect", "GuildInfo", ...],
  "five_character_tasks": ["CharacterSelect", "GuildInfo", ...], 
  "other_character_tasks": ["CharacterSelect", "GuildInfo", ...],
  "current_task_group": 0,
  "character_count": 5,
  "vice_character_count": 0,
  "last_updated": "2026-03-17T20:00:00"
}
```

### 命令行参数（兼容原版）
仍支持所有原版命令行参数：
```bash
python MSmAuto.py CharacterCount=10 TaskGroupIndex=1 ViceCharacterCount=2
```

### 备份机制
- 应用配置时自动备份原TaskGroup文件夹
- 备份文件名格式：`TaskGroup{X}_backup_{timestamp}`

## 🐛 故障排除

### 常见问题

**1. 配置界面无法启动**
- 检查是否安装了tkinter: `pip install tk`
- 确认Python版本支持tkinter

**2. 任务配置不生效**
- 确认已点击"保存配置"
- 确认已点击"应用到TaskGroup"
- 检查TaskGroup文件夹是否存在

**3. 找不到任务列表**
- 检查Data/TaskGroup0-6文件夹是否完整
- 确认JSON文件格式正确

**4. 游戏脚本无法启动**
- 确认模拟器已启动
- 检查游戏是否在角色选择界面
- 查看控制台错误输出

### 日志输出
配置界面底部的日志区域会显示所有操作记录，有助于定位问题。

## 🔄 兼容性说明

### 向后兼容
- 完全兼容原版TaskGroup文件格式
- 支持所有原版命令行参数
- 可与原版脚本无缝切换

### 配置优先级
1. 命令行参数（最高优先级）
2. task_config.json配置文件
3. 默认配置（最低优先级）

## 📝 更新日志

### v2.0.0 (2026-03-17)
- ✅ 新增任务配置UI界面
- ✅ 新增配置文件保存功能
- ✅ 新增启动器界面
- ✅ 支持分角色任务配置
- ✅ 自动备份原配置文件
- ✅ 完全兼容原版功能

---

## 🆘 技术支持

如果遇到问题，请：
1. 查看操作日志输出
2. 检查配置文件格式
3. 确认游戏环境设置
4. 提供详细错误信息

**享受更便捷的冒险岛M自动化体验！** 🎮