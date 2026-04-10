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

WaittingMaxTimes = 600
HitMaxTimes = 30

class MSmState(object):
    """description of class"""
    bMainCharacter = False
    bViceCharacter = False
    bAllMaterialHasGotten = False
    CharacterIndex = 0
    bUseDebug = False
    bFastMode = False
    bUseMainWindowCapture = False
    HandleNumber_Main = 0
    HandleNumber_Render = 0
    HandleNumber_Keyboard = 0
    bFirstStart = True
    GlobalExitHitPos = [749,20]
    GlobalExitHitRect = [8, 8]
    
    ReturnChachaterSelectHitPos = [482,400]
    ReturnChachaterSelectHitRect = [20, 10]
    
    GlobalExitPic = cv2.imdecode(fromfile(frozen.app_path() + "\\Data\\Global\\GameEnd.png" , dtype=uint8), -1)
    GlobalExitPic = cv2.cvtColor(GlobalExitPic, cv2.COLOR_BGR2GRAY)

    CharacterSelectIdPic = cv2.imdecode(fromfile(frozen.app_path() + "\\Data\\CharacterSelect\\Identification\\0.png" , dtype=uint8), -1)
    CharacterSelectIdPic = cv2.cvtColor(CharacterSelectIdPic, cv2.COLOR_BGR2GRAY)

    ForceLeaveConfirmPic = cv2.imdecode(fromfile(frozen.app_path() + "\\Data\\CharacterSelect\\ForceLeaveConfirm.png" , dtype=uint8), -1)
    ForceLeaveConfirmPic = cv2.cvtColor(ForceLeaveConfirmPic, cv2.COLOR_BGR2GRAY)


    def __init__(self, StateName):
        left, top, right, bottom = win32gui.GetWindowRect(MSmState.HandleNumber_Render)
        self.ScreenShotImage = None
        self.ScreenShotImageRGB = None 
        self.ScreenShotWidth = right - left
        self.ScreenShotHeight = bottom - top
        
        if MSmState.bUseMainWindowCapture:
            self.ScreenShotWidth +=50
            self.ScreenShotHeight +=50

        #self.HandleNumber = HandleNumber
        self.HitHandle = DoScreenHit(MSmState.HandleNumber_Render, MSmState.HandleNumber_Keyboard)
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

    def DoHitByNameFast(self, hitname):
        print("Hit position by Name - " + hitname)
        self.HitHandle.HitPosition(self.HitInfo[hitname][0], self.HitInfo[hitname][1])
        #self.DoHit(self.HitInfo[hitname][0],self.HitInfo[hitname][1])

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
            MaxOpTimes = HitMaxTimes
            OpTimes = 0
            sleeptime = 1
            if(self.Name == "SystemMenuOpening" and TargetState.Name == "GameModeDefault"):
                sleeptime = 3
            if(self.Name == "SystemMenuOpening" and TargetState.Name == "FastJump"):
                sleeptime = 3

            while(True):
                self.DoHit(HitPos, HitRange)
                sleep(sleeptime)
                OpTimes += 1
                if TargetState.IsUnderState():
                    print("Jump success by reaching taget state " + TargetState.Name)
                    sleep(WaitingTime)
                    return 0
                if OpTimes > MaxOpTimes:
                    raise RuntimeError("Can not leave current state " + self.Name)

        else:
            print("State " + self.Name + "has no methon jump to " + TargetState.Name +", please check jump table")
            return 2
    
    def SaveScreenShot(self, Prefix=""):
        #MSmState.CharacterIndex;
        filedir = frozen.app_path() + "\\" + self.Name + "_AutoSave"
        if os.path.exists(filedir) == False:
            os.makedirs(filedir)
        cv2.imwrite(filedir+"\\"+ Prefix + str(MSmState.CharacterIndex)+".png", self.ScreenShotImageRGB)
        #cv2.imwrite(str(MSmState.CharacterIndex)+".png", self.ScreenShotImage)

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
        self.ScreenShotImageRGB = self.ScreenShotImage;
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
        #self.SaveScreenShot()

    def Processing(self):
        #do Nothing
        return True

    def ReadPicArray(self, PicName):
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name
        PicArray = []
        for cur_dir, sub_dir, included_file in walk(Path_cur):
            if included_file:
                for file in included_file:
                    if search(PicName, file):
                        img = cv2.imdecode(fromfile(Path_cur + "\\" + file, dtype=uint8), -1)
                        PicArray.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

        return PicArray

    def ReadPicMap(self):
        """读取当前state目录下所有png文件，存储到map中，键值为文件名不带后缀"""
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name
        PicMap = {}
        for cur_dir, sub_dir, included_file in walk(Path_cur):
            if included_file:
                for file in included_file:
                    if file.lower().endswith('.png'):
                        img = cv2.imdecode(fromfile(cur_dir + "\\" + file, dtype=uint8), -1)
                        # 获取文件名不带后缀作为键值
                        key = file[:-4] if file.lower().endswith('.png') else file
                        PicMap[key] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return PicMap

    def ReadPic(self, PicName):
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name
        img = cv2.imdecode(fromfile(Path_cur + "\\" + PicName + ".png", dtype=uint8), -1)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);

    def ForceReturnTocharacterSelect(self):
        if self.IsUnderState():
            return
        self.HitHandle.PressKeyboardESC()
        sleep(1)
        self.TryLeaveJumpByPic(self.ForceLeaveConfirmPic, self.ForceLeaveConfirmPic, 0.5, 0.9, "Force Leave Confirm")
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(MSmState.GlobalExitPic)
        while bSuccess == False:
            self.HitHandle.PressKeyboardESC()
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(MSmState.GlobalExitPic)
        self.TryInnerJumpByPos([MSmState.ReturnChachaterSelectHitPos, MSmState.ReturnChachaterSelectHitRect], MSmState.CharacterSelectIdPic)

    def WaitUntil(self, CheckPic, MaxTime = 600):
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        CurLoop = 0
        while bSuccess == False:
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic)
            CurLoop += 1
            if CurLoop > MaxTime:
                raise RuntimeError("InfiniteLoop")

    def TryInnerJumpByPos(self, HitPos, CheckPic):
        self.DoHit(HitPos[0],HitPos[1])
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        CurLoop = 0
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
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def TryInnerJump(self, HitName, CheckPic, MatchingThreshold = 0.8):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic, MatchingThreshold)
        CurLoop = 0
        while bSuccess == False:
            self.DoHitByName(HitName);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def TryLeaveJumpByPos(self, HitPos, CheckPic):
        self.DoHit(HitPos[0],HitPos[1])
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        CurLoop = 0
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
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def TryLeaveJump(self, HitName, CheckPic, MatchingThreshold = 0.8):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic, MatchingThreshold)
        CurLoop = 0
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
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")
    
            
    def TryLeaveJumpAuto(self, CheckPic, HitOffset, HitRange):
        sleep(1)
        self.RefreshScreenShot();
        AutoPos = self.GetPicPos(CheckPic, 0.9,cv2.TM_CCORR_NORMED)
        if AutoPos is None:
            return
        self.DoHit([AutoPos[0] + HitOffset[0], AutoPos[1] + HitOffset[1] + DoScreenHit.ApplicationWindowsTitleHeight], HitRange);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        CurLoop = 0
        while bSuccess == True:
            AutoPos = self.GetPicPos(CheckPic, 0.9,cv2.TM_CCORR_NORMED)
            if AutoPos is None:
                return
            self.DoHit([AutoPos[0] + HitOffset[0], AutoPos[1] + HitOffset[1] + DoScreenHit.ApplicationWindowsTitleHeight],HitRange);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def GetHitInfo(self, HitPic, HitRange = 0.5, MatchingThreshold = 0.9):
        sleep(0.5)
        self.RefreshScreenShot();
        HitPos = self.GetPicPos(HitPic, MatchingThreshold)
        if HitPos is None:
            return None
        HitPicHeight, HitPicWidth = HitPic.shape[:2]
        AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                      HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
        AutoHitRange = [int(HitPicWidth * HitRange), int(HitPicHeight * HitRange)]
        return [AutoHitPos, AutoHitRange]

    def TryLeaveJumpByPic(self, HitPic, CheckPic, HitRange = 0.5, MatchingThreshold = 0.8, OpName = ""):
        sleep(1)
        print("TryLeaveJumpByPic matching threshold = " + str(MatchingThreshold) + "OpName = " + OpName)
        self.RefreshScreenShot();
        HitPos = self.GetPicPos(HitPic, MatchingThreshold)
        if HitPos is None:
            return
        
        # 根据HitPic的大小自动生成HitInfo，点击位置为HitPic的中心
        HitPicHeight, HitPicWidth = HitPic.shape[:2]
        AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                      HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
        AutoHitRange = [int(HitPicWidth * HitRange), int(HitPicHeight * HitRange)]
        
        self.DoHit(AutoHitPos, AutoHitRange)
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic, MatchingThreshold)
        CurLoop = 0
        while bSuccess == True:
# 更新HitPos
            HitPos = self.GetPicPos(HitPic, MatchingThreshold)
            if HitPos is not None:
                AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                              HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
            self.DoHit(AutoHitPos, AutoHitRange)
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic, MatchingThreshold)
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")
    def DoHitByPic(self, HitPic, HitRange = 0.5, MatchingThreshold = 0.8, HitTimes = 3):
        sleep(1)
        self.RefreshScreenShot();
        HitPos = self.GetPicPos(HitPic, MatchingThreshold)
        if HitPos is None:
            return
        HitPicHeight, HitPicWidth = HitPic.shape[:2]
        AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                      HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
        AutoHitRange = [int(HitPicWidth * HitRange), int(HitPicHeight * HitRange)]
        for i in range(HitTimes):
            self.DoHit(AutoHitPos, AutoHitRange)

    def TryInnerJumpByPic(self, HitPic, CheckPic, HitRange = 0.5, MatchingThreshold = 0.8, OpName =""):
        sleep(1)
        print("TryInnerJumpByPic = " + str(MatchingThreshold) + "OpName = " + OpName)
        self.RefreshScreenShot();
        HitPos = self.GetPicPos(HitPic, MatchingThreshold)
        if HitPos is None:
            return
        
        # 根据HitPic的大小自动生成HitInfo，点击位置为HitPic的中心
        HitPicHeight, HitPicWidth = HitPic.shape[:2]
        AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                      HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
        AutoHitRange = [int(HitPicWidth * HitRange), int(HitPicHeight * HitRange)]
        
        self.DoHit(AutoHitPos, AutoHitRange)
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic, MatchingThreshold)
        CurLoop = 0
        while bSuccess == False:
            # 更新HitPos
            HitPos = self.GetPicPos(HitPic, MatchingThreshold)
            if HitPos is not None:
                AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                              HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
            self.DoHit(AutoHitPos, AutoHitRange)
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess or self.IsPicMatching(CheckPic, MatchingThreshold)
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def ExecuteSequenceByFolder(self, FolderName, HitRange = 0.5, MatchingThreshold = 0.8):
        """
        从指定文件夹读取HitPic和CheckPic序列并执行操作
        
        文件夹结构应为:
        - HitPic_0.png, HitPic_1.png, ... (点击图片序列)
        - CheckPic_0_L.png, CheckPic_0_J.png, CheckPic_1_L.png, CheckPic_1_J.png, ... (检查图片序列)
        
        L后缀表示使用TryLeaveJumpByPic (点击直到CheckPic消失)
        J后缀表示使用TryInnerJumpByPic (点击直到CheckPic出现)
        注意：同一个索引的L和J后缀不会同时存在
        """
        Path_cur = frozen.app_path() + "\\Data\\" + self.Name + "\\" + FolderName
        
        # 读取所有HitPic
        HitPics = {}
        for file in os.listdir(Path_cur):
            if file.startswith("HitPic_") and file.endswith(".png"):
                # 提取索引号，例如 HitPic_0.png -> index="0"
                index = file.replace("HitPic_", "").replace(".png", "")
                img = cv2.imdecode(fromfile(Path_cur + "\\" + file, dtype=uint8), -1)
                HitPics[index] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 读取所有CheckPic
        CheckPics = {}
        for file in os.listdir(Path_cur):
            if file.startswith("CheckPic_") and file.endswith(".png"):
                # 提取索引号和后缀，例如 CheckPic_0_L.png -> index="0", suffix="L"
                parts = file.replace("CheckPic_", "").replace(".png", "").rsplit("_", 1)
                if len(parts) == 2:
                    index, suffix = parts
                    img = cv2.imdecode(fromfile(Path_cur + "\\" + file, dtype=uint8), -1)
                    CheckPics[index] = (suffix, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        
        # 按索引排序执行操作
        sorted_indices = sorted(HitPics.keys(), key=lambda x: int(x))
        
        for index in sorted_indices:
            if index not in HitPics:
                continue
                
            HitPic = HitPics[index]
            
            if index not in CheckPics:
                # 如果没有对应的CheckPic，只点击一次
                self.RefreshScreenShot()
                HitPos = self.GetPicPos(HitPic, MatchingThreshold)
                if HitPos is None:
                    raise RuntimeError(f"Cannot find HitPic_{index}")
                
                HitPicHeight, HitPicWidth = HitPic.shape[:2]
                AutoHitPos = [HitPos[0] + int(HitPicWidth / 2), 
                              HitPos[1] + int(HitPicHeight / 2) + DoScreenHit.ApplicationWindowsTitleHeight]
                AutoHitRange = [int(HitPicWidth * HitRange), int(HitPicHeight * HitRange)]
                self.DoHit(AutoHitPos, AutoHitRange)
            else:
                # 根据后缀执行不同操作
                suffix, CheckPic = CheckPics[index]
                
                if suffix == "L":
                    # L后缀: 点击直到CheckPic消失
                    self.TryLeaveJumpByPic(HitPic, CheckPic, HitRange, MatchingThreshold)
                elif suffix == "J":
                    # J后缀: 点击直到CheckPic出现
                    self.TryInnerJumpByPic(HitPic, CheckPic, HitRange, MatchingThreshold)
                else:
                    # 其他后缀默认使用TryInnerJumpByPic
                    self.TryInnerJumpByPic(HitPic, CheckPic, HitRange, MatchingThreshold)
            
            sleep(0.5)
        
        return True

    def TryLeaveJump2(self, HitName, CheckPic, CheckPic2):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
        CurLoop = 0
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
            CurLoop += 1
            if CurLoop > HitMaxTimes:
                raise RuntimeError("InfiniteLoop")

    def DoAddTimes(self):
        return
        for i in range(np.random.randint(5,7)):
            self.DoHitByName("AddTimes")

    def CloseAuction(self):
        return

    def WaitingForAutoFightingFinished(self):
        self.RefreshScreenShot()
        bAutoFightingFinished = self.IsPicMatching(self.ExitIdImage);
        CurLoop = 0
        while bAutoFightingFinished == False:
            sleep(5)
            self.RefreshScreenShot()
            self.CloseAuction()
            bAutoFightingFinished = self.IsPicMatching(self.ExitIdImage);
            CurLoop += 1
            if CurLoop > WaittingMaxTimes:
                raise RuntimeError("InfiniteLoop")

class MSmState_CharacterSelect(MSmState):
    CurrentSelectedCharacterIndex = 0
    bUseInverseSelect=0
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
    FastJumpType = 0;
    def __init__(self, StateName):
        super().__init__(StateName)
        self.Enter = self.ReadPic("Enter")
        self.Enter2 = self.ReadPic("Enter2")
        self.EnterConfirm = self.ReadPic("EnterConfirm")
        self.FinishConfirm = self.ReadPic("FinishConfirm")
        self.OpenTableIdenty = self.ReadPic("OpenTableIdenty")
        self.UseAllTimes = self.ReadPic("UseAllTimes")
        self.MPEnterDefault = self.ReadPic("MPEnterDefault")
        self.MPEnter = []
        self.MPIdenty = []
        for i in range(0,5):
            self.MPEnter.append(self.ReadPic("MPEnter" + str(i)))
        for i in range(0,3):
            self.MPIdenty.append(self.ReadPic("MPIdenty" + str(i)))
        self.NPIdenty = []
        for i in range(0,4):
            self.NPIdenty.append(self.ReadPic("NPIdenty" + str(i)))
        self.NPEnter = self.ReadPic("NPEnter")

    def Processing(self):
        self.TryInnerJump("OpenTable", self.OpenTableIdenty)
        self.RefreshScreenShot();
        bUseAllTimes = self.GetPicPos(self.UseAllTimes, 0.999, cv2.TM_CCORR_NORMED)               
        if bUseAllTimes is not None:
            self.TryLeaveJump("CloseTable", self.OpenTableIdenty)
            return True
        if MSmState_FastJump.FastJumpType == 1:
            self.HitHandle.DoMousePull(self.HitInfo["DoMouseWheel"][0],self.HitInfo["DoMouseWheel"][1],[0,-300], 20, 3)
            sleep(3)
            self.RefreshScreenShot();
            FastMPPos = None
            for i in range(0,3):
               if FastMPPos is None:
                    FastMPPos = self.GetPicPos(self.MPIdenty[i], 0.982, cv2.TM_CCORR_NORMED)     
        
            if FastMPPos is not None:
                self.TryInnerJump("OpenTable", self.OpenTableIdenty)
                FastMPEnterPos = [[FastMPPos[0] + 360, FastMPPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight + 16],[12,5]]
                self.TryInnerJumpByPos(FastMPEnterPos, self.Enter2)
                self.RefreshScreenShot();
                FastMPPos = None
                for i in range(4,5):
                    if FastMPPos is not None:
                        break
                    FastMPPos = self.GetPicPos(self.MPEnter[i], 0.998, cv2.TM_CCORR_NORMED)    
                if FastMPPos is None:
                    FastMPPos = self.GetPicPos(self.MPEnterDefault, 0.998, cv2.TM_CCORR_NORMED)
                if FastMPPos is not None:
                    FastMPEnterPos = [[FastMPPos[0] + 40, FastMPPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight],[10,10]]
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
        else:
            self.RefreshScreenShot();
            FastNPPos = None
            for i in range(0,4):
               if FastNPPos is None:
                    FastNPPos = self.GetPicPos(self.NPIdenty[i], 0.982, cv2.TM_CCORR_NORMED)     
            if FastNPPos is not None:
                FastNPEnterPos = [[FastNPPos[0] + 360, FastNPPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight +16],[12,5]]
                self.TryInnerJumpByPos(FastNPEnterPos, self.NPEnter)
                self.RefreshScreenShot();
                FastNPPos = None
                FastNPPos = self.GetPicPos(self.Enter, 0.98, cv2.TM_CCORR_NORMED)  
                if FastNPPos is not None:
                    self.RefreshScreenShot();
                    FastNPEnterPos = self.GetPicPos(self.Enter, 0.99, cv2.TM_CCORR_NORMED)
                    if FastNPEnterPos is not None:
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
    


class MSmState_Exchange(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.SoldPage = self.ReadPic("SoldPage")
        self.ShowCaseFull = self.ReadPic("ShowCaseFull")
        self.GoodsPics = self.ReadPicArray("Goods")
        self.GetBackAndGetMoney = self.ReadPic("GetBackAndGetMoney")
        self.SoldSetting = self.ReadPic("SoldSetting")
        self.SetLowestPrice = self.ReadPic("SetLowestPrice")
        self.SoldConfirm = self.ReadPic("SoldConfirm")
        self.FinalConfirm = self.ReadPic("FinalConfirm")


    def Processing(self): 
        self.TryInnerJump("SoldPage", self.SoldPage)
        self.TryInnerJump("GetBackAndGetMoney", self.GetBackAndGetMoney)
        for i in range(0,2):
            self.DoHitByName("GetBack")
        for i in range(0,4):
            self.DoHitByName("GetMoney")

        #ShowCaseFullPos = self.GetPicPos(self.ShowCaseFull, 0.99, cv2.TM_CCORR_NORMED)
        #if ShowCaseFullPos is not None:
        #    return True
        sleep(1)
        self.RefreshScreenShot();
        self.SaveScreenShot()
        for i in range(len(self.GoodsPics)):
            GoodsPos = self.GetPicPos(self.GoodsPics[i], 0.95, cv2.TM_CCORR_NORMED)
            if GoodsPos is not None:
                if GoodsPos[0] < 450:
                    continue
                GoodsPosHitInfo = [[GoodsPos[0] + 20, GoodsPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight + 20],[5,5]]
                self.TryInnerJumpByPos(GoodsPosHitInfo, self.SoldSetting)
                for i in range(0,2):
                    self.DoHitByName("SetMax")
                for i in range(0,20):
                     self.DoHitByNameFast("SetLowestPrice")
                     sleep(np.random.randint(20,80) / 1000)
                self.TryInnerJump("SetLowestPrice", self.SetLowestPrice)
                self.TryInnerJump("DoSold", self.SoldConfirm)
                self.TryInnerJump("SoldConfirm", self.FinalConfirm)
                self.TryLeaveJump("FinalConfirm", self.FinalConfirm)



        return True

class MSmState_GameModeDefault(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.MaterialEnterIdImage = self.ReadPic("MaterialEnterIdentify")
        self.EliteEnterIdImage = self.ReadPic("EliteEnterIdImage")
        self.EliteCount = 9
        self.EliteEnterIdImages = []
        for i in range(0, self.EliteCount ):
            self.EliteEnterIdImages.append(self.ReadPic("EliteEnterIdImage" + str(i)))

        self.TangyunEnterIdImage = self.ReadPic("TangyunEnterIdImage")
        self.PirateEnterIdImage = self.ReadPic("PirateEnterIdImage")
        self.NitePyramidEnterIdImage = self.ReadPic("NitePyramidEnterIdImage")
        self.WeeklyEnterIdImage = self.ReadPic("WeeklyEnterIdImage")
        self.MonsterParkEnterIdImage = self.ReadPic("MonsterParkEnterIdImage")
        self.WulinEnterIdImage = self.ReadPic("WulinEnterIdImage")
        self.DimensionEnterIdImage = self.ReadPic("DimensionEnterIdImage")
        self.ExpeditionEnterIdImage = self.ReadPic("ExpeditionEnterIdImage")

        self.PicMap = self.ReadPicMap()


    def AddEnter(self, ModeName, IdPic, MatchingThreshold = 0.8):
        Pos = self.GetPicPos(IdPic, MatchingThreshold)
        if Pos is None:
            print("Cannot find "+ ModeName + " Enter")
        else:
            print("find "+ ModeName + " Enter")
            self.JumpInfo[ModeName] = [[Pos[0]+ 75, Pos[1]+ 47 + DoScreenHit.ApplicationWindowsTitleHeight],[15, 15]]

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
        IsLargeVersion = self.IsPicMatching(self.PicMap["IsLargeVersion"], 0.975)
        if IsLargeVersion == True:
            self.AddEnter("Material", self.MaterialEnterIdImage)        
            self.AddEnter("Elite", self.EliteEnterIdImage,0.85)
            for i in range(0, self.EliteCount ):
                if "Elite" not in self.JumpInfo:
                    self.AddEnter("Elite", self.EliteEnterIdImages[i],0.85)


            self.AddEnter("Tangyun", self.TangyunEnterIdImage)        
            self.AddEnter("Pirate", self.PirateEnterIdImage)        
            self.AddEnter("NitePyramid", self.NitePyramidEnterIdImage)        
            self.AddEnter("Weekly", self.WeeklyEnterIdImage)     
            self.AddEnter("SpecialWeekly", self.WeeklyEnterIdImage)          
            self.AddEnter("Wulin", self.WulinEnterIdImage)        
            self.AddEnter("Dimension", self.DimensionEnterIdImage)        
            self.AddEnter("MonsterPark", self.MonsterParkEnterIdImage)        
            self.AddEnter("Expedition", self.ExpeditionEnterIdImage)
        else:
            self.AddEnter("Material", self.PicMap["MiniMaterialEnterIdentify"], 0.95)        
            self.AddEnter("Elite", self.PicMap["MiniEliteEnterIdImage"], 0.95)
            for i in range(0, self.EliteCount ):
                if "Elite" not in self.JumpInfo:
                    self.AddEnter("Elite", self.PicMap["MiniEliteEnterIdImage" + str(i)], 0.95)


            self.AddEnter("Tangyun", self.PicMap["MiniTangyunEnterIdImage"], 0.95)        
            self.AddEnter("Pirate", self.PicMap["MiniPirateEnterIdImage"], 0.95)        
            self.AddEnter("NitePyramid", self.PicMap["MiniNitePyramidEnterIdImage"], 0.95)        
            self.AddEnter("Weekly", self.PicMap["MiniWeeklyEnterIdImage"], 0.95)     
            self.AddEnter("SpecialWeekly", self.PicMap["MiniWeeklyEnterIdImage"], 0.95)          
            self.AddEnter("Wulin", self.PicMap["MiniWulinEnterIdImage"], 0.95)               
            self.AddEnter("MonsterPark", self.PicMap["MiniMonsterParkEnterIdImage"], 0.95)        
            self.AddEnter("Expedition", self.PicMap["MiniExpeditionEnterIdImage"], 0.95)       

        return True

class MSmState_GuildInfo(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.TreeGift = self.ReadPic("TreeGift")
        self.GuildinfoIdImage = self.ReadPicMap()

    def Processing(self):
        sleep(1)
        if MSmState.bMainCharacter == False:
            self.TryInnerJump("ReciveTreeGift", self.TreeGift, 0.9)
            for i in range(np.random.randint(1,3)):
                self.DoHitByName("ReciveTreeGift")
            self.TryLeaveJump("CloseTreeGift", self.TreeGift, 0.9)
        sleep(1)
        if MSmState.bMainCharacter == True:
            self.TryLeaveJumpByPic(self.GuildinfoIdImage["GuildBossEnter"], self.GuildinfoIdImage["GuildBossEnter"], 0.5, 0.9)
            CanEnter = self.GetHitInfo(self.GuildinfoIdImage["EnterTimes"], 0.9)
            if CanEnter is not None:
                for i in range(np.random.randint(3,5)):
                    self.DoHit(CanEnter[0], CanEnter[1])
                self.TryLeaveJumpByPic(self.GuildinfoIdImage["Confirm"], self.GuildinfoIdImage["Confirm"], 0.5, 0.9)
                self.WaitUntil(self.GuildinfoIdImage["Leave"])
                self.TryLeaveJumpByPic(self.GuildinfoIdImage["Leave"], self.GuildinfoIdImage["Leave"], 0.5, 0.9)
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

class MSmState_Material(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        MaterialGiveUpPath = Path_cur + "\\MaterialGiveUp.png"
        self.MaterialGiveUpIdImage = cv2.imdecode(fromfile(MaterialGiveUpPath, dtype=uint8), -1)
        self.MaterialGiveUpIdImage = cv2.cvtColor(self.MaterialGiveUpIdImage, cv2.COLOR_BGR2GRAY)
        MaterialExitPath = Path_cur + "\\MaterialExit.png"
        self.MaterialExitIdImage = cv2.imdecode(fromfile(MaterialExitPath, dtype=uint8), -1)
        self.MaterialExitIdImage = cv2.cvtColor(self.MaterialExitIdImage, cv2.COLOR_BGR2GRAY)

        self.Enter0 = self.ReadPic("Enter0")
        self.Enter1 = self.ReadPic("Enter1")
        self.AllMaterialsGotten = self.ReadPic("AllMaterialsGotten")
        self.MaterialMain = self.ReadPic("MaterialMain")
        self.SysOpeningIdImage = self.ReadPic("SysOpeningIdImage")


    def Processing(self):
        self.TryInnerJump("Enter0",self.Enter0)
        self.TryInnerJump("Enter1",self.Enter1)
        # if MSmState_PostProcess.bDefault == False or MSmState_PostProcess.bAdditionalMaterial == True:
        #     self.HitHandle.DoMousePull(self.HitInfo["CheckNeededPull"][0],self.HitInfo["CheckNeededPull"][1],[0,-300], 20, 3)
        #     sleep(2)
        #     self.RefreshScreenShot()
        #     TempPos = self.GetPicPos(self.AllMaterialsGotten, 0.95)
        #     if TempPos is not None:
        #         self.TryLeaveJump("Cancel0",self.Enter1)
        #         self.TryLeaveJump("CloseMaterial",self.MaterialMain)
        #         self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
        #         MSmState.bAllMaterialHasGotten = True
        #         return True


        self.TryLeaveJump("Enter2",self.Enter1)
        curloop = 0
        while True:
            self.RefreshScreenShot()
            if self.IsPicMatching(self.MaterialGiveUpIdImage):
                self.DoHitByName("GiveUp")
                sleep(3)
            if self.IsPicMatching(self.MaterialExitIdImage):
                self.SaveScreenShot()
                break
            sleep(5)
            curloop = curloop + 1
            if curloop > 100:
                raise RuntimeError("Material exit timeout")
            
        # MSmState.bAllMaterialHasGotten = False
        self.TryLeaveJump("Exit", self.MaterialExitIdImage)
        


class MSmState_SystemMenuOpening(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_Wander(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.PicMap = self.ReadPicMap()
        Path_cur = frozen.app_path() + "\\Data\\" + StateName
        self.AdImages = []
        for file in os.listdir(Path_cur):
            if search(r'FuckAd', file):
                self.AdImages.append(cv2.imdecode(fromfile(Path_cur+ "\\"+file, dtype=uint8), -1))
                self.AdImages[len(self.AdImages) - 1] = cv2.cvtColor(self.AdImages[len(self.AdImages) - 1], cv2.COLOR_BGR2GRAY)

    def GetChangePresetHitInfo(self):
        self.RefreshScreenShot()
        HitPos = self.GetHitInfo(self.PicMap["ChangePreset0"], 0.5, 0.85)
        if HitPos is None:
            HitPos = self.GetHitInfo(self.PicMap["ChangePreset1"], 0.5, 0.85)
        return HitPos

    def Processing(self):
        sleep(1)
        # if MSmState.bFirstStart == True and MSmState.bMainCharacter == True:
        #      ChangePresetHitInfo = self.GetChangePresetHitInfo()
        #      while ChangePresetHitInfo is None:
        #          self.HitHandle.DoMousePull(self.HitInfo["ChangePreset"][0],self.HitInfo["ChangePreset"][1],[200,0], 15, 5)
        #          sleep(2)
        #          ChangePresetHitInfo = self.GetChangePresetHitInfo()

        #      self.TryInnerJumpByPic(self.PicMap["ChangePreset0"], self.PicMap["ChangePreset1"], 0.5, 0.9)
        #      self.DoHitByName("Preset1")
        #      sleep(0.5)
        #      self.DoHitByName("Preset1")
        #      MSmState.bFirstStart = False

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
        #self.HitHandle.PressKeyboard()
        self.DoHitByName("AutoSkill")
        return True

class MSmState_DailyTask(MSmState):
    """日常任务状态 - 处理日常任务相关操作"""
    def __init__(self, StateName):
        super().__init__(StateName)
        # 加载日常任务相关的图片资源
        self.DailyTaskPic = self.ReadPicMap()


    def OpenMainDailyTaskWidget(self):
        self.TryInnerJump("OpenSystemMenu", self.DailyTaskPic["SysOpeningIdImage"])
        self.TryInnerJump("OpenDailyTask", self.DailyTaskPic["DailyTaskMain"])

    def CloseMainDailyTaskWidget(self):
        self.TryLeaveJump("OpenSystemMenu", self.DailyTaskPic["DailyTaskMain"])
        self.TryLeaveJump("OpenSystemMenu", self.DailyTaskPic["SysOpeningIdImage"])

    def GetAutoTaskRunningState(self):
        # 获取自动任务当前的运行状态
        # 返回值可以是 "NotStarted", "Running", "Completed" 等
        self.RefreshScreenShot()
        if self.IsPicMatching(self.DailyTaskPic["AutoTaskRunning"], 0.7) or self.IsPicMatching(self.DailyTaskPic["AutoTaskRunning0"], 0.85) or self.IsPicMatching(self.DailyTaskPic["AutoTaskRunning1"], 0.95):
            return True
        else:         
            return False

    def SelectTaskPrefer(self):
        self.RefreshScreenShot()
        self.DoHitByPic(self.DailyTaskPic["TaskType0"], 0.5, 0.75)
        self.TryLeaveJumpByPic(self.DailyTaskPic["CloseRewardDetail"], self.DailyTaskPic["CloseRewardDetail"], 0.3, 0.98)
        self.DoHitByPic(self.DailyTaskPic["TaskType1"], 0.5, 0.75)
        self.TryLeaveJumpByPic(self.DailyTaskPic["CloseRewardDetail"], self.DailyTaskPic["CloseRewardDetail"], 0.3, 0.98)
        self.DoHitByPic(self.DailyTaskPic["TaskType2"], 0.5, 0.75)
        self.TryLeaveJumpByPic(self.DailyTaskPic["CloseRewardDetail"], self.DailyTaskPic["CloseRewardDetail"], 0.3, 0.98)

    def Processing(self):
        # 处理日常任务逻辑
        self.OpenMainDailyTaskWidget()
        self.TryInnerJumpByPic(self.DailyTaskPic["TaskSettings"], self.DailyTaskPic["TaskSettingsSub"])
        self.RefreshScreenShot()
        IsSettingsOK = self.IsPicMatching(self.DailyTaskPic["TaskSettingsCheck0"], 0.95) and self.IsPicMatching(self.DailyTaskPic["TaskSettingsCheck1"], 0.95)
        if IsSettingsOK == False:
            self.TryLeaveJumpByPic(self.DailyTaskPic["CheckState1"], self.DailyTaskPic["CheckState1"], 0.5, 0.95)#clean all check state
            self.TryLeaveJumpByPic(self.DailyTaskPic["CheckDisplay0"], self.DailyTaskPic["CheckDisplay0"], 0.5, 0.996)
            self.TryInnerJump("DisplayDailyTask", self.DailyTaskPic["CheckState1"], 0.95)
            self.TryLeaveJumpByPic(self.DailyTaskPic["ApplySettings"], self.DailyTaskPic["ApplySettings"])             
        else:
             self.TryLeaveJumpByPic(self.DailyTaskPic["ApplySettings"], self.DailyTaskPic["ApplySettings"])
        self.CloseMainDailyTaskWidget()

        if 1: #委托相关
            self.TryInnerJump("OpenSystemMenu",self.DailyTaskPic["SysOpeningIdImage"] )
            self.TryInnerJump("Commission",self.DailyTaskPic["CommissionMain"])
            for i in range(0,3):
                self.SelectTaskPrefer()
                for i in range(np.random.randint(2,3)):
                    self.DoHitByName("ReciveCommission")
                for i in range(np.random.randint(2,3)):
                    self.DoHitByName("CloseCommissionRevice")
            CommissionFinished = self.GetPicPos(self.DailyTaskPic["CommissionFinished"], 0.95, cv2.TM_CCORR_NORMED)
            NoCommissionTicket = self.GetPicPos(self.DailyTaskPic["NoCommissionTicket"], 0.999, cv2.TM_CCORR_NORMED)
            if (NoCommissionTicket is None) and (CommissionFinished is None):
                self.TryInnerJump("AlignCommission",self.DailyTaskPic["CommisionReciveReady"],0.95)
                self.TryInnerJump("StartCommission",self.DailyTaskPic["CommisionStartReady"],0.95)
                self.TryInnerJump("DoCommission",self.DailyTaskPic["CommissionAllFinished"],0.95)
                if MSmState.bMainCharacter == True:
                    self.TryInnerJumpByPic(self.DailyTaskPic["GetMoreReward"], self.DailyTaskPic["BuyAddition"], 0.5, 0.98)
                    self.TryLeaveJumpByPic(self.DailyTaskPic["BuyAddition"], self.DailyTaskPic["BuyAddition"], 0.5, 0.95) 
            self.TryLeaveJump("CloseCommissionMain",self.DailyTaskPic["CommissionMain"])
            self.TryLeaveJump("OpenSystemMenu",self.DailyTaskPic["SysOpeningIdImage"])

        #self.TryInnerJumpByPic(self.DailyTaskPic["MysticAreaUnselect"], self.DailyTaskPic["MysticAreaSelect"], 0.5, 0.98)
                

        #开始跑日常任务
        self.TryInnerJumpByPic(self.DailyTaskPic["TaskClose"], self.DailyTaskPic["TaskOpen"], 0.5, 0.98)

        self.TryInnerJumpByPic(self.DailyTaskPic["BossTaskOpen"], self.DailyTaskPic["BossTaskClose"], 0.5, 0.9)  

        DailyTaskHitInfo = self.GetHitInfo(self.DailyTaskPic["TaskTinyIcon"])
        curloop = 0
        StillHasTask = DailyTaskHitInfo is not None
        bCanFastTransfer = False
        while StillHasTask :
            curloop = curloop + 1
            if curloop > 180: #超过半小时
                raise RuntimeError("DailyTask Loop Timeout")
            IsRunning = self.GetAutoTaskRunningState()
            if IsRunning == False and DailyTaskHitInfo is not None:
                self.DoHit(DailyTaskHitInfo[0], DailyTaskHitInfo[1])
            FastFinished = self.GetHitInfo(self.DailyTaskPic["FastFinished"], 0.5, 0.95) 
            if FastFinished is not None:
                self.TryInnerJumpByPic(self.DailyTaskPic["MysticAreaUnselect"], self.DailyTaskPic["MysticAreaSelect"], 0.5, 0.98)
                    
                for i in range(6): #防止切图黑屏的时候误判
                    self.TryLeaveJumpByPic(self.DailyTaskPic["FastFinished"], self.DailyTaskPic["FastFinished"], 0.5, 0.95)
                    sleep(1)
                bCanFastTransfer = True
                sleep(15)
            else:
                self.TryLeaveJumpByPic(self.DailyTaskPic["ContinueProcess"], self.DailyTaskPic["ContinueProcess"], 0.5, 0.9) 

            if IsRunning and bCanFastTransfer:
                for i in range(6): #防止切图黑屏的时候误判
                    self.TryLeaveJumpByPic(self.DailyTaskPic["FastTransfer"], self.DailyTaskPic["FastTransfer"], 0.5, 0.9) 
                bCanFastTransfer = False
            if self.IsPicMatching(self.DailyTaskPic["Confirm"], 0.9):
                self.TryLeaveJumpByPic(self.DailyTaskPic["Confirm"], self.DailyTaskPic["Confirm"], 0.5, 0.9) 
            
            self.TryLeaveJumpByPic(self.DailyTaskPic["ContinueProcess"], self.DailyTaskPic["ContinueProcess"], 0.5, 0.9) 
            self.TryLeaveJumpByPic(self.DailyTaskPic["MoveToVillage"], self.DailyTaskPic["MoveToVillage"], 0.5, 0.95)   
            GetAdditonHitInfo = self.GetHitInfo(self.DailyTaskPic["GetAddition"], 0.5, 0.95)
            if GetAdditonHitInfo is None:
                self.TryLeaveJumpByPic(self.DailyTaskPic["Confirm"], self.DailyTaskPic["Confirm"], 0.5, 0.9) 
            StillHasTask = False
            for i in range(10):
                DailyTaskHitInfo = self.GetHitInfo(self.DailyTaskPic["TaskTinyIcon"])
                StillHasTask =  StillHasTask or  DailyTaskHitInfo is not None   
        
        sleep(15) #等待自动回村
        if MSmState.bMainCharacter == True:
            self.TryLeaveJumpByPic(self.DailyTaskPic["GetAddition"], self.DailyTaskPic["GetAddition"], 0.5, 0.95)   
            self.TryLeaveJumpByPic(self.DailyTaskPic["BuyAddition"], self.DailyTaskPic["BuyAddition"], 0.5, 0.95) 
        else:
            self.TryLeaveJumpByPic(self.DailyTaskPic["Confirm"], self.DailyTaskPic["Confirm"], 0.5, 0.85) 
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
        self.TryInnerJump("CreateRoom", self.FindTeamIdImage)
        self.TryInnerJump("CreateTeam", self.AddTimesIdImage)
        self.TryLeaveJump("Comfirm", self.AddTimesIdImage)
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True        

class MSmState_Expedition(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.PicMap = self.ReadPicMap()
    
    def IsFinished(self):
        self.RefreshScreenShot()
        return self.IsPicMatching(self.PicMap["FinishAll"], 0.95)     

    
    def SelectBossMaxLevel(self):
        self.RefreshScreenShot()
        HitInfo = self.GetHitInfo(self.PicMap["Chaos"], 0.5, 0.95)
        if HitInfo is None:
            HitInfo = self.GetHitInfo(self.PicMap["Difficult"], 0.5, 0.95)
        for i in range(np.random.randint(2,4)):
            self.DoHit(HitInfo[0], HitInfo[1])
        self.TryInnerJumpByPic(self.PicMap["TeamMode0"], self.PicMap["FastTeam"], 0.5, 0.95, "Select FastTeam")

    def IsBossFightFinished(self, bosstype):
        self.RefreshScreenShot()
        if bosstype == 0:
            return self.IsPicMatching(self.PicMap["ReturnToMain"], 0.95)
        elif bosstype == 1:
            return self.IsPicMatching(self.PicMap["Confirm2"], 0.95)
        else:
            return self.IsPicMatching(self.PicMap["Confirm2"], 0.95)

    def WaitForFinished(self, bosstype):
        self.RefreshScreenShot()
        curloop = 0
        maxloop = 10
        if bosstype == 0:
            returniconname = "ReturnToMain0"
        elif bosstype == 1:
            returniconname = "ReturnToMain1"
        elif bosstype == 2:
            returniconname = "ReturnToMain2"
        if bosstype == 2:
            maxloop = 10
        while self.IsBossFightFinished(bosstype) == False:
            for skillnum in range(0,8):
                self.DoHitByName("UseSkill"+str(skillnum))
            curloop += 1
            print("boss loop fighting = "+ str(curloop))
            sleep(1)
            self.RefreshScreenShot()
            #这里如果死完了复活不了返回村庄要处理的流程太多了，直接走卡死流程重启算了 。 
            self.TryLeaveJumpByPic(self.PicMap["Recover"], self.PicMap["Recover"], 0.5, 0.95, "do recover")
              
            
            if curloop > maxloop: 
                print("Boss fight finished wait timeout, try to exit")
                self.RefreshScreenShot()
                self.TryInnerJumpByPic(self.PicMap["EarlyExit"], self.PicMap[returniconname], 0.5, 0.85, "Hit Exit")
                sleep(3)
                self.TryLeaveJumpByPic(self.PicMap[returniconname], self.PicMap[returniconname], 0.5, 0.95, "Hit Return to Main Early Exit")
                self.WaitUntil(self.PicMap["MainId"], 30)
                return
        if bosstype == 0:
            if self.IsPicMatching(self.PicMap["GetMoreReward"], 0.95):
                self.TryLeaveJumpByPic(self.PicMap["GetMoreReward"], self.PicMap["GetMoreReward"], 0.5, 0.95, "Finished Boss0 Return to Main")
                sleep(2)
                self.TryLeaveJumpByPic(self.PicMap["Confirm"], self.PicMap["Confirm"], 0.5, 0.98, "Finished Boss0 Return to Main")
                # self.TryInnerJumpByPic(self.PicMap["EarlyExit"], self.PicMap[returniconname], 0.5, 0.95, "Hit Exit")
                # sleep(2)
            self.TryLeaveJumpByPic(self.PicMap["ReturnToMain"], self.PicMap["ReturnToMain"], 0.5, 0.95, "Finished Boss0 Return to Main")
        elif bosstype == 1:
            self.TryLeaveJumpByPic(self.PicMap["Confirm2"], self.PicMap["Confirm2"], 0.5, 0.95, "Finished Boss1 Comfirm")
            sleep(2)
            self.TryInnerJumpByPic(self.PicMap["EarlyExit"], self.PicMap[returniconname], 0.5, 0.85, "Finished Boss1 Exit")
            sleep(3)
            self.TryLeaveJumpByPic(self.PicMap[returniconname], self.PicMap[returniconname], 0.5, 0.95, "Finished Boss1 Return To Main")
        else:
            self.TryLeaveJumpByPic(self.PicMap["Confirm2"], self.PicMap["Confirm2"], 0.5, 0.95, "Finished Boss2 Comfirm")
            sleep(2)
            self.TryInnerJumpByPic(self.PicMap["EarlyExit"], self.PicMap[returniconname], 0.5, 0.85, "Finished Boss2 Exit")
            sleep(3)
            self.TryLeaveJumpByPic(self.PicMap[returniconname], self.PicMap[returniconname], 0.5, 0.95, "Finished Boss2 Return To Main")
        self.WaitUntil(self.PicMap["MainId"], 30)

    def GetBossType(self):
        self.RefreshScreenShot()
        if self.IsPicMatching(self.PicMap["BossType0"], 0.98) or self.IsPicMatching(self.PicMap["BossType01"], 0.98):
            print("Cur Boss Type - 0") 
            return 0
        elif self.IsPicMatching(self.PicMap["BossType1"], 0.98):
            print("Cur Boss Type - 1")
            return 1    
        else:
            print("Cur Boss Type - 2")
            return 2   
    
       


    def Processing(self):
        sleep(1)
        self.TryInnerJumpByPic(self.PicMap["SelectWeekly"], self.PicMap["SelectDaily"], 0.5, 0.95, "SelectWeekly")
        self.TryInnerJumpByPic(self.PicMap["SelectCanEnter0"], self.PicMap["SelectCanEnter1"], 0.5, 0.95, "SelectCanEnter0")
        while self.IsFinished() == False:
            self.TryInnerJumpByPic(self.PicMap["SelectWeekly"], self.PicMap["SelectDaily"], 0.5, 0.95, "Undo SelectWeekly")
            self.TryInnerJumpByPic(self.PicMap["SelectCanEnter0"], self.PicMap["SelectCanEnter1"], 0.5, 0.95, "Undo SelectCanEnter0")
            self.TryInnerJump("SelectFirstBoss", self.PicMap["BossSubTitleOpen"], 0.935)
            self.SelectBossMaxLevel()
            bootype = self.GetBossType()
            bosswaittime = 12
            if bootype == 0:
                 bosswaittime = 6
            if bootype == 1:
                 bosswaittime = 6
            self.TryLeaveJumpByPic(self.PicMap["FastTeam"], self.PicMap["FastTeam"], 0.5, 0.95,"Fast Team")

            self.WaitUntil(self.PicMap["TimerIcon"], 60)
            sleep(bosswaittime)#兼容贝伦出地时间
            self.WaitForFinished(bootype)        
        self.TryLeaveJump("OpenSystemMenu", self.PicMap["MainId"])
        self.TryLeaveJump("OpenSystemMenu", self.PicMap["SysOpeningIdImage"])
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
        self.SelectSimpleLevel = self.ReadPic("SelectSimpleLevel")
        self.SelectSimpleLevel = self.ReadPic("SelectSimpleLevel")

    def Processing(self):
        #Main
        #if MSmState.bMainCharacter == False:    
        #    self.HitHandle.DoMousePull(self.HitInfo["SelectLevel"][0],self.HitInfo["SelectLevel"][1],[0,300], 20, 3)
        #    sleep(2)
        #    for i in range(np.random.randint(2,3)):
        #        self.DoHitByName("SelectSimple")
        self.TryInnerJump("CreateRoom", self.FindTeamIdImage)
        self.TryInnerJump("CreateTeam", self.AddTimesIdImage)
        self.TryLeaveJump("Comfirm", self.AddTimesIdImage)
        

        self.WaitingForAutoFightingFinished()
        self.SaveScreenShot()
        if MSmState.bMainCharacter == True:
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
        self.SimpleSelected = self.ReadPic("SimpleSelected")

    def Processing(self):
        if MSmState.bMainCharacter == False:
            SimpleSelected = self.GetPicPos(self.SimpleSelected, 0.95)
            while SimpleSelected is None:
                self.HitHandle.DoMousePull(self.HitInfo["SelectSimple"][0],self.HitInfo["SelectSimple"][1],[500,0], 30, 5)
                sleep(1.5)
                self.DoHitByName("SelectSimple")
                sleep(0.2)
                self.DoHitByName("SelectSimple")
                sleep(0.2)
                self.RefreshScreenShot()
                SimpleSelected = self.GetPicPos(self.SimpleSelected)

        self.TryInnerJump("Enter0", self.AddTimesIdImage)
        self.DoAddTimes()   
        self.TryInnerJump("Comfirm0", self.EnterMonsterParkIdImage)
        if MSmState.bMainCharacter == True:
            self.TryInnerJump("BuyMoreExp", self.BuyMoreExp)
        else:
            buypos =self.GetPicPos(self.BuyMoreExp, 0.997, cv2.TM_CCORR_NORMED);
            if buypos is not None:
                self.TryLeaveJump("BuyMoreExp", self.BuyMoreExp)
        self.TryLeaveJump("Enter1", self.EnterMonsterParkIdImage)
        self.WaitingForAutoFightingFinished()
        self.SaveScreenShot()
        if MSmState.bMainCharacter == True:
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
        #self.GiveUp = self.ReadPic("GiveUp")

    def Processing(self):
        if MSmState.bMainCharacter == False:
            for i in range(np.random.randint(2,3)):
                self.DoHitByName("SelectSimple")
        self.TryInnerJump("Enter",self.AddTimesIdImage)
        self.DoAddTimes()
        self.TryLeaveJump("Comfirm", self.AddTimesIdImage)
        self.WaitingForAutoFightingFinished()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True
    
class MSmState_SpecialWeekly(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")
        self.NoTimes = self.ReadPic("NoTimes")
        self.SwithSpecial = self.ReadPic("SwithSpecial")
        self.SelectNormal = self.ReadPic("SelectNormal")

    def Processing(self):
        self.TryInnerJump("SwithSpecial",self.SwithSpecial)
        if MSmState.bMainCharacter == True:
            self.TryInnerJump("SelectNormal",self.SelectNormal)
        if self.IsPicMatching(self.NoTimes,0.985):
            self.TryLeaveJump("CloseToWander", self.SwithSpecial)
            return True
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
        self.LastWeekReward = self.ReadPic("LastWeekReward")

    def Processing(self):
        TempPos = self.GetPicPos(self.LastWeekReward,0.9);
        if TempPos is not None:
            for i in range(np.random.randint(2,3)):
                self.DoHitByName("GetLastWeekReward")
                sleep(0.3)
        for i in range(np.random.randint(2,3)):
            self.DoHitByName("GiftConfirm")
            sleep(0.3)
        self.TryInnerJump("Enter",self.Enter2IdImage)
        self.TryLeaveJump("Enter1", self.Enter2IdImage)

        self.WaitingForAutoFightingFinished()
        self.SaveScreenShot()
        self.TryLeaveJump("Exit", self.ExitIdImage)
        return True

class MSmState_PostProcess(MSmState):
    # 默认功能：发送人气、交易商品、日常任务等
    bDefault = True
    # 收周任务奖励
    bWeeklyReward = False
    # 自动换黄图
    bAutoChange = False
    # 自动整理背包
    bOrganizePackage = False
    # 自动跳过委托
    bSkipCommission = False
    # 开材料卷
    bAdditionalMaterial = False
    
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

        self.FinishCommission = self.ReadPic("FinishCommission")
        self.CommisionStartReady = self.ReadPic("CommisionStartReady")
        self.NoCommissionTicket = self.ReadPic("NoCommissionTicket")
        self.CommissionMain = self.ReadPic("CommissionMain")
        self.CommisionReciveReady = self.ReadPic("CommisionReciveReady")
        self.CommissionFinished = self.ReadPic("CommissionFinished")
        self.CommissionAllFinished = self.ReadPic("CommissionAllFinished")

        self.WeeklyTask= self.ReadPic("WeeklyTask")
        self.ChangeToWeeklyTask= self.ReadPic("ChangeToWeeklyTask")
        self.WeeklyAnyThingToRecive= self.ReadPic("WeeklyAnyThingToRecive")
        self.SharePic= self.ReadPic("SharePic")
        self.SharePicButton= self.ReadPic("SharePicButton")
        self.SharePicTarget= self.ReadPic("SharePicTarget")
        self.MoreThan200= self.ReadPic("MoreThan200")

        self.OpenPackage = self.ReadPic("OpenPackage")
        self.OpenTreasureBox = self.ReadPic("OpenTreasureBox")
        self.HasNoTreasureBox = self.ReadPic("HasNoTreasureBox")
        self.SelectRandomTreasureBox = self.ReadPic("SelectRandomTreasureBox")
        self.TryOpenTreasureBox = self.ReadPic("TryOpenTreasureBox")
        self.DisassembleComfirm = self.ReadPic("DisassembleComfirm")
        self.DisassembleMain = self.ReadPic("DisassembleMain")

        self.OpenActivity = self.ReadPic("OpenActivity")
        self.ChangeEnter = self.ReadPic("ChangeEnter")
        self.ChangeMain = self.ReadPic("ChangeMain")
        self.SelectNite = self.ReadPic("SelectNite")
        self.SelectEssence = self.ReadPic("SelectEssence")
        self.NoChangeMaterial = self.ReadPic("NoChangeMaterial")
        self.ChangeAll = self.ReadPic("ChangeAll")
        self.ChangeAll2 = self.ReadPic("ChangeAll2")
        self.ChangeResult = self.ReadPic("ChangeResult")
        self.CompositeChangeResult = self.ReadPic("CompositeChangeResult")
        self.CompositeChangeResultMain = self.ReadPic("CompositeChangeResultMain")

        self.SelectTimeLimit = self.ReadPic("SelectTimeLimit")
        self.SelectTicket = self.ReadPic("SelectTicket")
        self.OpenSelectTicket0 = self.ReadPic("OpenSelectTicket0")
        self.OpenSelectTicket1 = self.ReadPic("OpenSelectTicket1")
        self.HasTicketSelected = self.ReadPic("HasTicketSelected")
        self.GetTicketsComfirm = self.ReadPic("GetTicketsComfirm")
        
        self.ChangePreset0 = self.ReadPic("ChangePreset0")
        self.ChangePreset1 = self.ReadPic("ChangePreset1")
        
    def GetChangePresetHitInfo(self):
        self.RefreshScreenShot()
        HitPos = self.GetHitInfo(self.PicMap["ChangePreset0"], 0.5, 0.85)
        if HitPos is None:
            HitPos = self.GetHitInfo(self.PicMap["ChangePreset1"], 0.5, 0.85)
        return HitPos

    def Processing(self):

        # if MSmState.bMainCharacter == True :
        #         ChangePresetHitInfo = self.GetChangePresetHitInfo
        #         while ChangePresetHitInfo is None:
        #             self.HitHandle.DoMousePull(self.HitInfo["ChangePreset"][0],self.HitInfo["ChangePreset"][1],[200,0], 15, 5)
        #             sleep(2)
        #             ChangePresetHitInfo = self.GetChangePresetHitInfo()
        #         self.TryInnerJumpByPic(self.ChangePreset0, self.ChangePreset1, 0.5, 0.9)
        #         self.DoHitByName("Preset3")
        #         sleep(0.5)
        #         self.DoHitByName("Preset3")
        #         sleep(1)

        # 默认功能：发送人气、交易商品、日常任务等
        if MSmState_PostProcess.bDefault:
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("Communication",self.FriendsIdImage)
            self.TryInnerJump("WeChatFriends",self.WeChatFriendsIdImage)
            self.RefreshScreenShot();
            SetPopularityPos = self.GetPicPos(self.CanSendPopularityIdImage, 0.997, cv2.TM_CCORR_NORMED)     
            if SetPopularityPos is not None:
                SetPopularityHitInfo = [[SetPopularityPos[0] + 20, SetPopularityPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight + 20],[10,10]]
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
                GotoTradePosHitInfo = [[GotoTradePos[0] + 20, GotoTradePos[1]+DoScreenHit.ApplicationWindowsTitleHeight+22],[10,10]]
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

            #for i in range(np.random.randint(2,4)):
            #    self.DoHitByName("DailyReciveAll")
            #sleep(1)

            ##self.TryLeaveJump("DailyComfirm",self.DailyComfirmIdImage)
            #self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
            #sleep(1)
            self.RefreshScreenShot()
            WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)
            while WeeklyAnyThingToRecive is not None:
                self.TryInnerJump("DailyReciveAll",self.DailyComfirmIdImage)
                self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
                WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)

            #goto wechat
            GotoWeChatHitPos = self.GetPicPos(self.GotoWeChatIdImage, 0.9)
            if GotoWeChatHitPos is not None:
                print("Find Goto WeChat")
                GotoWeChatHitInfo = [[GotoWeChatHitPos[0] + 311,GotoWeChatHitPos[1]+DoScreenHit.ApplicationWindowsTitleHeight+32],[10,10]]
                self.TryLeaveJumpByPos(GotoWeChatHitInfo,self.DailyIdImage)
                #now is under state system menu open
                self.TryInnerJump("CloseGotoWeChat",self.SysOpeningIdImage)
                self.TryInnerJump("Daily",self.DailyIdImage)
                sleep(0.5)
                #for i in range(np.random.randint(2,4)):
                #    self.DoHitByName("DailyReciveAll")
                #sleep(1)
                #self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
                #sleep(1)

            #for i in range(np.random.randint(2,4)):
            #    self.DoHitByName("DailyReciveAll")
            #sleep(1)
            #self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
            self.RefreshScreenShot()
            WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)
            while WeeklyAnyThingToRecive is not None:
                self.TryInnerJump("DailyReciveAll",self.DailyComfirmIdImage)
                self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
                WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)

            self.TryLeaveJump("CloseDaily",self.DailyIdImage)
            self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
            if MSmState.bMainCharacter == True:
                self.TryLeaveJump("AutoFighting",self.DailyIdImage)
                self.TryInnerJump("AutoFighting",self.AutoFightingIdImage)
                sleep(1)
                for i in range(np.random.randint(1,2)):
                    self.DoHitByName("UseFreeTime")
                self.TryLeaveJump("CloseAutoFighting",self.AutoFightingIdImage)

        #收周任务奖励
        if MSmState_PostProcess.bWeeklyReward:
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("Daily",self.DailyIdImage)
            #先做一次图片分享
            #MoreThan200Pos = self.GetPicPos(self.MoreThan200, 0.95, cv2.TM_CCORR_NORMED)
            #if MoreThan200Pos is not None:
            #    self.TryInnerJump("SharePic2",self.SharePic)
            #else:
            #    self.TryInnerJump("SharePic",self.SharePic)
            #self.HitHandle.DoMousePull(self.HitInfo["MoveSharePic"][0],self.HitInfo["MoveSharePic"][1],[0,-500], 30, 5)
            #sleep(2)
            #self.RefreshScreenShot()
            #SharePicButtonPos = self.GetPicPos(self.SharePicButton, 0.8, cv2.TM_CCORR_NORMED)
            #if SharePicButtonPos is not None:
            #    SharePicButtonInfo = [[SharePicButtonPos[0] + 40, SharePicButtonPos[1]+DoScreenHit.ApplicationWindowsTitleHeight+22],[10,10]]
            #    self.TryInnerJumpByPos(SharePicButtonInfo,self.SharePicTarget)
            #    for i in range(np.random.randint(2,3)):
            #        self.DoHitByName("ShareToWeChat")
            #    self.TryLeaveJump("CloseSharePic",self.SharePicTarget)
            #    sleep(0.2)
            ChangeToWeeklyTaskPos = self.GetPicPos(self.ChangeToWeeklyTask, 0.8)
            if ChangeToWeeklyTaskPos is not None:
                ChangeToWeeklyTaskHitInfo = [[ChangeToWeeklyTaskPos[0] + 40, ChangeToWeeklyTaskPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight + 22],[10,10]]

                self.TryInnerJumpByPos(ChangeToWeeklyTaskHitInfo,self.WeeklyTask)
                WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)
                while WeeklyAnyThingToRecive is not None:
                    self.TryInnerJump("DailyReciveAll",self.DailyComfirmIdImage)
                    self.TryLeaveJumpAuto(self.DailyComfirmIdImage,[100,30],[10,10])
                    WeeklyAnyThingToRecive = self.GetPicPos(self.WeeklyAnyThingToRecive, 0.995, cv2.TM_CCORR_NORMED)
                self.SaveScreenShot("WeeklyReward_")
            self.TryLeaveJump("CloseDaily",self.DailyIdImage)
            self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
    
        #自动换黄图
        if MSmState_PostProcess.bAutoChange:
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("OpenActivity",self.OpenActivity)
            ChangeEnterPos = self.GetPicPos(self.ChangeEnter, 0.85)
            if ChangeEnterPos is None:
                self.HitHandle.DoMousePull(self.HitInfo["ActivityDoMouseWheel"][0],self.HitInfo["ActivityDoMouseWheel"][1],[0,-100], 20, 3)
                sleep(2)
                self.RefreshScreenShot()
                ChangeEnterPos = self.GetPicPos(self.ChangeEnter, 0.85)
            if ChangeEnterPos is not None:
                ChangeEnterHitInfo = [[ChangeEnterPos[0] + 20, ChangeEnterPos[1]+DoScreenHit.ApplicationWindowsTitleHeight+12],[10,10]]
                self.TryInnerJumpByPos(ChangeEnterHitInfo,self.ChangeMain)
                self.TryInnerJump("SelectNite",self.SelectNite)
                self.TryInnerJump("SelectEssence",self.SelectEssence)
                NoChangeMaterialPos = self.GetPicPos(self.NoChangeMaterial, 0.9)
                ChangeAllPos = self.GetPicPos(self.ChangeAll, 0.98)
                if ChangeAllPos is None:
                    ChangeAllPos = self.GetPicPos(self.ChangeAll2, 0.98)
                while True:
                    if NoChangeMaterialPos is not None:
                        break
                    if ChangeAllPos is not None:
                        break
                    self.DoHitByName("SelectFirst")
                    sleep(0.1)
                    self.DoHitByName("SelectFirst")
                    sleep(0.1)
                    self.DoHitByName("SelectFirst")
                    sleep(0.5)
                    self.DoHitByName("AddMatertialMax")
                    sleep(0.1)
                    self.DoHitByName("AddMatertialMax")
                    sleep(0.5)
                    self.DoHitByName("AddMatertialConfirm")
                    sleep(0.1)
                    self.DoHitByName("AddMatertialConfirm")
                    sleep(0.5)
                    self.DoHitByName("DoChange")
                    sleep(0.1)
                    self.DoHitByName("DoChange")
                    self.RefreshScreenShot()
                    NoChangeMaterialPos = self.GetPicPos(self.NoChangeMaterial, 0.9)
                    ChangeAllPos = self.GetPicPos(self.ChangeAll, 0.98)
                    if ChangeAllPos is None:
                        ChangeAllPos = self.GetPicPos(self.ChangeAll2, 0.98)
                self.SaveScreenShot("Charge_")
                for i in range(0,6):
                    self.TryInnerJump("GetChange"+ str(i),self.ChangeResult)
                    self.TryLeaveJump("CloseChangeResult",self.ChangeResult)
                self.TryInnerJump("GetChange6",self.CompositeChangeResult)
                self.TryInnerJump("StartCompositeChangeResult",self.CompositeChangeResultMain)
                self.DoHitByName("CompositeMax")
                sleep(0.1)
                self.DoHitByName("CompositeMax")
                sleep(0.3)
                self.DoHitByName("DoComposite")
                sleep(0.1)
                self.DoHitByName("DoComposite")
                sleep(0.1)
                self.DoHitByName("DoComposite")
                sleep(0.5)
                self.DoHitByName("DoComposite2")
                sleep(0.2)
                self.DoHitByName("DoComposite2")
                sleep(0.2)
                self.DoHitByName("DoComposite2")
                sleep(0.2)
                self.DoHitByName("DoComposite2")
                sleep(5)
                self.DoHitByName("DoComposite3")
                sleep(0.2)
                self.DoHitByName("DoComposite3")
                sleep(0.2)
                self.TryLeaveJump("CloseCommissionMain",self.CompositeChangeResultMain)
                self.TryLeaveJump("CloseCommissionMain",self.ChangeMain)
                self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
            else:
                self.TryLeaveJump("OpenSystemMenu",self.OpenActivity)
                self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
        
        #自动整理背包
        if MSmState_PostProcess.bOrganizePackage:
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("OpenPackage",self.OpenPackage)

            #自动分解下装备
            self.TryInnerJump("Disassemble",self.DisassembleMain,0.85)
            for i in range(np.random.randint(2,3)):
                self.DoHitByName("Disassemble")
                sleep(0.2)
            for i in range(np.random.randint(3,4)):
                self.DoHitByName("DisassembleConfirm")
                sleep(0.2)
            for i in range(np.random.randint(3,4)):
                self.DoHitByName("DisassembleConfirm1")
                sleep(0.2)
            self.TryLeaveJump("CloseCommissionMain",self.DisassembleMain)

            #自动开箱子
            self.TryInnerJump("OpenTreasureBox",self.OpenTreasureBox)
            self.TryInnerJump("SelectRandomTreasureBox",self.SelectRandomTreasureBox)
            HasNoTreasureBoxPos = self.GetPicPos(self.HasNoTreasureBox, 0.98)
            while HasNoTreasureBoxPos is None:
                 self.TryInnerJump("TryOpenTreasureBox",self.TryOpenTreasureBox,0.95)
                 self.TryInnerJump("TryOpenTreasureBox2",self.DailyComfirmIdImage)
                 self.TryLeaveJump("OpenTreasureBoxComfirm",self.DailyComfirmIdImage)
                 self.RefreshScreenShot()
                 HasNoTreasureBoxPos = self.GetPicPos(self.HasNoTreasureBox, 0.98)
            self.TryLeaveJump("CloseCommissionMain",self.OpenTreasureBox)
            self.SaveScreenShot("Package_")
            self.TryLeaveJump("CloseCommissionMain",self.OpenPackage)
            self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)

        #自动跳过委托
        if MSmState_PostProcess.bSkipCommission:
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("Commission",self.CommissionMain)
            CommissionFinished = self.GetPicPos(self.CommissionFinished, 0.95, cv2.TM_CCORR_NORMED)
            NoCommissionTicket = self.GetPicPos(self.NoCommissionTicket, 0.999, cv2.TM_CCORR_NORMED)
            if (NoCommissionTicket is None) and (CommissionFinished is None):
                for k in range(3):
                    for i in range(np.random.randint(2,3)):
                        self.DoHitByName("CommissionTask" + str(k))
                    for i in range(np.random.randint(2,3)):
                        self.DoHitByName("ReciveCommission")
                    for i in range(np.random.randint(2,3)):
                        self.DoHitByName("CloseCommissionRevice")
                self.TryInnerJump("AlignCommission",self.CommisionReciveReady,0.95)
                self.TryInnerJump("StartCommission",self.CommisionStartReady,0.95)
                self.TryInnerJump("DoCommission",self.CommissionAllFinished,0.95)
            self.TryLeaveJump("CloseCommissionMain",self.CommissionMain)
            self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)

        if MSmState_PostProcess.bAdditionalMaterial == True:
            # if MSmState.bAllMaterialHasGotten == True:
            #     return True
            self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
            self.TryInnerJump("OpenPackage",self.OpenPackage)
            self.TryInnerJump("SelectTimeLimit",self.SelectTimeLimit)
            TicketPos = self.GetPicPos(self.SelectTicket, 0.9)
            if TicketPos is not None:
                TicketPosHitInfo = [[TicketPos[0] + 20, TicketPos[1]+ DoScreenHit.ApplicationWindowsTitleHeight + 22],[10,10]]
                self.TryInnerJumpByPos(TicketPosHitInfo, self.OpenSelectTicket0)
                self.TryInnerJump("Disassemble",self.OpenSelectTicket1)
                self.TryInnerJump("SelectMaterialTickets",self.HasTicketSelected,0.97)
                self.DoHitByName("AddTicketsMax")
                sleep(0.2)
                self.DoHitByName("AddTicketsMax")
                sleep(0.2)
                self.TryLeaveJump("GetTickets",self.HasTicketSelected, 0.985)
                self.TryLeaveJump("GetTicketsComfirm",self.GetTicketsComfirm, 0.985)    
            self.TryLeaveJump("CloseCommissionMain",self.OpenPackage)
            self.TryLeaveJump("OpenSystemMenu",self.SysOpeningIdImage)
            return True

        return True


if __name__ == "__main__":
    # ============ 测试配置 ============
    # 在这里修改要测试的状态名称
    TEST_STATE = "DailyTask"  #GameModeDefault 例如:Expedition  DailyTask, PostProcess, Material, Elite, Wander 等
    # =================================
    
    from win32gui import FindWindow, FindWindowEx
    
    # 获取窗口句柄 (参考 MSmAuto.py 的逻辑)
    hwd_title = "MuMu安卓设备"
    MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
    if MSmState.HandleNumber_Main != 0:
        MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "MuMuNxDevice")
        MSmState.HandleNumber_Keyboard = FindWindowEx(MSmState.HandleNumber_Render, None, None, "nemudisplay")
        DoScreenHit.ApplicationWindowsTitleHeight = 0
        print(f"找到 MuMu 窗口: {hwd_title}")
    else:
        hwd_title = "雷电模拟器"
        MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
        MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "TheRender")
        MSmState.HandleNumber_Keyboard = MSmState.HandleNumber_Render
        DoScreenHit.ApplicationWindowsTitleHeight = 0
        print(f"找到雷电模拟器窗口: {hwd_title}")
    
    if MSmState.HandleNumber_Main == 0:
        print("错误: 未找到 MuMu安卓设备 或 雷电模拟器 窗口")
        exit(1)
    
    if MSmState.HandleNumber_Main == MSmState.HandleNumber_Render:
        print("Warning: HandleNumber_Main is equal to HandleNumber_Render, consider run with -MainWindowsCapture")
    MSmState.bMainCharacter = True
    print(f"=" * 50)
    print(f"MSmState 单元测试")
    print(f"=" * 50)
    print(f"状态名称: {TEST_STATE}")
    print(f"主窗口句柄: {MSmState.HandleNumber_Main}")
    print(f"渲染窗口句柄: {MSmState.HandleNumber_Render}")
    print(f"键盘窗口句柄: {MSmState.HandleNumber_Keyboard}")
    print(f"=" * 50)
    
    # 查找状态类
    state_class_name = f"MSmState_{TEST_STATE}"
    state_class = None
    for name in dir():
        obj = eval(name)
        if isinstance(obj, type) and issubclass(obj, MSmState) and obj != MSmState and name == state_class_name:
            state_class = obj
            break
    
    if state_class is None:
        print(f"错误: 未找到状态类 '{state_class_name}'")
        print("可用的状态类:")
        for name in dir():
            obj = eval(name)
            if isinstance(obj, type) and issubclass(obj, MSmState) and obj != MSmState:
                print(f"  - {name.replace('MSmState_', '')}")
        exit(1)
    
    # 创建状态实例
    state_instance = state_class(TEST_STATE)
    
    print(f"\n开始执行 {TEST_STATE} 的 Processing() 方法...\n")
    
    try:
        result = state_instance.Processing()
        print(f"\n执行完成，返回值: {result}")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()
