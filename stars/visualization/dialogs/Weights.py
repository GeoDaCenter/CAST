"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['TimeWeightsDlg','WeightCharDlg','SelectWeightDlg','CreatingWeightDlg']

import copy,os
import scipy.spatial as spatial
import numpy as np
import pysal
from pysal.weights.user import *
from pysal.weights.util import min_threshold_distance

import wx
from wx import xrc

import stars
from stars.model import CShapeFileObject
from stars.visualization import PlotWidget
from stars.visualization.plots.Histogram import Histogram

from stars.og.OGWrapper import *

class TimeWeightsDlg():
    def __init__(self, main, t, shape_name):
        self.t            = t
        self.shape_name   = shape_name
        self.main         = main
        self.resource     = self.main.dialog_res
        dlg = self.resource.LoadDialog(main, 'IDD_DIALOG_TIME_WEIGHTS')
       
        self.rdo_selectweight= xrc.XRCCTRL(dlg, 'IDC_RADIO_OPENWEIGHT')
        self.txt_weightpath  = xrc.XRCCTRL(dlg, 'IDC_EDIT_FILEWEIGHT')
        self.btn_weightfile  = xrc.XRCCTRL(dlg, 'IDC_OPEN_FILEWEIGHT')
        self.rdo_createweight= xrc.XRCCTRL(dlg, 'IDC_RADIO_CREATEWEIGHT')
        self.txt_p_neighbors = xrc.XRCCTRL(dlg, 'IDC_EDIT_N_P_NEIGHBORS')
        #self.chk_future      = xrc.XRCCTRL(dlg, 'IDC_CHK_FUTURE')
        self.lbl_f_neighbors = xrc.XRCCTRL(dlg, 'IDC_STATIC_F_NEIGHBORS')
        self.lbl_p_neighbors = xrc.XRCCTRL(dlg, 'IDC_STATIC_P_NEIGHBORS')
        self.txt_f_neighbors = xrc.XRCCTRL(dlg, 'IDC_EDIT_N_F_NEIGHBORS')
        self.dialog          = dlg
      
        self.rdo_selectweight.Bind(wx.EVT_RADIOBUTTON, self.ChooseSelectWeight)
        self.rdo_createweight.Bind(wx.EVT_RADIOBUTTON, self.ChooseCreateWeight)
        self.btn_weightfile.Bind(wx.EVT_BUTTON, self.OpenWeightFile)
        #self.chk_future.Bind(wx.EVT_CHECKBOX, self.CheckFuture)
        
        self.n_p_neighbors = 0
        self.n_f_neighbors = 0
      
    def ChooseSelectWeight(self, event):
        self.btn_weightfile.Enable(True)
        self.txt_weightpath.Enable(True)
        self.txt_p_neighbors.Enable(False)
        #self.chk_future.Enable(False)
        self.lbl_f_neighbors.Enable(False)
        self.lbl_p_neighbors.Enable(False)
        self.txt_f_neighbors.Enable(False)
        
    def ChooseCreateWeight(self, event):
        self.btn_weightfile.Enable(False)
        self.txt_weightpath.Enable(False)
        self.txt_p_neighbors.Enable(True)
        #self.chk_future.Enable(True)
        self.lbl_p_neighbors.Enable(True)
        self.lbl_f_neighbors.Enable(True)
        self.txt_f_neighbors.Enable(True)
    
    def OpenWeightFile(self, event):
        dlg = wx.FileDialog(
            self.main, message="Choose a weights file", 
            wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.weight_path = dlg.GetPath() 
            self.txt_weightpath.SetValue(self.weight_path)
        dlg.Destroy()
        
    def CheckFuture(self,event):
        self.lbl_f_neighbors.Enable(event.IsChecked())
        self.txt_f_neighbors.Enable(event.IsChecked())
        if not event.IsChecked():
            self.txt_f_neighbors.SetValue("")
        
    def create_time_w(self, n_previous=1, n_future=0):
        t = self.t
        neighbors = {}
        for i in range(t):
            id = i
            neighbors[id] = []
            if i > 0:
                start_pos = 0 if i - n_previous<0 else i - n_previous
                end_pos   = i
                for j in range(start_pos, end_pos):
                    neighbors[id].append(j)
            if i < t -1:
                start_pos = i + 1
                end_pos   = t if start_pos+n_future>t else start_pos+n_future
                for j in range(start_pos, end_pos):
                    neighbors[id].append(j)
        return neighbors
    
    def Show(self):
        self.dialog.Fit()
        if self.dialog.ShowModal() == wx.ID_OK:
            import pysal
            time_gstar    = dict()
            time_gstar_z  = dict()
            
            if self.rdo_createweight.GetValue():
                if len(self.txt_p_neighbors.GetValue()):
                    self.n_p_neighbors = int(self.txt_p_neighbors.GetValue())
                
                if len(self.txt_f_neighbors.GetValue()):
                    self.n_f_neighbors = int(self.txt_f_neighbors.GetValue())
                   
                if self.n_p_neighbors ==0 and self.n_f_neighbors==0:
                    return False
                
                n_previous = self.n_p_neighbors
                n_future   = self.n_f_neighbors
                tneighbors = self.create_time_w(n_previous, n_future)
                tweights   = pysal.W(tneighbors)
                dlg = wx.FileDialog(
                    self.main, message="Save the time weights file as ...", 
                    defaultFile=self.shape_name +'.time.gal', 
                    wildcard="Weights file (*.gal)|*.gal|All files (*.*)|*.*", 
                    style=wx.SAVE)
                if dlg.ShowModal() == wx.ID_OK:
                    save_weight_path = dlg.GetPath()
                    o = pysal.open(save_weight_path,'w')
                    o.write(tweights)
                    o.close()
                dlg.Destroy()
                self.weight_path = save_weight_path
            self.dialog.Destroy()
            return self.weight_path
        self.dialog.Destroy()
        return False
        
class WeightCharDlg():
    """
    """
    def __init__(self, main, resource):
        self.main = main
        self.resource = resource
        self.dialog = resource.LoadDialog(main,'IDD_WEIGHT_CHARACTERISTICS')
        
        assert isinstance(self.dialog, wx.Dialog)
        
        self.txt_weight_path = xrc.XRCCTRL(self.dialog, 'IDC_EDIT_FILEWEIGHT')
        self.btn_open_weight = xrc.XRCCTRL(self.dialog, 'IDC_OPEN_FILEWEIGHT')
        self.btn_ok = xrc.XRCCTRL(self.dialog, 'wxID_OK')
        self.btn_close = xrc.XRCCTRL(self.dialog, 'wxID_CANCEL')
        
        self.btn_ok.SetId(wx.ID_OK)
        self.btn_close.SetId(wx.ID_CANCEL)
       
        self.dialog.Bind(wx.EVT_BUTTON, self.OnOpenWeightFile, self.btn_open_weight)
        
    def OnOpenWeightFile(self, event):
        dlg = wx.FileDialog(self.main, message="Choose a weights file", 
                            wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
                            style=wx.OPEN| wx.CHANGE_DIR)
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        weight_path = dlg.GetPath() 
        self.txt_weight_path.SetValue(weight_path)
    
    def Show(self):
        try:
            self.dialog.Fit()
            if self.dialog.ShowModal() == wx.ID_OK:
                path = self.txt_weight_path.GetValue()
                name = os.path.splitext(os.path.basename(path))[0]
                w = pysal.open(path).read()
                data = {name:w.histogram}
                data = dict([(w.id2i[id],len(nbs)) for id, nbs in w.neighbors.iteritems()])
                hist_widget = PlotWidget(
                    self.main,
                    name,
                    {'Connectivity':data}, 
                    Histogram, 
                    title="Histogram(%s) Connectivity of Weights" % name)
                hist_widget.Show() 
                """
                shp = self.main.GetSHP(name)
                if shp == None:
                    msg = "Please open shapefile \"%s\" first." % name
                    dlg = wx.MessageDialog(self.main, msg, 'Warning', wx.OK|wx.ICON_WARNING)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    w = pysal.open(path).read()
                    data = {name:w.histogram}
                    data = dict([(w.id2i[id],len(nbs)) for id, nbs in w.neighbors.iteritems()])
                    hist_widget = PlotWidget(
                        self.main,
                        shp,
                        {'Connectivity':data}, 
                        Histogram, 
                        title="Histogram(%s) Connectivity of Weights" % name)
                    hist_widget.Show() 
                """
            self.dialog.Destroy()
        except Exception as err:
            dlg = wx.MessageDialog(self.main, 
                                   """Could not open weights file! Please select a valid weights file.
                                   
Details: """+ str(err.message), 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            
class SelectWeightDlg():
    """
    """
    def __init__(self,main,resource):
        self.main = main
        self.resource = resource
        self.dialog = resource.LoadDialog(main,'IDD_SELECT_WEIGHT')
        
        assert isinstance(self.dialog, wx.Dialog)
        
        self.rdo_select_weight = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_OPENWEIGHT1')
        self.choice_select_weight = xrc.XRCCTRL(self.dialog, 'IDC_CURRENTUSED_W')
        self.rdo_open_weight = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_OPENWEIGHT2')
        self.cbox_set_default = xrc.XRCCTRL(self.dialog, 'IDC_CHECK_DEFAULT')

        self.txt_weight_path = xrc.XRCCTRL(self.dialog, 'IDC_EDIT_FILEWEIGHT')
        self.btn_open_weight = xrc.XRCCTRL(self.dialog, 'IDC_OPEN_FILEWEIGHT')
        self.btn_create_weight = xrc.XRCCTRL(self.dialog, 'ID_CREATE_WEIGHTS')
        self.btn_ok = xrc.XRCCTRL(self.dialog, 'wxID_OK')
        self.btn_close = xrc.XRCCTRL(self.dialog, 'wxID_CANCEL')
        
        self.btn_ok.SetId(wx.ID_OK)
        self.btn_close.SetId(wx.ID_CANCEL)
       
        self.dialog.Bind(wx.EVT_BUTTON, self.OnOpenWeightFile, self.btn_open_weight)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnCreateWeightClick, self.btn_create_weight)
       
        # init dialog
        self.rdo_open_weight.SetValue(True)
        
        if len(self.main.weightsfiles) > 0:
            self.rdo_select_weight.SetValue(True)
            for wfile in self.main.weightsfiles:
                self.choice_select_weight.Append(wfile)
                self.choice_select_weight.SetSelection(0)
        
    def OnOpenWeightFile(self, event):
        dlg = wx.FileDialog(
            self.main, message="Choose a weights file", 
            wildcard="Weights file (*.gal,*.gwt)|*.gal;*.gwt|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.weight_path = dlg.GetPath() 
            self.txt_weight_path.SetValue(self.weight_path)
        dlg.Destroy()
        
    def OnCreateWeightClick(self, event):
        create_weight_dlg = CreatingWeightDlg(self.main, self.resource)
        w_path = create_weight_dlg.Show()
        if w_path:
            self.weight_path = w_path
            self.txt_weight_path.SetValue(w_path)
            self.rdo_open_weight.SetValue(True)
        
    def ShowModal(self):
        self.dialog.Fit()
        return self.dialog.ShowModal()
    
    def Destroy(self):
        self.dialog.Destroy()
        
    def GetWeightPath(self):
        if self.rdo_open_weight.GetValue() == True:
            if self.weight_path not in self.main.weightsfiles:
                self.main.weightsfiles.append(self.weight_path)
            return self.weight_path
        elif self.rdo_select_weight.GetValue() == True:
            return self.choice_select_weight.GetStringSelection()
            
class CreatingWeightDlg():
    """
    """
    def __init__(self, main, resource):
        self.main = main
        self.resource = resource
        self.dlg_add_id_var = resource.LoadDialog(main,"IDD_ADD_ID_VARIABLE")
        self.dialog = resource.LoadDialog(main,'IDD_WEIGHTS_FILE_CREATION')

        self.dist_thres_max = None
        self.dist_thres_min = None
        self.xs = None
        self.ys = None
        
        assert isinstance(self.dialog, wx.Dialog)
        assert isinstance(self.dlg_add_id_var, wx.Dialog)
        
        # initial Ctrls
        self.btn_openshp = xrc.XRCCTRL(self.dialog, 'IDC_BROWSE_ISHP4W')
        self.txt_shapefile = xrc.XRCCTRL(self.dialog, 'ID_IN_SHP_TXT_CTRL')
        self.btn_add_id_var = xrc.XRCCTRL(self.dialog, 'ID_CREATE_ID')
        self.cho_id_var = xrc.XRCCTRL(self.dialog, 'IDC_IDVARIABLE')
        self.rdo_queen = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_QUEEN')
        self.rdo_rook = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_ROOK')
        self.txt_order_contiguity = xrc.XRCCTRL(self.dialog, 'IDC_EDIT_ORDEROFCONTIGUITY')
        self.spn_order_configuity = xrc.XRCCTRL(self.dialog, 'IDC_SPIN_ORDEROFCONTIGUITY')
        self.ckb_lower_order = xrc.XRCCTRL(self.dialog, 'IDC_CHECK1')
        self.cho_dist_metric = xrc.XRCCTRL(self.dialog, 'IDC_DISTANCE_METRIC')
        self.cho_x_coord = xrc.XRCCTRL(self.dialog, 'IDC_XCOORDINATES')
        self.cho_y_coord = xrc.XRCCTRL(self.dialog, 'IDC_YCOORDINATES')
        self.rdo_distance = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_DISTANCE')
        self.txt_threshold_dist = xrc.XRCCTRL(self.dialog, 'IDC_TRESHOLD_EDIT')
        self.sld_threshold_dist = xrc.XRCCTRL(self.dialog, 'IDC_TRESHOLD_SLIDER')
        self.rdo_knn = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_KNN')
        self.txt_knn = xrc.XRCCTRL(self.dialog, 'IDC_EDIT_KNN')
        self.spn_knn = xrc.XRCCTRL(self.dialog, 'IDC_SPIN_KNN')
        #self.rdo_kernel = xrc.XRCCTRL(self.dialog, 'IDC_RADIO_KERNEL')
        #self.txt_kernel_bandwidth= xrc.XRCCTRL(self.dialog, 'IDC_KERNEL_BANDWIDTH_EDIT')
        #self.spn_kernel_knn= xrc.XRCCTRL(self.dialog, 'IDC_SPIN_KERNEL_KNN')
        #self.cho_kernel_function = xrc.XRCCTRL(self.dialog, 'IDC_KERNAL_FUNCTION')
        
        #self.txt_shapefile.SetValue(main.shapefiles[0].name)
        
        self.btn_create = xrc.XRCCTRL(self.dialog, 'IDOK_CREATE1')
        self.btn_close = xrc.XRCCTRL(self.dialog, 'wxID_CLOSE')
        
        self.txt_new_ID_name = xrc.XRCCTRL(self.dlg_add_id_var, 'IDC_NEW_ID_VAR')
        self.lst_exist_vars_list = xrc.XRCCTRL(self.dlg_add_id_var, 'IDC_EXISTING_VARS_LIST')
        
        self.btn_create.SetId(wx.ID_OK)
        self.btn_close.SetId(wx.ID_CANCEL)
      
        self.btn_add_id_var.Enable(False)
        self.cho_id_var.Enable(False)
        self.rdo_queen.Enable(False)
        self.rdo_rook.Enable(False)
        self.txt_order_contiguity.Enable(False)
        self.txt_order_contiguity.SetValue("1")
        self.spn_order_configuity.Enable(False)
        self.ckb_lower_order.Enable(False)
        self.cho_dist_metric.Enable(False)
        self.cho_x_coord.Enable(False)
        self.cho_y_coord.Enable(False)
        self.rdo_distance.Enable(False)
        self.txt_threshold_dist.Enable(False)
        self.txt_threshold_dist.SetValue("0.0")
        self.txt_threshold_dist.SetEditable(True)
        self.sld_threshold_dist.Enable(False)
        self.rdo_knn.Enable(False)
        self.txt_knn.Enable(False)
        self.txt_knn.SetValue("1")
        self.txt_knn.SetEditable(True)
        self.spn_knn.Enable(False)
        #self.rdo_kernel.Enable(False)
        #self.txt_kernel_bandwidth.Enable(False)
        #self.spn_kernel_knn.Enable(False)
        #self.cho_kernel_function.Enable(False)
        self.btn_create.Enable(False)
        
        # events
        self.dialog.Bind(wx.EVT_CHOICE, self.OnWeightFieldIDSelect, self.cho_id_var)
        self.dialog.Bind(wx.EVT_CHOICE, self.OnDistWeightCho, self.cho_x_coord)
        self.dialog.Bind(wx.EVT_CHOICE, self.OnDistWeightCho, self.cho_y_coord)
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnContiguitySelect, self.rdo_queen)
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnContiguitySelect, self.rdo_rook)
        
        self.dialog.Bind(wx.EVT_SPIN_UP, self.OnOrderContiguitySpinUp, self.spn_order_configuity)
        self.dialog.Bind(wx.EVT_SPIN_DOWN, self.OnOrderContiguitySpinDown, self.spn_order_configuity)
        
        self.dialog.Bind(wx.EVT_SPIN_UP, self.OnKNNSpinUp, self.spn_knn)
        self.dialog.Bind(wx.EVT_SPIN_DOWN, self.OnKNNSpinDown, self.spn_knn)
        
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnThresDistSelect, self.rdo_distance)
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnKNNSelect, self.rdo_knn)
        self.dialog.Bind(wx.EVT_SLIDER, self.OnThresSlider, self.sld_threshold_dist)
        #self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnKernelSelect, self.rdo_kernel)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnOpenShapeFile, self.btn_openshp)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnAddIDVariable, self.btn_add_id_var)

    def ShowMsgBox(self,msg,mtype='Warning',micon=wx.ICON_WARNING):
        dlg = wx.MessageDialog(None, msg, mtype, wx.OK|micon)
        dlg.ShowModal()
        dlg.Destroy()
       
    def OnAddIDVariable(self, event):
        """
        Add ID variable for a dbf file
        """
        # setup vars
        txt_new_ID_name = self.txt_new_ID_name
        lst_exist_vars_list = self.lst_exist_vars_list
        lst_exist_vars_list.SetItems(self.id_var_list)

        # show ADD_ID_VARIABLE dialog
        if self.dlg_add_id_var.ShowModal() == wx.ID_CANCEL:
            self.dlg_add_id_var.Hide()#Destroy()
            return
        self.dlg_add_id_var.Hide()#Destroy()
        
        # check if dbf fields already contain POLY_ID
        new_ID_name = str(txt_new_ID_name.GetValue())
        if new_ID_name in self.id_var_list:
            self.ShowMsgBox('This ID variable already exists in the dbf file, please respecify.')
            return
        
        # add ID variable
        dbf = self.shp_layer.dbf
        try:
            orgDBF_path = '%s.dbf'%self.shp_path[:-4]
            newDBF_path = '%s.tmp.dbf'% self.shp_path[:-4]
            newDBF      = pysal.open(newDBF_path,'w')
            newDBF.header = []
            newDBF.field_spec = []
            newDBF.header.append(new_ID_name)
            newDBF.field_spec.append(('N',9,0))
            
            for i in dbf.header:
                newDBF.header.append(i)
                
            for i in dbf.field_spec:
                newDBF.field_spec.append(i)
                
            for i in range(dbf.n_records): 
                newRow = dbf.read_record(i)
                newRow.insert(0,i+1)
                newDBF.write(newRow)
                
            newDBF.close()
          
            dbf._dbf.close()
            os.remove(orgDBF_path)
            os.rename(newDBF_path, orgDBF_path)
            # reload dbf
            self.shp_layer.loadDBF(orgDBF_path)
            # reload "Weights File ID variable"
            self.LoadDBFFields()
            self.cho_id_var.SetSelection(0)
            
            self.triggerWeightsCho()
            self.get_ids_from_dbf(new_ID_name)
            
            self.ShowMsgBox("ID variable \"%s\" was added successfully."%new_ID_name,
                            mtype='Information',
                            micon=wx.ICON_INFORMATION)
            
        except Exception as err:
            self.ShowMsgBox("ID variable could not be added. Please make sure you do not have any empty cells in original dbf file. " + str(err.message))
        
    def OnKernelSelect(self, event):
        #self.txt_kernel_bandwidth.Enable(True)
        #self.cho_kernel_function.Enable(True)
       
        self.kernel_fun_list = ['triangular','uniform','quadratic','quartic','gaussian']
        self.cho_kernel_function.SetItems(self.kernel_fun_list)
        self.cho_kernel_function.SetSelection(0)
        
        self.txt_threshold_dist.Enable(False)
        self.sld_threshold_dist.Enable(False)
        self.txt_knn.Enable(False)
        self.spn_knn.Enable(False)
        self.txt_order_contiguity.Enable(False)
        self.spn_order_configuity.Enable(False)
        self.ckb_lower_order.Enable(False)
        
        self.cho_dist_metric.Enable(False)
        self.cho_x_coord.Enable(False)
        self.cho_y_coord.Enable(False)
        
    def OnWeightFieldIDSelect(self, event):
        self.get_ids_from_dbf(event.GetString())
        
    def get_ids_from_dbf(self, colname):
        try:
            self.ids = self.shp_layer.dbf.by_col(colname)
            if len(self.ids) != len(set(self.ids)):
                raise Exception("")
           
            self.ids = range(len(self.ids))
            self.ids = VecInt(self.ids)
            
            self.triggerWeightsCho()
            
        except Exception as err:
            self.ShowMsgBox("Please select a unique ID field for creating weights file.")
            self.cho_id_var.SetSelection(0)
    
    def triggerWeightsCho(self):
        if self.cho_id_var.GetCurrentSelection() >=0:
            if self.shp_layer.shape_type == stars.SHP_POLYGON:
                self.rdo_queen.Enable(True)
                self.rdo_rook.Enable(True)
                
            self.rdo_knn.Enable(True)
            self.rdo_distance.Enable(True)
            #self.rdo_kernel.Enable(True)
            self.btn_create.Enable(True)
            
    def OnKNNSelect(self, event):
        self.txt_knn.Enable(True)
        self.spn_knn.Enable(True)
        
        self.cho_dist_metric.Enable(False)
        self.cho_x_coord.Enable(False)
        self.cho_y_coord.Enable(False)
        self.txt_order_contiguity.Enable(False)
        self.spn_order_configuity.Enable(False)
        self.ckb_lower_order.Enable(False)
        
        self.txt_threshold_dist.Enable(False)
        self.sld_threshold_dist.Enable(False)
        #self.txt_kernel_bandwidth.Enable(False)
        #self.cho_kernel_function.Enable(False)
        
        self.updatePoints()
        
    def OnThresDistSelect(self, event):
        self.txt_order_contiguity.Enable(False)
        self.spn_order_configuity.Enable(False)
        self.ckb_lower_order.Enable(False)
        
        self.txt_knn.Enable(False)
        self.spn_knn.Enable(False)
        #self.txt_kernel_bandwidth.Enable(False)
        #self.cho_kernel_function.Enable(False)
        
        self.cho_dist_metric.Enable(True)
        self.cho_x_coord.Enable(True)
        self.cho_y_coord.Enable(True)
        self.txt_threshold_dist.Enable(True)
        self.sld_threshold_dist.Enable(True)
       
        self.cho_dist_metric.SetItems(['<Euclidean Distance>','<Arc Distance>'])
        self.cho_dist_metric.SetSelection(0)
        
        x_coord_list = []
        y_coord_list = []
        for i, field in enumerate(self.shp_layer.dbf.header):
            if self.shp_layer.dbf.field_spec[i][0] == 'N' or\
               self.shp_layer.dbf.field_spec[i][0] == 'F':
                x_coord_list.append(self.shp_layer.dbf.header[i])
                y_coord_list.append(self.shp_layer.dbf.header[i])
                                    
        if self.shp_layer.shape_type == stars.SHP_POLYGON:
            #x_coord_list.insert(0,'<X-Mean-Center>')
            x_coord_list.insert(0,'<X-Centroid>')
            #y_coord_list.insert(0,'<Y-Mean-Center>')
            y_coord_list.insert(0,'<Y-Centroid>')
        else:
            x_coord_list.insert(0,'<X>')
            y_coord_list.insert(0,'<Y>')
            
        self.cho_x_coord.SetItems(x_coord_list)
        self.cho_x_coord.SetSelection(0)
        self.cho_y_coord.SetItems(y_coord_list)
        self.cho_y_coord.SetSelection(0)
        
        if self.dist_thres_min == None and self.dist_thres_max == None:
            self.updatePoints()
            
            dist_type = self.cho_dist_metric.GetStringSelection()
            method = 1
            if dist_type == "Arc Distance":
                method = 2 
                
            self.dist_thres_min = OGComputeCutOffPoint(self.xs, self.ys, method)
            self.dist_thres_max = OGComputeMaxDistance(self.xs, self.ys ,method)        
        
        self.sld_threshold_dist.SetRange(0,100)
        self.txt_threshold_dist.SetValue('%.5f'%(self.dist_thres_min+1E-5))
       
    def OnDistWeightCho(self, event):
        self.updatePoints()
        
    def updatePoints(self):
        x_selection = self.cho_x_coord.GetSelection()
        y_selection = self.cho_y_coord.GetSelection()

        xs = []
        ys = []
        
        if x_selection <= 0 and y_selection <= 0:
            if self.shp_layer.shape_type == stars.SHP_POLYGON:
                for p in self.shp_layer.centroids:
                    if isinstance(p, list):
                        # todo, for polygon there might be several parts
                        xs.append(p[0][0])
                        ys.append(p[0][1])
            else:
                for p in self.shp_layer:
                    xs.append(p[0])
                    ys.append(p[1])
        else:
            # if user specifies columns for x,y
            if x_selection > 0:
                xs = self.shp_layer.dbf.by_col(self.cho_x_coord.GetStringSelection())
            if y_selection > 0:
                ys = self.shp_layer.dbf.by_col(self.cho_y_coord.GetStringSelection())
       
        if xs == None or len(xs) == 0 or ys==None or len(ys) == 0:
            self.dist_thres_min = None
            self.dist_thres_max = None
            return
            
        self.xs = VecDouble(xs)
        self.ys = VecDouble(ys)
       
        
    def OnThresSlider(self, event):
        tick = self.sld_threshold_dist.GetValue()
        thres = self.dist_thres_min + (self.dist_thres_max-self.dist_thres_min) * tick /100.0 
        self.txt_threshold_dist.SetValue('%.5f' %(thres+1E-5))
        
    def OnOrderContiguitySpinUp(self, event):
        oc_txt = self.txt_order_contiguity.GetValue()
        try:
            oc_val = int(oc_txt)
        except:
            return
        oc_val += 1 
        self.txt_order_contiguity.SetValue(str(oc_val))
        
    def OnOrderContiguitySpinDown(self, event):
        oc_txt = self.txt_order_contiguity.GetValue()
        try:
            oc_val = int(oc_txt)
        except:
            return
        oc_val = oc_val - 1  if oc_val > 0 else 0
        self.txt_order_contiguity.SetValue(str(oc_val))
        
    def OnKNNSpinUp(self, event):
        knn_txt = self.txt_knn.GetValue()
        try:
            knn_val = int(knn_txt)
        except:
            return
        knn_val += 1 
        self.txt_knn.SetValue(str(knn_val))
        
    def OnKNNSpinDown(self, event):
        knn_txt = self.txt_knn.GetValue()
        try:
            knn_val = int(knn_txt)
        except:
            return
        knn_val = knn_val - 1  if knn_val > 0 else 0
        self.txt_knn.SetValue(str(knn_val))
    
    def OnContiguitySelect(self, event):
        self.txt_order_contiguity.Enable(True)
        self.spn_order_configuity.Enable(True)
        self.ckb_lower_order.Enable(True)
        self.txt_knn.Enable(False)
        self.spn_knn.Enable(False)
        self.txt_threshold_dist.Enable(False)
        self.sld_threshold_dist.Enable(False)
        #self.txt_kernel_bandwidth.Enable(False)
        #self.cho_kernel_function.Enable(False)
        
        self.cho_dist_metric.Enable(False)
        self.cho_x_coord.Enable(False)
        self.cho_y_coord.Enable(False)
        
    def OnOpenShapeFile(self, event):
        dlg = wx.FileDialog(
            self.main, message="Choose a file", 
            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR)
        
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        shp_path = dlg.GetPath()
        self.shp_path = shp_path
        self.txt_shapefile.SetValue(shp_path)
       
        existed = False
        for shp in self.main.shapefiles:
            if shp.path == shp_path:
                self.shp_layer = shp
                existed = True
                break
       
        if not existed:
            self.shp_layer = CShapeFileObject(shp_path)
            self.main.shapefiles.append(self.shp_layer)
        
        if self.shp_layer.shape_type == stars.SHP_LINE:
            self.ShowMsgBox("Can't create weights file for LINE shapefile.")
            return
       
        self.LoadDBFFields()
        self.btn_add_id_var.Enable(True)
       
    def LoadDBFFields(self):
        self.cho_id_var.Clear()
        self.dbf_fields = []
        for i,field in enumerate(self.shp_layer.dbf.header):
            if self.shp_layer.dbf.field_spec[i][0] == 'N':
                self.dbf_fields.append(field)
        self.cho_id_var.SetItems(self.dbf_fields)
        self.id_var_list = self.dbf_fields
        self.cho_id_var.Enable(True)
    
    def Show(self):
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Creating weights file... ",
            maximum = 2,
            parent=self.main,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        progress_dlg.Hide()
        try:
            self.dialog.Fit()
            self.dialog.CenterOnScreen()
            if self.dialog.ShowModal() == wx.ID_OK:
                if self.shp_path.find('/')>=0:
                    defaultDir =self.shp_path[0:self.shp_path.rindex('/')]
                elif self.shp_path.find('\\') >=0:
                    defaultDir =self.shp_path[0:self.shp_path.rindex('\\')]
                else:
                    defaultDir = ''
                
                suffix = '.gal'
                wildcard="Weights file (*.gal)|*.gal| Weights file (*.gwt)|*.gwt|All files (*.*)|*.*"
                if self.rdo_knn.GetValue() == True or self.rdo_distance.GetValue() == True:
                    suffix = '.gwt'
                    wildcard="Weights file (*.gwt)|*.gwt|Weights file (*.gal)|*.gal| All files (*.*)|*.*"
                
                dlg = wx.FileDialog(
                    self.main, message="Save the weights file as ...", 
                    defaultDir = defaultDir,
                    defaultFile=self.shp_layer.name + suffix, 
                    wildcard=wildcard,
                    style=wx.SAVE
                )
                if dlg.ShowModal() != wx.ID_OK:
                    dlg.Destroy()
                    raise Exception("")
                
                weight_path = dlg.GetPath()
                dlg.Destroy()
                
                ooC = int(self.txt_order_contiguity.GetValue())
                is_include_lower = int(self.ckb_lower_order.GetValue())
                id_variable = self.id_var_list[self.cho_id_var.GetCurrentSelection()]
                dist_type = self.cho_dist_metric.GetStringSelection()
                method = 1
                if dist_type == "Arc Distance":
                    method = 2 
                    
                progress_dlg.Show()
                progress_dlg.CenterOnScreen()
                progress_dlg.Update(1)
                
                flag = False
                
                if self.rdo_queen.GetValue() == True:
                    flag = OGCreateGal(str(self.shp_path), str(weight_path), str(id_variable), 
                                       self.ids, 0, ooC, is_include_lower)
                    
                elif self.rdo_rook.GetValue() == True:
                    flag = OGCreateGal(str(self.shp_path), str(weight_path), str(id_variable), 
                                       self.ids, 1, ooC, is_include_lower)
                    
                elif self.rdo_knn.GetValue() == True:
                    if self.xs == None or self.ys==None:
                        raise Exception("Points/Centroids not correct.")
                    
                    k = int(self.txt_knn.GetValue())
                    if k < 1:
                        raise Exception("k (KNN) should be at least 1!")
                        
                    flag = OGCreateGwt(str(weight_path), str(id_variable),
                                       self.ids, self.xs, self.ys, .0, k, method)
                    
                elif self.rdo_distance.GetValue() == True:
                    if self.xs == None or self.ys==None:
                        raise Exception("Points/Centroids not correct.")
                    
                    thres = float(self.txt_threshold_dist.GetValue())
                    flag = OGCreateGwt(str(weight_path), str(id_variable),self.ids,
                                       self.xs, self.ys, thres, 0, method)
                    
                if flag == False:
                    raise Exception("Weights file NOT created.")
                
                progress_dlg.Update(2)
                progress_dlg.Destroy()        
                
                self.ShowMsgBox("Weights file created.",
                                mtype='Information',
                                micon=wx.ICON_INFORMATION)
                
                return  weight_path
                
        except Exception as err:
            progress_dlg.Update(2)
            progress_dlg.Destroy()        
            self.ShowMsgBox("Failed to create a Weights file: "+ str(err.message))
            
            return None