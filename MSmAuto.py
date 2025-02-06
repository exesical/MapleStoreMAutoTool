from MSmState import *
from re import search
from win32gui import GetWindowText, FindWindow, FindWindowEx, GetWindowRect, GetForegroundWindow
import os
import json
from time import sleep
from FrozenPath import frozen
import sys
#from datatime import datatime
import datetime
import time

if __name__ == '__main__':
    bExpeditionMode = False
    bExpeditionModeEnable = False;
    CharacterCount = 100000
    ExpeditionEndMinitue = 55
    bTestMode = False
    TestStartIndex = 2;
    for args in sys.argv:
        if search(r'debug', args):
            MSmState.bUseDebug = True
        if search(r'test', args):
            bTestMode = True
        if search(r'MainWindowsCapture',args):
            MSmState.bUseMainWindowCapture = True
        if search(r'Expedition',args):
            bExpeditionModeEnable = True
        if search(r'CharacterCount',args):
            CharacterCount = int(args.split("=")[1])
        if search(r'ExpeditionEndMinitue',args):
            ExpeditionEndMinitue = int(args.split("=")[1])
        if search(r'TestStartIndex',args):
            TestStartIndex = int(args.split("=")[1])

    IsMainCharacter = False
    hwd_title = "雷电模拟器"
    MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
    MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "TheRender")
    if MSmState.HandleNumber_Main  == MSmState.HandleNumber_Render:
        print("Warning: HandleNumber_Main is equal to HandleNumber_Render, considier run with -MainWindowsCapture")
    today = datetime.date.today()
    CurCharacterIndex = 0
    CurCharacterIndexFileName  = frozen.app_path() +"\\" + today.strftime('RecordFile%y%m%d');
    if os.path.exists(CurCharacterIndexFileName):
        CurCharacterIndexFile = open(CurCharacterIndexFileName, "r")
        for line in CurCharacterIndexFile:
            CurCharacterIndex = int(line.strip())
        CurCharacterIndexFile.close()
            
    CurCharacterIndexEx = 1
    CurCharacterIndexExFileName  = frozen.app_path() +"\\" + today.strftime('ExRecordFile%y%m%d');
    if os.path.exists(CurCharacterIndexExFileName):
        CurCharacterIndexExFile = open(CurCharacterIndexExFileName, "r")
        for line in CurCharacterIndexExFile:
            CurCharacterIndexEx = int(line.strip())
        CurCharacterIndexExFile.close()
    if bTestMode:
        CurCharacterIndex = TestStartIndex

    for cur_dir, sub_dir, included_file in walk(frozen.app_path()):
            if included_file:
                for file in included_file:
                    if search(r'RecordFile', file) or search(r'&m', file):
                        if not search(today.strftime('RecordFile%y%m%d'), file):
                            os.remove(file)

    if MSmState.HandleNumber_Main != 0:
        StateTable = {}
        #is python has Macro?
        StateTable["CharacterSelect"]      = MSmState_CharacterSelect("CharacterSelect")
        StateTable["ChangeCharacter"]      = MSmState_ChangeCharacter("ChangeCharacter")
        StateTable["GameModeDefault"]      = MSmState_GameModeDefault("GameModeDefault")
        StateTable["GuildInfo"]            = MSmState_GuildInfo("GuildInfo")
        StateTable["Loading"]              = MSmState_Loading("Loading")
        StateTable["Login"]                = MSmState_Login("Login")
        StateTable["Mail"]                 = MSmState_Mail("Mail")
        StateTable["MaterialAutoFighting"] = MSmState_MaterialAutoFighting("MaterialAutoFighting")
        StateTable["MaterialEnter0"]       = MSmState_MaterialEnter0("MaterialEnter0")
        StateTable["MaterialEnter1"]       = MSmState_MaterialEnter1("MaterialEnter1")
        StateTable["MaterialsMain"]        = MSmState_MaterialsMain("MaterialsMain")
        StateTable["SystemMenuOpening"]    = MSmState_SystemMenuOpening("SystemMenuOpening")
        StateTable["Wander"]               = MSmState_Wander("Wander")
        StateTable["Elite"]                = MSmState_Elite("Elite")
        StateTable["Pirate"]               = MSmState_Pirate("Pirate")
        StateTable["NitePyramid"]          = MSmState_NitePyramid("NitePyramid")
        StateTable["Dimension"]            = MSmState_Dimension("Dimension")
        StateTable["MonsterPark"]          = MSmState_MonsterPark("MonsterPark")
        StateTable["FastJump"]             = MSmState_FastJump("FastJump")
        StateTable["Tangyun"]              = MSmState_Tangyun("Tangyun")
        StateTable["Weekly"]               = MSmState_Weekly("Weekly")
        StateTable["Wulin"]                = MSmState_Wulin("Wulin")
        StateTable["PostProcess"]          = MSmState_PostProcess("PostProcess")
        StateTable["Expedition"]           = MSmState_Expedition("Expedition")

        #global jump table means 
        #TODO, global jump table can be gen by each states' jump table
        GlobalJumpTable = {}
        GlobalJumpTablePath = frozen.app_path() + "\\Data\\GlobalJumpTable.json" 
        GlobalJumpTableJson = json.load(open(GlobalJumpTablePath, 'r', encoding='utf-8'))
        for i in range(len(GlobalJumpTableJson)):
            TargetJumeTable = {}
            targetstatename = GlobalJumpTableJson[i]["TargetStateName"]
            targettable = GlobalJumpTableJson[i]["TargetTable"]
            for j in range(len(targettable)):
                TargetJumeTable[targettable[j][0]] = targettable[j][1]
            GlobalJumpTable[targetstatename] = TargetJumeTable

        
        TaskJsonExpedition = json.load(open(frozen.app_path() + "\\Data\\TaskListExpedition.json", 'r', encoding='utf-8'))
        TaskFilePath = frozen.app_path() + "\\Data\\TaskList.json" 
        TaskJson = json.load(open(TaskFilePath, 'r', encoding='utf-8'))
        TaskJsonMain = json.load(open(frozen.app_path() + "\\Data\\TaskListMain.json", 'r', encoding='utf-8'))
        TaskJsonFive = json.load(open(frozen.app_path() + "\\Data\\TaskListFive.json", 'r', encoding='utf-8'))
        if bTestMode:        
            TaskJson = json.load(open(frozen.app_path() + "\\Data\\TestList.json", 'r', encoding='utf-8'))
            TaskJsonMain = json.load(open(frozen.app_path() + "\\Data\\TestList.json", 'r', encoding='utf-8'))
            TaskJsonFive = json.load(open(frozen.app_path() + "\\Data\\TestList.json", 'r', encoding='utf-8'))

        InitState = StateTable["CharacterSelect"] 
        if InitState.IsUnderState() == False:
            print("Please move to character select widget and restart this script")
            exit(1)
        #InitState.SelectCharacter(3)
        LoadingState = StateTable["Loading"]
        LoginState = StateTable["Login"]
        CurrentState = InitState
        bStateChanged = False
        bLastExpeditionMode = bExpeditionMode
        
        if True:
            for j in range(0, 100000):
                current_time_h = int(time.strftime("%H:%M:%S")[0:2])
                current_time_m = int(time.strftime("%H:%M:%S")[3:5])
                bExpeditionMode = (current_time_h == 12 or current_time_h == 20) and( current_time_m <= ExpeditionEndMinitue) and bExpeditionModeEnable and CurCharacterIndexEx < CharacterCount
                    
                CurIndex = 0;
                if bExpeditionMode == True:
                    CurIndex = CurCharacterIndexEx
                    CurCharacterIndexEx = CurCharacterIndexEx + 1
                else: 
                    CurIndex = CurCharacterIndex       
                    CurCharacterIndex = CurCharacterIndex + 1

                if bExpeditionMode == True:
                    TaskCur = TaskJsonExpedition
                elif CurIndex == 0:
                    TaskCur = TaskJsonMain
                elif CurIndex <= 5:
                    TaskCur = TaskJsonFive
                else:
                    TaskCur = TaskJson
                #CurrentState.SelectCharacter(i)
                if j != 0 and CurCharacterIndex > 1:
                    CurCharacterIndexFile = open(CurCharacterIndexFileName, "w")
                    CurCharacterIndexFile.write(str(CurCharacterIndex - 1))
                    CurCharacterIndexFile.close()
                if j != 0 and CurCharacterIndexEx > 1:
                    CurCharacterIndexExFile = open(CurCharacterIndexExFileName, "w")
                    CurCharacterIndexExFile.write(str(CurCharacterIndexEx - 1))
                    CurCharacterIndexExFile.close()

                if bExpeditionMode == True and CurIndex > CharacterCount:
                    CurIndex = CharacterCount
                
                MSmState_CharacterSelect.CurrentSelectedCharacterIndex = CurIndex
                if CurIndex == 0:
                    MSmState.bMainCharacter = True
                else:
                    MSmState.bMainCharacter = False
   
                TaskLen = len(TaskCur)
                for StateIndex in range(TaskLen):
                    TargetStateName = TaskCur[StateIndex]
                    TargetState = StateTable[TargetStateName]
                    while CurrentState.Name != TargetStateName:
                        #Processing state
                        #mostly do close ads or select to main character
                        #now all Processing would return true
                        print("Start processing state " + CurrentState.Name)
                        CurrentState.Processing()
                        print("End processing state " + CurrentState.Name)
                        #find next jump
                        NextStateName = GlobalJumpTable[TargetStateName][CurrentState.Name]
                        NextState = StateTable[NextStateName]
                        res = CurrentState.JumpToTarget(NextState)
                        if res == 0:
                            MaxIter = 100
                            Iter = 0
                            while NextState.IsUnderState() == False and Iter < MaxIter:
                                sleep(1)
                                Iter = Iter + 1
                            if(Iter < MaxIter):
                                CurrentState = NextState
                                continue
                            else:
                                if LoginState.IsUnderState():
                                    #means miss connection
                                    CurrentState = LoginState
                                    break
                                if CurrentState.IsUnderState():
                                    #can not jump to next state in otherwise, go to next character task
                                    StateIndex = TaskLen -1
                                    break

                        elif res == 1:
                            exit(1)
                        elif res == 2:
                            #if has no jump info, just move to next target
                            break

    else:
        print("please open 雷电模拟器 first")



    