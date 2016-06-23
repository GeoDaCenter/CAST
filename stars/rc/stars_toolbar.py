stars_toolbar = '''
<?xml version="1.0" encoding="ISO-8859-15"?>
<resource>
  <object class="wxToolBar" name="ToolBar">
    <object class="tool" name="ID_OPEN_SHAPE_FILE">
      <bitmap stock_id="ToolBar-open-folder"/>
      <bitmap2 stock_id="ToolBar-open-folder_disabled"/>
      <tooltip>Open Project</tooltip>
    </object>
    <object class="tool" name="ID_MAPANALYSIS_MAPMOVIE">
      <bitmap stock_id="ToolBarBitmaps_31"/>
      <bitmap2 stock_id="ToolBarBitmaps_31_disabled"/>
      <tooltip>Map Movie (cumulative selection)</tooltip>
    </object>
    <object class="tool" name="ID_CLOSE_ALL">
      <bitmap stock_id="ToolBar-close-folder"/>
      <bitmap2 stock_id="ToolBar-close-folder_disabled"/>
      <tooltip>Close All</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="IDM_TABLE">
      <bitmap stock_id="ToolBarBitmaps_18"/>
      <bitmap2 stock_id="ToolBarBitmaps_18_disabled"/>
      <tooltip>Open Table</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_TOOLS_WEIGHTS_CREATE">
      <bitmap stock_id="ToolBarBitmaps_4"/>
      <bitmap2 stock_id="ToolBarBitmaps_4_disabled"/>
      <tooltip>Create weights</tooltip>
    </object>
    <object class="tool" name="ID_TOOLS_WEIGHTS_CHAR">
      <bitmap stock_id="ToolBarBitmaps_5"/>
      <bitmap2 stock_id="ToolBarBitmaps_5_disabled"/>
      <tooltip>Weight neighbors histogram</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_MAP_CHOICES">
      <bitmap stock_id="ToolBar_classify"/>
      <bitmap2 stock_id="ToolBar_classify_disabled"/>
      <tooltip>Maps and Smoothing</tooltip>
    </object>
    <!--
    <object class="tool" name="ID_NEW_MAP_WINDOW">
      <bitmap stock_id="ToolBarBitmaps_9"/>
      <bitmap2 stock_id="ToolBarBitmaps_9_disabled"/>
      <tooltip>New Map Window</tooltip>
    </object>
    -->
    <object class="separator"/>
    <object class="tool" name="ID_CALENDAR_MAP">
      <bitmap stock_id="ToolBar_calendar"/>
      <bitmap2 stock_id="ToolBar_calendar_disabled"/>
      <tooltip>Calendar Map</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_DENSITY_MAP">
      <bitmap stock_id="ToolBar_kde"/>
      <bitmap2 stock_id="ToolBar_kde_disabled"/>
      <tooltip>Density Map</tooltip>
    </object>
    <object class="tool" name="ID_UNI_DYNAMIC_LISA">
      <bitmap stock_id="ToolBarBitmaps_22"/>
      <bitmap2 stock_id="ToolBarBitmaps_22_disabled"/>
      <tooltip>LISA</tooltip>
    </object>
    <margins>1,1</margins>
    <style>wxTB_FLAT|wxTB_NODIVIDER</style>
    <object class="tool" name="ID_UNI_DYNAMIC_LOCAL_G">
      <bitmap stock_id="ToolBarBitmaps_37"/>
      <bitmap2 stock_id="ToolBarBitmaps_37_disabled"/>
      <tooltip>Local G Statistics</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_TREND_GRAPH">
      <bitmap stock_id="ToolBar-trend_graph"/>
      <bitmap2 stock_id="ToolBar-trend_graph_disabled"/>
      <tooltip>Time</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="IDM_BOX">
      <bitmap stock_id="ToolBarBitmaps_14"/>
      <bitmap2 stock_id="ToolBarBitmaps_14_disabled"/>
      <tooltip>Box Plot</tooltip>
    </object>
    <object class="tool" name="IDM_HIST">
      <bitmap stock_id="ToolBarBitmaps_12"/>
      <bitmap2 stock_id="ToolBarBitmaps_12_disabled"/>
      <tooltip>Histogram</tooltip>
    </object>
    <object class="tool" name="IDM_SCATTERPLOT">
      <bitmap stock_id="ToolBarBitmaps_13"/>
      <bitmap2 stock_id="ToolBarBitmaps_13_disabled"/>
      <tooltip>Scatter Plot</tooltip>
    </object>
    <object class="separator"/>
  </object>
  <object class="wxToolBar" name="ToolBar2">
    <object class="tool" name="ID_CD_ROM">
      <bitmap stock_id="wxART_CDROM"/>
      <tooltip>CD ROM</tooltip>
    </object>
    <object class="tool" name="ID_FLOPPY">
      <bitmap stock_id="wxART_FLOPPY"/>
    </object>
    <bitmapsize>16,15</bitmapsize>
    <margins>2,2</margins>
    <style>wxTB_FLAT|wxTB_NODIVIDER</style>
    <object class="tool" name="ID_EXPORT_MEAN_CENTERS">
      <bitmap stock_id="ToolBarBitmaps_36"/>
      <bitmap2 stock_id="ToolBarBitmaps_36_disabled"/>
      <tooltip>Export Mean Centers</tooltip>
    </object>
    <object class="tool" name="ID_EXPORT_CENTROIDS">
      <bitmap stock_id="ToolBarBitmaps_2"/>
      <bitmap2 stock_id="ToolBarBitmaps_2_disabled"/>
      <tooltip>Export Centroids</tooltip>
    </object>
    <object class="tool" name="ID_TOOLS_WEIGHTS_OPEN">
      <bitmap stock_id="ToolBarBitmaps_3"/>
      <bitmap2 stock_id="ToolBarBitmaps_3_disabled"/>
      <tooltip>Select Weights</tooltip>
    </object>
    <object class="tool" name="ID_SHOW_CONVERTED_FEATURES">
      <bitmap stock_id="ToolBarBitmaps_6"/>
      <bitmap2 stock_id="ToolBarBitmaps_6_disabled"/>
      <tooltip>Show Converted Features</tooltip>
    </object>
    <object class="tool" name="ID_SET_DEFAULT_VARIABLE_SETTINGS">
      <bitmap stock_id="ToolBarBitmaps_10"/>
      <bitmap2 stock_id="ToolBarBitmaps_10_disabled"/>
      <tooltip>Default Variable Settings</tooltip>
    </object>
  </object>
  <object class="wxToolBar" name="ToolBar3">
    <object class="tool" name="ID_HELP">
      <bitmap stock_id="wxART_HELP_BOOK"/>
    </object>
    <bitmapsize>16,16</bitmapsize>
    <margins>2,2</margins>
    <style>wxTB_NODIVIDER</style>
  </object>
  <object class="wxToolBar" name="ToolBar_MAP">
    <bitmapsize>16,16</bitmapsize>
    <margins>1,1</margins>
    <object class="tool" name="ID_ADD_MAP_LAYER">
      <bitmap stock_id="ToolBarBitmaps_7"/>
      <tooltip>add layer</tooltip>
    </object>
    <object class="tool" name="ID_REMOVE_MAP_LAYER">
      <bitmap stock_id="ToolBarBitmaps_8"/>
      <tooltip>remove layer</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="IDM_TABLE">
      <bitmap stock_id="ToolBarBitmaps_18"/>
      <bitmap2 stock_id="ToolBarBitmaps_18_disabled"/>
      <tooltip>Open Table</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_SELECT_LAYER">
      <bitmap stock_id="ToolBar_select"/>
      <tooltip>select</tooltip>
    </object>
    <object class="tool" name="ID_PAN_LAYER">
      <bitmap stock_id="ToolBar_hand"/>
      <tooltip>pan</tooltip>
    </object>
    <object class="tool" name="ID_ZOOM_LAYER">
      <bitmap stock_id="ToolBar_zoom"/>
      <tooltip>zoom in</tooltip>
    </object>
    <object class="tool" name="ID_EXTENT_LAYER">
      <bitmap stock_id="ToolBar_extent"/>
      <tooltip>extent</tooltip>
    </object>
    <object class="tool" name="ID_REFRESH_LAYER">
      <bitmap stock_id="ToolBar_refresh"/>
      <tooltip>refresh</tooltip>
    </object>
    <object class="tool" name="ID_BRUSH_LAYER">
      <bitmap stock_id="ToolBar_brush"/>
      <tooltip>brushing</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_EXPORT_MAP">
      <bitmap stock_id="ToolBar_export"/>
      <tooltip>save image as</tooltip>
    </object>
  </object>
  <object class="wxToolBar" name="ToolBar_ANIMATE_MAP">
    <bitmapsize>16,16</bitmapsize>
    <margins>1,1</margins>
    <object class="tool" name="ID_ADD_MAP_LAYER">
      <bitmap stock_id="ToolBarBitmaps_7"/>
    </object>
    <object class="tool" name="ID_REMOVE_MAP_LAYER">
      <bitmap stock_id="ToolBarBitmaps_8"/>
    </object>
    <object class="separator"/>
    <object class="tool" name="IDM_TABLE">
      <bitmap stock_id="ToolBarBitmaps_18"/>
      <bitmap2 stock_id="ToolBarBitmaps_18_disabled"/>
      <tooltip>Open Table</tooltip>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_SELECT_LAYER">
      <bitmap stock_id="ToolBar_select"/>
      <tooltip>select</tooltip>
    </object>
    <object class="tool" name="ID_PAN_LAYER">
      <bitmap stock_id="ToolBar_hand"/>
      <tooltip>pan</tooltip>
    </object>
    <object class="tool" name="ID_ZOOM_LAYER">
      <bitmap stock_id="ToolBar_zoom"/>
    </object>
    <object class="tool" name="ID_EXTENT_LAYER">
      <bitmap stock_id="ToolBar_extent"/>
    </object>
    <object class="tool" name="ID_REFRESH_LAYER">
      <bitmap stock_id="ToolBar_refresh"/>
    </object>
    <object class="tool" name="ID_BRUSH_LAYER">
      <bitmap stock_id="ToolBar_brush"/>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_EXPORT_MAP">
      <bitmap stock_id="ToolBar_export"/>
    </object>
    <object class="separator"/>
    <object class="tool" name="ID_PLAY">
      <bitmap stock_id="ToolBar_play"/>
    </object>
    <object class="tool" name="ID_PAUSE">
      <bitmap stock_id="ToolBar_pause"/>
    </object>
    <object class="tool" name="ID_STOP">
      <bitmap stock_id="ToolBar_stop"/>
    </object>
    <object class="separator"/>
    <object class="wxStaticText" name="ID_ANIMATE_START_LABEL">
      <label>12/12/1900</label>
      <style>wxTRANSPARENT_WINDOW|wxALIGN_RIGHT</style>
    </object>
    <object class="wxSlider" name="ID_ANIMATE_SLIDER">
      <size>120,-1</size>
      <style>wxNO_BORDER|wxTRANSPARENT_WINDOW|wxSL_AUTOTICKS</style>
    </object>
    <object class="wxStaticText" name="ID_ANIMATE_END_LABEL">
      <label>12/12/1900</label>
      <style>wxALIGN_LEFT</style>
    </object>
    <object class="separator"/>
    <object class="wxStaticText" name="ID_ANIMATE_CURRENT_LABEL">
      <label>current: 00 (00-month period)</label>
    </object>
  </object>
</resource>
'''