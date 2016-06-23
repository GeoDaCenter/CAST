"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['MovieWidget']

import wx
import wx.animate
from stars.visualization.AbstractWidget import AbstractWidget

class MovieWidget(AbstractWidget):
    """
    Widget for displaying animate movie (Dynamic Maps)
    """
    def __init__(self, parent, movie_path, **kwargs):
        title = "Movie" 
        if kwargs.has_key('title'):
            title = kwargs['title']
        if kwargs.has_key('size'):
            size = kwargs['size']
        AbstractWidget.__init__(self, parent, title, pos=(60, 60), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
     
        self.status_bar = self.CreateStatusBar()
        
        ani = wx.animate.Animation(movie_path)
        ani_ctrl = wx.animate.AnimationCtrl(self, -1, ani)
        ani_ctrl.SetUseWindowBackgroundColour()
        ani_ctrl.Play()
        self.canvas = ani_ctrl
        w,h = ani_ctrl.GetBestSize()
        self.SetSize((w,h+40))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ani_ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)