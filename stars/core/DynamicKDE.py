"""
Multi-processing version of Dynamic KDE
"""

__author__  = "Xun Li <xunli@asu.edu>"
__all__ = ['DynamicKDE']

import os
import numpy as np
from math import *
from multiprocessing import *
from stars.visualization.utils import GradientColor

class DynamicKDE:
    """
    A standalone class supporting Dynamic Kernel Density Estimation
    (D-KDE) computation and Multi-processing D-KDE computation.
    
    D-KDE: 
    given a matrix with specific width and height
    given a list of data (2D point (x,y) in this app) set,
    compute a KDE for each data set, and return a sequence of
    matrix and return.
    """
    def __init__(self, 
                 data_list, 
                 kernel, 
                 bandwidth, 
                 cell_size,
                 rows,
                 cols,
                 grid_lower,
                 grid_upper,
                 grid_left,
                 opaque,
                 color_band,
                 isAccumulative=False):
        self.data_list = data_list
        self.kernel = kernel
        self.bandwidth = bandwidth
        self.cell_size = cell_size
        self.rows = rows
        self.cols = cols
        self.grid_left = grid_left
        self.grid_lower = grid_lower
        self.grid_upper = grid_upper
        self.opaque = opaque
        self.color_band = color_band
        self.isAccumulative = isAccumulative
        
        
    def do(self):
        if self.__createProcesses():
            # first, compute KDE for each dataset
            for i,dataset in enumerate(self.data_list):
                task_data = {'method': 'compute',
                             'id':i, 
                             'data':dataset,
                             'kernel': self.kernel,
                             'bandwidth': self.bandwidth,
                             'cell_size': self.cell_size,
                             'rows': self.rows,
                             'cols': self.cols,
                             'grid_lower': self.grid_lower,
                             'grid_upper': self.grid_upper,
                             'grid_left': self.grid_left,
                             }
                self.taskQueue.put(task_data)
                
            self.gradient_color_min = 0
            self.gradient_color_max = 0
  
            num_tasks = len(self.data_list)
            num_proc_start = min(self.num_proc, num_tasks)
            
            self.tmp_grids = [None for i in range(num_tasks)]
            for i in range(num_tasks):
                args = self.doneQueue.get()
                idx = args['id']
                tmp_grid = args['grid']
                grid_max = args['grid_max']
                
                self.tmp_grids[idx] = tmp_grid
                
                if grid_max > self.gradient_color_max:
                    self.gradient_color_max = grid_max
                    
            if self.isAccumulative:
                for i in range(num_tasks-1):
                    self.tmp_grids[i+1] += self.tmp_grids[i]
                # need to recalculate the max value in tmp_grid
                self.gradient_color_max = np.max(self.tmp_grids[-1])
                
            # second,create KDE map
            self.grids = [None for i in range(num_tasks)]
            # submit tasks
            for i, grid in enumerate(self.tmp_grids):
                task_data = {'method':'create',
                             'id':i, 
                             'grid': grid,
                             'grid_max': self.gradient_color_max,
                             'opaque': self.opaque,
                             'color_band': self.color_band
                             }
                self.taskQueue.put(task_data)
            # process returns
            for i in range(num_tasks):
                args = self.doneQueue.get()
                idx = args['id']
                grid = args['data']
                
                self.grids[idx] = grid
                        
    def __del__(self):
        # deconstructor
        self.__releaseProcesses()

    def __createProcesses(self):
        try:
            # processes for dynamic KDE maps
            self.num_proc = cpu_count()
            self.taskQueue = Queue()
            self.doneQueue = Queue()
            self.processes = [ ]
            
            for n in range(self.num_proc):
                process = Process(target=DynamicKDE.compute_densityMap, args=(self.taskQueue,self.doneQueue))
                process.start()
                self.processes.append(process)
             
            return True
        except:
            return False
        
    def __releaseProcesses(self):
        try:
            # release resources for created processes and destroy them
            for i in range(self.num_proc):
                if self.processes[i].is_alive():
                    self.processes[i].terminate()
        except:
            pass
        
    def compute_densityMap(cls, input, output):
        """
        The function will be executed in each process.
        """
        while True:
            args = input.get()
            method = args['method']
            id = args['id']
            
            if method == 'compute': 
                # for computing KDE for each cell in grid
                points    = args['data']
                kernel    = args['kernel']
                bandwidth = args['bandwidth']
                cellSize  = args['cell_size']
                grid_left = args['grid_left']
                grid_lower= args['grid_lower']
                grid_upper= args['grid_upper']
                rows,cols = args['rows'], args['cols']
                
                invert = False
                radius    = bandwidth / cellSize
                tmpGrid = np.zeros((rows,cols))
                
                #print '%s:%s'%(os.getpid(),args.keys())
                
                for pt in points:
                    X,Y = pt
                    float_i = (Y - grid_lower) / cellSize
                    #float_i = (grid_upper -Y) / cellSize
                    i = int(floor(float_i - radius))
                    i = i if i >= 0 else 0
                    I = int(floor(float_i + radius))
                    I = I if I < rows else rows-1
            
                    float_j = (X-grid_left) / cellSize
                    j = int(floor(float_j - radius))
                    j = j if j >= 0 else 0
                    J = int(floor(float_j + radius))
                    J = J if J < cols else cols-1
            
                    for row in xrange(i,I+1):
                        for col in xrange(j,J+1):
                            x = grid_left + (col*cellSize)
                            y = grid_lower + (row*cellSize)
                            d = ((x-X)**2 + (y-Y)**2) ** (0.5)
                            if d <= bandwidth:
                                z = d/bandwidth
                                if invert:
                                    tmpGrid[row,col] -= kernel(z)
                                else:
                                    tmpGrid[row,col] += kernel(z)
                                    
                output.put({'id':id,'grid':tmpGrid, 'grid_max':np.max(tmpGrid)})
                
            elif method == 'create':
                grid      = args['grid']
                grid_max  = args['grid_max']
                opaque    = args['opaque']
                color_band = args['color_band']
                
                gradient_color = GradientColor(color_band)
                
                # make Byte Array for bmp
                rows,cols = grid.shape
                arr = np.zeros((rows, cols, 4), np.uint8)
                R, G, B, A = range(4)
                  
                # flip from real model coords to screen coords
                raster = grid
                raster = raster[::-1]
                raster_min, raster_max = raster.min(), grid_max #raster.max()
                raster_val_range = raster_max - raster_min
                if raster_val_range > 0:
                    raster_scaled = (raster - raster_min)/(raster_max - raster_min) 
                else:
                    raster_scaled = raster
                
                # tranfer 0~1 value to 0~255 pixel values, 
                red_matrix, blue_matrix, green_matrix, opaque_matrix = \
                          np.zeros((rows,cols)),\
                          np.zeros((rows, cols)), \
                          np.zeros((rows,cols)), \
                          np.ones((rows,cols))*opaque* (255/100.0) # opaque ranges (0,100)
            
                for i,row in enumerate(raster_scaled):
                    for j,item in enumerate(row):
                        clr = gradient_color.get_color_at(item)
                        
                        red_matrix[i][j]   = clr.red
                        green_matrix[i][j] = clr.green
                        blue_matrix[i][j]  = clr.blue
                        if item <0.15:
                            opaque_matrix[i][j] = 0
                
                arr[:,:,R] = (red_matrix).astype("B")
                arr[:,:,G] = (green_matrix).astype("B")
                arr[:,:,B] = (blue_matrix).astype("B")
                arr[:,:,A] = (opaque_matrix).astype("B")#self.opaque #alpha
                
                output.put({'id':id,'data':arr})
    compute_densityMap = classmethod(compute_densityMap)    
    