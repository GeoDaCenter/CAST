"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["LISAMap"]

import math,os
import wx
import numpy as np
import pysal

import stars
from stars.visualization.dialogs import VariableSelDialog,SelectWeightDlg
from ShapeMap import ShapeMap, ColorSchema 

class LISAError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class LISAMap(ShapeMap):
    """
    Regular LISA map using local Moran tests
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
            var_dlg = wx.SingleChoiceDialog(self, "Select variable for LISA","LISA Map", var_list, wx.CHOICEDLG_STYLE)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() != wx.ID_OK:
                var_dlg.Destroy()
                raise Exception('LISA maps cannot be created without ID variable.')
            field_name = var_dlg.GetStringSelection()
            var_dlg.Destroy()
            
            weight_dlg = SelectWeightDlg(self.main,self.main.dialog_res)
            if weight_dlg.ShowModal() != wx.ID_OK:
                weight_dlg.Destroy()
                raise Exception('LISA maps cannot be created without spatial weights.')
            
            weight_path = weight_dlg.GetWeightPath()
            weight_dlg.Destroy()
            if weight_path == None or len(weight_path) <=0:
                raise Exception('Please select a valid weights file.')
            
            self.siglevel = 0.05
            self.parentFrame.SetTitle('LISA - %s(%s)'% (layer.name,field_name))
            self.draw_layers[layer].set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
            
            data = np.array(dbf.by_col(field_name))
            id_groups = self.process_LISA(self,data, weight_path)
            
            # default color schema
            color_group =[
                stars.LISA_NOT_SIG_COLOR, 
                stars.LISA_HH_COLOR,
                stars.LISA_LL_COLOR, 
                stars.LISA_LH_COLOR,
                stars.LISA_HL_COLOR, 
                stars.LISA_OBSOLETE_COLOR
                ]
            label_group = [
                "Not Significant",
                "High-High",
                "Low-Low",
                "Low-High",
                "High-Low",
                "Neighborless"
                ]
            self.color_schema_dict[layer.name] = ColorSchema(color_group,label_group)
            #self.draw_layers[layer].set_edge_color(stars.LISA_MAP_EDGE_COLOR)
            self.draw_layers[layer].set_data_group(id_groups)
            self.draw_layers[layer].set_fill_color_group(color_group)
            
        except Exception as err:
            self.ShowMsgBox(str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return None
            
    @staticmethod
    def process_LISA(parent, data,weight_path):
        """
        """
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Computing LISA with 499 permutations...               ",
            maximum = 2,
            parent=parent,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
            )
        progress_dlg.CenterOnScreen()
        progress_dlg.Update(1)
        
        id_groups = [[] for i in range(6)]
       
        try:
            # call Geoda LISA DLL first
            from stars.core.LISAWrapper import call_lisa
            localMoran, sigLocalMoran, sigFlag, clusterFlag = call_lisa(data, str(weight_path), 499)
            # prepare drawing map
            # 0 not significant, 1 HH, 2 LL, 3 LH, 4 HL, 5 Neighborless
            lm_moran = np.array(localMoran)
            lm_p_sim = np.array(sigLocalMoran)
            lm_sig = np.array(sigFlag)
            lm_q = np.array(clusterFlag)
           
            for i,sig in enumerate(lm_sig):
                if sig > 0:
                    id_groups[lm_q[i]].append(i)
                else:
                    id_groups[0].append(i)
        except:
            # if DLL call is failed, try pysal LISA instead
            w = pysal.open(weight_path).read()
            lm = pysal.Moran_Local(data, w, transformation = "r", permutations = 499)
            
            for i, sig in enumerate(lm.p_sim):
                if sig < parent.siglevel:
                    id_groups[lm.q[i]].append(i)
                else:
                    id_groups[0].append(i)
                    
        progress_dlg.Update(2)
        progress_dlg.Destroy()
        
        return id_groups