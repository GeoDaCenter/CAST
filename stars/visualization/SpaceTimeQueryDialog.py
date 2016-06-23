"""
The SpaceTime Query dialogs.

SpaceTimeQueryDialog is the ABSTRACT base query dialog. 
It provides a base GUI, which contains a group of FIELD 
query controls, a group of TIME query controls, and a
group of SPACE query controls.

TrendGraphQueryDialog, DensityMapQueryDialog,
LisaMapQueryDialog, MarkovLisaMapQueryDialog are inherited
classes. 

All inherited classes could have their own customized controls
by overwriting Add_Customized_Controls() function. They 
could generate their own customizied query function and 
data by overwriting gen_data_by_step() function. They
could call their own customized representing GUI by 
overwriting OnQuery() function.
"""
__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['SpaceTimeQueryDialog']

import re, os,random
from datetime import *
import wx
import pysal
import numpy as np

import stars
from stars.model.ShapeObject import CShapeFileObject 



class SpaceTimeQueryDialog(wx.Frame):
    """
    Dialog for all Space-Time querying needs.

    The wx.ID_OK button is binding with a specific function.
    Therefore, there's no need to close this query window
    before showing query result. Users don't need to re-enter
    all information in this query form, if they want a small
    chance on their query.

    If a Modal Dialog is needed, then use paremeter:
    modal=True, while creating this dialog instance.
    """

    def __init__(self, parent, title, points_data, isShowSpace=True, **kwargs):
        pos = (20,20)
        size = (360, 450)
        background_shps = []
        modal = False

        if kwargs.has_key('pos'):
            pos = kwargs['pos']
        if kwargs.has_key('size'):
            size = kwargs['size']
        if kwargs.has_key('background_shps'):
            background_shps = kwargs['background_shps']
        if kwargs.has_key('modal'):
            modal = kwargs['modal']
            
        if not isShowSpace:
            size = (size[0], size[1] -40) 
            
        wx.Frame.__init__(self, parent, -1, title, pos=pos, size=size)

        self.parent = parent
        try:
            self.SetIcon(self.parent.logo)
        except:
            pass
        self.isShowSpace = isShowSpace
        self.shp = self.points_data = points_data
        self.points = self.points_data.shape_objects
        self.dbf = self.points_data.dbf
        self.background_shps = background_shps
        self.width, self.height = self.Size

        # put default SPACE-TIME QUERY controls on a Panel
        self.panel = wx.Panel(self,-1)
        panel = self.panel
        
        # Time
        x2,y2 = 20, 8 
        wx.StaticBox(panel, -1, "Time:",pos=(x2,y2),size=(325,215))
        wx.StaticText(panel, -1, "Field:",pos =(x2+10,y2+32),size=(35,-1))
        self.cmbox_datefield = wx.ComboBox(panel, -1,"Date field", pos =(x2+100,y2+30),size=(90,-1), style=wx.CB_DROPDOWN)
        self.cmbox_timefield = wx.ComboBox(panel, -1,"Time field", pos =(x2+210,y2+30),size=(90,-1), style=wx.CB_DROPDOWN)
        x2,y2 = x2, y2+50
        wx.StaticText(panel, -1, "Time of Day:",pos =(x2+10,y2+23),size=(90,-1))
        self.cmbox_tod = wx.ComboBox(panel, -1,"00:00-23:59", pos =(x2+100,y2+18),size=(130,-1), style=wx.CB_DROPDOWN)
        self.btn_add_tod = wx.Button(panel, -1, "+", pos = (x2+235,y2+20), size=(25,-1))
        self.btn_remove_tod = wx.Button(panel, -1, "-", pos = (x2+260,y2+20), size=(25,-1))
        self.cmbox_tod.Enable(False)
        self.btn_add_tod.Enable(False)
        self.btn_remove_tod.Enable(False)
        x2,y2 = x2, y2+40
        wx.StaticText(panel, -1, "Step By:",pos =(x2+10,y2+20),size=(60,-1))
        if os.name == 'posix':
            self.textbox_step = wx.TextCtrl(panel,-1,"",pos=(x2+100,y2+20),size =(25,-1))
        else:
            self.textbox_step = wx.TextCtrl(panel,-1,"",pos=(x2+100,y2+16),size =(25,-1))
        self.cmbox_step = wx.ComboBox(panel, -1, "Day/Week/Month/Year", choices=["Day","Week","Month","Year"],pos =(x2+130,y2+17),size=(160,-1), style=wx.CB_DROPDOWN)
        self.textbox_step.Enable(False)
        self.cmbox_step.Enable(False)
        x2,y2 = x2,y2+40
        text_interval = wx.StaticText(panel, -1, "Interval:",pos =(x2+10,y2+20),size=(90,45))
        text_interval_start = wx.StaticText(panel, -1, "Start",pos =(x2+100,y2+20),size=(40,-1))
        self.itv_start_date = wx.DatePickerCtrl(panel, pos=(x2+140,y2+20), size=(150,-1), style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE )
        text_interval_end = wx.StaticText(panel, -1, "End",pos =(x2+100,y2+50),size=(27,-1))
        self.itv_end_date = wx.DatePickerCtrl(panel, pos=(x2+140,y2+50), size=(150,-1), style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE )
        self.itv_start_date.Enable(False)
        self.itv_end_date.Enable(False)
        
        x2,y2 = x2, y2 + 85
        
        # Space
        if isShowSpace:
            location_box = wx.StaticBox(self.panel, -1, "Space:",pos=(x2,y2),size=(325,56))
            bg_shp_list = [shp.name for shp in self.background_shps if shp.shape_type==stars.SHP_POLYGON]
            self.cmbox_location = wx.ComboBox(self.panel, -1, "",choices=bg_shp_list,pos=(x2+10,y2+20),size=(200,-1),style=wx.CB_DROPDOWN)
            self.add_space_btn = wx.BitmapButton(self.panel, -1, wx.BitmapFromImage(stars.OPEN_ICON_IMG),pos=(x2+218,y2+25),style=wx.NO_BORDER)
            x2,y2 = x2, y2 + 50
            
        # Data Filter
        x1,y1 = x2, y2 + 10
        wx.StaticBox(panel, -1, "Subset data:", pos=(x1,y1),size=(325,55))
        self.cmbox_queryfield = wx.ComboBox(panel, -1,"All fields", pos =(x1+10,y1+20),size=(140,-1), style=wx.CB_DROPDOWN)
        self.cmbox_queryrange = wx.ComboBox(panel, -1, "All range",pos =(x1+160,y1+20),size=(135,-1), style=wx.CB_DROPDOWN)
        self.cmbox_queryrange.Enable(False)
       
        # Buttons
        if os.name == 'posix':
            x2,y2 = x2, self.height - 55
        else:
            x2,y2 = x2, self.height - 74 

        self.btn_query = wx.Button(panel, wx.ID_OK, "Run",pos=(x2,y2),size=(90, 30))
        self.btn_save  = wx.BitmapButton(panel, -1, wx.BitmapFromImage(stars.SAVE_ICON_IMG),pos=(x2+95, y2+3), style=wx.NO_BORDER)
        self.btn_reset = wx.Button(panel, wx.ID_RESET, "Reset",pos=(x2+125,y2),size=(90, 30))
        self.btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel",pos=(x2+215,y2),size=(90, 30))

        self.btn_save.Enable(False)
        # Events
        self.Bind(wx.EVT_TEXT, self.OnStepChange, self.textbox_step)
        self.Bind(wx.EVT_COMBOBOX, self.OnStepBySelect, self.cmbox_step)
        self.Bind(wx.EVT_COMBOBOX, self.OnQueryFieldSelected, self.cmbox_queryfield)
        self.Bind(wx.EVT_COMBOBOX, self.OnQueryRangeInput, self.cmbox_queryrange)
        self.cmbox_queryrange.Bind(wx.EVT_TEXT_ENTER, self.OnQueryRangeInput)
        self.Bind(wx.EVT_COMBOBOX, self.OnDateFieldSelected, self.cmbox_datefield)
        self.Bind(wx.EVT_COMBOBOX, self.OnTimeFieldSelected, self.cmbox_timefield)
        self.Bind(wx.EVT_TEXT, self.OnTODInput, self.cmbox_tod)
        self.Bind(wx.EVT_BUTTON, self.OnAddTOD, self.btn_add_tod)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveTOD, self.btn_remove_tod)
        self.Bind(wx.EVT_BUTTON, self.OnQuery, self.btn_query)
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.btn_reset)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.btn_cancel)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnItvStartDateChanged, self.itv_start_date)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnItvEndDateChanged, self.itv_end_date)
        #self.Bind(wx.EVT_TEXT, self.OnItvDateText, self.itv_start_date)
        
        if isShowSpace:
            self.Bind(wx.EVT_BUTTON, self.OnAddSpace, self.add_space_btn)
        self.Bind(wx.EVT_BUTTON, self.OnSaveQueryToDBF, self.btn_save)
        self.init_query()
        self.Add_Customized_Controls()

    def OnReset(self,event):
        self.reset()
    
    def OnCancel(self,event):
        self.Close(True)
    
    def init_query(self):
        """
        Init query forms by dbf parameter
        """
        self.init_variables()
        
        self.cmbox_queryfield.Append('All fields')
        self.cmbox_queryrange.Append('All ranges')
        self.cmbox_datefield.Append('Date field')
        self.cmbox_timefield.Append('Time field')

        full_candidates = {}
        dt_candidates = {}
        
        for i,item in enumerate(self.dbf.header):
            full_candidates[item.lower()] = i
            if self.dbf.field_spec[i][0] != 'F':
                dt_candidates[item.lower()] = i
                
        for item in sorted(full_candidates.keys()):
            idx = full_candidates[item]
            self.cmbox_queryfield.Append(self.dbf.header[idx])
            
        for item in sorted(dt_candidates.keys()):
            idx = dt_candidates[item]
            self.cmbox_timefield.Append(self.dbf.header[idx])
            self.cmbox_datefield.Append(self.dbf.header[idx])

        if self.shp.name in stars.ST_QUERY_SETTINGS:
            self.cust_setup = stars.ST_QUERY_SETTINGS[self.shp.name]
            
            if 'datefield' in  self.cust_setup:
                datefield = self.cust_setup['datefield']
                if datefield != "" and datefield != "Date field":
                    self.cmbox_datefield.SetStringSelection(self.cust_setup['datefield'])
               
                    self.date_field_idx = self.dbf.header.index(datefield)
                
                    if 'datefieldregex' in self.cust_setup:
                        cust_date_format = self.cust_setup['datefieldregex']
                        self.all_dates = self.dbf.by_col(datefield, ctype='datetime',ctype_info= cust_date_format)
                    else:
                        self.all_dates = self.dbf.by_col(datefield, ctype='datetime')
                    
                    
                self.dbf_start_date = min(self.all_dates)
                self.dbf_end_date = max(self.all_dates)
                    
                if 'interval_start' in self.cust_setup:
                    start_date_dmy = self.cust_setup['interval_start']
                    self.itv_start_date.SetValue(wx.DateTimeFromDMY(*start_date_dmy))
                    self.start_query_date = self._wxdate2pydate(self.itv_start_date.GetValue())
                    self.itv_start_date.Enable(True)
                    
                if 'interval_end' in self.cust_setup:
                    end_date_dmy = self.cust_setup['interval_end']
                    self.itv_end_date.SetValue(wx.DateTimeFromDMY(*end_date_dmy))
                    self.end_query_date =  self._wxdate2pydate(self.itv_end_date.GetValue())
                    self.itv_end_date.Enable(True)
                    
            if 'timefield' in self.cust_setup:
                tf_value = self.cust_setup['timefield']
                if tf_value != "" and tf_value != "Time field":
                    self.cmbox_timefield.SetStringSelection(self.cust_setup['timefield'])
                    self.time_field_idx  = self.dbf.header.index(self.cust_setup['timefield'])
               
                    self.cmbox_tod.Enable(True)
                
                    if 'tod' in self.cust_setup:
                        for item in self.cust_setup['tod']:
                            self.cmbox_tod.Append(item)
                
            if 'queryfield' in self.cust_setup:
                self.query_field = self.cust_setup['queryfield']
                if self.query_field != "" and self.query_field.lower() != "all fields":
                    self.cmbox_queryfield.SetValue(self.query_field)
                    self.query_field_idx = self.dbf.header.index(self.query_field)
                       
                    self.cmbox_queryfield.Enable(True)
                    self.cmbox_queryrange.Enable(True)
                        
                    if 'queryrange' in self.cust_setup:
                        self.query_range = self.cust_setup['queryrange']
                        if self.query_range != "" and self.query_range.lower() != "all ranges":
                            self.cmbox_queryrange.SetValue(self.query_range)
                    
            if 'stepby' in self.cust_setup:
                self.step_by = self.cust_setup['stepby']
                if self.step_by != "":
                    self.cmbox_step.SetValue(self.step_by)
                    self.cmbox_step.Enable(True)
                
            if 'step' in self.cust_setup:
                self.step = self.cust_setup['step']
                if self.step != "":
                    self.textbox_step.SetValue(str(self.step))
                    self.textbox_step.Enable(True)
                
        else:
            self.cmbox_queryfield.SetSelection(0)
            self.cmbox_queryrange.SetSelection(0)
            self.cmbox_datefield.SetSelection(0)
            self.cmbox_timefield.SetSelection(0)
    
            self.cmbox_step.SetValue('Day/Week/Month/Year')
            self.cmbox_tod.SetValue('00:00-23:59')
            
            
            self.cust_setup = stars.ST_QUERY_SETTINGS[self.shp.name] = dict()
        
    def init_variables(self):
        # Variables
        self.query_field = "All fields"
        self.query_field_idx = -1
        self.time_field_idx = -1
        self.date_field_idx = -1
        self.all_dates= None
        self.query_range = None
        self.query_date = None
        self.background_shp_idx = -1
        self.current_selected = range(self.dbf.n_records)
        self.query_data = None
        self.start_query_date = None
        self.end_query_date = None

    def reset(self):
        self.cmbox_datefield.SetSelection(0)
        self.cmbox_timefield.SetSelection(0)
        self.cmbox_queryfield.SetSelection(0)
        self.cmbox_queryfield.SetSelection(0)
        self.cmbox_tod.Clear()
        self.cmbox_tod.SetValue('00:00-23:59')
        self.cmbox_tod.Enable(False)
        self.cmbox_step.SetValue('Day/Week/Month/Year')
        self.cmbox_step.Enable(False)
        self.textbox_step.SetValue('')
        self.textbox_step.Enable(False)
        self.start_query_date = datetime.now()
        self.end_query_date = datetime.now()
        self.itv_start_date.SetValue(self._pydate2wxdate(self.start_query_date))
        self.itv_end_date.SetValue(self._pydate2wxdate(self.end_query_date))
        self.itv_start_date.Enable(False)
        self.itv_end_date.Enable(False)
        self.init_variables()
        
        self.cust_setup = dict()
        
    def _pydate2wxdate(self,date): 
        """
        Module function: convert from Python Date
        to wx.Date type
        """
        tt = date.timetuple() 
        dmy = (tt[2], tt[1]-1, tt[0]) 
        return wx.DateTimeFromDMY(*dmy) 

    def _wxdate2pydate(self,date): 
        """
        Module function: convert from wx.Date
        to Python Date type
        """
        if date.IsValid(): 
            ymd = map(int, date.FormatISODate().split('-')) 
            return datetime(*ymd) 
        else: 
            return None

    def OnStepChange(self,event):
        try:
            self.step = int(event.GetString())
            self.cust_setup['step'] = self.step
        except:
            pass
                        
    def OnStepBySelect(self, event):
        self.step_by = event.GetString()
        self.cust_setup['stepby'] = self.step_by
        
        
    def OnQueryFieldSelected(self, event):
        """
        If one dbf field selected, all its unique values
        should be listed under combobox QueryRange
        """
        self.query_field= event.GetString()
        if self.query_field == 'All fields':
            self.cmbox_queryrange.Clear()
            self.cmbox_queryrange.Append("All ranges")
            return

        self.query_field_idx = self.dbf.header.index(self.query_field)

        values = self.dbf.by_col(self.query_field)
        if values.count(None) or values.count(''):
            self.ShowMsgBox("This field has undefined values (e.g. empty or <NULL>), please specify a different field.")
            return

        unique_values = set(values)

        # show them in combobox
        self.cmbox_queryrange.Clear()
        self.cmbox_queryrange.Append("All ranges")
        for val in unique_values:
            self.cmbox_queryrange.Append("%s" % val)
        self.cmbox_queryrange.Enable(True)
        self.cmbox_queryrange.SetSelection(0)
        
        self.cust_setup['queryfield'] = self.query_field

    def OnAddSpace(self, event):
        """
        User can add a (1+) shapefile to current space combobox selections,
        in case of user forget to open it before SpaceTimeQuery.
        """
        dlg = wx.FileDialog(self, message="Choose a file", 
                            wildcard="ESRI shape file (*.shp)|*.shp|All files (*.*)|*.*",
                            style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            pth = dlg.GetPath()
            shp_name = pth
            if shp_name.find('/') >=0:
                shp_name = pth.split('/')[-1][:-4]
            elif shp_name.find('\\') >=0:
                shp_name = pth.split('\\')[-1][:-4]
            selected_idx = self.cmbox_location.FindString(shp_name)
            if selected_idx>=0:
                self.cmbox_location.Select(selected_idx)
            else:
                shp = CShapeFileObject(pth)
                #self.parent.shapefiles.append(shp)
                self.background_shps.append(shp)
                # append them in the space combobox
                pos = self.cmbox_location.Append(shp_name)
                self.cmbox_location.SetSelection(pos)
        dlg.Destroy()
            
    def EvtChar(self, event):
        event.Skip()
        
    def OnQueryRangeInput(self, event):
        """
        User can input value range, in the forms
        1) inequations: > < ==
        2) list of matches: A,B,C
        """
        self.query_range = event.GetString() 
        self.cust_setup['queryrange'] = self.query_range

    def OnDateFieldSelected(self, event):
        """
        If Field of Date is selecte, then Date related query
        input and selection controls will be enabled.
        """
        try:
            col_name = event.GetString()
            try:
                self.all_dates = self.dbf.by_col(col_name, ctype='datetime')
            except:
                # let user specify the date format
                tip = 'The variable (%s) has been selected is not a valid DATE type. Please specify its python date format here.' % col_name
                format_dlg = wx.TextEntryDialog(
                    self, 
                    tip + """
                    
You can use the following symbols to describe the date format of the selected variable. For example:
    %Y 4-digit year (e.g. 1999)
    %y 2-digit year (e.g. 99) 
    %m 2-digit month(e.g. 01)
    %d 2-digit day of month (e.g. 02)
  
CAST accepts all python date formats. For example:
    1999              %Y
    2000-1-31     %Y-%m-%d
    1/31/00         %m/%d/%y
    1/31/2000     %m/%d/%Y
    
For all python date formats, please see: http://docs.python.org/2/library/time.html
                    """,
                    "","")
                if format_dlg.ShowModal() == wx.ID_OK:
                    cust_date_format = format_dlg.GetValue()
                    self.all_dates = self.dbf.by_col(col_name, ctype='datetime',ctype_info= cust_date_format)
                    
                    self.cust_setup['datefieldregex'] = cust_date_format
                else:
                    # reset date field
                    self.cmbox_datefield.SetSelection(0)
                    return
                
            if len(self.all_dates) == 0:
                self.ShowMsgBox("There are no records in the DBF file.")
                return

            self.date_field_idx = self.dbf.header.index(col_name)
            self.dbf_start_date = min(self.all_dates)
            self.dbf_end_date = max(self.all_dates)

            #self.date.Enable(True)
            self.textbox_step.Enable(True)
            self.cmbox_step.Enable(True)
            self.itv_start_date.Enable(True)
            self.itv_end_date.Enable(True)

            start_date = self.dbf_start_date.timetuple()
            start_date_dmy = (start_date[2],start_date[1]-1,start_date[0])
            self.itv_start_date.SetValue(wx.DateTimeFromDMY(*start_date_dmy))
            end_date = self.dbf_end_date.timetuple()
            end_date_dmy = (end_date[2],end_date[1]-1,end_date[0])
            self.itv_end_date.SetValue(wx.DateTimeFromDMY(*end_date_dmy))
            
            self.start_query_date = self._wxdate2pydate(self.itv_start_date.GetValue())
            self.end_query_date =  self._wxdate2pydate(self.itv_end_date.GetValue())

            #self.date.SetValue(wx.DateTimeFromDMY(*start_date_dmy))
            #self.query_date = wx.DateTimeFromDMY(*start_date_dmy)
            
            self.cust_setup['datefield'] = col_name
            self.cust_setup['interval_start'] = start_date_dmy
            self.cust_setup['interval_end'] = end_date_dmy
            
        except:
            self.ShowMsgBox("There is a problem with the data in the selected field. Please check data or reselect.")
            # reset date field
            self.cmbox_datefield.SetSelection(0)

    def OnTimeFieldSelected(self, event):
        """
        If Time-Field is selecte, then TOD related query
        input and selection controls will be enabled.
        """
        col_name = event.GetString()
        self.time_field_idx = self.dbf.header.index(col_name)

        self.cmbox_tod.Enable(True)
        self.btn_add_tod.Enable(True)
        self.btn_remove_tod.Enable(True)
        
        self.cust_setup['timefield'] = col_name
        self.cust_setup['tod'] = []
        
    def OnItvStartDateChanged(self,event):
        """
        Interval of dates selected.
        """
        try:
            self.start_query_date = self._wxdate2pydate(event.Date)
            
            start_date = self.start_query_date.timetuple()
            start_date_dmy = (start_date[2],start_date[1]-1,start_date[0])
            self.cust_setup['interval_start'] = start_date_dmy
        except:
            pass

    def OnItvEndDateChanged(self,event):
        """
        Interval of dates selected.
        """
        try:
            self.end_query_date = self._wxdate2pydate(event.Date)
            
            end_date = self.end_query_date.timetuple()
            end_date_dmy = (end_date[2],end_date[1]-1,end_date[0])
            self.cust_setup['interval_end'] = end_date_dmy
        except:
            pass
        
    def OnTODInput(self, event):
        """
        If Time-Of-Day is input, set it to in-class
        varible for Add/Remove button using.
        """
        self.input_tod = event.GetString()

    def OnAddTOD(self, event):
        """
        Add the user inpupt TOD to the TOD-Combobox
        """
        try:
            # check input TOD
            input_tod = self.cmbox_tod.GetValue()
            tod_regex = '^[0-9]{0,2}(\:[0-9]{0,2})?\-[0-9]{0,2}(\:[0-9]{0,2})?$'
            if re.search(tod_regex, input_tod):
                t_start, t_end = input_tod.split('-')
                if t_start.find(':') < 0 and len(t_start) <= 2: 
                    t_start = t_start + ":00"
                if t_end.find(':') < 0 and len(t_end) <= 2:
                    t_end = t_end + ":00" 
                input_tod = t_start + "-" + t_end
                self.cmbox_tod.Append(input_tod)
                self.cmbox_tod.SetValue("")
                
                self.cust_setup['tod'].append(input_tod)
            else:
                self.ShowMsgBox("Incorrect time-of-day format. (e.g. HH:MM or HHMM)")
        except:
            self.ShowMsgBox("Empty time-of-day or incorrect time-of-day format. (e.g. HH:MM or HHMM)")

    def OnRemoveTOD(self, event):
        """
        Remove user-input TOD from ComboBox
        """
        try:
            current_tod = self.cmbox_tod.GetValue()
            tod_list = self.cmbox_tod.GetItems()
            tod_list.remove(current_tod)

            self.cmbox_tod.Clear()
            self.cmbox_tod.AppendItems(tod_list)
            
            self.cust_setup['tod'].remove(current_tod)
        except:
            # not a valid TOD item
            self.ShowMsgBox("Not a valid time-of-day item.")

    def ShowMsgBox(self,msg,mtype='Warning',micon=wx.ICON_WARNING):
        dlg = wx.MessageDialog(self, msg, mtype, wx.OK|micon)
        dlg.ShowModal()
        dlg.Destroy()
        
    def _filter_by_query_field(self):
        """
        filter  by QUERY FIELD and QUERY RANGE
        """
        self.query_range = self.cmbox_queryrange.GetValue()
        
        # no field filtering needed
        if self.query_field_idx < 0 or len(self.query_range) <=0:
            return
        
        if self.query_field.lower() == "all fields" or \
           self.query_range.lower() == "all ranges":
            return 

        queryField = self.query_field
        queryRange = self.query_range
        column_idx = self.dbf.column_index(queryField)
        
        self.current_selected = []
        if queryRange.find(',') < 0 and \
           queryRange.find('>') < 0 and \
           queryRange.find('=') < 0 and \
           queryRange.find('<') < 0:
            # directly filter DBF records 
            if self.dbf.field_spec[column_idx][0] == 'N':
                queryRange = int(queryRange)
            elif self.dbf.field_spec[column_idx][0] == 'F':
                queryRange = float(queryRange)
                
            column_data = self.dbf.by_col(queryField)
            for i in range(self.dbf.n_records):
                if column_data[i] == queryRange:
                    self.current_selected.append(i)
            return

        # handle some special customized ranges
        try:
            conditions = queryRange.split(',')
            column_data = self.dbf.by_col(queryField)
            for i,column_item in enumerate(column_data):
                isMatch = True
                for cond in conditions:
                    cond = cond if queryRange.find('>') > -1 or queryRange.find('=') > -1 or queryRange.find('<') > -1 \
                         else "=" + cond
                    if eval(str(column_item)+cond) == False:
                        isMatch = False
                        break
                if isMatch:
                    self.current_selected.append(i)
        except Exception as err:
            self.ShowMsgBox("Fail to query: " + str(err.message))
            return

    def _filter_by_date(self):
        """
        filter by one specific Date
        """
        if self.query_date != None and self.query_date.IsValid():# and self.date.GetValue().IsValid():
            query_date = self._wxdate2pydate(self.query_date)
            if query_date < self.dbf_start_date or \
               query_date > self.dbf_end_date:
                # no need to filter data
                return

            new_current_selected = []
            for i in self.current_selected:
                rec = self.dbf.read_record(i)
                _date = rec[self.date_field_idx]
                if _date == query_date:
                    new_current_selected.append(i)
            self.current_selected = new_current_selected

    def _filter_by_date_interval(self):
        """
        filter by Date interval.

        If Query Date is specified, then
        the interval filter should be not available.
        """
        if self.date_field_idx >= 0 and self.query_date == None:
            start_date = self.start_query_date #self.itv_start_date.GetValue())
            end_date   = self.end_query_date   #self.itv_end_date.GetValue())

            if start_date == self.dbf_start_date and end_date == self.dbf_end_date:
                # user didn't specify start_date and end_date,
                # , so there's no need to filter data
                return

            new_current_selected = []
            for i in self.current_selected:
                _date = self.all_dates[i]
                if start_date <= _date <= end_date:
                    new_current_selected.append(i)
            self.current_selected = new_current_selected

    def _filter_by_tod(self):
        """
        filter by TIME TOD 
        """
        try:
            if self.time_field_idx < 0:
                return True
            
            tod_list = self.cmbox_tod.GetItems() 
            if len(tod_list) <= 0:
                return True 
            
            _tod_list = []
            
            for tod in tod_list:
                t_start, t_end = tod.split('-') 
                if t_start.find(":") > 0: 
                    t_start = t_start.replace(":","")
                if t_end.find(":") > 0: 
                    t_end = t_end.replace(":","")
                t_start = int(t_start)
                t_end = int(t_end)
                _tod_list.append((t_start,t_end))
                
            new_current_selected = []
            
            for i in self.current_selected:
                rec = self.dbf.read_record(i)
                _time = int(rec[self.time_field_idx])
                
                for t_start, t_end in _tod_list:
                    if t_start <= _time <= t_end:
                        new_current_selected.append(i)
                        
            self.current_selected = list(set(new_current_selected))
            return True
                        
        except Exception as err:
            message = "Fail to filter by time. Time format shoule be HHMM (integer). " + str(err.message)
            dlg = wx.MessageDialog(self, message, 'Warning', wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def _check_space_input(self):
        try:
            shp_name = self.cmbox_location.GetValue()
            if len(shp_name) < 0:
                self.ShowMsgBox("Space is empty.")
                return False
            for i,shp in enumerate(self.background_shps):
                if shp.name == shp_name:
                    self.background_shp_idx = i
            return True
        except Exception as err:
            self.ShowMsgBox("Please respecify space shapefile. " + str(err.message))
            return False

    def _check_time_itv_input(self):
        try:
            step = self.textbox_step.GetValue()
            step_by = self.cmbox_step.GetValue()
   
            if len(step) <= 0:
                self.ShowMsgBox("Step By field is empty.")
                return False
            
            if step_by!="Day" and step_by!="Week" and \
               step_by!="Month" and step_by!="Year":
                self.ShowMsgBox("Step By field is not selected.")
                return False
   
            self.step = int(step)
            self.step_by = step_by
            
            self.cust_setup['step'] = step
            self.cust_setup['step_by'] = step_by
            
            if self.step <= 0:
                self.ShowMsgBox("Step By should be larger than 0.")
                return False
            return True
        except Exception as err:
            self.ShowMsgBox("Time interval is not valid. " + str(err.message))
            return False

    #----------------------------------
    # Belows are abstract functions
    # , that inherited classes can have
    # their own implementation to extend
    # Space-Time query.
    # ----------------------------------
    def Add_Customized_Controls(self):
        """
        This function could be overwritten by inherited
        classes for adding more customized controls to 
        this Sace-Time Query Dialog.
        """
        pass

    def OnQuery(self, event):
        """
        This function will be executed when user click 
        the "QUERY" button. 
        """
        pass


    def OnSaveQueryToDBF(self, event):
        """
        """
        pass

    def draw_space_in_buffer(self, space_shp, width=6000,height=6000):
        """
        Function for fast space-time query: how many points
        sit in each polygon
        """
        from stars.visualization.maps.BaseMap import PolygonLayer
        from stars.visualization.utils import View2ScreenTransform,DrawPurePoints
        # specify different color for each polygon
        poly_color_dict = {}
        n = len(space_shp)
        
        if n > 10000:
            width = 9000
            height = 9000
        
        id_group = []
        color_group = []
        color_range = 254*254*254 - 1
        used_color = {}
        for i in range(n):
            color_idx = random.randint(1,color_range)
            while color_idx in used_color: 
                color_idx = random.randint(1,color_range)
            used_color[color_idx] = True
            r = color_idx & 255
            g = (color_idx>>8) & 255
            b = (color_idx>>16) & 255
            id_group.append([i])
            color_group.append(wx.Color(r,g,b))
            poly_color_dict[(r,g,b)] = i
            
        # draw polygon to an empty_buffer
        polygon_layer = PolygonLayer(self, space_shp)
        polygon_layer.set_edge_color(wx.Color(0,0,0,0))
        polygon_layer.set_data_group(id_group)
        polygon_layer.set_fill_color_group(color_group)
        #polygon_layer.set_edge_color_group(color_group)
        
        view = View2ScreenTransform(space_shp.extent, width, height)
        buffer = wx.EmptyBitmap(width, height)
        dc = wx.BufferedDC(None, buffer)
        dc.Clear()
        polygon_layer.draw(dc, view, drawRaw=True)
        
        """
        _points = []
        for p in points: 
            x,y = view.view_to_pixel(p[0],p[1])
            x,y = int(round(x)), int(round(y))
            _points.append((x,y))
        DrawPurePoints(dc, _points)
        """
        bmp = wx.ImageFromBitmap(buffer)
        #buffer.SaveFile('test.bmp',wx.BITMAP_TYPE_BMP)
        return bmp,view,poly_color_dict
    
    def gen_date_by_step(self):
        """
        Can be overwritten to generate different data,
        such as: Trend data, Density data, Markov Lisa
        """
        from stars.visualization.utils import GetIntervalStep
        
        step               = self.step
        step_by            = self.step_by
        background_shp_idx = self.background_shp_idx    
        background_shp     = self.background_shps[background_shp_idx]
        
        if background_shp.shape_type != stars.SHP_POLYGON:
            self.ShowMsgBox("Background shapefile should be POLYGON.")
            return None
        
        if not pysal.cg.standalone.bbcommon(background_shp.extent, self.points_data.extent):
            self.ShowMsgBox("Mismatch in spatial extent of point and polygon shapefiles.")
            return None
        
        start_date      = self._wxdate2pydate(self.itv_start_date.GetValue())
        end_date        = self._wxdate2pydate(self.itv_end_date.GetValue())
        total_steps     = GetIntervalStep(end_date, start_date, step, step_by)
        if total_steps <= 0:
            self.ShowMsgBox("Start and end dates are not valid.")
            return None
        elif total_steps == 1:
            self.ShowMsgBox("Total steps should be larger than 1.")
            return None
        elif total_steps > 48:
            dlg = wx.MessageDialog(
                self,
                "Total steps is %s, it may take a lot of memory and time. Do you want to continue?"%total_steps,
                "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_OK:
                return None
            
        self.start_date = start_date
        self.end_date   = end_date
        
        return_data_dict = dict([(i,np.zeros(total_steps)) for i in range(len(background_shp))]) 
        
        # displaying progress
        n = len(self.current_selected)
        itv = n / 5
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Space-time query for dynamic graph/map... ",
            maximum = n+1,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        progress_dlg.CenterOnScreen()
        
        # check which point is in which polygon
        bmp,view,poly_color_dict = self.draw_space_in_buffer(background_shp)
        not_sure_points = []
        is_valid_query = False
        
        for count,j in enumerate(self.current_selected):
            if count % itv == 0:
                progress_dlg.Update(count)
                
            _date = self.all_dates[j]
            interval_idx = GetIntervalStep(_date, start_date, step, step_by)-1
            
            p = self.points[j]
            x,y = view.view_to_pixel(p[0],p[1])
            x,y = int(round(x)), int(round(y))
           
            if x < 0 or y < 0 or x >= bmp.Width or y >= bmp.Height:
                continue
            
            r = bmp.GetRed(x,y)
            g = bmp.GetGreen(x,y)
            b = bmp.GetBlue(x,y)
            
            if r==255 and g==255 and b==255:
                continue
            
            if (r,g,b) in poly_color_dict:
                poly_id = poly_color_dict[(r,g,b)]
                poly_id_cnt = 0
                for offset_x in range(-1,2):
                    for offset_y in range(-1,2):
                        n_x = x + offset_x
                        n_y = y + offset_y
                        if n_x<0 or n_y < 0 or n_x >= bmp.Width or n_y >= bmp.Height:
                            continue
                        n_r = bmp.GetRed(n_x,n_y)
                        n_g = bmp.GetGreen(n_x,n_y)
                        n_b = bmp.GetBlue(n_x,n_y)
                        if n_r==r and n_g==g and n_b==b:
                            poly_id_cnt += 1
                if poly_id_cnt > 3:
                    return_data_dict[poly_id][interval_idx] += 1
                    is_valid_query = True
                else:
                    # this case, the color of border line of severl polygons
                    # accidentally equals to an existing color code
                    not_sure_points.append(j)
             
                
            else:
                # check if this pixel is sitting on the boarder line
                # pick up the color code, in the case that this is 
                # the boarder line of only one polygon
                candidate_color = None
                candidate_color_cnt = 0
                for offset_x in range(-1,2):
                    for offset_y in range(-1,2):
                        n_x = x + offset_x
                        n_y = y + offset_y
                        if n_x < 0 or n_y < 0 or n_x >= bmp.Width or n_y >= bmp.Height:
                            continue
                        n_r = bmp.GetRed(n_x,n_y)
                        n_g = bmp.GetGreen(n_x,n_y)
                        n_b = bmp.GetBlue(n_x,n_y)
                       
                        local_color = (n_r,n_g,n_b)
                        if poly_color_dict.has_key(local_color):
                            candidate_color = local_color
                            candidate_color_cnt += 1
                        if candidate_color_cnt > 1:
                            break
                        
                if candidate_color_cnt == 1:
                    #todo: add a real test (poly_id, p)
                    poly_id = poly_color_dict[candidate_color]
                    return_data_dict[poly_id][interval_idx] += 1
                    is_valid_query = True
                else:
                    not_sure_points.append(j)
                    
        
        if len(not_sure_points)>0:
            query_points = [self.points[i] for i in not_sure_points]
            poly_ids = background_shp.test_point_in_polygon(query_points)
            
            for i, pid in enumerate(not_sure_points):
                if poly_ids[i] >=0:
                    _date = self.all_dates[pid]
                    interval_idx = GetIntervalStep(_date, start_date, step, step_by)-1
                    return_data_dict[poly_ids[i]][interval_idx] += 1
                    is_valid_query = True
            
        progress_dlg.Update(n+1)
        progress_dlg.Destroy()        
       
        if is_valid_query == False:
            self.ShowMsgBox("No point found in any polygon.")
            return None
        
        return background_shp, return_data_dict
    
    def gen_date_by_step_old_classic(self):
        """
        generate trend data by STEP
        This is the old and slow version
        """
        from stars.visualization.utils import GetIntervalStep
        
        step = self.step
        step_by = self.step_by
        background_shp_idx = self.background_shp_idx    
        
        background_shp = self.background_shps[background_shp_idx]
        if background_shp.shape_type != stars.SHP_POLYGON:
            self.ShowMsgBox("Background shapefile should be POLYGON.")
            return None
        
        start_date = self._wxdate2pydate(self.itv_start_date.GetValue())
        end_date   = self._wxdate2pydate(self.itv_end_date.GetValue())
        total_steps = GetIntervalStep(end_date, start_date, step, step_by)
      
        if total_steps <= 1:
            self.ShowMsgBox("Please choose a valid time step to generate more than 2 time intervals.")
            return None
            
        self.start_date = start_date
        self.end_date = end_date
        
        # displaying progress
        n = len(self.current_selected)
        itv = n / 5
        progress_dlg = wx.ProgressDialog(
            "Progress",
            "Space-time query for dynamic trend graph/maps.. ",
            maximum = n,
            parent=self,
            style = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        progress_dlg.CenterOnScreen()
        
        # use kd-tree from centroids
        kdtree = background_shp.get_kdtree_locator()
        num_inside = 0
        return_data_dict = dict([(i,np.zeros(total_steps))
                                for i in range(len(background_shp))]) 
        for count,j in enumerate(self.current_selected):
            if count % itv == 0:
                progress_dlg.Update(count +1)
                
            _date = self.all_dates[j]
            interval_idx = GetIntervalStep(_date, start_date, step, step_by) -1
            
            # test if this point sits inside its nearest polygon
            p = self.points[j]
            nn = kdtree.query(p, k=5)
            for id in nn[1]:
                poly_id = background_shp.get_kdtree_polyid(id)
                poly = pysal.cg.Polygon(background_shp.shape_objects[poly_id])
                ret = pysal.cg.get_polygon_point_intersect(poly, p)
                if ret != None:
                    # test success: this point sits in current polygon
                    return_data_dict[poly_id][interval_idx] += 1
                    num_inside += 1
                    break
        #print "o;d", n - num_inside 
        progress_dlg.Update(n)
        progress_dlg.Destroy()        
        
        return background_shp, return_data_dict
