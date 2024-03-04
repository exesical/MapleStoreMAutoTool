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

    def GetPicPos(self, InPic, MatchingThreshold = 0.8):
        res = cv2.matchTemplate(self.ScreenShotImage, InPic, cv2.TM_CCOEFF_NORMED)
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
            
            while(self.IsUnderState() and OpTimes != MaxOpTimes ):
                self.DoHit(HitPos, HitRange)
                sleep(1)
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

    def TryLeaveJump(self, HitName, CheckPic):
        self.DoHitByName(HitName);
        sleep(1)
        self.RefreshScreenShot();
        bSuccess = self.IsPicMatching(CheckPic)
        while bSuccess == True:
            self.DoHitByName(HitName);
            sleep(1)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)
            sleep(0.3)
            self.RefreshScreenShot();
            bSuccess = bSuccess and self.IsPicMatching(CheckPic)

    def DoAddTimes(self):
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


class MSmState_GameModeDefault(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.MaterialEnterIdImage = self.ReadPic("MaterialEnterIdentify")
        self.EliteEnterIdImage = self.ReadPic("EliteEnterIdImage")
        self.TangyunEnterIdImage = self.ReadPic("TangyunEnterIdImage")
        self.PirateEnterIdImage = self.ReadPic("PirateEnterIdImage")
        self.NitePyramidEnterIdImage = self.ReadPic("NitePyramidEnterIdImage")
        self.WeeklyEnterIdImage = self.ReadPic("WeeklyEnterIdImage")
        self.EvolutionEnterIdImage = self.ReadPic("EvolutionEnterIdImage")
        self.WulinEnterIdImage = self.ReadPic("WulinEnterIdImage")
        self.DimensionEnterIdImage = self.ReadPic("DimensionEnterIdImage")

    def AddEnter(self, ModeName, IdPic):
        Pos = self.GetPicPos(IdPic)
        if Pos is None:
            print("Cannot find "+ ModeName + " Enter")
        else:
            self.JumpInfo[ModeName] = [[Pos[0]+ 75, Pos[1]+ 65],[30, 30]]

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
        self.AddEnter("Elite", self.EliteEnterIdImage)        
        self.AddEnter("Tangyun", self.TangyunEnterIdImage)        
        self.AddEnter("Pirate", self.PirateEnterIdImage)        
        self.AddEnter("NitePyramid", self.NitePyramidEnterIdImage)        
        self.AddEnter("Weekly", self.WeeklyEnterIdImage)        
        self.AddEnter("Wulin", self.WulinEnterIdImage)        
        self.AddEnter("Dimension", self.DimensionEnterIdImage)        
        self.AddEnter("Evolution", self.EvolutionEnterIdImage)        

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

class MSmState_MaterialEnter0(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

    def Processing(self):
        self.DoAddTimes()
        return True

class MSmState_MaterialEnter1(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

class MSmState_MaterialsMain(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)

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
        self.TryInnerJump("CreateTeam", self.WaitingTeamIdImage)
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


class MSmState_Elite(MSmState_TeamCommon):
    def __init__(self, StateName):
        super().__init__(StateName)   

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

class MSmState_Evolution(MSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.AddTimesIdImage = self.ReadPic("AddTimesIdImage")
        self.EnterEvolutionIdImage = self.ReadPic("EnterEvolutionIdImage")
        self.ExitIdImage = self.ReadPic("ExitIdImage")

    def Processing(self):
        self.TryInnerJump("Enter", self.AddTimesIdImage)
        self.DoAddTimes()   
        self.TryInnerJump("Comfirm", self.EnterEvolutionIdImage)
        self.TryLeaveJump("Enter2", self.EnterEvolutionIdImage)
        self.WaitingForAutoFightingFinished()
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

    def Processing(self):
        self.TryInnerJump("OpenSystemMenu",self.SysOpeningIdImage)
        sleep(0.5)
        self.TryInnerJump("Communication",self.FriendsIdImage)
        sleep(0.5)
        self.TryInnerJump("WeChatFriends",self.WeChatFriendsIdImage)
        sleep(0.5)
        self.TryInnerJump("SendPopularity",self.SendPopularityIdImage)
        sleep(1)
        self.DoHitByName("SelectFreeGift")
        sleep(1)
        self.DoHitByName("Comfirm")
        sleep(1)
        self.DoHitByName("NotRemind")
        sleep(1)
        self.DoHitByName("CloseSelectFreeGift")
        sleep(1)
        self.TryLeaveJump("CloseDaily",self.WeChatFriendsIdImage)
        sleep(1)
        self.TryInnerJump("Daily",self.DailyIdImage)
        sleep(1)
        for i in range(np.random.randint(2,4)):
            self.DoHitByName("DailyReciveAll")
        sleep(1)

        self.TryLeaveJump("DailyComfirm",self.DailyComfirmIdImage)
        sleep(1)


        #goto wechat
        GotoWeChatHitPos = self.GetPicPos(self.GotoWeChatIdImage)
        if Pos is not None:
            GotoWeChatHitPos = [GotoWeChatHitPos[0] + 311,GotoWeChatHitPos[1]+32]
            self.TryLeaveJumpByPos(GotoWeChatHitPos,self.DailyIdImage)
            sleep(0.5)
            #now is under state system menu open
            self.TryInnerJump("Daily",self.DailyIdImage)
            sleep(0.5)


        for i in range(np.random.randint(2,4)):
            self.DoHitByName("DailyReciveAll")
        sleep(1)

        self.TryLeaveJump("DailyComfirm",self.DailyComfirmIdImage)
        sleep(1)

        self.TryLeaveJump("CloseDaily",self.DailyIdImage)
        sleep(0.5)
        self.TryLeaveJump("AutoFighting",self.DailyIdImage)
        sleep(1)
        self.TryInnerJump("AutoFighting",self.AutoFightingIdImage)
        sleep(1)
        for i in range(np.random.randint(1,2)):
            self.DoHitByName("UseFreeTime")
        sleep(1)
        self.TryLeaveJump("CloseAutoFighting",self.AutoFightingIdImage)
        return True
