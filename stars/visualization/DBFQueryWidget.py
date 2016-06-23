"""
"""
__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['DBFQueryWidget']

import re, datetime
import wx
import wx.lib.masked as masked
import pysal

from stars.model.ShapeObject import *
#from stars.visualization.AbstractCanvas import *

def _pydate2wxdate(date): 
    tt = date.timetuple() 
    dmy = (tt[2], tt[1]-1, tt[0]) 
    return wx.DateTimeFromDMY(*dmy) 

def _wxdate2pydate(date): 
    if date.IsValid(): 
        ymd = map(int, date.FormatISODate().split('-')) 
        return datetime.date(*ymd) 
    else: 
        return None

class DBFQueryWidget(wx.Frame):
    """
    """
    
    def __init__(self, parent, title, points_data,background_shp):
        wx.Frame.__init__(self, parent, -1, title, pos=(20, 20), size=(360, 490))
        
        self.parent = parent
        self.points_data = points_data
        self.points = self.points_data.shape_objects
        self.dbf = self.points_data.dbf
        self.background_shp = background_shp
        self.CreateStatusBar()
        
        panel = wx.Panel(self,-1)
        self.panel = panel
       

    
