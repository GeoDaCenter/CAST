#!/usr/bin/env python

"""
setup.py file for SWIG example
export CFLAGS=`wx-config --cxxflags`
export LDFLAGS=`wx-config --libs`
"""

from distutils.core import setup, Extension


extensions = [Extension('_OGWrapper',
                        sources=[
                            'OGWrapper_wrap.cxx', 
                            'OGWrapper.cpp', 
                            'ShapeOperations/AbstractShape.cpp',
                            'ShapeOperations/BasePoint.cpp',
                            'ShapeOperations/Box.cpp',
                            'ShapeOperations/GalWeight.cpp',
                            'ShapeOperations/GwtWeight.cpp',
                            'ShapeOperations/ShapeFile.cpp',
                            'ShapeOperations/ShapeFileHdr.cpp',
                            'ShapeOperations/shp2cnt.cpp',
                            'ShapeOperations/shp2gwt.cpp',
                            'ShapeOperations/ShpFile.cpp',
                            'ShapeOperations/shp.cpp',
                            'logger.cpp',
                            'GenGeomAlgs.cpp',
                            'GenUtils.cpp',
                            'GeoDaConst.cpp',
                            'kNN/ANN.cpp',
                            'kNN/kd_tree.cpp',
                            'kNN/kd_search.cpp',
                            'kNN/kd_pr_search.cpp',
                            'kNN/kd_split.cpp',
                            'kNN/kd_util.cpp'
                        ],
                        )
              ]

setup (name = 'CAST',
       version = '0.1',
       author      = "Xun Li",
       description = """Python wrapper for C++ KDE/LISA/Weigth""",
       ext_modules = extensions,
       py_modules = ["OGWrapper"],
       )




