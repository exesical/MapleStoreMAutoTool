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
import win32api
import win32con

def load_config_from_savetaskgroup(task_group):
    """从SaveTaskGroup加载配置信息"""
    try:
        config_info_path = frozen.app_path() + f"\\Data\\SaveTaskGroup\\TaskGroup{task_group}\\config_info.json"
        if os.path.exists(config_info_path):
            with open(config_info_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"从SaveTaskGroup{task_group}加载配置信息")
                return config
    except Exception as e:
        print(f"加载SaveTaskGroup配置信息失败: {e}")
    return None

def load_task_json_file(task_group, filename):
    """加载任务JSON文件，优先从SaveTaskGroup读取，否则从Data/TaskGroup读取"""
    save_path = frozen.app_path() + f"\\Data\\SaveTaskGroup\\TaskGroup{task_group}\\{filename}"
    default_path = frozen.app_path() + f"\\Data\\TaskGroup{task_group}\\{filename}"
    
    # 优先从SaveTaskGroup读取
    if os.path.exists(save_path):
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                print(f"从SaveTaskGroup加载: {filename}")
                return json.load(f)
        except Exception as e:
            print(f"从SaveTaskGroup加载{filename}失败: {e}，尝试加载默认配置...")
    
    # 回退到Data/TaskGroup（只读默认配置）
    if os.path.exists(default_path):
        try:
            with open(default_path, 'r', encoding='utf-8') as f:
                print(f"从Data/TaskGroup加载默认配置: {filename}")
                return json.load(f)
        except Exception as e:
            print(f"加载默认配置{filename}失败: {e}")
    
    # 如果都失败，返回空列表
    print(f"警告：无法加载{filename}，使用空配置")
    return []

def main():
    """主函数入口"""
    bExpeditionMode = False
    bExpeditionModeEnable = False;
    CharacterCount = 100000
    ExpeditionEndMinitue = 55
    bTestMode = False
    TestStartIndex = 1;
    bCanUesFastMode = False
    TestTaskIndex = 0;
    # 0 is NitePyramid, 1 is MonsterPark
    WeekDay = datetime.datetime.now().weekday()
    TaskGroupIndex = WeekDay % 2;
    ViceCharacterCount = 0
    PostProcessType = 10  # 默认值
    FastJumpType = 0  # 默认值
    AdditionalMaterial = 0  # 默认值
    
    #MSmState.bUseDebug = True

    # 先处理命令行参数，确定TaskGroupIndex
    for args in sys.argv:
        if search(r'debug', args):
            MSmState.bUseDebug = True
        if search(r'FastMode', args):
            bCanUesFastMode = True
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
        if search(r'TestTaskIndex',args):
            TestTaskIndex = int(args.split("=")[1])
        if search(r'FastJumpType',args):
            FastJumpType = int(args.split("=")[1])
        if search(r'PostProcessType',args):
            PostProcessType = int(args.split("=")[1])
        if search(r'TaskGroupIndex',args):
            TaskGroupIndex = int(args.split("=")[1])
        if search(r'AdditionalMaterial',args):
            AdditionalMaterial = int(args.split("=")[1])
        if search(r'ViceCharacterCount',args):
            ViceCharacterCount = int(args.split("=")[1])

    # 处理完命令行参数后，尝试从SaveTaskGroup加载配置信息
    task_config = load_config_from_savetaskgroup(TaskGroupIndex)
    if task_config:
        print("发现SaveTaskGroup配置信息，正在加载配置...")
        # 注意：不覆盖TaskGroupIndex，因为可能是从命令行指定的
        ViceCharacterCount = task_config.get("vice_character_count", ViceCharacterCount)
        # 从配置中加载PostProcessType（只有在命令行没有指定的情况下）
        if "post_process_type" in task_config:
            # 检查命令行是否已经设置了PostProcessType
            post_process_from_cmdline = any(search(r'PostProcessType', arg) for arg in sys.argv[1:])
            if not post_process_from_cmdline:
                PostProcessType = task_config["post_process_type"]
                print(f"从SaveTaskGroup加载PostProcessType: {PostProcessType}")
                
        # 从配置中加载FastJumpType（只有在命令行没有指定的情况下）
        if "fast_jump_type" in task_config:
            # 检查命令行是否已经设置了FastJumpType
            fast_jump_from_cmdline = any(search(r'FastJumpType', arg) for arg in sys.argv[1:])
            if not fast_jump_from_cmdline:
                FastJumpType = task_config["fast_jump_type"]
                print(f"从SaveTaskGroup加载FastJumpType: {FastJumpType}")
                
        # 从配置中加载AdditionalMaterial（只有在命令行没有指定的情况下）
        if "additional_material" in task_config:
            # 检查命令行是否已经设置了AdditionalMaterial
            additional_material_from_cmdline = any(search(r'AdditionalMaterial', arg) for arg in sys.argv[1:])
            if not additional_material_from_cmdline:
                AdditionalMaterial = task_config["additional_material"]
                print(f"从SaveTaskGroup加载AdditionalMaterial: {AdditionalMaterial}")
                
        print(f"配置已加载 - TaskGroup: {TaskGroupIndex}, 副号: {ViceCharacterCount}, 后处理: {PostProcessType}, 快速副本: {FastJumpType}, 额外材料: {AdditionalMaterial}")
    
    MSmState_CharacterSelect.bUseInverseSelect = TaskGroupIndex
    # PostProcessType说明:
    # 10 default 
    # 1 收周任务奖励
    # 2 自动换黄图
    # 3 自动整理背包
    # 4 自动跳过委托
    # 11 default + 收周任务奖励
    # 12 default + 自动换黄图
    # 13 default + 自动整理背包
    # 14 default + 自动跳过委托
    
    # 只有在没有从SaveTaskGroup或命令行设置时，才使用基于星期的默认值
    post_process_set_by_config = task_config and "post_process_type" in task_config
    post_process_set_by_cmdline = any(search(r'PostProcessType', arg) for arg in sys.argv[1:])
    fast_jump_set_by_config = task_config and "fast_jump_type" in task_config
    fast_jump_set_by_cmdline = any(search(r'FastJumpType', arg) for arg in sys.argv[1:])
    additional_material_set_by_config = task_config and "additional_material" in task_config
    additional_material_set_by_cmdline = any(search(r'AdditionalMaterial', arg) for arg in sys.argv[1:])
    
    if not post_process_set_by_config and not post_process_set_by_cmdline and WeekDay == 6:
        PostProcessType = 11
        
    if not fast_jump_set_by_config and not fast_jump_set_by_cmdline:
        # 基于星期的FastJumpType默认值
        if WeekDay <= 3:
            FastJumpType = 1
        else:
            FastJumpType = 0
    
    # AdditionalMaterial没有基于星期的默认值，保持默认的0
    
    print(f"最终配置 - TaskGroup: {TaskGroupIndex}, 副号: {ViceCharacterCount}, 后处理类型: {PostProcessType}, 快速副本类型: {FastJumpType}, 额外材料: {AdditionalMaterial}")

    IsMainCharacter = False
    hwd_title = "MuMu安卓设备"
    MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
    if MSmState.HandleNumber_Main != 0:
        MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "MuMuNxDevice")
        MSmState.HandleNumber_Keyboard = FindWindowEx(MSmState.HandleNumber_Render, None, None, "nemudisplay")
        DoScreenHit.ApplicationWindowsTitleHeight = 0
    else:
        hwd_title = "雷电模拟器"
        MSmState.HandleNumber_Main = FindWindow(None, hwd_title)
        MSmState.HandleNumber_Render = FindWindowEx(MSmState.HandleNumber_Main, None, None, "TheRender")
        MSmState.HandleNumber_Keyboard = MSmState.HandleNumber_Render
        DoScreenHit.ApplicationWindowsTitleHeight = 0
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
    if bTestMode == False:
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
        StateTable["Exchange"]             = MSmState_Exchange("Exchange")
        StateTable["GuildInfo"]            = MSmState_GuildInfo("GuildInfo")
        StateTable["Loading"]              = MSmState_Loading("Loading")
        StateTable["Login"]                = MSmState_Login("Login")
        StateTable["Mail"]                 = MSmState_Mail("Mail")
        StateTable["Material"]             = MSmState_Material("Material")
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
        StateTable["SpecialWeekly"]        = MSmState_SpecialWeekly("SpecialWeekly")
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

        
        # 使用新的加载函数，优先从SaveTaskGroup读取，回退到Data/TaskGroup
        if bTestMode:        
            TaskJsonExpedition = json.load(open(frozen.app_path() + "\\Data\\TestList"+ str(TestTaskIndex) +".json", 'r', encoding='utf-8'))
            TaskJson = json.load(open(frozen.app_path() + "\\Data\\TestList"+ str(TestTaskIndex) +".json", 'r', encoding='utf-8'))
            TaskJsonMain = json.load(open(frozen.app_path() + "\\Data\\TestList"+ str(TestTaskIndex) +".json", 'r', encoding='utf-8'))
            TaskJsonFive = json.load(open(frozen.app_path() + "\\Data\\TestList"+ str(TestTaskIndex) +".json", 'r', encoding='utf-8'))
        else:
            # 正常模式：优先从SaveTaskGroup加载，回退到Data/TaskGroup（只读）
            TaskJsonExpedition = load_task_json_file(TaskGroupIndex, "TaskListExpedition.json")
            TaskJson = load_task_json_file(TaskGroupIndex, "TaskList.json")
            TaskJsonMain = load_task_json_file(TaskGroupIndex, "TaskListMain.json") 
            TaskJsonFive = load_task_json_file(TaskGroupIndex, "TaskListFive.json")
            
            print(f"\n配置加载完成:")
            print(f"- TaskGroup: {TaskGroupIndex}")
            print(f"- 主号任务数: {len(TaskJsonMain)}")
            print(f"- 副号任务数: {len(TaskJsonFive)}")
            print(f"- 其他角色任务数: {len(TaskJson)}")
            print(f"- 远征任务数: {len(TaskJsonExpedition)}")
            
            # 详细打印各类型角色的任务列表
            print(f"\n=== 详细任务配置 ===")
            print(f"主号任务列表: {TaskJsonMain}")
            print(f"副号任务列表: {TaskJsonFive}")
            print(f"其他角色任务列表: {TaskJson}")
            print(f"远征任务列表: {TaskJsonExpedition}")
            print(f"==================\n")

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
        MSmState_FastJump.FastJumpType = FastJumpType;
        MSmState_PostProcess.PostProcessType = PostProcessType;
        MSmState_Material.bAdditionalMaterial = AdditionalMaterial;
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
                elif CurIndex <= ViceCharacterCount:
                    TaskCur = TaskJsonFive
                else:
                    TaskCur = TaskJson
                #CurrentState.SelectCharacter(i)
                if j != 0 and CurCharacterIndex > 1 and bTestMode == False:
                    CurCharacterIndexFile = open(CurCharacterIndexFileName, "w")
                    CurCharacterIndexFile.write(str(CurCharacterIndex - 1))
                    CurCharacterIndexFile.close()
                if j != 0 and CurCharacterIndexEx > 1 and bTestMode == False:
                    CurCharacterIndexExFile = open(CurCharacterIndexExFileName, "w")
                    CurCharacterIndexExFile.write(str(CurCharacterIndexEx - 1))
                    CurCharacterIndexExFile.close()

                if bExpeditionMode == True and CurIndex > CharacterCount:
                    CurIndex = CharacterCount
                
                MSmState_CharacterSelect.CurrentSelectedCharacterIndex = CurIndex
                MSmState.CharacterIndex = CurIndex
                if CurIndex == 0:
                    MSmState.bMainCharacter = True
                    MSmState.bFastMode = False
                elif CurIndex <= ViceCharacterCount:
                    MSmState.bViceCharacter = True
                    MSmState.bMainCharacter = False
                else:
                    MSmState.bMainCharacter = False
                    if bCanUesFastMode:
                        MSmState.bFastMode = True
   
                TaskLen = len(TaskCur)
                StateIndex = 0
                while StateIndex < TaskLen:
                    TargetStateName = TaskCur[StateIndex]
                    TargetState = StateTable[TargetStateName]
                    StateIndex = StateIndex + 1
                    try:
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
                                MaxIter = 30
                                Iter = 0
                                while NextState.IsUnderState() == False and Iter < MaxIter:
                                    sleep(1)
                                    Iter = Iter + 1
                                if(Iter < MaxIter):
                                    CurrentState = NextState
                                    continue
                                else:
                                    raise RuntimeError("Jump to target state failed")

                            elif res == 1:
                                exit(1)
                            elif res == 2:
                                #if has no jump info, just move to next target
                                break
                    except RuntimeError:
                        StateIndex = 0
                        CurrentState = StateTable["CharacterSelect"]
                        print("Error happened, return to character select and restart task")
                        StateTable["CharacterSelect"].ForceReturnTocharacterSelect()


    else:
        print("please open 雷电模拟器 first")

if __name__ == '__main__':
    main()
