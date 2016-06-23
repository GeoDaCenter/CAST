"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["DynamicCalendarMap"]

import datetime,calendar,itertools
import os,sys,math
import wx
import numpy as np
import pysal

import stars
from ShapeMap import ShapeMap, ColorSchema 
from stars.visualization.DynamicControl import DynamicMapControl
from stars.visualization.dialogs import choose_field_name
from stars.visualization.maps import CalendarMap, ClassifyMapFactory, ClassifyMap
from stars.visualization.utils import View2ScreenTransform

class DynamicCalendarMap(CalendarMap):
    """
    """
    def __init__(self, parent, layers, **kwargs):
        CalendarMap.__init__(self,parent, layers, **kwargs)
        
        try:
            self.isDynamic = True
            
            # create unique value map for points data
            field_name = choose_field_name(self,self.layer,info="Choose a field for the map categories:")
            data = np.array(self.layer.dbf.by_col(field_name))
            
            factory = ClassifyMapFactory(data, field_name=field_name)
            id_group, label_group, color_group = factory.createClassifyMap(
                stars.MAP_CLASSIFY_UNIQUE_VALUES)
            
            if 'Others' in label_group:
                self.ShowMsgBox('CAST maps 12 unique values; other values will be shown in gray.',
                                mtype='CAST information',
                                micon=wx.ICON_INFORMATION)
              
            colorSchema = ColorSchema(color_group, label_group)
            self.color_schema_dict[self.layer.name] = colorSchema
            self.draw_layers[self.layer].set_opaque(10)
            self.draw_layers[self.layer].set_data_group(id_group)
            self.draw_layers[self.layer].set_fill_color_group(color_group)       
            
            self.label_group = label_group
            self.color_group = color_group
            self.num_id_group = len(color_group)
            self.id_group_dict = {}
            for i,group in enumerate(id_group):
                for item in group:
                    self.id_group_dict[item] = i
                    
            # ask user to specify day/week/month/year
            deltatime = self.end_date - self.start_date
            self.total_days = deltatime.days
            
            # Thread-based controller for dynamic map
            self.dynamic_control = DynamicMapControl(self.parentFrame,self.total_days,self.updateDraw) 
            self.dynamic_control.interval = 0.1
                    
            # setup controls
            self.SetTitle("Dynamic calender map - %s" % self.layer.name)
            self.parentWidget = self.parent.GetParent()
            self.slider = self.parentWidget.animate_slider
            self.parentWidget.label_start.SetLabel(
                '%2d/%2d/%4d'% (self.start_date.day,self.start_date.month,self.start_date.year)
                )
            self.parentWidget.label_end.SetLabel(
                '%2d/%2d/%4d'% (self.end_date.day,self.end_date.month,self.end_date.year)
                )
            self.setCurrentLabel()
            
            self._pie = None
            
            self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
            
        except Exception as err:
            self.ShowMsgBox("""Dynamic calendar map could not be created. Please choose a valid datetime variable and a valid variable for map classification.

Details:""" + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            if os.name == 'nt':
                self.Destroy()
            return None
            
    def setCurrentLabel(self):
        self.parentWidget.label_current.SetLabel(
            'current: %2d/%2d/%4d' % \
            (self.current_date.day, self.current_date.month, self.current_date.year))
        
    def updateDraw(self, tick):
        """
        When SLIDER is dragged
        """
        if tick == 0:
            return
        inc_days = datetime.timedelta(days=tick)
        self.current_date = self.start_date + inc_days
        self.setCurrentLabel()
        
        current_id_list = []
        for i in range(tick):
            tmp_date = self.start_date + datetime.timedelta(days=i)
            year_idx = tmp_date.year - self.start_date.year
            month_idx = tmp_date.month -1
            day_idx = tmp_date.day -1
            current_id_list += self.data_idx[year_idx][month_idx][day_idx]
            
        id_group = [[] for i in range(self.num_id_group)]
        for item in current_id_list:
            id_group[self.id_group_dict[item]].append(item)
            
        self.draw_layers[self.layer].set_opaque(255)
        self.draw_layers[self.layer].set_data_group(id_group)
        self.draw_layers[self.layer].set_fill_color_group(self.color_group)       
        
        self.selected_year = self.current_date.year - self.start_year
        if self.current_date.month == 1 or\
           self.current_date.month - 1 - self.selected_month > 1 or\
           self.selected_month >= self.current_date.month:
            self.selected_month = self.current_date.month -1
        self.reInitBuffer = True
        
    def OnLeftUp(self, event):
        if not self.HasCapture():
            return
        if self._pie != None:
            self._pie.Destroy()
            self._pie = None
            
        super(DynamicCalendarMap, self).OnLeftUp(event)
        
    def OnLeftDClick(self, event):
        x,y = event.GetX(),event.GetY()
        
        bDrawDetail = False
        year_idx = -1
        month_idx = -1
        
        year_idx = self.get_clicked_year(x,y)
        if year_idx >= 0:
            bDrawDetail = True
            self.selected_year = year_idx
        else:
            month_idx = self.get_clicked_month(x,y)
            if month_idx >= 0:
                self.selected_month = month_idx
                bDrawDetail = True

        if bDrawDetail:
            tmpBuffer = wx.EmptyBitmapRGBA(self.bufferWidth, self.bufferHeight,255,255,255,255)
            dc = wx.BufferedDC(None, tmpBuffer)
            if not 'Linux' in stars.APP_PLATFORM \
               and 'Darwin' != stars.APP_PLATFORM:
                dc = wx.GCDC(dc)
            dc.DrawBitmap(self.buffer,0,0)
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(wx.Colour(100,100,100,200)))
            dc.DrawRectangle(0,0,self.bufferWidth,self.bufferHeight)
            if year_idx >= 0:
                self.draw_year_detail(dc,year_idx)
            elif month_idx >= 0:
                self.draw_month_detail(dc, month_idx)
            self.buffer = tmpBuffer
            #dc.Destroy()
            self.Refresh(False)
            
    def draw_year_detail(self, dc, year_idx):
        """
        When double click YEAR box, a detailed information 
        will be shown on graph
        """
        start_year = self.start_date.year
        yr_rect_width =  self.bufferWidth * 0.6
        yr_rect_height = self.bufferHeight * 0.4
        yr_start_pos = (self.bufferWidth*0.05 - 15, self.bufferHeight*0.3) 
        
        yr_fill_color = wx.Colour(255,165,0)
        yr_font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial Black') 
        yr_font_color = wx.WHITE
        
        dc.SetBrush(wx.Brush(yr_fill_color))
        dc.DrawRectangle( 
            yr_start_pos[0],
            yr_start_pos[1], 
            yr_rect_width,
            yr_rect_height
            )
        dc.SetFont(yr_font)
        txt_year = str(start_year+year_idx)
        txt_year_w,txt_year_h = dc.GetTextExtent(txt_year)
        dc.DrawTextList(
            [txt_year], 
            [(yr_start_pos[0] +2,
            yr_start_pos[1] + 2)], 
            yr_font_color,None
            )
        # draw number
        dc.SetFont(wx.NORMAL_FONT)
        number = 'sum: ' + str(int(np.sum(self.data[year_idx])))
        txt_w,txt_h = dc.GetTextExtent(number)
        dc.DrawTextList(
            [number], 
            [(yr_start_pos[0] + txt_year_w + 10,\
              yr_start_pos[1] + 8)], 
            wx.BLACK,
            None
            )
        # draw histogram
        dc.SetPen(wx.Pen(wx.WHITE, 2))
        month_data = [ sum(m) for m in self.data[year_idx]]
        self.draw_histogram(
            dc, month_data,
            (yr_start_pos[0] + 2, yr_start_pos[1] + yr_rect_height),
            yr_rect_width -4,
            yr_rect_height - 50,
            brush=wx.Brush(wx.Colour(34,139,34)),
            enableInfo= True,
            infoLabels=self.mt_text_list
            )
        # draw pie char
        dataset = [0 for i in range(self.num_id_group)]
        selected_pts = []
        for mt_pts in self.data_idx[year_idx]:
            for pt_indice in mt_pts:
                for pt_idx in pt_indice:
                    group_idx = self.id_group_dict[pt_idx]
                    dataset[group_idx] += 1
        self.draw_pie_chart(dataset)

    def draw_month_detail(self, dc, month_idx):
        """
        """
        mt_rect_width = self.bufferWidth * 0.6
        mt_rect_height = self.bufferHeight * 0.4
        mt_start_pos = (self.bufferWidth*0.05 - 15, self.bufferHeight*0.3) 
        
        mt_font = wx.Font(12, wx.NORMAL, wx.NORMAL, wx.BOLD) 
        mt_font_color = wx.WHITE
        mt_fill_color = wx.Colour(0,191,255)
        mt_text = self.mt_text_list_full
        
        month_count = int(np.sum(self.data[self.selected_year][month_idx]))
        if month_count == 0:
            dc.SetBrush(wx.Brush(wx.Colour(200,200,200)))
        else:
            dc.SetBrush(wx.Brush(mt_fill_color))
        dc.DrawRectangle( 
            mt_start_pos[0],
            mt_start_pos[1], 
            mt_rect_width,
            mt_rect_height
            )
        dc.SetFont(mt_font)
        txt_month = '%s,%s' % (mt_text[month_idx], self.start_year+self.selected_year)
        txt_month_w,txt_month_h = dc.GetTextExtent(txt_month)
        dc.DrawTextList(
            [txt_month], 
            [(mt_start_pos[0] + 8,
              mt_start_pos[1] + 5)],
            wx.WHITE, None
            )
        # draw number
        number = 'sum:' + str(month_count)
        txt_w,txt_h = dc.GetTextExtent(number)
        mt_num_font = wx.Font(12, wx.NORMAL, wx.NORMAL, wx.NORMAL) 
        dc.SetFont(mt_num_font)
        dc.DrawTextList(
            [number], 
            [(mt_start_pos[0] + txt_month_w + 12,\
              mt_start_pos[1] + 5)],
            wx.BLACK, None
            )
        # draw histogram
        dc.SetPen(wx.Pen(wx.WHITE, 2))
        month_data = self.data[self.selected_year][month_idx]
        self.draw_histogram(
            dc, 
            month_data,
            (mt_start_pos[0]+2,\
             mt_start_pos[1] + mt_rect_height),
            mt_rect_width - 4,
            mt_rect_height - 35,
            brush=wx.Brush(wx.Colour(230,230,230)),
            enableInfo=True,
            infoLabels=[str(i) for i in range(1,32)]
            )
        # draw pie char
        dataset = [0 for i in range(self.num_id_group)]
        selected_pts = []
        mt_pts = self.data_idx[self.selected_year][month_idx]
        for pt_indice in mt_pts:
            for pt_idx in pt_indice:
                group_idx = self.id_group_dict[pt_idx]
                dataset[group_idx] += 1
        self.draw_pie_chart(dataset)
        
    def draw_pie_chart(self, dataset):
        """
        Pie chart information for detailed drawing on 
        given dataset
        """
        from wx.lib.agw.piectrl import PieCtrl, PiePart
        
        if self._pie:
            self._pie.Destroy()
            self._pie = None
        
        pos = self.bufferWidth*0.65, self.bufferHeight*0.3
        self._pie = PieCtrl(self, -1, pos, wx.Size(self.bufferHeight*0.4,self.bufferHeight*0.4))
        self._pie.SetBackColour(wx.Colour(133,133,133))
        #self._pie.SetTransparent(True)
        self._pie.GetLegend().SetTransparent(True)
        self._pie.GetLegend().SetHorizontalBorder(10)
        self._pie.GetLegend().SetWindowStyle(wx.NO_BORDER)
        self._pie.GetLegend().SetLabelFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL)
            )
        self._pie.GetLegend().SetLabelColour(wx.BLACK)	
        self._pie.SetShowEdges(False)
        self._pie.SetAngle(float(38/180.0*math.pi) )
        self._pie.SetHeight(30)
       
        for i in range(self.num_id_group):
            if self.color_group[i] != None:
                part = PiePart()
                number = dataset[i]
                if number == int(number):
                    number = int(number)
                number = str(number)
                part.SetLabel('%s: %s'% (self.label_group[i],number))
                part.SetValue(dataset[i])
                part.SetColour(self.color_group[i])
                self._pie._series.append(part)
