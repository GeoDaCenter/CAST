"""
Abstract class for al wxWidgets. 
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['AbstractWidget']

import wx

import stars

class AbstractWidget(wx.Frame):
    """
    Abstract class for all wxWidgets
        DataWidget, MapWidget, 
        PlotWidget, DynamicWidget
    """
    def __init__(self, parent, title, **kwargs):
        wx.Frame.__init__(self, parent, -1, title, **kwargs)
        
        while parent != None:
            if isinstance(parent, stars.Main):
                self.stars = parent
                break
            parent = parent.GetParent()
            
        self.SetIcon(self.stars.logo)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def ShowMsgBox(self,msg):
        dlg = wx.MessageDialog(self, msg, 'Warning', wx.OK|wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnClose(self, event):
        """
        When close this frame, the wx.windows for either map or plot 
        should be unregistered from the observation first, (call its
        close() function. Then destroy this frame
        """
        if self.canvas:
            self.canvas.Close(True)
        self.Destroy()
        event.Skip()