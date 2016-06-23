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
