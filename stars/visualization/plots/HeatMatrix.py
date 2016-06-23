"""
"""
__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['HeatMatrix']

import math
import wx
import numpy as np

from stars.visualization.utils import GradientColor
from stars.visualization.PlotWidget import PlottingCanvas

class HeatMatrix(PlottingCanvas):
    def __init__(self,parent, layer, data,**kwargs):
        PlottingCanvas.__init__(self,parent,data)
        
        try:
            self.layer_name = layer.name
            self.title = "Transition probility matrix (%s)" % self.layer_name
            self.x_label = "LISA transition states (1=HH,2=LH,3=LL,4=HL)"
            self.y_label = "LISA transition states"
            self.data = data
            n = len(self.data)
            self.enable_axis_labels = False
            self.enable_axis = True
            self.enable_axis_x = False
            self.enable_axis_y = False
           
            # a NxN matrix
            self.x_min = 1
            self.x_max = n+1 
            self.y_min = 1
            self.y_max = n+1
            
            self.extent = (self.x_min, self.y_min, self.x_max,self.y_max)
            self.selected_polygon_ids = []
            self.status_bar = self.parentFrame.status_bar
            
            self.gradient_color = GradientColor(gradient_type='rdyibu')
            self.margin_right = 100
            
            # color schema: from blue to red
            self.color_matrix = []
            for i in range(n):
                color_row = []
                for j in range(n):
                    p = self.data[i][j]
                    color_row.append( self.gradient_color.get_color_at(p))
                self.color_matrix.append(color_row)
                
        except Exception as err:
            self.ShowMsgBox('Fail to init heat map! ' + str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
        
    def OnClose(self,event):
        event.Skip()
    
    def plot_data(self,dc):
        # draw a NxN matrix
        w,h = 1,1
        for i,row in enumerate(self.data):
            for j,item in enumerate(row):
                start_x = j + self.x_min
                start_y = self.y_max - i
                
                pixel_x,pixel_y = self.point_to_screen(start_x,start_y)
                pixel_w,pixel_h = math.ceil(self.length_to_screen(w)),math.ceil(self.length_to_screen(h,axis=1))
                
                brush = wx.Brush(self.color_matrix[i][j])
                dc.SetBrush(brush)
                dc.DrawRectangle(pixel_x,pixel_y,pixel_w,pixel_h)
              
                if i==len(self.data)-1:
                    dc.DrawText(str(j+1), pixel_x + pixel_w/2, pixel_y+pixel_h+5)
                if j==0:
                    dc.DrawText(str(len(self.data)-i), pixel_x - 10, pixel_y + pixel_h/2)
                        
                text_pixel_x, text_pixel_y = pixel_x + pixel_w/2.0 - 10, pixel_y + pixel_h / 2.0
                dc.SetPen(wx.WHITE_PEN)
                dc.SetBrush(wx.WHITE_BRUSH)
                dc.DrawText('%.4f'%(self.data[i][j]), text_pixel_x,text_pixel_y) 
                
        # draw a legend bar
        pixel_x,pixel_y = self.point_to_screen( start_x+w, self.y_max)
        pixel_x += 20
        pixel_h = self.length_to_screen(self.y_max-self.y_min,axis=1)
        pixel_w = 20
        
        gradient_colorbar = self.gradient_color.get_bmp(pixel_w, pixel_h)
        dc.DrawBitmap( gradient_colorbar, pixel_x, pixel_y)
        
        pixel_x = pixel_x + pixel_w + 10
        dc.SetPen(wx.BLACK_PEN)
        dc.DrawText(str('%.2f'% np.max(self.data)), pixel_x,pixel_y)
        pixel_y = pixel_y + pixel_h - 12 
        dc.DrawText(str('%.2f'% np.min(self.data)), pixel_x,pixel_y)
