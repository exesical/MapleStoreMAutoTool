import win32gui
import win32con
import ctypes
from ctypes import wintypes
import time

# Windows API常量
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SYSCHAR = 0x0103
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

def enable_uipi_bypass():
    """启用UIPI绕过，允许键盘消息跨进程边界"""
    print("正在启用UIPI绕过...")
    messages_to_allow = [
        WM_KEYDOWN, WM_KEYUP, 
        WM_CHAR, WM_SYSCHAR, 
        WM_SYSKEYDOWN, WM_SYSKEYUP
    ]
    
    success_count = 0
    for msg in messages_to_allow:
        try:
            # MSGFLT_ADD = 1 表示添加到过滤器允许列表
            result = ctypes.windll.user32.ChangeWindowMessageFilter(msg, 1)
            if result:
                success_count += 1
                print(f"  ✅ 消息 0x{msg:04X} 已添加到允许列表")
            else:
                print(f"  ❌ 消息 0x{msg:04X} 添加失败")
        except Exception as e:
            print(f"  ❌ 消息 0x{msg:04X} 添加异常: {e}")
    
    print(f"UIPI绕过设置完成: {success_count}/{len(messages_to_allow)} 个消息类型成功")
    return success_count > 0

def find_mumu_windows():
    """查找所有MuMu相关窗口"""
    print("正在查找MuMu窗口...")
    
    def enum_windows_proc(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            # 只匹配真正的MuMu窗口，排除包含文件名的VS Code等窗口
            if ("MuMu安卓设备" in window_text or 
                "MuMu模拟器" in window_text or
                (window_text.startswith("MuMu") and "Visual Studio Code" not in window_text)):
                windows.append((hwnd, window_text))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_proc, windows)
    
    if not windows:
        print("❌ 未找到MuMu窗口")
        return None, None
        
    print(f"找到 {len(windows)} 个MuMu窗口:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"  {i+1}. {title} (Handle: {hwnd})")
    
    # 使用第一个窗口作为主窗口
    main_hwnd = windows[0][0]
    print(f"\n使用主窗口: {windows[0][1]} (Handle: {main_hwnd})")
    
    # 查找子窗口
    child_windows = []
    win32gui.EnumChildWindows(main_hwnd, lambda hwnd, param: param.append(hwnd), child_windows)
    
    print(f"找到 {len(child_windows)} 个子窗口:")
    keyboard_handle = main_hwnd  # 默认使用主窗口
    
    for child in child_windows:
        try:
            class_name = win32gui.GetClassName(child)
            print(f"  子窗口: {class_name} (Handle: {child})")
            
            # 查找nemuwin类名的窗口作为键盘目标
            if "display" in class_name.lower():
                keyboard_handle = child
                print(f"  ✅ 找到目标键盘窗口: {class_name} (Handle: {child})")
        except Exception as e:
            print(f"  ❌ 获取子窗口信息失败: {e}")
    
    return main_hwnd, keyboard_handle

def send_esc_key(keyboard_handle):
    """向指定窗口发送ESC按键"""
    print(f"\n正在向窗口 {keyboard_handle} 发送ESC按键...")
    
    # ESC键的虚拟键码是27，扫描码是1
    virtual_key = 27  # VK_ESCAPE
    scan_code = 1     # ESC的扫描码
    
    # 构造lParam: bit0-15=重复次数, bit16-23=扫描码, bit24-31=扩展键标志等
    # 格式: repeat_count | (scan_code << 16)
    lParam_down = 1 | (scan_code << 16)  # 按下时的lParam
    lParam_up = 1 | (scan_code << 16) | 0xC0000000  # 释放时的lParam (设置释放和之前按下标志)
    
    success = False
    
    # 方法1: 使用SendMessage（同步）
    print("  尝试方法1: SendMessage")
    try:
        result_down = ctypes.windll.user32.SendMessageW(keyboard_handle, WM_KEYDOWN, virtual_key, lParam_down)
        result_up = ctypes.windll.user32.SendMessageW(keyboard_handle, WM_KEYUP, virtual_key, lParam_up)
        
        if result_down != 0 or result_up != 0:
            print(f"    ✅ SendMessage成功 (down: {result_down}, up: {result_up})")
            success = True
        else:
            print(f"    ⚠️ SendMessage返回0 (down: {result_down}, up: {result_up})")
    except Exception as e:
        print(f"    ❌ SendMessage异常: {e}")
    
    # 方法2: 使用PostMessage（异步）
    if not success:
        print("  尝试方法2: PostMessage")
        try:
            result_down = ctypes.windll.user32.PostMessageW(keyboard_handle, WM_KEYDOWN, virtual_key, lParam_down)
            result_up = ctypes.windll.user32.PostMessageW(keyboard_handle, WM_KEYUP, virtual_key, lParam_up)
            
            if result_down and result_up:
                print(f"    ✅ PostMessage成功")
                success = True
            else:
                print(f"    ❌ PostMessage失败 (down: {result_down}, up: {result_up})")
        except Exception as e:
            print(f"    ❌ PostMessage异常: {e}")
    
    # 方法3: 前台切换 + keybd_event（物理模拟）
    if not success:
        print("  尝试方法3: 前台切换 + keybd_event")
        try:
            # 保存当前前台窗口
            original_window = ctypes.windll.user32.GetForegroundWindow()
            print(f"    当前前台窗口: {original_window}")
            
            # 切换到目标窗口
            switch_result = ctypes.windll.user32.SetForegroundWindow(keyboard_handle)
            print(f"    窗口切换结果: {switch_result}")
            
            time.sleep(0.2)  # 等待窗口切换完成
            
            # 发送物理按键
            ctypes.windll.user32.keybd_event(virtual_key, scan_code, 0, 0)  # 按下
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(virtual_key, scan_code, 2, 0)  # 释放 (KEYEVENTF_KEYUP = 2)
            
            time.sleep(0.2)
            
            # 恢复原前台窗口
            if original_window != 0:
                ctypes.windll.user32.SetForegroundWindow(original_window)
                print(f"    已恢复前台窗口: {original_window}")
            
            print("    ✅ keybd_event执行完成")
            success = True
            
        except Exception as e:
            print(f"    ❌ keybd_event异常: {e}")
    
    return success

def main():
    """主函数"""
    print("=== MuMu UIPI绕过ESC按键测试 ===\n")
    
    # 第1步：启用UIPI绕过
    if not enable_uipi_bypass():
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

    
    # 第4步：发送ESC按键
    success = send_esc_key(keyboard_handle)
    
    # 第5步：报告结果
    print(f"\n=== 测试结果 ===")
    if success:
        print("✅ ESC按键发送完成！请检查MuMu中的游戏是否收到了ESC按键。")
    else:
        print("❌ 所有方法都失败了，ESC按键可能未成功发送。")
    
    print("\n提示：如果游戏中出现了ESC菜单或其他ESC相关反应，说明按键发送成功。")

if __name__ == "__main__":
    main()