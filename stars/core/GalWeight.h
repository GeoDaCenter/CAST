#ifndef __GEODA_CENTER_GAL_WEIGHT_H__
#define __GEODA_CENTER_GAL_WEIGHT_H__

#include <vector>
#include <fstream>


#include "GeoDaConst.h"


struct DataPoint
{
    double vertical, horizontal;
    
   // DataPoint(const double h= 0, const double v= 0): vertical(v), horizontal(h) {};
	//DataPoint& operator=(const DataPoint& s) 
    //{ vertical = s.vertical; horizontal = s.horizontal; return *this; }
};

/**
 *
 *  The weight for each observation
 */
class GalElement 
{
public:
    long size; // number of neighbors in data array.
    long* data;

public:
    GalElement(const long sz= 0) : data(0), size(0) {
		if (sz > 0) data = new long[sz]; }
    virtual ~GalElement() {
        if (data) delete [] data;
		size = 0; }
    int alloc (const int sz) {
		if (data) delete [] data;
        if (sz > 0) {
			size = 0;
			data = new long[sz];
		}
        return !empty(); }
    bool empty() const { return data == 0; }
    void Push(const long val) { data[size++] = val; }
    long Pop() {
        if (!size) return GeoDaConst::EMPTY;
        return data[--size]; }
    long Size() const { return size; }
	long elt(const long where) const { return data[where]; }
    long* dt() const { return data; }
	double SpatialLag(const std::vector<double>& x, const bool std=true) const;
    double SpatialLag(const double* x, const bool std=true) const;
    double SpatialLag(const DataPoint* x, const bool std=true) const;
    double SpatialLag(const DataPoint* x, const int* perm,
					  const bool std=true) const;
    double SpatialLag(const double* x, const int* perm,
					  const bool std=true) const;
    void Write(std::ofstream &out) const;
    void Read(std::ifstream &in);
	
	int ReadTxt(std::ifstream &in, long ob);
	int ReadTxt(int dim, long* dt, long ob);
};

class GalWeight 
{
public:
	GalWeight(const char* fname)
    {
        gal = ReadGal(fname);
    }
	~GalWeight() 
    { 
        if (gal) 
            delete [] gal; 
        gal = 0; 
    }
    
public:
	GalElement* gal;
    
	static bool HasIsolates(GalElement *gal, int num_obs) 
    {
		if (!gal) return false;
		for (int i=0; i<num_obs; i++) { 
            if (gal[i].Size() <= 0) return true; 
        }
		return false; 
    }
    
    GalElement* ReadGal(const char* w_fname);
};

#endif
