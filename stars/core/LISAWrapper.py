"""
"""

__author__='Xun Li <xunli@asu.edu>'
__all__=[]


from lisa import *
from weights import *
import ctypes
import numpy as np
import os

def call_lisa(data, weight_file, numPermutations):
    n = len(data)
    
    # validate data and weight_file
    o = open(weight_file)
    firstline = o.readline().strip()
    if firstline.find(" ")>=0:
        n_in_w = int(firstline.strip().split(' ')[1])
    else:
        n_in_w = int(firstline)
        
    if n != n_in_w:
        return None
    
    # check the content, convert to CAST style
    import pysal
    pyw = pysal.open(weight_file).read()
    pyw_new = pysal.remap_ids(pyw, pyw.id2i)
    
    weight_file = weight_file[:-4]+"_"+weight_file[-4:]
    tmpw = pysal.open(weight_file,'w')
    tmpw.write(pyw_new)
    tmpw.close()
    
    _data = doubleArray(n)
    for i in range(n):
        _data[i] = float(data[i])
    
    # define some return variables
    dummy_array = [0 for i in range(n)]
    localMoran = VecDouble(dummy_array)
    sigLocalMoran = doubleArray(n)
    sigFlag = intArray(n)
    clusterFlag = intArray(n)
  
    # read weights file
    suffix = weight_file[-3:]
    if suffix == "gal":
        wfile = GalWeight(weight_file)
    elif suffix == "gwt":
        wfile = GwtWeight(weight_file)
    else:
        os.remove(weight_file)
        return None
        
    weights = wfile.gal
   
    # call lisa
    GeodaLisa_LISA(
        n, 
        _data, 
        weights, 
        numPermutations, 
        localMoran, 
        sigLocalMoran,
        sigFlag,
        clusterFlag
    )
    
    # process return results
    _localMoran = []
    _sigLocalMoran = []
    _sigFlag = []
    _clusterFlag = []
    
    for i in range(n):
        _localMoran.append(localMoran[i])
        _sigLocalMoran.append(sigLocalMoran[i])
        _sigFlag.append(sigFlag[i])
        _clusterFlag.append(clusterFlag[i])
       
    os.remove(weight_file)
    
    return _localMoran, _sigLocalMoran, _sigFlag, _clusterFlag
    
if __name__=='__main__':
    #data = [16, 22, 28, 22, 19, 14, 27, 42, 17,  5, 27, 28, 16, 13,  9]
    #localMoran, sigLM, sigFlag, clusterFlag = call_lisa(data,'Data_and_Rates_for_Beats.gal', 999)
    import pysal
    dbf = pysal.open('NAT.dbf','r')
    data = dbf.by_col('FH90')
    localMoran, sigLM, sigFlag, clusterFlag = call_lisa(data,'NATQ.gal', 999)
