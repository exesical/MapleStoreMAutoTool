import math
import numpy as np
import matplotlib.pyplot as plt
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE, WM_MOUSEMOVE, WM_MOUSEWHEEL,MK_LBUTTON, WM_KEYDOWN,WM_KEYUP
from time import sleep

#为了兼容不容模拟器，后续所有Hitinfo 和jumpinfo坐标计算必须先去掉tile的高度

class DoScreenHit(object):
    ApplicationWindowsTitleHeight = 0
    """description of class"""
    def __init__(self, HandleNumber, HandleNumber_Keyboard):
        self.HandleNumber = HandleNumber;
        self.HandleNumber_Keyboard = HandleNumber_Keyboard;
        self.GaussDistributionSize = 5000;
        #random gauss list generate
        mx, my = zip(*np.random.normal(loc = 0.0, scale = 0.45, size = (self.GaussDistributionSize, 2)))
        self.GaussDistribution = []

        for i in range(len(mx)):
            #gen hit random data from gauss but add some jitters
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
            self.GaussDistribution[i][0] = self.GaussDistribution[i][0] * 0.816
            self.GaussDistribution[i][1] = self.GaussDistribution[i][1] * 0.712

            while(abs(self.GaussDistribution[i][0]) > 1):
                self.GaussDistribution[i][0] = self.GaussDistribution[i][0] * 0.728

            while(abs(self.GaussDistribution[i][1]) > 1):
                self.GaussDistribution[i][1] = self.GaussDistribution[i][1] * 0.642
        

    def HitPosition(self, HitPos, HitRange):
        randompos_f = self.GetRandomHitPosition(HitPos, HitRange);
        randompos_x = int(randompos_f[0])
        randompos_y = int(randompos_f[1])
        long_position = MAKELONG(randompos_x, randompos_y)
        SendMessage(self.HandleNumber, WM_ACTIVATE, WA_ACTIVE, 0)
        SendMessage(self.HandleNumber, WM_LBUTTONDOWN, 0, long_position)  # press
        sleep((np.random.randint(5, 10)) / 100)  # keep random time
        SendMessage(self.HandleNumber, WM_LBUTTONUP, 0, long_position)  # release
        
    # def MousePull(self, StartPos, EndPos, StepCount, RandRange):
    #     StartPosR = self.GetRandomHitPosition(StartPos, RandRange)
    #     EndPosR = self.GetRandomHitPosition(EndPos, RandRange)
    #     StepSize = abs(EndPosR - StartPosR) / StepCount + [1,1];
    #     if EndPosR[0]<StartPosR[0]:
    #         StepSize[0] = -StepSize[0]
    #     if EndPosR[1]<StartPosR[1]:
    #         StepSize[1] = -StepSize[1]
    #     long_position_start = MAKELONG(StartPosR[0], StartPosR[1])
    #     long_position_end = MAKELONG(EndPosR[0], EndPosR[1])
    #     SendMessage(self.HandleNumber, WM_ACTIVATE, WA_ACTIVE, 0)
    #     SendMessage(self.HandleNumber, WM_LBUTTONDOWN, 0, long_position_start)  # press

    def DoMousePull(self, HitPos, HitRange, Dir, Step, Count):        
        randompos_f = self.GetRandomHitPosition(HitPos, HitRange);
        randompos_x_start = int(randompos_f[0])
        randompos_x_end = randompos_x_start + Dir[0]
        randompos_y_start = int(randompos_f[1])
        randompos_y_end = randompos_y_start + Dir[1]
        long_position_start = MAKELONG(randompos_x_start, randompos_y_start)
        long_position_end = MAKELONG(randompos_x_end, randompos_y_end)
        SendMessage(self.HandleNumber, WM_ACTIVATE, WA_ACTIVE, 0)
        move_x = np.linspace(randompos_x_start, randompos_x_end, num=Step)[0:]
        move_y = np.linspace(randompos_y_start, randompos_y_end, num=Step)[0:]
        for i in range(0, Count):
            SendMessage(self.HandleNumber, WM_LBUTTONDOWN, 0, long_position_start)  # press
            for i in range(0, Step): 
                x = int(round(move_x[i]))
                y = int(round(move_y[i]))
                SendMessage(self.HandleNumber, WM_LBUTTONDOWN, 0, MAKELONG(x,y))  # press
                sleep(0.01)
            SendMessage(self.HandleNumber, WM_LBUTTONUP, 0, long_position_end)  # release
        
        return
        

    def GetRandomHitPosition(self, HitPos, HitRange):
        r = np.random.randint(0,self.GaussDistributionSize);
        RandomPos = np.multiply(self.GaussDistribution[r], HitRange) + HitPos
        return RandomPos

    def PressKeyboard(self):
        SendMessage(self.HandleNumber_Keyboard, WM_KEYDOWN, 0x50, 0)
        sleep(0.02)
        SendMessage(self.HandleNumber_Keyboard, WM_KEYUP, 0x50, 0)

#test
if __name__ == '__main__':
    hit = DoScreenHit(0)
    px = []
    py = []
    for i in range(1000):
        rp = hit.GetRandomHitPosition([0,0],[100,50])
        px.append(rp[0])
        py.append(rp[1])

    plt.plot(px, py,'o', color = 'b')
    plt.show()