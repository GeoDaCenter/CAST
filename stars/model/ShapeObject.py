"""
ShapeObject is the data model of input shape files
"""

__author__  = "Xun Li <xunli@asu.edu>"

import os, sys, datetime,math
import stars
import numpy as np
from scipy.spatial import cKDTree

if os.name != 'posix':
    import shapelib,dbflib, shptree, coordinator
else:
    sys.path.insert(0,os.path.split(__file__)[0])
    #print sys.path
    import shapelib,dbflib, shptree,coordinator
"""
class ShapeFileObject():
    def __init__(self, arg,**kwargs):
        self.name = ""
        self.extent = None
        
        if kwargs.has_key("name"):
            self.name = kwargs["name"]
        if kwargs.has_key("extent"):
            self.extent = kwargs["extent"]
        
        self.shapes = []
        self.shape_type = 0
        self.shape_objects = None
        self.dbf = None
        self.locator = None
        self.centroids = []
        
        if isinstance(arg, str) or isinstance(arg, unicode):
            # single file
            self.read_shape_file(arg)
        elif isinstance(arg, list):
            # arg: a list of pysal.cg.shapes.Point/Polygon
            self.shape_objects = arg
            # get a test object to detect the shape type
            test_obj = self.shape_objects[0] 
            if isinstance(test_obj, pysal.cg.Point):
                self.shape_type = stars.SHP_POINT
            elif isinstance(test_obj, pysal.cg.Line):
                self.shape_type = stars.SHP_LINE
            elif isinstance(test_obj, pysal.cg.Polygon):
                self.shape_type = stars.SHP_POLYGON
                self.get_centroids_from_plgs()
                        
    def get_centroids_from_plgs(self):
        for poly in self.shape_objects:
            try:
                c = pysal.cg.Point(poly.centroid)
                self.centroids.append(c)
            except:
                # if there's hole in polygon, use bounding box instead
                left,lower,right,upper= poly.bounding_box[:]
                c = pysal.cg.Point((left+(right-left)/2.0,lower+(upper-lower)/2.0))
                self.centroids.append(c) 
    
    def read_shape_file(self,path):
        f = pysal.open(path)
        if hasattr(f,'type'):
            if f.type == pysal.cg.Polygon:
                self.shape_type = stars.SHP_POLYGON
                self.shape_objects = f.read()
                self.get_centroids_from_plgs()
            elif f.type == pysal.cg.Point:
                self.shape_type = stars.SHP_POINT
                self.shape_objects = f.read()
            elif f.type == pysal.cg.Line:
                self.shape_type = stars.SHP_LINE
                self.shape_objects = f.read()
            else:
                raise "file type not recognized"
                
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.extent = f.bbox

        # load dbf
        if path.endswith('shp') and os.path.exists(path[:-4]+'.dbf'):
            self.path = path
            self.loadDBF()
        else:
            #self.dbf = NullDBF(len(layer))
            pass
   
    def loadDBF(self):
        self.dbf = pysal.open(self.path[:-4]+'.dbf','r')
        
    def get_locator(self):
        if not self.locator:
            #R-tree based locator
            if stars.SHAPE_LOCATOR_INDEX == stars.SHAPE_LOCATOR_RTREE:
                if self.shape_type == stars.SHP_POLYGON:
                    self.locator = pysal.cg.PolygonLocator(self.shape_objects)
                elif self.shape_type == stars.SHP_POINT:
                    self.locator = pysal.cg.PointLocator(self.shape_objects)
            
            #KD-tree locator for polygons(centroids) and points
            elif stars.SHAPE_LOCATOR_INDEX == stars.SHAPE_LOCATOR_KDTREE:
                if self.shape_type == stars.SHP_POINT:
                    #test_shape_object = list(set(self.shape_objects))
                    # cKDTree: KDTree -> 2.3x improvement
                    self.locator = cKDTree(self.shape_objects)
                elif self.shape_type == stars.SHP_POLYGON:
                    # NOTE:KD-tree search centroids is also slow than brutal force
                    # search centroids
                    self.locator = KDTree(self.centroids)
                    #self.locator = None
                
        return self.locator
    
    # ----------------------------------
    # Belows are reserved override functions
    # -----------------------------------
    def __len__(self):
        return len(self.shape_objects)
    
    def __getitem__(self, index):
        if self.shape_type == stars.SHP_POLYGON:
            return self.shape_objects[index].vertices
        elif self.shape_type == stars.SHP_POINT:
            return self.shape_objects[index]
"""      
class DBF():
    def __init__(self):
        self.header = []
        self.field_spec = [] # ('N',4,0) 
        self.n_records = 0
        self.n_fields = 0
        self.records = []
        self._dbf = None
        
    def read_record(self, i):
        """ return list"""
        if len(self.records) > 0:
            return self.records[i]
        else:
            rtn = []
            record = self._dbf.read_record(i)
            for col_name in self.header:
                rtn.append(record[col_name])
            return rtn
 
    def column_index(self, col_name):
        return self.header.index(col_name)
    
    def by_col(self, col_name, ctype=None, ctype_info=None):
        rtn = []
        col_idx = self.column_index(col_name)
        
        if ctype == 'datetime':
            if ctype_info == None:
                ctype_info = "%Y%m%d"
            for i in range(self.n_records):
                item = self.read_record(i)[col_idx]
                try:
                    item = datetime.datetime.strptime(str(item), ctype_info)
                except:
                    raise TypeError, "column type is not recognizable."
                rtn.append(item)
        elif ctype == None:
            # string by default
            for i in range(self.n_records):
                item = self.read_record(i)[col_idx]
                rtn.append(item)
        else:
            for i in range(self.n_records):
                item = eval('%s(%s)' % (ctype,self.read_record(i)[col_idx]))
                rtn.append(item)
            
        return rtn
    
class CShapeFileObject():
    """
    """
    def __init__(self, arg,**kwargs):
        self.name = ""
        self.path = ""
        self.extent = None
        self.engine = "c"
        
        if kwargs.has_key("name"):
            self.name = kwargs["name"]
        if kwargs.has_key("extent"):
            self.extent = kwargs["extent"]
        if kwargs.has_key("engine"):
            self.engine = kwargs["engine"]
        
        self.n = 0
        self.shape_type = 0
        self._shape_objects = []
        
        self.shp = None
        self.dbf = DBF()
        
        self.locator = None
        
        # for kd-tree
        self._kdtree = None
        self._kdtree_id_dict = {} # for polygon has several parts (centroids)
       
        # for prj file
        self.unit_name = None
        self.unit = None
        
        if kwargs.has_key("centroids"):
            self.centroids = kwargs["extent"]
        
        if isinstance(arg, str) or isinstance(arg, unicode):
            # single file
            self.path = arg
            self.read_shape_file(arg)
        elif isinstance(arg, list):
            import pysal
            # arg: a list of pysal.cg.shapes.Point/Polygon
            self._shape_objects = arg
            # get a test object to detect the shape type
            test_obj = self._shape_objects[0] 
            if isinstance(test_obj, tuple):
                self.shape_type = stars.SHP_POINT
            elif isinstance(test_obj, list):
                self.shape_type = stars.SHP_POLYGON
            else:
                # shouldn't be here, not support other types
                raise TypeError
                
    def clean(self):
        # clean memory here 
        del self.centroids
        del self._shape_objects
        coordinator.clean()
        
        if self.locator:
            del self.locator
        del self.dbf
        del self.shp
        if self._kdtree:
            del self._kdtree
                        
    def read_shape_file(self,path):
        self.name = str(os.path.splitext(os.path.basename(path))[0])
        shp = shapelib.ShapeFile(path)
        shpinfo = shp.info()
        self.n= shpinfo[0]
        self.shp = shp
        
        if shpinfo[1] == shapelib.SHPT_POINT:
            self.shape_type = stars.SHP_POINT
        elif shpinfo[1] == shapelib.SHPT_POLYGON:
            self.shape_type = stars.SHP_POLYGON
        else:
            raise Exception("Shape type not support in CAST")
        
        self.extent = shpinfo[2][:2] + shpinfo[3][:2]
        self.centroids = coordinator.centroids(shp.cobject())
        self._shape_objects = coordinator.read_objects(shp.cobject(),self.name)
        
        # load index
        self.locator = shptree.SHPTree(self.shp.cobject(), 2, 0)
        stars.SHAPE_LOCATOR_INDEX = stars.SHAPE_LOCATOR_QUADTREE
        #stars.SHAPE_LOCATOR_INDEX = None
        self.loadDBF(path)
        
        self.get_kdtree_locator()
           
        #self.read_project_file(path)
        # NOTE: quadtree is faster here, but kdtree must be used
        #       in space-time query, which needs a K nearest neighbor
        #       search
        #self.locator = cKDTree(self.shape_objects)
        #stars.SHAPE_LOCATOR_INDEX = stars.SHAPE_LOCATOR_KDTREE
            
    def convert_screen_objects(self, view):
        screen_objects = coordinator.convert(
            self.shp.cobject(),
            self.name,
            int(view.pixel_width),
            int(view.pixel_height),
            int(view.offset_x),
            int(view.offset_y),
            int(view.pan_offset_x),
            int(view.pan_offset_y),
            view.extent,
            view.zoom_extent
            )
        if len(view.zoom_extent) > 0:
            view.extent = view.zoom_extent
            view.zoom_extent = []
            
        return screen_objects
            
    def test_point_in_polygon(self, points):
        return coordinator.pnpolygon(self.shp.cobject(),points)
            
    def read_project_file(self,path):
        prj_file = path[:-4] + '.prj'
        if os.path.exists(prj_file):
            f = open(prj_file)
            line = f.readline().strip()
            pos = line.find("PROJECTION")
            if pos < 0:
                return
            line = line[pos:]
            parameters = line.split('],')
            for param in parameters:
                if param.startswith("UNIT"):
                    param = param[5:]
                    param = param[:param.find(']')]
                    unit_name, unit = param.split(',')
                    unit = float(unit)
                    if unit_name.lower().find('foot') >=0:
                        self.unit_name = 'feet'
                        self.unit = unit
                    elif unit_name.lower().find('degree') >=0:
                        self.unit_name = 'degree'
                        self.unit = unit
                    elif unit_name.lower().find('meter') >=0:
                        self.unit_name = 'meters'
                        self.unit = unit
                    elif unit_name.lower().find('mile') >=0:
                        self.unit_name = 'miles'
                        self.unit = unit
            
    def loadDBF(self, path):
        # load dbf
        #import dbflib 
        dbf = dbflib.DBFFile(path[:-4]+'.dbf')
        self.dbf.n_records = dbf.record_count()
        self.dbf.n_fields = dbf.field_count()
      
        self.dbf.header = []
        self.dbf.field_spec = []
            
        for i in range(self.dbf.n_fields):
            typee, name, lenn, decc = dbf.field_info(i)
            self.dbf.header.append(name)
            if typee == 0: # string
                self.dbf.field_spec.append(('C',lenn,decc))
            elif typee == 1: # integer
                self.dbf.field_spec.append(('N',lenn,decc))
            elif typee == 2: # float
                self.dbf.field_spec.append(('F',lenn,decc))
               
        self.dbf._dbf = dbf
        
            
    @property 
    def shape_objects(self):
        if len(self._shape_objects) == 0:
            self._shape_objects = coordinator.read_objects(self.shp.cobject())
        return self._shape_objects 
            
    def get_locator(self):
        return self.locator
    
    def get_kdtree_locator(self):
        if self._kdtree == None:
            if self.shape_type == stars.SHP_POINT:
                self._kdtree = cKDTree(self.shape_objects)
            else:
                flat_centroids = []
                idx = 0
                for i,part in enumerate(self.centroids):
                    #flat_centroids += part
                    for j in part:
                        if not math.isinf(j[0]):
                            flat_centroids.append(j)
                            self._kdtree_id_dict[idx] = i
                            idx += 1
                self._kdtree = cKDTree(flat_centroids)
        return self._kdtree
        
    def get_kdtree_polyid(self, query_idx):
        return self._kdtree_id_dict[query_idx]
            
    def __len__(self):
        return self.n
    
    def __getitem__(self, index):
        if self.shape_type == stars.SHP_POLYGON:
            return self.shape_objects[index]
        elif self.shape_type == stars.SHP_POINT:
            return self.shape_objects[index]        
    