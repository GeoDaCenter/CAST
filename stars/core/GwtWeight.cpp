/**
 * OpenGeoDa TM, Copyright (C) 2011 by Luc Anselin - all rights reserved
 *
 * This file is part of OpenGeoDa.
 * 
 * OpenGeoDa is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * OpenGeoDa is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <climits>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <iostream>
#include <stdint.h>

#include "GalWeight.h"
#include "GwtWeight.h"

double GwtElement::SpatialLag(const std::vector<double>& x,
							  const bool std) const
{
	double    lag= 0;
	int cnt = 0;
	for (cnt= Size() - 1; cnt >= 0; cnt--) {
		//lag += data[cnt].weight * x[ data[cnt].nbx ];
		lag += x[ data[cnt].nbx ];
	}
	if (std && Size() > 1) lag /= Size();
	return lag;
}

double GwtElement::SpatialLag(const double *x, const bool std) const  {
	double    lag= 0;
	int cnt = 0;
	for (cnt= Size() - 1; cnt >= 0; cnt--) {
		//lag += data[cnt].weight * x[ data[cnt].nbx ];
		lag += x[ data[cnt].nbx ];
	}
	if (std && Size() > 1) lag /= Size();
	return lag;
}

double GwtElement::SpatialLag(const DataPoint *x, const bool std) const  {
	double    lag= 0;
	int cnt = 0;
	for (cnt= Size() - 1; cnt >= 0; cnt--) {
		//lag += data[cnt].weight * x[ data[cnt].nbx ].horizontal; 
		lag += x[ data[cnt].nbx ].horizontal;
	}
	if (std && Size() > 1) lag /= Size();
	return lag;
}

double GwtElement::SpatialLag(const DataPoint *x, 
							  const int * perm, const bool std) const  {
	double    lag = 0;
	int cnt = 0;
	for (cnt = Size() - 1; cnt >= 0; cnt--) {
		//lag += data[cnt].weight * x[ perm[ data[cnt].nbx ] ].horizontal;
		lag += x[ perm[ data[cnt].nbx ] ].horizontal;
	}
	if (std && Size() > 1) lag /= Size();
	return lag;
}

long* GwtElement::GetData() const
{
	long* dt = new long[nbrs];
	for (int i=0;i<nbrs;i++) dt[i] = data[i].nbx;
	return dt;
}

GalElement* GwtWeight::ReadGwtAsGal(const char* fname)
{
	using namespace std;
	ifstream file;
	file.open(fname, ios::in);  // a text file
	if (!(file.is_open() && file.good())) {
		return 0;
	}
	// First determine if header line is correct
	// Can be either: int int string string  (type n_obs filename field)
	// or : int (n_obs)
	
	bool use_rec_order = false;
	string str;
	getline(file, str);
	cout << str << endl;
	stringstream ss(str, stringstream::in | stringstream::out);
	
	int64_t num1 = 0;
	int64_t num2 = 0;
	int64_t num_obs = 0;	
	string dbf_name, t_key_field;
	ss >> num1 >> num2 >> dbf_name >> t_key_field;
	
	if (num2 == 0) {
		use_rec_order = true;
		num_obs = num1;
	} else {
		num_obs = num2;
		if (t_key_field.length()>0) {
			use_rec_order = true;
		}
	}
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	
	map<int64_t, int> id_map;
	if (use_rec_order) {
		// we need to traverse through every line of the file and
		// record the max and min values.  So long as the max and min
		// values are such that num_obs = (max - min) + 1, we will assume
		// record order is valid.
		int64_t min_val = LLONG_MAX;
		int64_t max_val = LLONG_MIN;
		while (!file.eof()) {
			int64_t obs1=0, obs2=0;
			getline(file, str);
			if (!str.empty()) {
				stringstream ss (str, stringstream::in | stringstream::out);
				ss >> obs1 >> obs2;
				if (obs1 < min_val) {
					min_val = obs1;
				} else if (obs1 > max_val) {
					max_val = obs1;
				}
				if (obs2 < min_val) {
					min_val = obs2;
				} else if (obs2 > max_val) {
					max_val = obs2;
				}
			}
		}
		if (max_val - min_val != num_obs - 1) {
			return 0;
		}
		for (int i=0; i<num_obs; i++) id_map[i+min_val] = i;
	} else 
	{
	}
	
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	// we need to traverse through every line of the file and
	// record the number of neighbors for each observation.
	map<int64_t, int>::iterator it;
	map<int64_t, int> nbr_histogram;
	while (!file.eof()) {
		int64_t obs1=0;
		getline(file, str);
		if (!str.empty()) {
			stringstream ss (str, stringstream::in | stringstream::out);
			ss >> obs1;
			it = nbr_histogram.find(obs1);
			if (it == nbr_histogram.end()) {
				nbr_histogram[obs1] = 1;
			} else {
				nbr_histogram[obs1] = (*it).second + 1;
			}
		}
	}
	
	GalElement* gal = new GalElement[num_obs];
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	map<int64_t, int>::iterator it1;
	map<int64_t, int>::iterator it2;
	int line_num=1;
	while (!file.eof()) {
		int gwt_obs1, gwt_obs2;
		int64_t obs1, obs2;
		getline(file, str);
		if (!str.empty()) {
			stringstream ss(str, stringstream::in | stringstream::out);
			ss >> obs1 >> obs2;
			it1 = id_map.find(obs1);
			it2 = id_map.find(obs2);
			if (it1 == id_map.end() || it2 == id_map.end()) {
				int obs;
				if (it1 == id_map.end()) obs = obs1;
				if (it2 == id_map.end()) obs = obs2;
				delete [] gal;
				return 0;
			}
			gwt_obs1 = (*it1).second; // value
			gwt_obs2 = (*it2).second; // value
			if (gal[gwt_obs1].empty()) {
				gal[gwt_obs1].alloc(nbr_histogram[obs1]);
			}
			gal[gwt_obs1].Push(gwt_obs2);
		}
		line_num++;
	}	
	
	file.clear();
	if (file.is_open()) file.close();
	
	return gal;
}

/** This function should not be used unless an actual GWT object is needed
 internally.  In most cases, the ReadGwtAsGal function should be used */
GwtElement* GwtWeight::ReadGwt(const char* fname)
								 //DbfGridTableBase* grid_base)
{
	using namespace std;
	ifstream file;
	file.open(fname, ios::in);  // a text file
	if (!(file.is_open() && file.good())) {
		return 0;
	}
	
	// First determine if header line is correct
	// Can be either: int int string string  (type n_obs filename field)
	// or : int (n_obs)
	
	bool use_rec_order = false;
	string str;
	getline(file, str);
	cout << str << endl;
	stringstream ss(str, stringstream::in | stringstream::out);
	
	int64_t num1 = 0;
	int64_t num2 = 0;
	int64_t num_obs = 0;	
	string dbf_name, t_key_field;
	ss >> num1 >> num2 >> dbf_name >> t_key_field;
	string key_field(t_key_field);
	if (num2 == 0) {
		use_rec_order = true;
		num_obs = num1;
	} else {
		num_obs = num2;
		if (key_field.length()==0) {
			use_rec_order = true;
		}
	}
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	map<int64_t, int> id_map;
	if (use_rec_order) {
		// we need to traverse through every line of the file and
		// record the max and min values.  So long as the max and min
		// values are such that num_obs = (max - min) + 1, we will assume
		// record order is valid.
		int64_t min_val = LLONG_MAX;
		int64_t max_val = LLONG_MIN;
		while (!file.eof()) {
			int64_t obs1=0, obs2=0;
			getline(file, str);
			if (!str.empty()) {
				stringstream ss (str, stringstream::in | stringstream::out);
				ss >> obs1 >> obs2;
				if (obs1 < min_val) {
					min_val = obs1;
				} else if (obs1 > max_val) {
					max_val = obs1;
				}
				if (obs2 < min_val) {
					min_val = obs2;
				} else if (obs2 > max_val) {
					max_val = obs2;
				}
			}
		}
		if (max_val - min_val != num_obs - 1) {
			return 0;
		}
		for (int i=0; i<num_obs; i++) id_map[i+min_val] = i;
	} else {
	}
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	// we need to traverse through every line of the file and
	// record the number of neighbors for each observation.
	map<int64_t, int>::iterator it;
	map<int64_t, int> nbr_histogram;
	while (!file.eof()) {
		int64_t obs1=0;
		getline(file, str);
		if (!str.empty()) {
			stringstream ss (str, stringstream::in | stringstream::out);
			ss >> obs1;
		
			it = nbr_histogram.find(obs1);
			if (it == nbr_histogram.end()) {
				nbr_histogram[obs1] = 1;
			} else {
				nbr_histogram[obs1] = (*it).second + 1;
			}
		}
	}
	
	GwtElement* gwt = new GwtElement[num_obs];
	file.clear();
	file.seekg(0, ios::beg); // reset to beginning
	getline(file, str); // skip header line
	map<int64_t, int>::iterator it1;
	map<int64_t, int>::iterator it2;
	int line_num = 1;
	while (!file.eof()) {
		int gwt_obs1, gwt_obs2;
		int64_t obs1, obs2;
		getline(file, str);
		if (!str.empty()) {
			stringstream ss(str, stringstream::in | stringstream::out);
			ss >> obs1 >> obs2;
			it1 = id_map.find(obs1);
			it2 = id_map.find(obs1);
			if (it1 == id_map.end() || it2 == id_map.end()) {
				int obs;
				if (it1 == id_map.end()) obs = obs1;
				if (it2 == id_map.end()) obs = obs2;
				delete [] gwt;
				return 0;
			}
			gwt_obs1 = (*it1).second; // value
			gwt_obs2 = (*it2).second; // value
			if (gwt[gwt_obs1].empty()) gwt[gwt_obs1].alloc(nbr_histogram[obs1]);
			gwt[gwt_obs1].Push(gwt_obs2);
		}
		line_num++;
	}	
	
	if (file.is_open()) file.close();
	
	return gwt;
}

GalElement* GwtWeight::Gwt2Gal(GwtElement* Gwt, long obs) 
{
	if (Gwt == NULL) return NULL;
	GalElement* Gal = new GalElement[obs];
	
	for (int i=0; i<obs; i++) {
		Gal[i].alloc(Gwt[i].Size());
		for (int j=0; j < Gwt[i].Size(); j++) {
			Gal[i].Push(Gwt[i].data[j].nbx);
		}
	}
	return Gal;
}
