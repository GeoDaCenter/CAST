"""
"""

__author__='Xun Li <xunli@asu.edu>'
__all__=["StarsArtProvider"]

import wx
from toolbarimages import *

class StarsArtProvider(wx.ArtProvider):
    def __init__(self):
        wx.ArtProvider.__init__(self)

    def CreateBitmap(self, artid, client, size):
        bmp = wx.NullBitmap
        if artid == "ToolBarBitmaps_2":
            bmp = getToolBarBitmaps_2Bitmap()
        elif artid == "ToolBarBitmaps_2_disabled":
            bmp = getToolBarBitmaps_2_disabledBitmap()
        elif artid == "ToolBarBitmaps_3":
            bmp = getToolBarBitmaps_3Bitmap()
        elif artid == "ToolBarBitmaps_3_disabled":
            bmp = getToolBarBitmaps_3_disabledBitmap()
        elif artid == "ToolBarBitmaps_4":
            bmp = getToolBarBitmaps_4Bitmap()
        elif artid == "ToolBarBitmaps_4_disabled":
            bmp = getToolBarBitmaps_4_disabledBitmap()
        elif artid == "ToolBarBitmaps_5":
            bmp = getToolBarBitmaps_5Bitmap()
        elif artid == "ToolBarBitmaps_5_disabled":
            bmp = getToolBarBitmaps_5_disabledBitmap()
        elif artid == "ToolBarBitmaps_6":
            bmp = getToolBarBitmaps_6Bitmap()
        elif artid == "ToolBarBitmaps_6_disabled":
            bmp = getToolBarBitmaps_6_disabledBitmap()
        elif artid == "ToolBarBitmaps_7":
            bmp = getToolBarBitmaps_7Bitmap()
        elif artid == "ToolBarBitmaps_7_disabled":
            bmp = getToolBarBitmaps_7_disabledBitmap()
        elif artid == "ToolBarBitmaps_8":
            bmp = getToolBarBitmaps_8Bitmap()
        elif artid == "ToolBarBitmaps_8_disabled":
            bmp = getToolBarBitmaps_8_disabledBitmap()
        elif artid == "ToolBarBitmaps_9":
            bmp = getToolBarBitmaps_9Bitmap()
        elif artid == "ToolBarBitmaps_9_disabled":
            bmp = getToolBarBitmaps_9_disabledBitmap()
        elif artid == "ToolBarBitmaps_10":
            bmp = getToolBarBitmaps_10Bitmap()
        elif artid == "ToolBarBitmaps_10_disabled":
            bmp = getToolBarBitmaps_10_disabledBitmap()
        elif artid == "ToolBarBitmaps_11":
            bmp = getToolBarBitmaps_11Bitmap()
        elif artid == "ToolBarBitmaps_11_disabled":
            bmp = getToolBarBitmaps_11_disabledBitmap()
        elif artid == "ToolBarBitmaps_12":
            bmp = getToolBarBitmaps_12Bitmap()
        elif artid == "ToolBarBitmaps_12_disabled":
            bmp = getToolBarBitmaps_12_disabledBitmap()
        elif artid == "ToolBarBitmaps_13":
            bmp = getToolBarBitmaps_13Bitmap()
        elif artid == "ToolBarBitmaps_13_disabled":
            bmp = getToolBarBitmaps_13_disabledBitmap()
        elif artid == "ToolBarBitmaps_14":
            bmp = getToolBarBitmaps_14Bitmap()
        elif artid == "ToolBarBitmaps_14_disabled":
            bmp = getToolBarBitmaps_14_disabledBitmap()
        elif artid == "ToolBarBitmaps_15":
            bmp = getToolBarBitmaps_15Bitmap()
        elif artid == "ToolBarBitmaps_15_disabled":
            bmp = getToolBarBitmaps_15_disabledBitmap()
        elif artid == "ToolBarBitmaps_16":
            bmp = getToolBarBitmaps_16Bitmap()
        elif artid == "ToolBarBitmaps_16_disabled":
            bmp = getToolBarBitmaps_16_disabledBitmap()
        elif artid == "ToolBarBitmaps_17":
            bmp = getToolBarBitmaps_17Bitmap()
        elif artid == "ToolBarBitmaps_17_disabled":
            bmp = getToolBarBitmaps_17_disabledBitmap()
        elif artid == "ToolBarBitmaps_18":
            bmp = getToolBarBitmaps_18Bitmap()
        elif artid == "ToolBarBitmaps_18_disabled":
            bmp = getToolBarBitmaps_18_disabledBitmap()
        elif artid == "ToolBarBitmaps_19":
            bmp = getToolBarBitmaps_19Bitmap()
        elif artid == "ToolBarBitmaps_19_disabled":
            bmp = getToolBarBitmaps_19_disabledBitmap()
        elif artid == "ToolBarBitmaps_20":
            bmp = getToolBarBitmaps_20Bitmap()
        elif artid == "ToolBarBitmaps_20_disabled":
            bmp = getToolBarBitmaps_20_disabledBitmap()
        elif artid == "ToolBarBitmaps_21":
            bmp = getToolBarBitmaps_21Bitmap()
        elif artid == "ToolBarBitmaps_21_disabled":
            bmp = getToolBarBitmaps_21_disabledBitmap()
        elif artid == "ToolBarBitmaps_22":
            bmp = getToolBarBitmaps_22Bitmap()
        elif artid == "ToolBarBitmaps_22_disabled":
            bmp = getToolBarBitmaps_22_disabledBitmap()
        elif artid == "ToolBarBitmaps_23":
            bmp = getToolBarBitmaps_23Bitmap()
        elif artid == "ToolBarBitmaps_23_disabled":
            bmp = getToolBarBitmaps_23_disabledBitmap()
        elif artid == "ToolBarBitmaps_24":
            bmp = getToolBarBitmaps_24Bitmap()
        elif artid == "ToolBarBitmaps_24_disabled":
            bmp = getToolBarBitmaps_24_disabledBitmap()
        elif artid == "ToolBarBitmaps_25":
            bmp = getToolBarBitmaps_25Bitmap()
        elif artid == "ToolBarBitmaps_25_disabled":
            bmp = getToolBarBitmaps_25_disabledBitmap()
        elif artid == "ToolBarBitmaps_26":
            bmp = getToolBarBitmaps_26Bitmap()
        elif artid == "ToolBarBitmaps_26_disabled":
            bmp = getToolBarBitmaps_26_disabledBitmap()
        elif artid == "ToolBarBitmaps_27":
            bmp = getToolBarBitmaps_27Bitmap()
        elif artid == "ToolBarBitmaps_27_disabled":
            bmp = getToolBarBitmaps_27_disabledBitmap()
        elif artid == "ToolBarBitmaps_28":
            bmp = getToolBarBitmaps_28Bitmap()
        elif artid == "ToolBarBitmaps_28_disabled":
            bmp = getToolBarBitmaps_28_disabledBitmap()
        elif artid == "ToolBarBitmaps_29":
            bmp = getToolBarBitmaps_29Bitmap()
        elif artid == "ToolBarBitmaps_29_disabled":
            bmp = getToolBarBitmaps_29_disabledBitmap()
        elif artid == "ToolBarBitmaps_30":
            bmp = getToolBarBitmaps_30Bitmap()
        elif artid == "ToolBarBitmaps_30_disabled":
            bmp = getToolBarBitmaps_30_disabledBitmap()
        elif artid == "ToolBarBitmaps_31":
            bmp = getToolBarBitmaps_31Bitmap()
        elif artid == "ToolBarBitmaps_31_disabled":
            bmp = getToolBarBitmaps_31_disabledBitmap()
        elif artid == "ToolBarBitmaps_32":
            bmp = getToolBarBitmaps_32Bitmap()
        elif artid == "ToolBarBitmaps_32_disabled":
            bmp = getToolBarBitmaps_32_disabledBitmap()
        elif artid == "ToolBarBitmaps_33":
            bmp = getToolBarBitmaps_33Bitmap()
        elif artid == "ToolBarBitmaps_33_disabled":
            bmp = getToolBarBitmaps_33_disabledBitmap()
        elif artid == "ToolBarBitmaps_34":
            bmp = getToolBarBitmaps_34Bitmap()
        elif artid == "ToolBarBitmaps_34_disabled":
            bmp = getToolBarBitmaps_34_disabledBitmap()
        elif artid == "ToolBarBitmaps_35":
            bmp = getToolBarBitmaps_35Bitmap()
        elif artid == "ToolBarBitmaps_35_disabled":
            bmp = getToolBarBitmaps_35_disabledBitmap()
        elif artid == "ToolBarBitmaps_36":
            bmp = getToolBarBitmaps_36Bitmap()
        elif artid == "ToolBarBitmaps_36_disabled":
            bmp = getToolBarBitmaps_36_disabledBitmap()
        elif artid == "ToolBarBitmaps_37":
            bmp = getToolBarBitmaps_37Bitmap()
        elif artid == "ToolBarBitmaps_37_disabled":
            bmp = getToolBarBitmaps_37_disabledBitmap()
        elif artid == "ToolBarBitmaps_38":
            bmp = getToolBarBitmaps_38Bitmap()
        elif artid == "ToolBarBitmaps_38_disabled":
            bmp = getToolBarBitmaps_38_disabledBitmap()
        elif artid == "ToolBarBitmaps_39":
            bmp = getToolBarBitmaps_39Bitmap()
        elif artid == "ToolBarBitmaps_39_disabled":
            bmp = getToolBarBitmaps_39_disabledBitmap()
        elif artid == "ToolBarBitmaps_40":
            bmp = getToolBarBitmaps_40Bitmap()
        elif artid == "ToolBarBitmaps_40_disabled":
            bmp = getToolBarBitmaps_40_disabledBitmap()
        elif artid == "ToolBarBitmaps_MapChoices":
            bmp = getToolBarBitmaps_MapChoicesBitmap()
        elif artid == "ToolBarBitmaps_MapChoices_disabled":
            bmp = getToolBarBitmaps_MapChoices_disabledBitmap()
        elif artid == "ToolBar-open-folder":
            bmp = getToolBar_open_folderBitmap()
        elif artid == "ToolBar-open-folder_disabled":
            bmp = getToolBar_open_folder_disabledBitmap()
        elif artid == "ToolBar-close-folder":
            bmp = getToolBar_close_folderBitmap()
        elif artid == "ToolBar-close-folder_disabled":
            bmp = getToolBar_close_folder_disabledBitmap()
        elif artid == "ToolBar_down_arrow":
            bmp = getToolBar_down_arrowBitmap()
        elif artid == "ToolBar_down_arrow_disabled":
            bmp = getToolBar_down_arrow_disabledBitmap()
        elif artid == "ToolBar_Dynamic_LISA":
            bmp = getToolBar_Dynamic_LISABitmap()
        elif artid == "ToolBar-trend_graph":
            bmp = getToolBar_trend_graphBitmap()
        elif artid == "ToolBar-trend_graph_disabled":
            bmp = getToolBar_trend_graph_disabledBitmap()
        elif artid == "ToolBar-weights_map":
            bmp = getToolBar_weights_mapBitmap()
        elif artid == "ToolBar_brush":
            bmp = getToolBar_brushBitmap()
        elif artid == "ToolBar_calendar":
            bmp = getToolBar_calendarBitmap()
        elif artid == "ToolBar_calendar_disabled":
            bmp = getToolBar_calendar_disabledBitmap()
        elif artid == "ToolBar_export":
            bmp = getToolBar_exportBitmap()
        elif artid == "ToolBar_extent":
            bmp = getToolBar_extentBitmap()
        elif artid == "ToolBar_hand":
            bmp = getToolBar_handBitmap()
        elif artid == "ToolBar_pause":
            bmp = getToolBar_pauseBitmap()
        elif artid == "ToolBar_play":
            bmp = getToolBar_playBitmap()
        elif artid == "ToolBar_refresh":
            bmp = getToolBar_refreshBitmap()
        elif artid == "ToolBar_select":
            bmp = getToolBar_selectBitmap()
        elif artid == "ToolBar_stop":
            bmp = getToolBar_stopBitmap()
        elif artid == "ToolBar_zoom":
            bmp = getToolBar_zoomBitmap()
        elif artid == "open-folder":
            bmp = getopen_folderBitmap()
        elif artid == "about-geoda-logo":
            bmp = getabout_geoda_logoBitmap()
        elif artid == "ToolBar_kde":
            bmp = getToolBar_density_mapBitmap()
        elif artid == "ToolBar_kde_disabled":
            bmp = getToolBar_density_map_disabledBitmap()
        elif artid == "ToolBar_classify":
            bmp = getToolBarBitmaps_MapChoices2Bitmap()
        elif artid == "ToolBar_classify_disabled":
            bmp = getToolBarBitmaps_MapChoices_disabledBitmap()
        elif artid == "ToolBar_spacetime":
            bmp = getToolBar_Dynamic_LISABitmap()
        return bmp


