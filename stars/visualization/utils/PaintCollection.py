"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['GetRandomColor','DrawPurePoints','DrawPoints','DrawLines','DrawPolygons']

import random
import wx
import os

def GetRandomColor(opaque=255):
    return wx.Colour(
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255),
        opaque
    )

def DrawPurePoints(dc, points, **kwargs):
    """
    utility function which draw points with different
    color/size schemas to any DC
    """
    edge_color = wx.BLACK
    fill_color = wx.BLUE
    edge_thickness = 1
    size = 6
    opaque = 255
    
    # for different color schema
    data_group = None
    fill_color_group = None
    edge_color_group = None
    # for different size schema
    size_group = None
    
    if kwargs.has_key("edge_color"):
        edge_color = kwargs["edge_color"]
    if kwargs.has_key("fill_color"):
        fill_color = kwargs["fill_color"]
    if kwargs.has_key("edge_thickness"):
        edge_thickness = kwargs["edge_thickness"]
    if kwargs.has_key("size"):
        size = kwargs["size"]
    if kwargs.has_key("opaque"):
        opaque = kwargs["opaque"]
    if kwargs.has_key("data_group"):
        data_group = kwargs["data_group"]
    if kwargs.has_key("fill_color_group"):
        fill_color_group = kwargs["fill_color_group"]
    if kwargs.has_key("edge_color_group"):
        edge_color_group = kwargs["edge_color_group"]
    if kwargs.has_key("size_group"):
        size_group = kwargs["size_group"]

    """
    if edge_color.alpha > 0:
        dc.SetPen(wx.Pen(edge_color))
    else:
        dc.SetPen(wx.TRANSPARENT_PEN)
    """   
    if edge_color.alpha == 0 or (edge_color.red == 255 and edge_color.blue==255 and edge_color.green==255):
        #dc.SetPen(wx.Pen(fill_color,0))
        dc.SetPen(wx.TRANSPARENT_PEN)
    else:
        dc.SetPen(wx.Pen(edge_color))
        
    if data_group == None or len(data_group) <= 0:
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.BLACK_BRUSH)
        #dc.DrawPointList(points,pens=wx.BLACK_PEN)
        for x,y in points:
            dc.DrawRectangle(x,y,1,1)
    else:
        # different color schema scenario
        for i,group in enumerate(data_group):
            if len(group) == 0:
                continue
            isDraw = True
            if edge_color_group:
                dc.SetPen(
                    wx.Pen(
                        wx.Colour(
                            edge_color_group[i][0], 
                            edge_color_group[i][1],
                            edge_color_group[i][2],
                            opaque
                        )
                    )
                )
            if fill_color_group:
                dc.SetBrush(
                    wx.Brush(
                        wx.Colour(
                            fill_color_group[i][0],
                            fill_color_group[i][1],
                            fill_color_group[i][2],
                            opaque
                        )
                    )
                )
            if isDraw:
                pts = [points[j] for j in group]
                dc.DrawPointList(pts)
  
                
def DrawPoints(dc, points, **kwargs):
    """
    utility function which draw points with different
    color/size schemas to any DC
    """
    edge_color = wx.BLACK
    fill_color = wx.BLUE
    edge_thickness = 1
    size = 6
    opaque = 255
    
    # for different color schema
    data_group = None
    fill_color_group = None
    edge_color_group = None
    # for different size schema
    size_group = None
    
    if kwargs.has_key("edge_color"):
        edge_color = kwargs["edge_color"]
    if kwargs.has_key("fill_color"):
        fill_color = kwargs["fill_color"]
    if kwargs.has_key("edge_thickness"):
        edge_thickness = kwargs["edge_thickness"]
    if kwargs.has_key("size"):
        size = kwargs["size"]
    if kwargs.has_key("opaque"):
        opaque = kwargs["opaque"]
    if kwargs.has_key("data_group"):
        data_group = kwargs["data_group"]
    if kwargs.has_key("fill_color_group"):
        fill_color_group = kwargs["fill_color_group"]
    if kwargs.has_key("edge_color_group"):
        edge_color_group = kwargs["edge_color_group"]
    if kwargs.has_key("size_group"):
        size_group = kwargs["size_group"]
       
    if edge_color.alpha > 0:
        dc.SetPen(wx.Pen(wx.Colour(edge_color[0],edge_color[1],edge_color[2],edge_color.alpha),edge_thickness))
    else:
        dc.SetPen(wx.TRANSPARENT_PEN)
    
    if data_group == None or len(data_group) <= 0:
        dc.SetBrush(wx.Brush(wx.Colour(fill_color[0],fill_color[1],fill_color[2], fill_color.alpha)))
        ellipses = []
        offset = size /2.0
        unique_point = set(points)
        for p in unique_point:
            ellipses.append((p[0] - offset,p[1]-offset,size,size))
        dc.DrawEllipseList(ellipses)
        
    else:
        # different color schema scenario
        # rest_pts = set(range(len(points))) 
        for i,group in enumerate(data_group):
            if len(group) == 0:
                continue
            isDraw = True
            if edge_color_group:
                dc.SetPen(
                    wx.Pen(
                        wx.Colour(
                            edge_color_group[i][0], 
                            edge_color_group[i][1],
                            edge_color_group[i][2],
                            opaque
                        )
                    )
                )
            if fill_color_group:
                dc.SetBrush(
                    wx.Brush(
                        wx.Colour(
                            fill_color_group[i][0],
                            fill_color_group[i][1],
                            fill_color_group[i][2],
                            opaque
                        )
                    )
                )
            if isDraw:
                pts = [points[j] for j in group]
                pts = list(set(pts))
                if size_group != None:
                    size = size_group[i]
                ellipses = []
                offset = size / 2.0
                for p in pts:
                    ellipses.append((p[0]-offset,p[1]-offset,size,size))
                dc.DrawEllipseList(ellipses)
            #rest_pts = rest_pts - set(group) 
            
def DrawLines(dc, lines, **kwargs):
    """
    utlity function which draw lines with
    different color schemas to any DC
    """
    edge_color = wx.BLACK
    fill_color = wx.BLUE
    edge_thickness = 1
    opaque = 255
    size = 6
    
    # for different color schema
    data_group = None
    fill_color_group = None
    edge_color_group = None
    # for different size schema
    size_group = None
    
    if kwargs.has_key("edge_color"):
        edge_color = kwargs["edge_color"]
    if kwargs.has_key("fill_color"):
        fill_color = kwargs["fill_color"]
    if kwargs.has_key("edge_thickness"):
        edge_thickness = kwargs["edge_thickness"]
    if kwargs.has_key("size"):
        size = kwargs["size"]
    if kwargs.has_key("opaque"):
        opaque = kwargs["opaque"]
    if kwargs.has_key("data_group"):
        data_group = kwargs["data_group"]
    if kwargs.has_key("fill_color_group"):
        fill_color_group = kwargs["fill_color_group"]
    if kwargs.has_key("edge_color_group"):
        edge_color_group = kwargs["edge_color_group"]
    if kwargs.has_key("size_group"):
        size_group = kwargs["size_group"]
       
    if edge_color.alpha > 0:
        dc.SetPen(
            wx.Pen(
                wx.Colour(edge_color[0],
                          edge_color[1],
                          edge_color[2],
                          opaque),
                edge_thickness))
    else:
        dc.SetPen(wx.TRANSPARENT_PEN)
    
    if data_group == None or len(data_group) <= 0:
        """
        dc.SetBrush(
            wx.Brush(
                wx.Colour(fill_color[0],
                          fill_color[1],
                          fill_color[2], 
                          fill_color.alpha)))
        """
        lns = []
        for part in lines:
            lns += part
        lns = list(set(lns))
        dc.DrawLineList(lns)
    else:
        # different color schema scenario
        for i,group in enumerate(data_group):
            if len(group) == 0:
                continue
            isDraw = True
            if edge_color_group:
                dc.SetPen(
                    wx.Pen(
                        wx.Colour(
                            edge_color_group[i][0], 
                            edge_color_group[i][1],
                            edge_color_group[i][2],
                            opaque
                        ),
                        edge_thickness
                    )
                )
            if fill_color_group:
                dc.SetPen(
                    wx.Pen(
                        wx.Colour(
                            fill_color_group[i][0],
                            fill_color_group[i][1],
                            fill_color_group[i][2],
                            opaque
                        ),
                        edge_thickness
                    )
                )
            if isDraw:
                lns= []
                for j in group:
                    lns += lines[j]
                lns = list(set(lns))
                dc.DrawLineList(lns)

def DrawPolygons(dc, polygons, **kwargs):
    """
    utlity function which draw polygons with
    different color schemas to any DC
    """
    num_polys = len(polygons)
    edge_color = wx.BLACK
    fill_color = wx.BLUE
    brush_style = wx.SOLID
    edge_thickness = 1
    opaque = 255
    # for different color schema
    data_group = None
    fill_color_group = None
    edge_color_group = None
    
    if kwargs.has_key("edge_color"):
        edge_color = kwargs["edge_color"]
    if kwargs.has_key("fill_color"):
        fill_color = kwargs["fill_color"]
    if kwargs.has_key("edge_thickness"):
        edge_thickness = kwargs["edge_thickness"]
    if kwargs.has_key("opaque"):
        opaque= kwargs["opaque"]
    if kwargs.has_key("brush_style"):
        brush_style= kwargs["brush_style"]
    if kwargs.has_key("data_group"):
        data_group = kwargs["data_group"]
    if kwargs.has_key("fill_color_group"):
        fill_color_group = kwargs["fill_color_group"]
    if kwargs.has_key("edge_color_group"):
        edge_color_group = kwargs["edge_color_group"]
    """   
    try:
        gc = wx.GraphicsContext.Create(dc)
        # setup pen for drwaing polygons
        if edge_color.alpha > 0:
            gc.SetPen(wx.Pen(edge_color,edge_thickness))
        else:
            gc.SetPen(wx.TRANSPARENT_PEN)
        # start drawing polygons
        if data_group == None or len(data_group) == 0: 
            # default draw with unified color 
            #gc.SetBrush(wx.Brush(fill_color,brush_style))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            path = gc.CreatePath()
            for poly in polygons:
                path.MoveToPoint(poly[0])
                cnt = len(poly)
                for i in range(1,cnt):
                    p = poly[i]
                    path.AddLineToPoint(p)
                path.CloseSubpath()
            gc.FillPath(path)
            gc.StrokePath(path)
        else:
            # when different color schema is assigned: data_group <-> fill_color_group
            for i,group in enumerate(data_group):
                clr = fill_color_group[i]
                gc.SetBrush(wx.Brush(fill_color_group[i]))
                plgs = [polygons[j] for j in group]
                gc.DrawPolygonList(plgs)
        gc.Destroy()
    except:
    """
    dc.SetPen(wx.Pen(edge_color,edge_thickness))
    # start drawing polygons
    if data_group == None or len(data_group) == 0: 
        if edge_color.alpha == 0:
            dc.SetPen(wx.TRANSPARENT_PEN)
        elif edge_color == wx.WHITE:
            dc.SetPen(wx.Pen(fill_color,1))
            #dc.SetPen(wx.TRANSPARENT_PEN)
        # default draw with unified color 
        dc.SetBrush(wx.Brush(fill_color,brush_style))

        _polygons= []
        for parts in polygons:
            for poly in parts:
                _polygons.append(poly)
        _polygons = list(set(_polygons))
        dc.DrawPolygonList(_polygons)
    else:
        # when different color schema is assigned: 
        # data_group <-> fill_color_group
        for i,group in enumerate(data_group):
            fill_color = fill_color_group[i]
            dc.SetBrush(wx.Brush(fill_color))
            
            if edge_color.alpha == 0:
                # this is for "space-time query" algorithm
                dc.SetPen(wx.Pen(fill_color,1))
            elif edge_color == wx.WHITE:
                dc.SetPen(wx.Pen(fill_color,1))
                
            _polygons = []
            for j in group:
                for poly in polygons[j]:
                    _polygons.append(poly)
            _polygons = list(set(_polygons))
            dc.DrawPolygonList(_polygons)
                    
