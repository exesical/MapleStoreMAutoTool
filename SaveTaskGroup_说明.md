# SaveTaskGroup 文件结构说明

## 概述

为了保护原始配置文件不被意外修改，现在采用了双层配置结构：

## 文件夹结构

```
MapleStoreMAutoTool/
├── Data/
│   └── TaskGroup0-6/           # 只读默认配置（不会被修改）
│       ├── TaskListMain.json   # 主号默认任务
│       ├── TaskListFive.json   # 前五号默认任务
│       ├── TaskList.json       # 其他角色默认任务
│       └── TaskListExpedition.json # 远征默认任务
│
├── SaveTaskGroup/              # 用户自定义配置（优先级更高）
│   └── TaskGroup0-6/           # 用户保存的任务配置
│       ├── TaskListMain.json   # 主号自定义任务
│       ├── TaskListFive.json   # 前五号自定义任务
│       ├── TaskList.json       # 其他角色自定义任务
│       └── config_info.json    # 配置信息文件
│
├── TaskConfigUI.py             # 任务配置界面
├── MSmAuto.py                 # 游戏自动化主脚本
└── Launcher.exe               # 启动器
```

## 工作原理

### 1. 配置保存（TaskConfigUI.py）
- 用户在界面中配置任务
- 点击"保存配置到SaveTaskGroup"
- 配置保存到 `SaveTaskGroup/TaskGroupX/` 文件夹
- **原始 `Data/TaskGroup/` 保持不变（只读）**

### 2. 配置加载（MSmAuto.py）
游戏脚本按以下优先级加载配置：

1. **第一优先级**：`SaveTaskGroup/TaskGroupX/TaskListXXX.json`（用户自定义）
2. **第二优先级**：`Data/TaskGroupX/TaskListXXX.json`（默认配置）

```python
# 加载逻辑伪代码
if (SaveTaskGroup配置存在):
    使用SaveTaskGroup配置
else:
    使用Data/TaskGroup默认配置
```

### 3. 默认配置加载（TaskConfigUI.py）
- 点击"加载默认"按钮时
- 从只读的 `Data/TaskGroup/` 读取默认配置
- 不会加载用户已保存的 `SaveTaskGroup/` 配置

## 安全特性

### ✅ 保护原始配置
- `Data/TaskGroup/` 文件夹中的JSON文件被视为只读
- TaskConfigUI不会修改这些文件
- 确保默认配置始终可用

### ✅ 备份机制
- 保存新配置时，会自动备份现有的SaveTaskGroup配置
- 备份文件名包含时间戳，方便追溯

### ✅ 优雅降级
- 如果SaveTaskGroup配置损坏，自动回退到默认配置
- 如果默认配置也不存在，使用内置的硬编码配置

## 使用步骤

### 首次配置
1. 打开 TaskConfigUI
2. 点击各个"加载默认"按钮，加载Data/TaskGroup中的默认配置
3. 根据需要调整任务顺序
4. 点击"保存配置到SaveTaskGroup"

### 修改配置
1. 打开 TaskConfigUI
2. 当前配置会自动加载（优先从SaveTaskGroup读取）
3. 调整任务配置
4. 点击"保存配置到SaveTaskGroup"

### 恢复默认
1. 打开 TaskConfigUI
2. 点击相应的"加载默认"按钮
3. 这将从Data/TaskGroup加载只读的原始配置
4. 点击"保存配置到SaveTaskGroup"覆盖自定义配置

## 配置信息文件

每次保存配置时，会生成一个 `config_info.json` 文件：

```json
{
  "created_time": "2026-03-17T21:26:33.123456",
  "source": "TaskConfigUI",
  "task_group": 0,
  "character_count": 10,
  "vice_character_count": 5,
  "description": "用户自定义任务配置，优先级高于默认Data/TaskGroup配置"
}
```

此文件帮助识别配置的来源和创建时间。

## 技术优势

1. **向后兼容**：如果没有SaveTaskGroup，系统仍能正常工作
2. **配置隔离**：用户配置与默认配置完全分离
3. **易于重置**：删除SaveTaskGroup文件夹即可恢复默认行为
4. **版本升级友好**：更新软件时，用户配置不会丢失
5. **多人使用**：不同用户可以有各自的SaveTaskGroup文件夹

## 注意事项

- SaveTaskGroup文件夹在首次保存配置时自动创建
- 只有通过TaskConfigUI保存的配置才会产生config_info.json
- 手动修改SaveTaskGroup中的JSON文件是安全的，但不会生成config_info.json
- 删除整个SaveTaskGroup文件夹会让系统回到默认行为