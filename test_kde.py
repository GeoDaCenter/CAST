from stars.core.DKDEWrapper import call_kde
from Image import fromarray
from numpy import std 
from pysal import quantile
from math import pow

kernel    = 'gaussian'
gradient  = 'fire'
opaque    = 200
bandwidth = '' 
cellsize  = ''

f1 = open('dataset.txt')
x = []
y = []
for line in f1:
    pos1 = line.find(' ')
    pos2 = line.find(')')
    x.append(float(line[6:pos1]))
    y.append(float(line[pos1+1:pos2]))
f1.close()
n = len(x)
extent = [-111.978411801669,33.389877535993,-111.877413701099,33.4296472118644]
"""
f2 = open('extent.txt')
for line in f2:
    pos1 = line.find(' ')
    pos2 = line.find(',')
    pos3 = line.rfind(' ')
    pos4 = line.find(')')
    extent.append(float(line[4:pos1]))
    extent.append(float(line[pos1+1:pos2]))
    extent.append(float(line[pos2+1:pos3]))
    extent.append(float(line[pos3+1:pos4]))
f2.close()
"""
if cellsize == "":
    w = extent[2]-extent[0]
    h = extent[1]-extent[3]
    image_w = 600 
    image_h = h * image_w / w
    cellsize = max(w/image_w, h/image_h)
    std_x = std(x)
    std_y = std(y)
    Q_x = quantile(x)
    Q_y = quantile(y)
    IQR_x = Q_x[2] - Q_x[0]
    IQR_y = Q_y[2] - Q_y[0]
    h_x = 0.9 * min(std_x, IQR_x/1.34)*pow(n,-0.2)
    h_y = 0.9 * min(std_y, IQR_y/1.34)*pow(n,-0.2)
    bandwidth = max(h_x,h_y)*2
else:
    cellsize = float(cellsize)
    bandwidth = float(bandwidth)

itv_pts_ids = range(n)
arr,rows,cols,gmin,gmax = call_kde(n,x,y,itv_pts_ids,extent,bandwidth,cellsize,kernel,gradient,opaque)
fromarray(arr).save("test1.png")
