"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['DynamicMapWidget','DynamicPlotMapWidget']

import os
import wx
from wx import xrc
import numpy as np

import stars
from MapWidget import MapWidget
from AbstractCanvas import AbstractCanvas
from AbstractWidget import AbstractWidget 
from utils import *

class DynamicMapWidget(MapWidget):
    """
    Widget for space time map plotting, the layout should be like this:
    -------------------------
    | toolbar  > || []       |
    --------------------------
    |  l |                   |
    |  a |                   |
    |  y |     map           |
    |  e |                   |
    |  r |                   |
    --------------------------
    A toolbar with "PLAY" "PAUSE" and "STOP" button should be implemented.
    A slider bar to control the dynamic change of data shoule be implemented.
    """
    def __init__(self, parent, layers, canvas,**kwargs):
        MapWidget.__init__(self, parent, layers, canvas, **kwargs)
    
        self.isPlaying = False
        
       
    def OnClose(self, event):
        """
        When close this frame, the wx.windows for either map or plot 
        should be unregistered from the observation first, (call its
        close() function. Then destroy this frame
        """
        if self.canvas:
            self.canvas.dynamic_control.real_stop()
            try:
                self.canvas.dynamic_control.join()
            except:
                pass
            self.canvas.Close(True)
        self.Destroy()
        
    def setup_toolbar(self):
        self.toolbar = self.stars.toolbar_res.LoadToolBar(self,'ToolBar_ANIMATE_MAP')
        self.SetToolBar(self.toolbar)

        self.animate_slider = xrc.XRCCTRL(self.toolbar, 'ID_ANIMATE_SLIDER')

        self.label_start = xrc.XRCCTRL(self.toolbar, 'ID_ANIMATE_START_LABEL')
        self.label_end = xrc.XRCCTRL(self.toolbar, 'ID_ANIMATE_END_LABEL')
        self.label_current = xrc.XRCCTRL(self.toolbar, 'ID_ANIMATE_CURRENT_LABEL')
        
        self.toolbar.EnableTool(xrc.XRCID('ID_PAUSE'),False)
        self.toolbar.EnableTool(xrc.XRCID('ID_STOP'),False)
        # self.canvas is from base class MapWidget:AbstractWidget
        self.Bind(wx.EVT_TOOL, self.OnPlay, id=xrc.XRCID('ID_PLAY'))
        self.Bind(wx.EVT_TOOL, self.OnPause, id=xrc.XRCID('ID_PAUSE'))
        self.Bind(wx.EVT_TOOL, self.OnStop, id=xrc.XRCID('ID_STOP'))
        self.animate_slider.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.OnSliderChange)
        
        # bindings
        self.Bind(wx.EVT_TOOL, self.OnAddLayer, id=xrc.XRCID('ID_ADD_MAP_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnRemoveLayer, id=xrc.XRCID('ID_REMOVE_MAP_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnSelect, id=xrc.XRCID('ID_SELECT_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnPan, id=xrc.XRCID('ID_PAN_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnZoom, id=xrc.XRCID('ID_ZOOM_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnExtent, id=xrc.XRCID('ID_EXTENT_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnRefresh, id=xrc.XRCID('ID_REFRESH_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnBrush, id=xrc.XRCID('ID_BRUSH_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnExport, id=xrc.XRCID('ID_EXPORT_MAP'))
    
    def OnEnd(self):
        self.toolbar.EnableTool(xrc.XRCID("ID_STOP"), False) 
        self.toolbar.EnableTool(xrc.XRCID("ID_PAUSE"), False) 
        self.toolbar.EnableTool(xrc.XRCID("ID_PLAY"), True) 
        
    def OnPlay(self, event):
        """
        When PLAY button is clicked
        """
        # here we assume that all dynamic map canvas
        # has a property called: dynamic_control, which
        # is an instance of DynamicControl class
        if self.isPlaying == False:
            self.canvas.dynamic_control.start()
        else:
            self.canvas.dynamic_control.resume()
        self.isPlaying = True
        self.toolbar.EnableTool(xrc.XRCID('ID_PLAY'),False)
        self.toolbar.EnableTool(xrc.XRCID('ID_PAUSE'),True)
        self.toolbar.EnableTool(xrc.XRCID('ID_STOP'),True)
        
        
    def OnPause(self, event):
        """
        When PAUSE button is clicked
        """
        self.canvas.dynamic_control.pause()
        self.toolbar.EnableTool(xrc.XRCID('ID_PLAY'),True)
        self.toolbar.EnableTool(xrc.XRCID('ID_PAUSE'),False)
        self.toolbar.EnableTool(xrc.XRCID('ID_STOP'),True)
    
    def OnStop(self, event):
        """
        When STOP button is clicked
        """
        self.canvas.dynamic_control.stop()
        self.animate_slider.SetValue(0)
        # draw the first map
        self.canvas.updateDraw(0)
        
        self.toolbar.EnableTool(xrc.XRCID('ID_PLAY'),True)
        self.toolbar.EnableTool(xrc.XRCID('ID_PAUSE'),False)
        self.toolbar.EnableTool(xrc.XRCID('ID_STOP'),False)
   
    def OnSliderChange(self, event):
        """
        When SLIDER is moved
        """
        self.canvas.updateDraw(event.EventObject.GetValue())
        
    def OnExport(self, event):
        """
        Override parent OnExport to support export movie feature
        """
        choices = ['Export current map to an image','Export dynamic maps to a movie'] 
        dlg = wx.SingleChoiceDialog(
                self, 'Select an export method:', 'Export Map', choices, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            if 0==idx:
                super(DynamicMapWidget, self).OnExport(event)
            elif 1==idx:
                movie_dlg = wx.TextEntryDialog(
                    self, 'Setup duration (seconds) between maps in movie:',
                    'Movie Parameter', ''
                )
                movie_dlg.SetValue("3")
                if movie_dlg.ShowModal() == wx.ID_OK:
                    #try:
                    duration = int(movie_dlg.GetValue())
                    save_dlg = wx.FileDialog(
                        self, message="Save movie as a GIF file...", defaultDir=os.getcwd(), 
                        defaultFile='movie.gif', 
                        wildcard="GIF file (*.gif)|*.gif|All files (*.*)|*.*", 
                        style=wx.SAVE
                        )
                    if save_dlg.ShowModal() == wx.ID_OK:
                        path = save_dlg.GetPath()
                        self.canvas.ExportMovie(path,duration)
                    save_dlg.Destroy()
                    #except:
                    #    self.ShowMsgBox('Movie parameter setup error!')
                movie_dlg.Destroy() 
        dlg.Destroy()
    
class DynamicPlotMapWidget(DynamicMapWidget):
    """
    -------------------------
    | toolbar  > || []       |
    --------------------------
    |  l |                   |
    |  a |                   |
    |  y |     map           |
    |  e |                   |
    |  r |-------------------|
    |    |   trend graph     |
    --------------------------
    
    """
    def __init__(self, parent, layers, data, canvas, trend_canvas, **kwargs):
        self.cs_data = data
        self.layer = layers[0]
        self.trend_canvas = trend_canvas 
        
        DynamicMapWidget.__init__(self, parent, layers, canvas, **kwargs)
     
        
    def OnClose(self, event):
        """
        When close this frame, the wx.windows for either map or plot 
        should be unregistered from the observation first, (call its
        close() function. Then destroy this frame
        """
        if self.trend_canvas:
            self.trend_canvas.Close(True)
        if self.canvas:
            self.canvas.dynamic_control.real_stop()
            try:
                self.canvas.dynamic_control.join()
            except:
                pass
            self.canvas.Close(True)
        self.Destroy()
        
    def init_map(self, canvas):
        """
        overwritten for creating a Map&TrendGraph split window
        """
        self.sub_splitter = wx.SplitterWindow(self.splitter, -1,style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE )
        self.trend_canvas = self.trend_canvas(self.sub_splitter, self.layer, self.cs_data, **self.kwargs) 
        if self.trend_canvas == None:
            return False
        self.canvas = canvas(self.sub_splitter, self.layers, self.cs_data, self.trend_canvas, **self.kwargs)
        if self.canvas == None:
            return False
        self.sub_splitter.SplitHorizontally(self.canvas, self.trend_canvas,-260)
        
        self.splitter.SplitVertically(self.layer_list_panel, self.sub_splitter, 160)
        self.layer_list_panel.setup_tree(self.canvas)
        return True
        
    def OnSliderChange(self, event):
        """
        When SLIDER is moved
        """
        self.canvas.updateDraw(event.EventObject.GetValue())
        #self.trend_canvas.updateDraw(event.EventObject.GetValue())