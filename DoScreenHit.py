import math
import numpy as np
import matplotlib.pyplot as plt
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE
from time import sleep
class DoScreenHit(object):
    """description of class"""
    def __init__(self, HandleNumber):
        self.HandleNumber = HandleNumber;
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
        randompos_y = int(randompos_f[1] - 33)
        long_position = MAKELONG(randompos_x, randompos_y)
        SendMessage(self.HandleNumber, WM_ACTIVATE, WA_ACTIVE, 0)
        SendMessage(self.HandleNumber, WM_LBUTTONDOWN, 0, long_position)  # press
        sleep((np.random.randint(5, 10)) / 100)  # keep random time
        SendMessage(self.HandleNumber, WM_LBUTTONUP, 0, long_position)  # release

    def GetRandomHitPosition(self, HitPos, HitRange):
        r = np.random.randint(0,self.GaussDistributionSize);
        RandomPos = np.multiply(self.GaussDistribution[r], HitRange) + HitPos
        return RandomPos


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