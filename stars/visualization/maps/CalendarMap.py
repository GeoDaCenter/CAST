"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["CalendarMap"]

import datetime,calendar,itertools
import sys,math
import wx
import numpy as np
import pysal

import stars
from ShapeMap import ShapeMap, ColorSchema 
from stars.visualization.dialogs import choose_field_name
from stars.visualization.utils import View2ScreenTransform, ColorBrewer
from stars.visualization.maps import ClassifyMap, ClassifyMapFactory

class CalendarMap(ShapeMap):
    """
    """
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
        try:
            # setup point layer color to white
            self.bufferWidth, self.bufferHeight = kwargs["size"]
            self.date_field = kwargs["date_field"]
            
            self.parent = parent
            layer = layers[0]
            self.layer = layer
            self.layers = layers
            
            self.extent = self.layer.extent
            self.view   = View2ScreenTransform(
                self.extent, 
                self.bufferWidth - 500, 
                self.bufferHeight - 150,
                offset_x = 500,
                offset_y = 150 
                )
           
            self.isDynamic = False
            self.all_date= self.layer.dbf.by_col(self.date_field,ctype='datetime')
            self.start_date = min(self.all_date)
            self.end_date = max(self.all_date)
            self.gradient_color = ColorBrewer()
            #self.gradient_color.set_colorschema(self.gradient_color.RdYlGn6, reverse=True)
            self.gradient_color.set_colorschema(self.gradient_color.BuGn9, reverse=False)
            
            if not isinstance(self.start_date, datetime.date):
                raise Exception("Please select a DateTime field to create Calendar Map!")
            
            # variables
            self.weekday_list = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
            self.mt_text_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            self.mt_text_list_full = ['January','Febuary','March','April','May','June','July',
                                      'August','September','October','November','December']
            self.start_year = self.start_date.year
            self.start_month = self.start_date.month
            self.end_year = self.end_date.year
            self.end_month = self.end_date.month
            
            self.selected_day = 0
            self.selected_year = 0
            self.selected_month = self.start_month - 1 
            self.num_years = self.end_year - self.start_year + 1
            self.current_date = self.start_date
            
            self.year_histogram = [False for i in range(self.num_years)]
            self.month_histogram = [False for i in range(12)]
            
            self.data_min,self.data_max = self.parseData()
            self.selected_obj_ids = []
            
        except Exception as err:
            self.ShowMsgBox("""Calendar map could not be created. Please choose a valid datetime variable.

Details: """ + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return None
            
    def OnSize(self,event):
        """
        """
        bufferWidth,bufferHeight = self.GetClientSize()
        if bufferWidth> 0 and bufferHeight > 0:
            self.bufferWidth = bufferWidth
            self.bufferHeight = bufferHeight
            if self.view:
                self.view.setup(self.bufferHeight-150,self.bufferWidth-500)
            self.reInitBuffer = True
            
    def OnMotion(self, event):
        """
        """
        if event.Dragging() and event.LeftIsDown() and self.isMouseDrawing:
            x, y = event.GetX(), event.GetY() 
            # while mouse is down and moving
            if self.map_operation_type == stars.MAP_OP_PAN:
                # disable PAN (not support in this version)
                return
                          
        # give the rest task to super class
        super(CalendarMap,self).OnMotion(event)
          
    def parseData(self):
        """
        Get how many events/points in each day
        Get what events/points in each day
        """
        data_min = 100
        data_max = 0
        self.data = [[np.zeros(31) for j in range(12)] for i in range(self.num_years)]
        self.data_idx = [[[list() for k in range(31)] for j in range(12)] for i in range(self.num_years)]
   
        for i,item in enumerate(self.all_date):
            year_idx  = item.year - self.start_year
            month_idx = item.month -1
            day_idx   = item.day -1
            
            self.data[year_idx][month_idx][day_idx] += 1
            self.data_idx[year_idx][month_idx][day_idx].append(i)
            if self.data[year_idx][month_idx][day_idx] > data_max:
                data_max = self.data[year_idx][month_idx][day_idx]
            if self.data[year_idx][month_idx][day_idx] < data_min:
                data_min = self.data[year_idx][month_idx][day_idx]
        return data_min, data_max
    
    #-----------------------------------------------
    # Drawing functions
    #-----------------------------------------------
    def get_pos_of_year(self, year_idx):
        x,y = self.yr_start_pos
        x = x + (self.yr_rect_width + 10) * year_idx
        y = y
        return x,y
    
    def get_pos_of_month(self, month_idx):
        x,y = self.mt_start_pos
        x = x + (self.mt_rect_width +5)*(month_idx -1)
        y = y #+ (self.mt_rect_height + 5)*(month_idx-1)
        return x,y
    
    def get_pos_of_day(self, day_idx):
        return 0,0
    
    def get_clicked_year(self, px,py):
        """ Get year index that mouse is currently clicking on """
        if py < self.yr_start_pos[1] or py > self.yr_start_pos[1] + self.yr_rect_height:
            return -1
        if px < self.yr_start_pos[0] or px > self.yr_start_pos[0] + (self.yr_rect_width+10)*self.num_years:
            return -1
        
        tmp_idx = (px - self.yr_start_pos[0]) / (self.yr_rect_width + 10)
        if tmp_idx > self.num_years -1:
            return -1
       
        if px > self.yr_start_pos[0] + (self.yr_rect_width +10)* tmp_idx and\
           px < self.yr_start_pos[0] + (self.yr_rect_width +10)* tmp_idx + self.yr_rect_width:
            return tmp_idx
        
        return -1
    
    def get_clicked_month(self,px,py):
        """ Get month index that mouse is currently clicking on """
        if px < self.mt_start_pos[0] or px > self.mt_start_pos[0] + (self.mt_rect_width+5)*12:
            return -1
        if py < self.mt_start_pos[1] or py > self.mt_start_pos[1] + self.mt_rect_height:
            return -1
        
        tmp_idx = (px - self.mt_start_pos[0]) / (self.mt_rect_width + 5)
        if tmp_idx > 11:
            return -1
        
        if px > self.mt_start_pos[0] + (self.mt_rect_width + 5)* tmp_idx and\
           px < self.mt_start_pos[0] + (self.mt_rect_width + 5)* tmp_idx + self.mt_rect_width:
            return  tmp_idx
        
        return -1
    
    def get_clicked_day(self,px,py):
        if px >= self.dy_start_pos[0] and py > self.dy_start_pos[1] \
           and px <= self.dy_start_pos[0] + self.calendar_width \
           and py <= self.dy_start_pos[1] + self.calendar_height:
            # test for 1st calendar
            pass

        elif self.selected_month < 11:
            if px >= self.dy_start_pos1[0] and py > self.dy_start_pos1[1] \
               and px <= self.dy_start_pos1[0] + self.calendar_width1 \
               and py <= self.dy_start_pos1[1] + self.calendar_height1:
                # test for 2nd calendar
                pass
        
    def draw_selected_year(self,dc, year_idx):
        """ Draw highlight red bar under selected year box"""
        pos = self.get_pos_of_year(year_idx)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.RED_BRUSH)
        dc.DrawRectangle(pos[0],pos[1] + self.yr_rect_height+2, self.yr_rect_width, 3)
       
    def draw_selected_month(self, dc, month_idx):
        """ Draw highlight red bar beside selected month box"""
        pos = self.get_pos_of_month(month_idx+1)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.RED_BRUSH)
        dc.DrawRectangle( pos[0], pos[1]+ self.mt_rect_height+2,self.mt_rect_width,3) 
        
    def draw_histogram(self, dc, data, start_pos, width, height, brush=wx.WHITE_BRUSH,enableInfo=False, infoLabels=None):
        num_bins = len(data)
        if num_bins == 0:
            return
        bin_width = width / float(num_bins)
        bin_max_height = height
        data_max = max(data)
        
        #dc.SetBrush(wx.Brush(wx.Colour(34,139,34)))
        dc.SetBrush(brush)
        
        for i,item in enumerate(data):
            if data_max == 0 or item ==0:
                bin_height = 3
            else: 
                bin_height = item / float(data_max) * bin_max_height -2
            x = start_pos[0] + bin_width * i
            y = start_pos[1] - bin_height
            dc.DrawRectangle( x, y, bin_width, bin_height)
            if enableInfo:
                if item==int(item):
                    item = int(item) 
                number = str(item)
                dc.SetFont(wx.NORMAL_FONT)
                txt_w,txt_h = dc.GetTextExtent(number)
                dc.DrawTextList(
                    [number],
                    [(x + (bin_width - txt_w)/2.0,y - txt_h)],
                    wx.BLACK,None
                   )
                mt_font = wx.Font(12, wx.NORMAL, wx.NORMAL, wx.BOLD) 
                dc.SetFont(mt_font)
                mt_txt = infoLabels[i]
                txt_w,txt_h = dc.GetTextExtent(mt_txt)
                dc.DrawTextList(
                    [infoLabels[i]],
                    [(x + (bin_width - txt_w)/2.0, y+bin_height+6)],
                    wx.WHITE, None
                    )
    
    def draw_year_list(self,dc):
        """ Draw all list years from points data """
        # draw year list
        start_year = self.start_year
        end_year = self.end_year
        
        yr_start_pos = self.yr_start_pos
        yr_rect_width =  self.yr_rect_width
        yr_rect_height = self.yr_rect_height 
        
        yr_fill_color = wx.Colour(255,165,0)
        #yr_font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial Black') 
        yr_font = eval(stars.HISTOGRAM_YEAR_FONT)
        yr_font_color = wx.WHITE
        
        for i in range(end_year - start_year+1):
            dc.SetBrush(wx.Brush(yr_fill_color))
            dc.DrawRectangle( 
                yr_start_pos[0] + i*(yr_rect_width+10),
                yr_start_pos[1], 
                yr_rect_width,
                yr_rect_height
            )
            dc.SetFont(yr_font)
            dc.DrawTextList(
                [str(start_year+i)], 
                [(yr_start_pos[0] + i*(yr_rect_width+10)+2,
                yr_start_pos[1] + 2)], 
                yr_font_color,None
            )
            # draw number
            dc.SetFont(wx.NORMAL_FONT)
            number = str(int(np.sum(self.data[i])))
            txt_w,txt_h = dc.GetTextExtent(number)
            dc.DrawTextList(
                [number], 
                [(yr_start_pos[0] + i*(yr_rect_width+10)+ yr_rect_width - txt_w -2,\
                  yr_start_pos[1] + 8)], 
                wx.BLACK,
                None
            )
            # draw histogram
            month_data = [ sum(m) for m in self.data[i]]
            self.draw_histogram(
                dc, month_data,
                (yr_start_pos[0] + i*(yr_rect_width +10)+2,
                yr_start_pos[1] + yr_rect_height),
                yr_rect_width -4,
                yr_rect_height - 25,
                brush=wx.Brush(wx.Colour(34,139,34))
            )
            
    def draw_month_list(self,dc):
        """ Draw all list months from points data """
        mt_start_pos = self.mt_start_pos 
        mt_rect_width = self.mt_rect_width
        mt_rect_height = self.mt_rect_height 
        
        #mt_font = wx.Font(12, wx.NORMAL, wx.NORMAL, wx.BOLD) 
        mt_font = eval(stars.HISTOGRAM_MONTH_FONT)
        mt_font_color = wx.WHITE
        mt_fill_color = wx.Colour(0,191,255)
        mt_text = self.mt_text_list_full
        
        for i in range(12):
            month_count = int(np.sum(self.data[self.selected_year][i]))
            if month_count == 0:
                background_color = wx.Colour(200,200,200)
            else:
                background_color = mt_fill_color
                
            dc.SetBrush(wx.Brush(background_color))
            dc.DrawRectangle( 
                #mt_start_pos[0],
                #mt_start_pos[1] + i*(mt_rect_height + 5), 
                mt_start_pos[0] + i*(mt_rect_width + 5),
                mt_start_pos[1], 
                mt_rect_width,
                mt_rect_height
            )
            dc.SetFont(mt_font)
            dc.DrawTextList(
                [mt_text[i]], 
                [(mt_start_pos[0] + 8 + i*(mt_rect_width + 5),
                mt_start_pos[1] + 5)],
                wx.WHITE, None
            )
            # draw number
            number = str(month_count)
            txt_w,txt_h = dc.GetTextExtent(number)
            #mt_num_font = wx.Font(12, wx.NORMAL, wx.NORMAL, wx.NORMAL) 
            mt_num_font = eval(stars.HISTOGRAM_MONTH_NUMBER_FONT)
            dc.SetFont(mt_num_font)
            dc.DrawTextList(
                [number], 
                [(mt_start_pos[0] + i*(mt_rect_width +5) + mt_rect_width - txt_w - 2,\
                  mt_start_pos[1] +  5)],
                wx.BLACK, None
            )
            # draw histogram
            month_data = self.data[self.selected_year][i]
            """
            self.draw_histogram(
                dc, 
                month_data,
                (mt_start_pos[0]+2 + i*(mt_rect_width + 5),\
                 mt_start_pos[1] +mt_rect_height),
                mt_rect_width - 4,
                mt_rect_height - 35,
                brush=wx.WHITE_BRUSH
            )
            """
            start_date = datetime.datetime(
                self.start_year + self.selected_year,
                i + 1, 1)
            self.draw_sub_calendar(
                dc,
                start_date,
                month_data,
                self.data_max,
                (mt_start_pos[0]+5 + i*(mt_rect_width + 5),\
                 mt_start_pos[1] + 20),
                mt_rect_width - 8,
                mt_rect_height -24,
                background_color
            )
                
    def draw_sub_calendar(self, dc, start_date, data, data_max, start_pos, width, height,bgcolor,
                          brush=wx.WHITE_BRUSH,enableInfo=False, infoLabels=None):
        n_rows = 6
        n_cols = 7
        cell_width = int(round(width / float(n_cols)))
        cell_height = int(round(height / float(n_rows)))
        
        # draw calendar first
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(200,200,200)))
        dc.DrawRectangle(start_pos[0], start_pos[1], 7*cell_width,6*cell_height)
        dc.SetPen(wx.Pen(wx.Colour(160,160,160),1))
        for i in range(n_rows+1):
            start_x = start_pos[0]
            start_y = start_pos[1] + i*cell_height
            end_x = start_x + 7*cell_width
            end_y = start_y
            dc.DrawLine(start_x, start_y, end_x, end_y)
        for i in range(n_cols+1):
            start_x = start_pos[0] + i*cell_width
            start_y = start_pos[1]
            end_x = start_x
            end_y = start_y + 6*cell_height
            dc.DrawLine(start_x, start_y, end_x, end_y)
            
        start_weekday = start_date.weekday()
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
        end_day_index = start_weekday + days_in_month
   
        dc.SetPen(wx.TRANSPARENT_PEN)
        count_day = 0
        for i in range(n_rows):
            for j in range(n_cols):
                if count_day < start_weekday:
                    # draw unavailable cell
                    dc.SetBrush(wx.Brush(bgcolor))
                    start_x = start_pos[0] + j*cell_width
                    start_y = start_pos[1] + i*cell_height
                    dc.DrawRectangle(start_x, start_y, cell_width,cell_height)
                elif count_day >= end_day_index:
                    dc.SetBrush(wx.Brush(bgcolor))
                    if j > 0:
                        start_x = start_pos[0] + j*cell_width+1
                    else:
                        start_x = start_pos[0]
                    start_y = start_pos[1] + i*cell_height+1
                    dc.DrawRectangle(start_x, start_y, cell_width+1,cell_height)
                else:
                    if sum(data) == 0:
                        color = bgcolor
                    else:
                        n_obs = data[count_day - start_weekday]
                        ratio = n_obs / data_max
                        color = self.gradient_color.get_color_at(ratio)
                    dc.SetBrush(wx.Brush(color))
                    start_x = start_pos[0] + j*cell_width+1
                    start_y = start_pos[1] + i*cell_height+1
                    dc.DrawRectangle(start_x, start_y, cell_width-1,cell_height-1)
                count_day += 1
                
    def draw_calendar(self,dc, start_pos, date):
        ca_start_weekday = date.weekday()
        day_range = calendar.monthrange(date.year, date.month)[1]
    
        # draw Month text
        month_text = self.mt_text_list_full[date.month-1]
        #month_font = wx.Font(38, wx.BOLD, wx.NORMAL,wx.NORMAL,False,'Arial Black')
        month_font = eval(stars.HISTOGRAM_MONTH_VERTICAL_FONT)
        dc.SetTextForeground(wx.Colour(200,200,200))
        dc.SetFont(month_font)
        mt_w,mt_h = dc.GetTextExtent(month_text)
        dc.DrawRotatedText(month_text, -22, start_pos[1]+mt_w + 40,90)
        dc.SetTextForeground(wx.BLACK)
       
        start_pos = list(start_pos)
        start_pos[0] += mt_h - 35
        ca_start_pos = start_pos
        
        skip_firstRow = False
        if date > self.start_date and ca_start_weekday > 0:
            skip_firstRow = True
            
        ca_cols = 7
        ca_rows = int(1 + math.ceil( (day_range - 7 + ca_start_weekday) / 7.0))-skip_firstRow
        ca_header_height = 20
        ca_tile_width = 50
        ca_tile_height = 52
        ca_width = float(ca_tile_width * ca_cols)
        ca_height = float(ca_header_height + ca_tile_height * ca_rows)

        ca_fill_color = wx.Colour(240,255,240)
        ca_highlight_fill_color = wx.Colour(33,102,172,255)
        #ca_font = wx.Font(12, wx.NORMAL, wx.NORMAL,wx.NORMAL)
        ca_font = eval(stars.HISTOGRAM_CALENDAR_NUMBER_FONT)
        ca_font_color = wx.BLACK
        
        dc.SetFont(ca_font)
       
        weekday_list = self.weekday_list
        weekday_pos_list = [(ca_start_pos[0] + i*ca_tile_width + 5,
                             ca_start_pos[1]) for i in range(7)]
        dc.DrawTextList( weekday_list, weekday_pos_list, ca_font_color)
        
        #ca_font = wx.Font(14, wx.DEFAULT, wx.NORMAL,wx.NORMAL,False,'Arial Black')
        ca_font = eval(stars.HISTOGRAM_CALENDAR_FONT)
        
        sum_matrix = np.zeros((ca_rows,ca_cols))
        day_count = 1 if not skip_firstRow else 7 - ca_start_weekday + 1
        current_drawing_date = datetime.datetime(date.year,date.month, day_count)
        
        # determine if current_drawing_date goes beyond data range
        year_idx = current_drawing_date.year - self.start_year
        if year_idx >= len(self.data):
            return
        
        for i in range(ca_rows):
            for j in range(ca_cols):
                start_calendar = True
                if not skip_firstRow:
                    if i*7 + j < ca_start_weekday:
                        start_calendar = False
                
                _number = 0
                
                if start_calendar:
                    year_idx = current_drawing_date.year - self.start_year
                    if year_idx >= len(self.data):
                        _number = 0
                    else:
                        month_idx = current_drawing_date.month - 1
                        day_idx = current_drawing_date.day -1
                        _number = self.data[year_idx][month_idx][day_idx]
                    
                    ratio = _number/self.data_max
                    if math.isnan(ratio): ratio = 0
                    color = self.gradient_color.get_color_at(ratio)
                    
                    dc.SetBrush(wx.Brush(color))
                    dc.DrawRectangle( 
                        ca_start_pos[0] + j*ca_tile_width,
                        ca_start_pos[1] + ca_header_height +i*ca_tile_height,
                        ca_tile_width-1,ca_tile_height-1
                    )
                    if self.isDynamic \
                       and self.start_date <= current_drawing_date <= self.current_date:
                        # redraw current cell, if current is highlighted
                        dc.SetBrush(wx.Brush(ca_highlight_fill_color))
                        dc.DrawRectangle( 
                            ca_start_pos[0] + j*ca_tile_width,
                            ca_start_pos[1] + ca_header_height +i*ca_tile_height,
                            ca_tile_width-1,ca_tile_height-1
                        )
                    current_drawing_date +=  datetime.timedelta(days=1)
                    
                    # draw Day
                    if day_count > day_range: 
                        # 27,28,29,30,1,2,3
                        day_count = 1
                        
                    dc.SetFont(ca_font)
                    dc.DrawTextList( 
                        [str(day_count)],
                        [(ca_start_pos[0] + j*ca_tile_width+2,
                        ca_start_pos[1] + ca_header_height +i*ca_tile_height+2)],
                        wx.BLACK, None
                    )
                    
                    # draw number
                    number = str( int(_number) )
                    txt_w,txt_h = dc.GetTextExtent(number)
                    dc.SetFont(wx.NORMAL_FONT)
                    dc.DrawTextList( 
                        [number],
                        [(ca_start_pos[0] + j*ca_tile_width+ ca_tile_width - txt_w-8,
                        ca_start_pos[1] + ca_header_height +i*ca_tile_height + ca_tile_height - txt_h)],
                        wx.Colour(50,50,50), None
                    )
                    day_count += 1
                sum_matrix[i][j] = _number 
                
        # draw sum_week histogram
        sum_week = sum_matrix.sum(axis=1)
        sum_day = sum_matrix.sum(axis=0)
        max_width = ca_tile_width - 10
        max_height = ca_tile_height - 10
        
        max_sum_week = max(sum_week)
        for i,item in enumerate(sum_week):
            if item ==0 or max_sum_week == 0:
                bar_width = 3
            else:
                bar_width = item /  max_sum_week * max_width
            bar_height = ca_tile_height-2
            
            #ratio = item/max_number
            #color = wx.Colour(247 - 247*ratio,252 - 184*ratio,253-226*ratio)
            color = wx.Colour(200,200,200)
            dc.SetBrush(wx.Brush(color))
            x = ca_start_pos[0] + ca_cols * ca_tile_width
            y = ca_start_pos[1] + ca_header_height + i*ca_tile_height
            dc.DrawRectangle(x,y,bar_width,bar_height) 
            if item > 0:
                dc.DrawTextList([str(int(item))], [(x+5,y+5)],wx.BLACK,None)

        max_sum_day = max(sum_day)
        for i,item in enumerate(sum_day):
            if item ==0 or max_sum_day== 0:
                bar_height = 3
            else:
                bar_height = item /  max_sum_day * max_height
            bar_width= ca_tile_width-2
            
            #ratio = item/max_number
            #color = wx.Colour(247 - 247*ratio,252 - 184*ratio,253-226*ratio)
            color = wx.Colour(200,200,200)
            
            dc.SetBrush(wx.Brush(color))
            y = ca_start_pos[1] + ca_header_height+ ca_rows * ca_tile_height
            x = ca_start_pos[0] + i*ca_tile_width
            dc.DrawRectangle(x,y,bar_width,bar_height) 
            if item > 0:
                dc.DrawTextList([str(int(item))], [(x+5,y+5)],wx.BLACK,None)
                
        return (ca_width,ca_height)
                
    def DoDraw(self, dc, isAppendDraw=False):
        super(CalendarMap,self).DoDraw(dc, isAppendDraw)
        
        dc.SetPen(wx.WHITE_PEN)
        self.yr_start_pos = (10,10)
        self.yr_rect_width = 100 
        self.yr_rect_height =50 
        self.draw_year_list(dc)
        
        # draw 12 months
        self.mt_start_pos = (10, 70)
        self.mt_rect_width =80 
        self.mt_rect_height = 60
        self.draw_month_list(dc)
        
        # draw selected year
        self.draw_selected_year(dc,self.selected_year)
        # draw selected month
        self.draw_selected_month(dc, self.selected_month)
        date = datetime.datetime(self.start_year+self.selected_year, self.selected_month+1, 1) 
        
        self.dy_start_pos = (10,150)
        # draw selected calendar
        calendar_width, calendar_height = self.draw_calendar(dc, self.dy_start_pos, date)
        self.calendar_height = calendar_height
        self.calendar_width = calendar_width
        if self.selected_month < 11:
            self.draw_selected_month(dc, self.selected_month+1)
            self.dy_start_pos1 = (10,200+calendar_height)
            # draw another calendar
            date = datetime.datetime(self.start_year+self.selected_year, self.selected_month+2, 1) 
            self.calendar_width1,self.calendar_height1= self.draw_calendar(dc, self.dy_start_pos1, date)
        
        # draw color legend
        self.gradient_color.draw_color_legend(
            dc, 
            "Legend for calendar",
            (10+ calendar_width+70, 150),
            30,
            18,
            str(int(self.data_min)),
            str(int(self.data_max))
            )
            
        # draw highlighted
        if len(self.selected_obj_ids) > 0:
            wx.FutureCall(10,self.drawHighlighted)
                          
    def drawHighlighted(self):
        self.draw_selected_by_ids({self.layer.name:self.selected_obj_ids})
        self.selected_obj_ids = []
        
    #-----------------------------------------------
    # Mouse events 
    #-----------------------------------------------
    def OnLeftUp(self, event):
        if not self.HasCapture():
            return
        
        if not self.buffer:
            return
       
        self.mouse_end_pos = (event.GetX(), event.GetY())
        screen_region = self.mouse_start_pos+self.mouse_end_pos
        select_w = abs(self.mouse_end_pos[0] - self.mouse_start_pos[0])
        select_h = abs(self.mouse_end_pos[1] - self.mouse_start_pos[1])
        
        if select_w ==0 and select_h == 0:
            x,y = event.GetX(),event.GetY()
            year_idx = self.get_clicked_year(x,y)
            if year_idx >= 0:
                if year_idx != self.selected_year:
                    self.selected_year = year_idx
                    self.selected_month = 0
                    self.year_histogram[self.selected_year] = False
                    self.reInitBuffer = True
            else:
                month_idx = self.get_clicked_month(x,y)
                if month_idx >= 0:
                    if month_idx != self.selected_month:
                        self.selected_month = month_idx
                        self.month_histogram[self.selected_month] = False
                        self.reInitBuffer = True
                else:
                    pass
                
        # pass rest event to parent handler
        super(CalendarMap, self).OnLeftUp(event)
       
        
    def OnRightUp(self, event):
        x,y = event.GetX(),event.GetY()
        
        year_idx = self.get_clicked_year(x,y)
        if year_idx >= 0:
            self.selected_year = year_idx
            self.year_histogram[self.selected_year] = True
            self.selected_obj_ids= \
                list(itertools.chain(
                    *list(itertools.chain(*self.data_idx[self.selected_year]))
                    ))
            self.reInitBuffer = True
        else:
            month_idx = self.get_clicked_month(x,y)
            if month_idx >= 0:
                self.selected_month = month_idx
                self.month_histogram[self.selected_month] = True
                self.selected_obj_ids = \
                    list(itertools.chain(
                        *self.data_idx[self.selected_year][self.selected_month])
                         )
                # self.draw_selected_by_ids({self.layer.name: selected_ids})
                self.reInitBuffer = True
            else:
                pass
            
