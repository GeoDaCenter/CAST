"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['GradientColor','ColorBrewer']

import random,os
import wx
import stars

class GradientColor():
    def __init__(self, gradient_type='classic'):
        self.gradient_img = stars.GRADIENT_IMG_DICT[gradient_type]
        self.gradient_img_width, self.gradient_img_height = self.gradient_img.GetSize()
        
        assert self.gradient_img_height == 256
        
        self.color_scheme = self.getColorSchema()
        
    def getColorSchema(self):
        color_scheme = []
        reds = []
        greens = []
        blues = []
        for i in range(0,256):
            red = self.gradient_img.GetRed(1,i)
            green = self.gradient_img.GetGreen(1,i)
            blue = self.gradient_img.GetBlue(1,i)
            clr = wx.Colour(red,green,blue)
            color_scheme.append(clr)
            reds.append(red)
            greens.append(green)
            blues.append(blue)
        return color_scheme
    
    def get_rgb_at(self,pos):
        clr = self.get_color_at(pos)
        return clr.red, clr.green, clr.blue
    
    def get_color_at(self, pos):
        """
        pos: float, [0,1]
        """
        rgb_pos = int(255 * (1-pos))
        return self.color_scheme[rgb_pos]
    
    def get_bmp(self, width=None, height=None):
        """
        get a bitmap version of images by scaling it with
        input width and height
        """
        img = self.gradient_img
        if width!= None and height!= None:
            img = img.Scale(width,height,wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(img)
        return bmp
    
class ColorBrewer():
    def __init__(self,):
        self.YlOrBr9 = [wx.Colour(255,255,229),
                        wx.Colour(255,247,188),
                        wx.Colour(254,227,145),
                        wx.Colour(254,196,79),
                        wx.Colour(254,153,41),
                        wx.Colour(236,112,20),
                        wx.Colour(204,76,2),
                        wx.Colour(153,52,4),
                        wx.Colour(102,37,6)]
                        
        self.BuGn9 = [wx.Colour(255,255,229),
                      wx.Colour(247,252,185),
                      wx.Colour(217,240,163),
                      wx.Colour(173,221,142),
                      wx.Colour(120,198,121),
                      wx.Colour(65,171,93),
                      wx.Colour(35,132,67),
                      wx.Colour(0,104,55),
                      wx.Colour(0,69,41) ]
        
        # diverging
        self.RdYlGn6 = [wx.Colour(215,48,39), 
                        wx.Colour(252,141,89),
                        wx.Colour(254,224,139),
                        wx.Colour(217,239,139),
                        wx.Colour(145,207,96),
                        wx.Colour(26,152,80)]
                        
        self.colorschema = self.BuGn9
        
    def set_colorschema(self,cs,reverse=False):
        if reverse:
            self.colorschema = cs[::-1]
        else:
            self.colorschema = cs
        
    def get_color_at(self, p):
        interval = 1.0 / (len(self.colorschema)-1)
        idx = int(p / interval)
        return self.colorschema[idx]
        
    def draw_color_legend(self,dc, title, start_pos,width,height,left_lbl,right_lbl):
        start_x = start_pos[0]; start_y = start_pos[1]
        font    = stars.COLORBREWER_LEGEND_FONT
        dc.SetFont(eval(font))
        dc.DrawText(title, start_x, start_y)
        start_y += 20
        for i,clr in enumerate(self.colorschema):
            dc.SetBrush(wx.Brush(clr))
            dc.DrawRectangle(start_x, start_y, width, height)
            start_x = start_x + width
            
        start_x = start_pos[0]; start_y = start_pos[1]+30+height
        dc.DrawText(left_lbl, start_x, start_y)
        
        lbl_w,lbl_h = dc.GetTextExtent(right_lbl)
        start_x = start_pos[0] + len(self.colorschema)*width - lbl_w
        dc.DrawText(right_lbl, start_x, start_y)
