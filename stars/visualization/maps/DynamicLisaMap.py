"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["DynamicLISAMap","DynamicLISAQueryDialog", "ShowDynamicLISAMap"]

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


class DynamicLISAMap(ShapeMap):
    """
    Dynamic/Animated LISA Maps. 
    
    Parameters
    ----------
    
    layers         : array (n,1)
                     n SHAPE layers, the first one should be the used for generating LISA    
                     
    cs_data_dict   : dict (time_range:data)
                     crosssectional data dictionary
                     
    weight_file    : string
                     weight file path
    
    """
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

            self.t = len(self.cs_data_dict)
            self.data_sel_keys = sorted(self.cs_data_dict.keys())
            self.data_sel_values = [self.cs_data_dict[i] for i in self.data_sel_keys]
            self.weight = pysal.open(self.weight_file).read()
       
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.extent = self.layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight - self.bufferHeight/3.0
                ) 
           
            # strip map
            self.tick = 0
            self.bStrip = True
            self.nav_left = None
            self.nav_right = None
           
            self.bAnimate = False
            
            # setup dynamic control buttons
            self.SetTitle('Dynamic LISA - %s %s'% (self.layer.name,kwargs["title"]))
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.t, self.step, self.step_by)
            self.setupDynamicControls()
            
            # preprocess multi LISA maps
            self.processLISAMaps()
            
            # inital drawing lisa map
            self.updateDraw(0)
            
            # Thread-based controller for dynamic LISA
            self.dynamic_control = DynamicMapControl(self.parentFrame,self.t,self.updateDraw) 
            
        except Exception as err:
            self.ShowMsgBox("""Dynamic LISA map could not be created. Please choose or create a valid spatial weights file.
            
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
            
    def processLISAMaps(self):
        """
        Create LISA maps for each interval data
        """
        try:
            # precomputing LISA maps
            n = len(self.data_sel_keys)
            progress_dlg = wx.ProgressDialog(
                "Progress",
                "Computing LISA with 499 permutations...               ",
                maximum = n,
                parent=self,
                style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
            )
            progress_dlg.CenterOnScreen()
            
            from stars.core.LISAWrapper import call_lisa
            self.moran_locals = []
            for i, data in enumerate(self.data_sel_values):
                progress_dlg.Update(i+1)
                localMoran, sigLocalMoran, sigFlag, clusterFlag = call_lisa(
                    data,
                    str(self.weight_file),
                    499
                )
                ml = [localMoran, sigLocalMoran, sigFlag, clusterFlag]
                self.moran_locals.append(ml)
            progress_dlg.Destroy()
            
            # default color schema for LISA
            color_group =[
                stars.LISA_NOT_SIG_COLOR, 
                stars.LISA_HH_COLOR,
                stars.LISA_LL_COLOR, 
                stars.LISA_LH_COLOR,
                stars.LISA_HL_COLOR, 
                stars.LISA_OBSOLETE_COLOR]
            self.lisa_color_group = color_group
            label_group = ["Not Significant","High-High","Low-Low","Low-High","High-Low","Neighborless"]
            self.color_schema_dict[self.layer.name] = ColorSchema(self.lisa_color_group,label_group)

        except:
            raise Exception("Compute LISA error. Please check weight file.")
        
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
           
        self.bAnimate = False
        self.reInitBuffer = True
        
    def remove_layer(self,layer, isRemoveContent=True):
        # support Toolbar REMOVE_LAYER button
        #if self.fixed_layer:
        
        if layer.name == self.layer.name:
            self.ShowMsgBox("Can't remove original LISA layer.")
            return False
        
        super(DynamicLISAMap, self).remove_layer(layer, isRemoveContent)
        
            
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
        ml = self.moran_locals[tick]
        
        # 0 not significant, 1 HH, 2 LL, 3 LH, 4 HL, 5 Neighborless
        sigFlag = ml[2]
        clusterFlag = ml[3]
        lm_sig = np.array(sigFlag)
        lm_q = np.array(clusterFlag)
       
        id_groups = [[] for i in range(6)]
        for i,sig in enumerate(lm_sig):
            if sig > 0:
                id_groups[lm_q[i]].append(i)
            else:
                id_groups[0].append(i)
             
        self.draw_layers[self.layer].set_data_group(id_groups)
        self.draw_layers[self.layer].set_fill_color_group(self.lisa_color_group)
        
        edge_clr = self.color_schema_dict[self.layer.name].edge_color
        self.draw_layers[self.layer].set_edge_color(edge_clr)
   
        # trigger to draw 
        self.reInitBuffer = True
        self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)' % (tick+1,self.step, self.step_by))
        
    def DoDraw(self, dc):
        super(DynamicLISAMap, self).DoDraw(dc)
       
        if self.bStrip:
            if not self.bAnimate:
                #self.drawStripView(dc)
                self.stripBuffer = self.drawStrip()
            start_offset = -self.stripBmpFrameWidth * self.tick 
            dc.DrawBitmap(self.stripBuffer,start_offset, self.bufferHeight/1.5)
            self.drawHighlightSubview(dc)
            
    def drawHighlightSubview(self, dc):
        # draw red highlight box
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.RED_PEN)
        dc.DrawRectangle(
            self.middleBmpPos[0], 
            self.middleBmpPos[1], 
            int(math.ceil(self.stripBmpWidth)), 
            self.stripBmpHeight) 
            
    def drawStrip(self):
        n_stripBmps = len(self.data_sel_keys)
        stripFramePos = 0, self.bufferHeight * 2.0/3.0
        stripFrameHeight = self.bufferHeight / 3.0
        stripBmpHeight = stripFrameHeight * 0.8
        
        stripBmpWidth = stripBmpHeight * 0.8
        stripBmpGap = stripFrameHeight * 0.1
        stripBmpFrameWidth = stripBmpWidth + 2*stripBmpGap
        
        stripFrameMarginLR = (self.bufferWidth - stripBmpWidth)/ 2.0 - stripBmpGap
        stripFrameWidth = stripBmpFrameWidth * n_stripBmps  + stripFrameMarginLR * 2
        
        if stripFrameWidth < self.bufferWidth:
            stripFrameWidth = self.bufferWidth
           
        self.nav_left = stripFramePos[0], stripFramePos[1], \
            stripFramePos[0] + self.bufferWidth/ 2.0, \
            stripFramePos[1] + stripFrameHeight
        self.nav_right = stripFramePos[0] + self.bufferWidth/ 2.0, stripFramePos[1], \
            stripFramePos[0] + self.bufferWidth, \
            stripFramePos[1] + stripFrameHeight
        self.stripBmpFrameWidth = stripBmpFrameWidth
        self.stripBmpWidth = stripBmpWidth
        self.stripBmpHeight = stripBmpHeight
        self.stripFrameWidth = stripFrameWidth
        self.stripFrameHeight = stripFrameHeight
        self.stripFramePos = stripFramePos
        self.stripFrameMarginLR = stripFrameMarginLR
        self.middleBmpPos = stripFrameMarginLR + stripBmpGap, stripFramePos[1] + stripBmpGap 
        
        stripBuffer = wx.EmptyBitmap(stripFrameWidth, stripFrameHeight)
        tmp_dc = wx.BufferedDC(None, stripBuffer)
        
        # draw light gray background first
        pen = wx.Pen(stars.STRIP_VIEW_BG_COLOR)
        tmp_dc.SetPen(pen)
        brush = wx.Brush(stars.STRIP_VIEW_BG_COLOR)
        tmp_dc.SetBrush(brush)
        tmp_dc.DrawRectangle(0,0,stripFrameWidth,stripFrameHeight)
        
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        tmp_dc.SetFont(font)
        
        # draw each bmp at strip area
        tmp_dc.SetBrush(wx.Brush(stars.STRIP_VIEW_MAP_BG_COLOR))
        for i in range(n_stripBmps):
            start_pos = stripFrameMarginLR + stripBmpFrameWidth * i + stripBmpGap, stripBmpGap
            bmp = wx.EmptyBitmapRGBA(
                stripBmpWidth, stripBmpHeight,
                red = stars.STRIP_VIEW_BG_COLOR.red,
                green = stars.STRIP_VIEW_BG_COLOR.green,
                blue = stars.STRIP_VIEW_BG_COLOR.blue,
                alpha = stars.STRIP_VIEW_BG_COLOR.alpha
            )
            self.drawSubView(i,stripBmpWidth, stripBmpHeight, bmp)
            tmp_dc.SetBrush(wx.WHITE_BRUSH)
            tmp_dc.SetPen(wx.TRANSPARENT_PEN)
            tmp_dc.DrawRectangle(start_pos[0], start_pos[1], stripBmpWidth, stripBmpHeight)
            tmp_dc.DrawBitmap(bmp, start_pos[0], start_pos[1])
                
            # draw label for each map in subview
            start_date, end_date = self.datetime_intervals[i]
            if isinstance(start_date, datetime.date):
                info_tip = "%d/%d/%d - %d/%d/%d"% \
                         (start_date.month,
                          start_date.day,
                          start_date.year,
                          end_date.month, 
                          end_date.day, 
                          end_date.year)
            else:
                info_tip = "t%d" % (start_date)
            txt_w,txt_h = tmp_dc.GetTextExtent(info_tip)
            tmp_dc.DrawText(
                info_tip, 
                start_pos[0]+(stripBmpWidth-txt_w)/2, 
                start_pos[1]+stripBmpHeight+2)
        #tmp_dc.Destroy()
        
        return stripBuffer
     
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
            """
                # prepare DC for brushing drawing 
                tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
                tmp_dc = wx.BufferedDC(None, tmp_buffer)
                delta_px = -x0 + x 
                delta_py = -y0 + y
                tmp_dc.DrawBitmap(self.drawing_backup_buffer,delta_px,delta_py)
                if self.bStrip :
                    start_offset = -self.stripBmpFrameWidth * self.tick 
                    tmp_dc.DrawBitmap(self.stripBuffer,start_offset, self.bufferHeight/1.5)
                    self.drawHighlightSubview(tmp_dc)
                self.buffer = tmp_buffer
                self.Refresh(False)
                #tmp_dc.Destroy()
                return
            """
                
        # give the rest task to super class
        super(DynamicLISAMap,self).OnMotion(event)
        
    def drawStripView(self,dc):
        n = len(self.data_sel_keys)
        if n <= 1:
            return
        
        # put the current self.tick in the middle 
        if self.tick == 0:
            start = self.tick
        elif 1<= self.tick < n-1:
            start = self.tick -1
        else:
            start = self.tick -2
            
        # flag for drawing navigation arrow
        b2LeftArrow = False
        b2RightArrow = False
        
        if self.tick > 0:
            b2LeftArrow = True
        if self.tick < n-1:
            b2RightArrow = True
           
        # only display 3 maps on strip
        if n > 3: n = 3
        
        # at area: 0,self.bufferHeight * 2/3.0
        # draw a light gray area at the bottom first
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)
        brush = wx.Brush(stars.STRIP_VIEW_BG_COLOR)
        dc.SetBrush(brush)
        framePos = 0, self.bufferHeight * 2.0/3.0
        dc.DrawRectangle(framePos[0],framePos[1], self.bufferWidth, self.bufferHeight/3.0)
        # calculate width and height for each bmp
        bmpFrameWidth = self.bufferWidth / float(n)
        bmpFrameHeight = self.bufferHeight / 3.0
        bmpWidth = bmpFrameWidth * 0.7
        bmpHeight = bmpFrameHeight * 0.8
        bmpOffsetX = (bmpFrameWidth - bmpWidth )/2.0 
        bmpOffsetY = (bmpFrameHeight- bmpHeight)/2.0 
       
        # draw each bmp at strip area
        dc.SetBrush(wx.Brush(stars.STRIP_VIEW_MAP_BG_COLOR))
        end = self.t if start + 3 > self.t else start+3
        for i in range(start, end):
            start_pos = bmpFrameWidth * (i-start) + bmpOffsetX , framePos[1]+bmpOffsetY 
            bmp = wx.EmptyBitmapRGBA(
                bmpFrameWidth, bmpFrameHeight,
                red = stars.STRIP_VIEW_BG_COLOR.red,
                green = stars.STRIP_VIEW_BG_COLOR.green,
                blue = stars.STRIP_VIEW_BG_COLOR.blue,
                alpha = stars.STRIP_VIEW_BG_COLOR.alpha)
            self.drawSubView(i,bmpWidth, bmpHeight, bmp)

            dc.SetBrush(wx.WHITE_BRUSH)
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle( start_pos[0], start_pos[1], bmpWidth, bmpHeight)
            dc.DrawBitmap(bmp, start_pos[0], start_pos[1])
               
            # draw red highlight box
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self.tick == i:
                dc.SetPen(wx.RED_PEN)
            else:
                dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle( start_pos[0], start_pos[1], bmpWidth, bmpHeight)
                
            # draw label for each map in subview
            start_date, end_date = self.datetime_intervals[i]
            if isinstance(start_date, datetime.date):
                info_tip = "%d/%d/%d - %d/%d/%d"% \
                         (start_date.month,
                          start_date.day,
                          start_date.year,
                          end_date.month, 
                          end_date.day, 
                          end_date.year
                          )
            else:
                info_tip = "t%d" % (start_date)
            txt_w,txt_h = dc.GetTextExtent(info_tip)
            dc.DrawText(info_tip, start_pos[0] + (bmpWidth - txt_w)/2, start_pos[1]+bmpHeight+2)
            
        # draw navigation arrows
        arrow_y = framePos[1] + bmpFrameHeight/2.0
        
        dc.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL))
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
            
        #self.Refresh(False)
                      
    def drawSubView(self, lisa_idx, bufferWidth, bufferHeight,bmp):
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
        
        ml = self.moran_locals[lisa_idx]
        # 0 not significant, 1 HH, 2 LL, 3 LH, 4 HL, 5 Neighborless
        sigFlag = ml[2]
        clusterFlag = ml[3]
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
        #edge_clr = wx.WHITE#wx.Colour(200,200,200, self.opaque)
        edge_clr = self.color_schema_dict[self.layer.name].edge_color
        draw_layer.set_edge_color(edge_clr)
        draw_layer.set_data_group(id_groups)
        draw_layer.set_fill_color_group(self.lisa_color_group)
        draw_layer.draw(dc, view)
        
        
    def enableStripView(self, event):
        self.bStrip = not self.bStrip
        if self.bStrip == False:
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight
                )
        else:
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight - self.bufferHeight/3.0
                )
        self.reInitBuffer = True

    def OnLeftDown(self, event):
        """ override for click on strip view """
        if self.bStrip:
            mouse_end_x, mouse_end_y = (event.GetX(), event.GetY())
            # check for left
            if self.nav_left:
                if self.nav_left[0] <= mouse_end_x <= self.nav_left[2] and \
                   self.nav_left[1] <= mouse_end_y <= self.nav_left[3]:
                    self.stopAnimation = True
                    return
            # determine for right 
            if self.nav_right:
                if self.nav_right[0] <= mouse_end_x <= self.nav_right[2] and \
                   self.nav_right[1] <= mouse_end_y <= self.nav_right[3]:
                    self.stopAnimation = True
                    return
        # give the rest task to super class
        super(DynamicLISAMap,self).OnLeftDown(event)
        
    def OnLeftUp(self, event):
        """ override for click on strip view """
        if self.bStrip:
            mouse_end_x, mouse_end_y = (event.GetX(), event.GetY())
            # check for left
            t = 20
            acc = self.stripBmpFrameWidth * 2 / (t**2)
            if self.nav_left:
                if self.nav_left[0] <= mouse_end_x <= self.nav_left[2] and \
                   self.nav_left[1] <= mouse_end_y <= self.nav_left[3]:
                    self.stopAnimation = False
                    start_offset = -self.stripBmpFrameWidth * self.tick 
                    if self.tick < self.t-1:
                        self.tick = self.tick + 1
                        self.animateStripView(acc, start_offset)
                    else:
                        self.animateStripView(acc, start_offset,isEnd=True)
            # determine for right 
            if self.nav_right:
                if self.nav_right[0] <= mouse_end_x <= self.nav_right[2] and \
                   self.nav_right[1] <= mouse_end_y <= self.nav_right[3]:
                    self.stopAnimation = False
                    start_offset = -self.stripBmpFrameWidth * self.tick 
                    if self.tick>0:
                        self.tick = self.tick -1
                        self.animateStripView(acc, start_offset, isLeft=False)
                    else:
                        self.animateStripView(acc, start_offset, isLeft=False, isEnd=True)
            
        # give the rest task to super class
        super(DynamicLISAMap,self).OnLeftUp(event)
        
    def animateStripView(self, acc, start_offset, isLeft=True, t=1,isEnd=False):
        """
        """
        if t > 20:
            self.bAnimate = True
            self.updateDraw(self.tick)
        if t <= 20 and self.stopAnimation == False:
            if isEnd == False:
                offset = acc*20*t - acc * (t**2) / 2.0
            else:
                offset = acc*10*t - acc * (t**2) / 2.0
                
            if isLeft: offset = -offset
            offset = start_offset + offset
            
            tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
            tmp_dc = wx.BufferedDC(None, tmp_buffer)
            tmp_dc.DrawBitmap(self.drawing_backup_buffer,0,0)
            pen = wx.Pen(stars.STRIP_VIEW_BG_COLOR)
            tmp_dc.SetPen(pen)
            brush = wx.Brush(stars.STRIP_VIEW_BG_COLOR)
            tmp_dc.SetBrush(brush)
            tmp_dc.DrawRectangle(
                self.stripFramePos[0],
                self.stripFramePos[1],
                self.stripFrameWidth,
                self.stripFrameHeight
                )
            tmp_dc.DrawBitmap(self.stripBuffer, offset, self.bufferHeight/1.5)
            self.drawHighlightSubview(tmp_dc)
            self.buffer = tmp_buffer
            #tmp_dc.Destroy()
            self.Refresh(False)
          
            t = t + 1
            if self.stopAnimation == False:
                wx.FutureCall(10, self.animateStripView, acc, start_offset, isLeft,t,isEnd) 
        #tmp_dc.DrawBitmap(self.stripBuffer, offset_dist, self.bufferHeight/1.5)
        
    def OnRightUp(self,event):
        menu = wx.Menu()
        menu.Append(201, "Show/Hide strip view", "")
        menu.Append(210, "Select Neighbors", "")
        menu.Append(211, "Cancel Select Neighbors", "")
        
        menu.UpdateUI()
        menu.Bind(wx.EVT_MENU, self.enableStripView, id=201)
        menu.Bind(wx.EVT_MENU, self.select_by_weights, id=210)
        menu.Bind(wx.EVT_MENU, self.cancel_select_by_weights, id=211)
        self.PopupMenu(menu)
        
        event.Skip() 
        
    def ExportMovie(self,path,duration=3):
        from stars.visualization.utils.images2gif import writeGif,writeBmps2Gif
        
        if isinstance(self.start_date, datetime.date):
            Y,M,D = self.start_date.year, self.start_date.month, self.start_date.day # python.DateTime
            start_date = wx.DateTime.Today()
            start_date.Year,start_date.Month, start_date.Day = Y,M,D
        else:
            # 1,2,3..., n time step
            start_date = self.start_date 
        
        tick = self.tick
        movie_bmps = []
        for i in range(self.t):
            self.tick = i
            tmp_bmp = wx.EmptyBitmapRGBA(self.bufferWidth, self.bufferHeight,255,255,255,255)
            dc = wx.MemoryDC()
            dc.SelectObject(tmp_bmp)
            self.updateDraw(i)
            self.DoDraw(dc)
            
            # draw lables
            if isinstance(self.start_date, datetime.date):
                if i < self.t -1:
                    end_date = wx.DateTime.Today()
                    end_date.Set(start_date.Day, start_date.Month, start_date.Year)
               
                    if self.step_by == 'Day':
                        end_date += wx.DateSpan(days=self.step)
                    elif self.step_by == 'Month':
                        end_date += wx.DateSpan(months=self.step)
                    elif self.step_by == 'Year':
                        end_date += wx.DateSpan(years=self.step)
                        
                    label = '(%d/%d) %s/%s/%s - %s/%s/%s (%s %s period)' % \
                          (i+1,self.t, start_date.Month,start_date.Day,start_date.Year,
                           end_date.Month,  end_date.Day, end_date.Year,self.step, self.step_by
                           )
                    start_date.Year,start_date.Day = end_date.Year, end_date.Day
                    start_date.SetMonth( end_date.Month)
                else:
                    label = '(%d/%d) %s/%s/%s - %s/%s/%s (%s %s period)' % \
                          (i+1,self.t, start_date.Month,start_date.Day,start_date.Year,
                           self.end_date.month,  self.end_date.day,  self.end_date.year,self.step, self.step_by
                           )
            else:
                # 1,2,3....n time step, not datetime
                end_date = start_date + 1
                label = '(%d/%d) step: %d (%s %s period)' % (i+1, self.t, start_date, self.step, self.step_by)
                start_date = end_date
                      
            dc.DrawText(label, 5,5)
            #dc.Destroy()
            movie_bmps.append(tmp_bmp)
        writeBmps2Gif(path,movie_bmps, duration=duration, dither=0)
        self.tick = tick
        self.ShowMsgBox("Movie file (GIF) created successfully.",
                        mtype='CAST information',
                        micon=wx.ICON_INFORMATION)
    
class DynamicLISAQueryDialog(SpaceTimeQueryDialog):
    """
    Query Dialog for generating dynamic LISA Maps
    """
    def Add_Customized_Controls(self):
        x2,y2 = 20, 350
        wx.StaticBox(self.panel, -1, "LISA setting:",pos=(x2,y2),size=(325,70))
        wx.StaticText(self.panel, -1, "Weights file:",pos =(x2+10,y2+30),size=(90,-1))
        self.txt_weight_path = wx.TextCtrl(self.panel, -1, "",pos=(x2+100,y2+30), size=(180,-1) )
        #open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        open_bmp = wx.BitmapFromImage(stars.OPEN_ICON_IMG)
        self.btn_weight_path = wx.BitmapButton(self.panel,-1, open_bmp, pos=(x2+292,y2+32), style=wx.NO_BORDER)
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
            None, message="Choose a file", 
            wildcard="Weights file (*.gal,*.gwt)|*.gwt;*.gal|All files (*.*)|*.*",
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
            self.ShowMsgBox("Space should be a POLYGON layer.")
            return
        
        self.lisa_layer = lisa_layer
        lisa_data_dict = self.gen_date_by_step()
        self.query_data = lisa_data_dict
        
        if self.query_data == None:
            self.ShowMsgBox("Query dynamic data by STEP error.")
            return
        
        title = ""
        if self.query_field.lower() != "all fields":
            title = "(%s:%s)"%(self.query_field,self.query_range)
            
        # check the extent of LISA layer and Points layer
        """
        for lisa_data in lisa_data_dict.values(): 
            if sum(lisa_data) == 0:
                self.ShowMsgBox("No records found inside the space area, please check if the space and points are in same extent.")
                return
        """
        dynamic_lisa_widget= DynamicMapWidget(
            self.parent, [lisa_layer], DynamicLISAMap,
            weight = self.weight_path,
            data = lisa_data_dict,
            start=self.start_date,
            end=self.end_date,
            step_by=self.step_by,
            step=self.step,
            size =(800,650),
            title = title
            )
        dynamic_lisa_widget.Show()
        
        self.btn_save.Enable(True)
        
    def gen_date_by_step(self):
        """
        generate dynamic LISA map data by STEP
        """
        from stars.visualization.utils import GetIntervalStep
        
        step = self.step
        step_by = self.step_by
        background_shp_idx = self.background_shp_idx    
        background_shp = self.background_shps[background_shp_idx]
        
        if background_shp.shape_type != stars.SHP_POLYGON:
            self.ShowMsgBox("Background shape file should be POLYGON!")
            return None
        
        if not pysal.cg.standalone.bbcommon(background_shp.extent, self.points_data.extent):
            self.ShowMsgBox("Mismatch of spatial extent of points and polygon shapefiles.")
            return None
        
        start_date = self._wxdate2pydate(self.itv_start_date.GetValue())
        end_date   = self._wxdate2pydate(self.itv_end_date.GetValue())
        total_steps = GetIntervalStep(end_date, start_date, step, step_by)
        if total_steps <= 0:
            self.ShowMsgBox("Start and end dates are not correct.")
            return None
        elif total_steps == 1:
            self.ShowMsgBox("Total # of steps should be larger than 1.")
            return None
        elif total_steps > 48:
            dlg = wx.MessageDialog(
                self,
                "Total # of steps is %s, it may take a lot of memory and time. Do you want to continue?"%total_steps,
                "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION
                )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_OK:
                self.Destroy()
                return None
            self.Destroy()
            
        self.start_date = start_date
        self.end_date = end_date
        
        return_data_dict = dict([(i,np.zeros(len(background_shp))) for i in range(total_steps)]) 
        
        # create a kd-tree from centroids of lisa_shp
        n = len(self.current_selected)
        itv = n/5
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Space-time query for dynamic maps..               ",
            maximum = n,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        progress_dlg.CenterOnScreen()

        
        # check which point is in which polygon
        bmp,view,poly_color_dict = self.draw_space_in_buffer(background_shp)
        not_sure_points = []
        is_valid_query = False
        
        for count,j in enumerate(self.current_selected):
            if count % itv == 0:
                progress_dlg.Update(count +1)
                
            _date = self.all_dates[j]
            interval_idx = GetIntervalStep(_date, start_date, step, step_by)-1
            
            p = self.points[j]
            x,y = view.view_to_pixel(p[0],p[1])
            x,y = int(round(x)), int(round(y))
           
            if x<0 or y < 0 or x >= bmp.Width or y >= bmp.Height:
                continue
            
            r = bmp.GetRed(x,y)
            g = bmp.GetGreen(x,y)
            b = bmp.GetBlue(x,y)
            
            if r==255 and g==255 and b==255:
                continue
            
            if (r,g,b) in poly_color_dict:
                poly_id = poly_color_dict[(r,g,b)]
                poly_id_cnt = 0
                for offset_x in range(-1,2):
                    for offset_y in range(-1,2):
                        n_x = x + offset_x
                        n_y = y + offset_y
                        if n_x < 0 or n_y < 0 or n_x >= bmp.Width or n_y >= bmp.Height:
                            continue
                        n_r = bmp.GetRed(n_x,n_y)
                        n_g = bmp.GetGreen(n_x,n_y)
                        n_b = bmp.GetBlue(n_x,n_y)
                        if n_r==r and n_g==g and n_b==b:
                            poly_id_cnt += 1
                if poly_id_cnt > 3:
                    return_data_dict[interval_idx][poly_id] += 1
                    is_valid_query = True
                else:
                    # this case, the color of border line of severl polygons
                    # accidentally equals to an existing color code
                    not_sure_points.append(j)
                
            else:
                # check if this pixel is sitting on the boarder line
                # pick up the color code, in the case that this is 
                # the boarder line of only one polygon
                candidate_color = None
                candidate_color_cnt = 0
                for offset_x in range(-1,2):
                    for offset_y in range(-1,2):
                        n_x = x + offset_x
                        n_y = y + offset_y
                        if n_x < 0 or n_y < 0 or n_x >= bmp.Width or n_y >= bmp.Height:
                            continue
                        n_r = bmp.GetRed(n_x,n_y)
                        n_g = bmp.GetGreen(n_x,n_y)
                        n_b = bmp.GetBlue(n_x,n_y)
                       
                        local_color = (n_r,n_g,n_b)
                        if poly_color_dict.has_key(local_color):
                            candidate_color = local_color
                            candidate_color_cnt += 1
                        if candidate_color_cnt > 1:
                            break
                        
                if candidate_color_cnt == 1:
                    poly_id = poly_color_dict[candidate_color]
                    return_data_dict[interval_idx][poly_id] += 1
                    is_valid_query = True
                else:
                    not_sure_points.append(j)
                    
        
        if len(not_sure_points)>0:
            query_points = [self.points[i] for i in not_sure_points]
            poly_ids = background_shp.test_point_in_polygon(query_points)
            for i, pid in enumerate(not_sure_points):
                if poly_ids[i] >=0:
                    _date = self.all_dates[pid]
                    interval_idx = GetIntervalStep(_date, start_date, step, step_by)-1
                    return_data_dict[interval_idx][poly_ids[i]] += 1
                    is_valid_query = True
            
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
            self.ShowMsgBox("Query results have been saved to a new dbf file.",
                            mtype='CAST information',
                            micon=wx.ICON_INFORMATION)
        except:
            self.ShowMsgBox("Saving query results to new dbf file failed. Please check if the dbf file already exists.")
  
def ShowDynamicLISAMap(self):
    # self is Main.py
    if not self.shapefiles or len(self.shapefiles) < 1:
        return
    shp_list = [shp.name for shp in self.shapefiles]
    dlg = wx.SingleChoiceDialog(
        self, 'Select a POINT or Polygon(with time field) shape file:', 
        'Dynamic LISA Map', shp_list,wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.GetSelection()
        shp = self.shapefiles[idx]
        if shp.shape_type == stars.SHP_POINT:
            # create dynamic LISA from points
            d_lisa_dlg = DynamicLISAQueryDialog(
                self,"Dynamic LISA:" + shp.name,
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
                    wildcard="Weights file (*.gal,*.gwt)|*.gwt;*.gal|All files (*.*)|*.*",
                    style=wx.OPEN | wx.CHANGE_DIR
                )
                if wdlg.ShowModal() == wx.ID_OK:
                    weight_path = wdlg.GetPath()
                    # directly show Dynamic LISA Map
                    dynamic_lisa_widget= DynamicMapWidget(
                        self, [shp], DynamicLISAMap,
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
            self.ShowMsgBox("File type error. Should be a POINT shapefile.")
            dlg.Destroy()
            return
    dlg.Destroy()