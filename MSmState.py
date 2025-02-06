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
import random

GHasGottenAll = False

class MSmState(object):
    """description of class"""
    bMainCharacter = False
    bUseDebug = False
    bUseMainWindowCapture = False
    HandleNumber_Main = 0
    HandleNumber_Render = 0
    def __init__(self, StateName):
        left, top, right, bottom = win32gui.GetWindowRect(MSmState.HandleNumber_Render)
        self.ScreenShotImage = None
        self.ScreenShotWidth = right - left
        self.ScreenShotHeight = bottom - top
        
        if MSmState.bUseMainWindowCapture:
            self.ScreenShotWidth +=50
            self.ScreenShotHeight +=50

        #self.HandleNumber = HandleNumber
        self.HitHandle = DoScreenHit(MSmState.HandleNumber_Render)
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
        if len(self.IdImage) == 0:
            return True
        for i in range(len(self.IdImage)):
            if self.IsPicMatching(self.IdImage[i], MatchingThreshold):
                print("Now is under state - "+ self.Name)
                return True
        print("Now is not under state - "+ self.Name)
        return False

    def GetPicPos(self, InPic, MatchingThreshold = 0.8,method = cv2.TM_CCOEFF_NORMED):
        res = cv2.matchTemplate(self.ScreenShotImage, InPic, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= MatchingThreshold:
            return max_loc
        else:
            return None

    def IsPicMatching(self, InPic, MatchingThreshold = 0.8):

        if MSmState.bUseDebug:
            cv2.namedWindow('scr_img')  # 命名窗口
            cv2.imshow("scr_img", self.ScreenShotImage)  # 显示
            cv2.namedWindow('dst_img')  # 命名窗口
            cv2.imshow("dst_img", InPic)  # 显示
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        res = cv2.matchTemplate(self.ScreenShotImage, InPic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #print("Picture matching result = " + str(max_val) + "mactching pos = " + str(max_loc))
        if max_val >= MatchingThreshold:
            #print("Picture matching successed, p the max value = %.3f")
            return True
        return False

    def DoHit(self, HitPos, HitRange):
        self.HitHandle.HitPosition(HitPos, HitRange)
        #all operation 
        sleep(np.random.randint(20,80) / 100)

    def DoHitByName(self, hitname):
        print("Hit position by Name - " + hitname)
        self.DoHit(self.HitInfo[hitname][0],self.HitInfo[hitname][1])

    #return error code: 
    #0 - successed leave current state
    #1 - can not leave current state
    #2 - can not find jump info
    def JumpToTarget(self, TargetState, WaitingTime = 0.5):
        print("Try jump to taget " + TargetState.Name + "from target "+ self.Name )
        if TargetState.Name in self.JumpInfo:
            HitPos = self.JumpInfo[TargetState.Name][0]
            HitRange = self.JumpInfo[TargetState.Name][1]
            #make sure leave current state
            #try 30 times
            MaxOpTimes = 300
            OpTimes = 0
            sleeptime = 1
            if(self.Name == "SystemMenuOpening" and TargetState.Name == "GameModeDefault"):
                sleeptime = 3
            if(self.Name == "SystemMenuOpening" and TargetState.Name == "FastJump"):
                sleeptime = 3

            while(self.IsUnderState() and OpTimes != MaxOpTimes ):
                self.DoHit(HitPos, HitRange)
                sleep(sleeptime)
                if TargetState.IsUnderState():
                    print("Jump success by reaching taget state " + TargetState.Name)
                    sleep(WaitingTime)
                    return 0
            if OpTimes < 300:
                print("Jump success by leaving current state "+ self.Name)
                return 0
            else:
                print("State {self.Name} can not leave current state, please check jump table")
                return 1
        else:
            print("State " + self.Name + "has no methon jump to " + TargetState.Name +", please check jump table")
            return 2
    
    def RefreshScreenShot(self):
        if(MSmState.bUseMainWindowCapture):
            hwnd_dc = GetWindowDC(MSmState.HandleNumber_Main)
        else:
            hwnd_dc = GetWindowDC(MSmState.HandleNumber_Render)
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
        #print("Refresh ScreenShot Successed")
        DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()

        #show for test
        #cv2.namedWindow('scr_img')  # 命名窗口
        #cv2.imshow("scr_img", self.ScreenShotImage)  # 显示
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #return self.ScreenShotImage

    def Processing(self):
        #do Nothing
        return True

    def ReadPic(self, PicName):
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name
        img = cv2.imdecode(fromfile(Path_cur + "\\" + PicName + ".png", dtype=uint8), -1)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);

    def WaitUntil(self, CheckPic):
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == False:
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)

    def TryInnerJumpByPos(self, HitPos, CheckPic):
        self.DoHit(HitPos[0],HitPos[1])
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == False:
            self.DoHit(HitPos[0],HitPos[1])
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)

    def TryInnerJump(self, HitName, CheckPic):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == False:
            self.DoHitByName(HitName);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)

    def TryLeaveJumpByPos(self, HitPos, CheckPic):
        self.DoHit(HitPos[0],HitPos[1])
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == True:
            self.DoHit(HitPos[0],HitPos[1])
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)

    def TryLeaveJump(self, HitName, CheckPic, MatchingThreshold = 0.8):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic, MatchingThreshold)
        while bSuccess == True:
            self.DoHitByName(HitName);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
    
            
    def TryLeaveJumpAuto(self, CheckPic, HitOffset, HitRange):
        sleep(1)
        self.RefreshScreenShot();
        AutoPos = self.GetPicPos(CheckPic, 0.9,cv2.TM_CCORR_NORMED)
        if AutoPos is None:
            return
        self.DoHit([AutoPos[0] + HitOffset[0], AutoPos[1] + HitOffset[1] + 33], HitRange);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == True:
            self.DoHit([AutoPos[0] + HitOffset[0], AutoPos[1] + HitOffset[1] + 33],HitRange);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)

    def TryLeaveJump2(self, HitName, CheckPic, CheckPic2):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
        while bSuccess == True:
            self.DoHitByName(HitName);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))

    def DoAddTimes(self):
        return
        for i in range(np.random.randint(5,7)):
            self.DoHitByName("AddTimes")

    def CloseAuction(self):
        return

    def WaitingForAutoFightingFinished(self):
        self.RefreshScreenShot()
        bAutoFightingFinished = self.IsPicMatching(self.ExitIdImage);
        while bAutoFightingFinished == False:
            sleep(5)
            self.RefreshScreenShot()
            self.CloseAuction()
            bAutoFightingFinished = self.IsPicMatching(self.ExitIdImage);


class MSmState_CharacterSelect(MSmState):

    CurrentSelectedCharacterIndex = 0
    def __init__(self, StateName):
        super().__init__(StateName)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        IsMainCharacterIdImagePath = Path_cur + "\\IsMainCharacterSelected.png"
        self.IsMainCharacterIdImage = cv2.imdecode(fromfile(IsMainCharacterIdImagePath, dtype=uint8), -1)
        self.IsMainCharacterIdImage = cv2.cvtColor(self.IsMainCharacterIdImage, cv2.COLOR_BGR2GRAY);
        
        #cv2.namedWindow('scr_img')  # 命名窗口
        #cv2.imshow("scr_img", self.IsMainCharacterIdImage)  # 显示
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

    def TrySelecteMainCharacter(self):
        self.DoHitByName("SelectCharacter0")
        self.RefreshScreenShot()
        return self.IsPicMatching(self.IsMainCharacterIdImage)

    def Processing(self):
        while(self.TrySelecteMainCharacter() == False):
            self.DoHitByName("NextCharacterPage")
        c_page = int(MSmState_CharacterSelect.CurrentSelectedCharacterIndex / 7)
        c_index = MSmState_CharacterSelect.CurrentSelectedCharacterIndex % 7
        for i in range(c_page):
            self.DoHitByName("NextCharacterPage")
            sleep(0.5)
        HitInfo_CharacterN = self.HitInfo["SelectCharacter" + str(c_index)]
        for i in range(np.random.randint(2,4)):
            self.DoHit(HitInfo_CharacterN[0],HitInfo_CharacterN[1]);
        
        return True

        

class MSmState_ChangeCharacter(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_FastJump(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.Enter = self.ReadPic("Enter")
        self.Enter2 = self.ReadPic("Enter2")
        self.EnterConfirm = self.ReadPic("EnterConfirm")
        self.FinishConfirm = self.ReadPic("FinishConfirm")
        self.OpenTableIdenty = self.ReadPic("OpenTableIdenty")
        self.UseAllTimes = self.ReadPic("UseAllTimes")
        self.MPEnter = []
        self.MPIdenty = []
        for i in range(0,5):
            self.MPEnter.append(self.ReadPic("MPEnter" + str(i)))
        for i in range(0,3):
            self.MPIdenty.append(self.ReadPic("MPIdenty" + str(i)))

    def Processing(self):
        self.TryInnerJump("OpenTable", self.OpenTableIdenty)
        self.RefreshScreenShot();
        bUseAllTimes = self.GetPicPos(self.UseAllTimes, 0.995, cv2.TM_CCORR_NORMED)               
        if bUseAllTimes is not None:
            self.TryLeaveJump("CloseTable", self.OpenTableIdenty)
            return True
        self.HitHandle.DoMousePull(self.HitInfo["DoMouseWheel"][0],self.HitInfo["DoMouseWheel"][1],[0,-300], 20, 3)
        sleep(3)
        self.RefreshScreenShot();
        FastMPPos = None
        for i in range(0,3):
            if FastMPPos is None:
                FastMPPos = self.GetPicPos(self.MPIdenty[i], 0.987, cv2.TM_CCORR_NORMED)     
        
        if FastMPPos is not None:
            self.TryInnerJump("OpenTable", self.OpenTableIdenty)
            FastMPEnterPos = [[FastMPPos[0] + 360, FastMPPos[1]+49],[12,5]]
            self.TryInnerJumpByPos(FastMPEnterPos, self.Enter2)
            self.RefreshScreenShot();
            FastMPPos = None
            for i in range(0,5):
                if FastMPPos is not None:
                    break
                FastMPPos = self.GetPicPos(self.MPEnter[i], 0.998, cv2.TM_CCORR_NORMED)     
            if FastMPPos is not None:
                FastMPEnterPos = [[FastMPPos[0] + 40, FastMPPos[1]+33],[10,10]]
                for i in range(np.random.randint(2,4)):
                    self.DoHit(FastMPEnterPos[0],FastMPEnterPos[1])
                self.RefreshScreenShot();
                FastMPEnterPos = self.GetPicPos(self.Enter, 0.99, cv2.TM_CCORR_NORMED)
                if FastMPEnterPos is not None:
                    self.TryInnerJump("UseJump", self.EnterConfirm)
                    self.TryLeaveJump("FinalComfirm",self.EnterConfirm,0.9)
                    sleep(3)
                    self.TryLeaveJump("Finish",self.FinishConfirm)
                else:
                    self.TryLeaveJump("GiveUp",self.Enter2)
                    self.TryLeaveJump("CloseTable", self.OpenTableIdenty)
            else:
                self.TryLeaveJump("GiveUp",self.Enter2)
                self.TryLeaveJump("CloseTable", self.OpenTableIdenty)
        else:
            self.TryLeaveJump("CloseTable", self.OpenTableIdenty)

        return True
    


class MSmState_GameModeDefault(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.MaterialEnterIdImage = self.ReadPic("MaterialEnterIdentify")
        self.EliteEnterIdImage = self.ReadPic("EliteEnterIdImage")
        self.TangyunEnterIdImage = self.ReadPic("TangyunEnterIdImage")
        self.PirateEnterIdImage = self.ReadPic("PirateEnterIdImage")
        self.NitePyramidEnterIdImage = self.ReadPic("NitePyramidEnterIdImage")
        self.WeeklyEnterIdImage = self.ReadPic("WeeklyEnterIdImage")
        self.MonsterParkEnterIdImage = self.ReadPic("MonsterParkEnterIdImage")
        self.WulinEnterIdImage = self.ReadPic("WulinEnterIdImage")
        self.DimensionEnterIdImage = self.ReadPic("DimensionEnterIdImage")
        self.ExpeditionEnterIdImage = self.ReadPic("ExpeditionEnterIdImage")

    def AddEnter(self, ModeName, IdPic,MatchingThreshold = 0.8):
        Pos = self.GetPicPos(IdPic)
        if Pos is None:
            print("Cannot find "+ ModeName + " Enter")
        else:
            self.JumpInfo[ModeName] = [[Pos[0]+ 75, Pos[1]+ 80],[15, 15]]

    def Processing(self):
        #reload jump info
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name
        self.JumpInfo = {}
        JumpInfoPath = Path_cur + "\\JumpInfo.json"
        if os.path.exists(JumpInfoPath):
            JumpInfoJson = json.load(open(JumpInfoPath, 'r', encoding='utf-8'))
            for i in range(len(JumpInfoJson)):
                self.JumpInfo[JumpInfoJson[i]["NextStateName"]] = [JumpInfoJson[i]["ClickPos"],JumpInfoJson[i]["ClickRange"]]
        self.RefreshScreenShot()
        self.AddEnter("MaterialsMain", self.MaterialEnterIdImage)        
        self.AddEnter("Elite", self.EliteEnterIdImage,0.85)        
        self.AddEnter("Tangyun", self.TangyunEnterIdImage)        
        self.AddEnter("Pirate", self.PirateEnterIdImage)        
        self.AddEnter("NitePyramid", self.NitePyramidEnterIdImage)        
        self.AddEnter("Weekly", self.WeeklyEnterIdImage)        
        self.AddEnter("Wulin", self.WulinEnterIdImage)        
        self.AddEnter("Dimension", self.DimensionEnterIdImage)        
        self.AddEnter("MonsterPark", self.MonsterParkEnterIdImage)        
        self.AddEnter("Expedition", self.ExpeditionEnterIdImage)        

        return True

class MSmState_GuildInfo(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

    def Processing(self):
        sleep(3)
        for i in range(np.random.randint(2,5)):
            self.DoHitByName("ReciveGift")
        sleep(2)
        return True

class MSmState_Loading(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_Login(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_Mail(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
    def Processing(self):
        sleep(1)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("Confirm")
        sleep(2)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("Personal")
        sleep(2)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("ReciveAll")
        sleep(2)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("Confirm")
        sleep(1)
        return True

class MSmState_MaterialAutoFighting(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        MaterialGiveUpPath = Path_cur + "\\MaterialGiveUp.png"
        self.MaterialGiveUpIdImage = cv2.imdecode(fromfile(MaterialGiveUpPath, dtype=uint8), -1)
        self.MaterialGiveUpIdImage = cv2.cvtColor(self.MaterialGiveUpIdImage, cv2.COLOR_BGR2GRAY)
        MaterialExitPath = Path_cur + "\\MaterialExit.png"
        self.MaterialExitIdImage = cv2.imdecode(fromfile(MaterialExitPath, dtype=uint8), -1)
        self.MaterialExitIdImage = cv2.cvtColor(self.MaterialExitIdImage, cv2.COLOR_BGR2GRAY)
    def Processing(self):
        while True:
            self.RefreshScreenShot()
            if self.IsPicMatching(self.MaterialGiveUpIdImage):
                self.DoHitByName("GiveUp")
                sleep(3)
            if self.IsPicMatching(self.MaterialExitIdImage):
                return True
            sleep(5)
        #self.TryLeaveJump("Leave",self.MaterialExitIdImage)

class MSmState_MaterialEnter0(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

    def Processing(self):
        self.DoAddTimes()
        return True

class MSmState_MaterialEnter1(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        # self.HasGottenAll = self.ReadPic("HasGottenAll")
    
    def Processing(self):
        # self.HitHandle.MouseWheelMove([733,333],[20,20],5)
        # sleep(3)
        # self.RefreshScreenShot()
        # bHasGottenAll = self.IsPicMatching(self.HasGottenAll)
        # if(bHasGottenAll):
        #     GHasGottenAll = True
        return True

class MSmState_MaterialsMain(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.Material160 = self.ReadPic("Material160")
        self.Material170 = self.ReadPic("Material170")
    
    def Processing(self):
        if MSmState.bMainCharacter == False:
            b170 = self.IsPicMatching(self.Material170)
            if b170:
                self.TryInnerJumpByPos([[74,438],[30,10]],self.Material160)

        return True

class MSmState_SystemMenuOpening(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_Wander(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        self.AdImages = []
        for file in os.listdir(Path_cur):
            if search(r'FuckAd', file):
                self.AdImages.append(cv2.imdecode(fromfile(Path_cur+ "\\"+file, dtype=uint8), -1))
                self.AdImages[len(self.AdImages) - 1] = cv2.cvtColor(self.AdImages[len(self.AdImages) - 1], cv2.COLOR_BGR2GRAY)

    def Processing(self):
        sleep(1)
        AdCloseMask = []
        HasAdExist = False
        self.RefreshScreenShot()
        for i in range(len(self.AdImages)):
            AdCloseMask.append( self.IsPicMatching(self.AdImages[i]))
            if(AdCloseMask[i]):
                HasAdExist = True

        while HasAdExist:
            for i in range(len(self.AdImages)):
                if AdCloseMask[i]:
                    self.DoHitByName("CloseAd" + str(i))
                    HasAdExist = False
                    sleep(0.5)
            self.RefreshScreenShot()
            for i in range(len(self.AdImages)):
                AdCloseMask[i] = self.IsPicMatching(self.AdImages[i])
                if(AdCloseMask[i]):
                    HasAdExist = True
        return True

class MSmState_TeamCommon(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.WaitingRoomIdImage = self.ReadPic("WaitingRoomIdImage")
        self.WaitingTeamIdImage = self.ReadPic("WaitingTeamIdImage")
        self.FindTeamIdImage = self.ReadPic("FindTeamIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")

    def Processing(self):
        #Main
        self.TryInnerJump("CreateRoom", self.AddTimesIdImage)
        #Add times
        self.DoAddTimes()  
        #Try enter waiting room
        self.TryInnerJump("Comfirm", self.WaitingRoomIdImage)
        #In Room
        self.TryInnerJump("FindTeam", self.FindTeamIdImage)
        sleep(1)
        self.TryLeaveJump("CreateTeam", self.FindTeamIdImage)
        #waiting 300s for finding team, 
        self.RefreshScreenShot()
        bStillInRoom = self.IsPicMatching(self.WaitingTeamIdImage)
        Iter = 0
        while bStillInRoom and Iter < 300:
            sleep(1)
            self.RefreshScreenShot()
            bStillInRoom = self.IsPicMatching(self.WaitingTeamIdImage)
            Iter = Iter + 1
        if Iter >= 300 and bStillInRoom == True:
            self.TryLeaveJump("Start",self.WaitingTeamIdImage)  
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True


class MSmState_Expedition(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.SelectBoss = []
        self.SelectHard = []
        for i in range(0,4):
            self.SelectBoss.append(self.ReadPic("SelectBoss" + str(i)))
            self.SelectHard.append(self.ReadPic("SelectHard" + str(i)))
        self.FindCreateTeamWidget = self.ReadPic("FindCreateTeamWidget")   
        self.FindSpoils = self.ReadPic("FindSpoils")   
        self.PrepareRoom = self.ReadPic("PrepareRoom")   
        self.CreateRoom = self.ReadPic("CreateRoom")   
        self.ExpeditionMain = self.ReadPic("ExpeditionMain")   
        self.FightingRoom = self.ReadPic("FightingRoom")   
        self.LeaveWidget = self.ReadPic("LeaveWidget")   
        self.SetLimitation = self.ReadPic("SetLimitation")   
        
    def WaitingForFightingFinished(self):
        self.RefreshScreenShot()
        bAutoFightingFinished = self.IsPicMatching(self.FindSpoils);
        self.DoHit([873,456],[10,10])
        sleep(0.1)
        self.DoHit([821,530],[10,10])
        IterCount = 0
        while bAutoFightingFinished == False and IterCount < 180:
            sleep(random.random()+0.5)
            self.DoHit([873,456],[10,10])
            sleep(0.1)
            self.DoHit([821,530],[10,10])
            self.RefreshScreenShot()
            bAutoFightingFinished = self.IsPicMatching(self.FindSpoils);
            IterCount = IterCount + 1

    def ProcessInternal(self, index):    
        bCanEnter = self.IsPicMatching(self.CreateRoom);
        if bCanEnter == True:
            #the first time
            self.TryInnerJump("CreateRoom",self.PrepareRoom)
            self.TryInnerJump("FindTeam",self.FindCreateTeamWidget)
            self.TryInnerJump("SetLimitation",self.SetLimitation)
            self.TryLeaveJump("CreateTeam",self.FindCreateTeamWidget)
            self.WaitingForFightingFinished()
            
            self.TryLeaveJump("SpoilsComfirm",self.FindSpoils)
            self.TryInnerJump("Exit",self.LeaveWidget)  
            self.TryInnerJump("LeaveToMain",self.ExpeditionMain)
            sleep(3)
            #leave to main widget to do the second time
            self.TryInnerJump("SelectBoss" + str(index),self.SelectBoss[index])
            self.TryInnerJump("SelectHardMode",self.SelectHard[index])
            bCanEnter = self.IsPicMatching(self.CreateRoom);
            if bCanEnter == True:
                self.TryInnerJump("CreateRoom",self.PrepareRoom)
                self.TryInnerJump("FindTeam",self.FindCreateTeamWidget)
                self.TryInnerJump("SetLimitation",self.SetLimitation)
                self.TryLeaveJump("CreateTeam",self.FindCreateTeamWidget)
                self.WaitingForFightingFinished()
            
                self.TryLeaveJump("SpoilsComfirm",self.FindSpoils)
                self.TryInnerJump("Exit",self.LeaveWidget) 
                if index < 3:
                    self.TryInnerJump("LeaveToMain",self.ExpeditionMain)
                    sleep(3)
                else:
                    self.TryLeaveJump("Leave",self.LeaveWidget)
            

    def Processing(self):
        for i in range(0,4):
            self.TryInnerJump("SelectBoss" + str(i),self.SelectBoss[i])
            self.TryInnerJump("SelectHardMode",self.SelectHard[i])
            self.ProcessInternal(i)

        return True


class MSmState_Elite(MSmState_TeamCommon): 
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.WaitingRoomIdImage = self.ReadPic("WaitingRoomIdImage")
        self.WaitingTeamIdImage = self.ReadPic("WaitingTeamIdImage")
        self.FindTeamIdImage = self.ReadPic("FindTeamIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")
        self.BuyMore = self.ReadPic("BuyMore")

    def Processing(self):
        #Main
        self.TryInnerJump("CreateRoom", self.AddTimesIdImage)
        #Add times
        self.DoAddTimes()  
        #Try enter waiting room
        self.TryInnerJump("Comfirm", self.WaitingRoomIdImage)
        #In Room
        self.TryInnerJump("FindTeam", self.FindTeamIdImage)
        sleep(1)
        self.TryLeaveJump("CreateTeam", self.FindTeamIdImage)
        #waiting 300s for finding team, 
        self.RefreshScreenShot()
        bStillInRoom = self.IsPicMatching(self.WaitingTeamIdImage)
        Iter = 0
        while bStillInRoom and Iter < 300:
            sleep(1)
            self.RefreshScreenShot()
            bStillInRoom = self.IsPicMatching(self.WaitingTeamIdImage)
            Iter = Iter + 1
        if Iter >= 300 and bStillInRoom == True:
            self.TryLeaveJump("Start",self.WaitingTeamIdImage)  
        self.WaitingForAutoFightingFinished()

        self.TryInnerJump("BuyMore", self.BuyMore)
        self.TryLeaveJump("BuyMoreConfirm", self.BuyMore)
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True

class MSmState_Pirate(MSmState_TeamCommon):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AuctionIdPic = self.ReadPic("AuctionIdPic")

    def CloseAuction(self):
        if self.IsPicMatching(self.AuctionIdPic):
            self.DoHitByName("CloseAuction")
            sleep(1)

class MSmState_NitePyramid(MSmState_TeamCommon):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_Dimension(MSmState_TeamCommon):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_MonsterPark(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.EnterMonsterParkIdImage = self.ReadPic("EnterMonsterParkIdImage")
        self.GetMoreIdImage = self.ReadPic("GetMoreIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")
        self.BuyMoreExp = self.ReadPic("BuyMoreExp")

    def Processing(self):
        self.TryInnerJump("Enter0", self.AddTimesIdImage)
        self.DoAddTimes()   
        self.TryInnerJump("Comfirm0", self.EnterMonsterParkIdImage)
        self.TryInnerJump("BuyMoreExp", self.BuyMoreExp)
        self.TryLeaveJump("Enter1", self.EnterMonsterParkIdImage)
        self.WaitingForAutoFightingFinished()
        self.TryInnerJump("Spend",self.GetMoreIdImage)
        sleep(3)
        self.TryLeaveJump("SpendComfirm",self.GetMoreIdImage)
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True


class MSmState_Tangyun(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.Select0 = self.ReadPic("Select0")
        self.Select1 = self.ReadPic("Select1")
        self.Select2 = self.ReadPic("Select2")
        self.SelectFoodIdImage = self.ReadPic("SelectFoodIdImage")
        self.SelectMaterialIdImage = self.ReadPic("SelectMaterialIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")

    def Processing(self):
        self.TryInnerJump("SelectFood",self.SelectFoodIdImage)
        self.TryInnerJump("Enter",self.SelectMaterialIdImage)
        self.TryInnerJump("Select0",self.Select0)
        self.TryInnerJump("Select1",self.Select1)
        self.TryInnerJump("Select2",self.Select2)
        self.TryLeaveJump("Enter2", self.SelectMaterialIdImage)
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True

class MSmState_Weekly(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")

    def Processing(self):
        self.TryInnerJump("Enter",self.AddTimesIdImage)
        self.DoAddTimes()
        self.TryLeaveJump("Comfirm", self.AddTimesIdImage)
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True

class MSmState_Wulin(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.Enter2IdImage = self.ReadPic("Enter2IdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")

    def Processing(self):
        self.TryInnerJump("Enter",self.Enter2IdImage)
        self.TryLeaveJump("Enter1", self.Enter2IdImage)
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True

class MSmState_PostProcess(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AutoFightingIdImage = self.ReadPic("AutoFightingIdImage")
        self.DailyIdImage = self.ReadPic("DailyIdImage")
        self.FriendsIdImage = self.ReadPic("FriendsIdImage")
        self.SendPopularityIdImage = self.ReadPic("SendPopularityIdImage")
        self.CanSendPopularityIdImage = self.ReadPic("CanSendPopularityIdImage")
        self.SysOpeningIdImage = self.ReadPic("SysOpeningIdImage")
        self.WeChatFriendsIdImage = self.ReadPic("WeChatFriendsIdImage")
        self.DailyComfirmIdImage = self.ReadPic("DailyComfirmIdImage")
        self.GotoWeChatIdImage = self.ReadPic("GotoWeChatIdImage")
        self.NotRemindIdImage = self.ReadPic("NotRemindIdImage")
        self.TradeEnterIdImage = self.ReadPic("TradeEnterIdImage")
        self.GotoGetTradeGoodsIdImage = self.ReadPic("GotoGetTradeGoodsIdImage")
        self.GotoGetTradeGoodsEnterIdImage = self.ReadPic("GotoGetTradeGoodsEnterIdImage")
        self.GoodsPackageOpenIdImage = self.ReadPic("GoodsPackageOpenIdImage")
        self.LeaveGetTradeGoodsIdImage = self.ReadPic("LeaveGetTradeGoodsIdImage")
        self.GetGoodsResultConfirmIdImage = self.ReadPic("GetGoodsResultConfirmIdImage")
        self.GoodsPackageClosedIdImage = self.ReadPic("GoodsPackageClosedIdImage")

    def Processing(self):
        self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
        self.TryInnerJump("Communication",self.FriendsIdImage)
        self.TryInnerJump("WeChatFriends",self.WeChatFriendsIdImage)
        self.RefreshScreenShot();
        SetPopularityPos = self.GetPicPos(self.CanSendPopularityIdImage, 0.997, cv2.TM_CCORR_NORMED)     
        if SetPopularityPos is not None:
            SetPopularityHitInfo = [[SetPopularityPos[0] + 20, SetPopularityPos[1]+53],[10,10]]
            self.TryInnerJumpByPos(SetPopularityHitInfo,self.SendPopularityIdImage)
            sleep(1)
            self.DoHitByName("SelectFreeGift")
            sleep(1)
            self.DoHitByName("Comfirm")
            sleep(1)
            self.TryLeaveJump("NotRemind",self.NotRemindIdImage)
            self.TryLeaveJump("CloseSelectFreeGift",self.SendPopularityIdImage)
        self.TryLeaveJump("CloseDaily",self.WeChatFriendsIdImage)

        bGotoTrade = False;
        GotoTradePos = self.GetPicPos(self.TradeEnterIdImage, 0.9)
        if GotoTradePos is not None:
            GotoTradePosHitInfo = [[GotoTradePos[0] + 20, GotoTradePos[1]+55],[10,10]]
            self.TryInnerJumpByPos(GotoTradePosHitInfo, self.GotoGetTradeGoodsIdImage)
            self.TryLeaveJump("GotoGetTradeGoods", self.GotoGetTradeGoodsIdImage)
            EnterTradePos = self.GetPicPos(self.GotoGetTradeGoodsEnterIdImage,0.9)
            if EnterTradePos is not None:
                self.TryLeaveJump("GotoGetTradeGoodsEnter", self.GotoGetTradeGoodsEnterIdImage)
                sleep(0.5)
                self.WaitUntil(self.GoodsPackageOpenIdImage)
                self.TryLeaveJump("CloseGoodsPackage", self.GoodsPackageOpenIdImage)
                #self.TryInnerJump("CloseGoodsPackage", self.GoodsPackageClosedIdImage)

                self.TryInnerJump("LeaveGetTradeGoods", self.LeaveGetTradeGoodsIdImage)
                self.TryLeaveJump("LeaveGetTradeGoods2", self.LeaveGetTradeGoodsIdImage)
                sleep(0.5)
                self.WaitUntil(self.GetGoodsResultConfirmIdImage)
                self.TryLeaveJump("GetGoodsResultConfirm", self.GetGoodsResultConfirmIdImage)
                
                bGotoTrade = True;
                sleep(0.3)
                self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            else:
                self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)

        self.TryInnerJump("Daily",self.DailyIdImage)
        sleep(0.5)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("DailyReciveAll")
        sleep(1)

        #self.TryLeaveJump("DailyComfirm",self.DailyComfirmIdImage)
        self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
        sleep(1)
        #goto wechat
        GotoWeChatHitPos = self.GetPicPos(self.GotoWeChatIdImage, 0.9)
        if GotoWeChatHitPos is not None:
            print("Find Goto WeChat")
            GotoWeChatHitInfo = [[GotoWeChatHitPos[0] + 311,GotoWeChatHitPos[1]+65],[10,10]]
            self.TryLeaveJumpByPos(GotoWeChatHitInfo,self.DailyIdImage)
            #now is under state system menu open
            self.TryInnerJump("CloseGotoWeChat",self.SysOpeningIdImage)
            self.TryInnerJump("Daily",self.DailyIdImage)
            sleep(0.5)
            for i in range(np.random.randint(2,4)):
                self.DoHitByName("DailyReciveAll")
            sleep(1)
            self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
            sleep(1)

        for i in range(np.random.randint(2,4)):
            self.DoHitByName("DailyReciveAll")
        sleep(1)
        self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
        self.TryLeaveJump("CloseDaily",self.DailyIdImage)
        self.TryLeaveJump("AutoFighting",self.DailyIdImage)
        self.TryInnerJump("AutoFighting",self.AutoFightingIdImage)
        sleep(1)
        for i in range(np.random.randint(1,2)):
            self.DoHitByName("UseFreeTime")
        self.TryLeaveJump("CloseAutoFighting",self.AutoFightingIdImage)
        return True
