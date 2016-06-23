"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['DataListCtrl','DataTablePanel','DataWidget']

import sys
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.grid as gridlib

import stars
from stars.model import *
from stars.visualization.EventHandler import * 
from stars.visualization.AbstractWidget import *
from stars.visualization.AbstractCanvas import AbstractCanvas 

class DataGrid(wx.grid.Grid):
    def __init__(self, parent, dbf):
        wx.grid.Grid.__init__(self, parent, -1)
   
        self.dbf = dbf
        n_cols = len(dbf.header)
        n_rows = dbf.n_records
        self.CreateGrid(n_rows, n_cols)
       
        raw_dbf_data = []
        for i in range(n_rows):
            row_data = dbf.read_record(i)
            for j in range(n_cols):
                self.SetCellValue(i,j, str(row_data[j]))
            raw_dbf_data.append(row_data)
        self.dbf.records = raw_dbf_data
        
        for i in range(n_cols):
            self.SetColLabelValue(i, dbf.header[i])
            
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
    def OnIdle(self, event):
        pass

class DataTablePanel1(wx.Panel, AbstractCanvas):
    """
    Panel displaying dbf DataTable.
    The wxPanel container for DataList (wx.ListCtrl).
    """
    def __init__(self, parent, shapefileObject, name):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        
        from stars.visualization.maps.BaseMap import PolygonLayer, PointLayer, LineLayer
        
        self.layer = shapefileObject
        self.dbf = self.layer.dbf
        self.name = name
        self.parent = parent
        self.current_selected = {}  # {id: centroid}
        self.isEvtHandle = False
        
        self.table = DataGrid(self, self.dbf)        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.table, 1, wx.EXPAND)
       
        if self.layer.shape_type == stars.SHP_POINT:
            self.draw_layer = PointLayer(self,self.layer)
        elif self.layer.shape_type == stars.SHP_LINE:
            self.draw_layer = LineLayer(self, self.layer)
        elif self.layer.shape_type == stars.SHP_POLYGON:
            self.draw_layer = PolygonLayer(self,self.layer)  
             
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        # table events
        #self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        #self.table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        
        # register event_handler to THE OBSERVER
        while parent != None:
            if isinstance(parent, stars.Main):
                self.observer = parent.observer
            parent = parent.GetParent()
            
        self.Register(stars.EVT_OBJS_SELECT, self.OnRecordsSelect)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoRecordSelect)
        
        self.parent.Bind(wx.EVT_CLOSE, self.OnClose) # OnClose Only send to Frame/Dialog
        
    def OnClose(self, event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnRecordsSelect)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoRecordSelect)
        event.Skip()
        
    def OnRecordsSelect(self, event):
        pass
    
    def OnNoRecordSelect(self, event):
        pass
    
        
class DataListCtrl(wx.ListCtrl):
    """
    Virtual ListCtrl for fast display on large DBF file
    """
    def __init__(self, parent, ID, dbf, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
       
        self.dbf = dbf
        self.SetItemCount(dbf.n_records)
        
        n_columns = len(dbf.header)
        self.InsertColumn(0, "")
        for i,item in enumerate(dbf.header):
            self.InsertColumn(i+1, item)
            
        self.il = wx.ImageList(16,16)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        self.idx1 = self.il.Add(open_bmp)
        self.SetImageList(self.il,wx.IMAGE_LIST_NORMAL)
        
    def OnGetItemText(self, item, col):
        if col == 0: return str(item+1)
        #return self.dbf.read_record(item)[col]
        return self.dbf.read_record(item)[col-1]


    
class DataTablePanel(wx.Panel, AbstractCanvas,listmix.ColumnSorterMixin):
    """
    Panel displaying dbf DataTable.
    The wxPanel container for DataList (wx.ListCtrl).
    """
    def __init__(self, parent, shapefileObject, name):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        
        from stars.visualization.maps.BaseMap import PolygonLayer, PointLayer, LineLayer
        
        self.layer = shapefileObject
        self.dbf = self.layer.dbf
        self.name = name
        self.parent = parent
        self.current_selected = {}  # {id: centroid}
        self.isEvtHandle = False
        
        tID = wx.NewId()
        self.table = DataListCtrl(
            self, 
            tID,
            self.dbf,
            style=wx.LC_REPORT 
            | wx.LC_VIRTUAL
            #| wx.BORDER_SUNKEN
            | wx.BORDER_NONE
            | wx.LC_EDIT_LABELS
            #| wx.LC_SORT_ASCENDING
            #| wx.LC_NO_HEADER
            | wx.LC_VRULES
            | wx.LC_HRULES
            #| wx.LC_SINGLE_SEL
        )
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.table, 1, wx.EXPAND)
       
        if self.layer.shape_type == stars.SHP_POINT:
            self.draw_layer = PointLayer(self,self.layer)
        elif self.layer.shape_type == stars.SHP_LINE:
            self.draw_layer = LineLayer(self, self.layer)
        elif self.layer.shape_type == stars.SHP_POLYGON:
            self.draw_layer = PolygonLayer(self,self.layer)  
             
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        # table events
        self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        
        # register event_handler to THE OBSERVER
        while parent != None:
            if isinstance(parent, stars.Main):
                self.observer = parent.observer
            parent = parent.GetParent()
            
        self.Register(stars.EVT_OBJS_SELECT, self.OnRecordsSelect)
        self.Register(stars.EVT_OBJS_UNSELECT, self.OnNoRecordSelect)
        
        self.parent.Bind(wx.EVT_CLOSE, self.OnClose) # OnClose Only send to Frame/Dialog
        
    def OnClose(self, event):
        self.Unregister(stars.EVT_OBJS_SELECT, self.OnRecordsSelect)
        self.Unregister(stars.EVT_OBJS_UNSELECT, self.OnNoRecordSelect)
        event.Skip()
                
    def update_table(self, dbf):
        """
        Get and display data from dbf File on DataList (wx.ListCtrl)
        """
        self.table.ClearAll()
        self.table.SetItemCount(dbf.n_records)
        
        n_columns = len(dbf.header)
        self.table.InsertColumn(0, "ID")
        for i,item in enumerate(dbf.header):
            self.table.InsertColumn(i+1, item)
      
    def OnItemSelected(self, event):
        if self.isEvtHandle == False:
            # prevent backforce Event
            if self.table.SelectedItemCount == 1:
                self.current_selected = {}
            if not self.current_selected.has_key(event.m_itemIndex):
                dummy_region = []
                # find centroid of current_select objec
                if self.layer.shape_type == stars.SHP_POLYGON:
                    centroids = self.layer.centroids[event.m_itemIndex]
                    for centroid in centroids:
                        dummy_region += centroid + centroid
                else:
                    point = list(self.layer.shape_objects[event.m_itemIndex])
                    dummy_region = point + point
                    
                self.current_selected[event.m_itemIndex] = dummy_region
                
                # trigger Upadte Event to notify other
                # widgets to drawing the selected items
                self.OnRecordsSelect(None)
        event.Skip()
     
    def OnItemDeselected(self, event):
        if self.isEvtHandle == False:
            # prevent backforce Event
            if self.current_selected.has_key(event.m_itemIndex):
                self.current_selected.pop(event.m_itemIndex)
                # trigger Upadte Event to notify other
                # widgets to drawing the selected items
                self.OnRecordsSelect(None)
        event.Skip()
       
    def unhighlight_selected(self):
        for item in self.current_selected:            
            self.table.SetItemState(item, 0, wx.LIST_STATE_SELECTED)# | wx.LIST_STATE_FOCUSED) 
            
    def highlight_selected(self):
        if len(self.current_selected) > 0:
            first = self.current_selected.keys()[0]
            for item in self.current_selected:
                if item == first:
                    self.table.EnsureVisible(item)
                self.table.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)#|wx.LIST_STATE_FOCUSED) 
        
        
    #------------------------------
    # Belows are Event handlers
    #------------------------------
    def OnRecordsSelect(self, event):
        if event == None:
            # trigger other widgets
            data = AbstractData(self)
            data.shape_ids[self.name] =  self.current_selected.keys()
            data.boundary = self.current_selected.values()
            self.UpdateEvt(stars.EVT_OBJS_SELECT, data)
        else:
            # trigged by other widgets
            self.isEvtHandle = True
            data = event.data
            if data.shape_ids.has_key(self.name):
                # unselect first
                self.unhighlight_selected()
                # then select trigged
                selected_id_list = data.shape_ids[self.name]
                self.current_selected = {}
                for i in selected_id_list:
                    self.current_selected[i] = None
                self.highlight_selected()
            else:
                # unselect first
                self.unhighlight_selected()
                self.current_selected = {}
                # try to test if query regions can be used
                # to find shape ids
                query_regions = data.boundary
                if query_regions == None or len(query_regions) == 0:
                    pass
                else:
                    if isinstance(query_regions[0], float):
                        query_regions = [query_regions]
                    for region in query_regions:
                        shape_ids, query_region = self.draw_layer.get_selected_by_region(None, region)
                        for id in shape_ids:
                            self.current_selected[id] = None
                    self.highlight_selected()
            self.isEvtHandle = False
    
    def OnNoRecordSelect(self, event):
        self.isEvtHandle = True
        for item in self.current_selected:            
            self.table.SetItemState(item, 0, wx.LIST_STATE_SELECTED)# | wx.LIST_STATE_FOCUSED) 
        self.isEvtHandle = False
   
    
class DataWidget(AbstractWidget):
    """
    Widget for displaying dbf table, the layout should be like this:
    -------------------------
    | toolbar                |
    --------------------------
    |                        |
    |                        |
    |      Table             |
    |                        |
    |                        |
    --------------------------
    """
    def __init__(self, parent, shp, name):
        self.shp= shp
        self.name = name
        
        AbstractWidget.__init__(self, parent, self.name, pos=(60, 60), size=(600, 350))
       
        #self.toolbar = self._create_toolbar()
        #self.SetToolBar(self.toolbar)
        #self.toolbar.Realize()
        self.status_bar = self.CreateStatusBar()
        self.data_table = DataTablePanel(self,self.shp,self.name)
        self.canvas = self.data_table
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.data_table, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
    def _create_toolbar(self):
        tsize = (16,16)
        toolbar = self.CreateToolBar()
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        close_bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, tsize)
        toolbar.AddLabelTool(1001, "Filter Data", open_bmp)
        toolbar.AddLabelTool(1002, "Close", close_bmp)
        toolbar.EnableTool(1002, False)
        self.Bind(wx.EVT_TOOL, self.OnFilterData, id=1001)
        return toolbar
    
    def OnFilterData(self,event):
        frame = SpaceTimeQuery(self.data_table, "SpaceTime Query", self.dbf)
        frame.Show()
        