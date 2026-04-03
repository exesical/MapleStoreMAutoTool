import win32gui
import win32con
import ctypes
from ctypes import wintypes
import time

def send_esc_background_only():
    """仅使用后台方法发送ESC，不使用keybd_event"""
    print("=== 后台ESC发送测试（禁用keybd_event）===\n")
    
    # 1. 找到MuMu窗口
    mumu_main = win32gui.FindWindow(None, "MuMu安卓设备")
    if not mumu_main:
        print("❌ 未找到MuMu安卓设备窗口")
        return False
    
    print(f"找到MuMu主窗口: {mumu_main}")
    
    # 2. 启用UIPI绕过
    print("启用UIPI绕过...")
    messages = [0x0100, 0x0101, 0x0102, 0x0103, 0x0104, 0x0105]  # 键盘消息
    for msg in messages:
        try:
            ctypes.windll.user32.ChangeWindowMessageFilter(msg, 1)
        except:
            pass
    
    # 3. 找到子窗口
    child_windows = []
    win32gui.EnumChildWindows(mumu_main, lambda hwnd, param: param.append(hwnd), child_windows)
    
    nemuwin_handle = None
    qt_handle = None
    
    for child in child_windows:
        class_name = win32gui.GetClassName(child)
        enabled = win32gui.IsWindowEnabled(child)
        print(f"子窗口: {class_name} (Handle: {child}, 启用: {enabled})")
        
        if "nemuwin" in class_name.lower():
            nemuwin_handle = child
        elif "qt" in class_name.lower():
            qt_handle = child
    
    success_methods = []
    
    # 方案1: 临时启用nemuwin窗口
    if nemuwin_handle:
        print(f"\n方案1: 临时启用nemuwin窗口 (Handle: {nemuwin_handle})")
        try:
            original_enabled = win32gui.IsWindowEnabled(nemuwin_handle)
            print(f"  原始状态: {'启用' if original_enabled else '禁用'}")
            
            if not original_enabled:
                result = ctypes.windll.user32.EnableWindow(nemuwin_handle, True)
                print(f"  启用窗口结果: {result}")
                time.sleep(0.1)
            
            # 发送ESC
            result_down = ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0100, 27, 0x00010001)
            time.sleep(0.02)
            result_up = ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0101, 27, 0xC0010001)
            
            print(f"  SendMessage结果: down={result_down}, up={result_up}")
            
            # 恢复原状态
            if not original_enabled:
                ctypes.windll.user32.EnableWindow(nemuwin_handle, False)
                print("  窗口状态已恢复为禁用")
            
            if result_down != 0 or result_up != 0:
                success_methods.append("临时启用nemuwin")
                print("  ✅ 方案1可能成功")
            else:
                print("  ⚠️ 方案1返回值为0")
        except Exception as e:
            print(f"  ❌ 方案1异常: {e}")
    
    # 方案2: 向Qt窗口发送
    if qt_handle:
        print(f"\n方案2: 向Qt窗口发送 (Handle: {qt_handle})")
        try:
            result_down = ctypes.windll.user32.SendMessageW(qt_handle, 0x0100, 27, 0x00010001)
            time.sleep(0.02)
            result_up = ctypes.windll.user32.SendMessageW(qt_handle, 0x0101, 27, 0xC0010001)
            
            print(f"  SendMessage结果: down={result_down}, up={result_up}")
            
            if result_down != 0 or result_up != 0:
                success_methods.append("Qt窗口")
                print("  ✅ 方案2可能成功")
            else:
                print("  ⚠️ 方案2返回值为0")
        except Exception as e:
            print(f"  ❌ 方案2异常: {e}")
    
    # 方案3: 向主窗口发送
    print(f"\n方案3: 向主窗口发送 (Handle: {mumu_main})")
    try:
        result_down = ctypes.windll.user32.SendMessageW(mumu_main, 0x0100, 27, 0x00010001)
        time.sleep(0.02)
        result_up = ctypes.windll.user32.SendMessageW(mumu_main, 0x0101, 27, 0xC0010001)
        
        print(f"  SendMessage结果: down={result_down}, up={result_up}")
        
        if result_down != 0 or result_up != 0:
            success_methods.append("主窗口")
            print("  ✅ 方案3可能成功")
        else:
            print("  ⚠️ 方案3返回值为0")
    except Exception as e:
        print(f"  ❌ 方案3异常: {e}")
    
    # 方案4: PostMessage到nemuwin
    if nemuwin_handle:
        print(f"\n方案4: PostMessage到nemuwin")
        try:
            # 先临时启用窗口
            original_enabled = win32gui.IsWindowEnabled(nemuwin_handle)
            if not original_enabled:
                ctypes.windll.user32.EnableWindow(nemuwin_handle, True)
                time.sleep(0.1)
            
            result_down = ctypes.windll.user32.PostMessageW(nemuwin_handle, 0x0100, 27, 0x00010001)
            time.sleep(0.02)
            result_up = ctypes.windll.user32.PostMessageW(nemuwin_handle, 0x0101, 27, 0xC0010001)
            
            print(f"  PostMessage结果: down={result_down}, up={result_up}")
            
            # 恢复状态
            if not original_enabled:
                ctypes.windll.user32.EnableWindow(nemuwin_handle, False)
            
            if result_down and result_up:
                success_methods.append("PostMessage-nemuwin")
                print("  ✅ 方案4可能成功")
            else:
                print("  ❌ 方案4失败")
        except Exception as e:
            print(f"  ❌ 方案4异常: {e}")
    
    # 方案5: SendInput（不切换前台）
    print(f"\n方案5: SendInput后台注入")
    try:
        # 定义INPUT结构
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
            ]
        
        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]
            _anonymous_ = ("_input",)
            _fields_ = [("type", ctypes.c_ulong), ("_input", _INPUT)]
        
        # 创建按下事件
        key_down = INPUT()
        key_down.type = 1  # INPUT_KEYBOARD
        key_down.ki.wVk = 27
        key_down.ki.wScan = 1
        key_down.ki.dwFlags = 0  # KEYEVENTF_KEYDOWN
        key_down.ki.time = 0
        key_down.ki.dwExtraInfo = None
        
        # 创建释放事件
        key_up = INPUT()
        key_up.type = 1
        key_up.ki.wVk = 27
        key_up.ki.wScan = 1
        key_up.ki.dwFlags = 2  # KEYEVENTF_KEYUP
        key_up.ki.time = 0
        key_up.ki.dwExtraInfo = None
        
        # 发送输入（不切换窗口）
        result1 = ctypes.windll.user32.SendInput(1, ctypes.byref(key_down), ctypes.sizeof(INPUT))
        time.sleep(0.02)
        result2 = ctypes.windll.user32.SendInput(1, ctypes.byref(key_up), ctypes.sizeof(INPUT))
        
        print(f"  SendInput结果: down={result1}, up={result2}")
        
        if result1 > 0 and result2 > 0:
            success_methods.append("SendInput后台")
            print("  ✅ 方案5可能成功")
        else:
            print("  ❌ 方案5失败")
    except Exception as e:
        print(f"  ❌ 方案5异常: {e}")
    
    return success_methods

def main():
    """主函数"""
    print("请确保MuMu模拟器正在运行游戏，观察游戏界面是否有变化...")
    print("注意：此测试不会使用keybd_event，只使用后台发送方法")
    input("\n按Enter开始测试...")
    
    success_methods = send_esc_background_only()
    
    print(f"\n=== 测试结果 ===")
    if success_methods:
        print(f"✅ 执行成功的方法: {', '.join(success_methods)}")
        print("请观察MuMu模拟器游戏界面是否发生了变化！")
        print("如果游戏中出现了ESC菜单、暂停界面或其他反应，说明后台发送成功了。")
    else:
        print("❌ 所有后台方法的API调用都失败了。")
    
    print("\n观察要点：")
    print("- 游戏中是否出现了ESC菜单")
    print("- 游戏是否暂停")
    print("- 角色是否停止移动")
    print("- 任何与ESC相关的界面变化")

if __name__ == "__main__":
    main()