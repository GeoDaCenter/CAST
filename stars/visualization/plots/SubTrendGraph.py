"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['SubTrendGraph']

import os
import wx
import numpy as np
from scipy.spatial import cKDTree
import pysal

import stars
from stars.visualization.maps.BaseMap import PolygonLayer
from stars.visualization.EventHandler import AbstractData
from stars.visualization.PlotWidget import PlotWidget,PlottingCanvas
from stars.visualization.utils import PaintCollection, View2ScreenTransform, GetRandomColor
from stars.visualization.utils.PaintCollection import DrawLines 

class SubTrendGraph(PlottingCanvas):
    """
    """
    def __init__(self,parent, layer, data, **kwargs):
        PlottingCanvas.__init__(self,parent,data)
   
        try:
            self.layer        = layer
            self.layer_name   = layer.name
            self.data         = data[0]
            self.highlight_ids= data[1]
            self.labels       = data[2]
            self.tick         = data[3]
            self.time_gstar_p = data[4]
            self.time_gstar_z = data[5]
            self.time_neighbors = data[6]
            self.n              = len(self.data)
            
            self.selected_path_ids = []
            
            self.margin_right  = 10
            self.margin_top    = 22
            self.margin_bottom = 80# if os.name == 'posix' else 35
            self.margin_left   = 35 if os.name == 'posix' else 60
            self.enable_axis   = False
            self.enable_axis_x = False
            self.enable_axis_y = False
           
            
            #self.title   = "Trend graph for Gi* Space Time: %s[%s]" % (self.layer_name,len(self.time_neighbors))
            self.title = "Select observations to view trend graph"
            self.x_label = "Time intervals"
            self.y_label = "# of observations"
            
            self.font_size_title    = 8
            if os.name == "posix":
                self.font_size_title= 10
            self.font_size_x_axis   = 8
            self.font_size_y_axis   = 8
            self.font_size_xy_label = 8
            if os.name == "posix":
                self.font_size_xy_label = 10
                
            
            all_values = self.data.values()
            
            self.x_min = 1
            self.x_max = len(all_values[0]) 
            self.x_max = self.x_max if self.x_max > self.x_min else self.x_max*1.5
            
            all_values = np.array(all_values)
            self.y_min = np.min(all_values)
            self.y_min = self.y_min if self.y_min > 0 else 0
            self.y_max = np.max(all_values)
            
            self.local_paths = []
            
            self.extent = (self.x_min, self.y_min, self.x_max,self.y_max)
            
        except Exception as err:
            self.ShowMsgBox('Sub trend graph could not be created. ' + str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
        
        # linking-brushing events
        self.Register(stars.EVT_OBJS_SELECT, self.OnPathsSelected)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoPathSelect)
        
    def OnClose(self, event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnPathsSelected)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoPathSelect)
        event.Skip()
        
    def DoDraw(self,dc):
        super(SubTrendGraph, self).DoDraw(dc)
        
        # draw y axis at each time interval
        dc.SetFont(wx.Font(self.font_size_y_axis,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        dc.SetPen(wx.Pen(wx.Color(200,200,200)))
        for i in range(self.x_min, self.x_max+1):
            if i == self.x_min or i == self.x_max:
                self.enable_axis_labels = True
            else:
                self.enable_axis_labels = False
            self.draw_axis_y(dc, start_x=i, isRotate=False, lblFormat='%d')
            
    def test_line_at_rect_liang(self, line_seg, rect):
        t_min = 0
        t_max = 1
      
        x1,y1 = line_seg[0]
        x2,y2 = line_seg[1]
       
        left,upper = rect[0]
        right,bottom = rect[1]
       
        if max(x1,x2) < left or min(x1,x2) > right or max(y1,y2) < bottom or min(y1,y2) > upper:
            return False
        
        dx = float(x2-x1)
        dy = float(y2-y1)
        
        P1 = -dx
        q1 = x1 - left
        r1 = q1 / P1
        
        P2 = dx
        q2 = right - x1
        r2 = q2/P2
        
        P3 = -dy
        q3 = y1- bottom
        r3 = q3/P3
        
        P4 = dy
        q4 = upper - y1
        r4 = q4/P4
       
        P_set = (P1, P2, P3, P4)
        r_set = (r1, r2, r3, r4)
       
        t1_set = [0]
        t2_set = [1]
        
        for i in range(4):
            if P_set[i] < 0:
                t1_set.append(r_set[i])
            if P_set[i] > 0:
                t2_set.append(r_set[i])
                
        t1 = max(t1_set)
        t2 = min(t2_set)
        
        return t1 < t2
    
    def plot_data(self,dc):
        
        y_ticks = self.yAxisScale.GetNiceTicks()
        # draw verticle time lines at background
        dc.SetFont(wx.Font(self.font_size_y_axis,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        if os.name == 'posix':
            dc.SetFont(wx.Font(self.font_size_y_axis+2,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        for i in range(self.x_min, self.x_max+1):
            if i == self.x_min or i == self.x_max:
                dc.SetPen(wx.BLACK_PEN)
            else:
                dc.SetPen(wx.Pen(wx.Color(200,200,200)))
            vtl_start_x, vtl_start_y = self.transform_coord_pt(i, y_ticks[0])
            vtl_end_x, vtl_end_y     = self.transform_coord_pt(i, y_ticks[-1])
            dc.DrawLine(vtl_start_x, vtl_start_y, vtl_end_x, self.margin_top)
            lbl = 't'+str(i)
            lbl_w,lbl_h = dc.GetTextExtent(lbl)
            dc.DrawText(lbl, vtl_end_x - lbl_w/2.0, vtl_start_y+8)

        # draw legend
        dc.SetFont(wx.Font(stars.LISA_SPACE_LEGEND_FONT_SIZE,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        if os.name == 'posix':
            dc.SetFont(wx.Font(stars.LISA_SPACE_LEGEND_FONT_SIZE+2,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        dc.SetPen(wx.BLACK_PEN)
        y = self.bufferHeight - 18
        x = 6
        colors = [wx.Color(180,180,180),stars.LISA_HH_COLOR,stars.LISA_LL_COLOR]
        labels = ["Not significant","High-High","Low-Low"]
        for i in range(len(colors)):
            clr = colors[i]
            lbl = labels[i]
            dc.SetBrush(wx.Brush(clr))
            dc.DrawRectangle(x,y, 12,12)
            x += 12 + 1
            dc.DrawText(lbl, x, y)
            lbl_w,lbl_h = dc.GetTextExtent(lbl)
            x += lbl_w + 2    
        
        # plots data
        paths = []
        self.local_paths = []
        self.seg_dict = {}
        
        for key in self.data.keys():
            item = self.data[key]
            path = []
            local_path = []
            for i in range(len(item)-1):
                x0, x1 = i +1, i+2
                y0, y1 = item[i], item[i+1]
                seg = ((x0,y0),(x1,y1))
                
                if seg in self.seg_dict:
                    path.append(self.seg_dict[seg])
                else:
                    x0,y0 = seg[0]
                    x1,y1 = seg[1]
                    x0,y0 = self.transform_coord_pt(x0,y0)
                    x1,y1 = self.transform_coord_pt(x1,y1)
                    path.append((x0,y0,x1,y1))
                    self.seg_dict[seg] = (x0,y0,x1,y1)
                local_path.append(seg)
            paths.append(path)
            self.local_paths.append([local_path,min(item),max(item)]) 
            
        DrawLines(dc, paths,edge_thickness=1,edge_color=wx.Color(240,240,240))
                
        # draw initial highlights
        if len(self.highlight_ids) > 0:
            self.selected_path_ids = self.highlight_ids
            self.draw_selected(dc)
        
    def draw_selected(self,dc):
        dc = wx.GCDC(dc)
        if len(self.selected_path_ids) > 0:
            paths = []
            for id in self.selected_path_ids:
                item = self.data[id]
                path = []
                for i in range(len(item)-1):
                    x0, x1 = i +1, i+2
                    y0, y1 = item[i], item[i+1]
                    seg = ((x0,y0),(x1,y1))
                    path.append(self.seg_dict[seg])
                paths.append(path)
            DrawLines(dc,paths, edge_color=wx.Color(200,200,200),edge_thickness=2)       
                
            key = id
                
            for key in self.data.keys():
                item = self.data[key]
                t    = len(item)
                if key in self.selected_path_ids:
                    for i in range(t):
                        if self.time_gstar_p[key][i] > 0.05:
                            continue
                        
                        try:
                            neighbors = self.time_neighbors[str(i)]
                        except:
                            neighbors = self.time_neighbors[i]
                            
                        if len(neighbors) == 0:
                            continue
                        
                        if self.time_gstar_z[key][i] >= 0:
                            color = wx.RED
                        else:
                            color = wx.BLUE
                          
                        path = []
                        for n_id in neighbors:
                            j = int(n_id)
                            if j > i:
                                x0, x1 = j, j+1
                            else:
                                x0, x1 = j+1, j+2
                            y0, y1 = item[x0-1], item[x1-1]
                            seg = ((x0,y0),(x1,y1))
                            path.append(self.seg_dict[seg])
                            
                        DrawLines(dc, [path], edge_color=color, edge_thickness=2)
                                   
    def screen_to_plot(self,x,y):
        x,y = self.view.pan_to(x,y,-self.margin_left,-self.margin_top)
        w_x,w_y = self.view.pixel_to_view(x,y)
        return w_x,w_y
        
    def draw_selected_by_region(self, dc,select_region, isScreenCoordinates=True):
        """
        this function highlight the lines selected 
        by mouse drawing a region
        """
        self.selected_path_ids = []
        x0,y0,x1,y1= select_region
        x0,y0 = self.screen_to_plot(x0,y0)
        x1,y1 = self.screen_to_plot(x1,y1)
        
        if x0==x1 and y0==y1:
            # test point and path
            pass
        else:
            # test rectangular and path
            query_min_y = min(y0,y1)
            query_max_y = max(y0,y1)
            query_rect = [(x0,y0),(x1,y1)]
           
            for i, local_path in enumerate(self.local_paths):
                # try simple test first
                segs, p_ymin,p_ymax = local_path
                if (p_ymax < query_min_y or p_ymin > query_max_y):
                    continue

                #for seg,s_xmin,s_xmax,s_ymin,s_ymax in segs:
                for seg in segs:
                    if self.test_line_at_rect_liang(seg, query_rect):
                        self.selected_path_ids.append(i)
                        break
                    
        self.draw_selected(dc)
        
        if len(self.selected_path_ids)>0:
            # draw selected
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.shape_ids[self.layer_name] = self.selected_path_ids
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # unselect all
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            self.UpdateEvt(stars.EVT_OBJS_UNSELECT,data)
        
    def OnPathsSelected(self,event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        event is an instance of EventHandler.Event class
        event.object are the data for selecting shape objects
        """
        if not event: 
            return
        
        data = event.data
        if len(data.shape_ids) > 0 and self.layer_name in data.shape_ids:
            # directly select by shape_ids
            if data.shape_ids.has_key(self.layer_name):
                tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
                tmp_dc = wx.BufferedDC(None, tmp_buffer)
                background_buffer = self.drawing_backup_buffer if self.drawing_backup_buffer else self.buffer
                tmp_dc.DrawBitmap(background_buffer,0,0) # draw map as background first
                
                self.selected_path_ids = data.shape_ids[self.layer_name]
                self.draw_selected(tmp_dc)
                # exchange buffer
                self.buffer = tmp_buffer
                self.Refresh(False)

                
    def OnNoPathSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        Normally, event could be None, you just need to clean and refresh
        you selected/highlighted
        """
        self.selected_path_ids = []
        self.buffer = self.drawing_backup_buffer
        self.Refresh(False)        