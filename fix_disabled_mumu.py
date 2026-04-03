import win32gui
import win32con
import ctypes
from ctypes import wintypes
import time
import win32api
import win32process

def send_key_to_disabled_window():
    """专门针对禁用窗口的按键发送方案"""
    print("=== 针对禁用MuMu窗口的ESC发送方案 ===\n")
    
    # 1. 找到MuMu窗口
    mumu_main = win32gui.FindWindow(None, "MuMu安卓设备")
    if not mumu_main:
        print("❌ 未找到MuMu安卓设备窗口")
        return False
    
    print(f"找到MuMu主窗口: {mumu_main}")
    
    # 2. 找到nemuwin子窗口
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
    
    if not nemuwin_handle:
        print("❌ 未找到nemuwin窗口")
        return False
    
    print(f"目标窗口: nemuwin (Handle: {nemuwin_handle})")
    
    # 方案1: 临时启用窗口
    print("\n方案1: 临时启用窗口后发送消息")
    try:
        
        # 发送ESC
        result = ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0100, 27, 0x00010001)  # WM_KEYDOWN
        ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0101, 27, 0xC0010001)  # WM_KEYUP
        print(f"  SendMessage结果: {result}")
        
        # 恢复原状态
        if not original_enabled:
            ctypes.windll.user32.EnableWindow(nemuwin_handle, False)
            print("  窗口状态已恢复")
            
        if result != 0:
            print("  ✅ 方案1成功")
            return True
    except Exception as e:
        print(f"  ❌ 方案1异常: {e}")
    
    # 方案2: 向Qt窗口发送
    if qt_handle:
        print(f"\n方案2: 向Qt窗口发送 (Handle: {qt_handle})")
        try:
            result = ctypes.windll.user32.SendMessageW(qt_handle, 0x0100, 27, 0x00010001)
            ctypes.windll.user32.SendMessageW(qt_handle, 0x0101, 27, 0xC0010001)
            print(f"  SendMessage结果: {result}")
            if result != 0:
                print("  ✅ 方案2成功")
                return True
        except Exception as e:
            print(f"  ❌ 方案2异常: {e}")
    
    # 方案3: 向主窗口发送
    print(f"\n方案3: 向主窗口发送 (Handle: {mumu_main})")
    try:
        result = ctypes.windll.user32.SendMessageW(mumu_main, 0x0100, 27, 0x00010001)
        ctypes.windll.user32.SendMessageW(mumu_main, 0x0101, 27, 0xC0010001)
        print(f"  SendMessage结果: {result}")
        if result != 0:
            print("  ✅ 方案3成功")
            return True
    except Exception as e:
        print(f"  ❌ 方案3异常: {e}")
    
    # 方案4: 使用SetFocus + SendMessage
    print(f"\n方案4: 设置焦点后发送消息")
    try:
        # 获取当前焦点
        original_focus = win32gui.GetFocus()
        
        # 设置焦点到nemuwin (即使禁用也尝试)
        ctypes.windll.user32.SetFocus(nemuwin_handle)
        time.sleep(0.1)
        
        # 发送消息
        result = ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0100, 27, 0x00010001)
        ctypes.windll.user32.SendMessageW(nemuwin_handle, 0x0101, 27, 0xC0010001)
        print(f"  SendMessage结果: {result}")
        
        # 恢复焦点
        if original_focus:
            ctypes.windll.user32.SetFocus(original_focus)
        
        if result != 0:
            print("  ✅ 方案4成功")
            return True
    except Exception as e:
        print(f"  ❌ 方案4异常: {e}")
    
    # 方案5: 使用INPUT结构直接注入
    print(f"\n方案5: 使用INPUT结构注入按键")
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
        
        # 先切换到MuMu窗口
        original_window = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SetForegroundWindow(mumu_main)
        time.sleep(0.2)
        
        # 创建INPUT结构
        key_input = INPUT()
        key_input.type = 1  # INPUT_KEYBOARD
        key_input.ki.wVk = 27  # VK_ESCAPE
        key_input.ki.wScan = 1  # ESC scan code
        key_input.ki.dwFlags = 0  # KEYEVENTF_KEYDOWN
        key_input.ki.time = 0
        key_input.ki.dwExtraInfo = None
        
        # 按下
        result1 = ctypes.windll.user32.SendInput(1, ctypes.byref(key_input), ctypes.sizeof(INPUT))
        
        # 释放
        key_input.ki.dwFlags = 2  # KEYEVENTF_KEYUP
        result2 = ctypes.windll.user32.SendInput(1, ctypes.byref(key_input), ctypes.sizeof(INPUT))
        
        time.sleep(0.2)
        
        # 恢复窗口
        if original_window:
            ctypes.windll.user32.SetForegroundWindow(original_window)
        
        print(f"  SendInput结果: 按下={result1}, 释放={result2}")
        if result1 > 0 and result2 > 0:
            print("  ✅ 方案5成功")
            return True
    except Exception as e:
        print(f"  ❌ 方案5异常: {e}")
    
    
    
    return False

def main():
    """主函数"""
    print("请确保MuMu模拟器正在运行游戏...")
    input("按Enter开始测试...")
    
    success = send_key_to_disabled_window()
    
    print(f"\n=== 最终结果 ===")
    if success:
        print("✅ 至少有一种方法执行成功！")
        print("请检查MuMu游戏中是否收到ESC按键。")
    else:
        print("❌ 所有方法都失败了。")
    
    print("\n如果游戏中出现了ESC菜单或相关反应，说明某个方法成功了。")
    print("特别注意方案6（前台切换）通常是最可靠的。")

if __name__ == "__main__":
    main()