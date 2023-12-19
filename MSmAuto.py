from MSmState import MSmState_CharacterSelect,MSmState_ChangeCharacter,MSmState_GameModeDefault, MSmState_GuildInfo, MSmState_Loading, MSmState_Login, MSmState_Mail, MSmState_MaterialAutoFighting, MSmState_MaterialEnter0, MSmState_MaterialEnter1, MSmState_MaterialsMain, MSmState_SystemMenuOpening, MSmState_Wander
from re import search
from win32gui import GetWindowText, FindWindow, FindWindowEx, GetWindowRect, GetForegroundWindow
import os
import json
from time import sleep
from FrozenPath import frozen

if __name__ == '__main__':
    hwd_title = "雷电模拟器"
    HandleNumber = FindWindow(None, hwd_title)
    HandleNumber = FindWindowEx(HandleNumber, None, None, "TheRender")
    if HandleNumber != 0:
        StateTable = {}
        #is python has Macro?
        StateTable["CharacterSelect"]      = MSmState_CharacterSelect("CharacterSelect", HandleNumber)
        StateTable["ChangeCharacter"]      = MSmState_ChangeCharacter("ChangeCharacter", HandleNumber)
        StateTable["GameModeDefault"]      = MSmState_GameModeDefault("GameModeDefault", HandleNumber)
        StateTable["GuildInfo"]            = MSmState_GuildInfo("GuildInfo", HandleNumber)
        StateTable["Loading"]              = MSmState_Loading("Loading", HandleNumber)
        StateTable["Login"]                = MSmState_Login("Login", HandleNumber)
        StateTable["Mail"]                 = MSmState_Mail("Mail", HandleNumber)
        StateTable["MaterialAutoFighting"] = MSmState_MaterialAutoFighting("MaterialAutoFighting", HandleNumber)
        StateTable["MaterialEnter0"]       = MSmState_MaterialEnter0("MaterialEnter0", HandleNumber)
        StateTable["MaterialEnter1"]       = MSmState_MaterialEnter1("MaterialEnter1", HandleNumber)
        StateTable["MaterialsMain"]        = MSmState_MaterialsMain("MaterialsMain", HandleNumber)
        StateTable["SystemMenuOpening"]    = MSmState_SystemMenuOpening("SystemMenuOpening", HandleNumber)
        StateTable["Wander"]               = MSmState_Wander("Wander", HandleNumber)
        
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



        TaskFilePath = frozen.app_path() + "\\Data\\TaskList.json" 
        TaskJson = json.load(open(TaskFilePath, 'r', encoding='utf-8'))
        InitState = StateTable[TaskJson[0]]
        if InitState.IsUnderState() == False:
            print("Please move to character select widget and restart this script")
            exit(1)
        #InitState.SelectCharacter(3)
        LoadingState = StateTable["Loading"]
        LoginState = StateTable["Login"]
        CurrentState = InitState
        for i in range(18):
            #CurrentState.SelectCharacter(i)
            MSmState_CharacterSelect.CurrentSelectedCharacterIndex = i
            TaskLen = len(TaskJson)
            for StateIndex in range(TaskLen):
                TargetStateName = TaskJson[StateIndex]
                TargetState = StateTable[TargetStateName]
                while CurrentState.Name != TargetStateName:
                    #prepare state
                    #mostly do close ads or select to main character
                    prepareres = CurrentState.PrepareState()
                    if prepareres == False and StateIndex != TaskLen - 1:
                        #when state init is failed, go to character select and start next character's task
                        StateIndex = TaskLen - 1
                        break
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
    else:
        print("please open 雷电模拟器 first")



    