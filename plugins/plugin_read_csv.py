import math,os
import wx
from wx import xrc
import numpy as np
import pysal

import stars
from stars.visualization import MapWidget
from stars.visualization.maps import ShapeMap, ColorSchema 
from stars.visualization.utils import FilterShapeList
from stars.visualization.dialogs import VariableSelDialog
from stars.Plugin import *

class ReadShapeFromCSV(IMapPlugin):
    def __init__(self):
        IMapPlugin.__init__(self)
        
    def get_icon(self):
        new_bmp =  wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (16,16))
        return new_bmp
    
    def get_icon_size(self):
        return (16,16)
    
    def get_label(self):
        return 'Read points from CSV'
   
    def get_shortHelp(self):
        return ''
    
    def get_longHelp(self):
        return ''
    
    def get_toolbar_pos(self):
        return -1
    
    def get_parent_menu(self):
        return 'File'
    
    def show(self, event):
        main = event.EventObject.GetParent()

        dlg_res = xrc.XmlResource(os.path.join(os.getcwd(), 'plugins/read_csv.xrc'))
        dlg = ReadShapeObjectFromCSVDlg(main,dlg_res)
        
        if dlg.Show() == True:
            if dlg.shp == None:
                main.ShowMsgBox('Sorry, read csv to create shape object failed.')
                return
            csvMap= MapWidget(main,[dlg.shp],ShapeMap)
            csvMap.Show()
        
        
class ReadShapeObjectFromCSVDlg():
    def __init__(self, main, resource):
        self.main = main
        self.resource = resource
        self.dlg = resource.LoadDialog(None, 'IDD_READ_CSV')
       
        self.csv = []
        self.shp = None
        self.csv_path = xrc.XRCCTRL(self.dlg, 'IDC_EDIT1')
        self.delimiter_txt = xrc.XRCCTRL(self.dlg, 'IDC_DELIMITER')
        self.header_rdo = xrc.XRCCTRL(self.dlg, 'IDC_HEADER')
        self.btn_opencsv = xrc.XRCCTRL(self.dlg, 'IDC_OPEN_CSV')
        self.cbox_xcoords = xrc.XRCCTRL(self.dlg, 'IDC_XCOORDINATES')
        self.cbox_ycoords = xrc.XRCCTRL(self.dlg, 'IDC_YCOORDINATES')
        
        self.dlg.Bind(wx.EVT_BUTTON, self.OnOpenCSV, self.btn_opencsv)
        
    def OnOpenCSV(self, event):
        dlg = wx.FileDialog(
            self.main, 
            message="Choose a file", 
            wildcard="CSV file (*.csv)|*.csv|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            try:
                csv_path = dlg.GetPath()
                self.csv_path.SetValue(csv_path)
                hasHeader = self.header_rdo.GetValue()
                delimiter = str(self.delimiter_txt.GetValue())
                if len(delimiter) == 0: delimiter = ','
                
                f = open(csv_path)
                if hasHeader:
                    header = f.readline()
                line = f.readline()
                while len(line) > 0:
                    row = line.strip().split(delimiter)
                    self.csv.append(row)
                    line = f.readline()
                f.close()
                if not hasHeader:
                    header = self.csv[0]
                    
                self.cbox_xcoords.SetItems(header)
                self.cbox_ycoords.SetItems(header)
            except:
                self.csv = []
                self.main.ShowMsgBox('Open CSV file error.')
        dlg.Destroy()
        
    def ReadShapeObject(self):
        from stars.model import CShapeFileObject
        
        xCol = self.cbox_xcoords.GetCurrentSelection()
        yCol = self.cbox_ycoords.GetCurrentSelection()

        assert xCol != yCol
       
        point_set = []
        for row in self.csv:
            try:
                x = float(row[xCol])
                y = float(row[yCol])
                point_set.append((x,y))
            except:
                pass
            
        bbox = pysal.cg.get_bounding_box(point_set)
        
        shape_object = CShapeFileObject(point_set, name='test',extent=bbox)
        return shape_object
    
    def Show(self):
        success = False
        self.dlg.Fit()
        if self.dlg.ShowModal() == wx.ID_OK:
            self.shp = self.ReadShapeObject()
            success = True
        self.dlg.Destroy()
        
        return success