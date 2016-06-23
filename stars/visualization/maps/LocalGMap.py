"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["LocalGMap",'ShowLocalGMap']

import math,os
import wx
import numpy as np
import pysal

import stars
from stars.visualization.MapWidget import MapWidget
from stars.visualization.dialogs import VariableSelDialog,SelectWeightDlg, choose_local_g_settings
from stars.visualization.utils import View2ScreenTransform, FilterShapeList
from ShapeMap import ShapeMap, ColorSchema 

    
class LocalGMap(ShapeMap):
    """
    Regular Local G map 
    """
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
       
        try:
            layer = layers[0]
            dbf = layer.dbf
            field_name = ''
            weight_path = ''
           
            # let user choose weight_path and field_name
            var_list = dbf.header
            #var_dlg = VariableSelDialog(self,var_list,bDisable2nd=True)
            var_dlg = wx.SingleChoiceDialog(self, "Select variable for LISA","LISA Map", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() != wx.ID_OK:
                var_dlg.Destroy()
                raise Exception('Local G maps cannot be created without ID variable.')
            field_name = var_dlg.GetStringSelection()
            var_dlg.Destroy()
            
            weight_dlg = SelectWeightDlg(self.main,self.main.dialog_res)
            if weight_dlg.ShowModal() != wx.ID_OK:
                weight_dlg.Destroy()
                raise Exception('Local G maps cannot be created without spatial weights.')
            
            weight_path = weight_dlg.GetWeightPath()
            weight_dlg.Destroy()
            if weight_path == None or len(weight_path) <=0:
                raise Exception('Please select a valid weights file.')
            self.weight = pysal.open(weight_path).read()
            
            
            b_gstar, b_binary = choose_local_g_settings(self)
            map_type = 'Gi*' if b_gstar else 'Gi'
            add_type = 'binary' if b_binary else 'row-standardized'
            self.parentFrame.SetTitle('Local G Map (%s,%s)-%s' % (map_type,add_type,layer.name))
            
            y = np.array(dbf.by_col(field_name))
            
            if b_binary == False:
                lg = pysal.esda.getisord.G_Local(y,self.weight,star=b_gstar)
            else:
                lg = pysal.esda.getisord.G_Local(y,self.weight,star=b_gstar,transform='B')
            self.gstar_p   = lg.p_sim
            self.gstar_z = lg.Zs
            
            self.siglevel = 0.05
            # 0 not significant, 6 significant change
            not_sig = list(np.where(self.gstar_p>self.siglevel)[0])
            sig     = set(np.where(self.gstar_p<=self.siglevel)[0])
            hotspots = list(sig.intersection(set(np.where(self.gstar_z>=0)[0])) )
            coldspots = list(sig.intersection(set(np.where(self.gstar_z<0)[0])) )
            id_groups = [not_sig,hotspots,coldspots]
            
            # default color schema for Gi*
            self.HH_color = stars.LISA_HH_COLOR
            self.LL_color = stars.LISA_LL_COLOR
            self.NOT_SIG_color = stars.LISA_NOT_SIG_COLOR
            #self.OBSOLETE_color = stars.LISA_OBSOLETE_COLOR
            color_group =[self.NOT_SIG_color,self.HH_color,self.LL_color]
            label_group = ["Not Significant","High-High","Low-Low"]
            self.color_schema_dict[layer.name] = ColorSchema(color_group,label_group)
            
            self.draw_layers[layer].set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
            self.draw_layers[layer].set_data_group(id_groups)
            self.draw_layers[layer].set_fill_color_group(color_group)
            
        except Exception as err:
            self.ShowMsgBox(str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return None
            
def ShowLocalGMap(self):
    # self is Main.py
    if not self.shapefiles or len(self.shapefiles) < 1:
        return
    plg_shp_list = FilterShapeList(self.shapefiles, stars.SHP_POLYGON)
    if len(plg_shp_list) == 0:
        self.ShowMsgBox('No polygon shapefile is available')
        return
    shp_list = [shp.name for shp in plg_shp_list]
    dlg = wx.SingleChoiceDialog(
        self, 'Select a shape file:', 'Local G Map', shp_list,wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.GetSelection()
        shp = plg_shp_list[idx] 
        if shp.dbf == None:
            self.ShowMsgBox('No dbf file is available.')
            return
        gMap= MapWidget(self,[shp],LocalGMap)
        gMap.Show()
    dlg.Destroy()
    