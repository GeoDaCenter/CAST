%module OGWrapper

%{
#include "OGWrapper.h"
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

#include <vector>

bool OGIsLineShapeFile(char* fname);

bool OGCreateGal(char* shpname,
				 char* galname,
				 char* id,
                 std::vector<int>& id_vec,
				 int is_rook,
				 int ooC,
				 int is_include_lower);

bool OGCreateGwt(char* gwtname,
                 char* id,
                 std::vector<int>& id_vec,
				 std::vector<double>& x,
				 std::vector<double>& y,
				 double threshold,
				 int k,
				 int method);

double OGComputeCutOffPoint(std::vector<double>& x,
				            std::vector<double>& y,
							int method);
							
double OGComputeMaxDistance(std::vector<double>& x,
				            std::vector<double>& y,
							int method);