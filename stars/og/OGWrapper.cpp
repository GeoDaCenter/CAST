#include <vector>

#include "ShapeOperations/shp2cnt.h"
#include "ShapeOperations/shp2gwt.h"

bool OGIsLineShapeFile(char* fname)
{
    return IsLineShapeFile(fname);
}

double OGComputeCutOffPoint(std::vector<double>& x,
				            std::vector<double>& y,
							int method)
{
	return ComputeCutOffPoint(x,y,method);
}
							
							
double OGComputeMaxDistance(std::vector<double>& x,
				            std::vector<double>& y,
							int method)
{
	return ComputeMaxDistance(x,y,method);
}

/**
 *
 */
bool OGCreateGal(char* shpname,
                 char* galname,
				 char* id,
                 std::vector<int>& id_vec,
                 int is_rook,
                 int ooC,
                 int is_include_lower
                 )
{
	int num_obs = (int)(id_vec.size());	
	
	// create gal
    GalElement* gal = shp2gal(shpname, (is_rook? 1:0),true);
	GalElement* Hgal = 0;
    
    if (!gal)
        return false;
		
	bool flag = false;
	
    if (ooC > 1)
	{
        Hgal = HOContiguity(ooC, num_obs, gal, is_include_lower);
	    flag = SaveGal(Hgal, galname, id, id_vec);
	}
	else
	    flag = SaveGal(gal, galname, id, id_vec);

	if (Hgal)
		delete[] Hgal;
	delete[] gal;
		
	//delete &id_vec;
	
	return flag;
}


/**
 *
 */
bool OGCreateGwt(char* gwtname,
                 char* id,
				 std::vector<int>& id_vec,
				 std::vector<double>& x,
				 std::vector<double>& y,
				 double threshold,
				 int k,
				 int method)
{
	int num_obs = (int)(x.size());
	// create gwt
	GwtElement* gwt = 0;
	int degree = 1;
		
	if (threshold > 0 && k ==0)
		gwt = shp2gwt(num_obs, x, y, threshold, degree, method);
	else if (threshold == .0 && k > 0)
		gwt = DynKNN(x, y, k+1, method);	
	else
		return false;
	
	if (gwt == 0)
		return false;
		
	// save file
	bool geodaL = true; // geoda legacy format
	bool flag = false;

	if (threshold > 0 && k ==0)
		flag = WriteGwt(gwt, gwtname, id, id_vec, 1, geodaL);
	else if (threshold == .0 && k > 0)
		flag = WriteGwt(gwt, gwtname, id, id_vec, -2, geodaL);
	
	delete[] gwt;
	gwt = 0;
	
	//delete &id_vec;
	
	return flag;
}
				 
				 