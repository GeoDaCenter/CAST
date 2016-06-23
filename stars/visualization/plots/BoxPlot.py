"""
"""
__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['BoxPlot']

import math
import wx
import pysal
import numpy as np
from scipy.stats import scoreatpercentile

import stars
from stars.visualization import AbstractData
from stars.visualization.AbstractCanvas import AbstractCanvas
from stars.visualization.utils import LinearScale

class BoxPlot(AbstractCanvas):
    def __init__(self, parent, layer, data,**kwargs):
        AbstractCanvas.__init__(self,parent)
     
        try:
            self.view = None#"DUMMY"
            self.status_bar = None
            self.layer_name = layer.name
            
            self.var_name = data.keys()[0]
            self.data = data[self.var_name]
            
            # create a dict for input data for Brushing
            self.data_dict = dict([(item,i) for i,item in enumerate(self.data)])
            self.selected_pts = []
          
            self.hinge = 1.5
            
            # sort the data
            sorted_data = np.sort(self.data)
            
            # find the median
            self.median = np.median(sorted_data)
            
            # find the upper and lower quantiles:
            # the median of the numbers larger/smaller than the median
            boxplot = pysal.Box_Plot(np.array(self.data))
            bp_bins = boxplot.bins
            
            self.upper_median = boxplot.bins[3]
            self.lower_median = boxplot.bins[1]
            
            self.boxplot_min = boxplot.bins[0]
            self.boxplot_max = boxplot.bins[4]
            
            if sorted_data[0] < self.boxplot_min:
                self.boxplot_min = sorted_data[0]
            if sorted_data[-1] > self.boxplot_max:
                self.boxplot_max = sorted_data[-1]
           
            self.whisker_top = boxplot.bins[4]
            self.whisker_bottom = boxplot.bins[0]
            self.whisker = self.hinge * boxplot.iqr#(self.lower_median - self.upper_median)
    
            if self.whisker == 0:
                raise Exception("Divided by zero error, please check the input data")
          
            self.data_range = self.boxplot_max - self.boxplot_min
            self.ext_range = self.data_range * 0.1
            self.axis_scale = LinearScale(self.boxplot_min - self.ext_range, self.boxplot_max+self.ext_range)
            
            self.isValidPlot = True
        except Exception as err:
            self.ShowMsgBox("""Box plot could not be created! Please select a valid numeric variable.

Details:""" + str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
        
        # linking-brushing events
        self.Register(stars.EVT_OBJS_SELECT, self.OnObjsSelected)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoObjSelect)

    def OnClose(self,event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnObjsSelected)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoObjSelect)
        event.Skip()
                
    def OnObjsSelected(self, event):
        if not event: 
            return
        
        data = event.data
        if len(data.shape_ids) > 0:
            # directly select by shape_ids
            if data.shape_ids.has_key(self.layer_name):
                self.selected_pts = data.shape_ids[self.layer_name]
                self.draw_selected()
    
    def OnNoObjSelect(self, event):
        self.selected_obj_ids = []
        self.Refresh(False)
        
    def draw_selected(self, dc=None):
        if len(self.selected_pts) > 0:
            if dc == None:
                self.buffer = self.drawing_backup_buffer
                dc = wx.ClientDC(self)
                dc.DrawBitmap(self.drawing_backup_buffer,0,0)
                
            dc = wx.GCDC(dc)
            points = []
            for pt in self.selected_pts:
                item_pixel_x = self.graph_middle
                item_pixel_y = self.graph_top + (self.boxplot_max - self.data[pt]) / self.data_range_per_pixel
                points.append((item_pixel_x,item_pixel_y))
           
            dc.SetPen(wx.Pen(wx.RED,2))
            #dc.SetBrush(wx.RED_BRUSH)
            points = list(set(points))
            for pt in points:
                dc.DrawCircle(pt[0],pt[1],self.size)
                
    def draw_selected_by_regions(self, dc,select_region, isScreenCoordinates=True):
        pass
    
    def draw_selected_by_region(self, dc,select_region, isScreenCoordinates=True):
        """
        this function highlight the points selected 
        by mouse drawing a region
        """
        self.selected_pts = []
        x0,y0,x1,y1= select_region
        y_min = min(y0,y1)
        y_max = max(y0,y1)
        y0 = self.boxplot_max - (y_min - self.graph_top)* self.data_range_per_pixel
        y1 = self.boxplot_max - (y_max - self.graph_top)* self.data_range_per_pixel
        
        if x0 <=  self.graph_middle <= x1: 
            # test each point
            for i,item in enumerate(self.data):
                #y = self.graph_top + (self.boxplot_max - item) / self.data_range_per_pixel
                #if (x0<=x<=x1 or x1<=x<=x0) and (y0<=y<=y1 or y1<=y<=y0):
                y = item
                if y0<=y<=y1 or y1<=y<=y0:
                    self.selected_pts.append(i)
            self.draw_selected(dc)
        
        if len(self.selected_pts)>0:
            # draw selected
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.shape_ids[self.layer_name] = self.selected_pts
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # unselect all
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            self.UpdateEvt(stars.EVT_OBJS_UNSELECT,data)
            
    def DoDraw(self,dc):
        if not self.isValidPlot:
            return
        
        client_w,client_h = self.bufferWidth, self.bufferHeight
        if client_h <=0 or client_w <=0:
            return 
       
        dc.Clear()
        margin_top,margin_bottom = client_h/20 , client_h/10
        
        graph_top = int(round(margin_top))
        graph_middle = client_w / 2
        graph_height = int(round(client_h - margin_top - margin_bottom))
        
        if graph_middle <=0 or graph_top <=0 or graph_height <=0:
            return 
       
        data_range = self.boxplot_max - self.boxplot_min 
        data_range_per_pixel = float(data_range) / graph_height
      
        # box
        box_w = int(round(client_w / 9))
        if box_w < 50:
            box_w = 50
        box_h = int(round((self.upper_median - self.lower_median) / data_range_per_pixel))
        box_start_y = int(round(graph_top + (self.boxplot_max - self.upper_median) / data_range_per_pixel))
        box_start_x = int(round(graph_middle - box_w / 2))
        
        # upper whisker
        upper_hat_w = int(round(client_w / 10))
        upper_hat_start_y = int(round(graph_top + (self.boxplot_max-self.whisker_top) / data_range_per_pixel))
        upper_hat_end_y = box_start_y 
        upper_hat_start_x = int(round(graph_middle - upper_hat_w/2))
        upper_hat_end_x = int(round(graph_middle + upper_hat_w/2))
        
        dc.DrawLine(upper_hat_start_x, upper_hat_start_y, upper_hat_end_x, upper_hat_start_y)
        dc.DrawLine(graph_middle, upper_hat_start_y, graph_middle, upper_hat_end_y)
        
        # lower whisker
        lower_hat_w = int(round(client_w / 10))
        lower_hat_start_y = int(round(box_start_y + box_h))
        lower_hat_end_y = int(round(graph_top + (self.boxplot_max - self.whisker_bottom) / data_range_per_pixel))
        lower_hat_start_x = int(round(graph_middle - lower_hat_w/2))
        lower_hat_end_x = int(round(graph_middle + lower_hat_w/2))
        
        dc.DrawLine(lower_hat_start_x, lower_hat_end_y, lower_hat_end_x, lower_hat_end_y)
        dc.DrawLine(graph_middle, lower_hat_start_y, graph_middle, lower_hat_end_y)
                
        # draw data alone center line 
        size = 4
        dc.SetPen(wx.Pen(wx.BLUE))
        dc.SetBrush(wx.WHITE_BRUSH)
       
        points = []
        for item in self.data:
            item_pixel_x = graph_middle
            item_pixel_y = graph_top + int(round((self.boxplot_max - item) / data_range_per_pixel))
            if box_start_y <= item_pixel_y <= box_start_y+ box_h:
                continue
            points.append((item_pixel_x,item_pixel_y))
           
        min_py = graph_top
        max_py = graph_top
        points = list(set(points))
        for pt in points:
            dc.DrawCircle(pt[0],pt[1],size)
            if 0<pt[1] < min_py:
                min_py = pt[1]
            if max_py < pt[1] < self.bufferHeight:
                max_py = pt[1]
        
        # axis
        dc.SetPen(wx.BLACK_PEN)
        tick_size = 5
        axis_x = 55
        ticks = self.axis_scale.GetNiceTicks()
        tick_x = axis_x - tick_size
        
        axis_start_y = self.bufferHeight
        axis_end_y = 0
        
        for tick in ticks:
            if tick == int(tick):
                tick = int(tick)
            if tick < self.boxplot_max and tick > self.boxplot_min:
                tick_y = graph_top + (self.boxplot_max - tick) / data_range_per_pixel
                dc.DrawLine(tick_x, tick_y, axis_x, tick_y)
                tick_lbl = str(tick)
                lbl_w,lbl_h = dc.GetTextExtent(tick_lbl)
                dc.DrawRotatedText(tick_lbl, axis_x - 5- lbl_h, tick_y + lbl_w/2, 90)
                
                if axis_start_y > tick_y:
                    axis_start_y = tick_y
                if axis_end_y < tick_y:
                    axis_end_y = tick_y
                   
        if axis_start_y > upper_hat_start_y:
            axis_start_y = upper_hat_start_y
        if axis_start_y > min_py:
            axis_start_y = min_py
        if axis_end_y < lower_hat_end_y:
            axis_end_y = lower_hat_end_y
        if axis_end_y < max_py:
            axis_end_y = max_py
            
        dc.DrawLine(axis_x, axis_start_y, axis_x, axis_end_y)
        
        txt_w, txt_h = dc.GetTextExtent(self.var_name)
        dc.DrawRotatedText(self.var_name, txt_h + 2, axis_start_y/2 + axis_end_y/2 + txt_w/2, 90)
        
        # draw variable name
        var_x = graph_middle - txt_w / 2
        var_y = client_h - txt_h - 2
        dc.DrawText(self.var_name, var_x,var_y)
        
        # draw Q1,Q3 box
        dc.SetBrush(wx.Brush(wx.Colour(138,0,0)))
        dc.DrawRectangle(box_start_x, box_start_y, box_w, box_h)
        
        # draw median line
        median_line_w = client_w / 8
        if median_line_w < 60:
            median_line_w = 60
        median_line_y = graph_top + (self.boxplot_max - self.median) / data_range_per_pixel 
        median_line_start_x = graph_middle - int(round(median_line_w/2))
        median_line_end_x = graph_middle + int(round(median_line_w/2))
        
        dc.SetPen(wx.Pen(wx.Colour(238,0,0),4))
        dc.DrawLine(median_line_start_x, median_line_y, median_line_end_x, median_line_y)

        # draw middle point
        mp_x = graph_middle
        mp_y = int(round(upper_hat_start_y + (lower_hat_end_y - upper_hat_start_y ) / 2))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(0,225,0)))
        dc.DrawCircle(mp_x,mp_y,size+2)

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.graph_middle,self.graph_top, self.data_range_per_pixel,self.size = graph_middle,graph_top,data_range_per_pixel,size
        
    def OnRightUp(self, event):
        pass 
 