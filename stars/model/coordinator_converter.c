/* Copyright (c) 2012 by Xun LI 
 * Authors:
 * Xun Li <xunli@asu.edu>
 *
 */


#include <Python.h>
#include <math.h>

#include "shapefil.h"
#include "pyshapelib_api.h"

PyShapeLibAPI * api;

static PyObject * map_dict = NULL;

static PyObject *
clean(PyObject * self, PyObject * args)
{
    // NOTE: the value (key:value pairs) returned to 
    // python, holds a reference, which is shared with
    // this c extension. Delete that reference in Python
    // also impact the reference here.
    //PyDict_Clear(map_dict);
    Py_XDECREF(map_dict);
    map_dict = NULL;
    Py_RETURN_TRUE;
}

static PyObject *
read_centroids(PyObject * self, PyObject * args)
{
    SHPHandle hSHP;
    PyObject * cobject;

    if (!PyArg_ParseTuple(args, "O!", &PyCObject_Type, &cobject))
        return NULL;

    hSHP = PyCObject_AsVoidPtr(cobject);
    
    int nEntities;
    int nShapeType;

    SHPGetInfo(hSHP, &nEntities, &nShapeType, NULL, NULL);
    PyObject * list = NULL, * parts = NULL, * point = NULL, *px = NULL, *py = NULL;

    SHPObject * psCShape;
    int i,j,count;
    double x,y;

    list = PyList_New(nEntities);
   
    for (i=0; i< nEntities; i++)
    {   
        psCShape = SHPReadObject( hSHP, i);   
    
        if (psCShape->nSHPType == SHPT_POINT || psCShape->nSHPType == SHPT_POINTZ)
        {
            /*
            x = psCShape->centroidXX[0];
            y = psCShape->centroidYY[0];
            point = Py_BuildValue("(dd)", x,y);
            PyList_SetItem(list, i, point);
            */
            return PyList_New(0);
        }
        else if (psCShape->nSHPType == SHPT_POLYGON || psCShape->nSHPType == SHPT_POLYGONZ)
        {   
            // read polygons from shp file
            count = psCShape->nParts > 1 ? psCShape->nParts : 1;
            parts = PyList_New(count);

            for (j=0; j <psCShape->nParts; j++)
            { 
                x = psCShape->centroidXX[j];
                y = psCShape->centroidYY[j];
                
                //point = Py_BuildValue("(dd)", x,y);
                px = PyFloat_FromDouble(x);
                py = PyFloat_FromDouble(y);
                point = PyTuple_New(2);
                PyTuple_SetItem(point, 0, px);
                PyTuple_SetItem(point, 1, py);
                
                PyList_SetItem(parts,j,point);
            }   
            PyList_SetItem(list, i, parts);
        }
        SHPDestroyObject(psCShape);
    }    
    return list;
}


static PyObject *
read_objects(PyObject * self, PyObject * args)
{
    SHPHandle hSHP;
    PyObject * cobject;
    char * shape_name;

    if (!PyArg_ParseTuple(args, "O!s", &PyCObject_Type, &cobject, &shape_name))
        return NULL;

    hSHP = PyCObject_AsVoidPtr(cobject);
    
    // check if already in memory
    if (map_dict != NULL)
    {
        PyObject * result = PyDict_GetItemString(map_dict, shape_name);
        if (result != NULL)
            return result;
    }
    
    int nEntities;
    int nShapeType;

    SHPGetInfo(hSHP, &nEntities, &nShapeType, NULL, NULL);

    PyObject * list = NULL, * parts = NULL, * point = NULL, *vertices = NULL, *px = NULL, *py = NULL;

    SHPObject * psCShape;
    int i,j,k,s,count,numPoints;
    double x,y;

    list = PyList_New(nEntities);
   
    for (i=0; i< nEntities; i++)
    {   
        psCShape = SHPReadObject( hSHP, i);   
    
        if (psCShape->nSHPType == SHPT_POINT || psCShape->nSHPType == SHPT_POINTZ)
        {
            // read points from shp file
            numPoints = psCShape->nVertices; 
            
            for (j=0; j < numPoints; j++)
            {
                x = psCShape->padfX[j];
                y = psCShape->padfY[j];
       
                //point = Py_BuildValue("(dd)", x,y);
                px = PyFloat_FromDouble(x);
                py = PyFloat_FromDouble(y);
                point = PyTuple_New(2);
                PyTuple_SetItem(point, 0, px);
                PyTuple_SetItem(point, 1, py);
                
                PyList_SetItem(list, i, point);
            } 
        }
        else if (psCShape->nSHPType == SHPT_POLYGON || psCShape->nSHPType == SHPT_POLYGONZ)
        {   
            // read polygons from shp file
            count = psCShape->nParts > 1 ? psCShape->nParts : 1;
            parts = PyList_New(count);

            for (j=0; j <psCShape->nParts; j++)
            { 
                if ( j < psCShape->nParts - 1)
                    numPoints = psCShape->panPartStart[j+1] - psCShape->panPartStart[j];
                else
                    numPoints = psCShape->nVertices - psCShape->panPartStart[j];
               
                s = psCShape->panPartStart[j]; 
                vertices = PyList_New(numPoints);
    
                for (k=0; k < numPoints; k++)
                {
                    x = psCShape->padfX[s+k];
                    y = psCShape->padfY[s+k];
                                
                    px = PyFloat_FromDouble(x);
                    py = PyFloat_FromDouble(y);
                    point = PyTuple_New(2);
                    PyTuple_SetItem(point, 0, px);
                    PyTuple_SetItem(point, 1, py);
                    PyList_SetItem(vertices, k, point);
                }
                PyList_SetItem(parts,j,vertices);
            }   
            PyList_SetItem(list, i, parts);
        }
        SHPDestroyObject(psCShape);
    }    
    
    // store the list
    if (map_dict == NULL)
    {
        map_dict = PyDict_New();
    }
    PyDict_SetItemString(map_dict, shape_name, list);
    //Py_DECREF(list);
    
    return list;
}

/*********************************

following is for coordinate system

----------------------------------*/

static PyObject *
coordinator_convert(PyObject * self, PyObject * args)
{
    char * shape_name;
    double extent[4];
    int pixel_width = 0;
    int pixel_height = 0;
    int fixed_ratio = 1;
    int offset_x = 0;
    int offset_y = 0;
    int pan_offset_x = 0;
    int pan_offset_y = 0;
    double scaleX = 0.9;
    double scaleY = 0.9;
    double ratioX = 0.0;
    double ratioY = 0.0;
    int startX = 0;
    int startY = 0;
    int margin_x = 0;
    int margin_y = 0;
    int offset_from_upperleft = 1;

    SHPHandle hSHP;
    PyObject * cobject;
    PyObject * region;
    PyObject * zoom_region;

    if (!PyArg_ParseTuple(args, "O!siiiiiiOO", &PyCObject_Type,
        &cobject, 
        &shape_name,
        &pixel_width, 
        &pixel_height, 
        &offset_x, 
        &offset_y, 
        &pan_offset_x, 
        &pan_offset_y, 
        &region,
        &zoom_region))
        return NULL;
    
    hSHP = PyCObject_AsVoidPtr(cobject);
    
    int nEntities;
    int nShapeType;
    double adfBoundsMin[4], adfBoundsMax[4]; 
    int i,j,k,s,nParts,count,numPoints;
        
    SHPGetInfo(hSHP, &nEntities, &nShapeType, adfBoundsMin, adfBoundsMax);
    extent[0] = adfBoundsMin[0];
    extent[1] = adfBoundsMin[1];
    extent[2] = adfBoundsMax[0];
    extent[3] = adfBoundsMax[1];

    if (PyList_Size(region) > 0)
    {
        for (i =0; i<4;++i)        
            extent[i] = PyFloat_AsDouble(PyList_GetItem(region,i));
    }
    
    double view_width = fabs(extent[0] - extent[2]);
    double view_height = fabs(extent[1] - extent[3]);

    if (fixed_ratio == 1)
    {
        if ((double)(pixel_width)/(double)(pixel_height) < view_width/view_height)
        {
            ratioX = pixel_width/view_width;
            ratioY = ratioX;
            startY = (int)((pixel_height-view_height*ratioY)/2.0);
        }
        else
        {
            ratioY = pixel_height/view_height;
            ratioX = ratioY;
            startX = (int)((pixel_width-view_width*ratioX)/2.0);
        }
    }
    else
    {
        ratioX = pixel_width / view_width;
        ratioY = pixel_height / view_height;
    }

    margin_x = (int)(pixel_width * (1-scaleX) / 2.0); 
    margin_y = (int)(pixel_height* (1-scaleY) / 2.0); 
   
    double x,y,tmp_px,tmp_py,prev_x,prev_y,one_pixel_view_x,one_pixel_view_y;
    
    // get zoom parameters
    if (PyList_Size(zoom_region) > 0)
    {
        for (i =0; i<4;++i)        
            extent[i] = PyFloat_AsDouble(PyList_GetItem(zoom_region,i));
            
        view_width = fabs(extent[0] - extent[2]);
        view_height = fabs(extent[1] - extent[3]);
    
        if ((double)(pixel_width)/(double)(pixel_height) < view_width/view_height)
        {
            ratioX = pixel_width/view_width;
            ratioY = ratioX;
            startY = (int)((pixel_height-view_height*ratioY)/2.0);
        }
        else
        {
            ratioY = pixel_height/view_height;
            ratioX = ratioY;
            startX = (int)((pixel_width-view_width*ratioX)/2.0);
        }
    
        margin_x = (int)(pixel_width * (1-scaleX) / 2.0); 
        margin_y = (int)(pixel_height* (1-scaleY) / 2.0); 
    }
    
    // converter coordinators
    PyObject * objects = PyDict_GetItemString(map_dict, shape_name); 
    
    if (objects == NULL)
        return PyList_New(0);
   
    PyObject * list = NULL, * parts = NULL, * point = NULL;
    PyObject *vertices = NULL, *px = NULL, *py =NULL;
    PyObject *_point=NULL,*_px=NULL,*_py=NULL;
    PyObject *polygon=NULL,*part = NULL;

    list = PyList_New(nEntities);
    
    for (i=0; i< nEntities; i++)
    {   
        if (nShapeType == SHPT_POINT || nShapeType == SHPT_POINTZ)
        {
            _point = PyList_GetItem(objects, i);            
            _px = PyTuple_GetItem(_point, 0); 
            _py = PyTuple_GetItem(_point, 1); 
           
            x = PyFloat_AsDouble(_px); 
            y = PyFloat_AsDouble(_py); 
       
            tmp_px = pan_offset_x + startX + ratioX * (x - extent[0]);
            tmp_px = round(offset_x + tmp_px * scaleX + margin_x);
            
            tmp_py = pixel_height - pan_offset_y - startY - ratioY * (y-extent[1]);
            tmp_py = round(offset_y + tmp_py * scaleY + margin_y);

            px = PyInt_FromLong((int)tmp_px);
            py = PyInt_FromLong((int)tmp_py);
            point = PyTuple_New(2);
            
            PyTuple_SetItem(point, 0, px);
            PyTuple_SetItem(point, 1, py);
                
            PyList_SetItem(list, i, point);
        }
        else if (nShapeType == SHPT_POLYGON || nShapeType == SHPT_POLYGONZ)
        {  
            polygon = PyList_GetItem(objects, i);
            nParts = (int)PyList_Size(polygon);
            
            parts = PyList_New(nParts);
            
            for (j=0; j < nParts; j++)
            { 
                part = PyList_GetItem(polygon, j);
                numPoints = (int)PyList_Size(part);
                
                vertices = PyTuple_New(numPoints);
                for (k=0; k < numPoints; k++)
                {
                    _point = PyList_GetItem(part, k);
                    _px = PyTuple_GetItem(_point, 0); 
                    _py = PyTuple_GetItem(_point, 1); 
                    
                    x = PyFloat_AsDouble(_px); 
                    y = PyFloat_AsDouble(_py); 
           
                    tmp_px = pan_offset_x + startX + ratioX * (x - extent[0]);
                    tmp_px = offset_x + tmp_px * scaleX + margin_x;
            
                    tmp_py = pixel_height - pan_offset_y - startY - ratioY * (y-extent[1]);
                    tmp_py = offset_y + tmp_py * scaleY + margin_y;

                    px = PyInt_FromLong((int)tmp_px);
                    py = PyInt_FromLong((int)tmp_py);
                    point = PyTuple_New(2);
                    PyTuple_SetItem(point, 0, px);
                    PyTuple_SetItem(point, 1, py);
                    PyTuple_SetItem(vertices, k, point);
                }
                PyList_SetItem(parts,j,vertices);
            }   
            PyList_SetItem(list, i, parts);
        }
    }    
    return list;
}


static PyObject *
pnpolygon(PyObject * self, PyObject * args)
{
    PyObject * cobject;
    PyObject * qPoints;
    
    if (!PyArg_ParseTuple(args, "O!O", &PyCObject_Type, &cobject, &qPoints))
        return NULL;
        
        
    int nEntities;
    int nShapeType;
    SHPHandle hSHP;

    hSHP = PyCObject_AsVoidPtr(cobject);
    SHPGetInfo(hSHP, &nEntities, &nShapeType, NULL, NULL);

    SHPObject * psCShape;
    int c,i,j,k,l,n,s,count,numQueries,numPoints;
    double x,y,testx,testy, x_k,y_k,x_l,y_l;
    double bbox[4];

    numQueries = PyList_Size(qPoints);
    PyObject* rtn_polys_id = PyList_New(numQueries);
    
    // set default values
    for (n=0; n<numQueries; n++)
       PyList_SetItem(rtn_polys_id,n, PyInt_FromLong(-1));

    // set flag for founded query points
    int* pointFlags = (int*)malloc(numQueries * sizeof(int));
    for (n=0; n<numQueries; n++)
        pointFlags[n] = 0;
        
    PyObject* query_dict = PyDict_New();
    
    for (i=0; i< nEntities; i++)
    {   
        psCShape = SHPReadObject( hSHP, i);   
    
        bbox[0] =  psCShape->dfXMin;
        bbox[1] =  psCShape->dfYMin; 
        bbox[2] =  psCShape->dfXMax; 
        bbox[3] =  psCShape->dfYMax;
            
        for (n=0; n<numQueries; n++)
        {
            if (pointFlags[n] == 1)
                continue; // already found polygon for this point, continue to next
                
            PyObject* qPoint = PyList_GetItem(qPoints,n);
            Py_INCREF(qPoint); // protect qPoint
            
            if (PyDict_Contains(query_dict, qPoint)) // have same point (been found)
            {
                PyObject* value = PyDict_GetItem(query_dict, qPoint);
                Py_INCREF(value);
                PyList_SetItem(rtn_polys_id,n, value);
                pointFlags[n] = 1;
                
                Py_DECREF(qPoint);
                continue;
            }
            
            PyObject* pointX = PyTuple_GetItem(qPoint,0);
            PyObject* pointY = PyTuple_GetItem(qPoint,1);
            testx = PyFloat_AsDouble(pointX);
            testy = PyFloat_AsDouble(pointY);
            
            if (testx >= bbox[0] && testx <= bbox[2] && testy >=bbox[1] && testy <=bbox[3]) 
            {
                c = 0;
                count = psCShape->nParts > 1 ? psCShape->nParts : 1;
                
                for (j=0; j <psCShape->nParts; j++)
                { 
                    if ( j < psCShape->nParts - 1)
                        numPoints = psCShape->panPartStart[j+1] - psCShape->panPartStart[j];
                    else
                        numPoints = psCShape->nVertices - psCShape->panPartStart[j];
                   
                    s = psCShape->panPartStart[j]; 
        
                    for (k = 0, l = numPoints-1; k < numPoints; l = k++) 
                    {
                        x_k = psCShape->padfX[s+k];
                        y_k = psCShape->padfY[s+k];
                        x_l = psCShape->padfX[s+l];
                        y_l = psCShape->padfY[s+l];
                        if ( ((y_k>testy) != (y_l>testy)) &&
                             (testx < (x_l-x_k) * (testy-y_k) / (y_l-y_k) + x_k) )
                             c = !c;
                    }
                    
                    if (c)
                    {
                        PyObject* poly_id = PyInt_FromLong(i);
                        Py_INCREF(poly_id);
                        Py_INCREF(qPoint);
                        
                        PyList_SetItem(rtn_polys_id,n, poly_id);
                        PyDict_SetItem(query_dict, qPoint, poly_id);

                        Py_DECREF(poly_id);
                        Py_DECREF(qPoint);
                        
                        pointFlags[n] = 1;
                        break;
                    }
                }  
            }
            
            Py_DECREF(qPoint);
        }
        SHPDestroyObject(psCShape);
    }    
   
    PyDict_Clear(query_dict);
    Py_DECREF(query_dict);
    free(pointFlags);
        
    return rtn_polys_id;
}

static PyMethodDef module_functions[] = {
    {"convert",		coordinator_convert,		METH_VARARGS},
    {"read_objects",	read_objects,   		METH_VARARGS},
    {"centroids",	    read_centroids,   		METH_VARARGS},
    {"clean",	    clean,   		METH_VARARGS},
    {"pnpolygon",	    pnpolygon,   		METH_VARARGS},
    { NULL, NULL }
};


void
initcoordinator()
{
    PYSHAPELIB_IMPORT_API(api);
    Py_InitModule("coordinator", module_functions);
}
