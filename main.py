#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger

import threading
import os
import sys
from functools import partial

# Android specific imports
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    from plyer import screenshot
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    ANDROID = True
except ImportError:
    ANDROID = False
    Logger.info("MapleAuto: Running on non-Android platform")

# Import our modified state classes
from android_state import AndroidMSmState, AndroidScreenHit, run_android_automation, IS_ANDROID, APP_PATH

class MapleAutoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_thread = None
        self.is_running = False
        self.state_table = {}
        self.current_state = None
        self.log_text = ""
        
    def build(self):
        self.title = "冒险岛M自动助手"
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='冒险岛M自动助手',
            size_hint_y=0.1,
            font_size='20sp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Configuration panel
        config_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        
        # Character count input
        char_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        char_layout.add_widget(Label(text='角色数量:', size_hint_x=0.3))
        self.char_count_input = TextInput(
            text='5', 
            multiline=False, 
            size_hint_x=0.7,
            input_filter='int'
        )
        char_layout.add_widget(self.char_count_input)
        config_layout.add_widget(char_layout)
        
        # Task type dropdown
        task_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        task_layout.add_widget(Label(text='任务类型:', size_hint_x=0.3))
        
        self.task_dropdown = DropDown()
        task_options = [
            ('日常副本', 'daily'),
            ('材料副本', 'material'),
            ('精英副本', 'elite'),
            ('怪物公园', 'monster_park'),
            ('快速副本', 'fast_jump'),
            ('完整流程', 'full_process')
        ]
        
        for text, value in task_options:
            btn = Button(text=text, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn, v=value: self.select_task(v))
            self.task_dropdown.add_widget(btn)
            
        self.task_button = Button(text='选择任务类型', size_hint_x=0.7)
        self.task_button.bind(on_release=self.task_dropdown.open)
        self.task_dropdown.bind(on_select=lambda instance, x: setattr(self.task_button, 'text', x))
        
        task_layout.add_widget(self.task_button)
        config_layout.add_widget(task_layout)
        
        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=10)
        
        self.start_button = Button(
            text='开始自动化',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.start_button.bind(on_press=self.start_automation)
        
        self.stop_button = Button(
            text='停止自动化',
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True
        )
        self.stop_button.bind(on_press=self.stop_automation)
        
        self.permission_button = Button(
            text='申请权限',
            background_color=(0.2, 0.2, 0.8, 1)
        )
        self.permission_button.bind(on_press=self.request_permissions)
        
        button_layout.add_widget(self.start_button)
        button_layout.add_widget(self.stop_button)
        button_layout.add_widget(self.permission_button)
        
        config_layout.add_widget(button_layout)
        main_layout.add_widget(config_layout)
        
        # Progress bar
        self.progress_bar = ProgressBar(size_hint_y=0.05, max=100)
        main_layout.add_widget(self.progress_bar)
        
        # Log area
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.55)
        log_layout.add_widget(Label(text='运行日志:', size_hint_y=0.1))
        
        self.log_label = Label(
            text='等待开始...',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        log_layout.add_widget(scroll)
        
        main_layout.add_widget(log_layout)
        
        # Initialize Android specific features
        if ANDROID:
            Clock.schedule_once(self.check_permissions, 1)
            
        return main_layout
    
    def select_task(self, task_type):
        self.selected_task = task_type
        self.task_dropdown.dismiss()
        
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(0.6, 0.4))
        popup.open()
        
    def update_log(self, message):
        """Update log display in UI thread"""
        def _update(dt):
            self.log_text += f"\n{message}"
            # Keep only last 1000 characters to prevent memory issues
            if len(self.log_text) > 1000:
                self.log_text = self.log_text[-1000:]
            self.log_label.text = self.log_text
            self.log_label.text_size = (self.log_label.parent.width, None)
            
        Clock.schedule_once(_update, 0)
        
    def update_progress(self, progress):
        """Update progress bar in UI thread"""
        def _update(dt):
            self.progress_bar.value = progress
        Clock.schedule_once(_update, 0)
        
    def check_permissions(self, dt):
        """Check if we have necessary permissions"""
        if not ANDROID:
            return
            
        self.update_log("检查Android权限...")
        
        # Check if accessibility service is enabled
        try:
            # This is a simplified check - in real implementation you'd check properly
            self.update_log("请手动开启无障碍服务权限")
        except Exception as e:
            self.update_log(f"权限检查失败: {e}")
            
    def request_permissions(self, instance):
        """Request necessary Android permissions"""
        if not ANDROID:
            self.show_popup("提示", "当前运行环境不是Android")
            return
            
        self.update_log("申请Android权限...")
        
        try:
            # Request basic permissions
            permissions = [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.SYSTEM_ALERT_WINDOW
            ]
            request_permissions(permissions)
            
            # Open accessibility settings
            intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            PythonActivity.mActivity.startActivity(intent)
            
            self.update_log("请在设置中开启无障碍服务权限")
            
        except Exception as e:
            self.update_log(f"权限申请失败: {e}")
            
    def start_automation(self, instance):
        """Start the automation process"""
        if self.is_running:
            return
            
        if not hasattr(self, 'selected_task'):
            self.show_popup("错误", "请先选择任务类型")
            return
            
        self.is_running = True
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.log_text = ""

        # Start automation in separate thread
        self.auto_thread = threading.Thread(target=self.run_automation)
        self.auto_thread.daemon = True
        self.auto_thread.start()

        self.update_log("开始自动化...")

    def stop_automation(self, instance):
        """Stop the automation process"""
        self.is_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.update_log("停止自动化...")

    def run_automation(self):
        """Main automation logic running in separate thread"""
        try:
            char_count = int(self.char_count_input.text) if self.char_count_input.text else 1

            self.update_log(f"开始处理 {char_count} 个角色")
            self.update_log(f"任务类型: {self.selected_task}")

            # ---- 映射 UI 任务类型到 run_android_automation 参数 ----
            task_group = 0
            b_post_default = True
            b_post_weekly = False
            b_post_auto_change = False
            b_post_organize = False
            b_post_skip = False
            b_post_additional = False
            fast_jump_type = 0
            vice_count = 0

            if self.selected_task == 'daily':
                task_group = 0
            elif self.selected_task == 'material':
                task_group = 1
            elif self.selected_task == 'elite':
                task_group = 2
            elif self.selected_task == 'monster_park':
                task_group = 3
            elif self.selected_task == 'fast_jump':
                task_group = 4
                fast_jump_type = 1
            elif self.selected_task == 'full_process':
                task_group = 0
                b_post_default = True
                b_post_weekly = True
                b_post_auto_change = True
                b_post_organize = True
                b_post_additional = True

            self.update_log("启动安卓自动化引擎...")

            # 调用 android_state 的自动化主流程
            run_android_automation(
                task_group_index=task_group,
                character_count=char_count,
                vice_character_count=vice_count,
                b_post_process_default=b_post_default,
                b_post_process_weekly_reward=b_post_weekly,
                b_post_process_auto_change=b_post_auto_change,
                b_post_process_organize_package=b_post_organize,
                b_post_process_skip_commission=b_post_skip,
                b_post_process_additional_material=b_post_additional,
                fast_jump_type=fast_jump_type,
                progress_callback=self.update_progress,
                log_callback=self.update_log
            )

            self.update_progress(100)
            self.update_log("所有任务完成!")

        except Exception as e:
            self.update_log(f"自动化过程出错: {e}")
            import traceback
            self.update_log(traceback.format_exc())

        finally:
            # Reset UI state
            def reset_ui(dt):
                self.is_running = False
                self.start_button.disabled = False
                self.stop_button.disabled = True
            Clock.schedule_once(reset_ui, 0)


if __name__ == '__main__':
    MapleAutoApp().run()