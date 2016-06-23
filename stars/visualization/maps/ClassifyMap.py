"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ["ClassifyMapFactory", "ClassifyMap"]

import math
import wx
import numpy as np
import pysal

import stars
from stars.visualization import *
from ShapeMap import ShapeMap, ColorSchema

class ClassifyMapFactory():
    def __init__(self, data, **kwargs):
        self.data = data
        self.params = kwargs
        
    def pick_color_set(self, coltype, ncolor, reversed=False):
        colpos = [0, 0, 0, 0, 3, 7, 12, 18, 25, 33, 42] #11
       
        # sequential
        Color1 = [
            wx.Colour(255, 247, 188), wx.Colour(254, 196, 79), wx.Colour(217, 95, 14),
            wx.Colour(255, 255, 212), wx.Colour(254, 217, 142), wx.Colour(254, 153, 41),
            wx.Colour(204, 81, 2),
            wx.Colour(255, 255, 212), wx.Colour(254, 217, 142), wx.Colour(254, 153, 41),
            wx.Colour(217, 95, 14), wx.Colour(153, 52, 4),
            wx.Colour(255, 255, 212), wx.Colour(254, 227, 145), wx.Colour(254, 196, 79),
            wx.Colour(254, 153, 41), wx.Colour(217, 95, 14), wx.Colour(153, 52, 4),
            wx.Colour(255, 255, 212), wx.Colour(254, 227, 145), wx.Colour(254, 196, 79),
            wx.Colour(254, 153, 41), wx.Colour(236, 112, 20), wx.Colour(204, 81, 2),
            wx.Colour(140, 51, 5),
            wx.Colour(255, 255, 229), wx.Colour(255, 247, 188), wx.Colour(254, 227, 145),
            wx.Colour(254, 196, 79), wx.Colour(254, 153, 41), wx.Colour(236, 112, 20),
            wx.Colour(204, 81, 2), wx.Colour(140, 51, 5),
            wx.Colour(255, 255, 229), wx.Colour(255, 247, 188), wx.Colour(254, 227, 145),
            wx.Colour(254, 196, 79), wx.Colour(254, 153, 41), wx.Colour(236, 112, 20),
            wx.Colour(204, 81, 2), wx.Colour(153, 52, 4), wx.Colour(102, 46, 8),
            wx.Colour(255, 255, 229), wx.Colour(255, 247, 188), wx.Colour(254, 227, 145),
            wx.Colour(254, 196, 79), wx.Colour(254, 153, 41), wx.Colour(236, 112, 20),
            wx.Colour(204, 81, 2), wx.Colour(153, 52, 4), wx.Colour(120, 46, 8),
            wx.Colour(102, 46, 8)
        ]
        # Diverge
        Color2 = [ 
            wx.Colour(145, 191, 219), wx.Colour(255, 255, 191), wx.Colour(252, 141, 89),
            wx.Colour(44, 123, 182), wx.Colour(171, 217, 233), wx.Colour(253, 174, 97),
            wx.Colour(215, 25, 28),
            wx.Colour(44, 123, 182), wx.Colour(171, 217, 233), wx.Colour(255, 255, 191),
            wx.Colour(253, 174, 97), wx.Colour(215, 25, 28),
            wx.Colour(69, 117, 180), wx.Colour(145, 191, 219), wx.Colour(224, 243, 248),
            wx.Colour(254, 224, 144), wx.Colour(252, 141, 89), wx.Colour(215, 61, 41),
            wx.Colour(69, 117, 180), wx.Colour(145, 191, 219), wx.Colour(224, 243, 248),
            wx.Colour(255, 255, 191),
            wx.Colour(254, 224, 144), wx.Colour(252, 141, 89), wx.Colour(215, 61, 41),
            wx.Colour(69, 117, 180), wx.Colour(116, 173, 209), wx.Colour(171, 217, 233),
            wx.Colour(224, 243, 248), wx.Colour(254, 224, 144), wx.Colour(253, 174, 97),
            wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(69, 117, 180), wx.Colour(116, 173, 209), wx.Colour(171, 217, 233),
            wx.Colour(224, 243, 248), wx.Colour(255, 255, 191), wx.Colour(254, 224, 144),
            wx.Colour(253, 174, 97), wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(49, 54, 149), wx.Colour(69, 117, 180), wx.Colour(116, 173, 209),
            wx.Colour(171, 217, 233), wx.Colour(224, 243, 248), wx.Colour(254, 224, 144),
            wx.Colour(253, 174, 97), wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(173, 0, 49)
        ]
        # Diverge
        Color3 = [
            wx.Colour(145, 191, 219), wx.Colour(255, 255, 191), wx.Colour(252, 141, 89),
            wx.Colour(44, 123, 182), wx.Colour(171, 217, 233), wx.Colour(253, 174, 97),
            wx.Colour(215, 25, 28),
            wx.Colour(44, 123, 182), wx.Colour(171, 217, 233), wx.Colour(255, 255, 191),
            wx.Colour(253, 174, 97), wx.Colour(215, 25, 28),
            wx.Colour(215, 61, 41), wx.Colour(252, 141, 89), wx.Colour(254, 224, 139),
            wx.Colour(230, 245, 152), wx.Colour(153, 213, 148), wx.Colour(43, 131, 186),
            wx.Colour(69, 117, 180), wx.Colour(145, 191, 219), wx.Colour(224, 243, 248),
            wx.Colour(255, 255, 191),
            wx.Colour(254, 224, 144), wx.Colour(252, 141, 89), wx.Colour(215, 61, 41),
            wx.Colour(69, 117, 180), wx.Colour(116, 173, 209), wx.Colour(171, 217, 233),
            wx.Colour(224, 243, 248), wx.Colour(254, 224, 144), wx.Colour(253, 174, 97),
            wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(69, 117, 180), wx.Colour(116, 173, 209), wx.Colour(171, 217, 233),
            wx.Colour(224, 243, 248), wx.Colour(255, 255, 191), wx.Colour(254, 224, 144),
            wx.Colour(253, 174, 97), wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(49, 54, 149), wx.Colour(69, 117, 180), wx.Colour(116, 173, 209),
            wx.Colour(171, 217, 233), wx.Colour(224, 243, 248), wx.Colour(254, 224, 144),
            wx.Colour(253, 174, 97), wx.Colour(244, 109, 67), wx.Colour(215, 61, 41),
            wx.Colour(173, 0, 49)
        ]

        color_group = [None]*ncolor # size=ncolor , wxBLACK
        
        if not reversed:
            #switch (coltype) {
            if coltype == 1:
                for i in range(ncolor):
                    color_group[i] = Color1[colpos[ncolor] + i]
            elif coltype == 2:
                for i in range(ncolor):
                    color_group[i] = Color2[colpos[ncolor] + i]
            elif coltype == 3:
                for i in range(ncolor):
                    color_group[i] = Color3[colpos[ncolor] + i]
        else:
            if coltype == 1:
                for i in range(ncolor):
                    color_group[i] = Color1[colpos[ncolor] + ncolor - i -1]
            elif coltype == 2:
                for i in range(ncolor):
                    color_group[i] = Color2[colpos[ncolor] + ncolor - i -1]
            elif coltype == 3:
                for i in range(ncolor):
                    color_group[i] = Color3[colpos[ncolor] + ncolor - i -1]
                    
        return color_group
           
        
    def _get_color_schema_by_k(self, k):
        r_min, r_max = 150, 254
        g_min, g_max = 80, 255
        b_min, b_max = 19,  213
        _k = float(k)
        color_group = [wx.Colour(int(r_max - i*(r_max-r_min)/(_k)),
                                 int(g_max - i*(g_max-g_min)/(_k)),
                                 int(b_max - i*(b_max-b_min)/(_k))) 
                       for i in range(k)]
        return color_group
   
    def _get_default_color_schema(self,k):
        color_group = [wx.Colour(70,116,178),
                       wx.Colour(149,190,218),
                       wx.Colour(225,243,228),
                       wx.Colour(251,225,147),
                       wx.Colour(246,143,93),
                       wx.Colour(209,64,46)]
        return color_group
        
    def _get_label_group_by_k(self,bins,counts):
        label_group = []
       
        label_format = '[%d:%d](%d)'
        for val in bins: 
            if val > int(val):
                label_format = '[%.1f:%.1f](%d)'
            
        for i,upper_bound in enumerate(bins):
            lower_bound = min(self.data) if i == 0 else bins[i-1] 
            if isinstance(lower_bound, float):
                label_group.append(label_format % (lower_bound,upper_bound,counts[i]))
            else:
                label_group.append('[%s:%s](%d)' % (lower_bound,upper_bound,counts[i]))
        return label_group
        
    def createClassifyMap(self, map_type):
        """ return an instance of pysal.Map_Classifier """
        id_group = []
        color_group = []
        label_group = []
        
        if map_type == stars.MAP_CLASSIFY_EQUAL_INTERVAL:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Equal_Interval(self.data, k=k)
         
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins), False)
            
        elif map_type == stars.MAP_CLASSIFY_PERCENTILES:
            pct = [1,10,50,90,99,100]
            # doesn't support different defined pct 
            #if self.params.has_key("pct"):
            #    pct = self.params["pct"]
            cm = pysal.Percentiles(self.data,pct=pct)
            counts = list(cm.counts)
            n_counts = len(counts)
            if n_counts < 6:
                for i in range(6-n_counts):
                    counts.append(0)
            label_group = ['<1%%(%d)'% counts[0],
                           '1%% - 10%%(%d)'% counts[1],
                           '10%% - 50%%(%d)'% counts[2],
                           '50%% - 90%%(%d)'% counts[3],
                           '90%% - 99%%(%d)'% counts[4],
                           '>99%%(%d)'% counts[5]]
            #color_group = self._get_default_color_schema(n_bins)
            color_group = self.pick_color_set(3,6,True)
            
        elif map_type == stars.MAP_CLASSIFY_BOX_PLOT:
            hinge = 1.5 # default
            if self.params.has_key("hinge"):
                hinge = self.params["hinge"]
            
            cm = pysal.Box_Plot(self.data,hinge=hinge)
            n_bins = len(cm.bins)
            if n_bins == 5:
                n_upper_outlier = 0 
            else:
                n_upper_outlier = cm.counts[5] 
            label_group = ['Lower outlier(%d)' % cm.counts[0],
                           '<25%% (%d)' % cm.counts[1],
                           '25%% - 50%% (%d)' % cm.counts[2],
                           '50%% - 75%% (%d)' % cm.counts[3],
                           '>75%% (%d)' % cm.counts[4],
                           'Upper outlier (%d)' %n_upper_outlier ]
            
            #color_group = self._get_default_color_schema(n_bins)
            color_group = self.pick_color_set(2, 6 , False)
            
        elif map_type == stars.MAP_CLASSIFY_QUANTILES:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
                
            cm = pysal.Quantiles(self.data, k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins), False)
        
        elif map_type == stars.MAP_CLASSIFY_STD_MEAN:
            cm = pysal.Std_Mean(self.data, multiples=[-2,-1,0,1,2])
            n_bins = len(cm.bins)
            
        elif map_type == stars.MAP_CLASSIFY_MAXIMUM_BREAK:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Maximum_Breaks(self.data, k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins), False)
            
        elif map_type == stars.MAP_CLASSIFY_NATURAL_BREAK:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Natural_Breaks(self.data, k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
            
        elif map_type == stars.MAP_CLASSIFY_FISHER_JENKS:
            cm = pysal.Fisher_Jenks(self.data)
            
            # see blow: common label group and color group
            
        elif map_type == stars.MAP_CLASSIFY_JENKS_CASPALL:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Jenks_Caspall(self.data,k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k([i[0] for i in cm.bins], cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
    
        elif map_type == stars.MAP_CLASSIFY_JENKS_CASPALL_SAMPLED:
            k = 5 # default
            pct = 0.1
            if self.params.has_key("k"):
                k = self.params["k"]
            if self.params.has_key("pct"):
                pct = self.params["pct"]
            cm = pysal.Jenks_Caspall_Sampled(self.data,k=k, pct=pct)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
            
        elif map_type == stars.MAP_CLASSIFY_JENKS_CASPALL_FORCED:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Jenks_Caspall_Forced(self.data,k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
            
        elif map_type == stars.MAP_CLASSIFY_USER_DEFINED:
            assert self.params.has_key("bins")
            bins = self.params["bins"]
            cm = pysal.User_Defined(self.data,bins=bins)
            k = len(bins)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
            
        elif map_type == stars.MAP_CLASSIFY_MAX_P:
            k = 5 # default
            if self.params.has_key("k"):
                k = self.params["k"]
            cm = pysal.Max_P_Classifier(self.data,k=k)
            
            # add label group, color group
            label_group = self._get_label_group_by_k(cm.bins, cm.counts)
            #color_group = self._get_color_schema_by_k(k)
            color_group = self.pick_color_set(1, len(cm.bins),False)
            
        elif map_type == stars.MAP_CLASSIFY_UNIQUE_VALUES:
            id_group_dict = {}
            id_other = []
           
            n = 0
            for i,item in enumerate(self.data):
                if n < 10:
                    if not id_group_dict.has_key(item):
                        id_group_dict[item] = [] 
                        n += 1
                if id_group_dict.has_key(item):
                    id_group_dict[item].append(i) 
                else:
                    id_other.append(i)
                
            id_group = id_group_dict.values() 
            unique_values = id_group_dict.keys()
            max_num_values = n if n <= 10 else 10
            
            label_group = [str(unique_values[i]) for i in range(max_num_values)]
            color_group = [stars.MAP_COLOR_12_UNIQUE_FILL[i] for i in range(max_num_values)]
            #color_group = self.pick_color_set(1, max_num_values,False)
            if n >= 10:
                id_group.append(id_other)
                label_group.append('Others')
                color_group.append(stars.MAP_COLOR_12_UNIQUE_OTHER)
               
            field_name = self.params['field_name']
            id_group.insert(0, [])
            label_group.insert(0, field_name)
            color_group.insert(0, None)
            
            
        else:
            raise KeyError, 'Classify map type is illegal'
        
        # for some common label group and color group
        if map_type in [stars.MAP_CLASSIFY_FISHER_JENKS, stars.MAP_CLASSIFY_STD_MEAN]:
            """
            upper_bound = 0 if len(cm.counts) == 5 else cm.counts[5]
            label_group = ['<%s (%d)'% (cm.bins[0],cm.counts[0]),
                           '%s - %s (%d)'% (cm.bins[0], cm.bins[1],cm.counts[1]),
                           '%s - %s (%d)'% (cm.bins[1], cm.bins[2], cm.counts[2]),
                           '%s - %s (%d)'% (cm.bins[2], cm.bins[3], cm.counts[3]),
                           '%s - %s (%d)'% (cm.bins[3], cm.bins[4], cm.counts[4]),
                           '>%s (%d)'% (cm.bins[4], upper_bound)]
            #color_group = self._get_default_color_schema(len(cm.bins))
            color_group = self.pick_color_set(3,7,False)[1:]
            """
            label_group = self._get_range_labels(cm.bins, cm.counts)
            color_group = self.pick_color_set(3, len(cm.bins), True)#[1:]
            
        if map_type != stars.MAP_CLASSIFY_UNIQUE_VALUES:
            # convert
            binIds = cm.yb
            bins = cm.bins
            
            n_group = len(bins)
            id_group = [[] for i in range(n_group)]
            for i,gid in enumerate(binIds):
                id_group[gid].append(i)
            
        return id_group, label_group, color_group
    
    def _get_range_labels(self, bins, counts):
        label_format_start = '<%d (%d)'
        label_format_end = '>%d (%d)'
        label_format_middle = '%d ~ %d (%d'
        
        for val in bins:
            if val > int(val):
                label_format_start = '<%.1f (%d)'
                label_format_end = '>%.1f (%d)'
                label_format_middle = '%.1f ~ %.1f (%d)'
       
        label_group = []
        bin_start = bins[0]
        bin_end = bins[-1]
        
        label_group.append(label_format_start % (bin_start, counts[0]))
        
        for i in range(len(bins)-1):
            count_val = counts[i]
            bin_1 = bins[i]
            bin_2 = bins[i+1]
            label_group.append(label_format_middle % (bin_1, bin_2, count_val))
            
        #label_group.append(label_format_end % (bin_end, counts[-1]))
        
        return label_group
            
class Smoothing():
    def __init__(self, data, **kwargs):
        self.data = data
        self.params = kwargs
        
class ClassifyMap(ShapeMap):
    """
    """
    def __init__(self, parent, layers, **kwargs):
        from stars.visualization.dialogs import choose_field_name
        ShapeMap.__init__(self,parent, layers)
        
        try:
            layer = layers[0]
            map_type = kwargs["map_type"]
            title = kwargs["title"]
            if "field_name" in kwargs and "data" in kwargs:
                field_name = kwargs["field_name"]
                data = np.array(kwargs["data"])
            else:
                field_name = choose_field_name(self,layer)
                if field_name == None:
                    raise Exception("No field name")
                
                data = np.array(layer.dbf.by_col(field_name))
           
            self.k = None
            self.hinge = None
            self.bins = None
            
            self.parentFrame.SetTitle('%s-%s (%s)' % (title, layer.name, field_name))
            self.updateMap(title,map_type, field_name,data,layer)
            
        except Exception as err:
            self.ShowMsgBox("""Map could not be classified. Please choose a valid numeric variable.
            
Details: """ + str(err.message))
            self.UnRegister()
            self.parentFrame.Close(True)
            return
       
    def updateMap(self, title, map_type, field_name, data, layer):
        from stars.visualization.dialogs import select_k, choose_box_hinge_value, choose_sample_percent, choose_user_defined_bins
        if map_type in [stars.MAP_CLASSIFY_EQUAL_INTERVAL,
                        stars.MAP_CLASSIFY_QUANTILES,
                        stars.MAP_CLASSIFY_MAXIMUM_BREAK,
                        stars.MAP_CLASSIFY_NATURAL_BREAK,
                        stars.MAP_CLASSIFY_JENKS_CASPALL,
                        stars.MAP_CLASSIFY_JENKS_CASPALL_FORCED,
                        stars.MAP_CLASSIFY_MAX_P]:
            if self.k == None:
                self.k = select_k(self)
            factory = ClassifyMapFactory(data,k=self.k)
        
        elif map_type in [stars.MAP_CLASSIFY_JENKS_CASPALL_SAMPLED]:
            if self.k == None:
                self.k = select_k(self)
            pct = choose_sample_percent(self)
            factory = ClassifyMapFactory(data,k=self.k)
            
        elif map_type in [stars.MAP_CLASSIFY_BOX_PLOT]:
            if self.hinge == None:
                self.hinge = choose_box_hinge_value(self)
            self.parentFrame.SetTitle('%s hinge=%s-%s (%s)' % (title,self.hinge,layer.name, field_name))
            factory = ClassifyMapFactory(data,hinge=self.hinge)
            
        elif map_type in [stars.MAP_CLASSIFY_USER_DEFINED]:
            if self.bins == None:
                self.bins = choose_user_defined_bins(self)
            if self.bins == None:
                raise KeyError
            factory = ClassifyMapFactory(data,bins=self.bins)
            
        elif map_type in [stars.MAP_CLASSIFY_PERCENTILES,
                          stars.MAP_CLASSIFY_STD_MEAN,
                          stars.MAP_CLASSIFY_FISHER_JENKS,
                          ]:
            factory = ClassifyMapFactory(data)
            
        elif map_type in [stars.MAP_CLASSIFY_UNIQUE_VALUES]:
            factory = ClassifyMapFactory(data, field_name=field_name)
        
        id_group, label_group, color_group = factory.createClassifyMap(map_type)
        if len(id_group) != len(label_group) != len(color_group):
            raise AttributeError
        
        if 'Others' in label_group:
            self.ShowMsgBox('CAST maps 12 unique values; any additional values will be shown in gray.')
            
        self.color_schema_dict[layer.name] = ColorSchema(color_group, label_group)
        self.draw_layers[layer].set_data_group(id_group)
        self.draw_layers[layer].set_fill_color_group(color_group)       
       
        self.id_group = id_group
        self.label_group = label_group
        self.color_group = color_group
        
        #self.update_color_schema(layer, layer.name,
        
