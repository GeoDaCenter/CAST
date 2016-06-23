%module lisa

%include "typemaps.i"

%include "carrays.i"
%array_class(int, intArray);
%array_class(double, doubleArray);

%{
#include "GeoDaConst.h"
#include "Randik.h"
#include "GalWeight.h"
#include "Lisa.h"
%}

%include "std_vector.i"
namespace std {
  %template(VecDouble) vector<double>;
  %template(VecVecDouble) vector< vector<double> >;
  %template(VecInt) vector<int>;
  %template(VecVecInt) vector< vector<int> >;
  %template(VecUINT8) vector<unsigned char>;
  %template(VecVecUINT8) vector<vector<unsigned char> >;
}

/*
 *  Lisa.h
 *  OpenGeoDa
 *
 *  Copyright 2011 ASU. All rights reserved.
 *
 */

#ifndef __GEODA__LISA_H__
#define __GEODA__LISA_H__

/** GeodaLisa will serve as a namespace rather than a class.  Everything
 in GeodaLisa must be static */

#include <vector>
class GalElement;
struct DataPoint;

inline void DevFromMean(int nObs, double* RawData)
{
	double sumX = 0.0;
	int cnt = 0;
	for (cnt= 0; cnt < nObs; ++cnt) 
	{
		sumX += RawData[cnt];
	}
	const double  meanX = sumX / nObs;
	for (cnt= 0; cnt < nObs; ++cnt)
	{
		RawData[cnt] -= meanX;
	}
}	

inline bool StandardizeData(int nObs, double* RawData)
{
	DevFromMean(nObs, RawData);
	double sumX= 0;
	int cnt = 0;
	for (cnt= 0; cnt < nObs; ++cnt)
	{
		sumX += RawData[cnt] * RawData[cnt];
	}
	const double sdevX = sqrt(sumX / (nObs-1));
	if (sdevX == 0.0) 
		return false;
	for (cnt= 0; cnt < nObs; ++cnt)
	{
		RawData[cnt] /= sdevX;
	}
	return true;
}
/** Old code used by LISA functions */
class OgSet {
private:
    int size;
	int current;
    int* buffer;
    char* flags;
public:
	OgSet(const int sz) : size(sz), current(0) {
		buffer = new int [ size ];
		flags = new char [ size ];
		memset(flags, '\x0', size);
	}
	virtual ~OgSet() {
		if (buffer) delete [] buffer; buffer = 0;
		if (flags) delete [] flags; flags = 0;
		size = current = 0;
	}
    bool Belongs( const int elt) const {
		return flags[elt] != 0; }; // true if the elt belongs to the set
    void Push(const int elt) {
		// insert element in the set, if it is not yet inserted
		if (flags[elt] == 0)  {
			buffer[ current++ ] = elt;
			flags[elt] = 'i';  // check elt in
        }
    }
    int Pop() { // remove element from the set
		if (current == 0) return -1; // formerly GeoDaConst::EMPTY
        int rtn= buffer[ --current ];
        flags[rtn]= '\x0';   // check it out
        return rtn;
    }
    int Size() const { return current; }
};

/* clusterFlag: classification for each observation into LISA significance
clusters: not-significant=0 (>0.05) HH=1, LL=2, HL=3, LH=4, isolate=5*/

class GeodaLisa {
public:
	static bool LISA(int nObs,					// The size of data
					 double* Data,				// The input data 
					 GalElement* weights,		// The weight
					 const int numPermutations, // The number of permutation
					 std::vector<double>& localMoran, // The LISA
					 double* sigLocalMoran,		// The significances
					 int* sigFlag,				// The significance category
					 int* clusterFlag);			// The Cluster (HH,LL,LH,HL)
		
	static bool LISA(int nObs,					// The size of data
					 DataPoint* RawData,		// The input data 
					 GalElement* weights,		// The weight
					 const int numPermutations, // The num of permutation
					 std::vector<double>& localMoran,		// The LISA
					 double* sigLocalMoran,		// The significances
					 int* sigFlag,				// The significance category
					 int* clusterFlag);			// The Cluster (HH,LL,LH,HL)
	
	static bool MLISA(int nObs,					// The size of data
					  double* Data1,			// The input data 
					  double* Data2,			// The input data 
					  GalElement* weights,		// The weight
					  const int	numPermutations, // The number of permutation
					  std::vector<double>& localMoran,		// The LISA
					  double* sigLocalMoran,	// The significances
					  int* sigFlag,				// The significance category
					  int* clusterFlag);		// The Cluster (HH,LL,LH,HL)
};
	
#endif
