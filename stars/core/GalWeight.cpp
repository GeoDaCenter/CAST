#include <climits>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <stdint.h>

#include "GalWeight.h"

//*** compute spatial lag for a contiguity weights matrix
//*** optionally (default) performs standardization of the result
double GalElement::SpatialLag(const std::vector<double>& x,
							  const bool std) const  {
	double    lag= 0;
	for (int  cnt= Size(); cnt > 0; )
		lag += x[ data[--cnt] ];
	if (std && Size() > 1)
		lag /= Size();
	return lag;
}

//*** compute spatial lag for a contiguity weights matrix
//*** optionally (default) performs standardization of the result
double GalElement::SpatialLag(const double *x, const bool std) const  {
	double    lag= 0;
	for (int  cnt= Size(); cnt > 0; )
		lag += x[ data[--cnt] ];
	if (std && Size() > 1)
		lag /= Size();
	return lag;
}

//*** compute spatial lag for a contiguity weights matrix
//*** optionally (default) performs standardization of the result
double GalElement::SpatialLag(const DataPoint *x, const bool std) const  {
	double    lag= 0;
	for (int cnt= Size(); cnt > 0; )
		lag += x[ data[--cnt] ].horizontal;
	if (std && Size() > 1)
		lag /= Size();
	return lag;
}

//*** compute spatial lag for a contiguity matrix, with a given permutation
//*** optionally (default) performs standardization
double GalElement::SpatialLag(const DataPoint *x, const int * perm,
							  const bool std) const  {
	double    lag = 0;
	for (int cnt = Size(); cnt > 0; )
		lag += x[ perm[ data[--cnt] ] ].horizontal;
	if (std && Size() > 1)
		lag /= Size();
	return lag;
}

double GalElement::SpatialLag(const double *x, const int * perm,
							  const bool std) const  
{
	double    lag = 0;
	for (int cnt = Size(); cnt > 0; )
		lag += x[ perm[ data[--cnt]]];
	if (std && Size() > 1)
		lag /= Size();
	return lag;
}

void GalElement::Write(std::ofstream &out) const 
{
	const long val = Size();
	out.write((char *) &val, sizeof(long));
	
	if (Size())
		out.write( (char *) data, sizeof(long) * Size() );
	return;
}


int GalElement::ReadTxt(std::ifstream &in, long ob)  
{
	// Notes on return:
	// -1 : wrong # of neighbors, too big or negative
	//  0 : doesn't have neighbor
	//  1 : good
	
	long id; int dim; long mydt;
	in >> id >> dim;
	//	wxString xx;xx.Format("709:id:%d, dim:%d",id, dim);wxMessageBox(xx);
	
	
	size = dim;
	int obs = ob;
	
	if (size == 0) return 0;
	if (size > obs || size < 0) 
	{
		//		xx.Format("717:size:%d, obs:%d",size,obs);wxMessageBox(xx);
		in.close();
		return -1;
	}
	
	data = new long [ size ];
	if (data == NULL)  
	{
		size = 0;
		return 0;
	}
	for (int i=0;i< size;i++) 
	{
		in >> mydt; 
		data[i] = mydt-1;
		
		if (mydt > obs || mydt < 0) 
		{
			delete [] data;
			size = 0;
			data = NULL;
			return -1;
		}
	}
	return 1;
}


int GalElement::ReadTxt(int dim, long* dt, long ob)  
{
	size = dim;
	int obs = ob;
	if (size == 0) return 0;
	if (size > obs-1) return -1;
	data = new long [ size ];
	if (data == NULL)  
	{
		size = 0;
		return 0;
	}
	
	for (int i=0;i< size;i++) 
	{
		data[i] = dt[i];
		if (data[i] > obs || data[i] < 0) 
		{
			delete [] data;
			size = 0;
			data = NULL;
			return -1;
		}
	}
	
	return 1;
}

void GalElement::Read(std::ifstream &in)  
{
	long   val;
	in.read( (char *) &val, sizeof(long) );
	size = val;
	if (size == 0) return;
	data = new long [ size ];
	if (data == NULL)  {
		size = 0;
		return;
	};
	in.read( (char *) data, sizeof(long) * Size() );
}

GalElement* GalWeight::ReadGal(const char* fname)
{
	//LOG_MSG("Entering WeightUtils::ReadGal");
	using namespace std;
	ifstream file;
	file.open(fname, ios::in);  // a text file
	if (!(file.is_open() && file.good())) {
		return 0;
	}
	
	// First determine if header line is correct
	// Can be either: int int string string  (type n_obs filename field)
	// or : int (n_obs)
	
	int line_cnt = 0;
	bool use_rec_order = true;
	string str;
	getline(file, str);
	line_cnt++;
	stringstream ss (str, stringstream::in | stringstream::out);
	
	int num1 = 0;
	int num2 = 0;
	int num_obs = 0;
	string dbf_name, t_key_field;
	ss >> num1 >> num2 >> dbf_name >> t_key_field;
    
	if (num2 == 0) {
		use_rec_order = true;
		num_obs = num1;
	} else {
		num_obs = num2;
		if (!t_key_field.length()) {
			use_rec_order = true;
		}
	}
	
	// Note: we want to be able to support blank lines.  If an observation
	// has no neighbors, then we'd like to be able to not include the
	// observation, or, if it is recorded, then the following line can
	// either be empty or blank.
	map<int64_t, int> id_map;
	map<int64_t, int>::iterator it;
    
	if (use_rec_order) {
		// LOG_MSG("using record order");
		int64_t min_val = LLONG_MAX;
		int64_t max_val = LLONG_MIN;
		while (!file.eof()) {
			int64_t obs=0, num_neigh=0;
			// get next non-blank line
			str = "";
			while (str.empty() && !file.eof()) {
				getline(file, str);
				line_cnt++;
			}
			if (file.eof()) continue;
			{
				stringstream ss (str, stringstream::in | stringstream::out);
				ss >> obs >> num_neigh;
				if (obs < min_val) {
					min_val = obs;
				} else if (obs > max_val) {
					max_val = obs;
				}
			}
			if (num_neigh > 0) { // ignore the list of neighbors
				// get next non-blank line
				str = "";
				while (str.empty() && !file.eof()) {
					getline(file, str);
					line_cnt++;
				}
				if (file.eof()) continue;
			}
		}
		if (max_val - min_val != num_obs - 1) {
			return 0;
		}
		for (int i=0; i<num_obs; i++) 
            id_map[i+min_val] = i;
	} 
    else
    {
        // using DBF record
        //for (int i=0; i<num_obs; i++) 
        //   id_map[vec[i]] = i;
    }
	
	GalElement* gal = new GalElement[num_obs];
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	line_cnt = 0;
	getline(file, str); // skip header line
	line_cnt++;
	
	while (!file.eof()) 
    {
		int gal_obs;
		int64_t obs, num_neigh;
		// get next non-blank line
		str = "";
		while (str.empty() && !file.eof()) 
        {
			getline(file, str);
			line_cnt++;
		}
		if (file.eof()) 
            continue;
		{
			stringstream ss (str, stringstream::in | stringstream::out);
			ss >> obs >> num_neigh;
			it = id_map.find(obs);
			if (it == id_map.end()) {
				delete [] gal;
				return 0;
			}
			gal_obs = (*it).second; // value
			gal[gal_obs].alloc(num_neigh);
		}
		if (num_neigh > 0) { // skip next of no neighbors
			// get next non-blank line
			str = "";
			while (str.empty() && !file.eof()) 
            {
				getline(file, str);
				line_cnt++;
			}
			if (file.eof())
                continue;
			{
				stringstream ss (str, stringstream::in | stringstream::out);
				for (int j=0; j<num_neigh; j++) {
					long long neigh = 0;
					ss >> neigh;
					it = id_map.find(neigh);
					if (it == id_map.end()) {
						delete [] gal;
						return 0;
					}
					gal[gal_obs].Push((*it).second); // value of id_map[neigh];
				}
			}
		}
	}	
	
	file.clear();
	if (file.is_open()) 
        file.close();
	
	//LOG_MSG("Exiting WeightUtils::ReadGal");
	return gal;
}
