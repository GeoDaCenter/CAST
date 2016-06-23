"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["ColorSchema","GradientColor","ShapeMap"]

import os,random,sys
import wx
from wx import xrc
import pysal
import numpy as np

import stars
from BaseMap import LineLayer,PointLayer,PolygonLayer

from stars.visualization.EventHandler import AbstractData
from stars.visualization.AbstractCanvas import AbstractCanvas 
from stars.visualization.utils import GetRandomColor, GradientColor, View2ScreenTransform

class ColorSchema():
    """
    Color schema for regular maps
    """
    def __init__(self, colors=None,labels=None,edge_color=wx.Colour(0,0,0)):
        # pulic available 
        self.labels = labels
        self.bmps = []
        self.bmp_dict = {}
        
        # private
        self.edge_color = edge_color
        self.colors = colors
        self.size = (16,16)
        self.opaque = edge_color.alpha 
        
        self.createNodeBmps()

    def createNodeBmps(self):
        for i, label in enumerate(self.labels):
            color = self.colors[i]
            if color == None:
                # a text only tree node
                self.bmp_dict[label] = None
                continue
            
            # Creat a bitmap which can be used as TreeNode image
            node_bmp = wx.EmptyBitmap(self.size[0],self.size[1])
            dc = wx.MemoryDC()
            dc.SelectObject(node_bmp)
            dc.Clear()
            
            # draw rectangular with input color
            pen = wx.Pen(self.edge_color)
            brush = wx.Brush(color,wx.SOLID)
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawRectangle(0,0,self.size[0],self.size[1])
            #dc.Destroy()
            self.bmps.append(node_bmp)
            self.bmp_dict[label] = node_bmp
            
    def GetBmp(self, label):
        return self.bmp_dict[label]
    
    def GetColorIndex(self, label):
        return self.labels.index(label)
    
    def UpdateColorSchema(self):
        self.bmps = []
        self.createNodeBmps()
        return self
    
    def SetOpaque(self, opaque):
        self.opaque = int(opaque)
        
        self.edge_color.Set(self.edge_color.red,
                            self.edge_color.green,
                            self.edge_color.blue,
                            self.opaque)
        
        for color in self.colors:
            if color != None:
                color.Set(color.red,color.green,color.blue,self.opaque)
            
class GradientColorSchema(ColorSchema):
    def __init__(self, gradient_type):
        self.gradient_color = GradientColor(gradient_type)

        ColorSchema.__init__(self,None,[""])

    def createNodeBmps(self):
        node_bmp = wx.EmptyBitmap(self.size[0],self.size[1])
        dc = wx.MemoryDC()
        dc.SelectObject(node_bmp)
        dc.Clear()
       
        dc.DrawBitmap(self.gradient_color.get_bmp(self.size[0],self.size[1]),0,0)
        #dc.Destroy()
        self.bmps.append(node_bmp)
        label = 'Density Map'
        self.bmp_dict[label] = node_bmp
    
        
class ShapeMap(AbstractCanvas):
    """
    wxWindow ShapeFile drawing class for all types of SHP objects (Point, Polygon, Line)
    """
    def __init__(self,parent, layers, **kwargs):
        AbstractCanvas.__init__(self,parent,**kwargs)
        
        try:
            if layers == None or len(layers) == 0:
                raise "The parameter 'layers' is not valid."
            
            self.parent = parent
            self.layers = layers
            self.layer_dict = {}            # {layer_name: layer}
            self.draw_layers = {}           # {layer: BaseLayer}
            self.hide_layers = {}           # {layer: true}
            self.color_schema_dict = {}     # {layer: color_schema}
            
            self.fixed_layer = None         # fixed layer that can't be removed
            self.selected_shape_ids = {}    # for brushing-linking 
            self.default_label = ""         # default label for layer (tree control)
            self.opaque = 255               # default opaque for all layers
           
            self.oids   = None              # for selecting by Weights
            self.oid_dict = None 
            self.neighbor_dict = None
            self.is_selecting_by_weights = False
            
            title = "Map - %s" % self.layers[0].name
            self.SetTitle(title)
            
            # drawing all layers
            n = len(self.layers)
            for i,layer in enumerate(self.layers):
                self.layer_dict[layer.name] = layer
                if layer.shape_type == stars.SHP_POINT:
                    self.draw_layers[layer] = PointLayer(self,layer)
                elif layer.shape_type == stars.SHP_LINE:
                    self.draw_layers[layer] = LineLayer(self,layer)
                elif layer.shape_type == stars.SHP_POLYGON:
                    self.draw_layers[layer] = PolygonLayer(self,layer)        
                    
                # set color schema
                clr = self.draw_layers[layer].get_fill_color()
                edge_clr = self.draw_layers[layer].get_edge_color()
                color_schema = ColorSchema(colors=[clr],labels=[self.default_label],edge_color=edge_clr)
                self.color_schema_dict[layer.name] = color_schema 
                # set hidden status
                self.hide_layers[layer] = False
                  
            # for drawing sequences
            self.layer_name_list = [layer.name for layer in self.layers]
            
            # extent: set for first layer
            xl,yl,xr,yr = self.layers[0].extent 
            self.extent = [xl,yl,xr,yr]   
            self.map_query_region = self.extent
            
        except Exception as err:
            self.ShowMsgBox('ShapeMap could not be created. ' + str(err.message))
            self.parentFrame.Close(True)
            return None
        
        # register event_handler to THE OBSERVER
        self.Register(stars.EVT_OBJS_SELECT, self.OnShapesSelect)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoShapeSelect)
        
    def UnRegister(self):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnShapesSelect)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoShapeSelect)
        
    def OnClose(self, event):
        self.UnRegister()
        event.Skip()

    def RemoveRegister(self):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnShapesSelect)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoShapeSelect)
        
    def OnShapesSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        event is an instance of EventHandler.Event class
        event.object are the data for selecting shape objects
        """
        if event == None: 
            self.selected_shape_ids = {}
            return
        
        data = event.data
        
        current_layer_name_set = set(self.layer_dict.keys())
        selected_layer_name_set = set(data.shape_ids.keys())
        highlight_layer_names = list(current_layer_name_set.intersection(selected_layer_name_set))
        
        tmp_buffer = wx.EmptyBitmap(self.bufferWidth, self.bufferHeight)
        tmp_dc = wx.BufferedDC(None, tmp_buffer)
        background_buffer = self.drawing_backup_buffer if self.drawing_backup_buffer else self.buffer
        tmp_dc.DrawBitmap(background_buffer,0,0) # draw map as background first
        
        if len(highlight_layer_names) > 0:
            # highlighted shape objects by their ids
            self.draw_selected_by_ids(data.shape_ids, tmp_dc)
            
        elif len(data.boundary) >0:
            # select shape objects by boundary transmitted from other map widget
            if isinstance(data.boundary[0], int) or isinstance(data.boundary[0], float):
                self.draw_selected_by_region(tmp_dc, tuple(data.boundary), isEvtResponse=True)
            else:
                self.draw_selected_by_regions(tmp_dc, tuple(data.boundary), isEvtResponse=True)
             
        #tmp_dc.Destroy()
        self.buffer = tmp_buffer
        self.Refresh(False)
   
    def OnNoShapeSelect(self, event):
        """
        Event handler for EVT_OBJ_SELECT.
        Observer will call this function when any other widgets/panels
        dispatch EVT_OBJ_SELECT event
        
        Normally, event could be None, you just need to clean and refresh
        you selected/highlighted
        """
        self.selected_shape_ids = {}
        if self.drawing_backup_buffer:
            self.buffer = self.drawing_backup_buffer
        self.Refresh(False)
        
    def OnSize(self,event):
        """
        For simplification, a fixed size bitmap buffer will be
        specified for drawing codes (instead of determing the
        window size first, and then create bitmap buffer)
        """
        super(ShapeMap, self).OnSize(event)
        bufferWidth,bufferHeight = self.GetClientSize()
        if bufferWidth> 0 and bufferHeight > 0:
            self.bufferWidth = bufferWidth
            self.bufferHeight = bufferHeight
            if self.view:
                self.view.setup(self.bufferHeight,self.bufferWidth)
            self.reInitBuffer = True
            
    def OnRightDown(self, event):
        pass
    
    def OnRightUp(self, event):
        """
        pop-up menu for drawing map options
        """
        menu = wx.Menu()
        menu.Append(210, "Select Neighbors", "")
        menu.Append(211, "Cancel Select Neighbors", "")
        menu.Bind(wx.EVT_MENU, self.select_by_weights, id=210)
        menu.Bind(wx.EVT_MENU, self.cancel_select_by_weights, id=211)
        
        menu.UpdateUI()
        self.PopupMenu(menu)
        event.Skip()
    
    def DoDraw(self,dc,isAppendDraw=False):
        """
        Drawing code: drawing all map layers on bitmap buffer
        """
        if len(self.layers) == 0: 
            dc.Clear()
            return
        
        if os.name == 'nt':
            # in windows, it's weird to draw things with transparency
            # the workaround solution is draw a white background first
            # tried dc.SetBackground() and dc.SetBackgroundMode(wx.SOLID)
            # but doesn't work.
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.WHITE_BRUSH)
            dc.DrawRectangle(0,0,self.bufferWidth,self.bufferHeight)
        
        tmpBuffer = None
        
        # find the common extend by union all shapefile maps
        if self.view == None:
            self.view = View2ScreenTransform(self.extent, self.bufferWidth, self.bufferHeight)
            self.view.zoom_extent = self.extent
           
        # draw layer in buffer
        for layer_name in self.layer_name_list[::-1]:
            layer = self.layer_dict[layer_name]
            if self.hide_layers[layer] == False:
                self.draw_layers[layer].draw(dc,self.view)
            
    def cancel_select_by_weights(self, event):
        """
        cancel select_by_weights function
        """
        self.is_selecting_by_weights = False
        
    def select_by_weights(self,event):
        """
        Drawing neighbors for selected shape objects
        """
        try:
            bReuseWeights = False
            if self.oids != None:
                dlg = wx.MessageDialog(
                    self, 
                    "Do you want to use existed weights file?",
                    "Weights",
                    wx.YES_NO
                    )
                if dlg.ShowModal() == wx.ID_YES:
                    bReuseWeights = True
                    self.is_selecting_by_weights = True
                else:
                    self.is_selecting_by_weights = False
                dlg.Destroy()
                
            if bReuseWeights:
                return
            
            # choose layer
            # choose weights file
            shp = None
            if len(self.layers) == 1:
                shp = self.layers[0]
            else: 
                layer_list = [layer.name for layer in self.layers]
                layer_dlg = wx.SingleChoiceDialog(self, 'Select a layer:', 'layer view', layer_list)
                if layer_dlg.ShowModal() == wx.ID_OK:
                    idx = layer_dlg.GetSelection()
                    shp = self.layers[idx]
                    
            if shp == None or shp.shape_type != stars.SHP_POLYGON:
                self.ShowMsgBox('Please select a POLYGON shapefile.')
                return
            
            if shp.dbf == None:
                self.ShowMsgBox('No dbf file is available.')
                return
            
            from stars.visualization.dialogs import SelectWeightDlg
            weight_dlg = SelectWeightDlg(self.main, self.main.dialog_res)
            
            if weight_dlg.ShowModal() == wx.ID_OK:
                weight_path = weight_dlg.GetWeightPath()
                if weight_path != None or len(weight_path) > 0:
                    w = pysal.open(weight_path).read()
                    if w.n != shp.n:
                        raise Exception("Dismatch weights for current shape file.")
                    
                    self.oids = w.id_order
                    self.oid_dict = {} 
                    for i, oid in enumerate(w.id_order):
                        self.oid_dict[oid] = i
                        
                    self.neighbor_dict = w.neighbors 
                    # setting mouse operation type
                    self.is_selecting_by_weights = True
                    
            weight_dlg.Destroy()
            
        except Exception as err:
            self.ShowMsgBox("This weights file does not match the shapefile. Please select or create a matching one.")
    
    def draw_neighbors_by_weights(self, layer, selected_shape_ids, dc):
        """"
        Draw neighbors of given selected shape objects based on current weights file.
        self.oid, self.neighbor_dict are read from Weights file
        """
        try:
            if self.is_selecting_by_weights == True:
                neighbor_ids = []
                for shape_id in selected_shape_ids:
                    oid = self.oids[shape_id]
                    neighbors = self.neighbor_dict[oid]
                    for i in neighbors:
                        neighbor_ids.append(self.oid_dict[i])
                        
                # remove original shape ids
                for shape_id in selected_shape_ids:
                    n = neighbor_ids.count(shape_id)
                    while n > 0:
                        neighbor_ids.remove(shape_id)
                        n = n-1
                
                if len(neighbor_ids) > 0:
                    self.draw_layers[layer].draw_selected_neighbors(neighbor_ids, dc,self.view,width=self.bufferWidth)
                    self.selected_shape_ids[layer.name] += neighbor_ids
        except:
            self.ShowMsgBox("Selecting neighbors with weights failed.")
            self.oids = None
            self.is_selecting_by_weights = False
        
    def draw_selected_by_ids(self, shape_ids_dict, dc=None):
        # prepare DC for brushing drawing 
        isDrawed = False
        isDrawOnClient = False
        if dc == None:
            # draw on client DC directly
            dc = wx.ClientDC(self)
            dc.DrawBitmap(self.buffer,0,0)
            isDrawOnClient = True
        for layer in self.layers:
            if shape_ids_dict.has_key(layer.name) and self.hide_layers[layer] == False:
                shape_ids = shape_ids_dict[layer.name]
                self.draw_layers[layer].selected_obj_ids= shape_ids
                self.draw_layers[layer].draw_selected(dc, self.view,width=self.bufferWidth)
                isDrawed = True
        if isDrawOnClient:
            dc.Destroy()
        return isDrawed
            
    def draw_selected_by_regions(self, 
                                 dc, 
                                 select_regions, 
                                 isEvtResponse=False,
                                 isScreenCoordinates=False):
        """ Supprt function for AppendSelection drawing"""
        if not "Linux" in stars.APP_PLATFORM:
            # can't use GCDC in Linux
            dc = wx.GCDC(dc)
        self.selected_shape_ids = {}
        select_regions_of_view = [i for i in select_regions]
       
        # convert screen region to map region
        map_query_regions = [i for i in select_regions]
        if isScreenCoordinates:
            for i,query_region in enumerate(select_regions):
                x0,y0 = self.view.pixel_to_view(query_region[0],query_region[1])
                x1,y1 = self.view.pixel_to_view(query_region[2],query_region[3])
                map_query_regions[i] = (x0,y0,x1,y1)
            
        # draw objects in regions at different layer
        for layer in self.layers:
            if self.hide_layers[layer]:
                # if layer is hidden, ignore
                continue
            rtn_shape_ids = []
            for region in map_query_regions:
                sel_shape_ids, sel_region = \
                             self.draw_layers[layer].get_selected_by_region(self.view,region)
                rtn_shape_ids += sel_shape_ids 
            # remove duplicated selecting objects in sel_shape_ids
            objs = {};rtns = [] 
            for i in rtn_shape_ids:
                if not objs.has_key(i): 
                    objs[i] = 0
                objs[i] += 1
            for i,count in objs.iteritems():
                if count % 2 == 1:
                    rtns.append(i)
            rtn_shape_ids = rtns
            # draw shapes 
            if len(rtn_shape_ids) > 0:
                self.draw_layers[layer].selected_obj_ids = rtn_shape_ids 
                self.draw_layers[layer].draw_selected(dc,self.view,width=self.bufferWidth)
                self.selected_shape_ids[layer.name] = rtn_shape_ids
                
                if self.is_selecting_by_weights == True:
                    # for selecting wegiths neighbors:
                    # need to get their neighbors for the objects in query region
                    self.draw_neighbors_by_weights(layer, rtn_shape_ids, dc)
          
        if isEvtResponse == False:
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.boundary = map_query_regions
            data.shape_ids = self.selected_shape_ids
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        
    def draw_selected_by_region(self, 
                                dc,
                                query_region, 
                                isEvtResponse=False, 
                                isScreenCoordinates=False):
        """ Support function for select drawing """
        if not "Linux" in stars.APP_PLATFORM:
            # can't use GCDC in Linux
            dc = wx.GCDC(dc)
        self.selected_shape_ids = {}
        no_object_selected = True
        
        # convert screen region to map region
        map_query_region = query_region
        if isScreenCoordinates:
            x0,y0 = self.view.pixel_to_view(query_region[0],query_region[1])
            x1,y1 = self.view.pixel_to_view(query_region[2],query_region[3])
            map_query_region = (x0,y0,x1,y1)
            
        self.map_query_region = map_query_region
        # draw objects in region of each layer
        new_map_query_region = map_query_region
        for layer in self.layers:
            if self.hide_layers[layer]:
                # if layer is hidden, ignore
                continue
            # first get objects in query region
            rtn_shape_ids, _map_query_region = self.draw_layers[layer].get_selected_by_region(self.view,map_query_region)
            # then draw these objects
            if len(rtn_shape_ids) > 0:
                self.draw_layers[layer].draw_selected(dc,self.view,width=self.bufferWidth)
                self.selected_shape_ids[layer.name] = rtn_shape_ids
                no_object_selected= False
               
                if self.is_selecting_by_weights == True:
                    # for selecting wegiths neighbors:
                    # need to get their neighbors for the objects in query region
                    self.draw_neighbors_by_weights(layer, rtn_shape_ids, dc)
    
        if isEvtResponse == True:
            # if this drawing action trigged by others
            # there's no need to notify others to 
            # redrawing anymore.
            # Otherwise, execute following (below return)
            # code to notify others
            return []
        if no_object_selected == False:
            # draw selected
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            data.boundary = new_map_query_region
            data.shape_ids = self.selected_shape_ids
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # unselect all
            # tell this action to THE OBSERVER
            data = AbstractData(self)
            self.UpdateEvt(stars.EVT_OBJS_UNSELECT,data)
        return self.selected_shape_ids
        
    def hide_layer(self, layer, isHide=True):
        self.hide_layers[layer] = isHide
        self.isResizing = True
        self.reInitBuffer = True
        
    def add_layer(self, layer, color_schema=None):
        # support Toolbar ADD_LAYER button
        self.layers.append(layer)
        self.layer_dict[layer.name] = layer
        self.layer_name_list.append(layer.name)

        clr = None
        edge_color = None
        if layer.shape_type == stars.SHP_POINT:
            self.draw_layers[layer] = PointLayer(self,layer)
        elif layer.shape_type == stars.SHP_LINE:
            self.draw_layers[layer] = LineLayer(self,layer)
        elif layer.shape_type == stars.SHP_POLYGON:
            self.draw_layers[layer] = PolygonLayer(self,layer)  
            clr = wx.WHITE
            edge_color =wx.Colour(150,150,150,self.opaque)
            self.draw_layers[layer].set_edge_color(edge_color)
               
        if not clr:
            clr = GetRandomColor()
        
        if edge_color:
            color_schema = ColorSchema([clr],[""], edge_color)
        else:
            color_schema = ColorSchema([clr],[""])
            
        self.color_schema_dict[layer.name] = color_schema
        self.draw_layers[layer].set_fill_color(clr)
        
        self.isResizing = True
        self.reInitBuffer= True
        
    def remove_layer(self,layer, isRemoveContent=True):
        # support Toolbar REMOVE_LAYER button
        #if self.fixed_layer:
            
        self.draw_layers.pop(layer)
        self.layer_dict.pop(layer.name)
        self.layer_name_list.remove(layer.name)
        self.color_schema_dict.pop(layer.name)
        
        if isRemoveContent:
            self.layers.remove(layer)
        self.isResizing = True
        self.reInitBuffer = True
        
        self.resetTitle()

    def resetTitle(self):
        # reset title
        if len(self.layers) > 0:
            title = "Map - %s" % self.layers[0].name
            self.parentFrame.SetTitle(title)
        else:
            self.parentFrame.SetTitle("Map")
        
    def extentToLayer(self, layer):
        # support TreeList ctrl 
        self.extent = layer.extent
        self.view = View2ScreenTransform(self.extent, self.bufferWidth, self.bufferHeight)
        self.view.zoom_extent = self.extent
        self.reInitBuffer = True
        self.resetTitle()
        
    def update_color_schema(self, layer,  img_node_label, color=None, edge_color=None):
        try:
            # support TreeList ctrl to change color
            color_schema = self.color_schema_dict[layer.name]
            color_idx = color_schema.GetColorIndex(img_node_label)
            
            if edge_color:
                color_schema.edge_color = edge_color
                self.draw_layers[layer].set_edge_color(edge_color)
                
            if color:
                color_schema.colors[color_idx] = color
                color_list = color_schema.colors
                if len(color_list) == 1:
                    self.draw_layers[layer].set_fill_color(color_list[0])
                else:
                    self.draw_layers[layer].set_fill_color_group(color_list)
               
            self.isResizing = True
            self.reInitBuffer=True
            return color_schema.UpdateColorSchema()
        except:
            self.ShowMsgBox("Changing color here is not allowed.")
        
    def arrange_layers_by_names(self, layer_name_list):
        # support TreeList ctrl to drag-and-drop layers for displaying
        self.layer_name_list = layer_name_list
        self.reInitBuffer = True
        self.resetTitle()
        
    def resetMap(self, layer, map_type=None):
        # support TreeList ctrl
        clr = wx.WHITE
        color_schema = ColorSchema([clr],[""])
        self.color_schema_dict[layer.name] = color_schema
        self.draw_layers[layer].set_fill_color(clr)
        self.draw_layers[layer].set_data_group([])
        self.reInitBuffer = True
        return True

    def _select_k(self):
        cate_dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_QUANTILE')
        cate_txt = xrc.XRCCTRL(cate_dlg, 'IDC_EDIT_QUANTILE')
        cate_txt.SetValue(5)
        if cate_dlg.ShowModal() != wx.ID_OK:
            cate_dlg.Destroy()
            return False
        k = int(cate_txt.GetValue())
        cate_dlg.Destroy()
        return k
    
    def _choose_box_hinge_value(self):
        dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_BOX_HINGE')
        txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_HINGE')
        txt.SetValue(str(1.5))
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return False
        hinge = float(txt.GetValue())
        dlg.Destroy()
        return hinge
        
    def _choose_sample_percent(self):
        dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_JENKS_SAMPLE')
        txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_PERCENT')
        txt.SetValue(str(0.1))
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return False
        percent = float(txt.GetValue())
        dlg.Destroy()
        return percent
    
    def _choose_user_defined_bins(self):
        dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_USER_DEFINED')
        txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_Bins')
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return False
      
        bins = None
        try:
            bins = eval(txt.GetValue())
        except:
            self.ShowMsgBox("Bins should be a list. e.g. [0,10,20]")
        dlg.Destroy()
        return bins
    
    def createClassifyMap(self, layer, map_type):
        # support TreeList ctrl
        from stars.visualization.maps import ClassifyMapFactory
        try:
            dbf = layer.dbf
            var_list = dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select variable column:","Histogram Plot", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() != wx.ID_OK:
                var_dlg.Destroy()
                return False
            field_name = var_dlg.GetStringSelection()
            var_dlg.Destroy()
            data = np.array(layer.dbf.by_col(field_name))
            
            if map_type in [stars.MAP_CLASSIFY_EQUAL_INTERVAL,
                            stars.MAP_CLASSIFY_QUANTILES,
                            stars.MAP_CLASSIFY_MAXIMUM_BREAK,
                            stars.MAP_CLASSIFY_NATURAL_BREAK,
                            stars.MAP_CLASSIFY_JENKS_CASPALL,
                            stars.MAP_CLASSIFY_JENKS_CASPALL_FORCED,
                            stars.MAP_CLASSIFY_MAX_P]:
                k = self._select_k()
                factory = ClassifyMapFactory(data,k=k)
                
            elif map_type in [stars.MAP_CLASSIFY_JENKS_CASPALL_SAMPLED]:
                k = self._select_k()
                pct = self._choose_sample_percent()
                factory = ClassifyMapFactory(data,k=k)
                
            elif map_type in [stars.MAP_CLASSIFY_BOX_PLOT]:
                hinge = self._choose_box_hinge_value()
                factory = ClassifyMapFactory(data,hinge=hinge)
                
            elif map_type in [stars.MAP_CLASSIFY_USER_DEFINED]:
                bins = self._choose_user_defined_bins()
                if bins == None:
                    raise KeyError
                factory = ClassifyMapFactory(data,bins=bins)
                
            elif map_type in [stars.MAP_CLASSIFY_PERCENTILES,
                              stars.MAP_CLASSIFY_STD_MEAN,
                              stars.MAP_CLASSIFY_FISHER_JENKS]:
                factory = ClassifyMapFactory(data)
                
            elif map_type in [stars.MAP_CLASSIFY_UNIQUE_VALUES]:
                factory = ClassifyMapFactory(data, field_name=field_name)
                
            id_group, label_group, color_group = factory.createClassifyMap(map_type)
            self.color_schema_dict[layer.name] = ColorSchema(color_group, label_group)
            self.draw_layers[layer].set_data_group(id_group)
            self.draw_layers[layer].set_fill_color_group(color_group)
            self.reInitBuffer = True
            return True
        
        except Exception:
            return False
        
    def createLISA(self, layer, map_type=None):
        # support TreeList ctrl
        try:
            from stars.visualization.dialogs import VariableSelDialog, SelectWeightDlg
            from stars.visualization.maps import LISAMap
        
            var_list = layer.dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select variable for LISA","LISA Map", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() != wx.ID_OK:
                var_dlg.Destroy()
                return False
            
            field_name = var_dlg.GetStringSelection()
            data = np.array(layer.dbf.by_col(field_name))
            var_dlg.Destroy()
           
            weight_dlg = SelectWeightDlg(self.main, self.main.dialog_res)
            weight_dlg.dialog.CenterOnScreen()
            if weight_dlg.ShowModal() != wx.ID_OK:
                weight_dlg.Destroy()
                return False
            
            weight_path = weight_dlg.GetWeightPath()
            weight_dlg.Destroy()
       
            id_groups = LISAMap.process_LISA(self, data, weight_path)
            id_groups.insert(0,[])
            
            # default color schema
            color_group =[
                None,
                stars.LISA_NOT_SIG_COLOR, 
                stars.LISA_HH_COLOR,
                stars.LISA_LL_COLOR, 
                stars.LISA_LH_COLOR,
                stars.LISA_HL_COLOR, 
                stars.LISA_OBSOLETE_COLOR
            ]
            label_group = [
                "LISA",
                "Not Significant",
                "High-High",
                "Low-Low",
                "Low-High",
                "High-Low",
                "Neighborless"
            ]
            
            self.color_schema_dict[layer.name] = ColorSchema(color_group,label_group)
            
            self.draw_layers[layer].set_data_group(id_groups)
            self.draw_layers[layer].set_fill_color_group(color_group)
            
            self.reInitBuffer = True
            return True
        except:
            self.ShowMsgBox('LISA map could not be created.')
            return False
            