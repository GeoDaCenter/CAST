"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["AbstractCanvas"]

import os,abc
import wx

import stars
from stars.visualization.EventHandler import *
from stars.visualization.utils import *

class AbstractCanvas(wx.Window):
    """
    Abstract class for all drawing classes:
       stars.visualization.maps
       stars.visualization.plots
    
    Implemented a basic double buffered drawing
    framework based on wxPython.
    
    Inherited classes can take care
    of the drawing function: DoDraw(self,dc),
    to drawing to a buffer, then to the screen, 
    during EVT_PAINT event.
    
    Inherited classes can also use
    wx.BufferedDC to direct drawing to a buffer,
    then the screen outside EVT_PAINT event.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self,parent, **kwargs):
        
        style = wx.BORDER_SUNKEN
        if kwargs.has_key("style"):
            style = kwargs["style"]
            
        wx.Window.__init__(self, parent, style=style, **kwargs)
        
        self.SetBackgroundColour(wx.WHITE)
        self.bufferWidth, self.bufferHeight = 0,0
        self.buffer = None
        self.drawing_backup_buffer = None
        self.reInitBuffer = False
        self.InitBuffer()
       
        self.progress = 0
        self.main = None
        self.parentFrame = None
        self.observer = None
        self.status_bar = None
        
        while parent != None:
            if isinstance(parent, stars.Main):
                self.main = parent
                self.observer = parent.observer
            if self.parentFrame == None \
               and isinstance(parent, wx.Frame):
                self.parentFrame = parent
            if self.status_bar == None \
               and isinstance(parent, stars.visualization.MapWidget):
                self.status_bar = parent.status_bar
            parent = parent.GetParent()
      
        self.view = None
        self.map_operation_type = stars.MAP_OP_SELECT
        
        # for selection
        self.isMouseDrawing = False
        self.isDynamicSelection = False
        # for append selection
        self.current_region = None
        self.previous_region = None
        self.select_regions = []
        self.isAppendSelection = False
        # for panning
        self.previous_pan_pos = [0,0]
        # for brushing
        self.isBrushing = False
        self.brushing_height = 0
        self.brushing_width = 0
        self.brushing_keycode = stars.MAP_KEY_BRUSHING_POSIX \
            if os.name=='posix' else stars.MAP_KEY_BRUSHING_WIN
        
        # bindings mouse/key events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion) 
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        
        # bindings window events
        # OnClose Only send to Frame/Dialog
        #self.parentFrame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def SetTitle(self, title):
        self.parentFrame.SetTitle(title)
        
    #-----------------------------------------
    # belows are for event based
    # linking and brushing
    #-----------------------------------------
    def Register(self, event_type, func):
        """
        register my function as a listener for event_type
        parameters:
        event_type--global defined EVT_NAME
        event--self defined function
        """
        self.observer.add_event_listener(event_type, func)
    
    def UpdateEvt(self, event_type, event_data):
        """
        notify observer by sending the event_type with event_data
        """
        self.observer.dispatch_event(Event(event_type, event_data))       
   
    def Unregister(self,event_type, func):
        """
        unregister my registerd listener for event_type
        """
        self.observer.remove_event_listener(event_type, func)
    
    @abc.abstractmethod
    def OnClose(self, event):
        """
        When canvas close, it should unregister all registed
        Events if there's any (at Frame/Dialog level).

        NOTE:
        Every inherited class should overwrite this function
        to unregister any registered functions
        """
        event.Skip()
        
    def ShowMsgBox(self,msg,msg_title='Warning', msg_type=wx.OK|wx.ICON_WARNING):
        dlg = wx.MessageDialog(self, msg, msg_title, msg_type)
        dlg.ShowModal()
        dlg.Destroy()
        
    #----------------------------------
    # belows are drawing functions
    # (double buffered drawing)
    #----------------------------------
    def InitBuffer(self):
        if self.bufferWidth >0 and self.bufferHeight>0:
            self.buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
            dc = wx.BufferedDC(None, self.buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            # NOTE: in linux (Ubuntu), transparency doesn't work well in 
            # BufferedDC with wx.DC
            if not 'Linux' in stars.APP_PLATFORM \
               and 'Darwin' != stars.APP_PLATFORM:
                dc = wx.GCDC(dc)
            self.DoDraw(dc)
            self.reInitBuffer = False
            self._create_backup_buffer()
            
    def OnPaint(self, event):
        if self.buffer:
            dc = wx.BufferedPaintDC(self, self.buffer,wx.BUFFER_VIRTUAL_AREA)
        # remember to skip this EVT_PAINT,
        # especially in windows, otherwise the program
        # will hang in here. In MacOS/Linux, wxpython
        # may automatically skip this event to avoid
        # dead-lock here.
        event.Skip() 
        
    def OnIdle(self,event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
    
    def OnSize(self,event):
        self.drawing_backup_buffer = None
        self.bufferWidth,self.bufferHeight = self.GetClientSize()
        self.reInitBuffer = True

    #----------------------------------
    # belows are some support drawing functions
    # either ABSTRACT which should be
    # implemented in inherited class
    # , or COMMON drawing utilities, such as 
    # Mouse_drag_rectangular etc.
    #----------------------------------
    def DoDraw(self,dc):
        """
        Abstract main drawing function.
        Any maps or other objects, that need to
        be drawn to the double BUFFER, should be
        drawn here. 
        """
        return "Should never be here!"
        
    def draw_selected_by_region(self,dc, region, 
                                isEvtResponse=False, 
                                isScreenCoordinates=False):
        """ 
        Abstract function for Brushing and Linking
        If don't need Brushing and Linking, don't
        overwrite this function in inherited classes
        """
        pass
    
    def draw_selected_by_regions(self,dc, region, 
                                isEvtResponse=False, 
                                isScreenCoordinates=False):
        """ 
        Abstract function for Brushing and Linking
        If don't need Brushing and Linking, don't
        overwrite this function in inherited classes
        """
        pass
    #-------------------------------------
    # belows are mouse/key events handlers
    #
    #-------------------------------------
    def OnKeyDown(self, evt):
        """called when a key pressed"""
        keycode = evt.GetKeyCode()
        # Ctrl to enable brushing in WIN
        # CMD to enable brushing in MAC
        if keycode == self.brushing_keycode: 
            self.map_operation_type = stars.MAP_OP_BRUSHING
            self.isBrushing = True
            
        # shift key: append selection  
        elif keycode == stars.MAP_KEY_APPEND_SELECTION: 
            self.isAppendSelection = True
            if self.current_region:
                self.select_regions.append(self.current_region)
                
        elif keycode == stars.MAP_KEY_DYNAMIC_SELECTION:
            self.isDynamicSelection = True
            
        elif keycode == wx.WXK_ESCAPE:
            self.isBrushing = False
            self.brushing_height=None
            self.brushing_width=None
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            self.map_operation_type = stars.MAP_OP_SELECT
            
        elif keycode == wx.WXK_SHIFT:
            if evt.CmdDown():
                self.map_operation_type = stars.MAP_OP_SELECT
                self.isBrushing = False
                self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            

    def OnKeyUp(self, evt):
        """called when a key up"""
        keycode = evt.GetKeyCode()
        """
        if keycode == self.brushing_keycode \
           and self.map_operation_type == stars.MAP_OP_BRUSHING:
            self.SetCursor(wx.StockCursor(wx.CURSOR_PAINT_BRUSH))
            self.isBrushing = True
        """  
        # shift key: append selection    
        if keycode == stars.MAP_KEY_APPEND_SELECTION: 
            self.isMouseDrawing = False
            self.isAppendSelection = False
            self.current_region = None
            self.select_regions = []
            
        elif keycode == stars.MAP_KEY_DYNAMIC_SELECTION:
            self.isDynamicSelection = False
            
    def OnLeftDown(self, event):
        """called when the left mouse button is pressed"""
        self.current_region = None
        self.previous_region = None
        
        self.SetFocus()
        self.mouse_start_pos = (event.GetX(), event.GetY())
        self.isMouseDrawing = True
        self.CaptureMouse()
        
        # create a original drawing buffer for mousing drawing
        if self.drawing_backup_buffer == None:
            self._create_backup_buffer()
        
    def OnMotion(self, event):
        """ Called when the mouse is in motion"""
        x, y = event.GetX(), event.GetY() 
        self.display_xy_on_status(x,y)
        
        # prepare DC for brushing drawing 
        tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
        tmp_dc = wx.BufferedDC(None, tmp_buffer)
        tmp_dc.Clear()
        
        if event.Dragging() and event.LeftIsDown() and self.isMouseDrawing:
            # while mouse is down and moving
            x0,y0 = self.mouse_start_pos
            if self.map_operation_type == stars.MAP_OP_PAN:
                delta_px = -x0 + x 
                delta_py = -y0 + y
                tmp_dc.DrawBitmap(self.drawing_backup_buffer,delta_px,delta_py)
                self.buffer = tmp_buffer
                self.Refresh(False)
                #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
            else:
                # drawing the selection rectangular box
                # this works for both SELECT/ZOOM
                self.current_region = (x0,y0,x,y)
                tmp_dc.DrawBitmap(self.drawing_backup_buffer,0,0)
                self.draw_mouse_select_box(tmp_dc,x0,y0,x,y) 
                self.buffer = tmp_buffer
                self.Refresh(False)
                #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
                
        elif self.isBrushing == True:
            if self.brushing_height != None and self.brushing_width !=None \
               and (self.brushing_height > 0 or self.brushing_width >0):
                if self.drawing_backup_buffer:
                    tmp_dc.DrawBitmap(self.drawing_backup_buffer,0,0)
                    if self.brushing_height>0 or self.brushing_width >0:
                        x0,y0 = x - self.brushing_width, y - self.brushing_height
                        self.current_region = (x0,y0,x,y)
                        self.draw_mouse_select_box(tmp_dc, x0,y0,x,y)
                        self.buffer = tmp_buffer
                        self.Refresh(False)
                        #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
            else:
                if not self.map_operation_type == stars.MAP_OP_BRUSHING:
                    # prevent CMD+Tab combined keys (switch app in MAC)
                    self.reset_map_operator()
                
    def OnLeftUp(self, event):
        """called when the left mouse button is released"""
        if not self.HasCapture():
            return
        
        self.isMouseDrawing = False
        self.ReleaseMouse()
        
        if not self.buffer:
            return
        
        self.mouse_end_pos = (event.GetX(), event.GetY())
        self.current_region = self.mouse_start_pos+self.mouse_end_pos
        select_w = abs(self.mouse_end_pos[0] - self.mouse_start_pos[0])
        select_h = abs(self.mouse_end_pos[1] - self.mouse_start_pos[1])
       
        # prepare single click case
        if select_w == select_h == 0:
            # cancle brushing
            self.isBrushing = False
            self.brushing_height=None
            self.brushing_width=None
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            
        if self.map_operation_type == stars.MAP_OP_ZOOMIN:
            self._zoom_end(self.mouse_start_pos, self.mouse_end_pos, select_w, select_h)
            
        elif self.map_operation_type == stars.MAP_OP_PAN:
            self._pan_end(self.mouse_start_pos, self.mouse_end_pos, select_w, select_h)
        
        elif self.map_operation_type == stars.MAP_OP_BRUSHING:
            if select_w ==0 and select_h == 0:
                self.reset_map_operator()
                self.buffer = self.drawing_backup_buffer
                self.Refresh(False)
                #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
            else:
                self.brushing_width = select_w 
                self.brushing_height = select_h 
                
        elif self.map_operation_type == stars.MAP_OP_SELECT:
            tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
            tmp_dc = wx.BufferedDC(None, tmp_buffer)
            tmp_dc.DrawBitmap(self.drawing_backup_buffer,0,0)
            
            if self.isAppendSelection:
                if self.current_region in self.select_regions:
                    # if select same object twice, de-select this object
                    self.select_regions.remove(self.current_region)
                else:
                    # just add this new object in select_regions
                    self.select_regions.append(self.current_region)
                self.draw_selected_by_regions(tmp_dc, self.select_regions, isScreenCoordinates=True)
            else:
                if self.current_region:
                    self.draw_selected_by_region(tmp_dc, self.current_region,isScreenCoordinates=True)
            self.buffer = tmp_buffer
            self.Refresh(False)
            #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
    
    def OnRightDown(self, event):
        pass
    
    def OnRightUp(self, event):
        pass            

    #----------------------------------
    # belows are support functions for drawing
    # 
    #----------------------------------
    def restore(self):
        """ for extent/restore button at toolbar"""
        # restore view
        self.view.restore()
        # restore pan position
        self.previous_pan_pos = [0,0]
        # restore drawing buffer
        if self.drawing_backup_buffer:
            self.buffer = self.drawing_backup_buffer
            self.drawing_backup_buffer = None
            self.Refresh(False)
            #self.RefreshRect(wx.Rect(0,0,self.bufferWidth,self.bufferHeight))
        # trigger to redraw
        self.reInitBuffer = True
        
    def draw_mouse_select_box(self,dc,x0,y0,x,y):
        """
        NOTE: if inherited class (canvas) doesn't need
        this function, it can simply overwrite this 
        function with EMPTY content.
        """
        w = abs(x-x0)
        h = abs(y-y0)
        start_x,start_y = min(x0,x),min(y,y0)
        if self.isDynamicSelection or self.isBrushing:
            self.draw_selected_by_region(dc,self.current_region, isScreenCoordinates=True)
        # then draw the rectangular
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(start_x,start_y,w,h)

    def display_xy_on_status(self,x,y):
        """ Display information on status """
        if self.status_bar and self.view:
            # display current lat/lot on status bar
            w_y,w_x = self.view.pixel_to_view(x,y)
            self.status_bar.SetStatusText("%.4f,%.4f"%(w_x,w_y))
         
    def reset_map_operator(self):
        self.map_operation_type = stars.MAP_OP_SELECT
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        # cancle brushing
        self.isBrushing = False
        self.brushing_height=0
        self.brushing_width=0
       
    def _zoom_end(self, mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h):
        """for left mouse up zoomin"""
        delta_px = -mouse_start_pos[0]
        delta_py = -mouse_start_pos[1]
        
        if mouse_select_w ==0 and mouse_select_h == 0:
            self.reset_map_operator()
        else:
            self.view.zoom(mouse_start_pos+mouse_end_pos)
        #self.view.pan( delta_px, delta_py )
        self.reInitBuffer = True
        
    def _pan_end(self, mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h):
        """for left mouse up pan"""
        delta_px = -mouse_start_pos[0] + mouse_end_pos[0]
        delta_py = mouse_start_pos[1] - mouse_end_pos[1]
       
        self.previous_pan_pos[0] = self.previous_pan_pos[0] + delta_px
        self.previous_pan_pos[1] = self.previous_pan_pos[1] + delta_py
        
        if mouse_select_w ==0 and mouse_select_h == 0:
            self.reset_map_operator()
        else:
            self.view.pan( delta_px , delta_py)
        self.reInitBuffer = True
            
    def _generate_rect(self, region):
        x0,y0,x1,y1 = region
        start_x = min(x0,x1)
        start_y = min(y0,y1)
        w = abs(x0-x1)
        h = abs(y0-y1)
        return wx.Rect(start_x,start_y,w,h)
        
    def _create_backup_buffer(self):
        if 'Win' in stars.APP_PLATFORM:
            img = self.buffer.ConvertToImage()
            self.drawing_backup_buffer = wx.BitmapFromImage(img)
        else:
            self.drawing_backup_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
            tmp_dc = wx.BufferedDC(None, self.drawing_backup_buffer)
            tmp_dc.Clear()
            tmp_dc.DrawBitmap(self.buffer,0,0)