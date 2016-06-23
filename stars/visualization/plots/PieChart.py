"""
"""
__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['PieChart']

import math
import wx
from wx.lib.agw.piectrl import PieCtrl, PiePart
import numpy as np

from stars.visualization.AbstractCanvas import AbstractCanvas
from stars.visualization.utils import GetRandomColor

class PieChart(AbstractCanvas):
    """
    data: dict (key=lable, value=value)
    """
    def __init__(self, parent, layer, data):
        AbstractCanvas.__init__(self,parent)
        
        self.setupPieChart()
        
        for lbl,val in data.iteritems():
            self.addPie(lbl,val)
        
    def DoDraw(self,dc):
        self.SetBackgroundColour(wx.WHITE)
        pos = self.bufferWidth*0.1, self.bufferHeight*0.1
        self._pie.SetPosition(pos)
        self._pie.SetSize((self.bufferWidth*0.8,self.bufferHeight*0.8))
        
    def setupPieChart(self): 
        pos = self.bufferWidth*0.1, self.bufferHeight*0.1
        self._pie = PieCtrl(self, -1, pos, wx.Size(self.bufferWidth*0.8,self.bufferHeight*0.8))
        self._pie.SetBackgroundColour(wx.WHITE)
        self._pie.GetLegend().SetTransparent(True)
        self._pie.GetLegend().SetHorizontalBorder(10)
        self._pie.GetLegend().SetWindowStyle(wx.STATIC_BORDER)
        self._pie.GetLegend().SetLabelFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False, "Courier New"))
        self._pie.GetLegend().SetLabelColour(wx.Colour(0, 0, 127))	
        self._pie.SetShowEdges(False)
        self._pie.SetAngle(float(68/180.0*math.pi) )
        self._pie.SetHeight(30)
        
    def addPie(self, label, value):
        clr = GetRandomColor()
        part = PiePart()
        part.SetLabel('%s=%f'% (label,value))
        part.SetValue(value)
        part.SetColour(clr)
        self._pie._series.append(part)
        
