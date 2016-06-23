#-----------interfacs/functions ----
import os,platform
import wx
from Main import *
from rc.gradientimages import *
from rc.toolbarimages import getToolBar_exportImage, getToolBar_open_folderImage

APP_PLATFORM = platform.system()

#-----------global event--------
EVT_OBJS_SELECT = 9001
EVT_OBJS_UNSELECT = 9002

#-----------global custom setting-----
ST_QUERY_SETTINGS = dict()  # layername:date_field:xxx
                            # layername:date_field_regex:xxx
                            # layername:time_field:xxx
                            # layername:tod_field:[]
                            # layername:step:x
                            # layername:step_by:month
                            # layername:interval_start:xxx
                            # layername:interval_end:xxx
                            # layername:subset_field:xxx
                            # layername:subset_value:xxx
                            

#-----------global variables----
MAP_GRADIENT_COLOR_MAX = 0
MAP_GRADIENT_COLOR_MIN = 0xFFFFFFFF

SHP_POINT = 1001
SHP_POLYGON = 1002
SHP_LINE = 1003

MAP_OP_ZOOMIN = 2101
MAP_OP_ZOOMOUT  = 2102
MAP_OP_PAN = 2103
MAP_OP_SELECT = 2104
MAP_OP_BRUSHING = 2105
MAP_OP_PRE_BRUSHING = 2106

MAP_KEY_BRUSHING_POSIX = wx.WXK_COMMAND
MAP_KEY_BRUSHING_WIN = 308
MAP_KEY_APPEND_SELECTION = 306 #SHIFT KEY
MAP_KEY_DYNAMIC_SELECTION = 68 # "d" KEY

MAP_CLASSIFY_EQUAL_INTERVAL = 3001
MAP_CLASSIFY_PERCENTILES = 3002
MAP_CLASSIFY_BOX_PLOT = 3003
MAP_CLASSIFY_QUANTILES = 3004
MAP_CLASSIFY_STD_MEAN = 3005
MAP_CLASSIFY_MAXIMUM_BREAK = 3006
MAP_CLASSIFY_NATURAL_BREAK = 3007
MAP_CLASSIFY_FISHER_JENKS = 3008
MAP_CLASSIFY_JENKS_CASPALL = 3009
MAP_CLASSIFY_JENKS_CASPALL_SAMPLED = 3010
MAP_CLASSIFY_JENKS_CASPALL_FORCED = 3011
MAP_CLASSIFY_USER_DEFINED = 3012
MAP_CLASSIFY_MAX_P = 3013
MAP_CLASSIFY_UNIQUE_VALUES= 3014

SHAPE_LOCATOR_RTREE = 4001
SHAPE_LOCATOR_KDTREE = 4002
SHAPE_LOCATOR_QUADTREE = 4003
SHAPE_LOCATOR_INDEX = SHAPE_LOCATOR_KDTREE

#-----------color---------------
MAP_BRUSHING_COLOR = (255,255,0)
DEFAULT_MAP_EDGE_COLOR = wx.BLACK
LISA_MAP_EDGE_COLOR = wx.Colour(200,200,200)
MAP_COLOR_POLYGON_EDGE = wx.Colour(0,0,0)
MAP_COLOR_POLYGON_FILL = wx.Colour(0,104,139)
MAP_COLOR_POINT_EDGE = wx.Colour(0,0,0)
MAP_COLOR_POINT_FILL = wx.Colour(56,162,86)
MAP_COLOR_12_UNIQUE_FILL = (
    wx.Colour(141, 211, 199),wx.Colour(255, 255, 179),
    wx.Colour(190, 186, 218),wx.Colour(251, 128, 114),
    wx.Colour(128, 177, 211),wx.Colour(253, 180, 98),
    wx.Colour(179, 222, 105),wx.Colour(252, 205, 229),
    wx.Colour(217, 217, 217),wx.Colour(188, 128, 189),
    wx.Colour(204, 235, 197),wx.Colour(255, 237, 111))
MAP_COLOR_12_UNIQUE_OTHER = wx.Colour(240,240,240)

LISA_NOT_SIG_COLOR = wx.Colour(240,240,240)
LISA_HH_COLOR = wx.Colour(255,0,0)
LISA_LL_COLOR = wx.Colour(0,0,255)
LISA_LH_COLOR = wx.Colour(150,150,255)
LISA_HL_COLOR = wx.Colour(255,150,150)
LISA_OBSOLETE_COLOR = wx.Colour(140,140,140)

STRIP_VIEW_BG_COLOR = wx.Colour(200,200,200,255)
STRIP_VIEW_MAP_BG_COLOR = wx.Colour(255,255,255,255)
STRIP_VIEW_NAV_BAR_BG_COLOR = wx.Colour(100,100,100,100)

#-----------icon/image------------
"""
GRADIENT_IMG_DICT = {
    'classic':wx.Image('stars/rc/stars-gradient-classic.png', wx.BITMAP_TYPE_PNG),
    'fire'   :wx.Image('stars/rc/stars-gradient-fire.png',    wx.BITMAP_TYPE_PNG),
    'omg'    :wx.Image('stars/rc/stars-gradient-omg.png',     wx.BITMAP_TYPE_PNG),
    'pbj'    :wx.Image('stars/rc/stars-gradient-pbj.png',     wx.BITMAP_TYPE_PNG),
    'pgaitch':wx.Image('stars/rc/stars-gradient-pgaitch.png', wx.BITMAP_TYPE_PNG),
    'rdyibu' :wx.Image('stars/rc/stars-gradient-RdYIBu.png', wx.BITMAP_TYPE_PNG)}
OPEN_ICON_IMG = wx.Image('stars/rc/ToolBar-open-folder.png', wx.BITMAP_TYPE_PNG)
SAVE_ICON_IMG = wx.Image('stars/rc/ToolBar_export.png', wx.BITMAP_TYPE_PNG)
"""
GRADIENT_IMG_DICT = {
    'classic': getstars_gradient_classicImage(),
    'fire'   : getstars_gradient_fireImage(),
    'omg'    : getstars_gradient_omgImage(),
    'pbj'    : getstars_gradient_pbjImage(),
    'pgaitch': getstars_gradient_pgaitchImage(),
    'rdyibu' : getstars_gradient_RdYIBuImage()
}
OPEN_ICON_IMG = getToolBar_open_folderImage()
SAVE_ICON_IMG = getToolBar_exportImage()

#----------UI config------------
APP_SIZE_MAC = (480,22)
APP_SIZE_WIN = (480,72)
APP_SIZE_WIN_THEME = (480,82)
APP_SIZE_LINUX = (640,55)
APP_POS_MAC = (100,100)
APP_POS_WIN = (100,50)
APP_POS_LINUX = (100,50)
POPMENU_POS_TREND_GRAPH_MAC = (345,3)
POPMENU_POS_TREND_GRAPH_WIN = (310,22)
POPMENU_POS_TREND_GRAPH_LINUX = (345,22)
POPMENU_POS_DENSITY_MAP_MAC = (250,3)
POPMENU_POS_DENSITY_MAP_WIN = (235,22)
POPMENU_POS_DENSITY_MAP_LINUX = (275,22)
POPMENU_POS_CALENDAR_MAP_MAC = (244,3)
POPMENU_POS_CALENDAR_MAP_WIN = (214,22)
POPMENU_POS_CALENDAR_MAP_LINUX = (222,22)
POPMENU_POS_CLASSIFY_MAP_MAC = (205,3)
POPMENU_POS_CLASSIFY_MAP_WIN = (185,22)
POPMENU_POS_DYN_LISA_MAP_MAC = (300,3)
POPMENU_POS_DYN_LISA_MAP_WIN = (268,22)
POPMENU_POS_DYN_LISA_MAP_LINUX = (284,22)
POPMENU_POS_DYN_LOCAL_G_MAP_MAC = (322,3)
POPMENU_POS_DYN_LOCAL_G_MAP_WIN = (290,22)
POPMENU_POS_DYN_LOCAL_G_MAP_LINUX = (338,22)

MAP_SIZE_DYNAMIC_LISA = (800,650)
MAP_SIZE_MARKOV_LISA = (800,650)
MAP_SIZE_CALENDAR = (1280,860)
DIALOG_SIZE_QUERY_DYNAMIC_LISA = (360,510)
DIALOG_SIZE_QUERY_MARKOV_LISA = (360,420)
DIALOG_SIZE_QUERY_DYNAMIC_DENSITY= (364,630) if os.name == 'posix' else (364,660)
DIALOG_SIZE_QUERY_TIME_DENSITY= (364,630)
DIALOG_SIZE_QUERY_TREND_MAP=(364,420)
PLOT_SIZE_HISTOGRAM=(700,300)
PLOT_SIZE_BOX=(250,300)

HISTOGRAM_YEAR_FONT="wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial Black')"\
                   if os.name == 'posix' else "wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial Black')"
HISTOGRAM_MONTH_FONT="wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD)"\
                   if os.name == 'posix' else "wx.Font(8, wx.NORMAL, wx.NORMAL, wx.BOLD)"
HISTOGRAM_MONTH_NUMBER_FONT="wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)"\
                   if os.name == 'posix' else "wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL)"
HISTOGRAM_MONTH_VERTICAL_FONT="wx.Font(38, wx.BOLD, wx.NORMAL, wx.NORMAL,False,'Arial Black')"\
                   if os.name == 'posix' else "wx.Font(30, wx.BOLD, wx.NORMAL, wx.NORMAL,False,'Arial Black')"
HISTOGRAM_CALENDAR_NUMBER_FONT="wx.Font(12, wx.NORMAL, wx.NORMAL, wx.NORMAL)"\
                   if os.name == 'posix' else "wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL)"
HISTOGRAM_CALENDAR_FONT="wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL,False,'Arial Black')"\
                   if os.name == 'posix' else "wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL,False,'Arial Black')"

COLORBREWER_LEGEND_FONT="wx.Font(12, wx.NORMAL, wx.NORMAL, wx.NORMAL)"\
                   if os.name == 'posix' else "wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL)"

PLOT_TITLE_FONT_SIZE=14 if os.name=='posix' else 12
PLOT_X_AXIS_FONT_SIZE=10 if os.name=='posix' else 8
PLOT_Y_AXIS_FONT_SIZE=10 if os.name=='posix' else 8
PLOT_XY_LABEL_FONT_SIZE=12 if os.name=='posix' else 10

TRENDGRAPH_Y_AXIS_FONT_SIZE=10 if os.name=='posix' else 8

SCATTER_STATS_FONT_SIZE=11 if os.name=='posix' else 8

NAV_ARROW_FONT_SIZE = 8 if os.name=='posix' else 6
LISA_SPACE_LEGEND_FONT_SIZE = 8 if os.name=='posix' else 7
