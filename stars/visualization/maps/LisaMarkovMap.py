"""
5 canvas (LISA, LISAMarkovMap, PieChart, HeatMatrix, LISAMarkovPlot), will be
used to represent LISA Markov.
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["LISAMarkovMap", 'LISAMarkovPlot', 'LISAMarkovQueryDialog']

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
from stars.visualization.plots import PieChart,HeatMatrix
from stars.visualization.utils import View2ScreenTransform, GetDateTimeIntervals

class LISAMarkovMap(ShapeMap):
    """
    """
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
        
        try:
            self.weight_file = kwargs["weight"]
            self.cs_data_dict = kwargs["query_data"]
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.step, self.step_by = kwargs["step"] ,kwargs["step_by"]
            self.start_date, self.end_date = kwargs["start"],kwargs["end"]
            
            self.nav_left = None
            self.nav_right = None
            self.bStrip = True
            
            # preprocessing parameters 
            self.parent = parent
            self.layer = layers[0]
            self.data_sel_keys = sorted(self.cs_data_dict.keys())
            self.data_sel_values = [self.cs_data_dict[i] for i in self.data_sel_keys]
            self.weight = pysal.open(self.weight_file).read()
            self.t = len(self.cs_data_dict) # number of data slices
            self.n = len(self.data_sel_values[0]) # number of shape objects
                        
            self.extent = self.layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight - self.bufferHeight/3.0
                ) 
           
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            self.setupDynamicControls()
            self.parentFrame.SetTitle('LISA Markov-%s' % self.layer.name)
            self.dynamic_control = DynamicMapControl(self.parentFrame,self.t,self.updateDraw)
            
            # preprocessing Markov LISA maps
            self.processLISAMarkovMaps()
            
        except Exception as err:
            self.ShowMsgBox("""LISA Markov map could not be created. 
            
Details: """ + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return None
        
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
            
     
    def processLISAMarkovMaps(self):
        """
        preprocessing Markov LISA maps
        """
        self.computeMarkovLISA()
        # default color schema for LISA
        self.SIG_CHANGE_clor = wx.Colour(0,255,0)
        self.HH_color = stars.LISA_HH_COLOR
        self.LL_color = stars.LISA_LL_COLOR
        self.LH_color = stars.LISA_LH_COLOR 
        self.HL_color = stars.LISA_HL_COLOR 
        self.NOT_SIG_color = stars.LISA_NOT_SIG_COLOR
        self.OBSOLETE_color = stars.LISA_OBSOLETE_COLOR
        color_group =[
            self.NOT_SIG_color,
            self.HH_color,
            self.LL_color,
            self.LH_color,
            self.HL_color,
            self.OBSOLETE_color,
            self.SIG_CHANGE_clor
            ]
        self.mlisa_color_group = color_group
        label_group = ["Not Significant",
                       "High-High",
                       "Low-Low",
                       "Low-High",
                       "High-Low",
                       "Neighborless",
                       "Significant Change"
                       ]
        self.color_schema_dict[self.layer.name] = ColorSchema(self.mlisa_color_group,label_group)
        # inital drawing markov lisa map
        self.updateDraw(0)
        # Thread-based controller for dynamic LISA
        self.dynamic_control = DynamicMapControl(self.parentFrame,self.t-1,self.updateDraw) 
    
    def precomputeLISA(self):
        """
        """
        n = len(self.data_sel_keys)
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Pre-computing LISAs with 499 permutations...               ",
            maximum = n,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
            )
        progress_dlg.CenterOnScreen()
        moran_locals = []
        try:
            # C++ DLL call
            from stars.core.LISAWrapper import call_lisa
            for i,data in enumerate(self.data_sel_values):
                progress_dlg.Update(i+1)
                localMoran, sigLocalMoran, sigFlag, clusterFlag = call_lisa(
                    data, 
                    str(self.weight_file),
                    499)
                ml = [localMoran, sigLocalMoran, sigFlag, clusterFlag]
                moran_locals.append(ml)        
        except:
            # old for pysal
            for i,data in enumerate(self.data_sel_values):
                progress_dlg.Update(i+1)
                localMoran = pysal.Moran_Local(data, self.weight, transformation = "r", permutations = 499)
                ml = [localMoran.Is, localMoran.p_sim, [], localMoran.q]
                moran_locals.append(ml)        
        progress_dlg.Destroy()
        return moran_locals
        
    def computeMarkovLISA(self):
        """
        precomputing LISA maps
        """
        try:
            self.id_groups = []
            # computer the markov lisa and lisa maps
            progress_dlg = wx.ProgressDialog(
                "Progress",
                "Pre-computing Markov LISA...               ",
                maximum = 2,
                parent=self,
                style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
                )
            progress_dlg.CenterOnScreen()
            progress_dlg.Update(1)
            self.lisa_markov = pysal.LISA_Markov(np.array(self.data_sel_values).transpose(), self.weight)
            self.lisa_markov_mt = self.lisa_markov.move_types
            self.lisa_markov_p = np.array(self.lisa_markov.p)
            progress_dlg.Update(2)
            progress_dlg.Destroy()
            # precompute LISAs
            self.moran_locals = self.precomputeLISA() 
            # filter out non-sig: all LISA p-values should be
            # significant for one shape object
            for i in range(self.t):
                ml_p_sim = np.array(self.moran_locals[i][1]) # 1~p values
                for j in range(self.n):
                    if ml_p_sim[j] > 0.05:
                        # then object j is not significant
                        self.lisa_markov_mt[j][-1] = 0
        except:
            raise Exception("compute Markov LISA error! ")
            
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
        super(LISAMarkovMap,self).OnMotion(event)
        
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
        move_types = self.lisa_markov_mt.transpose()[-1] # only last time step is checked
        
        # 0 not significant, 6 significant change
        not_sig = list(np.where(move_types==0)[0])
        sig_change = list(np.where(move_types>0)[0])
        id_groups = [not_sig,[],[],[],[],[],sig_change]
            
        self.id_groups = id_groups
        self.draw_layers[self.layer].set_data_group(id_groups)
        self.draw_layers[self.layer].set_fill_color_group(self.mlisa_color_group)
        self.draw_layers[self.layer].set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
        # trigger to draw 
        self.reInitBuffer = True 
        self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (tick+1,self.step, self.step_by))
        
    def DoDraw(self, dc):
        """
        Overwrite this function from base class for customized drawing
        """
        super(LISAMarkovMap, self).DoDraw(dc)
        
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
        super(LISAMarkovMap,self).OnLeftUp(event)
        
    def drawStripView(self,dc):
        """
        For each Markov LISA map, two related LISA maps at 
        T_i ant T_(i+1) will be displayed in this strip area
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
       
        # draw two related LISA maps in strip area
        dc.SetBrush(wx.Brush(stars.STRIP_VIEW_MAP_BG_COLOR))
        for i in range(start, end):
            start_pos = bmpFrameWidth * (i-start) + bmpOffsetX , framePos[1]+bmpOffsetY 
            dc.DrawRectangle( start_pos[0], start_pos[1], bmpWidth, bmpHeight)
            bmp = wx.EmptyBitmapRGBA(
                bmpFrameWidth, bmpFrameHeight,
                red = stars.STRIP_VIEW_BG_COLOR.red,
                green = stars.STRIP_VIEW_BG_COLOR.green,
                blue = stars.STRIP_VIEW_BG_COLOR.blue,
                alpha = stars.STRIP_VIEW_BG_COLOR.alpha
                )
            bmp = self.drawSubLISA(i,bmpWidth, bmpHeight, bmp)
            
            dc.DrawBitmap(bmp, start_pos[0], start_pos[1])
                
            start_date, end_date = self.datetime_intervals[i]
            
            if isinstance(start_date, datetime.date):
                info_tip = "%d/%d/%d - %d/%d/%d"% \
                         (start_date.month,start_date.day,start_date.year,
                          end_date.month, end_date.day, end_date.year
                          )
            else:
                info_tip = "t%d - t%d" % (start_date, end_date)
            txt_w,txt_h = dc.GetTextExtent(info_tip)
            dc.DrawText(info_tip, start_pos[0] + (bmpWidth - txt_w)/2, start_pos[1]+bmpHeight+2)
        
        # draw arrow and info of two LISA maps
        arrow_start_pos = bmpFrameWidth - bmpOffsetX-1, framePos[1] + bmpHeight /2.0
        self.drawArrow(dc, arrow_start_pos, bmpHeight/5.0 ,bmpOffsetX)
        
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
            
    def drawArrow(self, dc, start_pos, size, length):
        """
        Draw an arrow at a specific position, size and length
        """
        length_old = length
        length = length + size/2.0
        pos0 = start_pos
        pos1 = (pos0[0] + length - size, pos0[1])
        pos2 = (pos1[0], pos1[1] - size /2.0)
        pos3 = (pos0[0] + length, pos0[1] + size / 2.0)
        pos6 = (pos0[0], pos0[1] + size)
        pos5 = (pos6[0] + length - size, pos6[1])
        pos4 = (pos5[0], pos5[1] + size/2.0)
        arrow = [pos0,pos1,pos2,pos3,pos4,pos5,pos6]
        
        dc.DrawPolygon(arrow)
        pos7 = (pos0[0]+length_old*2+1, pos0[1])
        pos8 = (pos7[0], pos7[1]+size)
        pos9 = (pos0[0],pos8[1])
        dc.DrawPolygon([pos0, pos7, pos8, pos9])
        
    def drawSubLISA(self, lisa_idx, bufferWidth, bufferHeight,bmp):
        """
        Draw two relative LISA maps for current Markov LISA map
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
        
        lm = self.moran_locals[lisa_idx]
        # 0 not significant, 1 HH, 2 LL, 3 LH, 4 HL, 5 Neighborless
        try:
            # LISA from c++ DLL call
            localMoran, sigLocalMoran, sigFlag, clusterFlag = lm
            lm_moran = np.array(localMoran)
            lm_p_sim = np.array(sigLocalMoran)
            lm_sig = np.array(sigFlag)
            lm_q = np.array(clusterFlag)
            candidates = np.where(lm_sig<1)[0]
            id_groups = []
            id_groups.append(list(candidates))
            for i in range(1,n):
                cluster = set(np.where(lm_q==i)[0]) - set(candidates)
                id_groups.append(cluster)
        except:
            # LISA from Pysal call
            sigFlag = lm[2]
            clusterFlag = lm[3]
            lm_sig = np.array(sigFlag)
            lm_q = np.array(clusterFlag)
            id_groups = [[] for i in range(6)]
            for i,sig in enumerate(lm_sig):
                if sig > 0:
                    id_groups[lm_q[i]].append(i)
                else:
                    id_groups[0].append(i)
            
        from stars.visualization.maps.BaseMap import PolygonLayer
        draw_layer = PolygonLayer(self, self.layer, build_spatial_index=False)
        #edge_clr = wx.Colour(200,200,200, self.opaque)
        edge_clr = self.color_schema_dict[self.layer.name].edge_color
        draw_layer.set_edge_color(edge_clr)
        draw_layer.set_data_group(id_groups)
        lisa_color_group = [self.NOT_SIG_color,self.HH_color,self.LL_color,
                            self.LH_color,self.HL_color,self.OBSOLETE_color]
        draw_layer.set_fill_color_group(lisa_color_group)
        draw_layer.draw(dc, view)        
        
        return bmp
        
    def OnRightUp(self,event):
        menu = wx.Menu()
        menu.Append(201, "View Markov transition plot", "")
        menu.Append(202, "View Markov transition probability matrix", "")
        menu.AppendSeparator()
        #menu.Append(210, "Select by Weights", "")
        menu.Append(210, "Select Neighbors", "")
        menu.Append(211, "Cancel Select Neighbors", "")
        
        menu.UpdateUI()
        menu.Bind(wx.EVT_MENU, self.showMarkovTransitionPlot, id=201)
        menu.Bind(wx.EVT_MENU, self.showMarkovTransitionMatrix, id=202)
        menu.Bind(wx.EVT_MENU, self.select_by_weights, id=210)
        self.PopupMenu(menu)
        
        event.Skip()     
        
    def showMarkovTransitionPlot(self, event):
        widget = PlotWidget(
            self,
            self.layer,
            [self.moran_locals,self.lisa_markov_mt, self.interval_labels],
            LISAMarkovPlot,
            title="Markov LISA Transition Plot:%s" % self.layer.name
            )
        widget.Show()    
        
    def showMarkovTransitionMatrix(self,event):
        widget = PlotWidget(
            self, 
            self.layer,
            self.lisa_markov_p,
            HeatMatrix,
            title="Markov LISA Transition Matrix:%s" % self.layer.name
            )
        widget.Show()
    
class LISAMarkovPlot(PlottingCanvas):
    """
    A plot for time series of LISA markov transitions.
    """
    def __init__(self,parent, layer, data, **kwargs):
        PlottingCanvas.__init__(self, parent, data)
       
        try:
            self.enable_axis = False
            self.enable_axis_x = False
            self.enable_axis_y = False
            self.isAutoScale = False
            self.enable_grid = False
          
            # setup toolbar for Markov LISA
            self.toolbar = parent.toolbar
            self.txt_from = wx.TextCtrl(self.toolbar, -1, "", size=(80,-1),style=wx.TE_PROCESS_ENTER)
            self.txt_to = wx.TextCtrl(self.toolbar, -1, "", size=(80,-1),style=wx.TE_PROCESS_ENTER)
            self.btn_previous = wx.Button(self.toolbar, 101, "<<")
            self.btn_next = wx.Button(self.toolbar, 102, ">>")
            self.toolbar.AddControl(wx.StaticText(self.toolbar,-1,"Current display from "))
            self.toolbar.AddControl(self.txt_from)
            self.toolbar.AddControl(wx.StaticText(self.toolbar,-1,"to"))
            self.toolbar.AddControl(self.txt_to)
            self.toolbar.AddControl(self.btn_previous)
            self.toolbar.AddControl(self.btn_next)
            parent.Bind(wx.EVT_BUTTON, self.OnClickPrevious, self.btn_previous)
            parent.Bind(wx.EVT_BUTTON, self.OnClickNext, self.btn_next)
            parent.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateDisplay, self.txt_from)
            parent.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateDisplay, self.txt_to)
            
            self.layer_name = layer.name
            self.moran_locals, lisa_markov_mt, self.interval_labels = data
            self.t = len(self.moran_locals)
            # convert LISA Markov move_types to {poly_id:seq_data}
            lisa_markov_mt.transpose()
            self.cs_data_dict = {}
            for i,seq in enumerate(lisa_markov_mt):
                self.cs_data_dict[i] = list(seq)
                
            self.status_bar = None
            self.data = True # Dummy
            self.title = "LISA Markov Plot"
            self.x_label = "time period"
            self.y_label = "shape id"
            self.tick = 0
            self.num_objects_per_page = 15
            self.n = len(self.cs_data_dict)
            self._y_max, self.x_max = lisa_markov_mt.shape
            self.x_max += 1
            #for setup view with extent, see PlotWidget.py line181
            self.y_max = self.num_objects_per_page 
            self.y_min, self.x_min = 0, 0
            self.extent = (self.x_min, 0, self.x_max, self.num_objects_per_page)
            
            self.selected_obj_ids = [] # objects that currectly selected
            self.highlighted_shape_objects = [] # objects that shown in plot

            # setup values for controls in toolbar
            self.id_start_object = 1
            self.id_end_object = self.num_objects_per_page if self.num_objects_per_page <= self.n else self.n
            self.txt_from.SetValue(str(self.id_start_object))
            self.txt_to.SetValue(str(self.id_end_object))
            self.btn_previous.Disable()
            if self.n <= self.num_objects_per_page:
                self.btn_next.Disable()
            self.toolbar.Realize()
            
        except Exception as err:
            self.ShowMsgBox("""LISA Markov plot could not be created. 
            
            
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
       
    def OnUpdateDisplay(self, event):
        self.id_start_object = int(self.txt_from.GetValue())
        self.id_end_object = int(self.txt_to.GetValue())
        if self.id_start_object <= 0:
            self.ShowMsgBox("Start id should larger than 0.")
            return
        if self.id_end_object <= 0:
            self.ShowMsgBox("End id should larger than 0.")
            return
        if self.id_start_object >= self.id_end_object:
            self.ShowMsgBox("Start id should larger than End id.")
            return
        self.extent = (self.x_min, 0, self.x_max, self.id_end_object - self.id_start_object + 1)
        self.reInitBuffer = True
    
    def OnClickPrevious(self, event):
        self.id_start_object -= self.num_objects_per_page
        if self.id_start_object < 0:
            self.id_start_object = 1
            
        self.id_end_object =  self.id_start_object + self.num_objects_per_page -1
        if self.id_end_object > self.n:
            self.id_end_object = self.n
        # update controls
        self.txt_from.SetValue(str(self.id_start_object))
        self.txt_to.SetValue(str(self.id_end_object))
        # toggle Prev/Next buttons
        if self.id_start_object == 1:
            self.btn_previous.Disable()
            self.btn_next.Enable()
        if self.id_end_object - self.id_start_object < self.num_objects_per_page -1:
            self.btn_next.Disable()
        else:
            self.btn_next.Enable()
            
        self.selected_obj_ids = []
        self.extent = (self.x_min, 0, self.x_max, self.num_objects_per_page)
        self.reInitBuffer = True
    
    def OnClickNext(self, event):
        self.id_start_object +=  self.num_objects_per_page 
        
        self.id_end_object = self.id_start_object + self.num_objects_per_page - 1
        self.id_end_object = self.n if self.n < self.id_end_object else self.id_end_object

        # update controls in toolbar
        self.txt_from.SetValue(str(self.id_start_object))
        self.txt_to.SetValue( str(self.id_end_object))
        # toggle Prev/Next buttons
        if self.id_end_object - self.id_start_object < self.num_objects_per_page -1:
            self.btn_next.Disable()
        if self.id_start_object == 1:
            self.btn_previous.Disable()
        else:
            self.btn_previous.Enable()
            
        self.selected_obj_ids = []
        self.extent = (self.x_min, 0, self.x_max, self.num_objects_per_page)
        self.reInitBuffer = True
    
    def plot_data(self,dc):
        color_group =[
            stars.LISA_NOT_SIG_COLOR, 
            stars.LISA_HH_COLOR,
            stars.LISA_LH_COLOR, 
            stars.LISA_LL_COLOR,
            stars.LISA_HL_COLOR, 
            stars.LISA_OBSOLETE_COLOR
            ]
        dc.SetFont(wx.Font(8,wx.ROMAN,wx.NORMAL,wx.NORMAL))
        
        n = len(self.moran_locals) # number of time intervals
       
        # selected/highlted shape objects
        self.highlighted_shape_objects = \
            [i-1 for i in self.selected_obj_ids] \
            if len(self.selected_obj_ids) > 0 \
            else range(self.id_start_object-1, self.id_end_object)
        
        y_max = len(self.highlighted_shape_objects) +1
        
        # draw grid  for current objects
        for count,i in enumerate(self.highlighted_shape_objects):
            #i = i-1
            for j in range(n):
                local_moran = self.moran_locals[j]
                local_moran_p_sim = np.array(local_moran[1])
                if local_moran_p_sim[i] <= 0.05:
                    item = self.cs_data_dict[i][j] if j < n-1 else self.cs_data_dict[i][j-1]
                    q1 = (item-1) % 4 + 1
                    q2 = (item-1) / 4 + 1
                    lisa_idx = q1 if j < n-1 else q2
                else:
                    lisa_idx = 0
   
                # draw cells
                start_x, start_y = self.point_to_screen(self.x_min + j, y_max -count)
                w, h = self.length_to_screen(1), math.ceil(self.length_to_screen(1,axis=1))
                h = h if h>4 else 4
                pen = wx.WHITE_PEN if len(self.highlighted_shape_objects)< 50 else wx.TRANSPARENT_PEN
                brush = wx.Brush(color_group[lisa_idx], wx.SOLID)
                dc.SetPen(pen)
                dc.SetBrush(brush)
                dc.DrawRectangle(start_x,start_y,w,h)
                
        # highlight significant object
        for count,i in enumerate(self.highlighted_shape_objects):
            for j in range(n):
                if self.cs_data_dict[i][-1] >0:
                    start_x, start_y = self.point_to_screen(self.x_min + 0, y_max -count)
                    w, h = self.length_to_screen(n), self.length_to_screen(1,axis=1)
                    pen = wx.Pen(wx.GREEN,3)
                    brush = wx.TRANSPARENT_BRUSH
                    dc.SetPen(pen)
                    dc.SetBrush(brush)
                    dc.DrawRectangle(start_x,start_y,w,h)
        
        # draw labels
        w, h = self.length_to_screen(1), math.ceil(self.length_to_screen(1,axis=1))
        h = h if h>4 else 4
        for i in range(n):
            lisa_type_list = self.moran_locals[i][-1]
            
            # for objects
            for count,j in enumerate(self.highlighted_shape_objects):
                item = lisa_type_list[j]
                start_x, start_y = self.point_to_screen(self.x_min + i, y_max -count)
                pen = wx.WHITE_PEN if len(self.highlighted_shape_objects)< 50 else wx.TRANSPARENT_PEN
                # draw labels (x,y)
                if i == 0:
                    start_x -= 20 # pixels for label
                    dc.DrawText('%4d'%(j), start_x, start_y)
                if count == 0:
                    # draw x label
                    x_label = '%s-%s'%(self.interval_labels[i][0],self.interval_labels[i][1])
                    txt_w, txt_h = dc.GetTextExtent(x_label)
                    _start_x = start_x +  (w-txt_w)/2 # pixels for tx 
                    _start_y = self.margin_top + self.ax_height #h*y_max + 45 if y_max > 16 else h*15 + 45
                    dc.DrawText(x_label,_start_x, _start_y)
        self.y_max = 16
        self.Refresh(False)
        
    def draw_selected(self,dc=None):
        y_max = len(self.selected_obj_ids)
        n_items = len(self.highlighted_shape_objects)
        
        if len(self.selected_obj_ids) > 0:
            if dc == None:
                # draw selected on client DC
                dc = wx.ClientDC(self)
                dc.DrawBitmap(self.buffer,0,0)
            for count,i in enumerate(self.selected_obj_ids):
                data = self.cs_data_dict[i]
                n = len(self.moran_locals)
                j = self.tick
                # 
                start_x, start_y = self.point_to_screen(
                    self.x_min + j, 
                    n_items - self.highlighted_shape_objects.index(i) + 1
                )
                w, h = self.length_to_screen(n), self.length_to_screen(1,axis=1)
                pen = wx.Pen(wx.BLACK,1)
                brush = wx.TRANSPARENT_BRUSH
                dc.SetPen(pen)
                dc.SetBrush(brush)
                dc.DrawRectangle(start_x,start_y,w,h)
        else:
            # un-highlight drawed line
            dc = wx.ClientDC(self)
            dc.DrawBitmap(self.buffer,0,0)
            #dc.Destroy()
            
    def draw_selected_by_region(self, dc, region, isScreenCoordinates=True):
        """
        this function highlight the points selected 
        by mouse drawing a region
        """
        select_region = region
        self.selected_obj_ids= []
        
        x0,y0,x1,y1= select_region
        x0,y0 = self.view.pan_to(x0,y0,-self.margin_left,-self.margin_top)
        x1,y1 = self.view.pan_to(x1,y1,-self.margin_left,-self.margin_top)
        x0,y0 = self.view.pixel_to_view(x0,y0)
        x1,y1 = self.view.pixel_to_view(x1,y1)
        y0,y1 = y0-1,y1-1
        
        self.selected_obj_ids = []
        
        n_items = len(self.highlighted_shape_objects)
        if (x0 < 0 and x1 < 0) or (x0 > self.t and x1 > self.t) \
           or (y1 < 0 and y0 < 0) or (y0 > n_items and y1 > n_items):
            # not in boundary
            pass
        else:
            # in boundary
            start = int(n_items - math.ceil(y0))
            end = int(n_items - math.ceil(y1))
            start = start if start >= 0 else 0
            end = end if end < n_items else n_items-1
            for i in range(start,end+1):
                self.selected_obj_ids.append(self.highlighted_shape_objects[i])
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
        
    def updateDraw(self):
        if not self.view:
            return
        
        self.extent = (self.x_min, 0, self.x_max, len(self.selected_obj_ids))
        self.reInitBuffer = True
       
        
    def OnObjsSelected(self,event):
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
        for layer_name, selected_object_ids in data.shape_ids.iteritems():
            if layer_name == self.layer_name and len(selected_object_ids) > 0:
                # directly select by shape_ids
                self.selected_obj_ids = selected_object_ids
                self.selected_obj_ids = [i+1 for i in self.selected_obj_ids]
                
                # update drawing based on selected objects
                n = len(self.selected_obj_ids)
                self.y_max = n if n >=15 else 15
                self.extent = (self.x_min, 0, self.x_max,self.y_max)
                self.reInitBuffer = True
                return
            
    def OnNoObjSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        Normally, event could be None, you just need to clean and refresh
        you selected/highlighted
        """
        self.selected_obj_ids = []
        self.extent = (self.x_min, 0, self.x_max, self.num_objects_per_page)
        self.reInitBuffer = True
        
# -------------------------------------------------
# old 16 default color schema for MarkovLISA
# delete at version 162
# -------------------------------------------------
       
class LISAMarkovQueryDialog(DynamicLISAQueryDialog):
    """
    Query Dialog for generating Markov LISA Maps
    """
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
            self.ShowMsgBox("Markov LISA requires at lest 2 intervals of dataset, please reselect step-by parameters.")
            return
        # LISA layer (only one)
        lisa_layer = [self.background_shps[self.background_shp_idx]]
        markov_lisa_widget = DynamicMapWidget(
            self.parent,
            lisa_layer,
            LISAMarkovMap,
            weight=self.weight_path,
            query_data=self.query_data,
            size=(800,650),
            start= self._wxdate2pydate(self.itv_start_date.GetValue()),
            end= self._wxdate2pydate(self.itv_end_date.GetValue()),
            step_by=self.step_by,
            step=self.step)
        markov_lisa_widget.Show()
       
        # (enable) save LISA Markov to new shp/dbf files
        self.btn_save.Enable(True)
        self.lisa_layer = lisa_layer[0]
        self.lisa_markov_map = markov_lisa_widget.canvas
        
        
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
            
            self.ShowMsgBox("Query results have been saved into new dbf file",
                            mtype='CAST Information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Save query results to new dbf file failed! Please check if the new dbf file is already existed.")
 
            
    