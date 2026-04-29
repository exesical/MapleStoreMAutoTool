#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android 适配版 — 截图、点击、OpenCV 图像识别
用于在 Android 设备上自动化冒险岛M
"""

import os
import cv2
import json
import random
import numpy as np
import subprocess
import sys
from os import walk
from re import search
from time import sleep
from numpy import uint8
from datetime import date

# ============================================================
# 路径工具（兼容 Android APK 与开发环境）
# ============================================================
def get_app_path():
    """获取应用根目录，兼容 Android APK 和 PC 开发环境"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包
        base = os.path.dirname(sys.executable)
    elif getattr(sys, 'android_app', None):
        # Kivy android APK
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            base = activity.getFilesDir().getAbsolutePath()
        except Exception:
            base = os.path.dirname(os.path.abspath(__file__))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return base

def is_android():
    """检测是否运行在 Android 上"""
    return getattr(sys, 'android_app', None) or os.path.exists('/system/bin/screencap')

APP_PATH = get_app_path()
IS_ANDROID = is_android()

# ============================================================
# 常量
# ============================================================
WaittingMaxTimes = 600
HitMaxTimes = 30

# ============================================================
# Android 屏幕点击实现
# ============================================================
class AndroidScreenHit(object):
    """Android 触控模拟 — 使用 input 命令 (兼容 DoScreenHit 接口)"""
    ApplicationWindowsTitleHeight = 0  # 兼容 Windows 属性

    def __init__(self):
        # 生成高斯分布随机位置（与 DoScreenHit 一致）
        self.GaussDistributionSize = 5000
        mx, my = zip(*np.random.normal(loc=0.0, scale=0.45,
                                        size=(self.GaussDistributionSize, 2)))
        self.GaussDistribution = []
        for i in range(len(mx)):
            if mx[i] < 0 and my[i] > 0:
                fx = mx[i] * 1.373
                fy = my[i] * 1.303
                self.GaussDistribution.append([fx, fy])
            elif mx[i] > 0 and my[i] < 0:
                roll = np.random.randint(0, 9)
                if roll < 5:
                    fx = mx[i] * -1.350
                    fy = my[i] * -1.201
                    self.GaussDistribution.append([fx, fy])
                elif roll >= 8:
                    self.GaussDistribution.append([mx[i], my[i]])
                else:
                    fx = mx[i] * 0.618
                    fy = my[i] * 0.618
                    self.GaussDistribution.append([fx, fy])
            else:
                self.GaussDistribution.append([mx[i], my[i]])
        for i in range(len(self.GaussDistribution)):
            self.GaussDistribution[i][0] *= 0.816
            self.GaussDistribution[i][1] *= 0.712
            while abs(self.GaussDistribution[i][0]) > 1:
                self.GaussDistribution[i][0] *= 0.728
            while abs(self.GaussDistribution[i][1]) > 1:
                self.GaussDistribution[i][1] *= 0.642

    def _shell(self, cmd):
        """执行 shell 命令"""
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        except Exception as e:
            print(f"[Hit] shell error: {e}")

    # ---------- 点击 ----------
    def HitPosition(self, HitPos, HitRange):
        """点击指定位置（带高斯抖动）"""
        rx, ry = self.GetRandomHitPosition(HitPos, HitRange)
        x, y = int(round(rx)), int(round(ry))
        self._shell(f"input tap {x} {y}")

    def DoMousePull(self, HitPos, HitRange, Dir, Step, Count):
        """拖拽/滑动"""
        start = self.GetRandomHitPosition(HitPos, HitRange)
        sx, sy = int(round(start[0])), int(round(start[1]))
        ex, ey = sx + Dir[0], sy + Dir[1]
        duration = max(Step * Count * 10, 300)
        self._shell(f"input swipe {sx} {sy} {ex} {ey} {duration}")

    # ---------- 键盘 ----------
    def PressKeyboardESC(self):
        """按返回键（ESC 等效）"""
        self._shell("input keyevent KEYCODE_BACK")

    def PressKeyboard(self):
        """通用按键占位"""
        self._shell("input keyevent KEYCODE_SPACE")

    # ---------- 随机位置 ----------
    def GetRandomHitPosition(self, HitPos, HitRange):
        r = np.random.randint(0, self.GaussDistributionSize)
        return np.multiply(self.GaussDistribution[r], HitRange) + HitPos


# ============================================================
# Android 截图
# ============================================================
def android_take_screenshot():
    """
    使用 screencap 截图并返回 OpenCV 灰度图 (H,W)
    返回 (gray_img, rgb_img, width, height) 或 (None, None, 0, 0)
    """
    tmp_path = "/sdcard/msma_screenshot.png"
    try:
        subprocess.run(["screencap", "-p", tmp_path],
                       capture_output=True, timeout=15)
        if not os.path.exists(tmp_path):
            print("[Screenshot] File not created")
            return None, None, 0, 0
        img_bgr = cv2.imread(tmp_path, cv2.IMREAD_COLOR)
        if img_bgr is None:
            print("[Screenshot] Failed to read image")
            return None, None, 0, 0
        h, w = img_bgr.shape[:2]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        os.remove(tmp_path)
        return gray, img_bgr, w, h
    except Exception as e:
        print(f"[Screenshot] Error: {e}")
        return None, None, 0, 0


# ============================================================
# Android 状态机基类 (完全替代 MSmState)
# ============================================================
GHasGottenAll = False

class AndroidMSmState(object):
    """Android 版状态基类 — 与 Windows 版 MSmState 接口兼容"""

    # ---- 类属性 ----
    bMainCharacter = False
    bViceCharacter = False
    bAllMaterialHasGotten = False
    CharacterIndex = 0
    bUseDebug = False
    bFastMode = False
    bFirstStart = True

    GlobalExitHitPos = [749, 20]
    GlobalExitHitRect = [8, 8]
    ReturnChachaterSelectHitPos = [482, 400]
    ReturnChachaterSelectHitRect = [20, 10]

    # 全局识别图片（惰性加载）
    _GlobalExitPic = None
    _CommonExitPic = None
    _CharacterSelectIdPic = None
    _ForceLeaveConfirmPic = None

    @classmethod
    def _load_pic(cls, rel_path):
        """从 Data/ 目录加载图片，返回灰度图"""
        p = os.path.join(APP_PATH, "Data", rel_path.replace("\\", "/"))
        if not os.path.exists(p):
            print(f"[Pic] NOT FOUND: {p}")
            return None
        img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), -1)
        if img is None:
            return None
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @classmethod
    def _get_global_exit_pic(cls):
        if cls._GlobalExitPic is None:
            cls._GlobalExitPic = cls._load_pic("Global/GameEnd.png")
        return cls._GlobalExitPic

    @classmethod
    def _get_common_exit_pic(cls):
        if cls._CommonExitPic is None:
            cls._CommonExitPic = cls._load_pic("Global/CommonExit.png")
        return cls._CommonExitPic

    @classmethod
    def _get_char_select_id_pic(cls):
        if cls._CharacterSelectIdPic is None:
            cls._CharacterSelectIdPic = cls._load_pic("CharacterSelect/Identification/0.png")
        return cls._CharacterSelectIdPic

    @classmethod
    def _get_force_leave_pic(cls):
        if cls._ForceLeaveConfirmPic is None:
            cls._ForceLeaveConfirmPic = cls._load_pic("CharacterSelect/ForceLeaveConfirm.png")
        return cls._ForceLeaveConfirmPic

    # ---- 实例方法 ----
    def __init__(self, StateName):
        self.ScreenShotImage = None   # 灰度图
        self.ScreenShotImageRGB = None
        self.ScreenShotWidth = 0
        self.ScreenShotHeight = 0

        self.HitHandle = AndroidScreenHit()
        self.Name = StateName

        # ---- 加载 Identification 图片 ----
        base = os.path.join(APP_PATH, "Data", StateName, "Identification").replace("\\", "/")
        self.IdImage = {}
        self.IdImageSize = (0, 0)
        if os.path.isdir(base):
            for f in sorted(os.listdir(base)):
                if f.lower().endswith('.png'):
                    fp = os.path.join(base, f)
                    img = cv2.imdecode(np.fromfile(fp, dtype=np.uint8), -1)
                    if img is None:
                        continue
                    self.IdImageSize = img.shape[:2]
                    idx = len(self.IdImage)
                    self.IdImage[idx] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if not self.IdImage:
            print(f"[AndroidMSmState] No Identification pics for '{StateName}'")

        # ---- 加载 HitInfo ----
        self.HitInfo = {}
        hit_path = os.path.join(APP_PATH, "Data", StateName, "HitInfo.json").replace("\\", "/")
        if os.path.exists(hit_path):
            with open(hit_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                self.HitInfo[item["OpName"]] = [item["ClickPos"], item["ClickRange"]]

        # ---- 加载 JumpInfo ----
        self.JumpInfo = {}
        jump_path = os.path.join(APP_PATH, "Data", StateName, "JumpInfo.json").replace("\\", "/")
        if os.path.exists(jump_path):
            with open(jump_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                self.JumpInfo[item["NextStateName"]] = [item["ClickPos"], item["ClickRange"]]

    # ========== 截图 ==========
    def RefreshScreenShot(self):
        """截图并转换为灰度"""
        gray, rgb, w, h = android_take_screenshot()
        if gray is None:
            print("[WARN] RefreshScreenShot failed, using previous frame")
            return
        self.ScreenShotImage = gray
        self.ScreenShotImageRGB = rgb
        self.ScreenShotWidth = w
        self.ScreenShotHeight = h

    # ========== 图片识别 ==========
    def IsUnderState(self, MatchingThreshold=0.8):
        self.RefreshScreenShot()
        if not self.IdImage:
            return True
        for img in self.IdImage.values():
            if self.IsPicMatching(img, MatchingThreshold):
                print(f"Now is under state - {self.Name}")
                return True
        print(f"Now is NOT under state - {self.Name}")
        return False

    def GetPicPos(self, InPic, MatchingThreshold=0.8, method=cv2.TM_CCOEFF_NORMED):
        if self.ScreenShotImage is None:
            return None
        res = cv2.matchTemplate(self.ScreenShotImage, InPic, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_loc if max_val >= MatchingThreshold else None

    def IsPicMatching(self, InPic, MatchingThreshold=0.8):
        if self.ScreenShotImage is None or InPic is None:
            return False
        res = cv2.matchTemplate(self.ScreenShotImage, InPic, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val >= MatchingThreshold

    # ========== 点击操作 ==========
    def DoHit(self, HitPos, HitRange):
        self.HitHandle.HitPosition(HitPos, HitRange)
        sleep(random.randint(20, 80) / 100.0)

    def DoHitByName(self, hitname):
        print(f"Hit position by Name - {hitname}")
        info = self.HitInfo.get(hitname)
        if info:
            self.DoHit(info[0], info[1])

    def DoHitByNameFast(self, hitname):
        print(f"Hit position by Name(Fast) - {hitname}")
        info = self.HitInfo.get(hitname)
        if info:
            self.HitHandle.HitPosition(info[0], info[1])

    # ========== 状态跳转 ==========
    def JumpToTarget(self, TargetState, WaitingTime=0.5):
        print(f"Try jump to target {TargetState.Name} from {self.Name}")
        info = self.JumpInfo.get(TargetState.Name)
        if info is None:
            print(f"State {self.Name} has no jump to {TargetState.Name}")
            return 2
        HitPos, HitRange = info
        op_times = 0
        st = 3 if (self.Name == "SystemMenuOpening" and
                   TargetState.Name in ("GameModeDefault", "FastJump")) else 1
        while True:
            self.DoHit(HitPos, HitRange)
            sleep(st)
            op_times += 1
            if TargetState.IsUnderState():
                print(f"Jump success to {TargetState.Name}")
                sleep(WaitingTime)
                return 0
            if op_times > HitMaxTimes:
                raise RuntimeError(f"Cannot leave state {self.Name}")

    # ========== 图片文件读取 ==========
    def ReadPicArray(self, PicName):
        base = os.path.join(APP_PATH, "Data", self.Name).replace("\\", "/")
        out = []
        if not os.path.isdir(base):
            return out
        for f in os.listdir(base):
            if f.lower().endswith('.png') and PicName in f:
                fp = os.path.join(base, f)
                img = cv2.imdecode(np.fromfile(fp, dtype=np.uint8), -1)
                if img is not None:
                    out.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        return out

    def ReadPicMap(self):
        base = os.path.join(APP_PATH, "Data", self.Name).replace("\\", "/")
        m = {}
        if not os.path.isdir(base):
            return m
        for f in os.listdir(base):
            if f.lower().endswith('.png'):
                fp = os.path.join(base, f)
                img = cv2.imdecode(np.fromfile(fp, dtype=np.uint8), -1)
                if img is not None:
                    key = f[:-4]
                    m[key] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return m

    def ReadPic(self, PicName):
        fp = os.path.join(APP_PATH, "Data", self.Name, f"{PicName}.png").replace("\\", "/")
        img = cv2.imdecode(np.fromfile(fp, dtype=np.uint8), -1)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img is not None else None

    # ========== 保存截图 ==========
    def SaveScreenShot(self, Prefix=""):
        if self.ScreenShotImageRGB is None:
            return
        today_str = date.today().strftime('%Y-%m-%d')
        d = os.path.join(APP_PATH, f"{self.Name}_AutoSave", today_str)
        os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, f"{Prefix}{AndroidMSmState.CharacterIndex}.png")
        cv2.imwrite(fn, self.ScreenShotImageRGB)

    # ========== 返回角色选择 ==========
    def ForceReturnTocharacterSelect(self):
        max_loop = 50
        loop = 0
        while not self.IsUnderState() and loop < max_loop:
            loop += 1
            self.RefreshScreenShot()
            for _ in range(30):
                self.RefreshScreenShot()
                g = self._get_global_exit_pic()
                c = self._get_common_exit_pic()
                if (g and self.IsPicMatching(g, 0.9)) or \
                   (c and self.IsPicMatching(c, 0.9)) or \
                   self.IsUnderState():
                    break
                self.HitHandle.PressKeyboardESC()
                sleep(1)
            for _ in range(2):
                self.DoHit([480, 400], [30, 10])
                sleep(1)

    # ========== 等待图片出现 ==========
    def WaitUntil(self, CheckPic, MaxTime=600):
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic)
        loop = 0
        while not ok:
            sleep(1)
            self.RefreshScreenShot()
            ok = self.IsPicMatching(CheckPic)
            loop += 1
            if loop > MaxTime:
                raise RuntimeError("WaitUntil InfiniteLoop")

    # ========== 内部跳转辅助 ==========
    def TryInnerJumpByPos(self, HitPos, CheckPic, InMaxHitTimes=None):
        if InMaxHitTimes is None:
            InMaxHitTimes = HitMaxTimes
        self.DoHit(HitPos[0], HitPos[1])
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic)
        loop = 0
        while not ok:
            self.DoHit(HitPos[0], HitPos[1])
            sleep(1)
            self.RefreshScreenShot()
            ok = ok or self.IsPicMatching(CheckPic)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok or self.IsPicMatching(CheckPic)
            loop += 1
            if loop > InMaxHitTimes:
                raise RuntimeError("TryInnerJumpByPos InfiniteLoop")

    def TryInnerJump(self, HitName, CheckPic, MatchingThreshold=0.8):
        self.DoHitByName(HitName)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic, MatchingThreshold)
        loop = 0
        while not ok:
            self.DoHitByName(HitName)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok or self.IsPicMatching(CheckPic, MatchingThreshold)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok or self.IsPicMatching(CheckPic, MatchingThreshold)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryInnerJump InfiniteLoop")

    def TryLeaveJumpByPos(self, HitPos, CheckPic):
        self.DoHit(HitPos[0], HitPos[1])
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic)
        loop = 0
        while ok:
            self.DoHit(HitPos[0], HitPos[1])
            sleep(1)
            self.RefreshScreenShot()
            ok = ok and self.IsPicMatching(CheckPic)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok and self.IsPicMatching(CheckPic)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryLeaveJumpByPos InfiniteLoop")

    def TryLeaveJump(self, HitName, CheckPic, MatchingThreshold=0.8):
        self.DoHitByName(HitName)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic, MatchingThreshold)
        loop = 0
        while ok:
            self.DoHitByName(HitName)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok and self.IsPicMatching(CheckPic, MatchingThreshold)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok and self.IsPicMatching(CheckPic, MatchingThreshold)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryLeaveJump InfiniteLoop")

    def TryLeaveJump2(self, HitName, CheckPic, CheckPic2):
        self.DoHitByName(HitName)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2)
        loop = 0
        while ok:
            self.DoHitByName(HitName)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok and (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok and (self.IsPicMatching(CheckPic) or self.IsPicMatching(CheckPic2))
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryLeaveJump2 InfiniteLoop")

    def TryLeaveJumpAuto(self, CheckPic, HitOffset, HitRange):
        sleep(1)
        self.RefreshScreenShot()
        pos = self.GetPicPos(CheckPic, 0.9, cv2.TM_CCORR_NORMED)
        if pos is None:
            return
        self.DoHit([pos[0] + HitOffset[0], pos[1] + HitOffset[1]], HitRange)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic)
        loop = 0
        while ok:
            pos = self.GetPicPos(CheckPic, 0.9, cv2.TM_CCORR_NORMED)
            if pos is None:
                return
            self.DoHit([pos[0] + HitOffset[0], pos[1] + HitOffset[1]], HitRange)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok and self.IsPicMatching(CheckPic)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok and self.IsPicMatching(CheckPic)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryLeaveJumpAuto InfiniteLoop")

    def GetHitInfo(self, HitPic, HitRange=0.5, MatchingThreshold=0.9):
        sleep(0.5)
        self.RefreshScreenShot()
        pos = self.GetPicPos(HitPic, MatchingThreshold)
        if pos is None:
            return None
        h, w = HitPic.shape[:2]
        return [[pos[0] + w // 2, pos[1] + h // 2],
                [int(w * HitRange), int(h * HitRange)]]

    def TryLeaveJumpByPic(self, HitPic, CheckPic, HitRange=0.5,
                          MatchingThreshold=0.8, OpName=""):
        sleep(1)
        print(f"TryLeaveJumpByPic threshold={MatchingThreshold} OpName={OpName}")
        self.RefreshScreenShot()
        pos = self.GetPicPos(HitPic, MatchingThreshold)
        if pos is None:
            return
        h, w = HitPic.shape[:2]
        auto_pos = [pos[0] + w // 2, pos[1] + h // 2]
        auto_range = [int(w * HitRange), int(h * HitRange)]
        self.DoHit(auto_pos, auto_range)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic, MatchingThreshold)
        loop = 0
        while ok:
            pos = self.GetPicPos(HitPic, MatchingThreshold)
            if pos is not None:
                auto_pos = [pos[0] + w // 2, pos[1] + h // 2]
            self.DoHit(auto_pos, auto_range)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok and self.IsPicMatching(CheckPic, MatchingThreshold)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok and self.IsPicMatching(CheckPic, MatchingThreshold)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryLeaveJumpByPic InfiniteLoop")

    def DoHitByPic(self, HitPic, HitRange=0.5, MatchingThreshold=0.8, HitTimes=3):
        sleep(1)
        self.RefreshScreenShot()
        pos = self.GetPicPos(HitPic, MatchingThreshold)
        if pos is None:
            return
        h, w = HitPic.shape[:2]
        auto_pos = [pos[0] + w // 2, pos[1] + h // 2]
        auto_range = [int(w * HitRange), int(h * HitRange)]
        for _ in range(HitTimes):
            self.DoHit(auto_pos, auto_range)

    def TryInnerJumpByPic(self, HitPic, CheckPic, HitRange=0.5,
                          MatchingThreshold=0.8, OpName="",
                          method=cv2.TM_CCOEFF_NORMED):
        sleep(1)
        print(f"TryInnerJumpByPic threshold={MatchingThreshold} OpName={OpName}")
        self.RefreshScreenShot()
        pos = self.GetPicPos(HitPic, MatchingThreshold, method)
        if pos is None:
            return
        h, w = HitPic.shape[:2]
        auto_pos = [pos[0] + w // 2, pos[1] + h // 2]
        auto_range = [int(w * HitRange), int(h * HitRange)]
        self.DoHit(auto_pos, auto_range)
        sleep(1)
        self.RefreshScreenShot()
        ok = self.IsPicMatching(CheckPic, MatchingThreshold)
        loop = 0
        while not ok:
            pos = self.GetPicPos(HitPic, MatchingThreshold)
            if pos is not None:
                auto_pos = [pos[0] + w // 2, pos[1] + h // 2]
            self.DoHit(auto_pos, auto_range)
            sleep(1)
            self.RefreshScreenShot()
            ok = ok or self.IsPicMatching(CheckPic, MatchingThreshold)
            for _ in range(3):
                sleep(0.3)
                self.RefreshScreenShot()
                ok = ok or self.IsPicMatching(CheckPic, MatchingThreshold)
            loop += 1
            if loop > HitMaxTimes:
                raise RuntimeError("TryInnerJumpByPic InfiniteLoop")

    def ExecuteSequenceByFolder(self, FolderName, HitRange=0.5, MatchingThreshold=0.8):
        base = os.path.join(APP_PATH, "Data", self.Name, FolderName).replace("\\", "/")
        if not os.path.isdir(base):
            return False

        hit_pics = {}
        for f in os.listdir(base):
            if f.startswith("HitPic_") and f.endswith(".png"):
                idx = f.replace("HitPic_", "").replace(".png", "")
                img = cv2.imdecode(np.fromfile(os.path.join(base, f), dtype=np.uint8), -1)
                if img is not None:
                    hit_pics[idx] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        check_pics = {}
        for f in os.listdir(base):
            if f.startswith("CheckPic_") and f.endswith(".png"):
                parts = f.replace("CheckPic_", "").replace(".png", "").rsplit("_", 1)
                if len(parts) == 2:
                    idx, suffix = parts
                    img = cv2.imdecode(np.fromfile(os.path.join(base, f), dtype=np.uint8), -1)
                    if img is not None:
                        check_pics[idx] = (suffix, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

        for idx in sorted(hit_pics, key=lambda x: int(x)):
            hp = hit_pics[idx]
            if idx in check_pics:
                suffix, cp = check_pics[idx]
                if suffix == "L":
                    self.TryLeaveJumpByPic(hp, cp, HitRange, MatchingThreshold)
                else:
                    self.TryInnerJumpByPic(hp, cp, HitRange, MatchingThreshold)
            else:
                self.RefreshScreenShot()
                pos = self.GetPicPos(hp, MatchingThreshold)
                if pos is not None:
                    h, w = hp.shape[:2]
                    self.DoHit([pos[0] + w // 2, pos[1] + h // 2],
                               [int(w * HitRange), int(h * HitRange)])
            sleep(0.5)
        return True

    # ========== 杂项 ==========
    def Processing(self):
        return True

    def DoAddTimes(self):
        pass

    def CloseAuction(self):
        pass

    def WaitingForAutoFightingFinished(self):
        self.RefreshScreenShot()
        ok = self.IsPicMatching(self.ExitIdImage) if hasattr(self, 'ExitIdImage') else False
        loop = 0
        while not ok:
            sleep(5)
            self.RefreshScreenShot()
            self.CloseAuction()
            ok = self.IsPicMatching(self.ExitIdImage) if hasattr(self, 'ExitIdImage') else False
            loop += 1
            if loop > WaittingMaxTimes:
                raise RuntimeError("WaitingForAutoFightingFinished InfiniteLoop")


# ============================================================
# Android 子类实现（各游戏状态）
# ============================================================
class AndroidMSmState_CharacterSelect(AndroidMSmState):
    CurrentSelectedCharacterIndex = 0
    bUseInverseSelect = 0

    def __init__(self, StateName):
        super().__init__(StateName)
        self._IsMainCharacterIdImage = self._load_pic(
            "CharacterSelect/IsMainCharacterSelected.png")

    def TrySelecteMainCharacter(self):
        self.DoHitByName("SelectCharacter0")
        self.RefreshScreenShot()
        return (self._IsMainCharacterIdImage is not None and
                self.IsPicMatching(self._IsMainCharacterIdImage))

    def Processing(self):
        while not self.TrySelecteMainCharacter():
            self.DoHitByName("NextCharacterPage")
        c_page = AndroidMSmState_CharacterSelect.CurrentSelectedCharacterIndex // 7
        c_index = AndroidMSmState_CharacterSelect.CurrentSelectedCharacterIndex % 7
        for _ in range(c_page):
            self.DoHitByName("NextCharacterPage")
            sleep(0.5)
        info = self.HitInfo.get(f"SelectCharacter{c_index}")
        if info:
            for _ in range(random.randint(2, 4)):
                self.DoHit(info[0], info[1])
        return True


class AndroidMSmState_ChangeCharacter(AndroidMSmState):
    pass


class AndroidMSmState_FastJump(AndroidMSmState):
    FastJumpType = 0

    def __init__(self, StateName):
        super().__init__(StateName)
        self.EnterCheckPics = self.ReadPicArray("EnterCheck")
        self.EnterHitPics = self.ReadPicArray("EnterHit")
        self.CheckAutoFighting = self.ReadPicArray("CheckAutoFighting")
        self.ExitIdImage = self.ReadPic("Exit")

    def DoFastJump(self, Target):
        if AndroidMSmState_FastJump.FastJumpType == 0:
            self.DoClickFastJump()
        else:
            self.DoMenuFastJump()

    def DoClickFastJump(self):
        for hp in self.EnterHitPics:
            self.DoHitByPic(hp, 0.5, 0.8)
            for cp in self.EnterCheckPics:
                if self.IsPicMatching(cp):
                    return
        for cp in self.CheckAutoFighting:
            if self.IsPicMatching(cp):
                return
        self.DoHitByName("ClickJump")

    def DoMenuFastJump(self):
        self.DoHitByName("OpenMenu")
        sleep(1)
        self.DoHitByName("SelectMenu")
        sleep(1)
        self.DoHitByName("ClickJump")

    def Processing(self):
        self.DoFastJump(0)
        return True


class AndroidMSmState_Exchange(AndroidMSmState):
    pass


class AndroidMSmState_GameModeDefault(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        return True


class AndroidMSmState_GuildInfo(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Loading(AndroidMSmState):
    def IsUnderState(self, MatchingThreshold=0.8):
        self.RefreshScreenShot()
        return super().IsUnderState(MatchingThreshold)


class AndroidMSmState_Login(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")


class AndroidMSmState_Mail(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("GetAll", self.ExitIdImage)
        return True


class AndroidMSmState_Material(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")
        self.MaterialBegin = self.ReadPicArray("MaterialBegin")
        self.EnterMaterialPics = self.ReadPicArray("EnterMaterial")

    def Processing(self):
        self.DoHitByName("GotoMateria")
        for begin_pic in self.MaterialBegin:
            self.TryInnerJumpByPic(begin_pic, self.ExitIdImage, 0.5, 0.8, "Processing")
        self.SaveScreenShot()
        return True


class AndroidMSmState_SystemMenuOpening(AndroidMSmState):
    def Processing(self):
        return True


class AndroidMSmState_Wander(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_DailyTask(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")
        self.DailyRewardPics = self.ReadPicArray("DailyReward")

    def Processing(self):
        for rp in self.DailyRewardPics:
            self.TryInnerJumpByPic(rp, self.ExitIdImage, 0.5, 0.8, "CollectDailyReward")
        self.TryInnerJump("AcceptDaily", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_TeamCommon(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")
        self.SelectDiff = self.ReadPicArray("SelectDiff")
        self.EnterPics = self.ReadPicArray("Enter")
        self.PreparePics = self.ReadPicArray("Prepare")


class AndroidMSmState_Expedition(AndroidMSmState_TeamCommon):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExpeditionBegin = self.ReadPicArray("ExpeditionBegin")
        self.ExpeditionEnterPics = self.ReadPicArray("ExpeditionEnter")

    def Processing(self):
        self.TryInnerJump("EnterExpedition", self.ExitIdImage)
        self.TryInnerJump("EnterExpedition2", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Elite(AndroidMSmState_TeamCommon):
    def Processing(self):
        for ep in self.EnterPics:
            self.TryInnerJumpByPic(ep, self.ExitIdImage, 0.5, 0.8, "EnterElite")
        self.WaitingForAutoFightingFinished()
        self.SaveScreenShot()
        return True


class AndroidMSmState_Pirate(AndroidMSmState_TeamCommon):
    def Processing(self):
        for ep in self.EnterPics:
            self.TryInnerJumpByPic(ep, self.ExitIdImage, 0.5, 0.8, "EnterPirate")
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_NitePyramid(AndroidMSmState_TeamCommon):
    def Processing(self):
        for ep in self.EnterPics:
            self.TryInnerJumpByPic(ep, self.ExitIdImage, 0.5, 0.8, "EnterNitePyramid")
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Dimension(AndroidMSmState_TeamCommon):
    def Processing(self):
        for ep in self.EnterPics:
            self.TryInnerJumpByPic(ep, self.ExitIdImage, 0.5, 0.8, "EnterDimension")
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_MonsterPark(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterMonsterPark", self.ExitIdImage)
        self.SaveScreenShot()
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Tangyun(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterTangyun", self.ExitIdImage)
        self.SaveScreenShot()
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Weekly(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterWeekly", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_SpecialWeekly(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterSpecialWeekly", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_Wulin(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterWulin", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


class AndroidMSmState_PostProcess(AndroidMSmState):
    bDefault = True
    bWeeklyReward = False
    bAutoChange = False
    bOrganizePackage = False
    bSkipCommission = False
    bAdditionalMaterial = False

    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")
        self.WeeklyRewardPics = self.ReadPicArray("WeeklyReward")
        self.AutoChangePics = self.ReadPicArray("AutoChange")
        self.OrganizePackagePics = self.ReadPicArray("OrganizePackage")
        self.AdditionalMaterialPics = self.ReadPicArray("AdditionalMaterial")

    def Processing(self):
        if self.bDefault:
            self.TryInnerJump("SendPopularity", self.ExitIdImage)
            self.TryInnerJump("TradeItem", self.ExitIdImage)
            self.TryInnerJump("DailyQuest", self.ExitIdImage)
        if self.bWeeklyReward:
            for rp in self.WeeklyRewardPics:
                self.TryInnerJumpByPic(rp, self.ExitIdImage, 0.5, 0.8, "WeeklyReward")
            self.SaveScreenShot("WeeklyReward_")
        if self.bAutoChange:
            for cp in self.AutoChangePics:
                self.TryInnerJumpByPic(cp, self.ExitIdImage, 0.5, 0.8, "AutoChange")
            self.SaveScreenShot("Charge_")
        if self.bOrganizePackage:
            for op in self.OrganizePackagePics:
                self.TryInnerJumpByPic(op, self.ExitIdImage, 0.5, 0.8, "OrganizePackage")
            self.SaveScreenShot("Package_")
        if self.bSkipCommission:
            self.TryInnerJump("SkipCommission", self.ExitIdImage)
        if self.bAdditionalMaterial:
            for ap in self.AdditionalMaterialPics:
                self.TryInnerJumpByPic(ap, self.ExitIdImage, 0.5, 0.8, "AdditionalMaterial")
        return True


class AndroidMSmState_Evolution(AndroidMSmState):
    def __init__(self, StateName):
        super().__init__(StateName)
        self.ExitIdImage = self.ReadPic("Exit")

    def Processing(self):
        self.TryInnerJump("EnterEvolution", self.ExitIdImage)
        self.WaitingForAutoFightingFinished()
        return True


# ============================================================
# 主自动化流程 (Android 版 MSmAuto.main 替代)
# ============================================================
def load_json_android(filename):
    """加载 Data/ 下的 JSON 文件"""
    p = os.path.join(APP_PATH, "Data", filename).replace("\\", "/")
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def clean_old_autosave_folders():
    """清理所有非当天的 _AutoSave 子文件夹（Android版）"""
    today_str = date.today().strftime('%Y-%m-%d')
    for cur_dir, sub_dirs, _ in walk(APP_PATH):
        for sub_dir in sub_dirs:
            if sub_dir.endswith('_AutoSave'):
                auto_save_path = os.path.join(cur_dir, sub_dir)
                for date_dir in os.listdir(auto_save_path):
                    date_dir_path = os.path.join(auto_save_path, date_dir)
                    if os.path.isdir(date_dir_path) and date_dir != today_str:
                        import shutil
                        shutil.rmtree(date_dir_path)
                        print(f"[CleanOldAutoSave] 已删除过期截图: {date_dir_path}")
        break  # 只扫描根目录


def run_android_automation(task_group_index=0, character_count=5,
                           vice_character_count=0,
                           b_post_process_default=True,
                           b_post_process_weekly_reward=False,
                           b_post_process_auto_change=False,
                           b_post_process_organize_package=False,
                           b_post_process_skip_commission=False,
                           b_post_process_additional_material=False,
                           fast_jump_type=0,
                           b_expedition_mode_enable=False,
                           expedition_end_minute=55,
                           progress_callback=None,
                           log_callback=None):
    """
    安卓自动化主流程
    progress_callback(value: float) — 进度 0-100
    log_callback(msg: str) — 日志输出
    """
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    def progress(v):
        if progress_callback:
            progress_callback(v)

    log("=== 冒险岛M 安卓自动化启动 ===")

    # ---- 清理过期的 AutoSave 截图 ----
    clean_old_autosave_folders()

    # ---- 构造状态表 ----
    StateTable = {}
    StateTable["CharacterSelect"] = AndroidMSmState_CharacterSelect("CharacterSelect")
    StateTable["ChangeCharacter"] = AndroidMSmState_ChangeCharacter("ChangeCharacter")
    StateTable["GameModeDefault"] = AndroidMSmState_GameModeDefault("GameModeDefault")
    StateTable["Exchange"] = AndroidMSmState_Exchange("Exchange")
    StateTable["GuildInfo"] = AndroidMSmState_GuildInfo("GuildInfo")
    StateTable["Loading"] = AndroidMSmState_Loading("Loading")
    StateTable["Login"] = AndroidMSmState_Login("Login")
    StateTable["Mail"] = AndroidMSmState_Mail("Mail")
    StateTable["Material"] = AndroidMSmState_Material("Material")
    StateTable["SystemMenuOpening"] = AndroidMSmState_SystemMenuOpening("SystemMenuOpening")
    StateTable["Wander"] = AndroidMSmState_Wander("Wander")
    StateTable["Elite"] = AndroidMSmState_Elite("Elite")
    StateTable["Pirate"] = AndroidMSmState_Pirate("Pirate")
    StateTable["NitePyramid"] = AndroidMSmState_NitePyramid("NitePyramid")
    StateTable["Dimension"] = AndroidMSmState_Dimension("Dimension")
    StateTable["MonsterPark"] = AndroidMSmState_MonsterPark("MonsterPark")
    StateTable["FastJump"] = AndroidMSmState_FastJump("FastJump")
    StateTable["Tangyun"] = AndroidMSmState_Tangyun("Tangyun")
    StateTable["Weekly"] = AndroidMSmState_Weekly("Weekly")
    StateTable["SpecialWeekly"] = AndroidMSmState_SpecialWeekly("SpecialWeekly")
    StateTable["Wulin"] = AndroidMSmState_Wulin("Wulin")
    StateTable["PostProcess"] = AndroidMSmState_PostProcess("PostProcess")
    StateTable["Expedition"] = AndroidMSmState_Expedition("Expedition")
    StateTable["DailyTask"] = AndroidMSmState_DailyTask("DailyTask")

    # ---- 加载全局跳转表 ----
    GlobalJumpTable = {}
    gjt = load_json_android("GlobalJumpTable.json")
    for item in gjt:
        target_name = item["TargetStateName"]
        target_table = {}
        for row in item["TargetTable"]:
            target_table[row[0]] = row[1]
        GlobalJumpTable[target_name] = target_table

    # ---- 加载任务列表 ----
    TaskJson = load_json_android(f"TaskList{task_group_index}.json")
    if not TaskJson:
        TaskJson = load_json_android("TestList0.json")
    TaskJsonExpedition = load_json_android("TaskListExpedition.json")
    if not TaskJsonExpedition:
        TaskJsonExpedition = TaskJson

    log(f"任务列表加载完成，共 {len(TaskJson)} 个任务")

    # ---- 检查初始状态 ----
    InitState = StateTable["CharacterSelect"]
    if not InitState.IsUnderState():
        log("错误：请在角色选择界面启动")
        return

    # ---- 设置参数 ----
    AndroidMSmState_FastJump.FastJumpType = fast_jump_type
    AndroidMSmState_PostProcess.bDefault = b_post_process_default
    AndroidMSmState_PostProcess.bWeeklyReward = b_post_process_weekly_reward
    AndroidMSmState_PostProcess.bAutoChange = b_post_process_auto_change
    AndroidMSmState_PostProcess.bOrganizePackage = b_post_process_organize_package
    AndroidMSmState_PostProcess.bSkipCommission = b_post_process_skip_commission
    AndroidMSmState_PostProcess.bAdditionalMaterial = b_post_process_additional_material

    # ---- 主循环 ----
    for idx in range(character_count):
        log(f"--- 处理角色 {idx + 1}/{character_count} ---")
        progress((idx / character_count) * 100)

        AndroidMSmState_CharacterSelect.CurrentSelectedCharacterIndex = idx
        AndroidMSmState.CharacterIndex = idx
        AndroidMSmState.bMainCharacter = (idx == 0)
        AndroidMSmState.bViceCharacter = (0 < idx <= vice_character_count)
        AndroidMSmState.bFastMode = (idx > vice_character_count)

        CurrentState = InitState
        TaskCur = TaskJson
        TaskLen = len(TaskCur)

        state_idx = 0
        while state_idx < TaskLen:
            target_name = TaskCur[state_idx]
            state_idx += 1
            TargetState = StateTable.get(target_name)
            if TargetState is None:
                log(f"跳过未知状态: {target_name}")
                continue

            try:
                while CurrentState.Name != target_name:
                    log(f"处理当前状态: {CurrentState.Name}")
                    CurrentState.Processing()

                    # 查全局跳转表
                    next_name = GlobalJumpTable.get(target_name, {}).get(CurrentState.Name)
                    if next_name is None:
                        log(f"无跳转路径 {CurrentState.Name} -> {target_name}，跳过")
                        break
                    NextState = StateTable[next_name]

                    res = CurrentState.JumpToTarget(NextState)
                    if res == 0:
                        for _ in range(30):
                            if NextState.IsUnderState():
                                break
                            sleep(1)
                        if NextState.IsUnderState():
                            CurrentState = NextState
                        else:
                            raise RuntimeError("Jump target state not reached")
                    elif res == 2:
                        break

            except RuntimeError as e:
                log(f"错误: {e}，返回角色选择")
                StateTable["CharacterSelect"].ForceReturnTocharacterSelect()
                CurrentState = StateTable["CharacterSelect"]
                state_idx = 0  # 重新执行该角色任务

        log(f"角色 {idx + 1} 完成")

    progress(100)
    log("=== 所有角色自动化完成 ===")


# ============================================================
# 测试入口
# ============================================================
if __name__ == '__main__':
    print("AndroidMSmState 模块运行于:", "Android" if IS_ANDROID else "PC(模拟测试)")
    print(f"APP_PATH = {APP_PATH}")
    print("请通过 main.py (Kivy App) 启动自动化流程")
