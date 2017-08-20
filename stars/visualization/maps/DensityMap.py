"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["DensityMap",'DensityMapQueryDialog','KDEConfigDialog']

import os,time
import wx
import wx.combo
import random
import numpy as np
import scipy
from math import exp,pi,ceil,floor,sqrt

import pysal
import stars
from ShapeMap import ShapeMap, GradientColorSchema
from stars.visualization.MapWidget import MapWidget
from stars.visualization.utils import View2ScreenTransform, GradientColor
from stars.visualization.SpaceTimeQueryDialog import SpaceTimeQueryDialog   

def triangular(z):
    return 1 - abs(z)

def uniform(z):
    return abs(z)

def quadratic(z):
    return 0.75*(1 - z*z)

def quartic(z):
    return (15*1.0/16)*(1-z*z)*(1-z*z)

def gaussian(z):
    return sqrt(2*pi)*exp(-0.5*z*z)

class DensityMap(ShapeMap):
    """
    wxWindow drawing density map based on points data or POINT SHAPE file
    """
    def __init__(self,parent, layers, **kwargs):
        ShapeMap.__init__(self,parent,layers)
        
        try:
            self.point_layer  = self.layers[0]
            #self.bg_layer     = kwargs["background"]
            self.cell_size    = kwargs["cell_size"]
            self.bandwidth    = kwargs["bandwidth"]
            self.kernel       = kwargs["kernel"]
            self.color_band   = kwargs["color_band"]
            self.opaque       = kwargs["opaque"]
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.points = self.point_layer.shape_objects
            self.extent = self.point_layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth, 
                self.bufferHeight
                )
            
            if kwargs.has_key("query_points"):
                self.query_points = kwargs["query_points"]
            else:
                self.query_points = range(len(self.points))
               
            """
            if self.bg_layer: 
                self.layers.append(self.bg_layer)
            """
            
            if len(self.query_points) < len(self.points):
                id_group         = [self.query_points]
                color_group      = [self.color_schema_dict[self.point_layer.name].colors[0]]
                edge_color_group = [self.color_schema_dict[self.point_layer.name].edge_color]
                """
                non_query_points = list(set(range(len(self.points))) - set(self.query_points))
                id_group.append(non_query_points)
                color_group.append(wx.Colour(255,255,255,0))
                edge_color_group.append(wx.Colour(255,255,255,0))
                """
                self.draw_layers[self.point_layer].set_data_group(id_group)
                self.draw_layers[self.point_layer].set_fill_color_group(color_group)
                self.draw_layers[self.point_layer].set_edge_color_group(edge_color_group)
            
            # setup gradient color
            self.gradient_color = GradientColor(self.color_band)
            # for tree node
            self.color_schema_dict["Density Map"] = GradientColorSchema(self.color_band)
            self.isHideDensityMap = False
            # for export gif
            self.img_array_rgb = None
            
            self.isResizing = False
            self.cells_Updated = False
            self.bmp = None
           
            self.setup_densityMap()
            self.createDensityMap()
           
            # dummy Layer for density map
            self.layer_seq_list = []
            self.layer_seq_list.insert(0,"Density Map")
            self.layer_name_list.insert(0,"Density Map")
            
        except Exception as err:
            self.ShowMsgBox("""Density map could not be created. Please choose/input valid parameters.
            
Details: """ + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return None
        
    def OnShapesSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        event is an instance of EventHandler.Event class
        event.object are the data for selecting shape objects
        """
        if not event: return
        if not self.buffer: return
        
        data = event.data
            
        if len(data.boundary) >0:
            # select shape object by boundary
            # prepare DC for brushing drawing 
            tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
            tmp_dc = wx.BufferedDC(None, tmp_buffer)
            tmp_dc.DrawBitmap(self.drawing_backup_buffer,0,0)
            
            regions = []
            if isinstance(data.boundary[0], int) or isinstance(data.boundary[0], float):
                regions.append(data.boundary)
            elif isinstance(data.boundary, list):
                regions = data.boundary
                
            for region in regions:
                x,y,x0,y0 = region
                x,y = self.view.view_to_pixel(x,y)
                x0,y0 = self.view.view_to_pixel(x0,y0)
                select_region = (x,y,x0,y0)
                w = abs(x-x0)
                h = abs(y-y0)
                start_x,start_y = min(x0,x),min(y,y0)
                tmp_dc.SetPen(wx.RED_PEN)
                tmp_dc.SetBrush(wx.TRANSPARENT_BRUSH)
                tmp_dc.DrawRectangle(int(start_x),int(start_y),int(w),int(h))
            self.buffer = tmp_buffer
            self.Refresh(False)
        
    def set_opaque(self, opaque):
        """
        Set the opaque of the Density Map
        Value range (0-255), less value, more transparent
        """
        self.opaque = opaque

        """
        Overwrite draw_background() to draw MAP buffer
        and DenstiyMAP buffer as background
        """
        if self.buffer:
            dc.DrawBitmap(self.buffer,0,0)
            
        if self.bmp:
            # always scale density map to correct window size and draw them
            scale_x = self.bmp_width / float(self.cols)
            scale_y = self.bmp_height / float(self.rows)
            dc.SetUserScale(scale_x, scale_y)
            dc.DrawBitmap(self.bmp, self.bmp_left/scale_x,  self.bmp_upper/scale_y)
        
    def createDensityMap(self):
        # compute density map, just once
        if self.cells_Updated == False:
            n = len(self.points)
            progress_dlg = wx.ProgressDialog(
                "Progress",
                "Creating density map...               ",
                maximum = 2,
                parent=self,
                style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
                )
            progress_dlg.CenterOnScreen()
           
            progress_dlg.Update(1)
            self.grid_to_buffer()
            progress_dlg.Update(2)
            
    def DoDraw(self,dc):
        """
        Implement inhereted DoDraw() function
        It will be called when window initialize and resize
        """
        # draw layer in buffer
        for layer_name in self.layer_name_list[::-1]:
            if layer_name == "Density Map":
                if self.isHideDensityMap == False:
                    self.drawDensityMap(dc)
            else:
                layer = self.layer_dict[layer_name]
                if self.hide_layers[layer] == False:
                    self.draw_layers[layer].draw(dc,self.view)
       
    def drawDensityMap(self,dc):
        bmp = self.bmp
        if self.isResizing:
            # resize bmp
            self.setup_bitmap()
            image = wx.ImageFromBitmap(self.bmp)
            
            if self.bmp_width > self.bufferWidth or self.bmp_height > self.bufferHeight:
                cropLeft = 0
                if self.bmp_left < 0:
                    cropLeft = abs(self.bmp_left) / self.bmp_width * self.bmp.Width
                    
                cropUpper = 0
                if self.bmp_upper < 0:
                    cropUpper = abs(self.bmp_upper) / self.bmp_height * self.bmp.Height
               
                cropWidth = self.bufferWidth / self.bmp_width * self.bmp.Width
                if self.bmp_left > 0:
                    cropWidth = (self.bufferWidth - self.bmp_left) / self.bmp_width * self.bmp.Width
                    
                cropHeight = self.bufferHeight / self.bmp_height * self.bmp.Height
                if self.bmp_upper > 0:
                    cropHeight = (self.bufferHeight - self.bmp_upper) / self.bmp_height * self.bmp.Height
                
                if cropWidth > 0 and cropHeight > 0:
                    image = image.GetSubImage(wx.Rect(cropLeft,cropUpper,cropWidth,cropHeight))
                    image = image.Scale(self.bufferWidth, self.bufferHeight, wx.IMAGE_QUALITY_HIGH)
                    
                    bmp = wx.BitmapFromImage(image)
                    
                    start_x = 0
                    start_y = 0
                    if self.bmp_left > 0:
                        start_x = self.bmp_left 
                    if self.bmp_upper > 0:
                        start_y = self.bmp_upper
                        
                    dc.DrawBitmap(bmp,start_x,start_y)
            else:
                image = image.Scale(self.bmp_width, self.bmp_height, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.BitmapFromImage(image)
                dc.DrawBitmap(bmp,self.bmp_left, self.bmp_upper)
                
            self.isResizing = False
        else: 
            # draw density map, by zooming the Density Map
            dc.DrawBitmap(bmp, self.bmp_left,  self.bmp_upper)
       
    def UpdateGradient(self,gradient_type):
        self.gradient_color = GradientColor(gradient_type)
        # update color schema
        self.color_schema_dict["Density Map"] = GradientColorSchema(gradient_type)
        
        self.color_band = gradient_type
        self.grid_to_buffer()
        self.isResizing = True
        self.reInitBuffer = True
        
        return self.color_schema_dict["Density Map"]
        
    def UpdateOpaque(self, opaque):
        self.opaque = opaque
        self.grid_to_buffer()
        self.isResizing = True
        self.reInitBuffer = True
        
    def OnSize(self, event):
        """ overwrittern for resizing kde map"""
        self.isResizing = True
        super(DensityMap, self).OnSize(event)
        
    def _zoom_end(self, mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h):
        """ overwrittern for zooming with mouse """
        self.isResizing = True
        super(DensityMap, self)._zoom_end(mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h)
    
    def _pan_end(self, mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h):
        """ overwrittern for panning with mouse """
        self.isResizing = True
        super(DensityMap, self)._pan_end(mouse_start_pos, mouse_end_pos, mouse_select_w, mouse_select_h)
        self.reInitBuffer = True
        
    def restore(self):
        """ overwritten for restoring/extenting kde map """
        self.isResizing = True
        super(DensityMap, self).restore()

    def setup_densityMap(self):
        """
        Setup the parameters of Density Map.
            extent, width, height, grid, view_transformer etc.
        """
        if self.bufferWidth >0 and self.bufferHeight>0: 
            # from extend to grid
            left, lower, right, upper = self.extent
            extent_width = self.extent[2] - self.extent[0]
            extent_height = self.extent[3] - self.extent[1]
            self.cols = int(ceil(extent_width / float(self.cell_size)))
            self.rows = int(ceil(extent_height/ float(self.cell_size)))
            self.grid = np.zeros((self.rows,self.cols))
            
            # grid variables
            self.grid_lower = lower + ( self.cell_size/2.0)
            self.grid_upper = self.grid_lower + ( (self.rows -1 ) * self.cell_size)
            self.grid_left = left + (self.cell_size/2.0)
            self.grid_right = self.grid_left + ( (self.cols -1) * self.cell_size)
            
    def setup_bitmap(self):
        """
        bmp variables, in case of resize/pan/extent/zoom
        """
        left, lower, right, upper = self.extent
        self.bmp_left, self.bmp_upper = self.view.view_to_pixel( left, upper)
        self.bmp_right, self.bmp_lower = self.view.view_to_pixel( right, lower)
        self.bmp_width = self.bmp_right - self.bmp_left
        self.bmp_height = self.bmp_lower - self.bmp_upper
            
    def update_density(self,X,Y,invert=False):
        """
        Go through each point in data, and calculate the density value of
        cells it impacted.
        """
        cellSize = self.cell_size
        radius = self.bandwidth / cellSize
        
        float_i = (Y - self.grid_lower) / cellSize
        #float_i = (self.grid_upper -Y) / cellSize
        i = int(floor(float_i - radius))
        i = i if i >= 0 else 0
        I = int(floor(float_i + radius))
        I = I if I < self.rows else self.rows-1

        float_j = (X-self.grid_left) / cellSize
        j = int(floor(float_j - radius))
        j = j if j >= 0 else 0
        J = int(floor(float_j + radius))
        J = J if J < self.cols else self.cols-1

        for row in xrange(i,I+1):
            for col in xrange(j,J+1):
                x = self.grid_left + (col*cellSize)
                y = self.grid_lower + (row*cellSize)
                d = ((x-X)**2 + (y-Y)**2) ** (0.5)
                if d <= self.bandwidth:
                    z = d/self.bandwidth
                    if invert:
                        self.grid[row,col] -= self.kernel(z)
                    else:
                        self.grid[row,col] += self.kernel(z)
        
        self.cells_Updated = True
                      
    def grid_to_buffer(self):
        from stars.core.DKDEWrapper import call_kde
        x = []
        y = []
        for i in self.query_points:
            pt = self.points[i]
            x.append(pt[0])
            y.append(pt[1])
        n = len(self.query_points)
        if n < len(self.points):
            query_points = range(n)
            
        arr,rows,cols,grad_min,grad_max = call_kde(
            n,
            x,
            y,
            #self.query_points,
            range(n),
            self.extent,
            self.bandwidth, 
            self.cell_size, 
            self.kernel, 
            self.color_band, 
            self.opaque*2.55
            )
        #from PIL import Image
        #Image.fromarray(arr).save("test.png")
        self.bmp = wx.BitmapFromBufferRGBA(cols, rows, arr)
        #self.bmp.SaveFile("test.png", wx.BITMAP_TYPE_PNG)
        self.gradient_color_min = grad_min
        self.gradient_color_max = grad_max
    
    def grid_to_buffer1(self):
        """
        Draw GRID based Density Map to wxBitmap. 
        
        Here, directly drawing GRID map onto a RGBA Bitmap.
        Then, this Bitmap will be draw to self.buffer.
        """
        if self.grid.max() == 0:
            return wx.EmptyBitmapRGBA(self.rows, self.cols,255,255,255)
        
        self.setup_bitmap()
        
        # make Byte Array
        arr = np.zeros((self.rows, self.cols, 4), np.uint8)
        R, G, B, A = range(4)
          
        # tranfer 0~1 value to 0~255 pixel values, 
        self.raster = self.grid
        rows,cols = self.rows, self.cols
        raster_min, raster_max = self.raster.min(), self.raster.max()
        raster_scaled = (self.raster - raster_min)/(raster_max - raster_min) 
        
        red_matrix, blue_matrix, green_matrix, opaque_matrix = np.zeros((rows,cols)),\
                 np.zeros((rows, cols)), np.zeros((rows,cols)), np.ones((rows,cols))*self.opaque* (255/100.0)
    
        for i,row in enumerate(raster_scaled):
            for j,item in enumerate(row):
                clr = self.gradient_color.get_color_at(item)
                
                red_matrix[i][j]   = clr.red
                green_matrix[i][j] = clr.green
                blue_matrix[i][j]  = clr.blue
                if item <0.15:
                    opaque_matrix[i][j] = 0
        
        arr[:,:,R] = (red_matrix).astype("B")
        arr[:,:,G] = (green_matrix).astype("B")
        arr[:,:,B] = (blue_matrix).astype("B")
        arr[:,:,A] =  (opaque_matrix).astype("B")#self.opaque #alpha
        
        # for export gif
        self.img_array_rgb = arr

        # use the array to create a bitmap
        return wx.BitmapFromBufferRGBA(cols, rows, arr)
        
    def OnCellsSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        event is an instance of EventHandler.Event class
        event.object are the data for selecting shape objects
        """
        if not event: 
            return
   
    def OnNoCellSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        Normally, event could be None, you just need to clean and refresh
        you selected/highlighted
        """
        self.Refresh(False)
        
    def hide_layer(self, layer, isHide=True):
        # override ShapeMap.hide_layer() add isHideDensityMap
        if layer == None:
            # Density Map layer
            self.isHideDensityMap = isHide
        else:
            self.hide_layers[layer] = isHide
        self.isResizing = True
        self.reInitBuffer = True
    
class KDEConfigDialog(wx.Dialog):
    def __init__(self, parent, pts_shp):
        pos = (20,20)
        size = (380,260)
        
        wx.Dialog.__init__(self,parent,-1,"KDE configuration",pos=pos,size=size)
       
        self.points_data = pts_shp
        self.panel = wx.Panel(self,-1, size=(380,285))
                
        x2,y2 = 20, 10
        self.kd_staticbox = wx.StaticBox(self.panel, -1, "Kernel Density:",pos=(x2,y2),size=(325,140))
        wx.StaticText(self.panel, -1, "Kernel:",pos =(x2+10,y2+30),size=(100,-1))
        self.cmbox_kernel = wx.ComboBox(self.panel, -1, "", choices= ["quadratic","triangular","uniform","quartic","gaussian"],pos=(x2+100, y2+30), size=(200,-1), style=wx.CB_DROPDOWN)
        self.cmbox_kernel.SetSelection(0)
        wx.StaticText(self.panel, -1, "Opaque:",pos =(x2+10,y2+65),size=(80,-1))
        self.textbox_opaque = wx.TextCtrl(self.panel,-1,"80",pos=(x2+100,y2+65),size =(45,-1))
        self.slideralpha= wx.Slider(self.panel, -1, 80, 0, 100, pos=(x2+150,y2+67),size=(100, -1))
        self.slideralpha.SetTickFreq(1, 1)
        
        wx.StaticText(self.panel, -1, "Color band:",pos =(x2+10,y2+100),size=(100,-1))
        self.cmbox_kde_colorschema= wx.combo.BitmapComboBox(self.panel, -1, "", pos=(x2+100, y2+97), size=(200,-1), style=wx.CB_DROPDOWN)
        self.addColorBand('classic')
        self.addColorBand('fire')
        self.addColorBand('omg')
        self.addColorBand('pbj')
        self.addColorBand('pgaitch')
        self.addColorBand('rdyibu')
        self.cmbox_kde_colorschema.SetSelection(0)
        self.color_band = 'classic'
        
        self.advPanel=advPanel = wx.Panel(self.panel, pos=(30,158), size=(320,30))
        sizer = wx.BoxSizer(wx.VERTICAL)
        advPanel.SetSizer(sizer)
        
        self.cp = cp = wx.CollapsiblePane(advPanel, pos=(0,0),size=(200,25),label="Advanced Options",style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
        
        advSizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
        advSizer.AddGrowableCol(1)
        
        txt_cellsize = wx.StaticText(cp.GetPane(), -1, "Cell size:",size=(60,-1))
        advSizer.Add(txt_cellsize,0, wx.ALIGN_LEFT)
        
        self.textbox_cellsize = wx.TextCtrl(cp.GetPane(),-1,"",size =(65,-1))
        advSizer.Add(self.textbox_cellsize,0, wx.ALIGN_LEFT)
        
        w = abs(self.points_data.extent[2] - self.points_data.extent[0])
        h = abs(self.points_data.extent[1] - self.points_data.extent[3])
        self.w,self.h = w,h
        self.cellsize_guess = wx.StaticText(cp.GetPane(), -1, "(%d x %d image)" % (0,0),size=(300,-1))
        advSizer.Add(self.cellsize_guess, 0, wx.ALIGN_LEFT)
        
        txt_bandwidth = wx.StaticText(cp.GetPane(), -1, "Bandwidth:",size=(80,-1))
        advSizer.Add(txt_bandwidth, 0, wx.ALIGN_LEFT)
        self.textbox_bandwidthh = wx.TextCtrl(cp.GetPane(),-1,"",size =(65,-1))
        advSizer.Add(self.textbox_bandwidthh, 0, wx.ALIGN_LEFT)
        
        txt_bdinfo = wx.StaticText(cp.GetPane(), -1, "(w/h:%.1f/%.1f)" % (w,h), size=(300,-1))
        advSizer.Add(txt_bdinfo, 0, wx.ALIGN_LEFT)
        
        border = wx.BoxSizer()
        border.Add(advSizer)
        cp.GetPane().SetSizer(border)
        sizer.Add(cp,0,wx.EXPAND)
        
        x2,y2 = 20,190
        self.btn_query = wx.Button(self.panel, wx.ID_OK, "Run",pos=(x2,y2),size=(90, 30))
        self.btn_reset = wx.Button(self.panel, wx.ID_RESET, "Reset",pos=(x2+95,y2),size=(90, 30))
        self.btn_cancel = wx.Button(self.panel, wx.ID_CANCEL, "Cancel",pos=(x2+190,y2),size=(90, 30))
   
        self.Bind(wx.EVT_COMBOBOX, self.OnBitmapCombo, self.cmbox_kde_colorschema)
        self.Bind(wx.EVT_TEXT, self.OnCellSizeChange, self.textbox_cellsize)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnOpaqueChange, self.slideralpha)
        
        self.guessParameters(400.0)
      
    def OnPaneChanged(self,event):
        self.Layout()
        offset = 70
        if self.cp.IsExpanded():
            self.advPanel.SetSize((310,30+offset))
            self.SetSize((380,260+offset))
            x,y = self.btn_query.GetPosition()
            self.btn_query.SetPosition((x,y+offset))
            self.btn_reset.SetPosition((x+95,y+offset))
            self.btn_cancel.SetPosition((x+190,y+offset))
        else:
            self.advPanel.SetSize((310,30))
            self.SetSize((380,260))
            x,y = self.btn_query.GetPosition()
            self.btn_query.SetPosition((x,y-offset))
            self.btn_reset.SetPosition((x+95,y-offset))
            self.btn_cancel.SetPosition((x+190,y-offset))
        
    def ShowMsgBox(self,msg,mtype='Warning',micon=wx.ICON_WARNING):
        dlg = wx.MessageDialog(None, msg, mtype, wx.OK|micon)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnOpaqueChange(self, event):
        self.textbox_opaque.SetValue('%s'% event.GetEventObject().GetValue())
        
    def guessParameters(self, guessLength):
        # guess a 400x?00 map
        cell_size = max(self.w / guessLength, self.h/guessLength)
        
        # get a optimized bandwidth: silverman (1986)
        # http://support.sas.com/documentation/cdl/en/statug/63033/HTML/default/viewer.htm#statug_kde_sect016.htm
        n = len(self.points_data.shape_objects)
        data = np.array(self.points_data.shape_objects)
        std_x,std_y = np.std(data,axis=0) 
        Q_x = scipy.stats.mstats.mquantiles(data[:,0])
        IQR_x = Q_x[2] -Q_x[0]
        Q_y = scipy.stats.mstats.mquantiles(data[:,1])
        IQR_y = Q_y[2] -Q_y[0]
        h_x = 0.9 * min(std_x, IQR_x/1.34)* pow(n, -0.2)
        h_y = 0.9 * min(std_y, IQR_y/1.34)* pow(n, -0.2)
       
        bandwidth = max(h_x,h_y)
        
        self.textbox_cellsize.SetValue(str('%.15f'%cell_size))
        self.textbox_bandwidthh.SetValue(str('%.15f'%bandwidth))
        
    def OnCellSizeChange(self, event):
        try:
            cell_size = float(event.GetString())
            img_w, img_h = self.w/cell_size, self.h/cell_size
            self.cellsize_guess.SetLabel('(%d x %d image)' % (img_w,img_h))
            # guess each cell impact 10 neigbors 
            bandwidth = cell_size * 10
            
            #self.textbox_cellsize.SetValue('%s'%cell_size)
            self.textbox_bandwidthh.SetValue('%s'%bandwidth)
        except Exception as err:
            self.ShowMsgBox("cell size value not correct: " + str(err.message))
    
    def addColorBand(self, scheme_type):
        gradient_img = stars.GRADIENT_IMG_DICT[scheme_type]
        gradient_img = gradient_img.Rotate90()
        gradient_img = gradient_img.Scale(140,20)
        bmp = gradient_img.ConvertToBitmap()
        self.cmbox_kde_colorschema.Append(scheme_type, bmp, None)
        
    def OnBitmapCombo(self, event):
        bcb = event.GetEventObject()
        idx = event.GetInt()
        self.color_band  = bcb.GetString(idx)
        
class DensityMapQueryDialog(SpaceTimeQueryDialog):
    
    def __init__(self, parent, title, points_data, isShowSpace=False, **kwargs):
        self.isAddAccumOption = False
        SpaceTimeQueryDialog.__init__(self,parent,title, points_data, isShowSpace, **kwargs)
        
    def Add_Customized_Controls(self):
        """
        It will add its own Controls to choose paremeters
        of KDE. 
        """
        #self.textbox_step.Enable(False)
        #self.cmbox_step.Enable(False)
        x2,y2 = 20, 350
        if not self.isShowSpace:
            y2 -= 50
        self.static_kde = wx.StaticBox(self.panel, -1, "Kernel Density:",pos=(x2,y2),size=(325,170))
        wx.StaticText(self.panel, -1, "Kernel:",pos =(x2+10,y2+30),size=(100,-1))
        self.cmbox_kernel = wx.ComboBox(self.panel, -1, "", choices= ["quadratic","triangular","uniform","quartic","gaussian"],pos=(x2+100, y2+30), size=(200,-1), style=wx.CB_DROPDOWN)
        self.cmbox_kernel.SetSelection(0)
        wx.StaticText(self.panel, -1, "Opaque:",pos =(x2+10,y2+65),size=(80,-1))
        self.textbox_opaque = wx.TextCtrl(self.panel,-1,"80",pos=(x2+100,y2+65),size =(45,-1))
        self.slideralpha= wx.Slider(self.panel, -1, 80, 0, 100, pos=(x2+150,y2+67),size=(100, -1))
        self.slideralpha.SetTickFreq(1, 1)
        
        wx.StaticText(self.panel, -1, "Color band:",pos =(x2+10,y2+100),size=(100,-1))
        self.cmbox_kde_colorschema= wx.combo.BitmapComboBox(self.panel, -1, "", pos=(x2+100, y2+97), size=(200,-1), style=wx.CB_DROPDOWN)
        self.addColorBand('classic')
        self.addColorBand('fire')
        self.addColorBand('omg')
        self.addColorBand('pbj')
        self.addColorBand('pgaitch')
        self.addColorBand('rdyibu')
        self.cmbox_kde_colorschema.SetSelection(0)
        self.color_band = 'classic'
        
        if self.isAddAccumOption:
            self.add_accu_kde_option(x2+10,y2+215)

        self.advPanel=advPanel = wx.Panel(self.panel, pos=(x2+10,y2+130), size=(310,30))
        sizer = wx.BoxSizer(wx.VERTICAL)
        advPanel.SetSizer(sizer)
        
        self.cp = cp = wx.CollapsiblePane(advPanel, pos=(0,0),size=(200,25),label="Advanced Options",style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
        
        advSizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
        advSizer.AddGrowableCol(1)
        
        txt_cellsize = wx.StaticText(cp.GetPane(), -1, "Cell size:",size=(60,-1))
        advSizer.Add(txt_cellsize,0, wx.ALIGN_LEFT)
        
        self.textbox_cellsize = wx.TextCtrl(cp.GetPane(),-1,"",size =(65,-1))
        advSizer.Add(self.textbox_cellsize,0, wx.ALIGN_LEFT)
        
        w = abs(self.points_data.extent[2] - self.points_data.extent[0])
        h = abs(self.points_data.extent[1] - self.points_data.extent[3])
        self.w,self.h = w,h
        self.cellsize_guess = wx.StaticText(cp.GetPane(), -1, "(%d x %d image)" % (0,0),size=(300,-1))
        advSizer.Add(self.cellsize_guess, 0, wx.ALIGN_LEFT)
        
        txt_bandwidth = wx.StaticText(cp.GetPane(), -1, "Bandwidth:",size=(80,-1))
        advSizer.Add(txt_bandwidth, 0, wx.ALIGN_LEFT)
        self.textbox_bandwidthh = wx.TextCtrl(cp.GetPane(),-1,"",size =(65,-1))
        advSizer.Add(self.textbox_bandwidthh, 0, wx.ALIGN_LEFT)
        
        txt_bdinfo = wx.StaticText(cp.GetPane(), -1, "(w/h:%.1f/%.1f)" % (w,h), size=(300,-1))
        advSizer.Add(txt_bdinfo, 0, wx.ALIGN_LEFT)
        
        border = wx.BoxSizer()
        border.Add(advSizer)
        cp.GetPane().SetSizer(border)
        sizer.Add(cp,0,wx.EXPAND)
        
        self.Bind(wx.EVT_COMBOBOX, self.OnBitmapCombo, self.cmbox_kde_colorschema)
        self.Bind(wx.EVT_TEXT, self.OnCellSizeChange, self.textbox_cellsize)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnOpaqueChange, self.slideralpha)
            
        self.guessParameters(400.0)
        
    def OnPaneChanged(self,event):
        self.Layout()
        offset = 50
        if self.cp.IsExpanded():
            self.advPanel.SetSize((310,30+offset))
            if os.name == 'posix':
                self.static_kde.SetSize((325,170+offset+50))
            else:
                self.static_kde.SetSize((325,170+offset))
            w,h = self.Size
            self.SetSize((w,h+offset))
            x,y = self.btn_query.GetPosition()
            self.btn_query.SetPosition((x,y+offset))
            self.btn_save.SetPosition((x+95,y+offset))
            self.btn_reset.SetPosition((x+125,y+offset))
            self.btn_cancel.SetPosition((x+215,y+offset))
            if self.isAddAccumOption:
                x,y = self.accu_kde.GetPosition()
                self.accu_kde.SetPosition((x,y+offset))
        else:
            if os.name == 'posix':
                self.advPanel.SetSize((310,30+20))
                self.static_kde.SetSize((325,170+50))
            else:
                self.advPanel.SetSize((310,30))
                self.static_kde.SetSize((325,170))
            w,h = self.Size
            self.SetSize((w,h-offset))
            x,y = self.btn_query.GetPosition()
            self.btn_query.SetPosition((x,y-offset))
            self.btn_save.SetPosition((x+95,y-offset))
            self.btn_reset.SetPosition((x+125,y-offset))
            self.btn_cancel.SetPosition((x+215,y-offset))
            if self.isAddAccumOption:
                x,y = self.accu_kde.GetPosition()
                self.accu_kde.SetPosition((x,y-offset))
            
    def add_accu_kde_option(self, x, y):
        self.accu_kde = wx.CheckBox(
            self.panel, -1, "Show cumulative density maps?",
            pos=(x, y), size=(280,-1) 
            )
        
    def OnDateFieldSelected(self, event):
        # step_by is not needed in Time Density Map
        super(DensityMapQueryDialog, self).OnDateFieldSelected(event)
        
        self.textbox_step.Enable(False)
        self.cmbox_step.Enable(False)
        
       
    def OnReset(self,event):
        self.reset()
        self.guessParameters(400.0)
        self.textbox_opaque.SetValue('80')
        self.slideralpha.SetValue(80)
        self.cmbox_kernel.SetSelection(0)
        self.cmbox_kde_colorschema.SetSelection(0)
        
    def OnOpaqueChange(self, event):
        self.textbox_opaque.SetValue('%s'% event.GetEventObject().GetValue())
             
    def guessParameters(self, guessLength):
        # guess a 400x?00 map
        cell_size = max(self.w / guessLength, self.h/guessLength)
        img_w, img_h = self.w/cell_size, self.h/cell_size
        self.cellsize_guess.SetLabel('(%d x %d image)' % (img_w,img_h))
        
        # get a optimized bandwidth: silverman (1986)
        # http://support.sas.com/documentation/cdl/en/statug/63033/HTML/default/viewer.htm#statug_kde_sect016.htm
        n = len(self.points_data.shape_objects)
        data = np.array(self.points_data.shape_objects)
        std_x,std_y = np.std(data,axis=0) 
        Q_x = scipy.stats.mstats.mquantiles(data[:,0])
        IQR_x = Q_x[2] -Q_x[0]
        Q_y = scipy.stats.mstats.mquantiles(data[:,1])
        IQR_y = Q_y[2] -Q_y[0]
        h_x = 0.9 * min(std_x, IQR_x/1.34)* pow(n, -0.2)
        h_y = 0.9 * min(std_y, IQR_y/1.34)* pow(n, -0.2)
        bandwidth = min(h_x,h_y)
        
        self.textbox_cellsize.SetValue('%s'%cell_size)
        self.textbox_bandwidthh.SetValue('%s'%bandwidth)
       
    def OnCellSizeChange(self, event):
        try:
            cell_size = float(event.GetString())
            img_w, img_h = self.w/cell_size, self.h/cell_size
            self.cellsize_guess.SetLabel('(%d x %d image)' % (img_w,img_h))
            # guess each cell impact 10 neigbors 
            bandwidth = cell_size * 10
            
            self.textbox_cellsize.SetValue('%s'%cell_size)
            self.textbox_bandwidthh.SetValue('%s'%bandwidth)
        except Exception as err:
            self.ShowMsgBox("cell size value not correct: " + str(err.message))
    
    def addColorBand(self, scheme_type):
        gradient_img = stars.GRADIENT_IMG_DICT[scheme_type]
        gradient_img = gradient_img.Rotate90()
        gradient_img = gradient_img.Scale(140,20)
        bmp = gradient_img.ConvertToBitmap()
        self.cmbox_kde_colorschema.Append(scheme_type, bmp, None)
        
    def OnBitmapCombo(self, event):
        bcb = event.GetEventObject()
        idx = event.GetInt()
        self.color_band  = bcb.GetString(idx)
        
    def _check_KDE_input(self):
        cell_size = self.textbox_cellsize.GetValue()
        bandwidth = self.textbox_bandwidthh.GetValue()
        kernel_method = self.cmbox_kernel.GetValue()
        opaque = self.textbox_opaque.GetValue()
       
        if len(cell_size) <= 0:
            self.ShowMsgBox("Cell size is empty.")
            return False
        if len(bandwidth) <= 0:
            self.ShowMsgBox("Bandwidth is empty.")
            return False
        kernels = ["quadratic","triangular","uniform","quartic","gaussian"]
        if kernels.count(kernel_method) <= 0:
            self.ShowMsgBox("Kernel method is not selected.")
            return False
        if len(opaque) <= 0:
            self.ShowMsgBox("Transparency is empty.")
            return False
        
        self.cell_size = float(cell_size)
        self.bandwidth = float(bandwidth)
        self.kernel_method = kernel_method
        self.opaque = float(opaque)
        return True
        
    def OnQuery(self,event):
        if self._check_KDE_input() == False:
            return
        
        self.current_selected = range(self.dbf.n_records)
        self._filter_by_query_field()
        self._filter_by_date()
        self._filter_by_date_interval()
        self._filter_by_tod()
       
        if len(self.current_selected) == 0:
            self.ShowMsgBox('No records match this query. Please respecify.')
            return
        
        background_layer = None 
        
        densityMap_widget= MapWidget(
            self.parent,
            [self.points_data],
            DensityMap,
            query_points=self.current_selected,
            #background=background_layer,
            cell_size=self.cell_size,
            bandwidth=self.bandwidth,
            kernel=self.kernel_method,
            opaque=self.opaque,
            color_band=self.color_band,
            title='Density Map'
            )
        densityMap_widget.Show()
        
        self.btn_save.Enable(True)
        
    def gen_date_by_step(self):
        """
        generate single density map data by STEP is not
        available case. STEP only works in dynamic density
        map scenario.
        """
        if len(self.step) > 0:
            self.ShowMsgBox("STEP BY only works with dynamic density maps.")
            
    def OnSaveQueryToDBF(self, event):
        """
        """
        dlg = wx.FileDialog(
            self, message="Save query as a dbf file...", defaultDir=os.getcwd(), 
            defaultFile='%s.dbf' % (self.points_data.name + '_query'), 
            wildcard="dbf file (*.dbf)|*.dbf|All files (*.*)|*.*", 
            style=wx.SAVE
            )
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        
        dbf = self.points_data.dbf
        
        newDBF= pysal.open(path,'w')
        newDBF.header = dbf.header
        newDBF.field_spec = dbf.field_spec
        newDBF.header.append('ISQUERYITEM')
        newDBF.field_spec.append(('N',4,0))
       
        for i,row in enumerate(dbf):
            if i in self.current_selected:
                row.append(1)
            newDBF.write(row)
        newDBF.close()
        
        self.ShowMsgBox("Query results have been saved in column 'ISQUERYITEM' of dbf file.",
                        mtype='Information',
                        micon=wx.ICON_INFORMATION)
            
