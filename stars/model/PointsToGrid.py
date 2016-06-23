__author__  = "Xun Li <xunli@asu.edu>"

import os,math
import pysal
import numpy as np

def PointsToGrid(pts_shp_path, grid_size, polygon_background=None, grid_shape_path=None, bFineBG=False):
    """
    Convert POINT  to GRID. 
    
    To avoid discontinued grid, a polygon background shape file
    can be used to maitain the EMPTY cellular, with point count
    equals to 0. The output GRID shape file and dbf file will 
    be saved to grid_shape_path location.
    
    Example
    --------
    >>> import stars
    >>> stars.PointsToGrid("../examples/Tempe090106_083107.shp", 1000,
                           polygon_background="../examples/Data_and_Rates_for_Beats.shp",
                           grid_shape_path='../examples/test.shp',
                           bFineBG=False)
    """
    f = pysal.open(pts_shp_path)
    if hasattr(f,'type'):
        if f.type != pysal.cg.Point:
            raise "File type not correct!"
    shape_objects = f.read()
    extent = f.bbox
    f.close()
    
    if polygon_background:            
        _f = pysal.open(polygon_background)
        _polygons = _f.read()
        extent = _f.bbox
        _f.close()
    
    left, top = extent[0],extent[3]
    shape_width = extent[2] - extent[0]
    shape_height = extent[3] - extent[1]
    grid_width = math.floor(shape_width / float(grid_size))
    grid_height = math.floor(shape_height / float(grid_size))
    grid_indice = np.zeros((grid_width, grid_height))
    
    # test POINTs and cellular
    for pt in shape_objects:
        x,y = pt
        grid_x = math.floor((x-left) / grid_size)
        grid_y = math.floor((top-y)/ grid_size)
        if grid_x < grid_width and grid_y < grid_height:
            grid_indice[grid_x][grid_y] += 1
            
    # test polygon Background and EMPTY cellulars
    if polygon_background and bFineBG:            
        for poly in _polygons:
            pts_test_results = {} # for accelerating polygon/point testing
            
            for x in range(int(grid_width)):
                for y in range(int(grid_height)):
                    if grid_indice[x][y] >= 0:
                        # need to see if this cell intersects with the POLY
                        p0 = pysal.cg.Point( (left + x*grid_size,     top - y*grid_size))
                        p1 = pysal.cg.Point( (left + (x+1)*grid_size, top - y*grid_size))
                        p2 = pysal.cg.Point( (left + (x+1)*grid_size, top - (y+1)*grid_size))
                        p3 = pysal.cg.Point( (left + x*grid_size,     top - (y+1)*grid_size))
                        
                        if p1[0] < 694055.4309 and p2[1] < 880708.8851:
                            grid_indice[x][y] = -1
                            continue
                        if p1[0] < 693998.8695 and p3[1] > 880734.4465:
                            grid_indice[x][y] = -1
                            continue
                        if p3[0] < 694033.0400 and p3[1] > 880748.8588:
                            grid_indice[x][y] = -1
                            continue
                        if p1[0] > 694101.1151:
                            grid_indice[x][y] = -1
                            continue
                        
                        if p0[0] > 694006.1066 and p0[1] < 880681.2252:
                            grid_indice[x][y]= -1
                            continue
                        #694056.1066
                        #694101.4089
                        
                        """
                        count = 0
                        for p in [p0,p1,p2,p3]:
                            if pts_test_results.has_key(p):
                                ret = pts_test_results[p]
                            else:
                                ret = pysal.cg.get_polygon_point_intersect(poly, p)
                                pts_test_results[p] = ret
                            if ret != None:
                                break
                            count += 1
                        if count == 4:
                            grid_indice[x][y] = -1 # just mark
                        """
    
    # save GRID shape and dbf file
    if grid_shape_path:
        grid_shp = pysal.open(grid_shape_path,'w')
        grid_dbf = pysal.open(grid_shape_path[:-3]+'dbf','w')
        grid_dbf.header = ['ID','count']
        grid_dbf.field_spec = [('N',9,0),('F',9,0)]
        
        cells_x, cells_y = np.where(grid_indice >= 0)
        count = 1
        for i,x  in enumerate(cells_x):
            y = cells_y[i]
            p0 = pysal.cg.Point( (left + x*grid_size,     top - y*grid_size))
            p1 = pysal.cg.Point( (left + (x+1)*grid_size, top - y*grid_size))
            p2 = pysal.cg.Point( (left + (x+1)*grid_size, top - (y+1)*grid_size))
            p3 = pysal.cg.Point( (left + x*grid_size,     top - (y+1)*grid_size))
            poly = pysal.cg.Polygon([p0,p1,p2,p3])
            grid_shp.write(poly)
            pts_count = grid_indice[x][y]
            pts_count = pts_count if pts_count > 0 else 0
            grid_dbf.write([count, pts_count])
            count += 1
        grid_shp.close()
        grid_dbf.close()
        
if __name__ == "__main__":
    points_files = ['Spring08/solitary_indoor.shp','Spring08/solitary_outdoor.shp',
                    'Spring08/social_in.shp','Spring08/social_out.shp',
                    'Spring08/teacher_nocircle_in.shp', 'Spring08/teacher_nocircle_out.shp',
                    'Spring08/parallel_in.shp','Spring08/parallel_out.shp',
                    'Fall08/solitary_in.shp','Fall08/solitary_out.shp',
                    'Fall08/social_in.shp','Fall08/social_out.shp',
                    'Fall08/teacher_in.shp','Fall08/teacher_out.shp',
                    'Fall08/parallel_in.shp','Fall08/parallel_out.shp',
                    'Spring09/solitary_in.shp','Spring09/solitary_out.shp',
                    'Spring09/social_in.shp','Spring09/social_out.shp',
                    'Spring09/teacher_in.shp','Spring09/teacher_out.shp',
                    'Spring09/parallel_in.shp','Spring09/parallel_out.shp']
    """
    points_files = ['Spring08/boy_solitary_in.shp','Spring08/boy_solitary_out.shp',
                    'Spring08/boy_social_in.shp','Spring08/boy_social_out.shp',
                    'Spring08/boy_tea_noc_in.shp', 'Spring08/boy_tea_noc_out.shp',
                    'Spring08/boy_parallel_int.shp','Spring08/boy_parallel_out.shp',
                    'Spring08/gilr_solitary_in.shp','Spring08/gilr_solitary_out.shp',
                    'Spring08/girl_social_in.shp','Spring08/girl_social_out.shp',
                    'Spring08/girl_teach_noc_in.shp', 'Spring08/girl_teach_noc_out.shp',
                    'Spring08/girl_parallel_int.shp','Spring08/girl_parallel_out.shp',
                    'Fall08/boy_solitary_in.shp','Fall08/boy_solitary_out.shp',
                    'Fall08/boy_social_in.shp','Fall08/boy_social_out.shp',
                    'Fall08/boy_teach_noc_in.shp', 'Fall08/boy_teach_noc_out.shp',
                    'Fall08/boy_parallel_in.shp','Fall08/boy_parallel_out.shp',
                    'Fall08/girl_solitary_in.shp','Fall08/girl_solitary_out.shp',
                    'Fall08/girl_social_indoor.shp','Fall08/girl_social_outdoor.shp',
                    'Fall08/girl_teach_noc_in.shp', 'Fall08/girl_tea_noc_out.shp',
                    'Fall08/girl_parallel_in.shp','Fall08/girl_parallel_out.shp',
                    'Spring09/boy_solitary_in.shp','Spring09/boy_solitary_out.shp',
                    'Spring09/boy_social_in.shp','Spring09/boy_social_out.shp',
                    'Spring09/boy_teach_noc_in.shp', 'Spring09/boy_teach_noc_out.shp',
                    'Spring09/boy_parallel_in.shp','Spring09/boy_parallel_out.shp',
                    'Spring09/girl_solitary_in.shp','Spring09/girl_solitary_out.shp',
                    'Spring09/girl_social_in.shp','Spring09/girl_social_out.shp',
                    'Spring09/girl_teach_noc_in.shp', 'Spring09/girl_teach_noc_out.shp',
                    'Spring09/girl_parallel_in.shp','Spring09/girl_parallel_out.shp']
    """
    taskList = [2,3,8,9,12,13,14,15,16,17,20,21,23,25,27]
    #points_file = ['Spring08/task_%d.shp']
    
    indoor_w = pysal.open("/indoor_grid.gal").read()
    outdoor_w = pysal.open("/outdoor_grid.gal").read()
    
    for i in range(len(points_files)/2):
        f = points_files[2*i]
        output_fname = '/%s_grid.shp' % f.replace('/','_')[:-4]
        PointsToGrid('/Users/xunli/Downloads/PALS/%s'%f,3,
                 polygon_background='/indoor.shp',
                 grid_shape_path=output_fname,
                 bFineBG=False)
        dbf = pysal.open(output_fname[:-3]+'dbf','r')
        y = np.array(dbf.by_col('count'))
        mi = pysal.Moran(y, indoor_w)
        print output_fname, mi.I, mi.EI, mi.p_norm, mi.p_sim, mi.z_sim
        dbf.close()
        
        f = points_files[2*i+1]
        output_fname = '/%s_grid.shp' % (f.replace('/','_')[:-4])
        PointsToGrid('/Users/xunli/Downloads/PALS/%s'%f,3,
             polygon_background='/outdoor.shp',
             grid_shape_path=output_fname,
             bFineBG=True)
        
        dbf = pysal.open(output_fname[:-3]+'dbf','r')
        y = np.array(dbf.by_col('count'))
        mi = pysal.Moran(y, outdoor_w)
        print output_fname, mi.I, mi.EI, mi.p_norm, mi.p_sim, mi.z_sim
        dbf.close()
    """
    from time import gmtime, strftime
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    PointsToGrid("../examples/Tempe090106_083107.shp", 1000,
                polygon_background="../examples/Data_and_Rates_for_Beats.shp",
                grid_shape_path='../examples/test.shp',
                bFineBG= True)
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    """
    pass