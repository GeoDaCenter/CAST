"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['SigTrendGraphLocalG', 'SigTrendGraphLocalGQueryDialog','ShowSigTrendGraphLocalG']

import os
import wx
import numpy as np
from scipy.spatial import cKDTree
import pysal

import stars
from stars.visualization.maps.DynamicLisaMap import DynamicLISAQueryDialog
from stars.visualization.maps.BaseMap import PolygonLayer
from stars.visualization.EventHandler import AbstractData
from stars.visualization.PlotWidget import PlotWidget,PlottingCanvas
from stars.visualization.utils import PaintCollection, View2ScreenTransform, GetRandomColor, FilterShapeList,GetDateTimeIntervals
from stars.visualization.utils.PaintCollection import DrawLines 
from stars.visualization.SpaceTimeQueryDialog import SpaceTimeQueryDialog

class SigTrendGraphLocalG(PlottingCanvas):
    """
    """
    def __init__(self,parent, layer, data, **kwargs):
        PlottingCanvas.__init__(self,parent,data)
   
        try:
            self.layer        = layer
            self.layer_name   = layer.name
            
            #self.weight_file  = kwargs["weight"]
            self.cs_data_dict = kwargs["query_data"]
            self.step, self.step_by        = kwargs["step"] ,kwargs["step_by"]
            self.start_date, self.end_date = kwargs["start"],kwargs["end"]
            self.parent = parent
            self.data_sel_keys   = sorted(self.cs_data_dict.keys())
            self.data_sel_values = [self.cs_data_dict[i] for i in self.data_sel_keys]
            #self.weight          = pysal.open(self.weight_file).read()
            self.t = len(self.cs_data_dict) # number of data slices
            self.n = len(self.data_sel_values[0]) # number of shape objects
            
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            
            # promote for time weights
            from stars.visualization.dialogs import TimeWeightsDlg
            tw_dlg  = TimeWeightsDlg(self.main, self.t, self.layer.name)
            tw_path = tw_dlg.Show()
            if tw_path == False:
                raise Exception("no time weights")
            
            tweights = pysal.open(tw_path).read()
           
            # G settings
            from stars.visualization.dialogs import choose_local_g_settings
            b_gstar, b_binary = choose_local_g_settings(self)
            map_type = 'Gi*' if b_gstar else 'Gi'
            add_type = 'binary' if b_binary else 'row-standardized'
            self.title = 'Local G (%s,%s) Trend Graph -%s %s' % (map_type,add_type,layer.name,kwargs["title"])
            self.parentFrame.SetTitle(self.title)
            
            # calculate Gi using time weights
            time_gstar   = dict()
            time_gstar_z = dict()
            tseries_data = []
            for pid in range(self.n):
                tseries = []
                for tid in range(self.t):
                    tseries.append(self.cs_data_dict[tid][pid])
                tseries_data.append(tseries)
            for pid in range(self.n):
                tseries = tseries_data[pid]
                y  = np.array(tseries)
                #lg = pysal.esda.getisord.G_Local(y,tweights,transform='B',star=True)
                if b_binary == False:
                    lg = pysal.esda.getisord.G_Local(y,tweights,star=b_gstar)
                else:
                    lg = pysal.esda.getisord.G_Local(y,tweights,star=b_gstar,transform='B')
                time_gstar[pid]   = lg.p_sim            
                time_gstar_z[pid] = lg.Zs
            
            trendgraph_data = dict()
            for i in range(self.n):
                data = []
                for j in range(self.t):
                    data.append(self.cs_data_dict[j][i])
                trendgraph_data[i] = data
            self.trendgraph_data = trendgraph_data 
            
            self.tweights     = tweights
            self.time_gstar   = time_gstar 
            self.time_gstar_z = time_gstar_z 
            self.t_neighbors  = tweights.neighbors
            
            data              = [self.trendgraph_data, [], self.interval_labels, 0, self.time_gstar,self.time_gstar_z, self.t_neighbors]
            self.data         = data[0]
            self.highlight_ids= data[1]
            self.labels       = data[2]
            self.tick         = data[3]
            self.time_gstar_p = data[4]
            self.time_gstar_z = data[5]
            self.time_neighbors = data[6]
            self.n              = len(self.data)
            
            self.selected_path_ids = []
            self.line_marker = []
            self.selected_line = None
            
            self.margin_right  = 50
            self.margin_bottom = 140
            self.margin_left   = 100
            self.enable_axis   = False
            self.enable_axis_x = False
            self.enable_axis_y = False
           
            
            self.x_label = ""
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
            self.ShowMsgBox('Local G Trend Graph could not be created. ' + str(err.message))
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
        super(SigTrendGraphLocalG, self).DoDraw(dc)
        
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
            
        self.line_marker = []
        self.verticle_lines = []
        for i in range(self.x_min, self.x_max+1):
            if i == self.x_min or i == self.x_max:
                dc.SetPen(wx.BLACK_PEN)
            else:
                dc.SetPen(wx.Pen(wx.Color(200,200,200)))
            vtl_start_x, vtl_start_y = self.transform_coord_pt(i, y_ticks[0])
            vtl_end_x, vtl_end_y     = self.transform_coord_pt(i, y_ticks[-1])
            dc.DrawLine(vtl_start_x, vtl_start_y, vtl_end_x, self.margin_top)

            # draw triangle line marker
            self.verticle_lines.append((vtl_start_x, vtl_start_y, vtl_end_x, self.margin_top))
            x,y = vtl_end_x, vtl_end_y - 3
            mark_w = 5
            x1,y1 = vtl_end_x - mark_w, y
            x2,y2 = vtl_end_x + mark_w, y
            x3,y3 = vtl_end_x + mark_w, y - mark_w*2
            x4,y4 = vtl_end_x - mark_w, y - mark_w*2
            self.line_marker.append([(x1,y1), (x3,y3)])
         
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.RED_BRUSH)
            dc.DrawPolygon([(x,y),(x3,y3),(x4,y4),(x,y)])
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(wx.BLACK_PEN)
            
            
            lbl = "%s-%s"%(self.interval_labels[i-1][0],self.interval_labels[i-1][1])
            lbl_w,lbl_h = dc.GetTextExtent(lbl)
            #dc.DrawText(lbl, vtl_end_x - lbl_w/2.0, vtl_start_y+8)
            dc.DrawRotatedText(lbl, vtl_start_x - lbl_w/1.414, vtl_start_y+lbl_w/1.414+4,45)

        x_label = "Time Interval"
        x_lbl_w, x_lbl_h = dc.GetTextExtent(x_label)
        center_x = max(self.margin_left + self.ax_width/2.0 - x_lbl_w/2.0, self.margin_left)
        dc.DrawText(x_label, center_x, self.bufferHeight - x_lbl_h - 30)
        
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
        
        x += 2
        dc.SetBrush(wx.RED_BRUSH)
        dc.DrawPolygon([(x,y),(x+12,y),(x+6,y+12),(x,y)])
        x += 14
        dc.DrawText("Click to show Core+Neighbors",x,y)
            
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
                                   
            # draw with line mark
            if self.selected_line != None:
                vline = self.verticle_lines[self.selected_line]
                try:
                    neighbors = self.time_neighbors[str(self.selected_line)]
                except:
                    neighbors = self.time_neighbors[self.selected_line]
                    
                left_neigh = None
                right_neigh = None
                for n_id in neighbors:
                    j = int(n_id)
                    if left_neigh == None or j < left_neigh:
                        left_neigh = j
                    if right_neigh == None or j> right_neigh:
                        right_neigh = j
                if right_neigh < self.selected_line:
                    right_neigh = self.selected_line
                if left_neigh > self.selected_line:
                    left_neigh = self.selected_line

                left_x = self.verticle_lines[left_neigh][0]
                right_x = self.verticle_lines[right_neigh][0]
                height = self.verticle_lines[left_neigh][1] - self.verticle_lines[left_neigh][3]
                
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetBrush(wx.Brush(wx.Color(245,245,245)))
                dc.DrawRectangle(left_x-10, vline[3], right_x-left_x+20, height)
                dc.SetPen(wx.BLACK_PEN)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawRectangle(left_x, vline[3], right_x-left_x, height)
                dc.SetBrush(wx.BLACK_BRUSH)
               
                dc.SetPen(wx.Pen(wx.Color(250,250,250)))
                for j in range(left_neigh+1, right_neigh):
                    ln = self.verticle_lines[j]
                    dc.DrawLine(ln[0],ln[1],ln[2],ln[3])
                dc.SetBrush(wx.BLACK_BRUSH)
                
                dc.SetPen(wx.Pen(wx.Color(255,255,0),5))
                dc.DrawLine(vline[0],vline[1],vline[2],vline[3])
                dc.SetPen(wx.BLACK_PEN)
               
                for key in self.data.keys():
                    item        = self.data[key]
                    t           = len(item)
                    dc.SetPen(wx.BLACK_PEN)
                    if key not in self.selected_path_ids:
                        continue
                    for i in range(t):
                        if i != self.selected_line:
                            continue
                        try:
                            neighbors = self.time_neighbors[str(i)]
                        except:
                            neighbors = self.time_neighbors[i]
                            
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
        x0,y0,x1,y1= select_region
        x0,y0 = self.screen_to_plot(x0,y0)
        x1,y1 = self.screen_to_plot(x1,y1)
        
        if x0==x1 and y0==y1:
            # test point and path
            for i,rect in enumerate(self.line_marker):
                (left,low),(right,upper) = rect
                left, low = self.screen_to_plot(left,low)
                right, upper = self.screen_to_plot(right,upper)
                w = right - left
                h = upper - low
                if left -w <= x0 <= right + w and low-h <=y0<= upper+h:
                    self.selected_line = i
                    self.draw_selected(dc)
                    return
            else:
                self.selected_path_ids = []
                self.selected_line = None
        else:
            self.selected_path_ids = []
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
        
class SigTrendGraphLocalGQueryDialog(DynamicLISAQueryDialog):
    """
    Query Dialog for generating Markov LISA Maps
    """
    def Add_Customized_Controls(self):
        pass
    """
        x2,y2 = 20, 350
        wx.StaticBox(
            self.panel, -1, "Local G* setting:",pos=(x2,y2),size=(325,70))
        wx.StaticText(self.panel, -1, "Weights file:",pos =(x2+10,y2+30),size=(90,-1))
        self.txt_weight_path = wx.TextCtrl(
            self.panel, -1, "",pos=(x2+100,y2+30), size=(180,-1) )
        #open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        open_bmp = wx.BitmapFromImage(stars.OPEN_ICON_IMG)
        
        self.btn_weight_path = wx.BitmapButton(
            self.panel,-1, open_bmp, pos=(x2+292,y2+32), style=wx.NO_BORDER)
        
        self.Bind(wx.EVT_BUTTON, self.BrowseWeightFile, self.btn_weight_path)
    """    
    def OnQuery(self,event):
        if self._check_time_itv_input() == False or\
           self._check_space_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self.query_date = None 
        self._filter_by_date_interval()
        self._filter_by_tod()
        
        self.query_data = self.gen_date_by_step()
        if self.query_data == None or len(self.query_data) <= 1:
            self.ShowMsgBox("Local G Trend Graph requires at least 2 time intervals, please reselect step-by parameters.")
            return
        
        title = ""
        if self.query_field.lower() != "all fields":
            title = "(%s:%s)"%(self.query_field,self.query_range)
            
        # LISA layer (only one)
        lisa_layer = self.background_shps[self.background_shp_idx]
        gi_widget = PlotWidget(
            self.parent,
            lisa_layer,
            None,
            SigTrendGraphLocalG,
            query_data=self.query_data,
            size=(800,650),
            start= self._wxdate2pydate(self.itv_start_date.GetValue()),
            end= self._wxdate2pydate(self.itv_end_date.GetValue()),
            step_by=self.step_by,
            step=self.step,
            title=title
            )
        gi_widget.Show()
       
        # (enable) save LISA Markov to new shp/dbf files
        #self.btn_save.Enable(True)
        #self.lisa_layer = lisa_layer[0]
        #self.lisa_markov_map = gi_widget.map_canvas
        
        
    def OnSaveQueryToDBF(self, event):
        """
        Save Markov type in each interval for each record to dbf file.
        """
        if self.query_data == None:
            return
        
        dlg = wx.FileDialog(
            self, 
            message="Save Markov LISA type to new dbf file...", 
            defaultDir=os.getcwd(), 
            defaultFile='%s.shp' % (self.lisa_layer.name + '_markov_lisa'), 
            wildcard="shape file (*.shp)|*.shp|All files (*.*)|*.*", 
            style=wx.SAVE
            )
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        path = dlg.GetPath()
        dbf = self.lisa_layer.dbf
        try:
            n_intervals = self.lisa_markov_map.t -1
            n_objects = len(dbf)
            lisa_markov_mt = self.lisa_markov_map.lisa_markov_mt
            
            newDBF= pysal.open('%s.dbf'%path[:-4],'w')
            newDBF.header = []
            newDBF.field_spec = []
            for i in dbf.header:
                newDBF.header.append(i)
            for i in dbf.field_spec:
                newDBF.field_spec.append(i)
                
            for i in range(n_intervals):
                newDBF.header.append('MARKOV_ITV%d'%(i+1))
                newDBF.field_spec.append(('N',4,0))
               
            for i in range(n_objects): 
                newRow = []
                newRow = [item for item in dbf[i][0]]
                for j in range(n_intervals):
                    move_type = lisa_markov_mt[i][j]
                    newRow.append(move_type)
                    
                newDBF.write(newRow)
            newDBF.close()
            
            self.ShowMsgBox("Query results have been saved to new dbf file.",
                            mtype='CAST Information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Saving query results to dbf file failed! Please check if the dbf file already exists.")
 
            
def ShowSigTrendGraphLocalG(self):
    # self is Main.py
    if not self.shapefiles or len(self.shapefiles) < 1:
        return
    shp_list = [shp.name for shp in self.shapefiles]
    dlg = wx.SingleChoiceDialog(
        self, 
        'Select a POINT or Polygon(with time field) shape file:', 
        'Local G Trend Graph', 
        shp_list,
        wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.GetSelection()
        shp = self.shapefiles[idx]
        background_shapes = FilterShapeList(self.shapefiles, stars.SHP_POLYGON)
        if shp.shape_type == stars.SHP_POINT:
            # create Markov LISA from points
            gi_dlg = SigTrendGraphLocalGQueryDialog(
                self,"Local G Trend Graph:" + shp.name,
                shp, 
                background_shps=background_shapes,
                size=stars.DIALOG_SIZE_QUERY_MARKOV_LISA
                )
            gi_dlg.Show()
        elif shp.shape_type == stars.SHP_POLYGON:
            # bring up a dialog and let user select 
            # the time field in POLYGON shape file
            dbf_field_list = shp.dbf.header 
            timedlg = wx.MultiChoiceDialog(
                self, 'Select TIME fields to generate Local G Trend Graph:', 
                'DBF fields view', 
                dbf_field_list
                )
            if timedlg.ShowModal() == wx.ID_OK:
                selections = timedlg.GetSelections()
                # compose lisa_data_dict
                dbf = shp.dbf
                lisa_data_dict = {}
                count = 0
                for idx in selections:
                    lisa_data_dict[count] = np.array(dbf.by_col(dbf.header[idx]))
                    count += 1 
                gi_spacetime_widget= PlotWidget(
                    self, 
                    shp, 
                    None,
                    SigTrendGraphLocalG,
                    #weight = weight_path,
                    query_data = lisa_data_dict,
                    size =stars.MAP_SIZE_MARKOV_LISA,
                    start=1,
                    end=count-1,
                    step_by='',
                    step=1
                    )
                gi_spacetime_widget.Show()
            timedlg.Destroy()
        else:
            self.ShowMsgBox("File type error. Should be a POINT or POLYGON shapefile.")
            dlg.Destroy()
            return
    dlg.Destroy() 
