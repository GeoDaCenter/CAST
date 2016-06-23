"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['View2ScreenTransform']

class View2ScreenTransform():
    def __init__(self,viewExtent,pixel_width,pixel_height, offset_x=0,offset_y=0, fixed_ratio=True):
        """ Intialize the view to the extent of the view """
        self.original_extent = viewExtent
        self.extent = viewExtent
        self.zoom_extent = []
        self.fixed_ratio = fixed_ratio
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.reset()
        self.setup(pixel_height,pixel_width)
        
    def setup(self, pixel_height,pixel_width):
        self.pixel_width = float(pixel_width)
        self.pixel_height = float(pixel_height)
        if self.pixel_height > 0 and self.pixel_width:
            self.init()
        
    def reset(self):
        self.extent = self.original_extent
        self.zoom_extent = self.extent
        self.startX = 0
        self.startY = 0
        # zoom scale
        self.scale = 0.9  # default for displaying map
        self.scaleX = 0.9
        self.scaleY = 0.9
        # ratio = screen:view
        self.ratio = 0 
        self.ratioX = .0
        self.ratioY = .0
        # for panning
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
    def init(self):
        extent = self.extent
        if len(self.zoom_extent)>0:
            extent = self.zoom_extent
            
        self.view_width = abs(extent[0]-extent[2])
        self.view_height = abs(extent[1]-extent[3])
        
        if self.fixed_ratio: # map_to_screen needs fixed ratio
            if self.pixel_width / self.pixel_height < self.view_width/self.view_height:
                self.ratioX= self.ratioY = self.pixel_width / self.view_width
                self.startY = (self.pixel_height - self.view_height * self.ratioY) / 2.0
            else:
                self.ratioY = self.ratioX = self.pixel_height/ self.view_height
                self.startX = (self.pixel_width - self.view_width * self.ratioX) / 2.0
            self.scaleX = self.scaleY = self.scale
        else:
            self.ratioX= self.pixel_width / self.view_width
            self.ratioY= self.pixel_height/ self.view_height
            
        self.marginX = self.pixel_width*(1-self.scaleX)/2.0
        self.marginY = self.pixel_height*(1-self.scaleY)/2.0
        
            
    def set_scaleX(self,scaleX):
        self.scaleX = scaleX
        self.marginX = self.pixel_width*(1-self.scaleX)/2.0
        
    def set_scaleY(self,scaleY):
        self.scaleY = scaleY
        self.marginY = self.pixel_height*(1-self.scaleY)/2.0
       
    def restore(self):
        self.reset()
        self.init()
        
    def zoom(self, p_extent):
        px0,py0, px,py = p_extent
        x0,y0 = min(px0,px), min(py0,py)        
        x,y = max(px0,px), max(py0,py)        
        
        vx0,vy0 = self.pixel_to_view(x0,y0)
        vx,vy = self.pixel_to_view(x,y)
        
        #self.extent = (vx0,vy,vx,vy0)
        self.zoom_extent = [vx0, vy, vx, vy0]
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        self.init()
        
    def pan(self,dpx,dpy):
        self.pan_offset_x += dpx/self.scaleX
        self.pan_offset_y += dpy/self.scaleY
        
    def pan_to(self, x,y,dpx,dpy):
        return x+dpx, y+dpy
        
    def get_one_pixel_view(self):
        x = 1.0 / self.ratioX / self.scaleX
        y = 1.0 / self.ratioY / self.scaleY
        return x,y
        
    def view_length_to_pixel(self, v_len, is_horizontal=True):
        """
        Returns the length in pixel
        """
        if is_horizontal:
            pixel_len = v_len * self.ratioX * self.scaleX
        else:
            pixel_len = v_len * self.ratioY * self.scaleY
            
        return int(pixel_len)
     

    def batch_view_to_pixel(self, points, offset_from_upperleft=True):
        import numpy as np
        
        points = np.array(points.shape_objects)
        xs = ((points[:,0] - self.extent[0]) * self.ratioX + self.startX)*self.scaleX + self.offset_x + self.marginX
        ys = (self.pixel_height - (points[:,1] - self.extent[1])*self.ratioY - self.startY)*self.scaleY + self.marginY
        return np.column_stack((xs,ys)).tolist()
    
       
    def view_to_pixel(self,x,y):
        """
        Returns the pixel of the view coordinate (x,y).
        """
        px = self.pan_offset_x + self.startX + self.ratioX * (x - self.extent[0])
        px = self.offset_x + px * self.scaleX + self.marginX 
        py = self.pixel_height - (self.pan_offset_y + self.startY + self.ratioY* (y - self.extent[1]))
        py = self.offset_y + py * self.scaleY + self.marginY
            
        return px,py

    def pixel_to_view(self,px,py):
        """
        Returns the view coordinates of the Pixel (px,py).
        (The inverse of view_to_pixel)
        """
        px = (px - self.marginX - self.offset_x) /self.scaleX
        x = (px - self.startX - self.pan_offset_x) / self.ratioX + self.extent[0]
        
        py = (py - self.marginY - self.offset_y) /self.scaleY
        y = (self.pixel_height - py - self.startY - self.pan_offset_y) / self.ratioY + self.extent[1]
        
        return x,y
