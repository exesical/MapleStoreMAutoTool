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
from time import sleep
import numpy as np
from numpy import frombuffer, uint8, array
from FrozenPath import frozen


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
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
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
                self.JumpInfo[JumpInfoJson[i]["NextStateName"]] = [JumpInfoJson[i]["ClickPos"],JumpInfoJson[i]["ClickRange"]]

    def IsUnderState(self, MatchingThreshold = 0.8):
        self.RefreshScreenShot()
        for i in range(len(self.IdImage)):
            if self.IsPicMatching(self.IdImage[i], MatchingThreshold):
                return True
        return False

    def GetPicPos(self, InPic, MatchingThreshold = 0.8):
        res = cv2.matchTemplate(self.ScreenShotImage, InPic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= MatchingThreshold:
            return max_loc
        else:
            return None

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
            #print("Picture matching successed, p the max value = %.3f")
            return True
        return False

    def DoHit(self, HitPos, HitRange):
        self.HitHandle.HitPosition(HitPos, HitRange)
        #all operation 
        sleep(np.random.randint(20,80) / 100)

    #return error code: 
    #0 - successed leave current state
    #1 - can not leave current state
    #2 - can not find jump info
    def JumpToTarget(self, TargetState, WaitingTime = 0.5):
        if TargetState.Name in self.JumpInfo:
            HitPos = self.JumpInfo[TargetState.Name][0]
            HitRange = self.JumpInfo[TargetState.Name][1]
            #make sure leave current state
            #try 30 times
            MaxOpTimes = 30
            OpTimes = 0
            
            while(self.IsUnderState() and OpTimes != MaxOpTimes ):
                self.DoHit(HitPos, HitRange)
                sleep(1)
                if TargetState.IsUnderState():
                    sleep(WaitingTime)
                    return 0
            if OpTimes < 30:
                return 0
            else:
                print("State {self.Name} can not leave current state, please check jump table")
                return 1
        else:
            print("State {self.Name} has no methon jump to State {TargetState}, please check jump table")
            return 2
    
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

    def PrepareState(self):
        #do Nothing
        return


class MSmState_CharacterSelect(MSmState):

    CurrentSelectedCharacterIndex = 0
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
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
        self.RefreshScreenShot()
        return self.IsPicMatching(self.IsMainCharacterIdImage)

    def PrepareState(self):
        MaxIter = 30
        iter = 0
        HitInfo_NextCharacterPage = self.HitInfo["NextCharacterPage"];
        while(self.TrySelecteMainCharacter() == False and iter < 30):
            iter = iter+1
            self.DoHit(HitInfo_NextCharacterPage[0],HitInfo_NextCharacterPage[1])
        c_page = int(MSmState_CharacterSelect.CurrentSelectedCharacterIndex / 7)
        c_index = MSmState_CharacterSelect.CurrentSelectedCharacterIndex % 7
        for i in range(c_page):
            self.DoHit(HitInfo_NextCharacterPage[0],HitInfo_NextCharacterPage[1])
            sleep(0.5)
        HitInfo_CharacterN = self.HitInfo["SelectCharacter" + str(c_index)]
        for i in range(np.random.randint(2,4)):
            self.DoHit(HitInfo_CharacterN[0],HitInfo_CharacterN[1]);
        
        if iter < 30:
            return True
        else:
            return False
        

class MSmState_ChangeCharacter(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)


class MSmState_GameModeDefault(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        MaterialEnterIdentifyPath = Path_cur + "\\MaterialEnterIdentify.png"
        self.MaterialEnterIdImage = cv2.imdecode(fromfile(MaterialEnterIdentifyPath, dtype=uint8), -1)
        self.MaterialEnterIdImage = cv2.cvtColor(self.MaterialEnterIdImage, cv2.COLOR_BGR2GRAY);

    def PrepareState(self):
        self.RefreshScreenShot()
        MaterialEnterPos = self.GetPicPos(self.MaterialEnterIdImage)
        if MaterialEnterPos is None:
            print("Cannot Find Material Enter")
            return False
        else:
            self.JumpInfo["MaterialsMain"] = [[MaterialEnterPos[0]+ 75,MaterialEnterPos[1]+ 65],[30, 30]]
            return True

class MSmState_GuildInfo(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

    def PrepareState(self):
        sleep(3)
        HitInfo_ReciveGift = self.HitInfo["ReciveGift"]
        for i in range(np.random.randint(2,5)):
            self.DoHit(HitInfo_ReciveGift[0], HitInfo_ReciveGift[1])
        sleep(2)
        return True

class MSmState_Loading(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

class MSmState_Login(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

class MSmState_Mail(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
    def PrepareState(self):
        sleep(1)
        for i in range(np.random.randint(2,4)):
            self.DoHit(self.HitInfo["Personal"][0],self.HitInfo["Personal"][1])
        sleep(2)
        for i in range(np.random.randint(2,4)):
            self.DoHit(self.HitInfo["ReciveAll"][0],self.HitInfo["ReciveAll"][1])
        sleep(2)
        for i in range(np.random.randint(2,4)):
            self.DoHit(self.HitInfo["Confirm"][0],self.HitInfo["Confirm"][1])
        sleep(1)
        return True

class MSmState_MaterialAutoFighting(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        MaterialGiveUpPath = Path_cur + "\\MaterialGiveUp.png"
        self.MaterialGiveUpIdImage = cv2.imdecode(fromfile(MaterialGiveUpPath, dtype=uint8), -1)
        self.MaterialGiveUpIdImage = cv2.cvtColor(self.MaterialGiveUpIdImage, cv2.COLOR_BGR2GRAY)
        MaterialExitPath = Path_cur + "\\MaterialExit.png"
        self.MaterialExitIdImage = cv2.imdecode(fromfile(MaterialExitPath, dtype=uint8), -1)
        self.MaterialExitIdImage = cv2.cvtColor(self.MaterialExitIdImage, cv2.COLOR_BGR2GRAY)
    def PrepareState(self):
        while True:
            self.RefreshScreenShot()
            if self.IsPicMatching(self.MaterialGiveUpIdImage):
                self.DoHit(self.HitInfo["GiveUp"][0],self.HitInfo["GiveUp"][1])
                sleep(3)
            if self.IsPicMatching(self.MaterialExitIdImage):
                return True
            sleep(5)

class MSmState_MaterialEnter0(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

    def PrepareState(self):
        for i in range(np.random.randint(5,7)):
            self.DoHit(self.HitInfo["AddTimes"][0],self.HitInfo["AddTimes"][1])
        return True

class MSmState_MaterialEnter1(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

class MSmState_MaterialsMain(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

class MSmState_SystemMenuOpening(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)

class MSmState_Wander(MSmState):
    def __init__(self, StateName, HandleNumber):
        super().__init__(StateName, HandleNumber)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        self.AdImages = []
        for i in range(4):
            AdFilePath =  Path_cur + "\\Ad" + str(i)+ ".png"
            self.AdImages.append(cv2.imdecode(fromfile(AdFilePath, dtype=uint8), -1))
            self.AdImages[i] = cv2.cvtColor(self.AdImages[i], cv2.COLOR_BGR2GRAY)



    def PrepareState(self):
        AdCloseMask = []
        HasAdExist = False
        self.RefreshScreenShot()
        for i in range(4):
            AdCloseMask.append( self.IsPicMatching(self.AdImages[i]))
            if(AdCloseMask[i]):
                HasAdExist = True

        while HasAdExist:
            for i in range(4):
                if AdCloseMask[i]:
                    self.DoHit(self.HitInfo["CloseAd" + str(i)][0],self.HitInfo["CloseAd" + str(i)][1])
                    HasAdExist = False
                    sleep(0.5)
            self.RefreshScreenShot()
            for i in range(4):
                AdCloseMask[i] = self.IsPicMatching(self.AdImages[i])
                if(AdCloseMask[i]):
                    HasAdExist = True
        return True