import math,os
import wx
from wx import xrc
import numpy as np
import pysal

import stars
from stars.visualization.utils import FilterShapeList
from stars.visualization.dialogs import VariableSelDialog
from stars.Plugin import *

class Points2GridPlugin(IMapPlugin):
    def __init__(self):
        IMapPlugin.__init__(self)
        
    def get_icon(self):
        new_bmp =  wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_TOOLBAR, (16,16))
        return new_bmp
    
    def get_icon_size(self):
        return (16,16)
    
    def get_label(self):
        return 'Points to Grid'
   
    def get_shortHelp(self):
        return ''
    
    def get_longHelp(self):
        return ''
    
    def get_toolbar_pos(self):
        return -1
    
    def get_parent_menu(self):
        return 'Tools'
    
    def show(self, event):
        main = event.EventObject.GetParent()
        self.main = main
        p2g_dlg_res = xrc.XmlResource(os.path.join(os.getcwd(), 'plugins/points_to_grid.xrc'))
        p2g_dlg = p2g_dlg_res.LoadDialog(None, 'IDD_PLUGIN_POINTS_TO_GRID')
        self.btn_openshp = xrc.XRCCTRL(p2g_dlg, 'IDC_OPEN_ISHP')
        self.btn_opengrid = xrc.XRCCTRL(p2g_dlg, 'IDC_OPEN_OSHP')
        self.bg_combox = xrc.XRCCTRL(p2g_dlg, 'IDC_BACKGROUND_SHP')
        self.point_shp_ctrl = xrc.XRCCTRL(p2g_dlg,'IDC_FIELD_POINT_SHP')
        self.grid_shp_ctrl = xrc.XRCCTRL(p2g_dlg,'IDC_FIELD_GRID_SHP')
        self.cell_size_ctrl = xrc.XRCCTRL(p2g_dlg,'IDC_CELL_SIZE')
        
        self.bg_combox.AppendItems([shp.name for shp in main.shapefiles])
        
        p2g_dlg.Bind(wx.EVT_BUTTON, self.OnSelectShapeFile, self.btn_openshp)
        p2g_dlg.Bind(wx.EVT_BUTTON, self.OnExportShapeFile, self.btn_opengrid)
        
        if p2g_dlg.ShowModal() == wx.ID_OK:
            point_shp = self.point_shp_ctrl.GetValue()
            grid_shp = self.grid_shp_ctrl.GetValue()
            cell_size = float(self.cell_size_ctrl.GetValue())
            background = None
            
            self.PointsToGrid(point_shp, cell_size, grid_shape_path=grid_shp)
            
            main.ShowMsgBox('Create grid shape file successful.',
                            mtype='CAST information',
                            micon=wx.ICON_INFORMATION)
        
        p2g_dlg.Destroy()
        
    def OnSelectShapeFile(self, event):
        dlg = wx.FileDialog(self.main, message="Choose a file", 
                            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
                            style=wx.OPEN| wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            shp_path = dlg.GetPath()
            self.point_shp_ctrl.SetValue(shp_path)
        dlg.Destroy()
            
    def OnExportShapeFile(self, event):
        dlg = wx.FileDialog(self.main, message="Choose a file", 
                            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
                            defaultDir=os.getcwd(),
                            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            shp_path = dlg.GetPath()
            self.grid_shp_ctrl.SetValue(shp_path)
        dlg.Destroy()
    
    def PointsToGrid(self, pts_shp_path, grid_size, polygon_background=None, grid_shape_path=None, bFineBG=False):
        """
        Convert POINT  to GRID. 
        
        To avoid discontinued grid, a polygon background shape file
        can be used to maitain the EMPTY cellular, with point count
        equals to 0. The output GRID shape file and dbf file will 
        be saved to grid_shape_path location.
        """
        f = pysal.open(pts_shp_path)
        if hasattr(f,'type'):
            if f.type != pysal.cg.Point:
                raise "File type not correct!"
        shape_objects = f.read()
        extent = f.bbox
        f.close()
        
        if polygon_background:            
            _f = pysal.open(polygon_background)
            _polygons = _f.read()
            extent = _f.bbox
            _f.close()
        
        left, top = extent[0],extent[3]
        shape_width = extent[2] - extent[0]
        shape_height = extent[3] - extent[1]
        grid_width = math.floor(shape_width / float(grid_size))
        grid_height = math.floor(shape_height / float(grid_size))
        grid_indice = np.zeros((grid_width, grid_height))
        
        # test POINTs and cellular
        for pt in shape_objects:
            x,y = pt
            grid_x = math.floor((x-left) / grid_size)
            grid_y = math.floor((top-y)/ grid_size)
            if grid_x < grid_width and grid_y < grid_height:
                grid_indice[grid_x][grid_y] += 1
                
        # test polygon Background and EMPTY cellulars
        if polygon_background and bFineBG:            
            for poly in _polygons:
                pts_test_results = {} # for accelerating polygon/point testing
                
                for x in range(int(grid_width)):
                    for y in range(int(grid_height)):
                        if grid_indice[x][y] >= 0:
                            # need to see if this cell intersects with the POLY
                            p0 = pysal.cg.Point( (left + x*grid_size,     top - y*grid_size))
                            p1 = pysal.cg.Point( (left + (x+1)*grid_size, top - y*grid_size))
                            p2 = pysal.cg.Point( (left + (x+1)*grid_size, top - (y+1)*grid_size))
                            p3 = pysal.cg.Point( (left + x*grid_size,     top - (y+1)*grid_size))
                            
                            count = 0
                            for p in [p0,p1,p2,p3]:
                                if pts_test_results.has_key(p):
                                    ret = pts_test_results[p]
                                else:
                                    ret = pysal.cg.get_polygon_point_intersect(poly, p)
                                    pts_test_results[p] = ret
                                if ret != None:
                                    break
                                count += 1
                            if count == 4:
                                grid_indice[x][y] = -1 # just mark
        
        # save GRID shape and dbf file
        if grid_shape_path:
            grid_shp = pysal.open(grid_shape_path,'w')
            grid_dbf = pysal.open(grid_shape_path[:-3]+'dbf','w')
            grid_dbf.header = ['ID','count']
            grid_dbf.field_spec = [('N',9,0),('F',9,0)]
            
            cells_x, cells_y = np.where(grid_indice >= 0)
            count = 1
            for i,x  in enumerate(cells_x):
                y = cells_y[i]
                p0 = pysal.cg.Point( (left + x*grid_size,     top - y*grid_size))
                p1 = pysal.cg.Point( (left + (x+1)*grid_size, top - y*grid_size))
                p2 = pysal.cg.Point( (left + (x+1)*grid_size, top - (y+1)*grid_size))
                p3 = pysal.cg.Point( (left + x*grid_size,     top - (y+1)*grid_size))
                poly = pysal.cg.Polygon([p0,p1,p2,p3])
                grid_shp.write(poly)
                pts_count = grid_indice[x][y]
                pts_count = pts_count if pts_count > 0 else 0
                grid_dbf.write([count, pts_count])
                count += 1
            grid_shp.close()
            grid_dbf.close()