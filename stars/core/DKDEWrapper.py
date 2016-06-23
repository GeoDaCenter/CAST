"""
"""

__author__='Xun Li <xunli@asu.edu>'
__all__=[]


from mt_densitymap import *
import ctypes
import numpy as np
import wx

def call_kde(n,x,y,pts_ids, extent,bandwidth,cellsize,kernel, gradient, opaque):
    _x = VecDouble(x)
    _y = VecDouble(y)
    _pts_ids = VecInt(pts_ids)
    _extent = VecDouble(extent)
  
    if kernel == 'quadratic':
        kernel_type = 0
    elif kernel == 'triangular':
        kernel_type = 1
    elif kernel == 'uniform':
        kernel_type = 2
    elif kernel == 'gaussian':
        kernel_type = 3
    else:
        kernel_type = 0
        
    if gradient == 'classic':
        gradient_type = 0
    elif gradient == 'fire':
        gradient_type = 1
    elif gradient == 'omg':
        gradient_type = 2
    elif gradient == 'pbj':
        gradient_type = 3
    elif gradient == 'pgaitch':
        gradient_type = 4
    elif gradient == 'rdyibu':
        gradient_type = 5
    else:
        gradient_type = 0
        
    kde = KDE(n, _x, _y, _pts_ids, _extent, bandwidth, cellsize, kernel_type, gradient_type, opaque)
    kde.update_grid()
    kde.get_minmax_gradient()
    gradient_min = kde.gradient_min
    gradient_max = kde.gradient_max
    kde.create_rgba_buffer(gradient_min,gradient_max)
   
    rows = kde.rows 
    cols = kde.cols
    
    arr = np.zeros((rows, cols, 4), np.uint8)
    R, G, B, A = range(4)
    rBuffer = kde.r_buffer
    gBuffer = kde.g_buffer
    bBuffer = kde.b_buffer
    aBuffer = kde.a_buffer
    
    for i in range(rows):
        for j in range(cols):
            buff_idx = i*cols + j
            arr[i,j,R] = rBuffer[buff_idx]
            arr[i,j,G] = gBuffer[buff_idx]
            arr[i,j,B] = bBuffer[buff_idx]
            arr[i,j,A] = aBuffer[buff_idx]
            
    return arr,rows,cols, gradient_min, gradient_max
    
    
def call_dkde(x,y,intervals, itv_pts_ids, extent,bandwidth,cellsize, kernel, gradient, opaque):
    # convert from list to C Arrays
    _x = VecDouble(x)
    _y = VecDouble(y)
    _itv_pts_ids = VecVecInt(itv_pts_ids)
    _extent = VecDouble(extent)
    
    if kernel == 'quadratic':
        kernel_type = 0
    elif kernel == 'triangular':
        kernel_type = 1
    elif kernel == 'uniform':
        kernel_type = 2
    elif kernel == 'gaussian':
        kernel_type = 3
    else:
        kernel_type = 0
        
    if gradient == 'classic':
        gradient_type = 0
    elif gradient == 'fire':
        gradient_type = 1
    elif gradient == 'omg':
        gradient_type = 2
    elif gradient == 'pbj':
        gradient_type = 3
    elif gradient == 'pgaitch':
        gradient_type = 4
    else:
        gradient_type = 0
    
    dkde = DKDE(_x,_y,intervals,_itv_pts_ids,_extent,bandwidth,cellsize,kernel_type, gradient_type, opaque) 

    rows = dkde.rows 
    cols = dkde.cols
    gradient_min = dkde.gradient_min
    gradient_max = dkde.gradient_max
    
    rBufferList = dkde.r_buffer_array
    gBufferList = dkde.g_buffer_array
    bBufferList = dkde.b_buffer_array
    aBufferList = dkde.a_buffer_array
   
    img_array = []
    for i in range(intervals):
        arr = np.zeros((rows, cols, 4), np.uint8)
        R, G, B, A = range(4)
        rBuffer = rBufferList[i]
        gBuffer = gBufferList[i]
        bBuffer = bBufferList[i]
        aBuffer = aBufferList[i]
        for i in range(rows):
            for j in range(cols):
                buff_idx = i*cols + j
                arr[i,j,R] = rBuffer[buff_idx]
                arr[i,j,G] = gBuffer[buff_idx]
                arr[i,j,B] = bBuffer[buff_idx]
                arr[i,j,A] = aBuffer[buff_idx]
        img_array.append(arr)
    del dkde
    return img_array,rows,cols, gradient_min, gradient_max
            
if __name__=='__main__':
    x = []
    y = []
    f = open("points.txt")
    line = f.readline()
    while len(line)>0:
        line = line.split(" ")
        x.append(float(line[0]))
        y.append(float(line[1]))
        line = f.readline()

    app = wx.App()
    app.MainLoop()
    
    n = 1307
    itv_pts_ids = [range(500),range(500,1307)]
    extent = [681438.7183029, 844117.2999509854, 710840.4064453088, 894312.9554290767]
    arr,rows,cols,gmin,gmax = call_kde(n,x,y,itv_pts_ids[0],extent,1421.01,125.01,'gaussian','fire',255)
    bmp = wx.BitmapFromBufferRGBA(cols, rows, arr)
    bmp.SaveFile("tet0.png", wx.BITMAP_TYPE_PNG)
   
    arrs,rows,cols,gmin,gmax = call_dkde(x,y,2,itv_pts_ids,extent,1421.01,125.01,'gaussian','fire',255)
    for i,arr in enumerate(arrs):
        bmp = wx.BitmapFromBufferRGBA(cols, rows, arr)
        bmp.SaveFile("test%d.png"%i, wx.BITMAP_TYPE_PNG)