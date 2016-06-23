%module weights

%{
#include "GeoDaConst.h"
#include "GalWeight.h"
#include "GwtWeight.h"
%}


#ifndef __GEODA_CENTER_GWT_WEIGHT_H__
#define __GEODA_CENTER_GWT_WEIGHT_H__

#include <fstream>
#include <vector>
#include "GeoDaConst.h"
#include "GalWeight.h"

class GalElement;
struct DataPoint;

struct GwtNeighbor
{
    long    nbx;
    double  weight;
    GwtNeighbor(const long nb=0, const double w=0) : nbx(nb), weight(w) {}
    void assign(const long nb=0, const double w=0) { nbx=nb;  weight=w; }
};

class GwtElement {
public:
    long nbrs; // current number of neighbors
    GwtNeighbor* data; // list neighborhood
	
public:
    GwtElement(const long sz=0) : data(0), nbrs(0) {
        if (sz > 0) data = new GwtNeighbor[sz]; }
    virtual ~GwtElement() {
        if (data) delete [] data;
        nbrs = 0; }
    bool alloc(const int sz) {
		if (data) delete [] data;
        if (sz > 0) {
			nbrs = 0;
			data = new GwtNeighbor[sz];
		}
        return !empty(); }
    bool empty() const { return data == 0; }
    void Push(const GwtNeighbor &elt) { data[nbrs++] = elt; }
    GwtNeighbor Pop() {
        if (!nbrs) return GwtNeighbor(GeoDaConst::EMPTY);
        return data[--nbrs]; }
    long Size() const { return nbrs; }
    GwtNeighbor elt(const long where) const { return data[where]; }
	GwtNeighbor* dt() const { return data; }
	double SpatialLag(const std::vector<double>& x, const bool std=true) const;
    double SpatialLag(const double* x, const bool std=true) const;
    double SpatialLag(const DataPoint* x, const bool std=true) const;
    double SpatialLag(const DataPoint* x, const int *perm,
					  const bool std=true) const;

	long* GetData() const; // this allocates an array and should be removed
};


class GwtWeight 
{
public:
	GwtWeight(const char* fname) 
	{ 
		gwt = 0;//ReadGwt(fname);
		gal = ReadGwtAsGal(fname);
	}
	~GwtWeight() 
	{ 
		if (gwt) delete [] gwt; gwt = 0; 
		if (gal) delete [] gal; gal = 0; 
	}
	
public:
	GwtElement* gwt;
	GalElement* gal;
	
	static bool HasIsolates(GwtElement *gwt, int num_obs) {
		if (!gwt) return false;
		for (int i=0; i<num_obs; i++) { if (gwt[i].Size() <= 0) return true; }
		return false; }
	
	
	GalElement* ReadGwtAsGal(const char* w_fname);
	GwtElement* ReadGwt(const char* w_fname);//, DbfGridTableBase* grid_base);
	GalElement* Gwt2Gal(GwtElement* Gwt, long obs);
};


#endif
