from MSmState import MSmState_CharacterSelect
from re import search
from win32gui import GetWindowText, FindWindow, FindWindowEx, GetWindowRect, GetForegroundWindow
import os
import json

if __name__ == '__main__':
    hwd_title = "雷电模拟器"
    HandleNumber = FindWindow(None, hwd_title)
    if HandleNumber != 0:
        StateTable = {}
        StateTable["CharacterSelect"] = MSmState_CharacterSelect("CharacterSelect", HandleNumber)
        
        #global jump table means 
        #TODO, global jump table can be gen by each states' jump table
        GlobalJumpTable = {}
        GlobalJumpTablePath = os.path.dirname(__file__) + "\\Data\\GlobalJumpTable.json" 
        GlobalJumpTableJson = json.load(open(GlobalJumpTablePath, 'r', encoding='utf-8'))
        for i in range(len(GlobalJumpTableJson)):
            TargetJumeTable = {}
            targetstatename = GlobalJumpTableJson[i]["TargetStateName"]
            targettable = GlobalJumpTableJson[i]["TargetTable"]
            for j in range(len(targettable)):
                TargetJumeTable[targettable[j][0]] = targettable[j][1]
            GlobalJumpTable[targetstatename] = TargetJumeTable



        TaskFilePath = os.path.dirname(__file__) + "\\Data\\TaskList.json" 
        TaskJson = json.load(open(TaskFilePath, 'r', encoding='utf-8'))
        InitState = StateTable[TaskJson[0]]
        if InitState.IsUnderState() == False:
            print("Please move to character select widget and restart this script")
            exit(1)
        InitState.DoHit([356,212],[1,1])
        exit(0)
        InitState.SelectCharacter(3)
        for StateIndex in range(len(TaskJson)):
            CurState = StateTable[TaskJson[StateIndex]]
            



    else:
        print("please open 雷电模拟器 first")



    