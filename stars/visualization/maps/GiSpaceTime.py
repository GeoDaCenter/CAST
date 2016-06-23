__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["GiSpaceTimeMap", "GiSpaceTimeQueryDialog", "ShowGiSpaceTimeMap"]

import os,math, datetime
import wx
import numpy as np
import pysal

import stars
from ShapeMap import *
from DynamicLisaMap import DynamicLISAMap, DynamicLISAQueryDialog
from stars.visualization.DynamicControl import DynamicMapControl
from stars.visualization.DynamicWidget import DynamicMapWidget
from stars.visualization.PlotWidget import PlottingCanvas
from stars.visualization import PlotWidget, AbstractData
from stars.visualization.utils import View2ScreenTransform, GetDateTimeIntervals, FilterShapeList
from stars.visualization.plots.SubTrendGraph import SubTrendGraph
from stars.visualization.dialogs import TimeWeightsDlg

class GiSpaceTimeMap(ShapeMap):
    """
    """
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
        
        try:
            self.weight_file  = kwargs["weight"]
            self.cs_data_dict = kwargs["query_data"]
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.step, self.step_by        = kwargs["step"] ,kwargs["step_by"]
            self.start_date, self.end_date = kwargs["start"],kwargs["end"]
            
            self.nav_left  = None
            self.nav_right = None
            self.bStrip    = True
            
            # preprocessing parameters 
            self.parent = parent
            self.layer  = layers[0]
            self.data_sel_keys   = sorted(self.cs_data_dict.keys())
            self.data_sel_values = [self.cs_data_dict[i] for i in self.data_sel_keys]
            self.weight          = pysal.open(self.weight_file).read()
            self.t = len(self.cs_data_dict) # number of data slices
            self.n = len(self.data_sel_values[0]) # number of shape objects
                        
            self.extent = self.layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight - self.bufferHeight/3.0
                ) 
          
            self.tick = 0
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            self.setupDynamicControls()
            self.parentFrame.SetTitle('Gi* Space Time Map-%s' % self.layer.name)
            self.dynamic_control = DynamicMapControl(self.parentFrame,self.t+1,self.updateDraw)
 
            self.trendgraphWidget = None
            self.popupTrendGraph = None
            
            # preprocessing Gi* SpaceTime maps
            self.processGiSpaceTimeMap()
            
        except Exception as err:
            detail_message = err.message
            if err.message == "dimension mismatch":
                detail_message = "The number of time intervals doesn't match time weights and space-time query."
            message = """Gi* Space Time map could not be created. Please re-select or create new time weights.
        
Details:""" + detail_message
            self.ShowMsgBox(message)
            
            self.UnRegister()
            if self.trendgraphWidget:
                self.trendgraphWidget.Close(True)
            if self.popupTrendGraph:
                self.popupTrendGraph.Close(True)
            self.parentFrame.Close(True)
            if os.name == 'nt':
                self.Destroy()
            return None
        
    def OnClose(self, event):
        self.UnRegister()
        if self.trendgraphWidget:
            self.trendgraphWidget.Close(True)
        if self.popupTrendGraph:
            self.popupTrendGraph.Close(True)
        event.Skip()
        
    def setupDynamicControls(self):
        """
        assign labels of dynamic controls
        """
        try:
            self.parentWidget = self.parent.GetParent()
            self.slider = self.parentWidget.animate_slider
            if isinstance(self.start_date, datetime.date):
                self.parentWidget.label_start.SetLabel('%2d/%2d/%4d'% (self.start_date.day,self.start_date.month,self.start_date.year))
                self.parentWidget.label_end.SetLabel('%2d/%2d/%4d'% (self.end_date.day,self.end_date.month,self.end_date.year))
            else:
                self.parentWidget.label_start.SetLabel('%d'% self.start_date)
                self.parentWidget.label_end.SetLabel('%4d'% self.end_date)
            self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (1,self.step, self.step_by))
        except:
            raise Exception("Setup dynamic controls in toolbar failed!")
            
    def processGiSpaceTimeMap(self):
        # promote for time weights
        tw_dlg  = TimeWeightsDlg(self.main, self.t, self.layer.name)
        tw_path = tw_dlg.Show()
        if tw_path == False:
            raise Exception("no time weights")
        
        tweights = pysal.open(tw_path).read()
        
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
            lg = pysal.esda.getisord.G_Local(y,tweights,transform='B',star=True)
            time_gstar[pid]   = lg.p_sim            
            time_gstar_z[pid] = lg.Zs
        
        self.tweights     = tweights
        self.time_gstar   = time_gstar 
        self.time_gstar_z = time_gstar_z 
        self.t_neighbors  = tweights.neighbors
        
        self.space_gstar  = dict() 
        self.space_gstar_z= dict()
        for tid,obs in self.cs_data_dict.iteritems():
            y = np.array(obs)
            lg = pysal.esda.getisord.G_Local(y,self.weight,star=True)
            self.space_gstar[tid]   = lg.p_sim
            self.space_gstar_z[tid] = lg.Zs
            
        trendgraph_data = dict()
        for i in range(self.n):
            data = []
            for j in range(self.t):
                data.append(self.cs_data_dict[j][i])
            trendgraph_data[i] = data
        self.trendgraph_data = trendgraph_data 
            
        self.trendgraphWidget = PlotWidget(
            self, 
            self.layer, 
            [self.trendgraph_data, [], self.interval_labels, self.tick, self.time_gstar,self.time_gstar_z, self.t_neighbors],
            SubTrendGraph, 
            pos = (self.parentFrame.Position[0] + self.parentFrame.Size[0], self.parentFrame.Position[1]),
            title="Trend Graph Plot for Time Gi*(%s): %s"%(self.t, self.layer.name)
            )
        self.trendgraphWidget.Show()
        # default color schema for Gi*
        self.HH_color = stars.LISA_HH_COLOR
        self.LL_color = stars.LISA_LL_COLOR
        self.NOT_SIG_color = stars.LISA_NOT_SIG_COLOR
        #self.OBSOLETE_color = stars.LISA_OBSOLETE_COLOR
        color_group =[self.NOT_SIG_color,self.HH_color,self.LL_color]
        label_group = ["Not Significant","High-High","Low-Low"]
        self.color_schema_dict[self.layer.name] = ColorSchema(color_group,label_group)
        
        self.gi_color_group = color_group
        self.internalLISA = False
        
        # inital drawing markov lisa map
        self.updateDraw(0)
        
        # Thread-based controller for dynamic LISA
        self.dynamic_control = DynamicMapControl(self.parentFrame,self.t,self.updateDraw) 
        
    def draw_selected_by_ids(self, shape_ids_dict, dc=None):
        super(GiSpaceTimeMap, self).draw_selected_by_ids(shape_ids_dict,dc)
        
        self.selected_shape_ids = shape_ids_dict
        if self.internalLISA:
            self.draw_popup(dc)
        
    def draw_selected_by_region(self,dc, region, 
                                isEvtResponse=False, 
                                isScreenCoordinates=False):
        if self.internalLISA:
            self.draw_popup(dc, region)
            
        super(GiSpaceTimeMap, self).draw_selected_by_region(
            dc, region, isEvtResponse, isScreenCoordinates)
        
     
    def showInternalPopupTimeLISA(self, event):
        self.internalLISA = not self.internalLISA
        
        if self.internalLISA == False:
            if self.popupTrendGraph != None:
                self.popupTrendGraph.Close(True)
                self.popupTrendGraph = None
            
        
    def showExtPopupTimeLISA(self, event):
        self.internalLISA = False
       
        # show LISA trend graph
        if self.trendgraphWidget == None or isinstance(self.trendgraphWidget, wx._core._wxPyDeadObject):
            self.trendgraphWidget = PlotWidget(
                self, 
                self.layer, 
                [self.trendgraph_data, [], self.interval_labels, self.tick, self.time_gstar,self.time_gstar_z, self.t_neighbors],
                SubTrendGraph, 
                pos = (self.parentFrame.Position[0] + self.parentFrame.Size[0], self.parentFrame.Position[1]),
                title="Trend Graph Plot for Time Gi*(%s): %s"%(self.t, self.layer.name)
            )
            self.trendgraphWidget.Show()
        self.trendgraphWidget.SetFocus()
            
    def draw_popup(self, dc, region=None):
        if self.popupTrendGraph != None:
            self.popupTrendGraph.Close(True)
            self.popupTrendGraph = None
            
        if len(self.selected_shape_ids) == 0:
            return
        
        selected_ids = []
        if self.layer.name in self.selected_shape_ids:
            selected_ids = self.selected_shape_ids[self.layer.name]
            
            
        self.popupTrendGraph = SubTrendGraph(
            self.parent, 
            self.layer, 
            [self.trendgraph_data, selected_ids, self.interval_labels, self.tick, self.time_gstar,self.time_gstar_z, self.t_neighbors]
            )
        self.popupTrendGraph.Hide()
      
        # start draw a popup within window
        if region:
            x,y = region[2],region[3]
        else:
            x,y = self.layer.centroids[selected_ids[0]][0]
            x,y = self.view.view_to_pixel(x,y)
            x,y = int(x),int(y)
        w = int(math.ceil(self.bufferWidth * 0.5))
        if w < 300: w = 300
        if w > 450: w = 450
        h = w * 0.7
        if x + w > self.bufferWidth: 
            if x - w > 0:
                x = x - w
            else:
                x = self.bufferWidth - w
        if y + h > self.bufferHeight: 
            if y - h > 0:
                y = y - h
            else:
                y = self.bufferHeight - h
        
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Color(120,120,120,160)))
        dc.DrawRectangle(x+5,y+h, w, 5)
        dc.DrawRectangle(x+w,y+5, 5, h)
        dc.SetPen(wx.Pen(wx.Color(100,100,100,100)))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(x,y,w,h)
        
        self.popupTrendGraph.bufferWidth = w
        self.popupTrendGraph.bufferHeight = h
        self.popupTrendGraph.buffer = wx.EmptyBitmapRGBA(w,h,255,255,255,222)
        tmp_dc = wx.BufferedDC(None, self.popupTrendGraph.buffer)
        if not 'Linux' in stars.APP_PLATFORM \
           and 'Darwin' != stars.APP_PLATFORM:
            tmp_dc = wx.GCDC(tmp_dc)
        self.popupTrendGraph.DoDraw(tmp_dc)
        dc.DrawBitmap(self.popupTrendGraph.buffer,x,y)
        
    def OnSize(self,event):
        """
        overwrite OnSize in ShapeMap.py
        """
        self.bufferWidth,self.bufferHeight = self.GetClientSize()
        if self.bufferHeight > 0:
            if self.bStrip == False:
                self.view.pixel_height = self.bufferHeight
            else:
                self.view.pixel_height = self.bufferHeight - self.bufferHeight/3.0
            self.view.pixel_width = self.bufferWidth
            self.view.init()
        if self.bStrip: 
            self.stripBuffer = None
        self.reInitBuffer = True
        
    def OnMotion(self, event):
        """
        """
        if self.bStrip:
            mouse_end_x, mouse_end_y = (event.GetX(), event.GetY())
            # check for left
            if self.nav_left:
                if self.nav_left[0] <= mouse_end_x <= self.nav_left[2] and \
                   self.nav_left[1] <= mouse_end_y <= self.nav_left[3]:
                    return
            # determine for right 
            if self.nav_right:
                if self.nav_right[0] <= mouse_end_x <= self.nav_right[2] and \
                   self.nav_right[1] <= mouse_end_y <= self.nav_right[3]:
                    return
        
        if event.Dragging() and event.LeftIsDown() and self.isMouseDrawing:
            x, y = event.GetX(), event.GetY() 
            # while mouse is down and moving
            if self.map_operation_type == stars.MAP_OP_PAN:
                # disable PAN (not support in this version)
                return
                          
        # give the rest task to super class
        super(GiSpaceTimeMap,self).OnMotion(event)

        
    def Update(self, tick):
        """
        When SLIDER is dragged
        """
        self.updateDraw(tick)     

    def updateDraw(self,tick):
        """
        Called for dynamic updating the map content
        """
        self.tick = tick
        p_values = self.space_gstar[tick]
        z_values = self.space_gstar_z[tick]
        
        # 0 not significant, 6 significant change
        not_sig = list(np.where(p_values>0.05)[0])
        sig     = set(np.where(p_values<=0.05)[0])
        hotspots = list(sig.intersection(set(np.where(z_values>=0)[0])) )
        coldspots = list(sig.intersection(set(np.where(z_values<0)[0])) )
        id_groups = [not_sig,hotspots,coldspots]
            
        self.id_groups = id_groups
        self.draw_layers[self.layer].set_data_group(id_groups)
        self.draw_layers[self.layer].set_fill_color_group(self.gi_color_group)
        edge_clr = self.color_schema_dict[self.layer.name].edge_color
        self.draw_layers[self.layer].set_edge_color(edge_clr)
        # trigger to draw 
        self.reInitBuffer = True 
        self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (tick+1,self.step, self.step_by))
        
    def DoDraw(self, dc):
        """
        Overwrite this function from base class for customized drawing
        """
        super(GiSpaceTimeMap, self).DoDraw(dc)
        
        if self.bStrip:
            self.drawStripView(dc)
 
    def OnLeftUp(self, event):
        """ override for click on strip view """
        if self.bStrip:
            mouse_end_x, mouse_end_y = (event.GetX(), event.GetY())
            # check for left
            if self.nav_left:
                if self.nav_left[0] <= mouse_end_x <= self.nav_left[0] + self.nav_left[2] and \
                   self.nav_left[1] <= mouse_end_y <= self.nav_left[1] + self.nav_left[3]:
                    self.tick = self.tick -1 if self.tick>0 else 0
                    self.updateDraw(self.tick)
            # determine for right 
            if self.nav_right:
                if self.nav_right[0] <= mouse_end_x <= self.nav_right[0] + self.nav_right[2] and \
                   self.nav_right[1] <= mouse_end_y <= self.nav_right[1] + self.nav_right[3]:
                    self.tick = self.tick +1 if self.tick<=self.n else self.tick
                    self.updateDraw(self.tick)
            
        # give the rest task to super class
        super(GiSpaceTimeMap,self).OnLeftUp(event)
        
    def drawStripView(self,dc):
        """
        For each Gi map at T_i, two related Gi maps at 
        T_(i-1) ant T_(i+1) will be displayed in this strip area
        """
        n = len(self.data_sel_keys)
        if n <= 1:
            return
            
        start = self.tick
        if start+2 > n:
            return
        end = start + 2
        
        # flag for drawing navigation arrow
        b2LeftArrow = True if self.tick > 0 else False
        b2RightArrow = True if self.tick < n-2 else False
        
        # at area: 0,self.bufferHeight * 2/3.0
        # draw a light gray area at the bottom first
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)
        dc.SetPen(wx.TRANSPARENT_PEN)
        brush = wx.Brush(stars.STRIP_VIEW_BG_COLOR)
        dc.SetBrush(brush)
        framePos = 0, self.bufferHeight * 2.0/3.0
        dc.DrawRectangle(framePos[0],framePos[1], self.bufferWidth, self.bufferHeight/3.0)
        
        # calculate width and height for each bmp
        bmpFrameWidth = self.bufferWidth / 2.0 # frame is divided into 2 parts
        bmpFrameHeight = self.bufferHeight / 3.0
        bmpWidth = bmpFrameWidth * 0.6
        bmpHeight = bmpFrameHeight * 0.8
        bmpOffsetX = (bmpFrameWidth - bmpWidth )/2.0 
        bmpOffsetY = (bmpFrameHeight- bmpHeight)/2.0 

        # draw text for center large graph
        start_date, end_date = self.datetime_intervals[self.tick]
        if isinstance(start_date, datetime.date):
            info_tip = "t%d:(%d/%d/%d-%d/%d/%d)" % \
                     (self.tick+1,start_date.month,start_date.day,start_date.year,
                     end_date.month, end_date.day, end_date.year)
        else:
            info_tip = "t%d - t%d" % (start_date, end_date)
        txt_w,txt_h = dc.GetTextExtent(info_tip)
        dc.DrawText(info_tip, (self.bufferWidth - txt_w)/2, framePos[1] - txt_h)
        
        # draw two related Gi* maps in strip area
        dc.SetBrush(wx.Brush(stars.STRIP_VIEW_MAP_BG_COLOR))
        #for i in range(start, end):
        if self.tick - 1 >= 0:
            start_pos = bmpOffsetX, framePos[1]+bmpOffsetY 
            dc.DrawRectangle(start_pos[0], start_pos[1], bmpWidth, bmpHeight)
            bmp = wx.EmptyBitmapRGBA(
                bmpFrameWidth, bmpFrameHeight,
                red = stars.STRIP_VIEW_BG_COLOR.red,
                green = stars.STRIP_VIEW_BG_COLOR.green,
                blue = stars.STRIP_VIEW_BG_COLOR.blue,
                alpha = stars.STRIP_VIEW_BG_COLOR.alpha
                )
            bmp = self.drawSubGiMap(self.tick-1,bmpWidth, bmpHeight, bmp)
            dc.DrawBitmap(bmp, start_pos[0], start_pos[1])
            start_date, end_date = self.datetime_intervals[self.tick-1]
            if isinstance(start_date, datetime.date):
                info_tip = "t%d:(%d/%d/%d-%d/%d/%d)" % \
                         (self.tick,start_date.month,start_date.day,start_date.year,
                         end_date.month, end_date.day, end_date.year)
            else:
                info_tip = "t%d - t%d" % (start_date, end_date)
            txt_w,txt_h = dc.GetTextExtent(info_tip)
            dc.DrawText(info_tip, start_pos[0] + (bmpWidth - txt_w)/2, start_pos[1]+bmpHeight+2)
            
        if self.tick + 1 < self.t:
            start_pos = bmpFrameWidth + bmpOffsetX , framePos[1]+bmpOffsetY 
            dc.DrawRectangle(start_pos[0], start_pos[1], bmpWidth, bmpHeight)
            bmp = wx.EmptyBitmapRGBA(
                bmpFrameWidth, bmpFrameHeight,
                red = stars.STRIP_VIEW_BG_COLOR.red,
                green = stars.STRIP_VIEW_BG_COLOR.green,
                blue = stars.STRIP_VIEW_BG_COLOR.blue,
                alpha = stars.STRIP_VIEW_BG_COLOR.alpha
                )
            bmp = self.drawSubGiMap(self.tick+1,bmpWidth, bmpHeight, bmp)
            dc.DrawBitmap(bmp, start_pos[0], start_pos[1])
            start_date, end_date = self.datetime_intervals[self.tick+1]
            if isinstance(start_date, datetime.date):
                info_tip = "t%d:(%d/%d/%d-%d/%d/%d)" % \
                         (self.tick+2,start_date.month,start_date.day,start_date.year,
                         end_date.month, end_date.day, end_date.year)
            else:
                info_tip = "t%d - t%d" % (start_date, end_date)
            txt_w,txt_h = dc.GetTextExtent(info_tip)
            dc.DrawText(info_tip, start_pos[0] + (bmpWidth - txt_w)/2, start_pos[1]+bmpHeight+2)
        
        # draw navigation arrows
        arrow_y = framePos[1] + bmpFrameHeight/2.0
        
        dc.SetFont(wx.Font(stars.NAV_ARROW_FONT_SIZE, wx.NORMAL, wx.NORMAL, wx.NORMAL))
        dc.SetBrush(wx.Brush(stars.STRIP_VIEW_NAV_BAR_BG_COLOR))
        dc.SetPen(wx.WHITE_PEN)
        if b2LeftArrow:
            self.nav_left = framePos[0], framePos[1], 20, self.bufferHeight/3.0
            dc.DrawRectangle(self.nav_left[0], self.nav_left[1], self.nav_left[2], self.nav_left[3])
            dc.SetPen(wx.WHITE_PEN)
            dc.DrawText("<<", framePos[0]+3, arrow_y)
        else:
            self.nav_left = None
            
        if b2RightArrow:
            self.nav_right = framePos[0]+self.bufferWidth - 20,framePos[1], 20, self.bufferHeight/3.0
            dc.DrawRectangle(self.nav_right[0], self.nav_right[1], self.nav_right[2], self.nav_right[3])
            dc.SetPen(wx.WHITE_PEN)
            dc.DrawText(">>", self.bufferWidth-15, arrow_y)
        else:
            self.nav_right = None
            
    def drawSubGiMap(self, idx, bufferWidth, bufferHeight,bmp):
        """
        Draw two relative Gi* maps for current Gi* map
        """
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
        
        p_values = self.space_gstar[idx]
        z_values = self.space_gstar_z[idx]
        
        not_sig = list(np.where(p_values>0.05)[0])
        sig     = set(np.where(p_values<=0.05)[0])
        hotspots = list(sig.intersection(set(np.where(z_values>=0)[0])) )
        coldspots = list(sig.intersection(set(np.where(z_values<0)[0])) )
        id_groups = [not_sig,hotspots,coldspots]
        
        from stars.visualization.maps.BaseMap import PolygonLayer
        draw_layer = PolygonLayer(self, self.layer, build_spatial_index=False)
        #edge_clr = wx.Colour(200,200,200, self.opaque)
        edge_clr = self.color_schema_dict[self.layer.name].edge_color
        draw_layer.set_edge_color(edge_clr)
        draw_layer.set_data_group(id_groups)
        draw_layer.set_fill_color_group(self.gi_color_group)
        draw_layer.draw(dc, view)        
        
        return bmp
        
    def OnRightUp(self,event):
        menu = wx.Menu()
        menu.Append(210, "Select Neighbors", "")
        menu.Append(211, "Cancel Select Neighbors", "")
        menu.Append(212, "Toggle internal popup window", "")
        #menu.Append(212, "Show external popup time LISA", "")
        
        menu.UpdateUI()
        menu.Bind(wx.EVT_MENU, self.select_by_weights, id=210)
        menu.Bind(wx.EVT_MENU, self.cancel_select_by_weights, id=211)
        menu.Bind(wx.EVT_MENU, self.showInternalPopupTimeLISA, id=212)
        #menu.Bind(wx.EVT_MENU, self.showExtPopupTimeLISA, id=212)
        self.PopupMenu(menu)
        
        event.Skip()     
        
class GiSpaceTimeQueryDialog(DynamicLISAQueryDialog):
    """
    Query Dialog for generating Markov LISA Maps
    """
    def Add_Customized_Controls(self):
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
        
    def ShowPopupMenu(self, event):
        """
        popup menu for checklist box
        """
        menu = wx.Menu()
        menu.Append(101, "Select all transitions", "")
        menu.Append(102, "De-select all transitions", "")
        menu.Bind(wx.EVT_MENU, self.EvtSelectAllCheckList, id=101)
        menu.Bind(wx.EVT_MENU, self.EvtDeselectAllCheckList, id=102)
        menu.UpdateUI()
        
        self.PopupMenu(menu)
    
    def EvtSelectAllCheckList(self, event):
        self.lm_labels = []
        checked_list = []
        for i in range(len(self.lm_filter_lables)):
            self.lb.SetSelection(i)
            self.lm_labels.append(i+1)
            checked_list.append(i)
        self.lb.SetChecked(checked_list)
    
    def EvtDeselectAllCheckList(self, event):
        for i in range(len(self.lm_filter_lables)):
            self.lb.SetSelection(i, False)
            self.lm_labels.append(i+1)
        self.lm_labels = []
        self.lb.SetChecked([])
    
    def EvtCheckListBox(self, event):
        index = event.GetSelection()
        label = self.lb.GetString(index)
        self.lb.SetSelection(index)
        
        if self.lm_labels.count(index+1):
            self.lm_labels.remove(index+1)
        else:
            self.lm_labels.append(index+1)
        
    def OnQuery(self,event):
        if self._check_time_itv_input() == False or\
           self._check_weight_path() == False or\
           self._check_space_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self.query_date = None 
        self._filter_by_date_interval()
        self._filter_by_tod()
        
        self.query_data = self.gen_date_by_step()
        if self.query_data == None or len(self.query_data) <= 1:
            self.ShowMsgBox("Gi* Space Time Cluster Map requires at least 2 time intervals, please reselect step-by parameters.")
            return
        # LISA layer (only one)
        lisa_layer = [self.background_shps[self.background_shp_idx]]
        gi_widget = DynamicMapWidget(
            self.parent,
            lisa_layer,
            GiSpaceTimeMap,
            weight=self.weight_path,
            query_data=self.query_data,
            size=(800,650),
            start= self._wxdate2pydate(self.itv_start_date.GetValue()),
            end= self._wxdate2pydate(self.itv_end_date.GetValue()),
            step_by=self.step_by,
            step=self.step+1
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
 
            
def ShowGiSpaceTimeMap(self):
    # self is Main.py
    if not self.shapefiles or len(self.shapefiles) < 1:
        return
    shp_list = [shp.name for shp in self.shapefiles]
    dlg = wx.SingleChoiceDialog(
        self, 
        'Select a POINT or Polygon(with time field) shape file:', 
        'Gi* Space Time Map', 
        shp_list,
        wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.GetSelection()
        shp = self.shapefiles[idx]
        background_shapes = FilterShapeList(self.shapefiles, stars.SHP_POLYGON)
        if shp.shape_type == stars.SHP_POINT:
            # create Markov LISA from points
            gi_dlg = GiSpaceTimeQueryDialog(
                self,"Gi* Space Time:" + shp.name,
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
                self, 'Select TIME fields to generate Gi* Space Time map:', 
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
                    # todo: select filter
                    weight_path = wdlg.GetPath()
                    gi_spacetime_widget= DynamicMapWidget(
                        self, 
                        [shp], 
                        GiSpaceTimeMap,
                        weight = weight_path,
                        query_data = lisa_data_dict,
                        size =stars.MAP_SIZE_MARKOV_LISA,
                        start=1,
                        end=count-1,
                        step_by='',
                        step=1
                        )
                    gi_spacetime_widget.Show()
                wdlg.Destroy()
            timedlg.Destroy()
        else:
            self.ShowMsgBox("File type error. Should be a POINT or POLYGON shapefile.")
            dlg.Destroy()
            return
    dlg.Destroy() 