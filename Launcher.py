#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冒险岛M自动助手启动器
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
from FrozenPath import frozen

# 移除停止脚本相关的全局变量

def main():
    """主函数 - 显示启动选择界面"""
    root = tk.Tk()
    root.title("冒险岛M自动助手启动器")
    root.geometry("450x350")  # 恢复原来的高度
    root.resizable(False, False)
    
    # 设置窗口居中
    root.eval('tk::PlaceWindow . center')
    
    # 标题
    title_label = tk.Label(root, text="冒险岛M自动助手", font=("微软雅黑", 18, "bold"), fg="blue")
    title_label.pack(pady=20)
    
    # 版本信息
    version_label = tk.Label(root, text="v2.0 - 带任务配置UI版本", font=("微软雅黑", 10))
    version_label.pack(pady=5)
    
    # 配置参数框架
    config_frame = tk.Frame(root)
    config_frame.pack(pady=15)
    
    # 角色索引
    index_label = tk.Label(config_frame, text="当前角色索引:", font=("微软雅黑", 12))
    index_label.grid(row=0, column=0, padx=5, sticky=tk.W)
    
    index_var = tk.StringVar()
    index_entry = tk.Entry(config_frame, textvariable=index_var, font=("微软雅黑", 12), width=10)
    index_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
    
    # 任务组选择
    taskgroup_label = tk.Label(config_frame, text="任务组:", font=("微软雅黑", 12))
    taskgroup_label.grid(row=0, column=2, padx=(20, 5), sticky=tk.W)
    
    taskgroup_var = tk.StringVar(value="0")
    taskgroup_combo = tk.ttk.Combobox(config_frame, textvariable=taskgroup_var, 
                                     values=["0", "1", "2", "3", "4", "5", "6"],
                                     width=8, font=("微软雅黑", 12), state="readonly")
    taskgroup_combo.grid(row=0, column=3, padx=5, sticky=tk.W)
    
    # 从RecordFile加载初始值
    load_record_file_value(index_var)
    
    # 按钮框架
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    # 配置任务按钮
    config_btn = tk.Button(button_frame, text="📋 配置任务", 
                          font=("微软雅黑", 14), 
                          width=15, height=2,
                          bg="#4CAF50", fg="white",
                          command=lambda: launch_config_ui_with_params(index_var.get(), taskgroup_var.get()))
    config_btn.pack(pady=8)
    
    # 直接启动按钮
    direct_btn = tk.Button(button_frame, text="🚀 直接启动", 
                          font=("微软雅黑", 14), 
                          width=15, height=2,
                          bg="#2196F3", fg="white",
                          command=lambda: launch_main_script_with_params(index_var.get(), taskgroup_var.get()))
    direct_btn.pack(pady=8)
    
    # 说明文字
    info_text = """使用说明:
• 角色索引值: 从当前日期RecordFile文件中读取，启动时会自动保存
• 任务组: 选择要使用的任务组配置（0-6）
• 配置任务: 打开任务配置界面，自动切换到指定任务组
• 直接启动: 使用指定任务组的配置直接运行

注意: 请确保游戏模拟器已启动并处于角色选择界面"""
    
    info_label = tk.Label(root, text=info_text, 
                         font=("微软雅黑", 9), 
                         justify=tk.LEFT,
                         fg="gray")
    info_label.pack(pady=20)
    
    root.mainloop()

def get_record_file_path():
    """获取当前日期对应的RecordFile路径"""
    today = datetime.now()
    filename = today.strftime('RecordFile%y%m%d')
    return os.path.join(frozen.app_path(), filename)

def load_record_file_value(index_var):
    """从RecordFile加载角色索引值"""
    try:
        record_path = get_record_file_path()
        if os.path.exists(record_path):
            with open(record_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.isdigit():
                    index_var.set(content)
                else:
                    index_var.set("0")
        else:
            index_var.set("0")
    except Exception as e:
        print(f"加载RecordFile失败: {e}")
        index_var.set("0")

def save_record_file_value(index_value):
    """保存角色索引值到RecordFile"""
    try:
        # 验证输入值
        if not index_value.isdigit():
            index_value = "0"
        
        record_path = get_record_file_path()
        with open(record_path, 'w', encoding='utf-8') as f:
            f.write(index_value)
        return True
    except Exception as e:
        print(f"保存RecordFile失败: {e}")
        return False

def launch_config_ui_with_index(index_value):
    """启动配置UI并保存索引值"""
    # 保存索引值到RecordFile
    save_record_file_value(index_value)
    
    try:
        # 直接导入并运行TaskConfigUI模块
        import TaskConfigUI
        
        # 创建新的独立窗口
        config_window = tk.Toplevel()
        config_window.withdraw()  # 先隐藏窗口
        
        # 创建TaskConfigUI实例，传入新窗口作为父窗口
        app = TaskConfigUI.TaskConfigUI(parent_window=config_window)
        config_window.deiconify()  # 显示窗口
        
    except Exception as e:
        messagebox.showerror("错误", f"启动配置UI失败: {e}")

def launch_main_script_with_index(index_value):
    """直接启动主脚本并保存索引值"""
    # 保存索引值到RecordFile
    if save_record_file_value(index_value):
        try:
            # 直接导入并运行MSmAuto
            import threading
            
            try:
                import MSmAuto
                # 在新线程中运行MSmAuto
                main_thread = threading.Thread(target=MSmAuto.main)
                main_thread.daemon = True
                main_thread.start()
                messagebox.showinfo("启动成功", f"游戏脚本已启动！\n角色索引值已保存: {index_value}")
            except ImportError:
                # 如果是开发环境，使用subprocess
                script_path = os.path.join(os.path.dirname(__file__), "MSmAuto.py")
                if os.path.exists(script_path):
                    subprocess.Popen([sys.executable, script_path])
                    messagebox.showinfo("启动成功", f"游戏脚本已启动！\n角色索引值已保存: {index_value}")
                else:
                    messagebox.showerror("错误", "MSmAuto.py 文件未找到！")
                
        except Exception as e:
            messagebox.showerror("错误", f"启动主脚本失败: {e}")
    else:
        messagebox.showerror("错误", "保存角色索引值失败！")

def launch_config_ui_with_params(index_value, taskgroup_value):
    """启动配置UI并保存参数"""
    # 保存索引值到RecordFile
    save_record_file_value(index_value)
    
    try:
        # 直接导入并运行TaskConfigUI模块
        import TaskConfigUI
        
        # 创建新的独立窗口
        config_window = tk.Toplevel()
        config_window.withdraw()  # 先隐藏窗口
        
        # 创建TaskConfigUI实例，传入新窗口作为父窗口
        app = TaskConfigUI.TaskConfigUI(parent_window=config_window)
        
        # 设置指定的任务组
        app.task_group_var.set(taskgroup_value)
        app.on_task_group_changed()  # 触发任务组切换
        
        config_window.deiconify()  # 显示窗口
        
    except Exception as e:
        messagebox.showerror("错误", f"启动配置UI失败: {e}")

def launch_main_script_with_params(index_value, taskgroup_value):
    """直接启动主脚本并保存参数"""
    # 保存索引值到RecordFile
    if save_record_file_value(index_value):
        try:
            # 直接导入并运行MSmAuto
            import threading
            
            try:
                # 设置任务组环境变量或参数
                import sys
                sys.argv.append(f"TaskGroupIndex={taskgroup_value}")
                
                import MSmAuto
                # 在新线程中运行MSmAuto
                main_thread = threading.Thread(target=MSmAuto.main)
                main_thread.daemon = True
                main_thread.start()
                
                messagebox.showinfo("启动成功", f"游戏脚本已启动！\n角色索引：{index_value}\n任务组：{taskgroup_value}")
            except ImportError:
                # 如果是开发环境，使用subprocess
                script_path = os.path.join(os.path.dirname(__file__), "MSmAuto.py")
                if os.path.exists(script_path):
                    subprocess.Popen([sys.executable, script_path, f"TaskGroupIndex={taskgroup_value}"])
                    messagebox.showinfo("启动成功", f"游戏脚本已启动！\n角色索引：{index_value}\n任务组：{taskgroup_value}")
                else:
                    messagebox.showerror("错误", "MSmAuto.py 文件未找到！")
                
        except Exception as e:
            messagebox.showerror("错误", f"启动主脚本失败: {e}")
    else:
        messagebox.showerror("错误", "保存角色索引值失败！")

def launch_config_ui():
    """启动配置UI (兼容性保留)"""
    launch_config_ui_with_index("0")

def launch_main_script():
    """直接启动主脚本 (兼容性保留)"""
    launch_main_script_with_index("0")

if __name__ == "__main__":
    main()
