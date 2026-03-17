import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from tkinter.scrolledtext import ScrolledText
from FrozenPath import frozen
import shutil
from datetime import datetime

class TaskConfigUI:
    def __init__(self):
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
            "Exchange": "交易所"
        }
        
        # 配置文件路径
        self.config_path = frozen.app_path() + "\\task_config.json"
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
            "character_count": 5,
            "vice_character_count": 0
        }
        
        self.create_ui()
        self.load_config()
        
    def load_available_tasks(self):
        """从现有的TaskGroup文件夹加载可用任务"""
        try:
            # 收集所有可能的任务
            all_tasks = set()
            
            # 从TaskGroup0-6收集所有任务
            for group in range(7):
                group_path = os.path.join(self.data_path, f"TaskGroup{group}")
                if os.path.exists(group_path):
                    for task_file in ["TaskListMain.json", "TaskList.json", "TaskListFive.json"]:
                        task_path = os.path.join(group_path, task_file)
                        if os.path.exists(task_path):
                            with open(task_path, 'r', encoding='utf-8') as f:
                                tasks = json.load(f)
                                all_tasks.update(tasks)
            
            # 排序并过滤重复的CharacterSelect
            self.available_tasks = []
            for task in sorted(all_tasks):
                if task == "CharacterSelect":
                    if "CharacterSelect" not in self.available_tasks:
                        self.available_tasks.insert(0, task)  # 角色选择始终在前面
                else:
                    self.available_tasks.append(task)
                    
        except Exception as e:
            messagebox.showerror("错误", f"加载任务列表失败: {e}")
            # 默认任务列表
            self.available_tasks = ["CharacterSelect", "GuildInfo", "Mail", "Material", 
                                  "MonsterPark", "FastJump", "Elite", "Weekly", "PostProcess"]
    
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
        
        # 角色数量设置
        ttk.Label(group_frame, text="总角色数:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.char_count_var = tk.StringVar(value=str(self.config_data["character_count"]))
        char_count_spin = ttk.Spinbox(group_frame, from_=1, to=100, textvariable=self.char_count_var, width=10)
        char_count_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(group_frame, text="前五号角色数:").grid(row=0, column=4, sticky=tk.W, padx=(20, 10))
        self.vice_char_count_var = tk.StringVar(value=str(self.config_data["vice_character_count"]))
        vice_char_spin = ttk.Spinbox(group_frame, from_=0, to=20, textvariable=self.vice_char_count_var, width=10)
        vice_char_spin.grid(row=0, column=5, sticky=tk.W)
        
        # 任务配置区域
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1) 
        config_frame.columnconfigure(2, weight=1)
        config_frame.rowconfigure(0, weight=1)
        
        # 主号任务配置
        self.create_task_config_frame(config_frame, "主号任务配置", 0, "main_character_tasks")
        
        # 前五号任务配置  
        self.create_task_config_frame(config_frame, "前五号任务配置", 1, "five_character_tasks")
        
        # 其他号任务配置
        self.create_task_config_frame(config_frame, "其他号任务配置", 2, "other_character_tasks")
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载配置", command=self.load_config_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="应用到TaskGroup", command=self.apply_to_task_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置配置", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="启动游戏", command=self.start_game).pack(side=tk.LEFT, padx=20)
        
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
        """刷新已选任务显示"""
        listbox = getattr(self, f"{config_key}_selected_listbox")
        listbox.delete(0, tk.END)
        
        for task in self.config_data[config_key]:
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
            if task_name not in self.config_data[config_key]:
                self.config_data[config_key].append(task_name)
                
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
            if task_name in self.config_data[config_key]:
                self.config_data[config_key].remove(task_name)
                
        self.refresh_selected_tasks(config_key)
        self.log(f"已从 {config_key} 移除任务")
    
    def move_up(self, selected_listbox, config_key):
        """上移任务"""
        selection = selected_listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        index = selection[0]
        task_list = self.config_data[config_key]
        task_list[index], task_list[index-1] = task_list[index-1], task_list[index]
        
        self.refresh_selected_tasks(config_key)
        selected_listbox.selection_set(index-1)
        self.log(f"任务上移: {config_key}")
    
    def move_down(self, selected_listbox, config_key):
        """下移任务"""
        selection = selected_listbox.curselection()
        task_list = self.config_data[config_key]
        if not selection or selection[0] >= len(task_list) - 1:
            return
            
        index = selection[0]
        task_list[index], task_list[index+1] = task_list[index+1], task_list[index]
        
        self.refresh_selected_tasks(config_key)
        selected_listbox.selection_set(index+1)
        self.log(f"任务下移: {config_key}")
    
    def add_all_tasks(self, config_key):
        """添加所有可用任务"""
        self.config_data[config_key] = self.available_tasks.copy()
        self.refresh_selected_tasks(config_key)
        self.log(f"已添加所有任务到 {config_key}")
    
    def clear_tasks(self, config_key):
        """清空任务列表"""
        self.config_data[config_key] = []
        self.refresh_selected_tasks(config_key)
        self.log(f"已清空 {config_key}")
    
    def load_default_config(self, config_key):
        """加载默认配置"""
        default_configs = {
            "main_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "Material", 
                                   "MonsterPark", "Elite", "Weekly", "PostProcess", "CharacterSelect"],
            "five_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "MonsterPark", 
                                   "FastJump", "Material", "Weekly", "PostProcess", "CharacterSelect"],
            "other_character_tasks": ["CharacterSelect", "GuildInfo", "Mail", "FastJump", 
                                    "Material", "Weekly", "PostProcess", "CharacterSelect"]
        }
        
        self.config_data[config_key] = default_configs.get(config_key, [])
        self.refresh_selected_tasks(config_key)
        self.log(f"已加载 {config_key} 的默认配置")
    
    def on_task_group_changed(self, event=None):
        """TaskGroup改变时的处理"""
        try:
            new_group = int(self.task_group_var.get())
            self.current_task_group = new_group
            self.config_data["current_task_group"] = new_group
            self.log(f"切换到TaskGroup {new_group}")
        except ValueError:
            pass
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 更新配置数据
            self.config_data["character_count"] = int(self.char_count_var.get())
            self.config_data["vice_character_count"] = int(self.vice_char_count_var.get())
            self.config_data["current_task_group"] = int(self.task_group_var.get())
            self.config_data["last_updated"] = datetime.now().isoformat()
            
            # 保存到配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
                
            self.log("配置已保存到 task_config.json")
            messagebox.showinfo("成功", "配置保存成功！")
            
        except Exception as e:
            self.log(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config_data.update(loaded_config)
                    
                # 更新UI
                self.char_count_var.set(str(self.config_data["character_count"]))
                self.vice_char_count_var.set(str(self.config_data["vice_character_count"]))
                self.task_group_var.set(str(self.config_data["current_task_group"]))
                self.current_task_group = self.config_data["current_task_group"]
                
                # 刷新任务列表
                for key in ["main_character_tasks", "five_character_tasks", "other_character_tasks"]:
                    if hasattr(self, f"{key}_selected_listbox"):
                        self.refresh_selected_tasks(key)
                        
                self.log("配置加载成功")
            else:
                self.log("配置文件不存在，使用默认配置")
                
        except Exception as e:
            self.log(f"加载配置失败: {e}")
            messagebox.showerror("错误", f"加载配置失败: {e}")
    
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
    
    def apply_to_task_group(self):
        """将配置应用到TaskGroup文件"""
        try:
            task_group = self.current_task_group
            group_path = os.path.join(self.data_path, f"TaskGroup{task_group}")
            
            if not os.path.exists(group_path):
                os.makedirs(group_path)
            
            # 备份原文件
            backup_path = os.path.join(self.data_path, f"TaskGroup{task_group}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if os.path.exists(group_path):
                shutil.copytree(group_path, backup_path)
                self.log(f"已备份原TaskGroup{task_group}到 {backup_path}")
            
            # 写入新配置
            configs = [
                ("TaskListMain.json", self.config_data["main_character_tasks"]),
                ("TaskListFive.json", self.config_data["five_character_tasks"]), 
                ("TaskList.json", self.config_data["other_character_tasks"])
            ]
            
            for filename, tasks in configs:
                file_path = os.path.join(group_path, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tasks, f, ensure_ascii=False, indent=2)
                self.log(f"已更新 {filename}")
            
            messagebox.showinfo("成功", f"配置已应用到TaskGroup{task_group}！")
            
        except Exception as e:
            self.log(f"应用配置失败: {e}")
            messagebox.showerror("错误", f"应用配置失败: {e}")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "是否要重置所有配置？"):
            self.config_data = {
                "main_character_tasks": [],
                "other_character_tasks": [],
                "five_character_tasks": [],
                "current_task_group": 0,
                "character_count": 5,
                "vice_character_count": 0
            }
            
            # 重新加载UI
            self.char_count_var.set("5")
            self.vice_char_count_var.set("0")
            self.task_group_var.set("0")
            
            for key in ["main_character_tasks", "five_character_tasks", "other_character_tasks"]:
                self.refresh_selected_tasks(key)
                
            self.log("配置已重置")
    
    def start_game(self):
        """启动游戏脚本"""
        try:
            # 先保存当前配置
            self.save_config()
            
            # 应用到TaskGroup
            self.apply_to_task_group()
            
            # 启动主脚本
            import subprocess
            script_path = frozen.app_path() + "\\MSmAuto.py"
            
            # 构建启动参数
            args = ["python", script_path]
            
            # 添加参数
            args.append(f"CharacterCount={self.config_data['character_count']}")
            args.append(f"ViceCharacterCount={self.config_data['vice_character_count']}")
            args.append(f"TaskGroupIndex={self.config_data['current_task_group']}")
            
            self.log("正在启动游戏脚本...")
            self.log(f"启动参数: {' '.join(args)}")
            
            # 启动进程
            process = subprocess.Popen(args, cwd=frozen.app_path())
            
            # 最小化当前窗口
            self.root.iconify()
            
            messagebox.showinfo("启动成功", "游戏脚本已启动！\n配置窗口已最小化。")
            
        except Exception as e:
            self.log(f"启动游戏失败: {e}")
            messagebox.showerror("错误", f"启动游戏失败: {e}")
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskConfigUI()
    app.run()