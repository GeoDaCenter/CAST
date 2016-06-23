"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['LayerTree','MapWidget']

import os, time
import wx,wx.lib.customtreectrl
from wx import xrc

import stars
from stars.model import CShapeFileObject 
from AbstractWidget import AbstractWidget 
from utils import GetRandomColor
from DataWidget import DataWidget

class LayerTree(wx.ScrolledWindow):    
    """
    A Tree control to list all opened shape file layers
    """
    def __init__(self, parent, map_layers):
        wx.ScrolledWindow.__init__(self, parent, -1)
       
        self.map_layers = map_layers
        self.layer_dict = {}
        
        self.SetBackgroundColour("WHITE")
        self.SetScrollRate(20,20)
        
        # NOTE: this ctrl only works in wxpython 2.8.12
        self.tree = wx.lib.customtreectrl.CustomTreeCtrl(
            self, -1, size=wx.DefaultSize, 
            agwStyle=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES |wx.TR_HIDE_ROOT|wx.TR_HAS_VARIABLE_ROW_HEIGHT
        )
        
        self.root = self.tree.AddRoot("Invisible Root")
        self.tree.SetPyData(self.root, None)
  
        sizer = wx.BoxSizer()
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.tree.SetPosition((-20,0))
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        self.tree.Bind(wx.lib.customtreectrl.EVT_TREE_ITEM_CHECKED, self.OnNodeChecked)
        # These go at the end of __init__
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginLeftDrag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        
    def setup_tree(self, map_canvas):
        """
        Mapcanvas can use this function to setup a tree with 
        customized legend and color schemas
        """
        self.map_canvas = map_canvas
        self.color_schema_dict = map_canvas.color_schema_dict
        self.map_layers = map_canvas.layers
            
        for layer in self.map_layers:
            self.layer_dict[layer.name] = layer
            
        # check dummy layer e.g. density map
        for layer_name in self.color_schema_dict.keys():
            if layer_name not in self.layer_dict: # e.g. density map
                self.layer_dict[layer_name] = None
                
        image_dict = {}
        isz = (16,16)
        n = len(self.color_schema_dict)
        il = wx.ImageList(isz[0], isz[1])
        
        self.node_list = []
        for layer_name in self.layer_dict.keys():
            self.node_list.append(layer_name)
            color_schema = self.color_schema_dict[layer_name]
            idx_list = []
            for bmp in color_schema.bmps:
                idx = il.Add(bmp)
                idx_list.append(idx)
            image_dict[layer_name] = idx_list
        self.tree.SetImageList(il)
        
        self.il = il
        self.isz = isz
        self.image_dict = image_dict
        
        for layer_name in self.node_list:
            self.appendTreeNode(layer_name)
            
        self.tree.ExpandAll()

    def add_layer(self,layer):
        try:
            self.node_list.index(layer.name)
            dlg = wx.MessageDialog(self, "%s already existed!" % layer.name,'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        except ValueError:
            # not found, then continue to add one
        
            # call map_canvas to add layer
            self.map_canvas.add_layer(layer)
            
            # note: donnot know why new added layer appears twice in self.node_list
            # temporary solution: check the layer.name in self.node_list again
            try:
                self.node_list.index(layer.name)
            except:
                self.node_list.append(layer.name)
                
            self.layer_dict[layer.name] = layer
            color_schema = self.color_schema_dict[layer.name]
            idx_list = []
            for bmp in color_schema.bmps:
                idx = self.il.Add(bmp)
                idx_list.append(idx)
            self.image_dict[layer.name] = idx_list
            self.tree.SetImageList(self.il)
            
            self.appendTreeNode(layer.name)
            self.tree.ExpandAll()
    
    def remove_layer(self):
        item = self.tree.GetSelection()
        if self.tree.GetItemParent(item) != self.root:
            dlg = wx.MessageDialog(self, "Please select a valid layer.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        layer_name = self.tree.GetItemText(item)
        if layer_name == 'Density Map':
            dlg = wx.MessageDialog(self, "Sorry, can't remove a density map.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
            
        for layer in self.map_layers:
            if layer.name == layer_name:
                break
        # call map_canvas to remove layer
        if self.map_canvas.remove_layer(layer) == False:
            return
        
        # remove it from tree
        self.layer_dict.pop(layer_name)
        self.image_dict.pop(layer_name)
        try:
            self.node_list.remove(layer_name)
        except:
            pass
        self.tree.Delete(item)
    
    def appendTreeNode(self, layer_name,layer=None):
        try:
            color_schema = self.color_schema_dict[layer_name]
            child = self.tree.AppendItem(self.root, layer_name,ct_type=1) #ct_type=1 checkbox
            self.tree.CheckItem(child,checked=True)
            self.tree.SetPyData(child, layer)
                
            image_idx_list = self.image_dict[layer_name]
            if layer_name == "Density Map":
                gradient_panel = wx.Panel(self.tree,-1,(0,0),(60,100))
                bmp = color_schema.gradient_color.get_bmp(16,100)
                wx.StaticBitmap(gradient_panel, -1, bmp)
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
                wx.StaticText(gradient_panel, -1, "%.1f"%self.map_canvas.gradient_color_max,pos=(17,0),size=(30,-1)).SetFont(font)
                wx.StaticText(gradient_panel, -1, "%.1f"%self.map_canvas.gradient_color_min,pos=(17,88),size=(30,-1)).SetFont(font)
                legend = self.tree.AppendItem(child, "", wnd=gradient_panel) #ct_type=1 checkbox
            else:
                """
                for i,image_idx in enumerate(image_idx_list):
                    legend = self.tree.AppendItem(child, color_schema.labels[i])
                    self.tree.SetPyData(legend,i)
                    self.tree.SetItemImage(legend, image_idx, wx.TreeItemIcon_Normal)
                """ 
                legend_img_count = 0
                for i,label in enumerate(color_schema.labels):
                    legend = self.tree.AppendItem(child, color_schema.labels[i])
                    if color_schema.GetBmp(label):
                        self.tree.SetPyData(legend, legend_img_count)
                        image_idx = image_idx_list[legend_img_count]
                        legend_img_count += 1
                        self.tree.SetItemImage(legend, image_idx, wx.TreeItemIcon_Normal)
                    else:
                        self.tree.SetPyData(legend, None)
                    
        except Exception as err:
            dlg = wx.MessageDialog(self, """Could not create this window.
            
Detail: """ + str(err.message), 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
           
    def moveTreeNode(self, frm, to, after=True):
        self.node_list.remove(frm)
        to_idx = self.node_list.index(to)
        to_idx = to_idx + after
        self.node_list.insert(to_idx, frm)
    
    def createCustomizedMap(self, layer_node, customizeFunc, map_type=None):
        layer_idx = self.tree.GetItemImage(layer_node)
        
        if layer_idx >= 0: # only applied to LayerNode
            return
        
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]

        # create customized map
        if customizeFunc(layer, map_type):
            self.color_schema_dict = self.map_canvas.color_schema_dict
           
            # first remove it from tree
            self.layer_dict.pop(layer_name)
            self.image_dict.pop(layer_name)
            self.node_list.remove(layer_name)
            self.tree.Delete(layer_node)
            
            # second add new map to tree
            self.layer_dict[layer.name] = layer
            self.node_list.append(layer.name)
            color_schema = self.color_schema_dict[layer.name]
            idx_list = []
            for bmp in color_schema.bmps:
                idx = self.il.Add(bmp)
                idx_list.append(idx)
            self.image_dict[layer.name] = idx_list
            self.tree.SetImageList(self.il)
            
            self.appendTreeNode(layer.name)
            self.tree.ExpandAll()

    def findLayerNodeByName(self, name):
        if name and len(name)>0:
            node, cookie = self.tree.GetFirstChild(self.root)
            while node and node.IsOk():
                if node.GetText() == name:
                    return node
                node,cookie = self.tree.GetNextChild(node, cookie)
            
    def updateLayer(self, layer):
        # when color_schema_dict from ShapeMap changed
        # redraw and update current tree structure
        # create customized map
        if layer:
            self.color_schema_dict = self.map_canvas.color_schema_dict
            layer_name = layer.name
           
            # find the target node
            layer_node = self.findLayerNodeByName(layer_name)
            
            # first remove it from tree
            self.layer_dict.pop(layer_name)
            self.image_dict.pop(layer_name)
            self.node_list.remove(layer_name)
            self.tree.Delete(layer_node)
            
            # second add new map to tree
            self.layer_dict[layer.name] = layer
            self.node_list.append(layer.name)
            color_schema = self.color_schema_dict[layer.name]
            idx_list = []
            for bmp in color_schema.bmps:
                idx = self.il.Add(bmp)
                idx_list.append(idx)
            self.image_dict[layer.name] = idx_list
            self.tree.SetImageList(self.il)
            
            self.appendTreeNode(layer.name)
            self.tree.ExpandAll()
        
        
    def createClassifyMap(self,event):
        if event.Id == 205:
            map_type = stars.MAP_CLASSIFY_PERCENTILES
        elif event.Id == 206:
            map_type = stars.MAP_CLASSIFY_QUANTILES
        elif event.Id == 207:
            map_type = stars.MAP_CLASSIFY_STD_MEAN
        elif event.Id == 208:
            map_type = stars.MAP_CLASSIFY_BOX_PLOT
        elif event.Id == 211:
            map_type = stars.MAP_CLASSIFY_EQUAL_INTERVAL
        elif event.Id == 212:
            map_type = stars.MAP_CLASSIFY_MAXIMUM_BREAK
        elif event.Id == 213:
            map_type = stars.MAP_CLASSIFY_NATURAL_BREAK
        elif event.Id == 214:
            map_type = stars.MAP_CLASSIFY_JENKS_CASPALL
        elif event.Id == 215:
            map_type = stars.MAP_CLASSIFY_JENKS_CASPALL_SAMPLED
        elif event.Id == 216:
            map_type = stars.MAP_CLASSIFY_JENKS_CASPALL_FORCED
        elif event.Id == 217:
            map_type = stars.MAP_CLASSIFY_FISHER_JENKS
        elif event.Id == 218:
            map_type = stars.MAP_CLASSIFY_MAX_P
        elif event.Id == 219:
            map_type = stars.MAP_CLASSIFY_USER_DEFINED
            
        layer_node = self.tree.GetSelection()
        self.createCustomizedMap(layer_node, self.map_canvas.createClassifyMap, map_type)
        
    def createLISA(self, event):
        layer_node = self.tree.GetSelection()
        self.createCustomizedMap(layer_node, self.map_canvas.createLISA)
    
    def resetMap(self, event):
        layer_node = self.tree.GetSelection()
        self.createCustomizedMap(layer_node, self.map_canvas.resetMap)
        
    def extentToLayer(self, event):
        layer_node = self.tree.GetSelection()
        layer_idx = self.tree.GetItemImage(layer_node)
        
        if layer_idx >= 0: # only applied to LayerNode
            return
        
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
       
        self.map_canvas.extentToLayer(layer)
        
    def openDBFTable(self, event):
        layer_node = self.tree.GetSelection()
        layer_idx = self.tree.GetItemImage(layer_node)
        
        if layer_idx >= 0: # only applied to LayerNode
            return
        
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        dbf = layer.dbf
        dbf_widget = DataWidget(self, layer, layer_name)
        dbf_widget.Show()
        
    def changeColor(self,event):
        img_node = self.tree.GetSelection()
        img_idx = self.tree.GetItemImage(img_node)
        
        if img_idx < 0: # only applied to ColorNode
            dlg = wx.MessageDialog(self, "Change color only apply to Color Node.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        img_node_idx = self.tree.GetItemPyData(img_node)
        img_node_label = self.tree.GetItemText(img_node)
        layer_node = self.tree.GetItemParent(img_node)
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        orig_color = self.map_canvas.color_schema_dict[layer_name].colors[img_node_idx]
        
        data = wx.ColourData()
        data.SetChooseFull(True)
        data.SetColour(orig_color)
        
        dlg = wx.ColourDialog(self,data)
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            clr = data.GetColour()
           
            # update map
            color_schema = self.map_canvas.update_color_schema(layer, img_node_label, clr, None)
            self.color_schema_dict = self.map_canvas.color_schema_dict
            
            # update tree
            self.il.Replace(img_idx, color_schema.GetBmp(img_node_label) )
            self.tree.SetImageList(self.il)
            self.tree.SetItemImage(img_node, img_idx, wx.TreeItemIcon_Normal)
            
        dlg.Destroy()
    
    def changeOutlineColor(self, event):
        img_node = self.tree.GetSelection()
        img_idx = self.tree.GetItemImage(img_node)
        
        if img_idx < 0: # only applied to ColorNode
            dlg = wx.MessageDialog(self, "Change color only apply to Color Node.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        img_node_idx = self.tree.GetItemPyData(img_node)
        img_node_label = self.tree.GetItemText(img_node)
        layer_node = self.tree.GetItemParent(img_node)
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            clr = data.GetColour()
           
            # update map
            color_schema = self.map_canvas.update_color_schema(layer, img_node_label, None, clr)
            self.color_schema_dict = self.map_canvas.color_schema_dict
            
            # update tree
            color_node, cookie = self.tree.GetFirstChild(layer_node)
            while color_node and color_node.IsOk():
                img_idx = self.tree.GetItemPyData(color_node)
                if img_idx != None:
                    label = self.tree.GetItemText(color_node)
                    
                    self.il.Replace(img_idx, color_schema.GetBmp(label))
                    self.tree.SetImageList(self.il)
                    self.tree.SetItemImage(color_node, img_idx, wx.TreeItemIcon_Normal)
                color_node,cookie = self.tree.GetNextChild(layer_node, cookie)
        dlg.Destroy()
        
    def hideOutline(self, event):
        img_node = self.tree.GetSelection()
        img_idx = self.tree.GetItemImage(img_node)
        
        if img_idx < 0: # only applied to ColorNode
            dlg = wx.MessageDialog(self, "Change color only apply to Color Node.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        img_node_idx = self.tree.GetItemPyData(img_node)
        img_node_label = self.tree.GetItemText(img_node)
        layer_node = self.tree.GetItemParent(img_node)
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        
        clr = wx.WHITE  # todo: white outline will be processed as transparency
       
        # update map
        color_schema = self.map_canvas.update_color_schema(layer, img_node_label, None, clr)
        self.color_schema_dict = self.map_canvas.color_schema_dict
        
        # update tree
        color_node, cookie = self.tree.GetFirstChild(layer_node)
        while color_node and color_node.IsOk():
            img_idx = self.tree.GetItemPyData(color_node)
            if img_idx != None:
                label = self.tree.GetItemText(color_node)
                
                self.il.Replace(img_idx, color_schema.GetBmp(label))
                self.tree.SetImageList(self.il)
                self.tree.SetItemImage(color_node, img_idx, wx.TreeItemIcon_Normal)
            color_node,cookie = self.tree.GetNextChild(layer_node, cookie)
        
    def displayOutline(self, event):
        img_node = self.tree.GetSelection()
        img_idx = self.tree.GetItemImage(img_node)
        
        if img_idx < 0: # only applied to ColorNode
            dlg = wx.MessageDialog(self, "Change color only apply to Color Node.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        img_node_idx = self.tree.GetItemPyData(img_node)
        img_node_label = self.tree.GetItemText(img_node)
        layer_node = self.tree.GetItemParent(img_node)
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        
        clr = wx.BLACK # todo: white outline will be processed as transparency
       
        # update map
        color_schema = self.map_canvas.update_color_schema(layer, img_node_label, None, clr)
        self.color_schema_dict = self.map_canvas.color_schema_dict
        
        # update tree
        color_node, cookie = self.tree.GetFirstChild(layer_node)
        while color_node and color_node.IsOk():
            img_idx = self.tree.GetItemPyData(color_node)
            if img_idx != None:
                label = self.tree.GetItemText(color_node)
                
                self.il.Replace(img_idx, color_schema.GetBmp(label))
                self.tree.SetImageList(self.il)
                self.tree.SetItemImage(color_node, img_idx, wx.TreeItemIcon_Normal)
            color_node,cookie = self.tree.GetNextChild(layer_node, cookie)
        
        
    def changeTransparency(self,event):
        layer_node = self.tree.GetSelection()
        layer_idx = self.tree.GetItemImage(layer_node)
        
        if layer_idx >= 0: # only applied to LayerNode
            dlg = wx.MessageDialog(self, "Change transparency only apply to Layer Node.", 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
       
        from stars.visualization.dialogs import TransparentDlg
        dlg = TransparentDlg(self.map_canvas, layer_name)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            opaque = dlg.slideralpha.GetValue()*2.55
            # update opaque for color schema
            color_schema = self.map_canvas.color_schema_dict[layer_name]
            color_schema.SetOpaque(opaque)
            edge_color = color_schema.edge_color
            color_node, cookie = self.tree.GetFirstChild(layer_node)
            img_node_idx_prefix = 0
            while color_node and color_node.IsOk():
                img_node_idx = self.tree.GetItemPyData(color_node)
                if img_node_idx != None: # for pure text node
                    clr = color_schema.colors[img_node_idx + img_node_idx_prefix]
                    if clr != None:
                        clr=wx.Colour(clr.red,clr.green,clr.blue,opaque)
                        img_node_label = color_node.GetText()
                        self.map_canvas.update_color_schema(layer, img_node_label, clr,edge_color)
                else:
                    img_node_idx_prefix += 1 # handle the pure text node case
                color_node,cookie = self.tree.GetNextChild(layer_node, cookie)
                
            self.color_schema_dict = self.map_canvas.color_schema_dict
            
        dlg.Destroy()
    
    def changeDensityMapGradient(self, event):
        from stars.visualization.dialogs import GradientDlg
        dlg = GradientDlg(self.map_canvas)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            gradient_type = dlg.gradient_type
            gradient_color = self.map_canvas.UpdateGradient(gradient_type)

            # update tree
            item = self.tree.GetSelection()
            child,cookie = self.tree.GetFirstChild(item)
            
            gradient = wx.Panel(self.tree,-1,(0,0),(24,100))
            bmp = gradient_color.gradient_color.get_bmp(16,100)
            wx.StaticBitmap(gradient, -1, bmp)

            self.tree.AppendItem(item, "", wnd=gradient)
            self.tree.Delete(child)
        dlg.Destroy()

    def changeDensityMapTransparency(self, event):
        from stars.visualization.dialogs import TransparentDlg
        dlg = TransparentDlg(self.map_canvas,"Density Map")
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            opaque = dlg.slideralpha.GetValue()
            self.map_canvas.UpdateOpaque(opaque)
        dlg.Destroy()
    
    #----------------------------------
    # Belows are mouse events
    #---------------------------------- 
    def OnNodeChecked(self, event):
        layer_node = event.GetItem()
        layer_name = self.tree.GetItemText(layer_node)
        layer = self.layer_dict[layer_name]
        
        if self.tree.IsItemChecked(layer_node):
            self.map_canvas.hide_layer(layer, False)
        else:
            self.map_canvas.hide_layer(layer,True)
        event.Skip()
        
    def OnRightClick(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        
        if not item or not item.IsOk():
            return
        
        self.tree.SelectItem(item)
        layer_name = self.tree.GetItemText(item)
        layer_node = self.tree.GetSelection()
        layer_idx = self.tree.GetItemImage(layer_node)
        parent_layer_name = self.tree.GetItemText(layer_node.GetParent())
        
        menu = wx.Menu()
        if layer_name == "Density Map":
            menu.Append(210, "Change gradient", "")
            menu.Append(211, "Change transparency", "")
            menu.Bind(wx.EVT_MENU, self.changeDensityMapGradient, id=210)
            menu.Bind(wx.EVT_MENU, self.changeDensityMapTransparency, id=211)
        else:    
            if 'Root' in parent_layer_name:
                # for layer node
                menu.Append(202, "Change transparency", "")
                menu.Append(203, "Open DBF Table", "")
                menu.Append(204, "Full Extent", "")
                menu.Bind(wx.EVT_MENU, self.changeTransparency, id=202)
                menu.Bind(wx.EVT_MENU, self.openDBFTable, id=203)
                menu.Bind(wx.EVT_MENU, self.extentToLayer, id=204)
        
                if self.map_canvas.__class__ == stars.visualization.maps.ShapeMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.LISAMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.DynamicLISAMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.DensityMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.DynamicDensityMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.DynamicCalendarMap or\
                   self.map_canvas.__class__ == stars.visualization.maps.CalendarMap:
                   
                    menu.AppendSeparator()
                    menu.Append(280, "LISA Map", "")
                    menu.AppendSeparator()
                    menu.Append(205, "Percentile Map", "")
                    menu.Append(206, "Quantile Map", "")
                    menu.Append(207, "Std Mean Map", "")
                    menu.Append(208, "Box Map", "")
                    menu.Append(211, "Equal Interval Map", "")
                    menu.Append(212, "Maximum Break Map", "")
                    menu.Append(213, "Natural Break Map", "")
                    #menu.Append(214, "Jenks Caspall Map", "")
                    #menu.Append(215, "Jenks Caspall Sampled Map", "")
                    #menu.Append(216, "Jenks Caspall Forced Map", "")
                    #menu.Append(217, "Fisher Jenks Map", "")
                    #menu.Append(218, "Max P Map", "")
                    #menu.Append(219, "User Defined Map", "")
                    menu.AppendSeparator()
                    menu.Append(299, "Reset Map", "")
                    
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=205)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=206)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=207)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=208)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=211)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=212)
                    menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=213)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=214)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=215)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=216)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=217)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=218)
                    #menu.Bind(wx.EVT_MENU, self.createClassifyMap, id=219)
                    
                    menu.Bind(wx.EVT_MENU, self.createLISA, id=280)
                    menu.Bind(wx.EVT_MENU, self.resetMap, id=299)
                
            elif layer_idx >= 0:
                # for item node
                menu.Append(200, "Change color", "")
                menu.Append(201, "Change outline color", "")
                menu.AppendSeparator()
                menu.Append(901, "Hide outline", "")
                menu.Append(902, "Display outline", "")
                menu.Bind(wx.EVT_MENU, self.changeColor, id=200)
                menu.Bind(wx.EVT_MENU, self.changeOutlineColor, id=201)
                menu.Bind(wx.EVT_MENU, self.hideOutline, id=901)
                menu.Bind(wx.EVT_MENU, self.displayOutline, id=902)
                
        menu.UpdateUI()
        self.PopupMenu(menu)
        
        event.Skip()
        
    def OnLeftDClick(self,event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item.IsOk():
            self.tree.Toggle(item)
        event.Skip()
    
    def OnLeftClick(self,event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if None == item:
            return
        
        if not item or item.IsOk():
            self.tree.SelectItem(item)
            
        event.Skip()
    
    def OnBeginLeftDrag(self,event):
        #Allow drag-and-drop for leaf nodes.
        self.dragItem = event.GetItem()
        if self.tree.GetItemImage(self.dragItem) >0:
            event.Skip()
            return
        event.Allow()
    
    def OnEndDrag(self,event):
        #Allow drag-and-drop for leaf nodes.
        selectItem = event.GetItem()
        if selectItem and event.GetItem().IsOk():
            target = event.GetItem()
        else:
            return
        
        try:
            source = self.dragItem
        except:
            return
        
        if self.tree.GetItemParent(target) != self.root or\
           self.tree.GetItemParent(source) != self.root:
            self.tree.Unselect()
            return
            
        def MoveHere(event):
            try:
                from_name = self.tree.GetItemText(source)
                to_name = self.tree.GetItemText(target)
                
                after = True if event.Id == 102 else False
                self.moveTreeNode(from_name, to_name, after)
                self.tree.DeleteChildren(self.root)
                for layer_name in self.node_list:
                    self.appendTreeNode(layer_name)
                self.tree.ExpandAll()
                
                # update drawing maps
                self.map_canvas.arrange_layers_by_names(self.node_list)
            except:
                pass
       
        menu = wx.Menu()
        menu.Append(101, "Move above this layer", "")
        menu.Append(102, "Move below this layer", "")
        menu.UpdateUI()
        menu.Bind(wx.EVT_MENU, MoveHere, id=101)
        menu.Bind(wx.EVT_MENU, MoveHere, id=102)
        self.PopupMenu(menu)
        

class MapWidget(AbstractWidget):
    """
    Widget for displaying maps, the layout should be like this:
    -------------------------
    | toolbar                |
    --------------------------
    |  l |                   |
    |  a |                   |
    |  y |     map           |
    |  e |                   |
    |  r |                   |
    --------------------------
    """
    def __init__(self, parent, layers, canvas,**kwargs):
        title = ""
        size = (600,350)
        pos = (100,160)
        
        if kwargs.has_key("size"):
            size = kwargs["size"]
        if kwargs.has_key("pos"):
            pos = kwargs["pos"]
        if kwargs.has_key("title"):
            title = kwargs["title"]
            
        AbstractWidget.__init__(self, parent, title, pos=pos, size=size)
       
        self.layers = layers
        self.setup_toolbar()
        self.status_bar = self.CreateStatusBar()
       
        self.kwargs = kwargs
        self.kwargs['size'] = (size[0]-163,size[1]-40) # TODO: this value is only for (600,350) frame size
        
        self.splitter = wx.SplitterWindow(self, -1,style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE )
        self.layer_list_panel = LayerTree(self.splitter, layers)
        self.canvas = None
        
        if self.init_map(canvas):
            sizer = wx.BoxSizer()
            sizer.Add(self.splitter, 1, wx.EXPAND)
            self.SetSizer(sizer)
            self.SetAutoLayout(True)
     
    def setup_toolbar(self):
        self.toolbar = self.stars.toolbar_res.LoadToolBar(self,'ToolBar_MAP')
        self.SetToolBar(self.toolbar)
        
        # bindings
        self.Bind(wx.EVT_TOOL, self.OnAddLayer, id=xrc.XRCID('ID_ADD_MAP_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnRemoveLayer, id=xrc.XRCID('ID_REMOVE_MAP_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnSelect, id=xrc.XRCID('ID_SELECT_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnPan, id=xrc.XRCID('ID_PAN_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnZoom, id=xrc.XRCID('ID_ZOOM_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnExtent, id=xrc.XRCID('ID_EXTENT_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnRefresh, id=xrc.XRCID('ID_REFRESH_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnBrush, id=xrc.XRCID('ID_BRUSH_LAYER'))
        self.Bind(wx.EVT_TOOL, self.OnExport, id=xrc.XRCID('ID_EXPORT_MAP'))
        
    def init_map(self,canvas):
        # plugin map widget
        self.canvas = canvas(self.splitter, self.layers, **self.kwargs)
        if self.canvas:
            self.splitter.SplitVertically(self.layer_list_panel, self.canvas, 160)
            self.layer_list_panel.setup_tree(self.canvas)
            return True
        return False
      
    def OnAddLayer(self, event):
        dlg = wx.FileDialog(self, message="Choose a file", 
                            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
                            style=wx.OPEN| wx.CHANGE_DIR)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        
        shp_name = os.path.splitext(os.path.basename(path))[0]
        # check existence
        b_shp_exist = False
        for shp in self.stars.shapefiles:
            if shp.name == shp_name:
                b_shp_exist = True
                layer = shp
                break
        if b_shp_exist == False:
            layer = CShapeFileObject(path)
            if layer.shape_type == 0:
                self.ShowMsgBox("This shapefile type is not supported.")
                return
            self.stars.shapefiles.append(layer)
                
        # call TreeCtrl to add layer
        self.layer_list_panel.add_layer(layer)
   
    def OnRemoveLayer(self, event):
        self.layer_list_panel.remove_layer()
    
    def OnSelect(self,event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        self.canvas.reset_map_operator()
        
    def OnZoom(self,event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_MAGNIFIER))
        self.canvas.map_operation_type = stars.MAP_OP_ZOOMIN
    
    def OnPan(self,event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.canvas.map_operation_type = stars.MAP_OP_PAN
    
    def OnRefresh(self,event):
        self.canvas.Refresh()
        
    def OnExtent(self,event):
        self.canvas.restore()
        #self.canvas.extentToLayer(self.layers[0])
    
    def OnBrush(self,event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_PAINT_BRUSH))
        self.canvas.map_operation_type = stars.MAP_OP_BRUSHING
        self.canvas.brushing_height = 0
        self.canvas.brushing_width = 0
        self.canvas.isBrushing = True
        
    def OnExport(self, event):
        dlg = wx.FileDialog(
            self, message="Export maps as a Bitmap file...", defaultDir=os.getcwd(), 
            defaultFile='maps.bmp', 
            wildcard="bmp file (*.bmp)|*.bmp|png file (*.png)|*.png|"\
                     "jpg file (*.jpg)|*.jpg|tif file (*.tif)|*.tif|All files (*.*)|*.*", 
            style=wx.SAVE
            )
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        filetype = path[:-3]
        imagetype = wx.BITMAP_TYPE_PNG
        if filetype == 'bmp':
            imagetype = wx.BITMAP_TYPE_BMP
        elif filetype == 'png':
            imagetype = wx.BITMAP_TYPE_PNG
        elif filetype == 'jpg':
            imagetype = wx.BITMAP_TYPE_JPEG
        elif filetype == 'tif':
            imagetype = wx.BITMAP_TYPE_TIF
        self.canvas.buffer.SaveFile(path, imagetype)
