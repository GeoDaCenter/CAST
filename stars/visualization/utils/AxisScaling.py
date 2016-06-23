"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ["LinearScale"]

import math

class LinearScale():
    """
    The observation is that the nicest numbers in decimal
    are 1, 2, and 5, and all power-of-ten multiples of these numbers. 
    We will use only such numbers for the tick spacing, and place 
    tick marks at multiples of the tick spacing.
    """
    def __init__(self, _min, _max,_ticks=10):
        self.minPoint = _min
        self.maxPoint = _max
        
        self.maxTicks = _ticks
        self.calculateScale()
        
    def calculateScale(self):
        """
        Calculate and update values for tick spacing and nice
        minimum and maximum data points on the axis.
        """
        self.valueRange = self.niceNumber(self.maxPoint - self.minPoint, False)
        self.tickSpacing = self.niceNumber(self.valueRange/ (self.maxTicks-1), True)
        self.niceMin = math.floor( self.minPoint / self.tickSpacing) * self.tickSpacing
        self.niceMax = math.ceil( self.maxPoint / self.tickSpacing) * self.tickSpacing
        
        
    def niceNumber(self, rangeVal, roundVal):
        """
        Calculate and update values for tick spacing and nice
        the number if round = true Takes the ceiling if round = false.
        """
        
        exponentOfRange = math.floor( math.log10(rangeVal))
        fraction = rangeVal / math.pow(10, exponentOfRange)
        niceFraction = .0
        
        if roundVal:
            if fraction < 1.5:
                niceFraction = 1
            elif fraction < 3:
                niceFraction = 2
            elif fraction < 7:
                niceFraction = 5
        else:
            if fraction <= 1:
                niceFraction = 1
            elif fraction <=2:
                niceFraction = 2
            elif fraction <=5:
                niceFraction = 5
            else:
                niceFraction = 10
                
        return niceFraction * math.pow(10, exponentOfRange)
    

    def setMinMaxPoints(self, _min, _max):
        self.minPoint = _min
        self.maxPoint = _max
        self.calculateScale()
       
    def setMaxTicks(self, ticks):
        self.maxTicks = ticks
        self.calculateScale()
    
    def GetNiceRange(self):
        return self.niceMax - self.niceMin
    
    def GetNiceTicks(self):
        ticks = []
        maxVal = self.niceMin 
        i = 1
        while maxVal <= self.niceMax:
            ticks.append(maxVal)
            maxVal += self.tickSpacing
        return ticks
        
if __name__ == "__main__":
    numScale = LinearScale(-0.085,0.173)
    print numScale.tickSpacing
    print numScale.niceMin
    print numScale.niceMax
    print numScale.GetNiceTicks()
            