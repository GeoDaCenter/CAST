"""
The main entry of Stars program.
A toolbar with menu will be displayed.
All widgets will be created/destroyed/managed here.
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ =['Main','main']

import os,platform,sys
import wx
from wx import xrc
import pysal

from stars.Plugin import *
from stars.model import *
from stars.visualization import *
from stars.visualization.utils import *
from stars.visualization.maps import *
from stars.visualization.plots import *
from stars.visualization.dialogs import *
from stars.rc.artprovider import StarsArtProvider
from stars.rc.stars_toolbar import stars_toolbar
from stars.rc.stars_menus import stars_menus
from stars.rc.stars_dialogs import stars_dialogs
from stars.rc.logoimages import logo

class Main(wx.Frame):
    """
    Main GUI for Stars program. 
    """
    def __init__(self, parent, **kwargs):
        
        size = stars.APP_SIZE_WIN
        pos = stars.APP_POS_WIN
        
        if os.name == 'posix':
            size = stars.APP_SIZE_MAC
            pos = stars.APP_POS_MAC
            if 'Linux' in  stars.APP_PLATFORM:
                size = stars.APP_SIZE_LINUX
                pos = stars.APP_POS_LINUX
        else:
            import ctypes
            if ctypes.windll.UxTheme.IsThemeActive():
                size = stars.APP_SIZE_WIN_THEME
            
        wx.Frame.__init__(
            self, parent, -1, 
            "CAST (alpha)",
            pos=pos, size=size)
       
        # main variables 
        self.shapefiles = []
        self.datafiles = []
        self.weightsfiles = []
       
        wx.ArtProvider.Push(StarsArtProvider())
        
        #self.logo = wx.Icon('stars/rc/stars-logo.ico', wx.BITMAP_TYPE_ICO)
        self.logo = logo.GetIcon()
        self.SetIcon(self.logo)
        
        #self.dialog_res = xrc.XmlResource('stars/rc/stars_dialogs.xrc')
        self.dialog_res = wx.xrc.EmptyXmlResource()
        self.dialog_res.LoadFromString(stars_dialogs.strip())
        
        #self.toolbar_res = xrc.XmlResource('stars/rc/stars_toolbar.xrc')
        self.toolbar_res= wx.xrc.EmptyXmlResource()
        self.toolbar_res.LoadFromString(stars_toolbar.strip())
        self.toolbar = self.toolbar_res.LoadToolBar(self,'ToolBar')
        self.SetToolBar(self.toolbar)
        
        #self.menu_res = xrc.XmlResource('stars/rc/stars_menus.xrc')
        self.menu_res = wx.xrc.EmptyXmlResource()
        self.menu_res.LoadFromString(stars_menus.strip())
        self.menubar = self.menu_res.LoadMenuBar('ID_SHARED_MAIN_MENU')
        self.SetMenuBar(self.menubar)
        
        self.observer = EventHandler()
       
        self.menu_dict = self._create_menu_dict()
        #self.LoadPlugins()
        
        # Binding Events
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        self.Bind(wx.EVT_MENU, self.OnOpenSHPFile, id=xrc.XRCID('ID_OPEN_SHAPE_FILE'))
        self.Bind(wx.EVT_MENU, self.OnCloseAll, id=xrc.XRCID('ID_CLOSE_ALL'))
        self.Bind(wx.EVT_MENU, self.OnPolysFromGrid, id=xrc.XRCID('ID_SHAPE_POLYGONS_FROM_GRID'))
        
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_QUANTILE'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_PERCENTILE'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_BOXPLOT'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_STDDEV'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_UNIQUE_VALUES'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_NATURAL_BREAKS'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_MAXIMUM_BREAKS'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_EQUAL_INTERVALS'))
        self.Bind(wx.EVT_MENU, self.OnClassifyMap, id=xrc.XRCID('ID_OPEN_MAPANALYSIS_JENKS_CASPALL'))
        
        
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_SMOOTH_RAWRATE'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_SMOOTH_EXCESSRISK'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_EMPERICAL_BAYES_SMOOTHER'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_SPATIAL_RATE_SMOOTHER'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_SPATIAL_EMPERICAL_BAYES'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_SPATIAL_MEDIAN_RATE'))
        self.Bind(wx.EVT_MENU, self.OnSmoothRate, id=xrc.XRCID('ID_OPEN_RATES_DISK_SMOOTHER'))
       
        
        self.Bind(wx.EVT_MENU, self.OnLocalGMap, id=xrc.XRCID('IDM_LOCAL_G'))
        self.Bind(wx.EVT_MENU, self.OnDynamicLocalG, id=xrc.XRCID('IDM_DYNAMIC_LOCAL_G'))
        
        self.Bind(wx.EVT_MENU, self.OnLISAMap, id=xrc.XRCID('IDM_UNI_LISA'))
        self.Bind(wx.EVT_MENU, self.OnTrendGraphPlot, id=xrc.XRCID('IDM_TREND_GRAPH'))
        self.Bind(wx.EVT_MENU, self.OnDynamicTrendGraphPlot, id=xrc.XRCID('IDM_DYNAMIC_TREND_GRAPH'))
        self.Bind(wx.EVT_MENU, self.OnDensityMap, id=xrc.XRCID('IDM_DENSITY_MAP'))
        self.Bind(wx.EVT_MENU, self.OnTimeDensityMap, id=xrc.XRCID('IDM_TIME_DENSITY_MAP'))
        self.Bind(wx.EVT_MENU, self.OnDynamicDensityMap, id=xrc.XRCID('IDM_DYNAMIC_DENSITY_MAP'))
        self.Bind(wx.EVT_MENU, self.OnDynamicLISAMap, id=xrc.XRCID('IDM_DYNAMIC_LISAMAP'))
        #self.Bind(wx.EVT_MENU, self.OnLISAMarkovMap, id=xrc.XRCID('IDM_MARKOV_LISAMAP'))
        self.Bind(wx.EVT_MENU, self.OnLISASpaceTimeMap, id=xrc.XRCID('IDM_LISA_SPACETIME_MAP'))
        self.Bind(wx.EVT_MENU, self.OnGiSpaceTimeMap, id=xrc.XRCID('IDM_GI_SPACETIME_MAP'))
        #self.Bind(wx.EVT_MENU, self.On3DGiSpaceTimeMap, id=xrc.XRCID('IDM_3D_GI_SPACETIME_MAP'))
        self.Bind(wx.EVT_MENU, self.OnCalendarMap, id=xrc.XRCID('IDM_CALENDAR_MAP'))
        self.Bind(wx.EVT_MENU, self.OnDynamicCalendarMap, id=xrc.XRCID('IDM_DYNAMIC_CALENDAR_MAP'))
        self.Bind(wx.EVT_MENU, self.OnAbout, id=xrc.XRCID('wxID_ABOUT'))
        
        self.Bind(wx.EVT_TOOL, self.OnOpenSHPFile, id=xrc.XRCID('ID_OPEN_SHAPE_FILE'))
        self.Bind(wx.EVT_TOOL, self.OnCloseAll, id=xrc.XRCID('ID_CLOSE_ALL'))
        self.Bind(wx.EVT_TOOL, self.OnOpenDBFFile, id=xrc.XRCID('IDM_TABLE'))
        self.Bind(wx.EVT_TOOL, self.OnCreateWeight, id=xrc.XRCID('ID_TOOLS_WEIGHTS_CREATE'))
        self.Bind(wx.EVT_TOOL, self.OnWeightHistogram, id=xrc.XRCID('ID_TOOLS_WEIGHTS_CHAR'))
        self.Bind(wx.EVT_TOOL, self.OnClassifyMapClick, id=xrc.XRCID('ID_MAP_CHOICES'))
        #self.Bind(wx.EVT_TOOL, self.OnNewMapWindow, id=xrc.XRCID('ID_NEW_MAP_WINDOW'))
        self.Bind(wx.EVT_TOOL, self.OnMapMovie, id=xrc.XRCID('ID_MAPANALYSIS_MAPMOVIE'))
        self.Bind(wx.EVT_TOOL, self.OnDensityMapClick, id=xrc.XRCID('ID_DENSITY_MAP'))
        self.Bind(wx.EVT_TOOL, self.OnTrendGraphClick, id=xrc.XRCID('ID_TREND_GRAPH'))
        self.Bind(wx.EVT_TOOL, self.OnBoxPlot, id=xrc.XRCID('IDM_BOX'))
        self.Bind(wx.EVT_TOOL, self.OnHistogram, id=xrc.XRCID('IDM_HIST'))
        self.Bind(wx.EVT_TOOL, self.OnScatterPlot, id=xrc.XRCID('IDM_SCATTERPLOT'))
        self.Bind(wx.EVT_TOOL, self.OnLISAMap, id=xrc.XRCID('IDM_UNI_LISA'))
        self.Bind(wx.EVT_TOOL, self.OnCalendarMapClick, id=xrc.XRCID('ID_CALENDAR_MAP'))
        self.Bind(wx.EVT_TOOL, self.OnDynamicLISAClick, id=xrc.XRCID('ID_UNI_DYNAMIC_LISA'))
        self.Bind(wx.EVT_MENU, self.OnDynamicLocalGClick, id=xrc.XRCID('ID_UNI_DYNAMIC_LOCAL_G'))
        
        self.toolbar_flag = False
        self.ToggleToolbar(self.toolbar_flag)
        
    def OnAbout(self, event):
        self.ShowMsgBox("CAST v0.99 (alpha) release of Feb 20 2013.",
                        mtype='CAST information',
                        micon=wx.ICON_INFORMATION)
       
    def OnPolysFromGrid(self, event):
        dlg = CreateGridDlg(self)
        dlg.Show()
        
    def OnExit(self, event):
        dlg = wx.MessageDialog(
            self,
            "Do you really want to exit CAST?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            #sys.exit()
        
    def GetSHP(self,name):
        """
        Get SHP instance by layer name
        """
        for shp in self.shapefiles:
            if shp.name == name:
                return shp
        
    def _create_menu_dict(self):
        stack = []
        menu_dict = {}
        stack.append(self.menubar)
        
        while len(stack) > 0:
            item = stack.pop()
            
            if isinstance(item, wx.MenuBar):
                menus = item.GetMenus()
                for menu, name in menus:
                    stack.append(menu)
                    menu_dict[name] = menu
                    
            elif isinstance(item, wx.Menu):
                m_items = item.GetMenuItems()
                for m_item in m_items:
                    stack.append(m_item)
                    
            elif isinstance(item, wx.MenuItem):
                label = item.GetItemLabel()
                sub_menu = item.GetSubMenu()
                if sub_menu:
                    menu_dict[label] = sub_menu
                    stack.append(sub_menu)
    
        return menu_dict
            
    def LoadPlugins(self):
        from yapsy.PluginManager import PluginManager
        # Load the plugins from the plugin directory.
        manager = PluginManager(
            categories_filter={
                "MapPlugin": IMapPlugin,
                "PlotPlugin": IPlotPlugin,
                "TablePlugin": ITablePlugin
                },
            plugin_info_ext="stars-plugin"
        )
        manager.setPluginPlaces(["plugins"])
        manager.collectPlugins()
    
        # Loop round the plugins 
        for plugin in manager.getAllPlugins():
            plugin_obj = plugin.plugin_object
            rtn_id, rtn_func = plugin_obj.add_toolbar_item(self.toolbar)
            if rtn_id and rtn_func:
                self.Bind(wx.EVT_TOOL, rtn_func, id=rtn_id)
            rtn_id, rtn_func = plugin_obj.add_menu_item(self.menu_dict)
            if rtn_id and rtn_func:
                self.Bind(wx.EVT_MENU, rtn_func, id=rtn_id)
        
    def ToggleToolbar(self, flag):
        def set_toolbar_icon(id,flag, icons):
            icon = StarsArtProvider.GetBitmap(icons[0]) if flag else StarsArtProvider.GetBitmap(icons[1])
            self.toolbar.SetToolNormalBitmap(id, icon)
            
        set_toolbar_icon(xrc.XRCID('ID_CLOSE_ALL'),flag,('ToolBar-close-folder','ToolBar-close-folder_disabled'))
        set_toolbar_icon(xrc.XRCID('IDM_TABLE'),flag,('ToolBarBitmaps_18','ToolBarBitmaps_18_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_TOOLS_WEIGHTS_CREATE'),flag,('ToolBarBitmaps_4','ToolBarBitmaps_4_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_TOOLS_WEIGHTS_CHAR'),flag,('ToolBarBitmaps_5','ToolBarBitmaps_5_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_NEW_MAP_WINDOW'),flag,('ToolBarBitmaps_9','ToolBarBitmaps_9_disabled'))
        set_toolbar_icon(xrc.XRCID('IDM_BOX'),flag,('ToolBarBitmaps_14','ToolBarBitmaps_14_disabled'))
        set_toolbar_icon(xrc.XRCID('IDM_HIST'),flag,('ToolBarBitmaps_12','ToolBarBitmaps_12_disabled'))
        set_toolbar_icon(xrc.XRCID('IDM_SCATTERPLOT'),flag,('ToolBarBitmaps_13','ToolBarBitmaps_13_disabled'))
        #set_toolbar_icon(xrc.XRCID('IDM_UNI_LISA'),flag,('ToolBarBitmaps_3','ToolBarBitmaps_3_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_CALENDAR_MAP'),flag,('ToolBar_calendar','ToolBar_calendar_disabled'))
        #set_toolbar_icon(xrc.XRCID('IDM_LISA_EBRATE'),flag,('ToolBarBitmaps_3','ToolBarBitmaps_3_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_UNI_DYNAMIC_LOCAL_G'),flag,('ToolBarBitmaps_37','ToolBarBitmaps_37_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_MAP_CHOICES'),flag,('ToolBar_classify','ToolBar_classify_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_DENSITY_MAP'),flag,('ToolBar_kde','ToolBar_kde_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_TREND_GRAPH'),flag,('ToolBar-trend_graph','ToolBar-trend_graph_disabled'))
        set_toolbar_icon(xrc.XRCID('ID_UNI_DYNAMIC_LISA'),flag,('ToolBarBitmaps_22','ToolBarBitmaps_22_disabled'))
        
    def ShowMsgBox(self,msg,mtype='Warning',micon=wx.ICON_WARNING):
        dlg = wx.MessageDialog(self, msg, mtype, wx.OK|micon)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnCloseAll(self, event):
        wnds = self.GetChildren()
        for wnd in wnds:
            if issubclass(wnd.__class__, stars.visualization.AbstractWidget.AbstractWidget) or\
               issubclass(wnd.__class__, stars.visualization.SpaceTimeQueryDialog):
                wnd.Close(True)
        
        for shapefile in self.shapefiles:
            #del shapefile
            shapefile.clean()
        self.shapefiles = []
        self.datafiles = []

        self.toolbar_flag = False
        self.ToggleToolbar(self.toolbar_flag)
    
    def OnTrendGraphClick(self,event):
        if self.toolbar_flag == False:
            return
        
        pos = stars.POPMENU_POS_TREND_GRAPH_WIN
        if 'Linux' in  stars.APP_PLATFORM:
            pos = stars.POPMENU_POS_TREND_GRAPH_LINUX
        elif os.name=='posix':
            pos = stars.POPMENU_POS_TREND_GRAPH_MAC

        tg_menu = self.menu_res.LoadMenu('ID_TREND_GRAPHS')
        self.PopupMenu(tg_menu, pos)
    
    def OnDensityMapClick(self,event):
        if self.toolbar_flag == False:
            return
        pos = stars.POPMENU_POS_DENSITY_MAP_WIN
        if 'Linux' in  stars.APP_PLATFORM:
            pos = stars.POPMENU_POS_DENSITY_MAP_LINUX
        elif os.name=='posix':
            pos = stars.POPMENU_POS_DENSITY_MAP_MAC

        dm_menu = self.menu_res.LoadMenu('ID_DENSITY_MAPS')
        self.PopupMenu(dm_menu, pos)

    def OnCalendarMapClick(self,event):
        if self.toolbar_flag == False:
            return
        
        pos = stars.POPMENU_POS_CALENDAR_MAP_WIN
        if 'Linux' in  stars.APP_PLATFORM:
            pos = stars.POPMENU_POS_CALENDAR_MAP_LINUX
        elif os.name=='posix':
            pos = stars.POPMENU_POS_CALENDAR_MAP_MAC

        dm_menu = self.menu_res.LoadMenu('ID_CALENDAR_MAPS')
        self.PopupMenu(dm_menu, pos)
        
    def OnClassifyMapClick(self,event):
        if self.toolbar_flag == False:
            return
        
        pos = stars.POPMENU_POS_CLASSIFY_MAP_WIN
        if os.name=='posix':
            pos = stars.POPMENU_POS_CLASSIFY_MAP_MAC
        cm_menu = self.menu_res.LoadMenu('ID_MAP_CHOICES')
        self.PopupMenu(cm_menu, pos)
        
    def OnDynamicLISAClick(self,event):
        if self.toolbar_flag == False:
            return
        
        pos = stars.POPMENU_POS_DYN_LISA_MAP_WIN
        if 'Linux' in  stars.APP_PLATFORM:
            pos = stars.POPMENU_POS_DYN_LISA_MAP_LINUX
        elif os.name=='posix':
            pos = stars.POPMENU_POS_DYN_LISA_MAP_MAC

        dl_menu = self.menu_res.LoadMenu('ID_MENU_LISA')
        self.PopupMenu(dl_menu, pos)
        
    def OnDynamicLocalGClick(self,event):
        if self.toolbar_flag == False:
            return
        
        pos = stars.POPMENU_POS_DYN_LOCAL_G_MAP_WIN
        if 'Linux' in  stars.APP_PLATFORM:
            pos = stars.POPMENU_POS_DYN_LISA_MAP_LINUX
        elif os.name=='posix':
            pos = stars.POPMENU_POS_DYN_LISA_MAP_MAC

        dl_menu = self.menu_res.LoadMenu('ID_MENU_LOCAL_G')
        self.PopupMenu(dl_menu, pos)
        
    def OnCalendarMap(self, event):
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('Sorry, no point shapefile is available')
            return
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a shapefile:', 'Calendar Map', shp_list,wx.CHOICEDLG_STYLE)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = pts_shp_list[idx]   
            var_list = shp.dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select a date field:","Calendar Map", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() == wx.ID_OK:
                field_name = var_dlg.GetStringSelection()
                calender_map = MapWidget(
                    self, [shp], CalendarMap, 
                    date_field=field_name,
                    title="Calendar map",
                    size=stars.MAP_SIZE_CALENDAR
                    )
                calender_map.Show()
            var_dlg.Destroy()
        dlg.Destroy()
        
    def OnDynamicCalendarMap(self, event):
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('Sorry, no point shape file is available')
            return
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a shape file:', 'Dynamic Calendar Map', shp_list,wx.CHOICEDLG_STYLE)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = pts_shp_list[idx]   
            var_list = shp.dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select the date column","Dynamic Calendar Map", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() == wx.ID_OK:
                field_name = var_dlg.GetStringSelection()
                dynamic_calender_map = DynamicMapWidget(
                    self, [shp], DynamicCalendarMap, 
                    date_field=field_name,
                    title="Dynamic Calendar map",
                    size=stars.MAP_SIZE_CALENDAR)
                dynamic_calender_map.Show()
            var_dlg.Destroy()
        dlg.Destroy()
        
    def OnMapMovie(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file", 
            wildcard="Animate file (*.gif)|*.gif|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR)
        dlg.CenterOnScreen()
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        movie_widget = MovieWidget(self, path)
        movie_widget.Show()
    
    def OnBoxPlot(self, event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        dbf_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
                self, 'Select a dbf file:', 'DBF table view', dbf_list,wx.CHOICEDLG_STYLE)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = self.shapefiles[idx]
            dbf = shp.dbf
            var_list = dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select variable column:","Box Plot", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() == wx.ID_OK:
                field_name = var_dlg.GetStringSelection()
                data = {field_name:dbf.by_col(field_name)}
                box_widget = PlotWidget(
                    self,shp,data, BoxPlot, 
                    title="Box Plot (%s)" % shp.name,
                    size=stars.PLOT_SIZE_BOX)
                box_widget.Show()
            var_dlg.Destroy()
        dlg.Destroy()
    
    def OnHistogram(self, event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        dbf_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
                self, 'Select a dbf file:', 'DBF table view', dbf_list,wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = self.shapefiles[idx]
            dbf = shp.dbf
            var_list = dbf.header
            var_dlg = wx.SingleChoiceDialog(self, "Select variable column:","Histogram Plot", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() == wx.ID_OK:
                field_name = var_dlg.GetStringSelection()
                data = dict([(id,val) for id,val in enumerate(dbf.by_col(field_name))])
                hist_widget = PlotWidget(
                    self,
                    shp,
                    {field_name:data}, 
                    Histogram, 
                    title="Histogram (%s - %s)" % (shp.name,field_name),
                    size=stars.PLOT_SIZE_HISTOGRAM)
                hist_widget.Show()
            var_dlg.Destroy()
        dlg.Destroy()
        
    def OnNewMapWindow(self, event):
        self.OnOpenSHPFile(event)
        
    def OnOpenSHPFile(self,event):
        dlg = wx.FileDialog(
            self, message="Choose a file", 
            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
            style=wx.OPEN| wx.MULTIPLE | wx.CHANGE_DIR)
        if dlg.ShowModal() != wx.ID_OK:
            return
        paths = dlg.GetPaths()
        shapefiles= []
        try:
            progress_dlg = wx.ProgressDialog(
                "Progress",
                "Loading maps (shp,dbf) ...                      ",
                maximum = len(paths)+1,
                parent=self,
                style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
            progress_dlg.CenterOnScreen()
            for i,pth in enumerate(paths):
                progress_dlg.Update(i+1)
                shp_name = os.path.splitext(os.path.basename(pth))[0]
                # check existence
                b_shp_exist = False
                for shp in self.shapefiles:
                    if shp.name == shp_name:
                        b_shp_exist = True
                        shapefiles.append(shp)
                        break
                if b_shp_exist == False:
                    shapefile = CShapeFileObject(pth)
                    shapefiles.append(shapefile)
                    self.shapefiles.append(shapefile)
            progress_dlg.Update(len(paths) + 1)
            shape_widget = MapWidget(self, shapefiles, ShapeMap)
            shape_widget.Show()
           
            self.toolbar_flag = True
            self.ToggleToolbar(self.toolbar_flag)
            
        except Exception as err:
            progress_dlg.Destroy()
            self.ShowMsgBox("Open shapefile (%s) error. Please specify a valid shapefile (.shp)" %pth)
            
    def OnOpenDBFFile(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        dbf_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
                self, 'Select a dbf file:', 'DBF table view', dbf_list,wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            #dbf = self.shapefiles[idx].dbf
            shapeFileObject = self.shapefiles[idx]
            name = shapeFileObject.name
            #dbf_widget = DataWidget(self,dbf,name)
            dbf_widget = DataWidget(self, shapeFileObject, name)
            dbf_widget.Show()
        dlg.Destroy()

    def OnClassifyMap(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        title = ''
        map_type = None
        if event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_QUANTILE'):
            title = 'Quantile Map'
            map_type = stars.MAP_CLASSIFY_QUANTILES
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_PERCENTILE'):
            title = 'Percentile Map'
            map_type = stars.MAP_CLASSIFY_PERCENTILES
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_BOXPLOT'):
            title = 'Box Map'
            map_type = stars.MAP_CLASSIFY_BOX_PLOT
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_CHOROPLETH_STDDEV'):
            title = 'Std dev Map'
            map_type = stars.MAP_CLASSIFY_STD_MEAN
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_UNIQUE_VALUES'):
            title = 'Unique Values Map'
            map_type = stars.MAP_CLASSIFY_UNIQUE_VALUES
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_NATURAL_BREAKS'):
            title = 'Natural Breaks Map'
            map_type = stars.MAP_CLASSIFY_NATURAL_BREAK
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_MAXIMUM_BREAKS'):
            title = 'Maximum Breaks Map'
            map_type = stars.MAP_CLASSIFY_MAXIMUM_BREAK
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_EQUAL_INTERVALS'):
            title = 'Equal Interval Map'
            map_type = stars.MAP_CLASSIFY_EQUAL_INTERVAL
        elif event.Id == xrc.XRCID('ID_OPEN_MAPANALYSIS_JENKS_CASPALL'):
            title = 'Jenks Caspall Map'
            map_type = stars.MAP_CLASSIFY_JENKS_CASPALL
        shp_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a shape file:', title, shp_list, wx.CHOICEDLG_STYLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = self.shapefiles[idx]   
            classify_widget= MapWidget(
                self,[shp],ClassifyMap,
                map_type=map_type,
                title=title)
            classify_widget.Show()
        dlg.Destroy() 
        
    def _select_layer(self):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return None
        shp_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(self, 'Select a shape file:', 'Spatial smoothing', shp_list, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = self.shapefiles[idx]   
        dlg.Destroy() 
        return shp
    
    def _get_map_type(self, title):
        if title == 'Quantile Map':
            map_type = stars.MAP_CLASSIFY_QUANTILES
        elif title == 'Percentile Map':
            map_type = stars.MAP_CLASSIFY_PERCENTILES
        elif title == 'Box Map':
            map_type = stars.MAP_CLASSIFY_BOX_PLOT
        elif title == 'Std dev Map':
            map_type = stars.MAP_CLASSIFY_STD_MEAN
        elif title == 'Unique Values Map':
            map_type = stars.MAP_CLASSIFY_UNIQUE_VALUES
        elif title == 'Natural Breaks Map':
            map_type = stars.MAP_CLASSIFY_NATURAL_BREAK
        elif title == 'Maximum Breaks Map':
            map_type = stars.MAP_CLASSIFY_MAXIMUM_BREAK
        elif title == 'Equal Interval Map':
            map_type = stars.MAP_CLASSIFY_EQUAL_INTERVAL
        elif title == 'Jenks Caspall Map':
            map_type = stars.MAP_CLASSIFY_JENKS_CASPALL
        return map_type
    
    def _get_weights(self):
        w = None
        weight_dlg = SelectWeightDlg(self, self.dialog_res)
        if weight_dlg.ShowModal() == wx.ID_OK:
            weight_path = weight_dlg.GetWeightPath()
            weight_dlg.Destroy()
            if weight_path and len(weight_path) >0:
                w = pysal.open(weight_path,'r').read()
                return w
        else:
            weight_dlg.Destroy()
        return None 
        
    def OnSmoothRate(self,event):
        try:
            layer = self._select_layer()
            if layer == None:
                return
            classify_map_list = ['Quantile Map','Percentile Map','Box Map','Std dev Map',
                                 'Unique Values Map', 'Natural Breaks Map', 'Equal Interval Map',
                                 'Jenks Caspall Map']
            
            dlg =  self.dialog_res.LoadDialog(self, 'IDD_RATE_SMOOTHER')
            event_lst = xrc.XRCCTRL(dlg, 'IDC_LIST_VARIABLE1')
            base_lst = xrc.XRCCTRL(dlg,'IDC_LIST_VARIABLE2')
            map_type_cmb = xrc.XRCCTRL(dlg,'IDC_COMBO_THEMATIC')
            event_lst.AppendItems(layer.dbf.header)
            base_lst.AppendItems(layer.dbf.header)
            map_type_cmb.AppendItems(classify_map_list)
            
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            
            event_var_name = layer.dbf.header[event_lst.GetSelection()]
            base_var_name = layer.dbf.header[base_lst.GetSelection()]
            map_type_id = classify_map_list[map_type_cmb.GetSelection()]
            dlg.Destroy()
            
            map_type = self._get_map_type(map_type_id)
            
            field_name = '%s over %s' % (event_var_name, base_var_name)
          
            event_var = np.array(layer.dbf.by_col(event_var_name))
            base_var = np.array(layer.dbf.by_col(base_var_name))
            data = []
    
            if event.Id == xrc.XRCID('ID_OPEN_RATES_SMOOTH_RAWRATE'):
                title = '%s: Raw Rate ' % map_type_id
                # data = event_var / base_var
                n = len(event_var)
                for i in range(n):
                    if base_var[i] == 0:
                        data.append(0)
                    else:
                        data.append(event_var[i] / float(base_var[i]))
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_SMOOTH_EXCESSRISK'):
                title = '%s: Excess Risk' % map_type_id
                data = pysal.esda.smoothing.Excess_Risk(event_var, base_var)
                data = data.r
                
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_EMPERICAL_BAYES_SMOOTHER'):
                title = '%s: Emperical Bayes ' % map_type_id
                data = pysal.esda.smoothing.Empirical_Bayes(event_var, base_var)
                data = data.r
                
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_SPATIAL_RATE_SMOOTHER'):
                title = '%s: Spatial Rate ' % map_type_id
                w = self._get_weights()
                if w == None:
                    return
                data = pysal.esda.smoothing.Spatial_Rate(event_var, base_var,w)
                data = data.r
                
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_SPATIAL_EMPERICAL_BAYES'):
                title = '%s: Spatial Emperical Bayes' % map_type_id
                w = self._get_weights()
                if w == None:
                    return
                data = pysal.esda.smoothing.Spatial_Empirical_Bayes(event_var, base_var, w)
                data = data.r
            
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_SPATIAL_MEDIAN_RATE'):
                title = '%s: Spatial Median Rate' % map_type_id
                w = self._get_weights()
                if w == None:
                    return
                data = pysal.esda.smoothing.Spatial_Median_Rate(event_var, base_var, w)
                data = data.r
                
            elif event.Id == xrc.XRCID('ID_OPEN_RATES_DISK_SMOOTHER'):
                title = '%s: Disk Smoother ' % map_type_id
                w = self._get_weights()
                if w == None:
                    return
                data = pysal.esda.smoothing.Disk_Smoother(event_var, base_var, w)
                data = data.r
                
            classify_widget= MapWidget(
                self,[layer],ClassifyMap,
                map_type=map_type,
                data = data,
                field_name = field_name,
                title=title
            )
            classify_widget.Show()
        except:
            self.ShowMsgBox('Failed to create smoothed rates map. Please check the input variables or weights file.')
        
    def OnLISAMap(self, event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        plg_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POLYGON)
        if len(plg_shp_list) == 0:
            self.ShowMsgBox('No polygon shapefile is available')
            return
        shp_list = [shp.name for shp in plg_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a shape file:', 'LISA Map', shp_list,wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = plg_shp_list[idx] 
            if shp.dbf == None:
                self.ShowMsgBox('No dbf file is available.')
                return
            lisaMap= MapWidget(self,[shp],LISAMap)
            lisaMap.Show()
        dlg.Destroy()
        
    def OnDynamicLISAMap(self,event):
        ShowDynamicLISAMap(self)
           
    def On3DGiSpaceTimeMap(self,event):
        ShowSpaceTimeClusterMap(self)
        
    def OnLISASpaceTimeMap(self,event):
        #ShowLISASpaceTimeMap(self)
        ShowSigTrendGraphLISA(self)
        
    def OnGiSpaceTimeMap(self,event):
        #ShowGiSpaceTimeMap(self)
        ShowSigTrendGraphLocalG(self)
        
    def OnDynamicLocalG(self,event):
        ShowDynamicLocalGMap(self)
        
    def OnLocalGMap(self, event):
        ShowLocalGMap(self)
        
    def OnLISAMarkovMap(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        shp_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
            self, 
            'Select a POINT or Polygon(with time field) shape file:', 
            'LISA Markov Map', 
            shp_list,
            wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = self.shapefiles[idx]
            background_shapes = FilterShapeList(self.shapefiles, stars.SHP_POLYGON)
            if shp.shape_type == stars.SHP_POINT:
                # create Markov LISA from points
                m_lisa_dlg = LISAMarkovQueryDialog(
                    self,"LISA Markov:" + shp.name,
                    shp, 
                    background_shps=background_shapes,
                    size=stars.DIALOG_SIZE_QUERY_MARKOV_LISA)
                m_lisa_dlg.Show()
            elif shp.shape_type == stars.SHP_POLYGON:
                # bring up a dialog and let user select 
                # the time field in POLYGON shape file
                dbf_field_list = shp.dbf.header 
                timedlg = wx.MultiChoiceDialog(
                    self, 'Select TIME fields to generate Markov LISA:', 
                    'DBF fields view', 
                    dbf_field_list)
                if timedlg.ShowModal() == wx.ID_OK:
                    selections = timedlg.GetSelections()
                    # compose lisa_data_dict
                    dbf = shp.dbf
                    lisa_data_dict = {}
                    count = 0
                    for idx in selections:
                        lisa_data_dict[count] = np.array(dbf.by_col(dbf.header[idx]))
                        count += 1 
                        
                    # select weight file
                    wdlg = wx.FileDialog(
                        self, message="Select a weights file",
                        wildcard="Weights file (*.gal,*.gwt)|*.gwt;*.gal|All files (*.*)|*.*",
                        style=wx.OPEN | wx.CHANGE_DIR)
                    if wdlg.ShowModal() == wx.ID_OK:
                        # todo: select filter
                        weight_path = wdlg.GetPath()
                        # directly show Markov LISA Map
                        markov_lisa_widget= DynamicMapWidget(
                            self, 
                            [shp], 
                            LISAMarkovMap,
                            weight = weight_path,
                            query_data = lisa_data_dict,
                            size =stars.MAP_SIZE_MARKOV_LISA,
                            start=1,
                            end=count-1,
                            step_by='',
                            step=1,
                            labels=range(1,17))
                        markov_lisa_widget.Show()
                    wdlg.Destroy()
                timedlg.Destroy()
            else:
                self.ShowMsgBox("File type error. Should be a POINT or POLYGON shape file.")
                dlg.Destroy()
                return
        dlg.Destroy() 
        
    def OnDensityMap(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('Sorry, no point shapefile is available')
            return
        
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a POINT shapefile:', 'Density Map', shp_list,wx.CHOICEDLG_STYLE
            )
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            pts_shapefile = pts_shp_list[idx]
            kde = KDEConfigDialog(self,pts_shapefile)
            kde.CenterOnScreen()
            if kde.ShowModal() == wx.ID_OK:            
                try:
                    cell_size = float(kde.textbox_cellsize.GetValue())
                    bandwidth = float(kde.textbox_bandwidthh.GetValue())
                    opaque = float(kde.textbox_opaque.GetValue())
                    kernel = kde.cmbox_kernel.GetValue()
                    color_band = kde.color_band
                    densityMap_data = [pts_shapefile]
                    background_layer = None
                    densitymap_widget = MapWidget(
                        self,
                        densityMap_data,
                        DensityMap, 
                        background=background_layer,
                        cell_size=cell_size,
                        bandwidth=bandwidth,
                        kernel=kernel,
                        opaque=opaque,
                        color_band=color_band
                        )
                    densitymap_widget.Show()
                except:
                    self.ShowMsgBox('Please input valid KDE parameters.')
            kde.Destroy()
        dlg.Destroy()
        
    def OnDynamicDensityMap(self, event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('No point shapefile is available')
            return
        
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a POINT shape file:', 
            'Dynamic Density Map', shp_list, wx.CHOICEDLG_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            pts_shp = pts_shp_list[idx]
            trend_dlg=DynamicDensityMapQueryDialog(
                self,"Dynamic Density Map:" + pts_shp.name,
                pts_shp, background_shps=self.shapefiles, 
                size=stars.DIALOG_SIZE_QUERY_DYNAMIC_DENSITY
            )
            trend_dlg.Show()
        dlg.Destroy()
    
    def OnTimeDensityMap(self, event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('No point shapefile is available')
            return
        
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
                self, 'Select a POINT shape file:', 
                'Time Density Map', shp_list,wx.CHOICEDLG_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            pts_shp = pts_shp_list[idx]
            trend_dlg=DensityMapQueryDialog(
                self,
                "Time Density Map:" + pts_shp.name,
                pts_shp, 
                background_shps=self.shapefiles,
                size=stars.DIALOG_SIZE_QUERY_TIME_DENSITY
            )
            self.ShowMsgBox('For the Time Density Map, the "step by" option is NOT available.',
                            'Note',
                            wx.ICON_INFORMATION)
            trend_dlg.Show()
        dlg.Destroy()
    
    def OnTrendGraphPlot(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        if len(pts_shp_list) == 0:
            self.ShowMsgBox('No point shapefile is available')
            return
        
        shp_list = [shp.name for shp in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
                self, 'Select a POINT shapefile:', 
                'Trend Graph', shp_list,wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            pts_shp = pts_shp_list[idx]
            if pts_shp.shape_type != stars.SHP_POINT:
                self.ShowMsgBox("File type error. Should be a POINT shapefile.")
                dlg.Destroy()
                return
            trend_dlg=TrendGraphQueryDialog(
                self,"Trend Graph:" + pts_shp.name,
                pts_shp, 
                background_shps=self.shapefiles
            )
            trend_dlg.Show()
        dlg.Destroy()
        
    def OnDynamicTrendGraphPlot(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        
        pts_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POINT)
        shp_options = [i.name for i in pts_shp_list]
        dlg = wx.SingleChoiceDialog(
            self, 'Select a POINT shape file:', 
            'Dynamic Trend Graph', 
            shp_options,wx.CHOICEDLG_STYLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            pts_shp = pts_shp_list[idx]
            if pts_shp.shape_type != stars.SHP_POINT:
                self.ShowMsgBox("File type error. Should be a POINT shapefile.")
                dlg.Destroy()
                return
            d_trend_dlg=DynamicTrendMapQueryDialog(
                self,"Dynamic Trend Graph:" + pts_shp.name,
                pts_shp, 
                background_shps=self.shapefiles,
                size=stars.DIALOG_SIZE_QUERY_TREND_MAP
            )
            d_trend_dlg.Show()
        dlg.Destroy()
    
    def OnScatterPlot(self,event):
        if not self.shapefiles or len(self.shapefiles) < 1:
            return
        dbf_list = [shp.name for shp in self.shapefiles]
        dlg = wx.SingleChoiceDialog(
            self, 
            'Select a dbf file:', 
            'Scatter Plot', 
            dbf_list,
            wx.CHOICEDLG_STYLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            try:
                idx = dlg.GetSelection()
                shp = self.shapefiles[idx]
                dbf_name = shp.name
                
                var_list = shp.dbf.header
                var_dlg = VariableSelDialog(self,var_list,bDisable2nd=False,title="Scatter Plot")
                var_dlg.CenterOnScreen()
                if var_dlg.ShowModal() == wx.ID_OK:
                    if var_dlg.lb1.Select > -1 and var_dlg. lb2.Select > -2:
                        var1 = var_dlg.lb1.GetString(var_dlg.lb1.Selection)
                        var2 = var_dlg.lb2.GetString(var_dlg.lb2.Selection)
                        data = {var1:shp.dbf.by_col(var1), var2:shp.dbf.by_col(var2)}
                        scatter_widget = PlotWidget(self,shp,data, Scatter,title="Scatter Plot",size=(750,750))
                        scatter_widget.Show()
                var_dlg.Destroy()
            except Exception as err:
                self.ShowMsgBox("""Scatter plot could not be created. 
                
Details: """ + str(err.message))
        dlg.Destroy() 
        
    def OnCreateWeight(self, event):
        if self.toolbar_flag == False:
            return
        
        dlg = CreatingWeightDlg(self, self.dialog_res)
        dlg.Show()
        
    def OnOpenWeightFile(self, event):
        if self.toolbar_flag == False:
            return
        
        dlg = SelectWeightDlg(self, self.dialog_res)
        dlg.Show()
        
    def OnWeightHistogram(self, event):
        if self.toolbar_flag == False:
            return
        
        dlg = WeightCharDlg(self, self.dialog_res)
        dlg.Show()

   
def main():
    app = wx.App()
    main = Main(None)
    main.Show()
    app.MainLoop()
    
if __name__ == "__main__":
    main()
