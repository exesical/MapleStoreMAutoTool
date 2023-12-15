import os
import cv2
import json
#from cv2 import cv2
from os import path, walk
from re import search
from numpy import uint8, fromfile
from DoScreenHit import DoScreenHit
import win32gui 
from win32gui import DeleteObject, SetForegroundWindow, GetWindowRect, GetWindowDC
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY

from numpy import frombuffer, uint8, array

class MSmState(object):
    """description of class"""

    def __init__(self, StateName, HandleNumber):
        left, top, right, bottom = win32gui.GetWindowRect(HandleNumber)
        self.ScreenShotImage = None
        self.ScreenShotWidth = right - left
        self.ScreenShotHeight = bottom - top
        
        self.HandleNumber = HandleNumber
        self.HitHandle = DoScreenHit(HandleNumber)
        self.Name = StateName
        Path_cur = os.path.dirname(__file__) + "\\Data\\" + StateName
        Path_Identification = Path_cur + "\\Identification\\" 
        IdImagePath = []
        self.IdImageSize = {}
        self.IdImage     = {}
        for cur_dir, sub_dir, included_file in walk(Path_Identification):
            if included_file:
                for file in included_file:
                    if search(r'.png', file):
                        IdImagePath.append(cur_dir + "\\" + file)

        if len(IdImagePath) == 0:
            print("<br> Load Identification pic failed, check the path or state name")
        for i in range(len(IdImagePath)):
            img = cv2.imdecode(fromfile(IdImagePath[i], dtype=uint8), -1)
            self.IdImageSize = img.shape[:2]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);
            self.IdImage[i] = img
        
        self.HitInfo = {}
        HitInfoPath = Path_cur + "\\HitInfo.json"
        if os.path.exists(HitInfoPath):
            HitInfoJson = json.load(open(HitInfoPath, 'r', encoding='utf-8'))
            for i in range(len(HitInfoJson)):
                self.HitInfo[HitInfoJson[i]["OpName"]] = [HitInfoJson[i]["ClickPos"],HitInfoJson[i]["ClickRange"]]
        
        self.JumpInfo = {}
        JumpInfoPath = Path_cur + "\\JumpInfo.json"
        if os.path.exists(JumpInfoPath):
            JumpInfoJson = json.load(open(JumpInfoPath, 'r', encoding='utf-8'))
            for i in range(len(JumpInfoJson)):
                self.JumpInfo[JumpInfoJson[i]["NextStateName"]] = [HitInfoJson[i]["ClickPos"],HitInfoJson[i]["ClickRange"]]

    def IsUnderState(self, MatchingThreshold = 0.8):
        self.RefreshScreenShot()
        for i in range(len(self.IdImage)):
            if self.IsPicMatching(self.IdImage[i], MatchingThreshold):
                return True
        return False

    def IsPicMatching(self, InPic, MatchingThreshold = 0.8):

        #cv2.namedWindow('scr_img')  # 命名窗口
        #cv2.imshow("scr_img", self.ScreenShotImage)  # 显示
        #cv2.namedWindow('dst_img')  # 命名窗口
        #cv2.imshow("dst_img", InPic)  # 显示
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        res = cv2.matchTemplate(self.ScreenShotImage, InPic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= MatchingThreshold:
            return True
        return False

    def DoHit(self, HitPos, HitRange):
        self.HitHandle.HitPosition(HitPos, HitRange)

    def JumpToTarget(self, TargetState):
        if JumpInfo.has_key(TargetState):
            HitPos = JumpInfo[TargetState][0]
            HitRange = JumpInfo[TargetState][1]
            #do hit opration
            self.DoHit(HitPos, HitRange)
            return True
        else:
            return False
    
    def RefreshScreenShot(self):
        hwnd_dc = GetWindowDC(self.HandleNumber)
        mfc_dc = CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bit_map = CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, self.ScreenShotWidth, self.ScreenShotHeight)
        save_dc.SelectObject(save_bit_map)
        save_dc.BitBlt((0, 0), (self.ScreenShotWidth, self.ScreenShotHeight), mfc_dc, (0, 0), SRCCOPY)
        signed_ints_array = save_bit_map.GetBitmapBits(True)
        self.ScreenShotImage = frombuffer(signed_ints_array, dtype='uint8')
        self.ScreenShotImage.shape = (self.ScreenShotHeight, self.ScreenShotWidth, 4)
        self.ScreenShotImage = cv2.cvtColor(self.ScreenShotImage, cv2.COLOR_BGRA2GRAY)
        print("Refresh ScreenShot Successed")
        DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()

        #show for test
        #cv2.namedWindow('scr_img')  # 命名窗口
        #cv2.imshow("scr_img", self.ScreenShotImage)  # 显示
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #return self.ScreenShotImage


class MSmState_CharacterSelect(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
        Path_cur = os.path.dirname(__file__) + "\\Data\\" + StateName
        IsMainCharacterIdImagePath = Path_cur + "\\IsMainCharacterSelected.png"
        self.IsMainCharacterIdImage = cv2.imdecode(fromfile(IsMainCharacterIdImagePath, dtype=uint8), -1)
        self.IsMainCharacterIdImage = cv2.cvtColor(self.IsMainCharacterIdImage, cv2.COLOR_BGR2GRAY);
        
        #cv2.namedWindow('scr_img')  # 命名窗口
        #cv2.imshow("scr_img", self.IsMainCharacterIdImage)  # 显示
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

    def TrySelecteMainCharacter(self):
        HitInfo_SelectCharacter0 = self.HitInfo["SelectCharacter0"]
        self.DoHit(HitInfo_SelectCharacter0[0],HitInfo_SelectCharacter0[1])
        #self.RefreshScreenShot()
        return self.IsPicMatching(self.IsMainCharacterIdImage)
            

    def SelectCharacter(self, CharacterIndex):
        HitInfo_NextCharacterPage = self.HitInfo["NextCharacterPage"];
        while(self.TrySelecteMainCharacter() == False):
            self.DoHit(HitInfo_NextCharacterPage[0],HitInfo_NextCharacterPage[1])
        c_page = int(CharacterIndex / 7)
        c_index = CharacterIndex % 7
        for i in range(c_page):
            self.DoHit(HitInfo_NextCharacterPage[0],HitInfo_NextCharacterPage[1])
        HitInfo_CharacterN = self.HitInfo["SelectCharacter" + str(c_index)]
        self.DoHit(HitInfo_CharacterN[0],HitInfo_CharacterN[1]);

        
        

        
    


