"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["SpaceTimeClusterMap", "SpaceTimeClusterQueryDialog","ShowSpaceTimeClusterMap"]

import os,math, datetime, time
import wx
import numpy as np
from scipy.spatial import cKDTree
import pysal

import stars
from ShapeMap import *
from stars.visualization.DynamicControl import DynamicMapControl
from stars.visualization.DynamicWidget import DynamicMapWidget
from stars.visualization.SpaceTimeQueryDialog import SpaceTimeQueryDialog
from stars.visualization.utils import View2ScreenTransform, GetDateTimeIntervals


class SpaceTimeClusterMap(ShapeMap):
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
       
        try:
            self.parent = parent
            self.layer = layers[0]
            
            self.cs_data_dict = kwargs["data"]
            self.weight_file  = kwargs["weight"]
            start_date,end_date = kwargs["start"],kwargs["end"]
            self.step, self.step_by = kwargs["step"] ,kwargs["step_by"]
            self.start_date, self.end_date= start_date, end_date

            self.n = len(self.layer)
            self.t = len(self.cs_data_dict)
            self.data_sel_keys = sorted(self.cs_data_dict.keys())
            self.data_sel_values = [self.cs_data_dict[i] for i in self.data_sel_keys]
            self.weight = pysal.open(self.weight_file).read()
       

            time_gstar    = dict()
            time_gstar_z  = dict()
            space_gstar   = dict()
            space_gstar_z = dict()
            tneighbors = self.create_time_w(self.t)
            tweights   = pysal.W(tneighbors)
            for tid,obs in self.cs_data_dict.iteritems():
                y = np.array(obs)
                lg = pysal.esda.getisord.G_Local(y,self.weight,star=True)
                space_gstar[tid]   = lg.p_sim
                space_gstar_z[tid] = lg.Zs
            
            tseries_data = []
            for pid in range(self.n):
                tseries = []
                for tid in range(self.t):
                    tseries.append(self.cs_data_dict[tid][pid])
                tseries_data.append(tseries)
                    
            for pid in range(self.n):
                tseries = tseries_data[pid]
                y  = np.array(tseries)
                lg = pysal.esda.getisord.G_Local(y,tweights,star=True)
                time_gstar[pid]   = lg.p_sim            
                time_gstar_z[pid] = lg.Zs
                
            self.tweights     = tweights
            self.time_gstar   = time_gstar
            self.time_gstar_z = time_gstar_z
            self.space_gstar  = space_gstar
            self.space_gstar_z= space_gstar_z
            
            # default color schema for LISA
            self.HH_color = stars.LISA_HH_COLOR
            self.LL_color = stars.LISA_LL_COLOR
            self.NOT_SIG_color = stars.LISA_NOT_SIG_COLOR
            #self.OBSOLETE_color = stars.LISA_OBSOLETE_COLOR
            color_group =[self.NOT_SIG_color,self.HH_color,self.LL_color]
            label_group = ["Not Significant","High-High","Low-Low"]
            self.color_schema_dict[self.layer.name] = ColorSchema(color_group,label_group)
            self.gi_color_group = color_group           


            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.extent = self.layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth * 0.5, 
                self.bufferHeight,
                offset_x = self.bufferWidth * 0.5) 
            
            # setup dynamic control buttons
            self.SetTitle('SpaceTime Cluster Map- %s'% self.layer.name)
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            self.setupDynamicControls()
            
            # preprocess multi LISA maps
            
            # inital drawing lisa map
            
            # Thread-based controller for dynamic LISA
            self.dynamic_control = DynamicMapControl(self.parentFrame,self.t,self.updateDraw) 
        except:
            self.ShowMsgBox("Please respecify valid parameters for Dynamic LISA Map.")
            #self.parentFrame.Close(True)
            wx.FutureCall(10, self.parentFrame.Close,True)
 
    def create_time_w(self, t, n=1, consider_future=False):
        neighbors = {}
        for i in range(t):
            neighbors[i] = []
            for j in range(1,n+1):
                if i - j >= 0:
                    neighbors[i].append(i-j)
                if consider_future and i+j <= t:
                    neighbors[i].append(i+j)
        return neighbors
            
    def setupDynamicControls(self):
        """
        assign labels of dynamic controls
        """
        try:
            self.parentWidget = self.parent.GetParent()
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
            self.ShowMsgBox("Setup dynamic controls in toolbar failed!")
            
        
    def Update(self, tick):
        """
        When SLIDER is dragged
        """
        self.updateDraw(tick) 
        
    def updateDraw(self, tick):
        """
        When SLIDER is dragged
        """
        self.tick = tick
             
        #self.draw_layers[self.layer].set_data_group(id_groups)
        #self.draw_layers[self.layer].set_fill_color_group(self.lisa_color_group)
        #self.draw_layers[self.layer].set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
   
        # trigger to draw 
        self.reInitBuffer = True
        self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (tick+1,self.step, self.step_by))
        
    def OnSize(self,event):
        bufferWidth,bufferHeight = self.GetClientSize()
        if bufferWidth> 0 and bufferHeight > 0:
            self.bufferWidth = bufferWidth
            self.bufferHeight = bufferHeight
            if self.view:
                self.view.setup(self.bufferHeight,self.bufferWidth*0.2)
            self.reInitBuffer = True        
            
    def DoDraw(self, dc):
        #super(SpaceTimeClusterMap, self).DoDraw(dc)
        self.draw3DMaps(dc)
        
    def draw_selected_by_region(self,dc,query_region,isEvtResponse=False, isScreenCoordinates=False):
        pass
        
    def draw3DMaps(self,dc):
        startPos = [0,0]
        
        subBmpHeight = self.bufferHeight / self.t
        subBmpWidth  = self.bufferWidth * 0.5 
        orig_subBmpHeight = subBmpWidth
        
        
        for idx in range(self.t):
            bmp = wx.EmptyBitmapRGBA(subBmpWidth, orig_subBmpHeight)
            self.draw3DMap(bmp,idx,subBmpWidth*0.9, orig_subBmpHeight*0.9)
            dc.DrawBitmap(bmp, startPos[0] + 70, startPos[1])
            startPos[1] += subBmpHeight
            
        axis_pos = (5, self.bufferHeight - 5)
        dc.DrawLine(axis_pos[0],axis_pos[1], axis_pos[0]+80, axis_pos[1])
        dc.DrawLine(axis_pos[0],axis_pos[1], axis_pos[0], axis_pos[1]-80)
        dc.DrawLine(axis_pos[0],axis_pos[1], 
                    axis_pos[0] + math.cos(math.pi/6)*80, 
                    axis_pos[1] - math.sin(math.pi/6)*80)
        
    
    def draw3DMap(self, bmp, idx, bufferWidth, bufferHeight):
        dc = wx.BufferedDC(None, bmp)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0,0,bufferWidth,bufferHeight)
        
        if not "Linux" in stars.APP_PLATFORM:
            # not good drawing effect using GCDC in linux
            dc = wx.GCDC(dc)
        
        view = View2ScreenTransform(
            self.extent, 
            bufferWidth, 
            bufferHeight
        ) 
        view.zoom_extent = self.map_query_region 
        subBmpHeight = self.bufferHeight / self.t
        ratio = bufferHeight / float(subBmpHeight)
        from stars.visualization.maps.BaseMap import PolygonLayer
        draw_layer = PolygonLayer(self, self.layer, build_spatial_index=False)
        
        p_values = self.space_gstar[idx]
        z_values = self.space_gstar_z[idx]
        
        not_sig = list(np.where(p_values>0.05)[0])
        sig     = set(np.where(p_values<=0.05)[0])
        hotspots = list(sig.intersection(set(np.where(z_values>=0)[0])) )
        coldspots = list(sig.intersection(set(np.where(z_values<0)[0])) )
        id_groups = [not_sig,hotspots,coldspots]
            
        self.id_groups = id_groups
        draw_layer.set_data_group(id_groups)
        draw_layer.set_fill_color_group(self.gi_color_group)
        draw_layer.set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
        
        edge_clr = wx.Colour(200,200,200, self.opaque)
        draw_layer.set_edge_color(edge_clr)
        draw_layer.draw(dc, view, draw3D=ratio)
            
    
class SpaceTimeClusterQueryDialog(SpaceTimeQueryDialog):
    """
    Query Dialog for generating dynamic LISA Maps
    """
    def Add_Customized_Controls(self):
        x2,y2 = 20, 350
        wx.StaticBox(
            self.panel, -1, "SpaceTime cluster setting:",pos=(x2,y2),size=(325,70))
        wx.StaticText(self.panel, -1, "Weights file:",pos =(x2+10,y2+30),size=(90,-1))
        self.txt_weight_path = wx.TextCtrl(
            self.panel, -1, "",pos=(x2+100,y2+30), size=(180,-1) )
        #open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        open_bmp = wx.BitmapFromImage(stars.OPEN_ICON_IMG)
        
        self.btn_weight_path = wx.BitmapButton(
            self.panel,-1, open_bmp, pos=(x2+292,y2+32), style=wx.NO_BORDER)
        
        self.Bind(wx.EVT_BUTTON, self.BrowseWeightFile, self.btn_weight_path)
        
    def OnReset(self,event):
        self.reset()
        self.cmbox_location.SetSelection(-1)
        self.txt_weight_path.SetValue('')
        self.background_shps = []
        self.background_shp_idx = -1
        self.weight_path =None 
        
    def BrowseWeightFile(self,event):
        dlg = wx.FileDialog(
            None, message="Choose a weights file", 
            wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
            style=wx.OPEN | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.weight_path = dlg.GetPath()            
            self.txt_weight_path.SetValue(self.weight_path)
        dlg.Destroy() 
       
    def _check_weight_path(self):
        if len(self.txt_weight_path.GetValue())>0:
            return True
        return False
    
    def OnQuery(self,event):
        if self._check_time_itv_input() == False:
            self.ShowMsgBox("Please select a time interval first.")
            return
        if self._check_space_input() == False:
            self.ShowMsgBox("Please select a space file first.")
            return
        if self._check_weight_path() == False:
            self.ShowMsgBox("Please select a weights file first.")
            return
       
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self.query_date = None # query_date is not available in Trend Graph case
        self._filter_by_date_interval()
        self._filter_by_tod()
       
        # LISA layer (only one)
        lisa_layer = self.background_shps[self.background_shp_idx]
        if lisa_layer.shape_type != stars.SHP_POLYGON:
            self.ShowMsgBox("Space should be a POLYGON layer")
            return
        
        self.lisa_layer = lisa_layer
        lisa_data_dict = self.gen_date_by_step()
        self.query_data = lisa_data_dict
        
        if self.query_data == None:
            self.ShowMsgBox("Query dynamic data by step error!")
            return
        
        # check the extent of LISA layer and Points layer
        spacetimemap_widget= DynamicMapWidget(
            self.parent, [lisa_layer], SpaceTimeClusterMap,
            weight = self.weight_path,
            data = lisa_data_dict,
            start=self.start_date,
            end=self.end_date,
            step_by=self.step_by,
            step=self.step,
            size =(800,650),
        )
        spacetimemap_widget.Show()
        
        self.btn_save.Enable(True)
        
    def gen_date_by_step(self):
        """
        generate dynamic LISA map data by STEP
        """
        from stars.visualization.utils import GetIntervalStep
        from time import gmtime, strftime
        
        step = self.step
        step_by = self.step_by
        background_shp_idx = self.background_shp_idx    
        
        background_shp = self.background_shps[background_shp_idx]
        if background_shp.shape_type != stars.SHP_POLYGON:
            self.ShowMsgBox("Background shape file should be POLYGON!")
            return None
        
        start_date = self._wxdate2pydate(self.itv_start_date.GetValue())
        end_date   = self._wxdate2pydate(self.itv_end_date.GetValue())
        total_steps = GetIntervalStep(end_date, start_date, step, step_by) + 1
      
        self.start_date = start_date
        self.end_date = end_date
        
        return_data_dict = dict([(i,np.zeros(len(background_shp))) for i in range(total_steps)]) 
        
        # create a kd-tree from centroids of lisa_shp
        n = len(self.current_selected)
        itv = n/5
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Space-time query for dynamic LISA maps..               ",
            maximum = n,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        progress_dlg.CenterOnScreen()
        
        # check which point is in which polygon
        bmp,view,poly_color_dict = self.draw_space_in_buffer(background_shp)
        not_sure_points = []
        
        for count,j in enumerate(self.current_selected):
            if count % itv == 0:
                progress_dlg.Update(count +1)
                
            _date = self.all_dates[j]
            interval_idx = GetIntervalStep(_date, start_date, step, step_by)
            
            p = self.points[j]
            x,y = view.view_to_pixel(p[0],p[1])
            x,y = int(x), int(y)
            r = bmp.GetRed(x,y)
            g = bmp.GetGreen(x,y)
            b = bmp.GetBlue(x,y)
            
            if (r,g,b) in poly_color_dict:
                poly_id = poly_color_dict[(r,g,b)]
                return_data_dict[interval_idx][poly_id] += 1
            else:
                # todo: verify this
                # check 8 neighbors of (x,y), choose the valid one
                # which has closest color of (x,y)
                sel_poly_id = None
                for offset_x in range(-2,3):
                    for offset_y in range(-2,3):
                        if offset_x == 0 and offset_y == 0:
                            continue
                        n_x = x + offset_x
                        n_y = y + offset_y
                        n_r = bmp.GetRed(n_x,n_y)
                        n_g = bmp.GetGreen(n_x,n_y)
                        n_b = bmp.GetBlue(n_x,n_y)
                        if (n_r,n_g,n_b) in poly_color_dict:
                            sel_poly_id = poly_color_dict[(n_r,n_g,n_b)]
                            break
                if sel_poly_id:
                    return_data_dict[interval_idx][sel_poly_id] += 1
                else:
                    if (r,g,b) != (255,255,255):
                        not_sure_points.append(j)
        
        if len(not_sure_points)>0:
            # use kd-tree from centroids
            kdtree = background_shp.get_kdtree_locator()
            found_points = {}
            for count,j in enumerate(not_sure_points):
                _date = self.all_dates[j]
                interval_idx = GetIntervalStep(_date, start_date, step, step_by)
                
                # test if this point sits inside its nearest polygon
                p = self.points[j]

                # some points have same coordinates
                if p in found_points:
                    poly_id = found_points[p]
                    if poly_id != None:
                        return_data_dict[interval_idx][poly_id] += 1
                    continue
                    
                nn = kdtree.query(p, k=5)
                for id in nn[1]:
                    poly_id = background_shp.get_kdtree_polyid(id)
                    poly = pysal.cg.Polygon(background_shp.shape_objects[poly_id])
                    if poly.contains_point(p):
                        # test success: this point sits in current polygon
                        return_data_dict[interval_idx][poly_id] += 1
                        found_points[p] = poly_id
                        break
                found_points[p] = None
                
        progress_dlg.Update(n)
        progress_dlg.Destroy()
        
        return return_data_dict
    
    def OnSaveQueryToDBF(self, event):
        try:
            if self.query_data == None:
                return
            dlg = wx.FileDialog(
                self, message="Save query into new dbf files...", defaultDir=os.getcwd(), 
                defaultFile='%s.dbf' % (self.lisa_layer.name + '_dynamic_lisa'), 
                wildcard="shape file (*.dbf)|*.dbf|All files (*.*)|*.*", 
                style=wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            path = dlg.GetPath()
            dlg.Destroy()
            
            dbf = self.lisa_layer.dbf
            newDBF= pysal.open('%s.dbf'%path[:-4],'w')
            newDBF.header = []
            newDBF.field_spec = []
            for i in dbf.header:
                newDBF.header.append(i)
            for i in dbf.field_spec:
                newDBF.field_spec.append(i)
            for i in self.query_data.keys():
                newDBF.header.append('T_%d'%(i+1))
                newDBF.field_spec.append(('N',4,0))
            for i in range(dbf.n_records): 
                newRow = []
                row = dbf.read_record(i)
                newRow = [item for item in row]
                for j in self.query_data.keys():
                    val = self.query_data[j][i]
                    newRow.append(int(val))
                newDBF.write(newRow)
            newDBF.close()
            self.ShowMsgBox("Query results have been saved into new dbf file",
                            mtype='CAST Information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Save query results to new dbf file failed! Please check if the new dbf file is already existed.")
  
def ShowSpaceTimeClusterMap(self):
    # self is Main.py
    if not self.shapefiles or len(self.shapefiles) < 1:
        return
    shp_list = [shp.name for shp in self.shapefiles]
    dlg = wx.SingleChoiceDialog(
        self, 'Select a POINT or Polygon(with time field) shape file:', 
        'Space Time Cluster Map', shp_list,wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.GetSelection()
        shp = self.shapefiles[idx]
        if shp.shape_type == stars.SHP_POINT:
            # create dynamic LISA from points
            d_lisa_dlg = SpaceTimeClusterQueryDialog(
                self,"Space Time Cluster Map:" + shp.name,
                shp, 
                background_shps=self.shapefiles,
                size=stars.DIALOG_SIZE_QUERY_DYNAMIC_LISA
            )
            d_lisa_dlg.Show()
        elif shp.shape_type == stars.SHP_POLYGON:
            # bring up a dialog and let user select 
            # the time field in POLYGON shape file
            dbf_field_list = shp.dbf.header 
            timedlg = wx.MultiChoiceDialog(
                self, 'Select TIME fields to generate Dynamic LISA:', 
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
                # select weight file
                wdlg = wx.FileDialog(
                    self, message="Select a weights file",
                    wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
                    style=wx.OPEN | wx.CHANGE_DIR
                )
                if wdlg.ShowModal() == wx.ID_OK:
                    weight_path = wdlg.GetPath()
                    # directly show Dynamic LISA Map
                    dynamic_lisa_widget= DynamicMapWidget(
                        self, [shp], SpaceTimeClusterMap,
                        weight = weight_path,
                        data = lisa_data_dict,
                        start=1,
                        end=count,
                        step_by='',
                        step=1,
                        size =stars.MAP_SIZE_DYNAMIC_LISA,
                    )
                    dynamic_lisa_widget.Show()
                wdlg.Destroy()
            timedlg.Destroy()
        else: 
            self.ShowMsgBox("File type error! Should be a POINT shape file.")
            dlg.Destroy()
            return
    dlg.Destroy()