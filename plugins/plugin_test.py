import math,os
import wx
import numpy as np
import pysal

import stars
from stars.visualization import MapWidget
from stars.visualization.maps import ShapeMap, ColorSchema 
from stars.visualization.utils import FilterShapeList
from stars.visualization.dialogs import VariableSelDialog
from stars.Plugin import *

class PluginOne(IMapPlugin):
    def __init__(self):
        IMapPlugin.__init__(self)
        
    def get_icon(self):
        new_bmp =  wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (16,16))
        return new_bmp
    
    def get_icon_size(self):
        return (16,16)
    
    def get_label(self):
        return 'test'
   
    def get_shortHelp(self):
        return ''
    
    def get_longHelp(self):
        return ''
    
    def get_toolbar_pos(self):
        return -1
    
    def get_parent_menu(self):
        return 'File'
    
    def show(self, event):
        main = event.EventObject.GetParent()
        
        shapefiles = main.shapefiles
        if not shapefiles or len(shapefiles) < 1:
            return
        plg_shp_list = FilterShapeList(shapefiles, stars.SHP_POLYGON)
        if len(plg_shp_list) == 0:
            main.ShowMsgBox('Sorry, no polygon shape file is available')
            return
        shp_list = [shp.name for shp in plg_shp_list]
        dlg = wx.SingleChoiceDialog(
            main, 'Select a shape file:', 'LISA Map', shp_list,wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            shp = plg_shp_list[idx] 
            if shp.dbf == None:
                main.ShowMsgBox('Sorry, no dbf file is available.')
                return
            lisaMap= MapWidget(main,[shp],MyLISAMap)
            lisaMap.Show()
        dlg.Destroy()
    
class MyLISAMap(ShapeMap):
    def __init__(self, parent, layers, **kwargs):
        ShapeMap.__init__(self,parent, layers)
       
        try:
            layer = layers[0]
            dbf = layer.dbf
            weight_path = ''
            field_name = ''
           
            # let user choose weight_path and field_name
            var_list = dbf.header
            var_dlg = VariableSelDialog(self,var_list,bDisable2nd=True)
            var_dlg.CenterOnScreen()
            if var_dlg.ShowModal() == wx.ID_OK:
                field_name = var_dlg.lb1.GetString(var_dlg.lb1.Selection)
                weight_dlg = WeightSelDialog(self.main.weightsfiles)
                weight_dlg.CenterOnScreen()
                if weight_dlg.ShowModal() == wx.ID_OK:
                    weight_path = weight_dlg.weight_path
                    # add current weight_path to global weights list
                    # for further usage
                    if weight_path not in self.main.weightsfiles:
                        self.main.weightsfiles.append(weight_path)
            var_dlg.Destroy()
            
            self.siglevel = 0.05
            self.parentFrame.SetTitle('Gi Cluster Map- %s'% layer.name)
            self.draw_layers[layer].set_edge_color(stars.DEFAULT_MAP_EDGE_COLOR)
            
            data = np.array(dbf.by_col(field_name))
            id_groups = self.process_LISA(data, weight_path)
            
            # default color schema
            color_group =[
                stars.LISA_NOT_SIG_COLOR, 
                stars.LISA_HH_COLOR,
                stars.LISA_LL_COLOR, 
            ]
            label_group = ["Not Significant","High","Low"]
            
            self.color_schema_dict[layer.name] = ColorSchema(color_group,label_group)
            self.draw_layers[layer].set_data_group(id_groups)
            self.draw_layers[layer].set_fill_color_group(color_group)
            
        except TypeError:
            # could be data type error (not int/float)
            self.ShowMsgBox("LISA data type error!")
            # cleanup from Observer
            #self.parentFrame.Close(True)
            wx.FutureCall(10, self.parentFrame.Close,True)
        except KeyError:
            # parameters error
            self.ShowMsgBox("LISA parameters error!")
            # cleanup from Observer
            #self.parentFrame.Close(True)
            wx.FutureCall(10, self.parentFrame.Close,True)
        except:
            self.ShowMsgBox("Unexpected LISA error!")
            #self.parentFrame.Close(True)
            wx.FutureCall(10, self.parentFrame.Close,True)
            
        
    def process_LISA(self,data,weight_path):
        """
        """
        id_groups = [[] for i in range(3)]
       
        w = pysal.open(weight_path).read()
        lm = pysal.esda.getisord.G_Local(data, w)
        
        for i, sig in enumerate(lm.p_sim):
            if sig < self.siglevel:
                id_groups[1].append(i)
            else:
                id_groups[0].append(i)
                    
        
        return id_groups
            
class WeightSelDialog(wx.Dialog):
    """
    """
    def __init__(self,exist_weights, parent=None):
        size = (400,300)
        if os.name == 'nt':
            size = (400,320)
        wx.Dialog.__init__(self, parent, -1, "Select Weights",
                           size = size,
                           pos = wx.DefaultPosition,
                           style = wx.DEFAULT_DIALOG_STYLE)
        self.weight_path = ''
        
        panel = wx.Panel(self,-1,size=size)
        x1,y1 = 0,0
        self.rb_used_weigths = wx.RadioButton(
            panel, -1, "Select from currently used", pos=(x1+10,y1+20),size=(200,-1))
        self.cmbox_weights = wx.ComboBox(panel, -1, "", (x1+10,y1+50),(350,-1),[])
        self.rb_weight_path =  wx.RadioButton(
            panel, -1,"Select from file (gal,gwt)", pos=(x1+10,y1+100),size=(200,-1))

        self.txt_weight_path = wx.TextCtrl(panel, -1, "",pos=(x1+10,y1+130), size=(330,-1) )
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        self.btn_weight_path = wx.BitmapButton(panel,-1, open_bmp, pos=(x1+345,y1+130))
        
        new_weight_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        wx.StaticText(panel, -1, "Create new weights file:",pos =(x1+10,y1+180),size=(135,-1))
        self.cb_used_weigths = wx.CheckBox(panel, -1, "Set as default", pos=(x1+10, y1+210),size=(135,-1))
                                           
        self.btn_ok = wx.Button(panel, wx.ID_OK, "OK",pos=(x1+80,y1+250),size=(90, 30))
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, "Close",pos=(x1+200,y1+250),size=(90, 30))
       
        self.rb_used_weigths.Enable(False)
        self.rb_weight_path.SetValue(True)
       
        if len(exist_weights) > 0:
            for w_path in exist_weights:
                self.cmbox_weights.Append(w_path)
            self.rb_used_weigths.Enable(True)
        
        self.Bind(wx.EVT_COMBOBOX, self.OnExistWSelect, self.cmbox_weights)
        self.Bind(wx.EVT_BUTTON, self.BrowseWeightFile, self.btn_weight_path)

    def OnExistWSelect(self, event):
        self.weight_path = event.GetString()
        self.txt_weight_path.SetValue(self.weight_path)
        
    def BrowseWeightFile(self,event):
        dlg = wx.FileDialog(None, message="Choose a weights file", 
                        wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
                        style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.weight_path = dlg.GetPath()            
            self.txt_weight_path.SetValue(self.weight_path)
        dlg.Destroy()    
        
if __name__=="__main__":
    issubclass(PluginOne, IMapPlugin)