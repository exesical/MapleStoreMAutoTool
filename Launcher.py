#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冒险岛M自动助手启动器
"""

import os
import sys
import subprocess
from tkinter import messagebox
import tkinter as tk
from datetime import datetime
from FrozenPath import frozen

def main():
    """主函数 - 显示启动选择界面"""
    root = tk.Tk()
    root.title("冒险岛M自动助手启动器")
    root.geometry("450x350")
    root.resizable(False, False)
    
    # 设置窗口居中
    root.eval('tk::PlaceWindow . center')
    
    # 标题
    title_label = tk.Label(root, text="冒险岛M自动助手", font=("微软雅黑", 18, "bold"), fg="blue")
    title_label.pack(pady=20)
    
    # 版本信息
    version_label = tk.Label(root, text="v2.0 - 带任务配置UI版本", font=("微软雅黑", 10))
    version_label.pack(pady=5)
    
    # 角色索引输入框架
    index_frame = tk.Frame(root)
    index_frame.pack(pady=15)
    
    index_label = tk.Label(index_frame, text="当前跑到哪个角色了:", font=("微软雅黑", 12))
    index_label.pack(side=tk.LEFT, padx=5)
    
    # 创建StringVar来管理输入框的值
    index_var = tk.StringVar()
    index_entry = tk.Entry(index_frame, textvariable=index_var, font=("微软雅黑", 12), width=10)
    index_entry.pack(side=tk.LEFT, padx=5)
    
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
                          command=lambda: launch_config_ui_with_index(index_var.get()))
    config_btn.pack(pady=8)
    
    # 直接启动按钮
    direct_btn = tk.Button(button_frame, text="🚀 直接启动", 
                          font=("微软雅黑", 14), 
                          width=15, height=2,
                          bg="#2196F3", fg="white",
                          command=lambda: launch_main_script_with_index(index_var.get()))
    direct_btn.pack(pady=8)
    
    # 说明文字
    info_text = """
使用说明:
• 角色索引值: 从当前日期RecordFile文件中读取，启动时会自动保存
• 配置任务: 打开任务配置界面，可自定义每个角色的任务
• 直接启动: 使用默认或已保存的配置直接运行

注意: 请确保游戏模拟器已启动并处于角色选择界面
"""
    
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
        script_path = os.path.join(os.path.dirname(__file__), "TaskConfigUI.py")
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showerror("错误", "TaskConfigUI.py 文件未找到！")
    except Exception as e:
        messagebox.showerror("错误", f"启动配置UI失败: {e}")

def launch_main_script_with_index(index_value):
    """直接启动主脚本并保存索引值"""
    # 保存索引值到RecordFile
    if save_record_file_value(index_value):
        try:
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

def launch_config_ui():
    """启动配置UI (兼容性保留)"""
    launch_config_ui_with_index("0")

def launch_main_script():
    """直接启动主脚本 (兼容性保留)"""
    launch_main_script_with_index("0")

if __name__ == "__main__":
    main()