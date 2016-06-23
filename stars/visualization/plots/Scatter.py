"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['Scatter']

import wx
import numpy as np
from scipy.stats import linregress

import stars
from stars.stats.ols import ols
from stars.stats.chow import chow
from stars.visualization.EventHandler import AbstractData
from stars.visualization.PlotWidget import PlottingCanvas
from stars.visualization.utils import *

class Scatter(PlottingCanvas):
    def __init__(self,parent,layer, data,**kwargs):
        try:
            PlottingCanvas.__init__(self,parent,data)
          
            self.margin_top  = 70
            self.margin_left = 70
            self.layer_name  = layer.name 
            
            self.data = data
            var_names = data.keys()
            x_label   = var_names[0]
            y_label   = var_names[1] if len(var_names)>1 else x_label
           
            self.parentFrame.SetTitle = 'Scatter plot-%s' % self.layer_name
            self.title   = ''
            self.x_label = x_label 
            self.y_label = y_label
            
            self.x, self.y = data[x_label],data[y_label]
            
            self.n = len(self.x)
            self.x_min, self.x_max = min(self.x), max(self.x)
            self.y_min, self.y_max = min(self.y), max(self.y)
            self.x_min -= 0
            self.y_min -= 0
            self.extent = (self.x_min, self.y_min, self.x_max,self.y_max)
            
            # test data
            float(self.x_min)
            float(self.y_min)
            
            self.selected_pts = []
            self.status_bar = None
            
            
        except Exception as err:
            self.ShowMsgBox("""Scatter plot could not be created. 
            
Detail: """+ str(err.message))
            self.isValidPlot = False
            self.parentFrame.Close(True)
            return None
        
        # linking-brushing events
        self.Register(stars.EVT_OBJS_SELECT, self.OnPointsSelected)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoPointSelect)

    def OnClose(self,event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnPointsSelected)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoPointSelect)
        event.Skip()
        
    def plot_data(self,dc):
        pts = [self.point_to_screen(self.x[i],self.y[i]) for i in range(self.n)]
        DrawPoints(dc,pts,fill_color=wx.WHITE)
        
        dc.SetFont(wx.Font(stars.SCATTER_STATS_FONT_SIZE,wx.ROMAN,wx.NORMAL,wx.NORMAL))
        labels = ('#obs','R^2','const a','std-err a', 't-stat a','p-value a','slope b','std-err b', 't-stat b','p-value b')
        start_pos_x = self.ax_start_x
        self.start_pos_x = start_pos_x
        start_pos_y = 5
        self.start_pos_y = start_pos_y
        stats_label = '{0:<18}'.format(labels[0])
        stats_lbl_w, stats_lbl_h = dc.GetTextExtent(stats_label)
        dc.DrawText("", start_pos_x, start_pos_y)
        for item in labels:
            start_pos_x += stats_lbl_w
            dc.DrawText(item, start_pos_x, start_pos_y)
            
        self.stats_lbl_h = stats_lbl_h
        self.stats_lbl_w = stats_lbl_w
        
        self.draw_regression_lines(dc, self.x, self.y, wx.Color(255,10,205),start_pos_y + stats_lbl_h, "All:")
        self.draw_selected(dc)
        
    def draw_regression_lines(self, dc, X, Y, color, pos_y, title):
        # draw regression lines
        pen = wx.Pen(color)
        dc.SetPen(pen)
        dc.SetTextForeground(color)
        n_obs = len(Y)
        pos_x = self.ax_start_x
        dc.DrawText(title, pos_x, pos_y)
        try:
            if n_obs < 2:
                raise Exception
            model = ols(np.array(Y),np.array(X))
            intercept = model.b[0]
            slope = model.b[1]
            
            x0,x1 = self.x_min, self.x_max
            y_min,y_max = self.y_min, self.y_max
            
            y0_hat = x0*slope + intercept
            y1_hat = x1*slope + intercept
            
            if y0_hat < y_min:
                # need use y_min as lower bound
                y0_hat = y_min
                x0 = (y0_hat - intercept) / slope
            elif y0_hat > y_max:
                y0_hat = y_max
                x0 = (y0_hat - intercept) / slope
                
            if y1_hat < y_min:
                # need use y_max as upper bound
                y1_hat = y_min
                x1 = (y1_hat - intercept) / slope
            elif y1_hat > y_max:
                # need use y_max as upper bound
                y1_hat = y_max
                x1 = (y1_hat - intercept) / slope
               
            x0,y0_hat = self.point_to_screen(x0,y0_hat)
            x1,y1_hat = self.point_to_screen(x1,y1_hat)
            dc.DrawLine(x0,y0_hat, x1,y1_hat)
            values = [model.nobs, model.R2, model.b[0],model.se[0],model.t[0],
                      model.p[0], model.b[1], model.se[1], model.t[1], model.p[1]]
            for item in values:
                item = str(item) if isinstance(item,int) else '%.3f'%item
                pos_x += self.stats_lbl_w
                dc.DrawText(item, pos_x, pos_y)
        except:
            dc.DrawText("", pos_x, pos_y)
            values = (n_obs, 0,0,0,0,0,0,0,0,0)
            for item in values:
                pos_x += self.stats_lbl_w
                dc.DrawText(str(item), pos_x, pos_y)
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
    def draw_selected(self,dc=None):
        if len(self.selected_pts) > 0:
            if dc == None:
                # draw selected on client DC
                
                dc = wx.ClientDC(self)
                if self.drawing_backup_buffer:
                    dc.DrawBitmap(self.drawing_backup_buffer,0,0)
                else:
                    dc.DrawBitmap(self.buffer,0,0)
                
            if not isinstance(dc, wx.GCDC):
                dc = wx.GCDC(dc)
            
            points = [(self.x[i],self.y[i]) for i in self.selected_pts]
            points = list(set(points))
            pts = [self.view.view_to_pixel(p[0],p[1]) for p in points]
            pts = [self.view.pan_to(p[0],p[1],self.margin_left,self.margin_top) for p in pts]
            DrawPoints(dc,pts,fill_color=wx.RED) 
           
            s_X = []; s_Y=[]
            for i in self.selected_pts:
                s_X.append(self.x[i])
                s_Y.append(self.y[i])
             
            dc.SetFont(wx.Font(stars.SCATTER_STATS_FONT_SIZE,wx.ROMAN,wx.NORMAL,wx.NORMAL))
            start_pos_x = self.start_pos_x + self.stats_lbl_w
            start_pos_y = self.start_pos_y
            stats_lbl_h = self.stats_lbl_h
            
            # OLS for selected points
            self.draw_regression_lines(dc, s_X, s_Y, wx.RED, start_pos_y + 2*stats_lbl_h, "Selected:")
            # OLS for un-selected points
            unselected_ids = set(range(self.n)) - set(self.selected_pts)
            us_X = []; us_Y= []
            for i in unselected_ids:
                us_X.append(self.x[i])
                us_Y.append(self.y[i])
            self.draw_regression_lines(dc, us_X, us_Y, wx.BLUE, start_pos_y + 3*stats_lbl_h, "UnSelected:")
            
            # Chow test for selected vs un-selected
            dc.SetTextForeground(wx.BLACK)
            try:
                if len(self.selected_pts) <= 2:
                    raise Exception("too few points selected!")
                rst = chow(np.array(self.x),np.array(self.y),
                           np.array(s_X),np.array(s_Y),
                           np.array(us_X),np.array(us_Y))
                lbl = 'Chow test for sel/unsel regression subsets: distrib=F(%d,%d), ratio=%s, p-val=%s'\
                    % (rst[3],rst[4],'%.3f'%rst[0],'%.3f'%rst[1])
            except:
                lbl = 'Chow test for sel/unsel regression subsets: needs two valid regressions'
            dc.DrawText(lbl, start_pos_x, start_pos_y + 4*stats_lbl_h+4)
    
    def draw_selected_by_region(self, dc,select_region, isScreenCoordinates=True):
        """
        this function highlight the points selected 
        by mouse drawing a region
        """
        self.selected_pts = []
        x0,y0,x1,y1= select_region
        
        x0,y0 = self.view.pan_to(x0,y0,-self.margin_left,-self.margin_top)
        x1,y1 = self.view.pan_to(x1,y1,-self.margin_left,-self.margin_top)
        x0,y0 = self.view.pixel_to_view(x0,y0)
        x1,y1 = self.view.pixel_to_view(x1,y1)
        
        # test each point
        for i in range(self.n):
            x,y = self.x[i],self.y[i]
            if (x0<=x<=x1 or x1<=x<=x0) and (y0<=y<=y1 or y1<=y<=y0):
                self.selected_pts.append(i)
        self.draw_selected(dc)
        
        if len(self.selected_pts)>0:
            # draw selected
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.shape_ids[self.layer_name] = self.selected_pts
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # unselect all
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            self.UpdateEvt(stars.EVT_OBJS_UNSELECT,data)
        
    def OnPointsSelected(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        event is an instance of EventHandler.Event class
        event.object are the data for selecting shape objects
        """
        if not event: return
        
        data = event.data
        if len(data.shape_ids) > 0:
            # directly select by shape_ids
            if data.shape_ids.has_key(self.layer_name):
                self.selected_pts = data.shape_ids[self.layer_name]
                self.draw_selected()
                
    def OnNoPointSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        Normally, event could be None, you just need to clean and refresh
        you selected/highlighted
        """
        self.selected_pts = []
        self.Refresh(False)


