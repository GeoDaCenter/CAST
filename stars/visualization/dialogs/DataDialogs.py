"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['VariableSelDialog']

import os
import wx

            
class VariableSelDialog(wx.Dialog):
    def __init__(self, parent, varibles, 
                 bDisable2nd=False, 
                 title="Variable Settings",
                 title1="Select Variables",
                 title2="1st Variable (X):",
                 title3="2nd Variable (X):"):
        size = (600, 400)
        if os.name == 'posix':
            size = (600,400)
        wx.Dialog.__init__(self, parent, -1, title,
                           size = size,
                           pos = wx.DefaultPosition,
                           style = wx.DEFAULT_DIALOG_STYLE)
        
        panel = wx.Panel(self,-1, size=(600,380))
        x1,y1 = 10,10
        wx.StaticBox(panel, -1, title1, pos=(10,10),size=(580,320))
        wx.StaticText(panel, -1, title2, pos =(x1+90,y1+30),size=(135,-1))
        wx.StaticText(panel, -1, title3, pos =(x1+380,y1+30),size=(135,-1))
        
        self.lb1 = wx.ListBox(panel, -1, (x1+20, y1+60), (220, 210), varibles, wx.LB_SINGLE)
        self.lb2 = wx.ListBox(panel, -1, (x1+320, y1+60), (220, 210), varibles, wx.LB_SINGLE)
        
        self.btn_ok = wx.Button(panel, wx.ID_OK, "OK",pos=(x1+179,y1+330),size=(90, 30))
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, "Close",pos=(x1+330,y1+330),size=(90, 30))
        
        if bDisable2nd:
            self.lb2.Enable(False)