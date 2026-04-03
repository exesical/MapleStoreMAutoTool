import win32gui
import win32con
import ctypes
from ctypes import wintypes
import time
import win32api
import win32process

def analyze_mumu_input_architecture():
    """分析MuMu的输入架构"""
    print("=== MuMu输入架构分析 ===\n")
    
    # 1. 找到MuMu窗口（跳过进程枚举）
    print("查找MuMu窗口...")
    
    # 2. 检查是否有键盘钩子
    print("\n检查系统键盘钩子...")
    try:
        # 尝试安装一个测试钩子来检查是否有冲突
        def low_level_keyboard_proc(nCode, wParam, lParam):
            return ctypes.windll.user32.CallNextHookExW(None, nCode, wParam, lParam)
        
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        keyboard_proc = HOOKPROC(low_level_keyboard_proc)
        
        hook = ctypes.windll.user32.SetWindowsHookExW(13, keyboard_proc, ctypes.windll.kernel32.GetModuleHandleW(None), 0)  # WH_KEYBOARD_LL
        if hook:
            print("  ✅ 能够安装低级键盘钩子")
            ctypes.windll.user32.UnhookWindowsHookEx(hook)
        else:
            print("  ❌ 无法安装低级键盘钩子")
    except Exception as e:
        print(f"  ❌ 键盘钩子检查异常: {e}")
    
    # 3. 检查MuMu窗口的详细属性
    print("\n详细窗口分析...")
    mumu_main = win32gui.FindWindow(None, "MuMu安卓设备")
    if mumu_main:
        print(f"主窗口句柄: {mumu_main}")
        
        # 窗口类名和样式
        class_name = win32gui.GetClassName(mumu_main)
        window_info = win32gui.GetWindowInfo(mumu_main)
        print(f"窗口类名: {class_name}")
        print(f"窗口样式: 0x{window_info[2]:08X}")
        print(f"扩展样式: 0x{window_info[3]:08X}")
        
        # 进程信息
        thread_id, process_id = win32process.GetWindowThreadProcessId(mumu_main)
        print(f"进程ID: {process_id}, 线程ID: {thread_id}")
        
        # 检查窗口消息队列
        queue_status = ctypes.windll.user32.GetQueueStatus(0x00FF)  # QS_ALLINPUT
        print(f"消息队列状态: 0x{queue_status:08X}")
        
        # 子窗口详细信息
        print("\n子窗口详细分析:")
        child_windows = []
        win32gui.EnumChildWindows(mumu_main, lambda hwnd, param: param.append(hwnd), child_windows)
        
        for child in child_windows:
            try:
                child_class = win32gui.GetClassName(child)
                child_text = win32gui.GetWindowText(child)
                child_rect = win32gui.GetWindowRect(child)
                child_visible = win32gui.IsWindowVisible(child)
                child_enabled = win32gui.IsWindowEnabled(child)
                
                print(f"  子窗口: {child_class} (Handle: {child})")
                print(f"    标题: '{child_text}'")
                print(f"    可见: {child_visible}, 启用: {child_enabled}")
                print(f"    区域: {child_rect}")
                
                # 尝试获取窗口属性
                try:
                    child_style = win32gui.GetWindowLong(child, -16)  # GWL_STYLE
                    child_ex_style = win32gui.GetWindowLong(child, -20)  # GWL_EXSTYLE
                    print(f"    样式: 0x{child_style:08X}, 扩展: 0x{child_ex_style:08X}")
                except:
                    pass
                
                print()
            except Exception as e:
                print(f"    获取子窗口信息失败: {e}")
    
    # 4. 测试不同的消息发送方式
    print("测试消息发送响应:")
    if mumu_main:
        # 测试WM_CHAR消息
        print("  测试WM_CHAR消息...")
        result_char = ctypes.windll.user32.SendMessageW(mumu_main, 0x0102, ord('A'), 0)
        print(f"    WM_CHAR结果: {result_char}")
        
        # 测试WM_SYSCOMMAND
        print("  测试WM_SYSCOMMAND...")
        result_syscmd = ctypes.windll.user32.SendMessageW(mumu_main, 0x0112, 0xF020, 0)  # SC_MINIMIZE
        print(f"    WM_SYSCOMMAND结果: {result_syscmd}")
        
        # 测试自定义消息
        print("  测试自定义消息...")
        custom_msg = 0x8000  # WM_USER
        result_custom = ctypes.windll.user32.SendMessageW(mumu_main, custom_msg, 123, 456)
        print(f"    自定义消息结果: {result_custom}")
    
    # 5. 检查是否有输入法或其他输入处理程序
    print("\n检查输入处理程序...")
    try:
        # 获取当前输入法
        current_hkl = ctypes.windll.user32.GetKeyboardLayout(0)
        print(f"当前键盘布局: 0x{current_hkl:08X}")
        
        # 检查是否有IME
        ime_window = ctypes.windll.user32.ImmGetDefaultIMEWnd(mumu_main)
        if ime_window:
            print(f"IME窗口: {ime_window}")
        else:
            print("无IME窗口")
    except Exception as e:
        print(f"输入法检查异常: {e}")
    
    return mumu_main

def test_alternative_methods(mumu_main):
    """测试替代输入方法"""
    print("\n=== 测试替代输入方法 ===")
    
    if not mumu_main:
        print("❌ 没有MuMu主窗口")
        return
    
    # 方法1: 模拟鼠标点击ESC按钮位置（如果游戏有ESC按钮）
    print("方法1: 查找并点击ESC相关UI元素...")
    # 这需要OCR或图像识别，这里只是示例
    print("  需要OCR或图像识别来定位ESC按钮")
    
    # 方法2: 发送Alt+F4（通用退出）
    print("方法2: 发送Alt+F4...")
    try:
        original_window = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SetForegroundWindow(mumu_main)
        time.sleep(0.2)
        
        # Alt down
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # VK_MENU (Alt)
        time.sleep(0.02)
        # F4 down
        ctypes.windll.user32.keybd_event(0x73, 0, 0, 0)  # VK_F4
        time.sleep(0.02)
        # F4 up
        ctypes.windll.user32.keybd_event(0x73, 0, 2, 0)
        time.sleep(0.02)
        # Alt up
        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
        
        time.sleep(0.2)
        if original_window:
            ctypes.windll.user32.SetForegroundWindow(original_window)
        
        print("  ✅ Alt+F4发送完成")
    except Exception as e:
        print(f"  ❌ Alt+F4异常: {e}")
    
    # 方法3: 发送Ctrl+C（可能触发某些游戏功能）
    print("方法3: 发送Ctrl+C...")
    try:
        original_window = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SetForegroundWindow(mumu_main)
        time.sleep(0.2)
        
        # Ctrl down
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # VK_CONTROL
        time.sleep(0.02)
        # C down
        ctypes.windll.user32.keybd_event(0x43, 0, 0, 0)  # 'C'
        time.sleep(0.02)
        # C up
        ctypes.windll.user32.keybd_event(0x43, 0, 2, 0)
        time.sleep(0.02)
        # Ctrl up
        ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)
        
        time.sleep(0.2)
        if original_window:
            ctypes.windll.user32.SetForegroundWindow(original_window)
        
        print("  ✅ Ctrl+C发送完成")
    except Exception as e:
        print(f"  ❌ Ctrl+C异常: {e}")

def main():
    """主函数"""
    print("开始分析MuMu的输入架构...")
    input("按Enter开始...")
    
    mumu_main = analyze_mumu_input_architecture()
    
    print("\n" + "="*50)
    print("现在测试一些替代方法...")
    input("按Enter继续测试替代方法...")
    
    test_alternative_methods(mumu_main)
    
    print(f"\n=== 分析总结 ===")
    print("基于以上分析，可能的解决方案：")
    print("1. 使用ADB命令直接与安卓系统通信")
    print("2. 使用图像识别定位游戏UI元素并点击")
    print("3. 研究MuMu的键盘映射配置文件")
    print("4. 使用硬件级输入注入（如DD驱动）")
    print("5. 尝试其他按键组合（可能某些按键能工作）")
    
    print("\n观察Alt+F4和Ctrl+C是否在MuMu中产生了任何反应...")

if __name__ == "__main__":
    main()