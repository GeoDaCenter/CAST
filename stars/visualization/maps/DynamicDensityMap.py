"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['DynamicDensityMap','DynamicDensityMapQueryDialog']

import os,math, datetime
from multiprocessing import Process, Queue
import wx

import stars
from ShapeMap import GradientColorSchema,ShapeMap
from DensityMap import DensityMap, DensityMapQueryDialog
from stars.visualization.DynamicWidget import DynamicMapWidget
from stars.visualization.DynamicControl import DynamicMapControl
from stars.visualization.SpaceTimeQueryDialog import SpaceTimeQueryDialog   
from stars.visualization.utils import *

class DynamicDensityMap(DensityMap):
    """
    Canvas drawing dynamic density maps
    """
    def __init__(self, parent,  layers, **kwargs):
        DensityMap.__init__(self,parent, layers, **kwargs)
        
        try:
            self.start_date = kwargs["start"]
            self.end_date = kwargs["end"]
            self.step, self.step_by = kwargs["step"] ,kwargs["step_by"]
            self.density_data_dict  = kwargs["density_data_dict"]
            self.isAccumulative     = kwargs["isAccumulative"]
            
            self.data_sel_keys   = sorted(self.density_data_dict.keys())
            self.data_sel_values = [self.density_data_dict[i] for i in self.data_sel_keys]
            self.n = len(self.data_sel_values)
            self.tick = 0
          
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.extent = self.point_layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight - self.bufferHeight/3.0
                ) 
            
            # strip map
            self.bStrip = True
            self.nav_left = None
            self.nav_right = None
            self.stripBuffer = None
            self.bAnimate = False
            
            # setup dynamic control buttons
            self.datetime_intervals, self.interval_labels = GetDateTimeIntervals(self.start_date, self.end_date,self.n, self.step, self.step_by)
            self.setupDynamicControls()
            self.parentFrame.SetTitle('Dynamic Density Map-%s %s' % (self.point_layer.name,kwargs["title"]))
           
            self.gradient_color_max = stars.MAP_GRADIENT_COLOR_MAX
            self.gradient_color_min = stars.MAP_GRADIENT_COLOR_MIN
            
            # preload density maps
            self.createDensityMaps()
            
            # display first map 
            self.updateDraw(0)
            
            # Thread-based controller for dynamic LISA
            self.dynamic_control = DynamicMapControl(
                self.parentFrame,
                self.n,
                self.updateDraw
                )
        except Exception as err:
            self.ShowMsgBox("""Dynamic density map could not be created. Please choose/input valid parameters.""")
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
                self.parentWidget.label_start.SetLabel(
                    '%2d/%2d/%4d'% 
                    (self.start_date.day,
                     self.start_date.month,
                     self.start_date.year
                    )
                )
                self.parentWidget.label_end.SetLabel(
                    '%2d/%2d/%4d'% 
                    (self.end_date.day,
                     self.end_date.month,
                     self.end_date.year
                     )
                )
            else:
                self.parentWidget.label_start.SetLabel('%d'% self.start_date)
                self.parentWidget.label_end.SetLabel('%4d'% self.end_date)
            self.parentWidget.label_current.SetLabel('current: %d (%d-%s period)'%(1,self.step, self.step_by))
        except:
            raise Exception("Setup dynamic controls in toolbar failed!")
        
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
        super(DynamicDensityMap,self).OnMotion(event)

        
    def updateDraw(self, tick):
        """
        When SLIDER is dragged
        """
        self.tick = tick
        self.reInitBuffer = True
        
        self.parentWidget.label_current.SetLabel(
            'current: %d (%d-%s period)' % 
            (tick+1,self.step, self.step_by))
        
    def createDensityMap(self):
        """
        Override to avoid regular densitymap function
        """
        pass

    def createDensityMaps(self):
        """
        c++ version:
        create density maps for all interval points data
        """
        x = [] 
        y = []
        for pt in self.points:
            x.append(pt[0])
            y.append(pt[1])
        intervals = len(self.data_sel_values)
            
        from stars.core.DKDEWrapper import call_dkde
        
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Creating density maps...               ",
            maximum = 2,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
            )
        progress_dlg.CenterOnScreen()
        progress_dlg.Update(1)

        arrs,rows,cols,gmin,gmax = call_dkde(
            x,
            y,
            intervals,
            self.data_sel_values,
            self.extent,
            self.bandwidth,
            self.cell_size,
            self.kernel, 
            self.color_band, 
            self.opaque*2.55
        )
        
        progress_dlg.Update(2)
       
        self.grids = arrs
        self.gradient_color_max = gmax
        self.gradient_color_min = gmin
        
        self.density_bmps = []
        for grid in self.grids:
            bmp = wx.BitmapFromBufferRGBA(cols, rows, grid)
            self.density_bmps.append(bmp)
        
    def setup_bitmap(self):
        """
        bmp variables, in case of resize/pan/extent/zoom
        """
        left, lower, right, upper = self.extent
        self.bmp_left, self.bmp_upper  = self.view.view_to_pixel(left, upper)
        self.bmp_right, self.bmp_lower = self.view.view_to_pixel(right, lower)
        self.bmp_width = self.bmp_right - self.bmp_left
        self.bmp_height = self.bmp_lower - self.bmp_upper
        
    def drawDensityMaps(self,dc):
        density_bmp = self.density_bmps[self.tick]
        
        if self.isResizing:
            self.setup_bitmap()
           
            # resize the one displaying
            image = wx.ImageFromBitmap(density_bmp)
            image = image.Scale(self.bmp_width, self.bmp_height, wx.IMAGE_QUALITY_HIGH)
            density_bmp = wx.BitmapFromImage(image)
        
        # draw density map 
        dc.DrawBitmap(density_bmp, self.bmp_left,  self.bmp_upper)
        
        
    def DoDraw(self, dc):
        # draw background shape files once
        # when Density map is ready, draw it 
        
        # change color schema for every tick
        local_query_pts = self.data_sel_values[self.tick]
        if len(local_query_pts) < len(self.points):
            id_group = [local_query_pts]
            color_group = [self.color_schema_dict[self.point_layer.name].colors[0]]
            edge_color_group = [self.color_schema_dict[self.point_layer.name].edge_color]
           
            """
            non_query_points = list(set(range(len(self.points))) - set(local_query_pts))
            id_group.append(non_query_points)
            color_group.append(wx.Colour(255,255,255,0))
            edge_color_group.append(wx.Colour(255,255,255,0))
            """
            
            self.draw_layers[self.point_layer].set_data_group(id_group)
            self.draw_layers[self.point_layer].set_fill_color_group(color_group)
            self.draw_layers[self.point_layer].set_edge_color_group(edge_color_group)
         
        # draw layer in buffer
        for layer_name in self.layer_name_list[::-1]:
            if layer_name == "Density Map":
                if self.isHideDensityMap == False:
                    self.drawDensityMaps(dc)
            else:
                layer = self.layer_dict[layer_name]
                if self.hide_layers[layer] == False:
                    self.draw_layers[layer].draw(dc,self.view)
           
        if self.bStrip == True:
            if not self.bAnimate:
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
            self.stripBmpHeight
            ) 
       
    def enableKDEStrip(self,event):
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
        
    def drawSubView(self, index, bufferWidth, bufferHeight, bmp):
        dc = wx.BufferedDC(None, bmp)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0,0,bufferWidth,bufferHeight)
        image = wx.ImageFromBitmap(self.density_bmps[index])
        
        bmpWidth = self.stripBmpWidth* 0.8
        bmpHeight = self.stripBmpHeight* 0.8
        bmpRatio = self.bmp_width / self.bmp_height
        
        if self.bmp_width > self.bmp_height:
            bmpHeight = bmpWidth / bmpRatio
        else:
            bmpWidth = bmpHeight * bmpRatio
            
        bmpOffsetX = (self.stripBmpWidth- bmpWidth )/2.0 
        bmpOffsetY = (self.stripBmpHeight- bmpHeight)/2.0 
        image = image.Scale(bmpWidth, bmpHeight, wx.IMAGE_QUALITY_NORMAL)
        bmp = wx.BitmapFromImage(image)
        dc.DrawBitmap(bmp,bmpOffsetX,bmpOffsetY) 
        #dc.Destroy()
       
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
                start_pos[1]+stripBmpHeight+2
            )
        #tmp_dc.Destroy()
        
        return stripBuffer        
    
    def OnMotion(self, event):
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
        # give the rest task to super class
        super(DynamicDensityMap,self).OnMotion(event)
        
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
        super(DynamicDensityMap,self).OnLeftDown(event)
        
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
                    if self.tick < self.n-1:
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
        super(DynamicDensityMap,self).OnLeftUp(event)
        
    def animateStripView(self, acc, start_offset, isLeft=True, t=1,isEnd=False):
        """
        """
        if t > 20:
            self.bAnimate= True
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
            tmp_dc.DrawRectangle(self.stripFramePos[0],
                                 self.stripFramePos[1],
                                 self.stripFrameWidth,
                                 self.stripFrameHeight)
            tmp_dc.DrawBitmap(self.stripBuffer, offset, self.bufferHeight/1.5)
            self.drawHighlightSubview(tmp_dc)
            self.buffer = tmp_buffer
            #tmp_dc.Destroy()
            self.Refresh(False)
            #self.RefreshRect(wx.Rect(self.stripFramePos[0],self.stripFramePos[1],
            #                         self.stripFrameWidth, self.stripFrameHeight))
            t = t + 1
            if self.stopAnimation == False:
                wx.FutureCall(10, self.animateStripView, acc, start_offset, isLeft,t,isEnd)     
        
        
    def ExportMovie(self,path,duration=3):
        from stars.visualization.utils.images2gif import writeGif,writeBmps2Gif
        
        Y,M,D = self.start_date.year, self.start_date.month, self.start_date.day # python.DateTime
        start_date = wx.DateTime.Today()
        start_date.Year,start_date.Month, start_date.Day = Y,M,D
        
        tick = self.tick
        movie_bmps = []
        for i in range(self.n):
            self.tick = i
            tmp_bmp = wx.EmptyBitmapRGBA(self.bufferWidth, self.bufferHeight,255,255,255,255)
            dc = wx.MemoryDC()
            dc.SelectObject(tmp_bmp)
            self.isResizing = True
            self.DoDraw(dc)
            self.isResizing = False
            
            # draw lables
            if i < self.n -1:
                end_date = wx.DateTime.Today()
                end_date.Set(start_date.Day, start_date.Month, start_date.Year)
           
                if self.step_by == 'Day':
                    end_date += wx.DateSpan(days=self.step)
                elif self.step_by == 'Month':
                    end_date += wx.DateSpan(months=self.step)
                elif self.step_by == 'Year':
                    end_date += wx.DateSpan(years=self.step)
                    
                label = '(%d/%d) %s/%s/%s - %s/%s/%s (%s %s period)' % \
                      (i+1,self.n, start_date.Month,start_date.Day,start_date.Year,
                       end_date.Month,  end_date.Day,  end_date.Year,self.step, self.step_by
                       )
                start_date.Year,start_date.Day = end_date.Year, end_date.Day
                start_date.SetMonth( end_date.Month)
            else:
                label = '(%d/%d) %s/%s/%s - %s/%s/%s (%s %s period)' % \
                      (i+1,self.n, start_date.Month,start_date.Day,start_date.Year,
                       self.end_date.month,  self.end_date.day,  self.end_date.year,self.step, self.step_by
                       )
                
            dc.DrawText(label, 5,5)
            #dc.Destroy()
            movie_bmps.append(tmp_bmp)
        writeBmps2Gif(path,movie_bmps, duration=duration, dither=0)
        self.tick = tick
        self.ShowMsgBox("Movie file (GIF) created successfully.",
                        mtype='CAST information',
                        micon=wx.ICON_INFORMATION)
        
    def UpdateGradient(self,gradient_type):
        self.color_band = gradient_type
        self.gradient_color = GradientColor(gradient_type)
        # update color schema
        self.color_schema_dict["Density Map"] = GradientColorSchema(gradient_type)
        self.createDensityMaps()
        self.isResizing = True
        self.reInitBuffer = True
        
        return self.color_schema_dict["Density Map"]
        
    def UpdateOpaque(self, opaque):
        self.opaque = opaque*2.55
        self.createDensityMaps()
        self.isResizing = True
        self.reInitBuffer = True
        
    def OnRightUp(self,event):
        menu = wx.Menu()
        menu.Append(201, "Show/Hide KDE strip", "")
        
        menu.UpdateUI()
        menu.Bind(wx.EVT_MENU, self.enableKDEStrip, id=201)
        self.PopupMenu(menu)
        
        event.Skip()
              
class DynamicDensityMapQueryDialog(DensityMapQueryDialog):

    def __init__(self, parent, title, points_data, isShowSpace=False, **kwargs):
        DensityMapQueryDialog.__init__(self,parent,title, points_data, isShowSpace, **kwargs)
        
    def Add_Customized_Controls(self):
        self.isAddAccumOption = True
        super(DynamicDensityMapQueryDialog,self).Add_Customized_Controls()
        
    def OnDateFieldSelected(self, event):
        # step_by is not needed in Time Density Map
        super(DynamicDensityMapQueryDialog, self).OnDateFieldSelected(event)
        
        self.textbox_step.Enable(True)
        self.cmbox_step.Enable(True)
        
    
    def OnQuery(self,event):
        if self._check_time_itv_input() == False or\
           self._check_KDE_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self.query_date = None # query_date is not available in Trend Graph case
        self._filter_by_date_interval()
        self._filter_by_tod()
         
        self.isAccumulative = self.accu_kde.GetValue()
        density_data_dict = self.gen_date_by_step()
        
        background_layer = None
        if self.isShowSpace:
            background_layer = None if self.cmbox_location.CurrentSelection<0 else\
                             self.background_shps[self.cmbox_location.CurrentSelection]
           
        title = ""
        if self.query_field.lower() != "all fields":
            title = "(%s:%s)"%(self.query_field,self.query_range)
            
        densityMap_widget= DynamicMapWidget(
            self.parent,
            [self.points_data],
            DynamicDensityMap,
            density_data_dict=density_data_dict,
            #background=background_layer,
            cell_size=self.cell_size,
            bandwidth=self.bandwidth,
            kernel=self.kernel_method,
            opaque=self.opaque,
            color_band=self.color_band,
            start=self._wxdate2pydate(self.itv_start_date.GetValue()),
            end=self._wxdate2pydate(self.itv_end_date.GetValue()),
            step_by=self.step_by,
            step=self.step,
            isAccumulative=self.isAccumulative,
            size =(800,650),
            title=title
            ) 
        densityMap_widget.Show()
        
        self.btn_save.Enable(True)
    
    def OnSaveQueryToDBF(self, event):
        try:
            import pysal
            if self.query_data == None:
                return
            dlg = wx.FileDialog(
                self, message="Save query into a dbf file...", defaultDir=os.getcwd(), 
                defaultFile='%s.dbf' % (self.points_data.name + '_dynamicKDE'), 
                wildcard="dbf file (*.dbf)|*.dbf|All files (*.*)|*.*", 
                style=wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            path = dlg.GetPath()
            dlg.Destroy()
            dbf = self.points_data.dbf
            
            field_name = ""
            for item in dbf.header:
                if item.startswith('TIME_PERIOD'):
                    field_name = item +"_1"
            if field_name == "":
                field_name = "TIME_PERIOD"
           
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
                
            newDBF.header.append(field_name)
            newDBF.field_spec.append(('N',4,0))
       
            rows = []
            for i in range(dbf.n_records):
                rows.append(dbf.read_record(i))
           
            for key in self.query_data.keys():
                vals = self.query_data[key]
                for i in vals:
                    rows[i].append(key)
                    
            for row in rows: 
                newDBF.write(row)
            newDBF.close()
        
            self.ShowMsgBox("Query results have been saved to column 'TIME_PERIOD' in dbf file",
                            mtype='CAST information',
                            micon=wx.ICON_INFORMATION)
        except Exception as err:
            self.ShowMsgBox("""Saving query results to new dbf file failed.
            
Details: """+str(err.message))
    
    def gen_date_by_step(self):
        """
        generate dynamic density map data by STEP
        """
        from stars.visualization.utils import GetIntervalStep
        
        step = self.step
        step_by = self.step_by
        #background_shp_idx = self.background_shp_idx    
        
        #background_shp = self.background_shps[background_shp_idx]
        start_date = self.start_query_date # already python datetime
        end_date   = self.end_query_date  
        total_steps = GetIntervalStep(end_date, start_date, step, step_by)
        
        # displaying progress
        n = len(self.current_selected)        
       
        if total_steps <= 0:
            self.ShowMsgBox("Start and end dates are not correct.")
            return None
        elif total_steps > 24:
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
            
        if n == 0:
            self.ShowMsgBox("There is no points in query result. Please change query parameters and retry.")
            return None
        
        itv = n/5
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Space-time query for density maps..               ",
            maximum = n,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
        )
        progress_dlg.CenterOnScreen()
        
        density_data_dict = {}  # startdatetime:points
        density_data_dict = dict([(s,[]) for s in range(total_steps)])
        
        for count,j in enumerate(self.current_selected):
            if count % itv == 0:
                progress_dlg.Update(count +1)
                
            _date = self.all_dates[j] 
            interval_idx = GetIntervalStep(_date, start_date, step, step_by) -1
            density_data_dict[interval_idx].append(j)
            
        progress_dlg.Update(n)
        progress_dlg.Destroy()            
        
        self.query_data = density_data_dict
        
        return density_data_dict