import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from tkinter.scrolledtext import ScrolledText
from FrozenPath import frozen
from datetime import datetime

class TaskConfigUI:
    def __init__(self, parent_window=None):
        if parent_window is not None:
            self.root = parent_window
        else:
            self.root = tk.Tk()
        
        self.root.title("冒险岛M自动助手 - 任务配置")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 任务映射表
        self.task_mapping = {
            "CharacterSelect": "角色选择",
            "GuildInfo": "公会信息", 
            "Mail": "邮件",
            "Material": "材料副本",
            "MonsterPark": "怪物公园",
            "NitePyramid": "夜金字塔",
            "Wulin": "武林道场", 
            "Elite": "精英副本",
            "SpecialWeekly": "特殊周常",
            "Weekly": "周常副本",
            "Pirate": "海盗副本",
            "Tangyun": "糖云",
            "PostProcess": "后处理",
            "FastJump": "快速副本",
            "Dimension": "次元副本",
            "Expedition": "远征队",
            "Evolution": "进化副本",
            "Exchange": "交易所",
            "DailyTask": "日常任务"
        }
        
        # 数据文件路径
        self.data_path = frozen.app_path() + "\\Data\\"
        
        # 当前选中的TaskGroup
        self.current_task_group = 0
        
        # 可用的任务列表（从TaskGroup0获取）
        self.available_tasks = []
        self.load_available_tasks()
        
        # 配置数据
        self.config_data = {
            "main_character_tasks": [],
            "other_character_tasks": [],
            "five_character_tasks": [],
            "current_task_group": 0,
            "vice_character_count": 0,
            "b_post_process_default": True,  # 默认功能：发送人气、交易商品、日常任务等
            "b_post_process_weekly_reward": False,  # 收周任务奖励
            "b_post_process_auto_change": False,  # 自动换黄图
            "b_post_process_organize_package": False,  # 自动整理背包
            "b_post_process_skip_commission": False,  # 自动跳过委托
            "b_post_process_additional_material": False,  # 开材料卷
            "fast_jump_type": 0  # 默认值为0
        }
        
        # FastJumpType选项映射
        self.fast_jump_options = {
            "0 - 夜金字塔": 0,
            "1 - 怪物公园": 1
        }
        
        self.create_ui()
        # 初始加载当前TaskGroup的配置
        self.load_existing_taskgroup_config(self.current_task_group)
        
    def load_available_tasks(self):
        """从task_mapping中获取所有可用的任务（对应StateTable中声明的状态）"""
        # task_mapping 定义了所有可用的状态，直接从中获取
        # CharacterSelect 不在可选列表中显示，但会自动添加到任务列表头尾
        self.available_tasks = []
        for task in sorted(self.task_mapping.keys()):
            if task != "CharacterSelect":
                self.available_tasks.append(task)
    
    def create_ui(self):
        """创建UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="任务配置管理", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # TaskGroup选择
        group_frame = ttk.LabelFrame(main_frame, text="任务组选择", padding="10")
        group_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        group_frame.columnconfigure(1, weight=1)
        
        ttk.Label(group_frame, text="当前任务组:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.task_group_var = tk.StringVar(value=str(self.current_task_group))
        group_combo = ttk.Combobox(group_frame, textvariable=self.task_group_var, 
                                  values=[str(i) for i in range(7)], state="readonly", width=10)
        group_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        group_combo.bind("<<ComboboxSelected>>", self.on_task_group_changed)
        
        # 角色数量设置（仅保留副号数量）
        
        ttk.Label(group_frame, text="副号角色数:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.vice_char_count_var = tk.StringVar(value=str(self.config_data["vice_character_count"]))
        vice_char_spin = ttk.Spinbox(group_frame, from_=0, to=20, textvariable=self.vice_char_count_var, width=10)
        vice_char_spin.grid(row=0, column=3, sticky=tk.W)
        
        # 第二行：PostProcess 设置（使用复选框，行优先显示）
        ttk.Label(group_frame, text="后处理功能:").grid(row=1, column=0, sticky=tk.NW, padx=(0, 10), pady=(10, 0))
        
        post_process_frame = ttk.Frame(group_frame)
        post_process_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 第一行：默认功能、收周任务奖励
        row1_frame = ttk.Frame(post_process_frame)
        row1_frame.pack(anchor=tk.W, fill=tk.X)
        
        self.b_post_process_default_var = tk.BooleanVar(value=self.config_data["b_post_process_default"])
        ttk.Checkbutton(row1_frame, text="默认功能(人气/交易/日常)", 
                       variable=self.b_post_process_default_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.b_post_process_weekly_reward_var = tk.BooleanVar(value=self.config_data["b_post_process_weekly_reward"])
        ttk.Checkbutton(row1_frame, text="收周任务奖励", 
                       variable=self.b_post_process_weekly_reward_var).pack(side=tk.LEFT, padx=(0, 20))
        
        # 第二行：自动换黄图、自动整理背包、自动跳过委托
        row2_frame = ttk.Frame(post_process_frame)
        row2_frame.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))
        
        self.b_post_process_auto_change_var = tk.BooleanVar(value=self.config_data["b_post_process_auto_change"])
        ttk.Checkbutton(row2_frame, text="自动换黄图", 
                       variable=self.b_post_process_auto_change_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.b_post_process_organize_package_var = tk.BooleanVar(value=self.config_data["b_post_process_organize_package"])
        ttk.Checkbutton(row2_frame, text="自动整理背包", 
                       variable=self.b_post_process_organize_package_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.b_post_process_skip_commission_var = tk.BooleanVar(value=self.config_data["b_post_process_skip_commission"])
        ttk.Checkbutton(row2_frame, text="自动跳过委托", 
                       variable=self.b_post_process_skip_commission_var).pack(side=tk.LEFT, padx=(0, 20))
        
        # 第三行：开材料卷
        row3_frame = ttk.Frame(post_process_frame)
        row3_frame.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))
        
        self.b_post_process_additional_material_var = tk.BooleanVar(value=self.config_data["b_post_process_additional_material"])
        ttk.Checkbutton(row3_frame, text="开材料卷", 
                       variable=self.b_post_process_additional_material_var).pack(side=tk.LEFT)
        
        # 第四行：FastJumpType设置
        ttk.Label(group_frame, text="快速副本类型:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 找到默认的FastJumpType对应的选项文本
        default_fast_jump_option = "0 - 夜金字塔"
        for option_text, value in self.fast_jump_options.items():
            if value == self.config_data["fast_jump_type"]:
                default_fast_jump_option = option_text
                break
        
        self.fast_jump_var = tk.StringVar(value=default_fast_jump_option)
        fast_jump_combo = ttk.Combobox(group_frame, textvariable=self.fast_jump_var, 
                                      values=list(self.fast_jump_options.keys()), 
                                      state="readonly", width=25)
        fast_jump_combo.grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 任务配置区域
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1) 
        config_frame.columnconfigure(2, weight=1)
        config_frame.rowconfigure(0, weight=1)
        
        # 主号任务配置
        self.create_task_config_frame(config_frame, "主号任务配置", 0, "main_character_tasks")
        
        # 副号任务配置
        self.create_task_config_frame(config_frame, "副号任务配置", 1, "five_character_tasks")
        
        # 其他号任务配置
        self.create_task_config_frame(config_frame, "其他号任务配置", 2, "other_character_tasks")
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="保存配置", command=self.apply_to_task_group).pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = ScrolledText(log_frame, height=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始化日志
        self.log("任务配置UI已启动")
        self.log(f"当前TaskGroup: {self.current_task_group}")
        
    def create_task_config_frame(self, parent, title, column, config_key):
        """创建任务配置框架"""
        frame = ttk.LabelFrame(parent, text=title, padding="10")
        frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # 快速设置按钮
        quick_frame = ttk.Frame(frame)
        quick_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(quick_frame, text="添加全部", 
                  command=lambda: self.add_all_tasks(config_key)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="清空", 
                  command=lambda: self.clear_tasks(config_key)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="默认配置", 
                  command=lambda: self.load_default_config(config_key)).pack(side=tk.LEFT, padx=2)
        
        # 任务列表（双列表框）
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(2, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 可用任务列表
        available_frame = ttk.Frame(list_frame)
        available_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(1, weight=1)
        
        ttk.Label(available_frame, text="可用任务").grid(row=0, column=0)
        
        available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED)
        available_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        available_scroll = ttk.Scrollbar(available_frame, orient=tk.VERTICAL, command=available_listbox.yview)
        available_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        available_listbox.config(yscrollcommand=available_scroll.set)
        
        # 填充可用任务
        for task in self.available_tasks:
            display_name = self.task_mapping.get(task, task)
            available_listbox.insert(tk.END, f"{display_name} ({task})")
        
        # 中间按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=0, column=1, padx=10)
        
        ttk.Button(button_frame, text=">>", width=5,
                  command=lambda: self.move_task(available_listbox, selected_listbox, config_key)).pack(pady=5)
        ttk.Button(button_frame, text="<<", width=5,
                  command=lambda: self.remove_task(selected_listbox, config_key)).pack(pady=5)
        ttk.Button(button_frame, text="↑", width=5,
                  command=lambda: self.move_up(selected_listbox, config_key)).pack(pady=5)
        ttk.Button(button_frame, text="↓", width=5,
                  command=lambda: self.move_down(selected_listbox, config_key)).pack(pady=5)
        
        # 已选任务列表
        selected_frame = ttk.Frame(list_frame)
        selected_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(1, weight=1)
        
        ttk.Label(selected_frame, text="已选任务").grid(row=0, column=0)
        
        selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED)
        selected_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        selected_scroll = ttk.Scrollbar(selected_frame, orient=tk.VERTICAL, command=selected_listbox.yview)
        selected_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        selected_listbox.config(yscrollcommand=selected_scroll.set)
        
        # 保存引用
        setattr(self, f"{config_key}_available_listbox", available_listbox)
        setattr(self, f"{config_key}_selected_listbox", selected_listbox)
        
        # 加载已配置的任务
        self.refresh_selected_tasks(config_key)
    
    def refresh_selected_tasks(self, config_key):
        """刷新已选任务显示（过滤掉CharacterSelect）"""
        listbox = getattr(self, f"{config_key}_selected_listbox")
        listbox.delete(0, tk.END)
        
        # 过滤掉CharacterSelect，只显示中间的任务
        for task in self.config_data[config_key]:
            if task != "CharacterSelect":
                display_name = self.task_mapping.get(task, task)
                listbox.insert(tk.END, f"{display_name} ({task})")
    
    def move_task(self, from_listbox, to_listbox, config_key):
        """移动任务到已选列表"""
        selection = from_listbox.curselection()
        if not selection:
            return
            
        for index in selection:
            item_text = from_listbox.get(index)
            # 提取任务名称（括号内的部分）
            task_name = item_text.split('(')[-1].replace(')', '')
            
            # 获取当前过滤后的任务列表（不含CharacterSelect）
            filtered_tasks = [task for task in self.config_data[config_key] if task != "CharacterSelect"]
            
            if task_name not in filtered_tasks and task_name != "CharacterSelect":
                filtered_tasks.append(task_name)
                # 重建完整任务列表（开头和结尾加上CharacterSelect）
                self.config_data[config_key] = ["CharacterSelect"] + filtered_tasks + ["CharacterSelect"]
                
        self.refresh_selected_tasks(config_key)
        self.log(f"已添加任务到 {config_key}")
    
    def remove_task(self, selected_listbox, config_key):
        """从已选列表移除任务"""
        selection = selected_listbox.curselection()
        if not selection:
            return
            
        # 从后往前删除，避免索引问题
        for index in reversed(selection):
            item_text = selected_listbox.get(index)
            task_name = item_text.split('(')[-1].replace(')', '')
            
            # 获取当前过滤后的任务列表（不含CharacterSelect）
            filtered_tasks = [task for task in self.config_data[config_key] if task != "CharacterSelect"]
            
            if task_name in filtered_tasks:
                filtered_tasks.remove(task_name)
                # 重建完整任务列表（开头和结尾加上CharacterSelect）
                self.config_data[config_key] = ["CharacterSelect"] + filtered_tasks + ["CharacterSelect"]
                
        self.refresh_selected_tasks(config_key)
        self.log(f"已从 {config_key} 移除任务")
    
    def move_up(self, selected_listbox, config_key):
        """上移任务（排除CharacterSelect）"""
        selection = selected_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        # 获取过滤后的任务列表（不含CharacterSelect）
        filtered_tasks = [task for task in self.config_data[config_key] if task != "CharacterSelect"]
        if len(filtered_tasks) <= 1:
            return
            
        index = selection[0]
        if index == 0:
            return
            
        # 在过滤后的列表中交换
        filtered_tasks[index], filtered_tasks[index-1] = filtered_tasks[index-1], filtered_tasks[index]
        
        # 重建完整任务列表（开头和结尾加上CharacterSelect）
        self.config_data[config_key] = ["CharacterSelect"] + filtered_tasks + ["CharacterSelect"]
        
        self.refresh_selected_tasks(config_key)
        selected_listbox.selection_set(index-1)
        self.log(f"任务上移: {config_key}")
    
    def move_down(self, selected_listbox, config_key):
        """下移任务（排除CharacterSelect）"""
        selection = selected_listbox.curselection()
        if not selection:
            return
            
        # 获取过滤后的任务列表（不含CharacterSelect）
        filtered_tasks = [task for task in self.config_data[config_key] if task != "CharacterSelect"]
        if len(filtered_tasks) <= 1:
            return
            
        index = selection[0]
        if index >= len(filtered_tasks) - 1:
            return
            
        # 在过滤后的列表中交换
        filtered_tasks[index], filtered_tasks[index+1] = filtered_tasks[index+1], filtered_tasks[index]
        
        # 重建完整任务列表（开头和结尾加上CharacterSelect）
        self.config_data[config_key] = ["CharacterSelect"] + filtered_tasks + ["CharacterSelect"]
        
        self.refresh_selected_tasks(config_key)
        selected_listbox.selection_set(index+1)
        self.log(f"任务下移: {config_key}")
    
    def add_all_tasks(self, config_key):
        """添加所有可用任务"""
        self.config_data[config_key] = self.available_tasks.copy()
        self.refresh_selected_tasks(config_key)
        self.log(f"已添加所有任务到 {config_key}")
    
    def clear_tasks(self, config_key):
        """清空任务列表（保留CharacterSelect结构）"""
        # 只保留CharacterSelect结构，清空中间的任务
        self.config_data[config_key] = ["CharacterSelect", "CharacterSelect"]
        self.refresh_selected_tasks(config_key)
        self.log(f"已清空 {config_key}")
    
    def load_default_config(self, config_key):
        """从Data/TaskGroup加载只读的默认配置"""
        task_group = self.current_task_group
        filename_map = {
            "main_character_tasks": "TaskListMain.json",
            "five_character_tasks": "TaskListFive.json", 
            "other_character_tasks": "TaskList.json"
        }
        
        filename = filename_map.get(config_key)
        if not filename:
            self.log(f"未知的配置类型: {config_key}")
            return
        
        # 从Data/TaskGroup（只读默认配置）读取
        default_path = os.path.join(self.data_path, f"TaskGroup{task_group}", filename)
        
        if os.path.exists(default_path):
            try:
                with open(default_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    self.config_data[config_key] = tasks
                    self.refresh_selected_tasks(config_key)
                    self.log(f"已从Data/TaskGroup{task_group}加载 {filename} 的默认配置（{len(tasks)}个任务）")
                    return
            except Exception as e:
                self.log(f"加载默认配置失败: {e}")
        
        # 如果文件不存在，使用硬编码的备用默认配置
        fallback_configs = {
            "main_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "Material", 
                                   "MonsterPark", "Elite", "Weekly", "PostProcess", "CharacterSelect"],
            "five_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "MonsterPark", 
                                   "FastJump", "Material", "Weekly", "PostProcess", "CharacterSelect"],
            "other_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "FastJump", 
                                    "Material", "Weekly", "PostProcess", "CharacterSelect"]
        }
        
        self.config_data[config_key] = fallback_configs.get(config_key, [])
        self.refresh_selected_tasks(config_key)
        self.log(f"已加载 {config_key} 的内置默认配置")
    
    def on_task_group_changed(self, event=None):
        """TaskGroup改变时的处理"""
        try:
            new_group = int(self.task_group_var.get())
            old_group = self.current_task_group
            self.current_task_group = new_group
            self.config_data["current_task_group"] = new_group
            self.log(f"切换到TaskGroup {new_group} (从TaskGroup {old_group})")
            
            # 重新加载可用任务列表（因为不同TaskGroup可能有不同的任务）
            self.load_available_tasks()
            
            # 尝试从SaveTaskGroup或Data/TaskGroup加载现有配置
            self.load_existing_taskgroup_config(new_group)
            
        except ValueError:
            self.log("TaskGroup切换失败：无效的数值")
    
    def load_existing_taskgroup_config(self, task_group):
        """加载指定TaskGroup的现有配置（优先从SaveTaskGroup，回退到Data/TaskGroup）"""
        try:
            # 清空当前配置（保留CharacterSelect结构）
            self.config_data["main_character_tasks"] = ["CharacterSelect", "CharacterSelect"]
            self.config_data["five_character_tasks"] = ["CharacterSelect", "CharacterSelect"]
            self.config_data["other_character_tasks"] = ["CharacterSelect", "CharacterSelect"]
            
            # 任务文件映射
            task_files = {
                "main_character_tasks": "TaskListMain.json",
                "five_character_tasks": "TaskListFive.json",
                "other_character_tasks": "TaskList.json"
            }
            
            # 尝试从SaveTaskGroup加载（使用与MSmAuto一致的路径构建方式）
            save_base_path = frozen.app_path() + "\\Data\\SaveTaskGroup"
            save_group_path = os.path.join(save_base_path, f"TaskGroup{task_group}")
            
            # 先尝试从SaveTaskGroup加载每个配置
            for config_key, filename in task_files.items():
                loaded = False
                
                # 优先从SaveTaskGroup加载
                save_file_path = os.path.join(save_group_path, filename)
                if os.path.exists(save_file_path):
                    try:
                        with open(save_file_path, 'r', encoding='utf-8') as f:
                            tasks = json.load(f)
                            self.config_data[config_key] = tasks
                        loaded = True
                        self.log(f"从SaveTaskGroup{task_group}加载了 {filename}")
                    except Exception as e:
                        self.log(f"从SaveTaskGroup加载{filename}失败: {e}")
                
                # 如果SaveTaskGroup没有该配置，从Data/TaskGroup加载默认配置
                if not loaded:
                    default_group_path = os.path.join(self.data_path, f"TaskGroup{task_group}")
                    default_file_path = os.path.join(default_group_path, filename)
                    if os.path.exists(default_file_path):
                        try:
                            with open(default_file_path, 'r', encoding='utf-8') as f:
                                tasks = json.load(f)
                                self.config_data[config_key] = tasks
                            self.log(f"从Data/TaskGroup{task_group}加载了默认配置 {filename}")
                        except Exception as e:
                            self.log(f"从Data/TaskGroup加载{filename}失败: {e}")
                    else:
                        # 如果文件都不存在，使用内置默认配置
                        self.log(f"TaskGroup{task_group}的{filename}不存在，使用内置默认配置")
                        # 使用内置的默认配置
                        fallback_configs = {
                            "main_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "Material", 
                                                   "MonsterPark", "Elite", "Weekly", "PostProcess", "CharacterSelect"],
                            "five_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "MonsterPark", 
                                                   "FastJump", "Material", "Weekly", "PostProcess", "CharacterSelect"],
                            "other_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "FastJump", 
                                                    "Material", "Weekly", "PostProcess", "CharacterSelect"]
                        }
                        self.config_data[config_key] = fallback_configs.get(config_key, ["CharacterSelect", "CharacterSelect"])
                            
            # 同时加载config_info.json中的角色数量和 PostProcess 相关配置
            config_info_path = os.path.join(save_group_path, "config_info.json")
            config_loaded = False
            if os.path.exists(config_info_path):
                try:
                    with open(config_info_path, 'r', encoding='utf-8') as f:
                        config_info = json.load(f)
                        
                        # 加载副号角色数量
                        if "vice_character_count" in config_info:
                            self.config_data["vice_character_count"] = config_info["vice_character_count"]
                            self.vice_char_count_var.set(str(config_info["vice_character_count"]))
                        
                        # 加载 PostProcess 相关的 bool 配置
                        if "b_post_process_default" in config_info:
                            self.config_data["b_post_process_default"] = config_info["b_post_process_default"]
                            self.b_post_process_default_var.set(config_info["b_post_process_default"])
                        else:
                            self.config_data["b_post_process_default"] = True
                            self.b_post_process_default_var.set(True)
                            
                        if "b_post_process_weekly_reward" in config_info:
                            self.config_data["b_post_process_weekly_reward"] = config_info["b_post_process_weekly_reward"]
                            self.b_post_process_weekly_reward_var.set(config_info["b_post_process_weekly_reward"])
                        else:
                            self.config_data["b_post_process_weekly_reward"] = False
                            self.b_post_process_weekly_reward_var.set(False)
                            
                        if "b_post_process_auto_change" in config_info:
                            self.config_data["b_post_process_auto_change"] = config_info["b_post_process_auto_change"]
                            self.b_post_process_auto_change_var.set(config_info["b_post_process_auto_change"])
                        else:
                            self.config_data["b_post_process_auto_change"] = False
                            self.b_post_process_auto_change_var.set(False)
                            
                        if "b_post_process_organize_package" in config_info:
                            self.config_data["b_post_process_organize_package"] = config_info["b_post_process_organize_package"]
                            self.b_post_process_organize_package_var.set(config_info["b_post_process_organize_package"])
                        else:
                            self.config_data["b_post_process_organize_package"] = False
                            self.b_post_process_organize_package_var.set(False)
                            
                        if "b_post_process_skip_commission" in config_info:
                            self.config_data["b_post_process_skip_commission"] = config_info["b_post_process_skip_commission"]
                            self.b_post_process_skip_commission_var.set(config_info["b_post_process_skip_commission"])
                        else:
                            self.config_data["b_post_process_skip_commission"] = False
                            self.b_post_process_skip_commission_var.set(False)
                            
                        # 加载FastJumpType
                        if "fast_jump_type" in config_info:
                            self.config_data["fast_jump_type"] = config_info["fast_jump_type"]
                            # 找到对应的选项文本并更新UI
                            for option_text, value in self.fast_jump_options.items():
                                if value == config_info["fast_jump_type"]:
                                    self.fast_jump_var.set(option_text)
                                    self.log(f"从config_info.json加载FastJumpType: {option_text}")
                                    break
                        else:
                            # 如果没有FastJumpType配置，使用默认值并更新UI
                            self.config_data["fast_jump_type"] = 0
                            self.fast_jump_var.set("0 - 夜金字塔")
                            
                        # 加载AdditionalMaterial (兼容旧配置)
                        if "b_post_process_additional_material" in config_info:
                            self.config_data["b_post_process_additional_material"] = config_info["b_post_process_additional_material"]
                            self.b_post_process_additional_material_var.set(config_info["b_post_process_additional_material"])
                            self.log(f"从config_info.json加载b_post_process_additional_material: {config_info['b_post_process_additional_material']}")
                        elif "additional_material" in config_info:
                            # 兼容旧配置：从整数转换为bool
                            old_value = config_info["additional_material"]
                            new_value = old_value == 1
                            self.config_data["b_post_process_additional_material"] = new_value
                            self.b_post_process_additional_material_var.set(new_value)
                            self.log(f"从旧配置转换AdditionalMaterial: {old_value} -> {new_value}")
                        else:
                            # 如果没有配置，使用默认值
                            self.config_data["b_post_process_additional_material"] = False
                            self.b_post_process_additional_material_var.set(False)
                            
                        config_loaded = True
                        self.log(f"加载了TaskGroup{task_group}的配置（角色数量、后处理类型）")
                except Exception as e:
                    self.log(f"加载config_info.json失败: {e}")
            
            # 如果没有找到SaveTaskGroup的config_info.json，重置为默认值
            if not config_loaded:
                self.config_data["vice_character_count"] = 0
                self.vice_char_count_var.set("0")
                self.config_data["b_post_process_default"] = True
                self.b_post_process_default_var.set(True)
                self.config_data["b_post_process_weekly_reward"] = False
                self.b_post_process_weekly_reward_var.set(False)
                self.config_data["b_post_process_auto_change"] = False
                self.b_post_process_auto_change_var.set(False)
                self.config_data["b_post_process_organize_package"] = False
                self.b_post_process_organize_package_var.set(False)
                self.config_data["b_post_process_skip_commission"] = False
                self.b_post_process_skip_commission_var.set(False)
                self.config_data["b_post_process_additional_material"] = False
                self.b_post_process_additional_material_var.set(False)
                self.config_data["fast_jump_type"] = 0
                self.fast_jump_var.set("0 - 夜金字塔")
                self.log(f"TaskGroup{task_group}没有保存的配置，使用默认值")
            
            # 刷新界面
            for config_key in task_files.keys():
                self.refresh_selected_tasks(config_key)
                
            self.log(f"TaskGroup{task_group}配置加载完成")
            
        except Exception as e:
            self.log(f"加载TaskGroup{task_group}配置失败: {e}")
    
    def refresh_post_process_ui(self):
        """刷新PostProcess、FastJumpType和AdditionalMaterial UI控件"""
        try:
            # 刷新PostProcess bool值
            self.b_post_process_default_var.set(self.config_data.get("b_post_process_default", True))
            self.b_post_process_weekly_reward_var.set(self.config_data.get("b_post_process_weekly_reward", False))
            self.b_post_process_auto_change_var.set(self.config_data.get("b_post_process_auto_change", False))
            self.b_post_process_organize_package_var.set(self.config_data.get("b_post_process_organize_package", False))
            self.b_post_process_skip_commission_var.set(self.config_data.get("b_post_process_skip_commission", False))
            self.b_post_process_additional_material_var.set(self.config_data.get("b_post_process_additional_material", False))
            self.log("UI已更新PostProcess配置")
            
            # 刷新FastJumpType
            current_fast_jump_type = self.config_data.get("fast_jump_type", 0)
            fast_jump_updated = False
            for option_text, value in self.fast_jump_options.items():
                if value == current_fast_jump_type:
                    if self.fast_jump_var.get() != option_text:
                        self.fast_jump_var.set(option_text)
                        self.log(f"UI更新FastJumpType为: {option_text}")
                    fast_jump_updated = True
                    break
            if not fast_jump_updated:
                self.fast_jump_var.set("0 - 夜金字塔")
                self.log("UI重置FastJumpType为默认值")
                
        except Exception as e:
            self.log(f"刷新UI失败: {e}")
    
    def load_config_file(self):
        """从文件选择器加载配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config_data.update(loaded_config)
                    
                self.load_config()  # 刷新UI
                self.log(f"从 {file_path} 加载配置成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {e}")
    
    def ensure_character_select_wrapper(self, task_list):
        """确保任务列表以CharacterSelect开始和结束"""
        # 移除所有现有的CharacterSelect
        filtered_tasks = [task for task in task_list if task != "CharacterSelect"]
        
        # 添加开始和结束的CharacterSelect
        if not filtered_tasks:
            return ["CharacterSelect", "CharacterSelect"]
        
        return ["CharacterSelect"] + filtered_tasks + ["CharacterSelect"]
    
    def apply_to_task_group(self):
        """将配置应用到SaveTaskGroup文件夹（保护原始Data/TaskGroup不被修改）"""
        try:
            task_group = self.current_task_group
            
            # 创建SaveTaskGroup文件夹（使用与MSmAuto一致的路径构建方式）
            save_base_path = frozen.app_path() + "\\Data\\SaveTaskGroup"
            if not os.path.exists(save_base_path):
                os.makedirs(save_base_path)
                self.log(f"创建SaveTaskGroup文件夹: {save_base_path}")
            
            save_group_path = os.path.join(save_base_path, f"TaskGroup{task_group}")
            
            if not os.path.exists(save_group_path):
                os.makedirs(save_group_path)
            
            # 直接写入新配置到SaveTaskGroup，确保任务列表格式正确
            configs = [
                ("TaskListMain.json", self.ensure_character_select_wrapper(self.config_data["main_character_tasks"])),
                ("TaskListFive.json", self.ensure_character_select_wrapper(self.config_data["five_character_tasks"])), 
                ("TaskList.json", self.ensure_character_select_wrapper(self.config_data["other_character_tasks"]))
            ]
            
            for filename, tasks in configs:
                file_path = os.path.join(save_group_path, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tasks, f, ensure_ascii=False, indent=2)
                self.log(f"已保存 {filename} 到 SaveTaskGroup{task_group} (包含CharacterSelect包装)")
            
            # 创建一个标识文件，表明这是用户自定义配置
            info_file = os.path.join(save_group_path, "config_info.json")
            
            # 获取当前选中的 PostProcess 相关 bool 值
            b_post_process_default = self.b_post_process_default_var.get()
            b_post_process_weekly_reward = self.b_post_process_weekly_reward_var.get()
            b_post_process_auto_change = self.b_post_process_auto_change_var.get()
            b_post_process_organize_package = self.b_post_process_organize_package_var.get()
            b_post_process_skip_commission = self.b_post_process_skip_commission_var.get()
            b_post_process_additional_material = self.b_post_process_additional_material_var.get()
            
            selected_fast_jump_text = self.fast_jump_var.get()
            selected_fast_jump_value = self.fast_jump_options.get(selected_fast_jump_text, 0)
            
            # 获取当前UI中的副号角色数量
            try:
                current_vice_char_count = int(self.vice_char_count_var.get())
            except ValueError:
                current_vice_char_count = 0
            
            config_info = {
                "created_time": datetime.now().isoformat(),
                "source": "TaskConfigUI",
                "task_group": task_group,
                "vice_character_count": current_vice_char_count,
                "b_post_process_default": b_post_process_default,
                "b_post_process_weekly_reward": b_post_process_weekly_reward,
                "b_post_process_auto_change": b_post_process_auto_change,
                "b_post_process_organize_package": b_post_process_organize_package,
                "b_post_process_skip_commission": b_post_process_skip_commission,
                "b_post_process_additional_material": b_post_process_additional_material,
                "fast_jump_type": selected_fast_jump_value,
                "description": "用户自定义任务配置，优先级高于默认Data/TaskGroup配置"
            }
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(config_info, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"配置已保存到SaveTaskGroup{task_group}！")
            
        except Exception as e:
            self.log(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "是否要重置所有配置？"):
            self.config_data = {
                "main_character_tasks": [],
                "other_character_tasks": [],
                "five_character_tasks": [],
                "current_task_group": 0,
                "vice_character_count": 0,
                "b_post_process_default": True,
                "b_post_process_weekly_reward": False,
                "b_post_process_auto_change": False,
                "b_post_process_organize_package": False,
                "b_post_process_skip_commission": False,
                "b_post_process_additional_material": False,
                "fast_jump_type": 0
            }
            
            # 重新加载UI
            self.vice_char_count_var.set("0")
            self.task_group_var.set("0")
            self.b_post_process_default_var.set(True)
            self.b_post_process_weekly_reward_var.set(False)
            self.b_post_process_auto_change_var.set(False)
            self.b_post_process_organize_package_var.set(False)
            self.b_post_process_skip_commission_var.set(False)
            self.b_post_process_additional_material_var.set(False)
            
            for key in ["main_character_tasks", "five_character_tasks", "other_character_tasks"]:
                self.refresh_selected_tasks(key)
                
            self.log("配置已重置")
    
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数入口"""
    app = TaskConfigUI()
    app.run()

if __name__ == "__main__":
    main()
