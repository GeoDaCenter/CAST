"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['PlottingCanvas','PlotWidget']

import wx
import numpy as np
import stars
from stars.visualization.AbstractCanvas import AbstractCanvas 
from stars.visualization.AbstractWidget import AbstractWidget
from stars.visualization.utils import *

class PlotWidget(AbstractWidget):
    """
    Widget for simple data plotting, the layout should be like this:
    -------------------------
    | toolbar                |
    --------------------------
    |                        |
    |                        |
    |       Plot             |
    |                        |
    |                        |
    --------------------------
    
    It provides base operating functions for 
    all inherited plotting widgets:
       Zoom()
       Pan()
       ColorPanel()
       SaveFigure()
    """
    def __init__(self, parent, layer, data, canvas, **kwargs):
        if isinstance(layer, str) or isinstance(layer, unicode):
            layer_name = layer
        else:    
            layer_name = layer.name
        title = "Plot " + layer_name
        size  = (600,600)
        pos   = (60,60)
        
        if kwargs.has_key('title'):
            title = kwargs['title']
        if kwargs.has_key('size'):
            size = kwargs['size']
        if kwargs.has_key('pos'):
            pos = kwargs['pos']
        
        AbstractWidget.__init__(self, parent, title, pos=(60, 60), size=size)
     
        self.status_bar = self.CreateStatusBar()
        
        # toolbar
        self.toolbar = wx.ToolBar(self)
        #self.toolbar.SetSize((36,36))
        #self.toolbar.Realize()
        
        # plotting canvas
        self.canvas = None
        self.canvas = canvas(self,layer,data,**kwargs)
        if self.canvas:
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.toolbar,0,wx.EXPAND)
            sizer.Add(self.canvas, 1, wx.EXPAND)
            self.SetSizer(sizer)
            self.SetAutoLayout(True)
        
class PlottingCanvas(AbstractCanvas):
    """
    Base plotting canvas (wxWindow) for plotting data. 
    It provides base plotting functions for 
    all inherited plotting canvas:
        grid()
        axis()
        color()
    """
    def __init__(self,parent,data,**kwargs):
        AbstractCanvas.__init__(self,parent,**kwargs)
      
        self.data = None
        self.isAutoScale = True
        self.enable_axis = True
        self.draw_full_axis = True
        self.enable_axis_x = True
        self.enable_axis_y = True
        self.enable_axis_labels = True
        self.enable_grid = True
        self.enable_xy_labels = True
        self.title = "Title"
        self.x_label = "x_label"
        self.y_label = "y_label"
        self.x_slim = []
        self.y_slim = []
        self.x_slim_labels = []
        self.y_slim_labels = []
        self.margin_top,self.margin_left,self.margin_right,self.margin_bottom = 40,50,40,50
        
        self.font_size_title    = stars.PLOT_TITLE_FONT_SIZE
        self.font_size_x_axis   = stars.PLOT_X_AXIS_FONT_SIZE
        self.font_size_y_axis   = stars.PLOT_Y_AXIS_FONT_SIZE
        self.font_size_xy_label = stars.PLOT_XY_LABEL_FONT_SIZE
        
        if kwargs.has_key("title"):
            self.title = kwargs["title"]
            
        self.isValidPlot = True
            
    def draw_axis_x(self,dc,offset_y=0, lblFormat='%d'):
        scale_drawlist_x = []
        total_lbl_width = 0
        x_ticks = self.xAxisScale.GetNiceTicks()

        for tick in x_ticks:
            if tick != int(tick):
                lblFormat = '%.1f'
        
        n_ticks = len(x_ticks)
        y0 = self.yAxisScale.niceMin
        for i,x_tick in enumerate(x_ticks):
            x0, y0 = self.point_to_screen(x_tick, y0)
            y0 = offset_y 
            if i == n_ticks-1:
                x0 = self.ax_start_x + self.ax_width-1
            scale_drawlist_x.append((x0,y0,x0,y0 + self.tick_length))
          
            if self.enable_axis_labels:
                lbl = lblFormat % x_tick
                lbl_w, lbl_h = dc.GetTextExtent(lbl)
                dc.DrawText(lbl, x0 - lbl_w/2.0, y0 + self.tick_length+2)
        dc.DrawLineList(scale_drawlist_x)       
            
    def draw_axis_y(self,dc,start_x=None,isRotate=True, lblFormat='%d'):
        scale_drawlist_y = []
        total_lbl_height = 0
        y_ticks = self.yAxisScale.GetNiceTicks()
        
        for tick in y_ticks:
            if tick != int(tick):
                lblFormat = '%.1f'
                
        for y_tick in y_ticks:
            if y_tick == int(y_tick):
                lbl = str(int(y_tick))
            else:
                lbl = lblFormat % y_tick
            lbl_w, lbl_h = dc.GetTextExtent(lbl)
            total_lbl_height += lbl_w
           
        n_ticks = len(y_ticks)
        for i,y_tick in enumerate(y_ticks):
            x0 = self.xAxisScale.niceMin if not start_x else start_x
            x0, y0= self.point_to_screen(x0,y_tick)
            if i == n_ticks-1:
                y0 = self.ax_start_y
            scale_drawlist_y.append((x0- self.tick_length,y0,x0,y0))

            if self.enable_axis_labels:
                if y_tick == int(y_tick):
                    lbl = str(int(y_tick))
                else:
                    lbl = lblFormat % y_tick
                lbl_w, lbl_h = dc.GetTextExtent(lbl)
                if isRotate:
                    dc.DrawRotatedText(lbl, x0-lbl_h-self.tick_length-2, y0 + lbl_w/2.0, 90)
                else:
                    dc.DrawText(lbl, x0 - self.tick_length- lbl_w, y0 - lbl_h/2.0)
        dc.DrawLineList(scale_drawlist_y) 
        
    def DoDraw(self,dc):
        if not self.isValidPlot:
            return
        
        if self.bufferHeight==0 or self.bufferWidth == 0 or self.data == None: 
            dc.Clear()
            return  
        
        # darw axis
        ax_start_x,ax_start_y = self.margin_left, self.margin_top
        ax_width = max(self.bufferWidth - self.margin_left-self.margin_right,1)
        ax_height = max(self.bufferHeight - self.margin_top-self.margin_bottom,1)
        tick_length = self.bufferHeight / 80

        self.ax_start_x = ax_start_x
        self.ax_start_y = ax_start_y
        self.ax_width = ax_width
        self.ax_height = ax_height
        self.tick_length = tick_length
        
        self.xAxisScale = LinearScale(self.x_min,self.x_max)
        self.yAxisScale = LinearScale(self.y_min,self.y_max)
        self.extent = (self.xAxisScale.niceMin, self.yAxisScale.niceMin, 
                       self.xAxisScale.niceMax, self.yAxisScale.niceMax)
        
        self.view = View2ScreenTransform(self.extent,ax_width,ax_height,fixed_ratio=False)
        self.view.set_scaleX(1.0)
        self.view.set_scaleY(1.0)
       
        # plot data
        self.plot_data(dc)
        
        # draw axis box
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetTextForeground(wx.BLACK)
        pen = wx.BLACK_PEN
        dc.SetPen(pen)
        
        if self.enable_axis:
            if self.draw_full_axis:
                dc.DrawRectangle(ax_start_x,ax_start_y,ax_width,ax_height+1)
            else:
                # draw half axis box
                dc.DrawLine(ax_start_x, ax_start_y, ax_start_x, ax_start_y + ax_height)
                dc.DrawLine(ax_start_x, ax_start_y + ax_height , ax_start_x+ax_width, ax_start_y + ax_height)
        
        # draw scales along x_axis
        dc.SetFont(wx.Font(self.font_size_x_axis,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        if self.enable_axis_x:
            self.draw_axis_x(dc,offset_y=ax_start_y + ax_height)
            
        # draw scales along y_axis
        if self.enable_axis_y:
            self.draw_axis_y(dc)
            
        # draw X,Y labels
        dc.SetFont(wx.Font(self.font_size_xy_label, wx.NORMAL, wx.NORMAL,wx.NORMAL))
        if self.enable_xy_labels:
            x_lbl_w, x_lbl_h = dc.GetTextExtent(self.x_label)
            y_lbl_w, y_lbl_h = dc.GetTextExtent(self.y_label)
            center_x = max(self.margin_left + ax_width/2.0 - x_lbl_w/2.0, self.margin_left)
            dc.DrawText(self.x_label, center_x, self.margin_top + ax_height+ x_lbl_h + 8)
            center_y = max(self.margin_top + ax_height/2.0 + y_lbl_w/2.0, self.margin_top)
            #dc.DrawRotatedText(self.y_label, margin_left - 40, center_y, 90)
            dc.DrawRotatedText(self.y_label, 5, center_y, 90)
                    
        # draw title
        dc.SetFont(wx.Font(self.font_size_title, wx.NORMAL, wx.NORMAL,wx.NORMAL))
        title_lbl_w, title_lbl_h = dc.GetTextExtent(self.title)
        title_x = max(self.margin_left + ax_width/2.0- title_lbl_w/2.0, self.margin_left*1.5)
        title_y = self.margin_top / 5.0
        dc.DrawText(self.title,title_x,title_y)
        
       
        
    def transform_coord_pt(self,x,y):
        x,y = self.view.view_to_pixel(x,y)
        x,y = self.view.pan_to(x,y, self.margin_left,self.margin_top)
        return x,y
        
    def point_to_screen(self,x,y):
        x,y = self.view.view_to_pixel(x,y)
        x,y = self.view.pan_to(x,y, self.margin_left,self.margin_top)
        return x,y
    
    def length_to_screen(self,length,axis=0):
        """
        axis: 0 x, 1 y
        """
        if axis == 0:
            return self.view.ratioX* length / self.view.scaleX
        return self.view.ratioY*length / self.view.scaleY
        
    def plot_data(self,dc):
        """
        plot data onto canvas, should be implemented in each inherited class
        for different purposes, such as:
            scatter plot (as demo here)
            Morean scatter plot
            Lasso graph
            Trend graph
        """
        pass
    
        
        