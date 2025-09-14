
import win32gui
import win32con
import sys
from PyQt5.QtWidgets import QApplication
import d3dshot

class Hwnd():
    def get_hwnd_dic(self, hwnd, hwnd_title):
        if (win32gui.IsWindow(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
                and win32gui.IsWindowVisible(hwnd)
                and win32gui.GetWindowText(hwnd)):
            hwnd_title[f"{hwnd}"] = win32gui.GetWindowText(hwnd)

    def get_hwnd(self):
        """
        :return: {hwnd:title}
        """
        hwnd_title = {}
        win32gui.EnumWindows(self.get_hwnd_dic, hwnd_title)
        return hwnd_title


hwnd = Hwnd()
print(hwnd.get_hwnd())

# 返回窗口标题为"雷电模拟器"句柄
hld_leidian = win32gui.FindWindow(None, u"雷电模拟器")
print("雷电模拟器窗口句柄ID:" + str(hld_leidian))


# 根据句柄获取句柄标题和类名
def get_child_windows(parent):
    """
    获得parent的所有子窗口句柄
    返回子窗口句柄列表
    :param parent: parent为父窗口句柄id
    :return:
    """

    if not parent:
        return
    hwndchildlist = []
    win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd),  hwndchildlist)
    return hwndchildlist


ret_leidian = get_child_windows(hld_leidian)
print(ret_leidian)

def print_window_info(i):
    title = win32gui.GetWindowText(i)  # i为句柄id
    # 获取标题
    clsname = win32gui.GetClassName(i)
    print(title, clsname)
    # 获取左、上、右、下的窗口位置
    left, top, right, bottom = win32gui.GetWindowRect(i)
    print(left, top, right, bottom)
    print("id：{id}、title：{title}、clsname：{clsname}、left：{left}, top：{top}, right：{right}, bottom：{bottom}"
          .format(id=i, title=title, clsname=clsname, left=left, top=top, right=right, bottom=bottom))

# 根据句柄获取句柄标题和类名
if ret_leidian is not None:
    for i in ret_leidian:
        print_window_info(i)


# 使用PyQt5 进行雷电截图
# 雷电窗口可以遮挡，但不可最小化，最小化截图黑屏
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()
for i in (ret_leidian):
    ret_leidian2 = get_child_windows(i)
    
    for j in (ret_leidian2):
        print_window_info(j)

    img = screen.grabWindow(i).toImage()
    img.save("screenshot"+str(i)+".jpg")  # 大小150k



# 关闭雷电模拟器窗口
#win32gui.PostMessage(hld_leidian, win32con.WM_CLOSE, 0, 0)  # 参数1 窗口句柄