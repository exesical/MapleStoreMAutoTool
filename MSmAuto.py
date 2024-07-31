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

if __name__ == '__main__':

    bExpeditionMode = False;
    for args in sys.argv:
        if search(r'debug', args):
            MSmState.bUseDebug = True
        if search(r'MainWindowsCapture',args):
            MSmState.bUseMainWindowCapture = True
        if search(r'Expedition',args):
            bExpeditionMode = True

    IsMainCharacter = False
    hwd_title = "雷电模拟器"
    MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
    MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "TheRender")
    if MSmState.HandleNumber_Main  == MSmState.HandleNumber_Render:
        print("Warning: HandleNumber_Main is equal to HandleNumber_Render, considier run with -MainWindowsCapture")
    today = datetime.date.today()
    StartCharacterIndex = 0
    
    if bExpeditionMode == True:
        StartCharacterIndexFileName  = frozen.app_path() +"\\" + today.strftime('ExRecordFile%y%m%d');
        if os.path.exists(StartCharacterIndexFileName):
            StartCharacterIndexFile = open(StartCharacterIndexFileName, "r")
            for line in StartCharacterIndexFile:
                StartCharacterIndex = int(line.strip())
            StartCharacterIndexFile.close()
    else:
        StartCharacterIndexFileName  = frozen.app_path() +"\\" + today.strftime('RecordFile%y%m%d');
        if os.path.exists(StartCharacterIndexFileName):
            StartCharacterIndexFile = open(StartCharacterIndexFileName, "r")
            for line in StartCharacterIndexFile:
                StartCharacterIndex = int(line.strip())
            StartCharacterIndexFile.close()

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
        InitState = StateTable["CharacterSelect"] 
        if InitState.IsUnderState() == False:
            print("Please move to character select widget and restart this script")
            exit(1)
        #InitState.SelectCharacter(3)
        LoadingState = StateTable["Loading"]
        LoginState = StateTable["Login"]
        CurrentState = InitState
        for i in range(StartCharacterIndex, 100):
            if bExpeditionMode == True:
                TaskCur = TaskJsonExpedition
            elif i == 0:
                TaskCur = TaskJsonMain
            elif i <= 5:
                TaskCur = TaskJsonFive
            else:
                TaskCur = TaskJson
            #CurrentState.SelectCharacter(i)
            if i != 0:
                StartCharacterIndexFile = open(StartCharacterIndexFileName, "w")
                #StartCharacterIndexFile.seek(0)
                StartCharacterIndexFile.write(str(i))
                StartCharacterIndexFile.close()
            MSmState_CharacterSelect.CurrentSelectedCharacterIndex = i
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



    