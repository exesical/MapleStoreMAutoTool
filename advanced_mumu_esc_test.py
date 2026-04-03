import win32gui
import win32con
import ctypes
from ctypes import wintypes
import time
import win32api
import win32process

# Windows API常量
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SYSCHAR = 0x0103
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# 更多消息类型
WM_INPUT = 0x00FF
WM_KEYFIRST = 0x0100
WM_KEYLAST = 0x0109

def enable_advanced_uipi_bypass():
    """启用更全面的UIPI绕过"""
    print("正在启用高级UIPI绕过...")
    
    messages_to_allow = [
        WM_KEYDOWN, WM_KEYUP, WM_CHAR, WM_SYSCHAR, WM_SYSKEYDOWN, WM_SYSKEYUP,
        WM_INPUT, 0x0106, 0x0107, 0x0108, 0x0109,  # 更多键盘消息
        0x0200, 0x0201, 0x0202, 0x0203, 0x0204, 0x0205, 0x0206, 0x0207, 0x0208, 0x0209, 0x020A, 0x020B, 0x020C, 0x020D, 0x020E  # 鼠标消息
    ]
    
    success_count = 0
    for msg in messages_to_allow:
        try:
            # MSGFLT_ADD = 1, MSGFLT_ALLOW = 1 
            result1 = ctypes.windll.user32.ChangeWindowMessageFilter(msg, 1)
            # 也尝试ChangeWindowMessageFilterEx
            try:
                result2 = ctypes.windll.user32.ChangeWindowMessageFilterEx(win32gui.GetDesktopWindow(), msg, 1, None)
            except:
                result2 = True  # 如果函数不存在就忽略
            
            if result1 or result2:
                success_count += 1
                print(f"  ✅ 消息 0x{msg:04X}")
            else:
                print(f"  ❌ 消息 0x{msg:04X}")
        except Exception as e:
            print(f"  ❌ 消息 0x{msg:04X}: {e}")
    
    print(f"高级UIPI绕过设置完成: {success_count}/{len(messages_to_allow)} 成功")
    return success_count > 0

def get_process_info(hwnd):
    """获取窗口的进程信息"""
    try:
        thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
        process_handle = win32api.OpenProcess(0x0400, False, process_id)  # PROCESS_QUERY_INFORMATION
        process_name = win32process.GetModuleFileNameEx(process_handle, 0)
        win32api.CloseHandle(process_handle)
        return {
            "process_id": process_id,
            "thread_id": thread_id,
            "process_name": process_name.split("\\")[-1]
        }
    except Exception as e:
        return {"error": str(e)}

def find_mumu_windows():
    """查找所有MuMu相关窗口"""
    print("正在查找MuMu窗口...")
    
    def enum_windows_proc(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if ("MuMu安卓设备" in window_text or 
                "MuMu模拟器" in window_text or
                (window_text.startswith("MuMu") and "Visual Studio Code" not in window_text)):
                process_info = get_process_info(hwnd)
                windows.append((hwnd, window_text, process_info))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_proc, windows)
    
    if not windows:
        print("❌ 未找到MuMu窗口")
        return None, None
        
    print(f"找到 {len(windows)} 个MuMu窗口:")
    for i, (hwnd, title, process_info) in enumerate(windows):
        print(f"  {i+1}. {title} (Handle: {hwnd})")
        if "error" not in process_info:
            print(f"     进程: {process_info['process_name']} (PID: {process_info['process_id']})")
    
    # 选择"MuMu安卓设备"窗口
    main_hwnd = None
    for hwnd, title, process_info in windows:
        if "MuMu安卓设备" in title:
            main_hwnd = hwnd
            main_title = title
            main_process_info = process_info
            break
    
    if not main_hwnd:
        main_hwnd = windows[0][0]
        main_title = windows[0][1]
        main_process_info = windows[0][2]
    
    print(f"\n使用主窗口: {main_title} (Handle: {main_hwnd})")
    if "error" not in main_process_info:
        print(f"进程信息: {main_process_info['process_name']} (PID: {main_process_info['process_id']})")
    
    # 查找所有子窗口
    child_windows = []
    def enum_child_proc(hwnd, lParam):
        child_windows.append(hwnd)
        return True
    
    win32gui.EnumChildWindows(main_hwnd, enum_child_proc, 0)
    
    print(f"找到 {len(child_windows)} 个子窗口:")
    keyboard_handles = []  # 可能的键盘目标
    
    for child in child_windows:
        try:
            class_name = win32gui.GetClassName(child)
            window_text = win32gui.GetWindowText(child)
            rect = win32gui.GetWindowRect(child)
            visible = win32gui.IsWindowVisible(child)
            enabled = win32gui.IsWindowEnabled(child)
            
            print(f"  子窗口: {class_name} (Handle: {child})")
            print(f"    标题: '{window_text}'")
            print(f"    位置: {rect}")
            print(f"    可见: {visible}, 启用: {enabled}")
            
            # 收集可能的键盘目标
            if "nemuwin" in class_name.lower():
                keyboard_handles.append(("nemuwin", child))
                print(f"    ✅ 找到nemuwin窗口")
            elif "qt" in class_name.lower() and visible:
                keyboard_handles.append(("qt", child))
                print(f"    ⚠️ 找到Qt窗口")
            elif visible and enabled and (rect[2] - rect[0]) * (rect[3] - rect[1]) > 10000:  # 大窗口
                keyboard_handles.append(("large", child))
                print(f"    ⚠️ 找到大窗口")
            
        except Exception as e:
            print(f"  ❌ 获取子窗口信息失败: {e}")
    
    # 选择最佳键盘目标
    if keyboard_handles:
        # 优先选择nemuwin，然后是大窗口，最后是Qt窗口
        keyboard_handles.sort(key=lambda x: {"nemuwin": 0, "large": 1, "qt": 2}.get(x[0], 3))
        keyboard_handle = keyboard_handles[0][1]
        print(f"\n✅ 选择键盘目标: {keyboard_handles[0][0]} 类型 (Handle: {keyboard_handle})")
    else:
        keyboard_handle = main_hwnd
        print(f"\n⚠️ 使用主窗口作为键盘目标: (Handle: {keyboard_handle})")
    
    return main_hwnd, keyboard_handle

def send_esc_with_different_methods(keyboard_handle):
    """使用多种方法发送ESC按键"""
    print(f"\n正在向窗口 {keyboard_handle} 发送ESC按键...")
    
    virtual_key = 27  # VK_ESCAPE
    scan_code = 1     # ESC的扫描码
    
    success_methods = []
    
    # 方法1: SendMessage with different lParam variations
    print("  尝试方法1: SendMessage (多种lParam)")
    lParam_variations = [
        1 | (scan_code << 16),                    # 标准格式
        0x00010001,                               # 简化格式
        1,                                        # 最简格式
        scan_code << 16,                          # 只有扫描码
        0x01010001,                               # 修改版本
    ]
    
    for i, lParam in enumerate(lParam_variations):
        try:
            result_down = ctypes.windll.user32.SendMessageW(keyboard_handle, WM_KEYDOWN, virtual_key, lParam)
            result_up = ctypes.windll.user32.SendMessageW(keyboard_handle, WM_KEYUP, virtual_key, lParam | 0xC0000000)
            
            if result_down != 0 or result_up != 0:
                print(f"    ✅ SendMessage 变体 {i+1} 成功 (down: {result_down}, up: {result_up})")
                success_methods.append(f"SendMessage-{i+1}")
            else:
                print(f"    ⚠️ SendMessage 变体 {i+1} 返回0")
        except Exception as e:
            print(f"    ❌ SendMessage 变体 {i+1} 异常: {e}")
    
    # 方法2: PostMessage variations
    print("  尝试方法2: PostMessage (多种变体)")
    for i, lParam in enumerate(lParam_variations[:3]):  # 只测试前3种
        try:
            result_down = ctypes.windll.user32.PostMessageW(keyboard_handle, WM_KEYDOWN, virtual_key, lParam)
            result_up = ctypes.windll.user32.PostMessageW(keyboard_handle, WM_KEYUP, virtual_key, lParam | 0xC0000000)
            
            if result_down and result_up:
                print(f"    ✅ PostMessage 变体 {i+1} 成功")
                success_methods.append(f"PostMessage-{i+1}")
                time.sleep(0.1)  # 给异步消息一点时间
            else:
                print(f"    ❌ PostMessage 变体 {i+1} 失败")
        except Exception as e:
            print(f"    ❌ PostMessage 变体 {i+1} 异常: {e}")
    
    # 方法3: 尝试发送到所有相关窗口
    print("  尝试方法3: 多窗口发送")
    try:
        # 获取父窗口
        parent_hwnd = win32gui.GetParent(keyboard_handle)
        if parent_hwnd != 0:
            print(f"    向父窗口发送: {parent_hwnd}")
            result = ctypes.windll.user32.SendMessageW(parent_hwnd, WM_KEYDOWN, virtual_key, 0x00010001)
            ctypes.windll.user32.SendMessageW(parent_hwnd, WM_KEYUP, virtual_key, 0xC0010001)
            if result != 0:
                success_methods.append("Parent-SendMessage")
        
        # 获取焦点窗口
        focus_hwnd = win32gui.GetFocus()
        if focus_hwnd != 0 and focus_hwnd != keyboard_handle:
            print(f"    向焦点窗口发送: {focus_hwnd}")
            result = ctypes.windll.user32.SendMessageW(focus_hwnd, WM_KEYDOWN, virtual_key, 0x00010001)
            ctypes.windll.user32.SendMessageW(focus_hwnd, WM_KEYUP, virtual_key, 0xC0010001)
            if result != 0:
                success_methods.append("Focus-SendMessage")
    except Exception as e:
        print(f"    多窗口发送异常: {e}")
    
    # 方法4: keybd_event (全局)
    print("  尝试方法4: keybd_event (前台切换)")
    try:
        original_window = ctypes.windll.user32.GetForegroundWindow()
        
        # 尝试激活窗口
        result = ctypes.windll.user32.SetForegroundWindow(keyboard_handle)
        if not result:
            # 如果直接设置失败，尝试通过Alt+Tab方式
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # Alt down
            ctypes.windll.user32.SetForegroundWindow(keyboard_handle)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # Alt up
        
        time.sleep(0.3)  # 等待窗口激活
        
        # 发送ESC
        ctypes.windll.user32.keybd_event(virtual_key, scan_code, 0, 0)  # 按下
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(virtual_key, scan_code, 2, 0)  # 释放
        
        time.sleep(0.3)
        
        # 恢复原窗口
        if original_window != 0:
            ctypes.windll.user32.SetForegroundWindow(original_window)
        
        print("    ✅ keybd_event 执行完成")
        success_methods.append("keybd_event")
        
    except Exception as e:
        print(f"    ❌ keybd_event 异常: {e}")
    
    return success_methods

def main():
    """主函数"""
    print("=== 高级MuMu ESC按键测试 ===\n")
    
    # 第1步：启用高级UIPI绕过
    if not enable_advanced_uipi_bypass():
        print("❌ UIPI绕过设置失败，但继续尝试...")
    
    print()
    
    # 第2步：查找MuMu窗口
    main_hwnd, keyboard_handle = find_mumu_windows()
    if not main_hwnd:
        print("❌ 无法找到MuMu窗口，测试终止")
        return
    
    # 第3步：等待用户确认
    print(f"\n将向窗口 {keyboard_handle} 发送ESC按键")
    print("请确保MuMu模拟器正在运行游戏，然后按Enter继续...")
    input()
    
    # 第4步：发送ESC按键
    success_methods = send_esc_with_different_methods(keyboard_handle)
    
    # 第5步：报告结果
    print(f"\n=== 测试结果 ===")
    if success_methods:
        print(f"✅ 成功的方法: {', '.join(success_methods)}")
        print("请检查MuMu中的游戏是否收到了ESC按键。")
    else:
        print("❌ 所有方法都失败了。")
        print("可能的原因：")
        print("1. MuMu使用了特殊的输入处理机制")
        print("2. 需要管理员权限")
        print("3. 游戏本身不响应ESC键")
        print("4. 窗口句柄不正确")
    
    print("\n建议：")
    print("1. 尝试手动按ESC键看游戏是否响应")
    print("2. 检查MuMu设置中的键盘映射")
    print("3. 尝试以管理员权限运行此脚本")

if __name__ == "__main__":
    main()