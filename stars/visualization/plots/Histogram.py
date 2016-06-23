"""
"""
__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['Histogram']

import math
import wx
import numpy as np
from scipy.stats import histogram

import stars
from stars.visualization import AbstractData, PlottingCanvas
from stars.visualization.utils import GradientColor

class Histogram(PlottingCanvas):
    def __init__(self, parent, layer, data, **kwargs):
        PlottingCanvas.__init__(self,parent, data)
        
        try:
            if isinstance(layer,str) or isinstance(layer, unicode):
                # in case of weights histogram
                self.layer_name = layer
            else:
                self.layer_name = layer.name
            self.isAutoScale = False 
            self.intervals = 7
            #self.title = "Histogram (%s)" % (self.layer_name)
            self.title = ""
            self.x_label = data.keys()[0]
            self.y_label = "Counts in bins"
            self.data = data[self.x_label]
            
            self.enable_axis_x = False
            self.draw_full_axis = False
            self.margin_right = 250 # for legend
            
            # create a dict for input data for Brushing
            self.data_dict = sorted(self.data, key=self.data.get) #[obj_id]
            sorted_data = sorted(self.data.values()) #[value]
            
            if self.x_label == 'Connectivity': 
                self.intervals = len(set(sorted_data))
                self.intervals = sorted_data[-1] - sorted_data[0] + 1
                if self.intervals > 50:
                    self.enable_axis_x = True
                    self.margin_right = 40
                
            if self.intervals > 1:
                self.hist, low_range, binsize, extrapoints = histogram(sorted_data, self.intervals)
            else:
                self.hist = np.array([len(sorted_data)])
           
            cnt = 0; bin_idx = 0
            self.bin_index = {} # key: obj_id, value: bin_idx
            for n in self.hist:
                for i in range(int(n)):
                    obj_id = self.data_dict[cnt]
                    self.bin_index[obj_id] = bin_idx
                    cnt += 1
                bin_idx += 1
            
            data_min, data_max = sorted_data[0], sorted_data[-1]
            
            if self.x_label == 'Connectivity': 
                #unique_num_neighbors = list(set(sorted_data))
                self.data_intervals = []
                for n in range(sorted_data[0], sorted_data[-1]+1):
                    self.data_intervals.append((n,n))
            else:
                end_pos = np.cumsum(self.hist)
                start_pos = end_pos - self.hist + 1
                self.data_intervals = [ (start_pos[i],end_pos[i]) for i in range(len(self.hist))]
        
            # a NxN matrix
            self.x_min = 1
            self.x_max = self.intervals +1
            self.y_min = 0
            self.y_max = np.max(self.hist) +1
    
            self.extent = (self.x_min, self.y_min, self.x_max,self.y_max)
            self.status_bar = None#self.parentFrame.status_bar
            
            self.gradient_color = GradientColor(gradient_type='rdyibu')
            
            # color schema: from blue to red
            self.color_matrix = []
            for i in range(self.intervals):
                p = float(i+1) / self.intervals
                self.color_matrix.append( self.gradient_color.get_color_at(p))
       
            self.selected_obj_ids = []
            
        except Exception as err:
            self.ShowMsgBox(""" Histogram could not be created. Please select a numeric variable.
            
Details: """ + str(err.message))
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
        if not event: return
        
        data = event.data
        if len(data.shape_ids) > 0:
            # directly select by shape_ids
            if data.shape_ids.has_key(self.layer_name):
                self.selected_obj_ids = data.shape_ids[self.layer_name]
                self.draw_selected()
    
    def OnNoObjSelect(self, event):
        self.selected_obj_ids = []
        self.Refresh(False)
        
    def draw_selected(self,dc=None):
        if len(self.selected_obj_ids) > 0:
            if dc == None:
                # draw selected on client DC
                dc = wx.ClientDC(self)
                dc.DrawBitmap(self.buffer,0,0)
           
            highlight_counts_in_bins = [0] * len(self.hist)
            for obj_id in self.selected_obj_ids:
                bin_idx = self.bin_index[obj_id]
                highlight_counts_in_bins[bin_idx] += 1
                
            # draw highlighted
            w=1
            brush = wx.Brush(wx.Colour(255,255,0), wx.CROSSDIAG_HATCH)
            for i,count in enumerate(highlight_counts_in_bins):
                start_x = i+1
                start_y = count
                h = count
                pixel_x,pixel_y = self.point_to_screen(start_x,start_y)
                pixel_w,pixel_h = math.ceil(self.length_to_screen(w)),math.ceil(self.length_to_screen(h,axis=1))
                
                dc.SetBrush(brush)
                dc.DrawRectangle(pixel_x,pixel_y,pixel_w,pixel_h)
                
    def draw_selected_by_region(self, dc,select_region, isScreenCoordinates=True):
        """
        this function highlight the points selected 
        by mouse drawing a region
        """
        self.selected_obj_ids= []
        x0,y0,x1,y1= select_region
        ymin = min(y0,y1)
        ymax = max(y0,y1)
        y0 = ymin
        y1 = ymax
        
        x0,y0 = self.view.pan_to(x0,y0,-self.margin_left,-self.margin_top)
        x1,y1 = self.view.pan_to(x1,y1,-self.margin_left,-self.margin_top)
        x0,y0 = self.view.pixel_to_view(x0,y0)
        x1,y1 = self.view.pixel_to_view(x1,y1)
        
        # test intersection
        x0,y0,x1,y1 = int(math.floor(x0)),int(math.floor(min(y1,y0))),int(math.ceil(x1)),int(math.ceil(max(y0,y1)))
        if y0<0: y0=0
        if x0<1: x0=1
       
        n = len(self.hist)
        for x in range(x0,x1):
            if x <= n:
                start_pos = int(sum(self.hist[:x-1]))
                if y0 < self.hist[x-1]:
                    m = y1 if y1 < self.hist[x-1] else self.hist[x-1]
                    m = int(m)
                    for i in range(y0,m):
                        idx = self.data_dict[start_pos+i]
                        self.selected_obj_ids.append(idx)
        self.draw_selected(dc)
        
        if len(self.selected_obj_ids)>0:
            # draw selected
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.shape_ids[self.layer_name] = self.selected_obj_ids
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # unselect all
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            self.UpdateEvt(stars.EVT_OBJS_UNSELECT,data)
        
    def set_intervals(self):
        pass
    
    def plot_data(self,dc):
        w = 1
       
        o_x, o_y = self.point_to_screen(1,0)
        
        for i in range(self.intervals):
            binNum = self.hist[i]
            start_x = i+1
            start_y = binNum
            pixel_x,pixel_y = self.point_to_screen(start_x,start_y)
            pixel_nx,pixel_ny = self.point_to_screen(start_x+1,start_y)
            pixel_w = int(pixel_nx) - int(pixel_x) + 1
            pixel_h = int(o_y) -  int(pixel_y) + 1
           
            """
            h = binNum 
            pixel_w,pixel_h = self.length_to_screen(w),self.length_to_screen(h,axis=1)
            
            pixel_w = round(int(pixel_w) + pixel_w - int(pixel_w) + pixel_x - int(pixel_x))
            pixel_h = round(int(pixel_h) + pixel_h - int(pixel_h) + pixel_y - int(pixel_y))
            """
            brush = wx.Brush(self.color_matrix[i])
            dc.SetBrush(brush)
            dc.DrawRectangle(pixel_x,pixel_y,pixel_w,pixel_h)
            
        if self.x_label == "Connectivity" and self.intervals > 50:
            return
        
        # draw a legend bar
        pixel_x,pixel_y = self.point_to_screen( start_x+w, self.y_max)
        pixel_x = self.ax_start_x + self.ax_width + 10
        pixel_y = self.ax_start_y
        pixel_h = self.length_to_screen(self.y_max-self.y_min,axis=1)
        pixel_w = 30
       
        num_items = self.intervals 
        if num_items == 1: num_items += 1
        legend_item_h = pixel_h * 0.7 / num_items 
        
        dc.SetBrush(wx.Brush(wx.Colour(255,255,0),wx.CROSSDIAG_HATCH))
        dc.DrawRectangle( pixel_x, pixel_y, pixel_w, legend_item_h)
        dc.DrawText( "selected features", pixel_x + pixel_w + 5, pixel_y) 
        for i in range(self.intervals):
            pixel_y += legend_item_h + 5
            dc.SetBrush( wx.Brush(self.color_matrix[i]))
            dc.DrawRectangle( pixel_x, pixel_y, pixel_w, legend_item_h)
            label = '%s - %s (%d)' % (self.data_intervals[i][0], self.data_intervals[i][1], self.hist[i])
            dc.DrawText( label, pixel_x + pixel_w + 5, pixel_y) 
