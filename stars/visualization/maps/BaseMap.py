"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["BaseLayer","PointLayer","LineLayer","PolygonLayer"]

import math,copy
import numpy as np
from datetime import datetime

import wx
import pysal
import stars
from stars.visualization.utils import *
from stars.visualization.AbstractCanvas import *

    
#-----------detail drawing classes----------------
# PointLayer,LineLayer,PolygonLayer
# They draw their own data using any dc.
#
#-------------------------------------------------

class BaseLayer():
    """
    Base class for all Drawing classes
    """
    def __init__(self, **kwargs):
        self.n = 0 # number of objects
        self.kwargs = kwargs
        
        if kwargs.has_key("fill_color"):
            self.default_fill_color = kwargs["fill_color"]
        else:
            # default fill color
            self.kwargs["fill_color"] =  wx.BLUE
        
    def set_fill_color(self,color):
        self.kwargs["fill_color"] = color
        
    def get_fill_color(self):
        return self.kwargs["fill_color"]
    
    def set_brush_style(self, brush_style):
        self.kwargs["brush_style"] = brush_style
        
    def set_fill_color_group(self, color_group):
        self.kwargs["fill_color_group"] = color_group
        self.default_fill_color_group = copy.copy(color_group)
    
    def set_edge_color(self, color):
        self.kwargs["edge_color"] = color
        
    def get_edge_color(self):
        return self.kwargs["edge_color"]
        
    def set_edge_thickness(self,thickness):
        self.kwargs["edge_thickness"] = thickness
    
    def set_edge_color_group(self, color_group):
        self.kwargs["edge_color_group"] = color_group
        
    def set_data_group(self, data_group):
        self.kwargs["data_group"] = data_group
        self.default_data_group = copy.copy(data_group)
    
    def set_size_group(self, size_group):
        self.kwargs["size_group"] = size_group
    
    def set_opaque(self, opaque):
        self.kwargs["opaque"] = opaque
        
    def init_spatial_index(self):
        """
        spatial index: for fast selecting polygons/points
        """
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Init spatial index ...                ",
            maximum = 2,
            parent=self.parent,
            style = wx.PD_AUTO_HIDE)
        progress_dlg.CenterOnScreen()
        progress_dlg.Update(1)

        self.locator = self.shapefile_object.get_locator()
        progress_dlg.Update(2)
        progress_dlg.Destroy()
        
    def brutalforce_search_points(self,query_region, points):
        selected_obj_ids = []
        for i,pt in enumerate(points):
            if pysal.cg.get_rectangle_point_intersect(query_region, pt):
                selected_obj_ids.append(i)
        return selected_obj_ids
    
    def query_objects_in_rectangle_region(self, query_region, points):
        selected_obj_ids = []
        if self.locator == None:
            selected_obj_ids = self.brutalforce_search_points(
                query_region, points)
        else:
            if stars.SHAPE_LOCATOR_INDEX == None:
                selected_obj_ids = self.brutalforce_search_points(query_region, points)
                
            # using spatial index to query
            elif stars.SHAPE_LOCATOR_INDEX == stars.SHAPE_LOCATOR_KDTREE:
                kdtree = self.shapefile_object.get_kdtree_locator()
                
                query_center = (query_region.left + query_region.width/2.0,
                                query_region.lower + query_region.height/2.0)
                search_radius = ((query_region.width/2)**2 + (query_region.height/2)**2)**0.5
                thres = min(query_region.width/2, query_region.height/2)
                
                dist_list, id_list = kdtree.query(
                    query_center, 
                    distance_upper_bound=search_radius,
                    k=len(points))
                
                for i,id in enumerate(id_list):
                    if dist_list[i] != np.inf:
                        if dist_list[i] <= thres:
                            selected_obj_ids.append(id)
                            continue
                        if pysal.cg.get_rectangle_point_intersect(
                            query_region, points[id]):
                            selected_obj_ids.append(id)
                    else:
                        break
                    
            elif stars.SHAPE_LOCATOR_INDEX == stars.SHAPE_LOCATOR_QUADTREE:
                if query_region[0] == query_region[2] \
                   and query_region[1] == query_region[3]:
                    # single click, do a kd-tree query
                    p = (query_region[0],query_region[1])
                    
                    kdtree = self.shapefile_object.get_kdtree_locator()
                    
                    if self.shapefile_object.shape_type == stars.SHP_POINT:
                        nn = kdtree.query(p,k=1)
                        if nn[0] < 0.0001:
                            selected_obj_ids = nn[1]
                    elif self.shapefile_object.shape_type == stars.SHP_POLYGON:
                        nn = kdtree.query(p,k=4)
                        for id in nn[1]:
                            poly_id = self.shapefile_object.get_kdtree_polyid(id)
                            poly = self.shapefile_object.shape_objects[poly_id]
                            poly = pysal.cg.Polygon(poly)
                            ret = pysal.cg.get_polygon_point_intersect(poly, p)
                            if ret != None:
                                selected_obj_ids = [poly_id]
                                break
                else:
                    # do a quad-tree query
                    selected_obj_ids = self.locator.find_shapes(
                        query_region[:2],query_region[2:])
            
        return selected_obj_ids
    
    
class PointLayer(BaseLayer):
    """
    Drawing class, which draw POINT data to DC
    """
    def __init__(self, parent, shp, build_spatial_index=True, **kwargs):
        BaseLayer.__init__(self,**kwargs)
        
        self.parent = parent
        self.points = shp
        self.shapefile_object = shp
        self.extent = shp.extent
        self.locator = shp.locator
        self.screen_objects = []
        self.selected_obj_ids = []
        self.dist_threshold = 0.0001
        self.n = len(self.points)
        
        self.shape_bbox = pysal.cg.Rectangle(
            self.extent[0],
            self.extent[1],
            self.extent[2],
            self.extent[3]
        )
        
        # set default color
        self.set_edge_color(stars.MAP_COLOR_POINT_EDGE)
        self.set_fill_color(stars.MAP_COLOR_POINT_FILL)
        
        # incremental drawing
        self.maxNumDrawPoint = 10000
        self.isAppendingDraw = False
        if self.n > self.maxNumDrawPoint:
            self.isAppendingDraw = True
          
        self.default_fill_color_group = None 
        self.default_data_group = None
            
        if 'data_group' in self.kwargs:
            self.default_data_group = copy.copy(self.kwargs['data_group'])
        if 'fill_color_group' in self.kwargs:
            self.default_fill_color_group = copy.copy(self.kwargs['fill_color_group'])
        
    def draw(self,dc,view):
        if self.shapefile_object.engine == "c":
            self.screen_objects = self.shapefile_object.convert_screen_objects(view)
            DrawPoints(dc, self.screen_objects, **self.kwargs)
        else:
            # some cases not display shp file, e.g. csv, and database
            points = self.shapefile_object.shape_objects
            self.screen_objects= []
            for pt in points:
                self.screen_objects.append(view.view_to_pixel(pt[0],pt[1]))
            DrawPoints(dc, self.screen_objects, **self.kwargs)
       
        
    def draw_selected(self,dc,view,width=0):
        if len(self.selected_obj_ids) == 0:
            return
        
        screen_pts = []
        for i in self.selected_obj_ids:
            screen_point = self.screen_objects[i]
            screen_pts.append(screen_point)
            
        # drawing on client DC
        DrawPoints(dc, screen_pts, fill_color=wx.RED, brush_style=wx.CROSSDIAG_HATCH)
        
    def get_selected_by_region(self,view, map_query_region):
        """
        """
        self.selected_obj_ids= []
        x0,y0,x1,y1 = map_query_region
        
        query_region = pysal.cg.Rectangle(min(x0,x1),min(y0,y1),max(x1,x0),max(y0,y1))
        if not pysal.cg.bbcommon(query_region, self.shape_bbox):
            # if boundary of layer is not overlay, ignore
            # or single click
            pass
        else:
            self.selected_obj_ids = self.query_objects_in_rectangle_region(query_region, self.points)
                    
        return self.selected_obj_ids, map_query_region 
    


class PolygonLayer(BaseLayer):
    """
    Drawing class, which draw POLYGON data to DC
    """
    def __init__(self, parent,shp,build_spatial_index=True, **kwargs):
        BaseLayer.__init__(self,**kwargs)
        
        # set default color
        self.set_edge_color(stars.MAP_COLOR_POLYGON_EDGE)
        self.set_fill_color(stars.MAP_COLOR_POLYGON_FILL)
        
        self.parent           = parent
        self.shapefile_object = shp
        self.n                = len(shp)
        self.extent           = shp.extent
        self.polygons         = shp.shape_objects
        self.centroids        = shp.centroids
        self.locator          = shp.locator
        
        self.shape_bbox = pysal.cg.Rectangle(
            self.extent[0],
            self.extent[1],
            self.extent[2],
            self.extent[3]
        )
        self.selected_obj_ids = []
        self.screen_objects = {}
       
    def draw(self,dc,view,draw3D=False,drawRaw=False):
        if self.shapefile_object.engine == "c":
            del self.screen_objects
            self.screen_objects = self.shapefile_object.convert_screen_objects(view)
            if draw3D:
                new_screen_objects = []
                for parts in self.screen_objects:
                    new_parts = []
                    for poly in parts:
                        new_poly = []
                        for pt in poly:
                            x,y = pt
                            y = y / draw3D
                            x = x - y*math.tan(math.pi/3) + 160
                            new_poly.append((x,y))
                        new_parts.append(new_poly)
                    new_screen_objects.append(new_parts)
                self.screen_objects = new_screen_objects            
            DrawPolygons(dc, self.screen_objects, **self.kwargs)
        else:
            self.screen_objects = []
            for poly in self.polygons:
                _poly = []
                for pt in poly:
                    x,y = view.view_to_pixel(pt[0],pt[1])
                    _poly.append((x,y))
                self.screen_objects.append([_poly])
            DrawPolygons(dc, self.screen_objects, **self.kwargs)
            
        
    def draw_selected(self,dc,view,width=0):
        if len(self.selected_obj_ids) == 0:
            return
       
        selected_polygons= []
        
        for i in self.selected_obj_ids:
            selected_polygons.append(self.screen_objects[i])
                
        DrawPolygons(dc, selected_polygons, 
                     edge_color=wx.Color(255,255,0),#wx.Color(0,0,0,0),
                     fill_color=stars.MAP_BRUSHING_COLOR, 
                     brush_style=wx.CROSSDIAG_HATCH)
        
    def draw_selected_neighbors(self,neighbor_ids, dc,view,width=0):
        if len(neighbor_ids) == 0:
            return
        
        selected_polygons = []
        for i in neighbor_ids:
            selected_polygons.append(self.screen_objects[i])
                
        DrawPolygons(dc, selected_polygons, edge_color=wx.RED,fill_color=wx.RED, brush_style=wx.CROSSDIAG_HATCH)
        
    def get_selected_by_region(self,view, map_query_region):
        self.selected_obj_ids = []
        x0,y0,x1,y1 = map_query_region
        query_region = pysal.cg.Rectangle(
            min(x0,x1),min(y0,y1),max(x1,x0),max(y0,y1))
        
        if not pysal.cg.bbcommon(query_region, self.shape_bbox):
            # if boundary of layer is not overlay, ignore
            # or single click
            pass
        else:
            self.selected_obj_ids = \
                self.query_objects_in_rectangle_region(
                    query_region, self.centroids)
               
        return self.selected_obj_ids, map_query_region
                

class LineLayer():
    """
    """
    def __init__(self, parent, shp, build_spatil_index=False, **kwargs):
        BaseLayer.__init__(self,**kwargs)
        
        # set default color
        self.set_edge_color(stars.MAP_COLOR_POLYGON_EDGE)
        self.set_fill_color(stars.MAP_COLOR_POLYGON_FILL)
        
        self.parent           = parent
        self.shapefile_object = shp
        self.n                = len(shp)
        self.extent           = shp.extent
        self.polygons         = shp.shape_objects
        self.centroids        = shp.centroids
        self.locator          = shp.locator
        
        self.shape_bbox = pysal.cg.Rectangle(
            self.extent[0],
            self.extent[1],
            self.extent[2],
            self.extent[3]
        )
        self.selected_obj_ids = []
        self.screen_objects = {}
       
    
    def draw(self,dc):
        pass