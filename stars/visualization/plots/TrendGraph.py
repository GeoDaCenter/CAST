"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['TrendGraph','TrendGraphQueryDialog']

import os
import wx
import numpy as np
from scipy.spatial import cKDTree
import pysal

import stars
from stars.visualization.maps.BaseMap import PolygonLayer
from stars.visualization.EventHandler import AbstractData
from stars.visualization.PlotWidget import PlotWidget,PlottingCanvas
from stars.visualization.utils import PaintCollection, View2ScreenTransform, GetRandomColor, GetDateTimeIntervals
from stars.visualization.utils.PaintCollection import DrawLines 
from stars.visualization.SpaceTimeQueryDialog import SpaceTimeQueryDialog
from stars.visualization.maps.ClassifyMap import ClassifyMapFactory

class TrendGraph(PlottingCanvas):
    """
    """
    def __init__(self,parent, layer, trend_data, **kwargs):
        PlottingCanvas.__init__(self,parent,trend_data)
        
        try:
            self.start_date,self.end_date = kwargs["start"],kwargs["end"]
            self.step, self.step_by = kwargs["step"] ,kwargs["step_by"]
            
            self.margin_right = 70
            self.margin_left =100 
            self.margin_bottom = 140
            self.enable_axis = False
            self.enable_axis_x = False
            self.enable_axis_y = False
            
            self.layer_name = layer.name 
            self.layer = layer
            self.data = trend_data
            self.n = len(self.data)
            all_values = self.data.values()
            self.t = len(all_values[0])
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            
            self.title = "%s %s" % (self.layer_name,kwargs["title"])
            self.x_label = ""
            self.y_label = "Number of observations"
            
            self.x_min = 1
            self.x_max = len(all_values[0]) 
            self.x_max = self.x_max if self.x_max > self.x_min else self.x_max*1.5
            
            all_values = np.array(all_values)
            self.y_min = np.min(all_values)
            self.y_min = self.y_min if self.y_min > 0 else 0
            self.y_max = np.max(all_values)
            
            self.local_paths = []
            
            self.extent = (self.x_min, self.y_min, self.x_max,self.y_max)
            self.selected_path_ids = []
            self.status_bar = self.parentFrame.status_bar
          
            """
            self.sum_data = np.sum(all_values,axis=1)
            factory = ClassifyMapFactory(self.sum_data, k=5)
            classify_results = factory.createClassifyMap(stars.MAP_CLASSIFY_QUANTILES)
            self.id_group, self.label_group, self.color_group = classify_results
            """
            
        except Exception as err:
            self.ShowMsgBox("Trend graph could not be created. " + str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
        
        # linking-brushing events
        self.Register(stars.EVT_OBJS_SELECT, self.OnPathsSelected)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoPathSelect)

    def OnClose(self,event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnPathsSelected)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoPathSelect)
        event.Skip()
        
    def DoDraw(self,dc):
        super(TrendGraph, self).DoDraw(dc)
        
        # draw y axis at each time interval
        y_axis_font_size = stars.TRENDGRAPH_Y_AXIS_FONT_SIZE
        dc.SetFont(wx.Font(y_axis_font_size,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        for i in range(self.x_min, self.x_max+1):
            if i == self.x_min or i == self.x_max:
                self.enable_axis_labels = True
            else:
                self.enable_axis_labels = False
            self.draw_axis_y(dc, start_x=i, isRotate=False)
            
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
        dc.SetFont(wx.Font(10,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        j = 0
        for i in range(self.x_min, self.x_max+1):
            vtl_start_x, vtl_start_y = self.transform_coord_pt(i, y_ticks[0])
            vtl_end_x, vtl_end_y     = self.transform_coord_pt(i, y_ticks[-1])
            dc.DrawLine(vtl_start_x, vtl_start_y, vtl_end_x, self.margin_top)
            lbl = "%s-%s"%(self.interval_labels[j][0],self.interval_labels[j][1])
            j += 1
            lbl_w,lbl_h = dc.GetTextExtent(lbl)
            #dc.DrawText(lbl, vtl_end_x - lbl_w/2.0, vtl_start_y+8)
            dc.DrawRotatedText(lbl, vtl_start_x - lbl_w/1.414, vtl_start_y+lbl_w/1.414+4,45)
           
        x_label = "Time Interval"
        x_lbl_w, x_lbl_h = dc.GetTextExtent(x_label)
        center_x = max(self.margin_left + self.ax_width/2.0 - x_lbl_w/2.0, self.margin_left)
        dc.DrawText(x_label, center_x, self.bufferHeight - x_lbl_h - 8)
        
        # plots data
        pen = wx.BLACK_PEN
        pen.SetStyle(wx.SOLID)
        dc.SetPen(pen)
       
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
        """ 
        DrawLines(dc,paths,
                  data_group=self.id_group,
                  fill_color_group=self.color_group,
                  edge_thickness=2,
                  opaque=255)
        """
        DrawLines(dc, paths)
           
    def draw_selected(self,dc):
        dc = wx.GCDC(dc)
        if len(self.selected_path_ids) > 0:
            for id in self.selected_path_ids:
                item = self.data[id]
                path = []
                for i in range(len(item)-1):
                    x0, x1 = i +1, i+2
                    y0, y1 = item[i], item[i+1]
                    seg = ((x0,y0),(x1,y1))
                    path.append(self.seg_dict[seg])
                DrawLines(dc,[path], edge_color=wx.RED,edge_thickness=2)       
                
    def display_xy_on_status(self,x,y):
        if self.status_bar and self.view:
            # display current lat/lot on status bar
            x,y = self.view.pan_to(x,y,-self.margin_left,-self.margin_top)
            w_y,w_x = self.view.pixel_to_view(x,y)
            self.status_bar.SetStatusText("%.4f,%.4f"%(w_x,w_y))
        
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
        #self.reInitBuffer = True
        
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
        #self.reInitBuffer = True

class TrendGraphQueryDialog(SpaceTimeQueryDialog):
    """
    Space time query dialog for generating data for Trend graph
    """
    def OnQuery(self,event):
        if self._check_space_input() == False or\
           self._check_time_itv_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        # query_date is not available in Trend Graph case
        self.query_date = None         
        self._filter_by_date_interval()
        self._filter_by_tod()
  
        self.query_data = self.gen_date_by_step()
        
        if self.query_data== None:
            self.ShowMsgBox("Querying dynamic data by time step could not be completed. Please respecify input parameters.")
            return
        
        background_shp, trend_data_dict  = self.query_data
       
        queryfield = "" if self.query_field_idx < 0 else self.query_field
        queryrange = "" if self.query_range == None else ""
        
        title = ""
        if self.query_field.lower() != "all fields":
            title = "(%s:%s)"%(self.query_field,self.query_range)
            
        trendgraph_widget= PlotWidget(
            self.parent,
            background_shp,
            trend_data_dict,
            TrendGraph,
            queryfield=queryfield,
            queryrange=queryrange,
            start=self.start_date,
            end=self.end_date,
            step_by=self.step_by,
            step=self.step,
            title=title
            )
        trendgraph_widget.Show()
        
        self.btn_save.Enable(True)
            
    def OnSaveQueryToDBF(self, event):
        try:
            if self.query_data == None:
                return
            dlg = wx.FileDialog(
                self, message="Save query into a dbf file...", defaultDir=os.getcwd(), 
                defaultFile='%s.dbf' % (self.points_data.name + '_trendgraph'), 
                wildcard="dbf file (*.dbf)|*.dbf|All files (*.*)|*.*", 
                style=wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            path = dlg.GetPath()
            dlg.Destroy()
            dbf = self.background_shps[0].dbf
         
            n_new_fields = len(self.query_data[1].values()[0])
            field_names = []
            for item in dbf.header:
                if item.startswith('TIME_PERIOD'):
                    for i in range(n_new_fields):
                        field_name = item +"_"+str(i+1)
                        field_names.append(field_name)
                    break
            if len(field_names) == 0:
                for i in range(n_new_fields):
                    field_name = "TIME_PERIOD" +"_"+ str(i+1)
                    field_names.append(field_name)
           
            try:
                os.remove(path)
            except:
                pass
            
            newDBF= pysal.open(path,'w')
            newDBF.header = []
            newDBF.field_spec = []
            for i in dbf.header:
                newDBF.header.append(i)
            for i in dbf.field_spec:
                newDBF.field_spec.append(i)
               
            for field_name in field_names:
                newDBF.header.append(field_name)
                newDBF.field_spec.append(('N',4,0))
            
            rows = []
            for i in range(dbf.n_records):
                rows.append(dbf.read_record(i))
            for key in self.query_data[1].keys():
                vals = self.query_data[1][key]
                for val in vals:
                    rows[key].append(val)
            for row in rows: 
                newDBF.write(row)
            newDBF.close()
            
            self.ShowMsgBox("Query results have been saved to new dbf file successfully.",
                            mtype='CAST Information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Saving query results to new dbf file failed.")    
        
    def OnReset(self,event):
        self.reset()
        self.cmbox_location.SetSelection(-1)
        
        
