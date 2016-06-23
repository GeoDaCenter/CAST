"""
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['CreateGridDlg','TransparentDlg', 'GradientDlg', 
           'choose_field_name', 'choose_box_hinge_value', 'select_k', 
           'choose_sample_percent', 'choose_user_defined_bins',
           'choose_local_g_settings']

import os
import pysal
import wx
from wx import xrc
            
class CreateGridDlg():
    def __init__(self, main):
        self.main = main
        self.resource = main.dialog_res
        self.dialog = self.resource.LoadDialog(main,"IDD_CREATE_GRID")
       
        self.rdo_manually = xrc.XRCCTRL(self.dialog, "IDC_RADIO1")
        self.txt_ll_x = xrc.XRCCTRL(self.dialog, "IDC_EDIT1")
        self.txt_ll_y = xrc.XRCCTRL(self.dialog, "IDC_EDIT2")
        self.txt_ur_x = xrc.XRCCTRL(self.dialog, "IDC_EDIT3")
        self.txt_ur_y = xrc.XRCCTRL(self.dialog, "IDC_EDIT4")
        
        self.rdo_shpbbox = xrc.XRCCTRL(self.dialog, "IDC_RADIO3")
        self.txt_shp_fpath = xrc.XRCCTRL(self.dialog, "IDC_EDIT5")
        self.btn_open_shp = xrc.XRCCTRL(self.dialog, "IDC_REFERENCEFILE2")
        
        self.txt_n_rows = xrc.XRCCTRL(self.dialog, "IDC_EDIT7")
        self.txt_n_cols = xrc.XRCCTRL(self.dialog, "IDC_EDIT8")
        
        self.txt_save_shp_fpath = xrc.XRCCTRL(self.dialog, "IDC_EDIT9")
        self.btn_save_shp = xrc.XRCCTRL(self.dialog, "IDC_BROWSE_OFILE")
        
        self.btn_create = xrc.XRCCTRL(self.dialog, "ID_CREATE")
        self.btn_close = xrc.XRCCTRL(self.dialog, "IDCANCEL")
        self.btn_close.SetId(wx.ID_CANCEL)
        
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnRdoManually, self.rdo_manually)
        self.dialog.Bind(wx.EVT_RADIOBUTTON, self.OnRdoShpbbox, self.rdo_shpbbox)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnOpenShapeFile, self.btn_open_shp)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnSaveShapeFile, self.btn_save_shp)
        self.dialog.Bind(wx.EVT_BUTTON, self.OnCreate, self.btn_create)
        
        self.bManually = True
        self.bShpbbox = False
        self.open_shp_path = ""
        self.save_shp_path = ""
        
        self.btn_open_shp.Enable(False)
        self.txt_shp_fpath.Enable(False)
        self.txt_ll_x.Enable(True)
        self.txt_ll_y.Enable(True)
        self.txt_ur_x.Enable(True)
        self.txt_ur_y.Enable(True)
        
    def ShowMsgBox(self,msg,mtype='Warning',micon=wx.ICON_WARNING):
        dlg = wx.MessageDialog(self.main, msg, mtype, wx.OK|micon)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnRdoManually(self, event):
        self.bManually = True
        self.bShpbbox = False
        
        self.btn_open_shp.Enable(False)
        self.txt_shp_fpath.Enable(False)
        self.txt_ll_x.Enable(True)
        self.txt_ll_y.Enable(True)
        self.txt_ur_x.Enable(True)
        self.txt_ur_y.Enable(True)
    
    def OnRdoShpbbox(self, event):
        self.bManually = False
        self.bShpbbox = True
        
        self.btn_open_shp.Enable(True)
        self.txt_shp_fpath.Enable(True)
        
        self.txt_ll_x.Enable(False)
        self.txt_ll_y.Enable(False)
        self.txt_ur_x.Enable(False)
        self.txt_ur_y.Enable(False)
    
    def OnOpenShapeFile(self, event):
        dlg = wx.FileDialog(
            self.main, message="Choose a file", 
            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
            style=wx.OPEN| wx.CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            shp_path = dlg.GetPath()
            self.open_shp_path = shp_path
            self.txt_shp_fpath.SetValue(shp_path)
        dlg.Destroy()
    
    def OnSaveShapeFile(self, event):
        if self.open_shp_path.find('/')>=0:
            defaultDir =self.open_shp_path[0:self.open_shp_path.rindex('/')]
        elif self.open_shp_path.find('\\') >=0:
            defaultDir =self.open_shp_path[0:self.open_shp_path.rindex('\\')]
        else:
            defaultDir = ''
            
        dlg = wx.FileDialog(
            self.main, message="Save shape file as ...", 
            defaultDir = defaultDir,
            defaultFile= '',
            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*", 
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            shp_path = dlg.GetPath()
            self.save_shp_path = shp_path
            self.txt_save_shp_fpath.SetValue(shp_path)
        
        dlg.Destroy()
    
    def Show(self):
        self.dialog.Fit()
        self.dialog.CenterOnScreen()
        self.dialog.Show()
        
    def OnCreate(self, event):
        try:
            if self.save_shp_path == "":
                raise Exception(" Please choose output weights file.")
            
            n_rows = int(self.txt_n_rows.GetValue())
            n_cols = int(self.txt_n_cols.GetValue())
            
            if n_rows<=0 or n_cols <=0:
                raise Exception(" Please choose valid row/column number.")
            
            if self.bManually:
                ll_x = float(self.txt_ll_x.GetValue())
                ll_y = float(self.txt_ll_y.GetValue())
                ur_x = float(self.txt_ur_x.GetValue())
                ur_y = float(self.txt_ur_y.GetValue())
               
                if ur_x <= ll_x:
                    raise Exception(" Upper-right corner X-coordinate should be larger than lower-left X-coordinate.")
                if ur_y <= ll_y:
                    raise Exception(" Upper-right corner Y-coordinate should be larger than lower-left corner Y-coordinate.")
                
                left = ll_x
                top = ur_y
                grid_w = (ur_x - ll_x) / n_rows
                grid_h = (ur_y - ll_y) / n_cols
                
            elif self.bShpbbox:
                open_shp = pysal.open(self.open_shp_path)
                shp_bbox = open_shp.bbox
                left,lower,right,top = shp_bbox
                grid_w = (right -left) / n_rows
                grid_h = (top - lower) / n_cols
                
            self.save_shp_path = self.txt_save_shp_fpath.GetValue()
            if not self.save_shp_path.lower().endswith('.shp'):
                self.save_shp_path += ".shp"
            grid_shp = pysal.open(self.save_shp_path,'w')
            grid_dbf = pysal.open(self.save_shp_path[:-3]+'dbf','w')
            grid_dbf.header = ['POLY_ID']
            grid_dbf.field_spec = [('N',9,0)]
           
            count = 1
            for i in range(n_rows):
                for j in range(n_cols):
                    p0 = pysal.cg.Point((left+i*grid_w, top-j*grid_h))
                    p1 = pysal.cg.Point((left+(i+1)*grid_w, top-j*grid_h))
                    p2 = pysal.cg.Point((left+(i+1)*grid_w, top-(j+1)*grid_h))
                    p3 = pysal.cg.Point((left+i*grid_w, top-(j+1)*grid_h))
                    
                    poly = pysal.cg.Polygon([p0,p1,p2,p3])
                    grid_shp.write(poly)
                    grid_dbf.write([count])
                    count += 1
                        
            grid_shp.close()
            grid_dbf.close()
            
            self.ShowMsgBox("Grid shapefile created successfully.",
                            mtype="Information",
                            micon=wx.ICON_INFORMATION)
            
        except Exception as err:
            self.ShowMsgBox("""Grid shape file could not be created. 
            
Details: """ + str(err.message))
    
    
class TransparentDlg(wx.Dialog):
    def __init__(self,map_canvas, layer_name): 
        size = (300, 165)
        if os.name == 'posix':
            size = (300,140)
        wx.Dialog.__init__(self, map_canvas, -1, "Transparent Settings",
                           size = size,
                           pos = wx.DefaultPosition,
                           style = wx.DEFAULT_DIALOG_STYLE)
        
        panel = wx.Panel(self,-1,size=size, pos=(10,5))
        x1,y1 = 10,10
           
        
        if os.name == 'posix':
            label= wx.StaticText(panel, -1, "Change opaque value:", pos=(x1,y1))
        else:
            label= wx.StaticText(panel, -1, "Change opaque value:", pos=(x1,y1-5))
            
        self.slideralpha= wx.Slider(panel, wx.NewId(), 100, 0, 100, pos=(x1,y1+15),size=(250, -1), style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slideralpha.SetTickFreq(10, 1)
     
        if layer_name == "Density Map":
            self.slideralpha.SetValue(int(map_canvas.opaque))
        else:
            color_schema = map_canvas.color_schema_dict[layer_name]
            self.slideralpha.SetValue(int(color_schema.opaque*100.0/255.0))
        
        if os.name == 'posix':
            label= wx.StaticText(panel, -1, "Current:", pos=(x1+45,y1+44))
        else:
            label= wx.StaticText(panel, -1, "Current:", pos=(x1+55,y1+15))
       
        self.btn_ok = wx.Button(panel, wx.ID_OK, "OK",pos=(x1+1,y1+74),size=(90, 30))
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, "Close",pos=(x1+95,y1+74),size=(90, 30))

class GradientDlg(wx.Dialog):
    def __init__(self,map_canvas): 
        size = (280, 140)
        if os.name == 'posix':
            size = (280,140)
        wx.Dialog.__init__(self, map_canvas, -1, "Gradient Settings",
                           size = size,
                           pos = wx.DefaultPosition,
                           style = wx.DEFAULT_DIALOG_STYLE)
        
        panel = wx.Panel(self,-1,size=size)
        x1,y1 = 10,10
            
        label= wx.StaticText(panel, -1, "Select gradient:", pos=(x1,y1))
        
        self.cmbox_kde_colorschema= wx.combo.BitmapComboBox(
            panel, -1, "", 
            pos=(x1, y1+25), size=(200,-1), style=wx.CB_DROPDOWN)
        self.addColorBand('classic')
        self.addColorBand('fire')
        self.addColorBand('omg')
        self.addColorBand('pbj')
        self.addColorBand('pgaitch')
        self.addColorBand('rdyibu')
        self.cmbox_kde_colorschema.SetSelection(0)
        self.gradient_type = 'classic'
        
        self.btn_ok = wx.Button(panel, wx.ID_OK, "OK",pos=(x1+1,y1+60),size=(90, 30))
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, "Close",pos=(x1+95,y1+60),size=(90, 30))
        
        self.Bind(wx.EVT_COMBOBOX, self.OnBitmapCombo, self.cmbox_kde_colorschema)
        
    def addColorBand(self, scheme_type):
        import stars
        gradient_img = stars.GRADIENT_IMG_DICT[scheme_type]
        gradient_img = gradient_img.Rotate90()
        gradient_img = gradient_img.Scale(140,20)
        bmp = gradient_img.ConvertToBitmap()
        self.cmbox_kde_colorschema.Append(scheme_type, bmp, None)

    def OnBitmapCombo(self, event):
        bcb = event.GetEventObject()
        idx = event.GetInt()
        self.gradient_type = bcb.GetString(idx)
        
    
def choose_field_name(self,layer, title="Choose a field", info="Select a column:"):
    var_list = layer.dbf.header
    var_dlg = wx.SingleChoiceDialog(self, info, title, var_list, wx.CHOICEDLG_STYLE)
    var_dlg.CenterOnScreen()
    if var_dlg.ShowModal() != wx.ID_OK:
        var_dlg.Destroy()
        return None
    field_name = var_dlg.GetStringSelection()
    var_dlg.Destroy()
    return field_name

def select_k(self):
    cate_dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_QUANTILE')
    cate_txt = xrc.XRCCTRL(cate_dlg, 'IDC_EDIT_QUANTILE')
    cate_txt.SetValue(5)
    cate_dlg.CenterOnScreen()
    if cate_dlg.ShowModal() != wx.ID_OK:
        cate_dlg.Destroy()
        return False
    k = int(cate_txt.GetValue())
    cate_dlg.Destroy()
    return k

def choose_box_hinge_value(self):
    dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_BOX_HINGE')
    txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_HINGE')
    txt.SetValue(str(1.5))
    dlg.CenterOnScreen()
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return False
    hinge = float(txt.GetValue())
    dlg.Destroy()
    return hinge
    
def choose_sample_percent(self):
    dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_JENKS_SAMPLE')
    txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_PERCENT')
    txt.SetValue(str(0.1))
    dlg.CenterOnScreen()
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return False
    percent = float(txt.GetValue())
    dlg.Destroy()
    return percent

def choose_user_defined_bins(self):
    dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_USER_DEFINED')
    txt = xrc.XRCCTRL(dlg, 'IDC_EDIT_Bins')
    dlg.CenterOnScreen()
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return False
  
    bins = None
    try:
        bins = eval(txt.GetValue())
    except:
        pass
    dlg.Destroy()
    return bins

def choose_local_g_settings(self):
    dlg = self.main.dialog_res.LoadDialog(self, 'IDD_DIALOG_LOCAL_G')
    rdo_gi = xrc.XRCCTRL(dlg, 'IDC_RDO_GI')
    rdo_gi_star = xrc.XRCCTRL(dlg, 'IDC_RDO_GI_STAR')
    rdo_row_stand = xrc.XRCCTRL(dlg, 'IDC_RDO_ROW_STAND')
    rdo_binary = xrc.XRCCTRL(dlg, 'IDC_RDO_BINARY')
    
    dlg.CenterOnScreen()
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return False
 
    gi_star = 0 #gi
    try:
        gi_star = rdo_gi_star.GetValue()
        binary = rdo_binary.GetValue()
    except:
        pass
    dlg.Destroy()
    return gi_star, binary
    
    
    