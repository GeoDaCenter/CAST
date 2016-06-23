"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['DynamicShapeMap', 'DynamicTrendGraph', 'DynamicTrendMapQueryDialog']

import math,datetime,os
import wx
import numpy as np
import pysal

import stars
from TrendGraph import TrendGraph, TrendGraphQueryDialog
from stars.visualization.DynamicControl import DynamicMapControl
from stars.visualization.maps.ClassifyMap import ClassifyMap
from stars.visualization.maps.ShapeMap import ColorSchema,ShapeMap
from stars.visualization.utils import GetDateTimeIntervals
from stars.visualization.utils.PaintCollection import DrawLines 

                              
class DynamicShapeMap(ClassifyMap):
    """
    Only used for DynamicTrendGraph
    """
    def __init__(self, parent, layers, cs_data, trend_graph, **kwargs):
        try:
            self.parent = parent
            self.layer = layers[0]
            self.cs_data_dict = cs_data 
            self.trend_graph = trend_graph
           
            self.map_type = kwargs["map_type"]
            self.map_type_name = kwargs["map_type_name"]
            self.start_date,self.end_date = kwargs["start"],kwargs["end"]
            self.step, self.step_by = kwargs["step"] ,kwargs["step_by"]
            
            self.data_sel_keys = sorted(self.cs_data_dict.keys())
            self.data_sel_values = []
            
            for i in self.data_sel_keys:
                vals = self.cs_data_dict[i]
                self.data_sel_values.append(vals)
               
            self.n = len(self.layer)
            self.t = len(self.data_sel_values[0]) 
            data = np.array([self.data_sel_values[i][0] for i in range(len(self.cs_data_dict))])
            
            ClassifyMap.__init__(
                self,parent, 
                layers, 
                map_type=self.map_type,
                data=data,
                field_name='Count(points in polygon)',
                title='')
            
            self.datetime_intervals, self.interval_labels = \
                GetDateTimeIntervals(self.start_date, self.end_date,
                                     self.t, self.step, self.step_by)
            
            title = 'Dynamic Trend Graph-%s[%s] %s %s-%s' %\
                  (
                   self.layer.name,
                   self.map_type_name,
                   kwargs["title"],
                   self.interval_labels[0][0],
                   self.interval_labels[0][1])
    
            self.SetTitle(title)
            
            self.setupDynamicControls()
           
            self.trend_graph.setIntervalLabels(self.interval_labels)
            self.trend_graph.setColorSchema(
                self.id_group,
                self.label_group,
                self.color_group)
            
            self.dynamic_control = DynamicMapControl(
                self.parentFrame, self.t, self.updateDraw) 
            
            wx.FutureCall(100,self.trend_graph.updateDraw, 0)
            
        except Exception as err:
            self.ShowMsgBox("""Dynamic trend graph could not be created. Please check the spatial extent of point and polygon shapefiles.
            
Details: """ + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            if os.name == 'nt':
                self.Destroy()
            return None

    def setupDynamicControls(self):
        """
        assign labels of dynamic controls
        """
        try:
            self.parentWidget = self.parent.GetParent().GetParent()
            self.slider = self.parentWidget.animate_slider
            if isinstance(self.start_date, datetime.date):
                self.parentWidget.label_start.SetLabel(
                    '%2d/%2d/%4d'% (self.start_date.day,self.start_date.month,self.start_date.year)
                )
                self.parentWidget.label_end.SetLabel(
                    '%2d/%2d/%4d'% (self.end_date.day,self.end_date.month,self.end_date.year)
                )
            else:
                self.parentWidget.label_start.SetLabel('%d'% self.start_date)
                self.parentWidget.label_end.SetLabel('%4d'% self.end_date)
            self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (1,self.step, self.step_by))
        except:
            raise Exception("Setup dynamic controls in toolbar failed!")
            
            
    def updateDraw(self, tick):
        # get data at tick
        data = np.array([self.data_sel_values[i][tick] for i in range(len(self.cs_data_dict))])
        
        # in some cases, user changed the color schema, and they want all maps applied 
        # copy existed colors and edge color in color schema
        color_schema = self.color_schema_dict[self.layer.name]
        existed_colors  = [clr for clr in color_schema.colors]
        existed_edgecolor = color_schema.edge_color
        
        # get map classification 
        self.updateMap('', self.map_type, '', data, self.layer)
        
        #  apply ever changed color schema
        self.color_schema_dict[self.layer.name].colrs = existed_colors
        self.color_schema_dict[self.layer.name].edge_color = existed_edgecolor
        self.draw_layers[self.layer].set_fill_color_group(existed_colors)       
        self.draw_layers[self.layer].set_edge_color(existed_edgecolor)       
        
        # trigger to draw 
        self.reInitBuffer = True
        # update label
        self.parentWidget.label_current.SetLabel(
            'current: %d (%d-%s period)' % \
            (tick+1,self.step, self.step_by))
        # update title 
        title = 'Dynamic Trend Graph-%s(%s) %s-%s' %\
              (self.map_type_name,
               self.layer.name,
               self.interval_labels[tick][0],
               self.interval_labels[tick][1]
               )
        self.SetTitle(title)
        
        # update tree node
        self.parentWidget.layer_list_panel.updateLayer(self.layer)
        
        # trigger trend graph
        self.trend_graph.updateDraw(tick)
        
        
    def ExportMovie(self,path,duration=3):
        self.ShowMsgBox("Exporting dynamic trend graph is not yet supported. Please try to export trend graph.")
                
class DynamicTrendGraph(TrendGraph):
    def __init__(self,parent, layer, trend_data_dict,  **kwargs):
        TrendGraph.__init__(self,parent,layer, trend_data_dict,**kwargs)
       
        try:
            self.margin_right = 70
            self.margin_bottom = 120
            self.enable_axis = False
            self.enable_axis_x = False
            self.enable_axis_y = False
           
            self.interval_labels = None
            self.id_group = None
            self.label_group = None
            self.color_group = None
            
            # convert trend_data_dict {poly_id:seq_data} to {time_step:poly_data}
            n_obj = len(trend_data_dict)
            steps = len(trend_data_dict.values()[0])
            new_trend_data_dict = dict([(i,np.zeros(n_obj)) for i in range(steps)]) 
            poly_ids = sorted(trend_data_dict.keys()) # 0,1,2,3,4...
            for poly_id in poly_ids:
                seq_data = trend_data_dict[poly_id]
                for step,item in enumerate(seq_data):
                    new_trend_data_dict[step][poly_id] = item
            trend_data_dict = new_trend_data_dict
            
            # animate control the trend graph, trend graph will send update info
            self.cs_idx = None 
            self.data_sel_keys = sorted(trend_data_dict.keys())
            self.data_sel_values = [trend_data_dict[i] for i in self.data_sel_keys]
            
        except Exception as err:
            self.ShowMsgBox("""Dynamic trend graph could not be created. Please check the spatial extent of selected point and polygon shapefiles.

Details: """ + str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
      
    def setIntervalLabels(self, labels):
        self.interval_labels = labels
        
    def setColorSchema(self, ids,labels,colors):
        self.id_group = ids
        self.label_group = labels
        self.color_group = colors
        
    def updateDraw(self, tick):
        if tick != self.cs_idx:
            self.cs_idx = tick
            
        self.draw_time_band()
        
    def draw_time_band(self):
        if self.cs_idx == None or self.view == None:
            return 
        
        dc = wx.ClientDC(self)
        # draw a rectangular selection band
        start_x = self.cs_idx + 1 
        start_y = self.y_max #+ (self.y_max - self.y_min) * 0.2
        start_x,start_y= self.transform_coord_pt(start_x,start_y)
        start_y = self.ax_start_y
        w = 10
        h = self.ax_height
        start_x = start_x - w/2
      
        dc.DrawBitmap(self.buffer, 0,0)
        """
        if len(self.selected_path_ids) > 0:
            self.draw_selected(dc)
        """
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(255,255,0,50)))
        dc.DrawRectangle(start_x,start_y,w,h)
        #dc.Destroy()
        
    def plot_data(self,dc):
        y_ticks = self.yAxisScale.GetNiceTicks()
        # draw verticle time lines at background
        dc.SetFont(wx.Font(10,wx.ROMAN,wx.NORMAL,wx.NORMAL))
        for i in range(self.x_min, self.x_max+1):
            vtl_start_x, vtl_start_y = self.transform_coord_pt(i, y_ticks[0])
            vtl_end_x, vtl_end_y     = self.transform_coord_pt(i, y_ticks[-1])
            dc.DrawLine(vtl_start_x, vtl_start_y, vtl_end_x, self.margin_top)
            lbl = '%s-%s' % (self.interval_labels[i-1][0], self.interval_labels[i-1][1])
            lbl_w,lbl_h = dc.GetTextExtent(lbl)
            #dc.DrawText(lbl, vtl_end_x - lbl_w/2.0, vtl_start_y+8)
            dc.DrawRotatedText(lbl, vtl_start_x - lbl_w/1.414, vtl_start_y+lbl_w/1.414+4,45)
            
            
        x_label = "Time Interval"
        x_lbl_w, x_lbl_h = dc.GetTextExtent(x_label)
        center_x = max(self.margin_left + self.ax_width/2.0 - x_lbl_w/2.0, self.margin_left)
        dc.DrawText(x_label, center_x, self.bufferHeight - x_lbl_h - 8)
        
        # plots data
        n_group = len(self.id_group)
        for i in range(n_group):
            ids = self.id_group[i]
            color = self.color_group[i]

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

        DrawLines(dc,paths, 
                  data_group=self.id_group, 
                  fill_color_group=self.color_group,
                  edge_thickness=2,
                  opaque=255)
        
        #self.draw_selected(dc)
        wx.FutureCall(50,self.draw_time_band)
        
    def draw_selected(self,dc):
        super(DynamicTrendGraph, self).draw_selected(dc)
        
        wx.FutureCall(50,self.draw_time_band)
        
    def OnNoPathSelect(self, event):
        super(DynamicTrendGraph, self).OnNoPathSelect(event)
        wx.FutureCall(50,self.draw_time_band)
        

class DynamicTrendMapQueryDialog(TrendGraphQueryDialog):
    def OnQuery(self,event):
        from stars.visualization.DynamicWidget import DynamicPlotMapWidget
        
        if self._check_space_input() == False or\
           self._check_time_itv_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self.query_date = None # query_date is not available in Trend Graph case
        self._filter_by_date_interval()
        self._filter_by_tod()
        self.query_data = self.gen_date_by_step()
        
        if self.query_data== None:
            self.ShowMsgBox("Query dynamic data by step error.")
            return
        
        background_shp, trend_data_dict  = self.query_data
       
        # let user choose which classify map will be used
        dlg = wx.SingleChoiceDialog(
            self, 'Choice a map type for trend graph/map', 'Map Type',
            ['Quantile Map', 'Percentile Map', 'Box Map', 'Std dev Map', 
             'Natural Breaks Map', 'Maximum Breaks Map', 
             'Equal Interval Map'], 
            wx.CHOICEDLG_STYLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            title =  dlg.GetStringSelection()
            map_type = stars.MAP_CLASSIFY_QUANTILES
            
            if title == 'Quantile Map':
                map_type = stars.MAP_CLASSIFY_QUANTILES
            elif title == 'Percentile Map':
                map_type = stars.MAP_CLASSIFY_PERCENTILES
            elif title == 'Box Map':
                map_type = stars.MAP_CLASSIFY_BOX_PLOT
            elif title == 'Std dev Map':
                map_type = stars.MAP_CLASSIFY_STD_MEAN
            elif title == 'Natural Breaks Map':
                map_type = stars.MAP_CLASSIFY_NATURAL_BREAK
            elif title == 'Maximum Breaks Map':
                map_type = stars.MAP_CLASSIFY_MAXIMUM_BREAK
            elif title == 'Equal Interval Map':
                map_type = stars.MAP_CLASSIFY_EQUAL_INTERVAL
            elif title == 'Jenks Caspall Map':
                map_type = stars.MAP_CLASSIFY_JENKS_CASPALL
                
            queryfield = "" if self.query_field_idx < 0 else self.query_field
            queryrange = "" if self.query_range == None else ""
            
            title = ""
            if self.query_field.lower() != "all fields":
                title = "(%s:%s)"%(self.query_field,self.query_range)
                
            # invoke widget to display data
            dynamic_trendgraph_widget= DynamicPlotMapWidget(
                self.parent,
                [background_shp],
                trend_data_dict, # cross-sectional data
                DynamicShapeMap,
                DynamicTrendGraph,
                queryfield=queryfield,
                queryrange=queryrange,
                size =(600,620),
                start=self.start_date,
                end=self.end_date,
                step_by=self.step_by,
                step=self.step,
                map_type_name=title,
                map_type=map_type
            )
            dynamic_trendgraph_widget.Show()
        dlg.Destroy()
        
        self.bg_layer = background_shp
        self.btn_save.Enable(True)
            
    def OnSaveQueryToDBF(self, event):
        try:
            if self.query_data == None:
                return
            dlg = wx.FileDialog(
                self, message="Save dynamic trend graph query into new dbf files...", defaultDir=os.getcwd(), 
                defaultFile='%s.dbf' % (self.bg_layer.name + '_dynamic_trandgraph'), 
                wildcard="shape file (*.dbf)|*.dbf|All files (*.*)|*.*", 
                style=wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            path = dlg.GetPath()
            dlg.Destroy()
            
            trend_data_dict  = self.query_data[1]
            dbf = self.bg_layer.dbf
            newDBF= pysal.open('%s.dbf'%path[:-4],'w')
            newDBF.header = []
            newDBF.field_spec = []
            n_intervals = len(trend_data_dict.values()[0])
            for i in dbf.header:
                newDBF.header.append(i)
            for i in dbf.field_spec:
                newDBF.field_spec.append(i)
            for i in range(n_intervals):
                newDBF.header.append('T_%d'%(i+1))
                newDBF.field_spec.append(('N',4,0))
            for i in range(dbf.n_records): 
                newRow = []
                row = dbf.read_record(i)
                newRow = [item for item in row]
                for j in range(n_intervals):
                    val = trend_data_dict[i][j]
                    newRow.append(int(val))
                newDBF.write(newRow)
            newDBF.close()
            self.ShowMsgBox("Query results have been saved to new dbf file",
                            mtype='CAST Information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Save query results to new dbf file failed. Please check if the dbf file already exists.")
