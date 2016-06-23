/**
 *  GeoDaConst.h
 *  OpenGeoDa
 *
 *  Created by Mark McCann on 5/20/10.
 *  Copyright 2011 ASU. All rights reserved.
 *
 *  This file is the place to hold all constants such as default colors,
 *  as well as common text strings used in various dialogs.  Everything
 *  should be kept in the GeoDaConst namespace
 *
 */

#ifndef __GEODA_CENTER_GEODACONST_H__
#define __GEODA_CENTER_GEODACONST_H__


class GeoDaConst {	
public:
	static const int EMPTY = -1;
	
	// This should be called only once in MyApp::OnInit()
	static void init();
	
	// Types for use in Table
	enum FieldType {
		unknown_type,
		double_type, // N or F with decimals > 0 in DBF
		long64_type, // N or F with decimals = 0 in DBF
		string_type, // C in DBF, max 254 characters
		date_type // D in DBF, YYYYMMDD format
	};
	
	static const int max_dbf_numeric_len = 20; // same for long and double
	static const int max_dbf_long_len = 20;
	static const int min_dbf_long_len = 1;
	static const int default_dbf_long_len = 18;
	static const int max_dbf_double_len = 20;
	static const int min_dbf_double_len = 2; // allow for "0." always
	static const int default_dbf_double_len = 18;
	static const int max_dbf_double_decimals = 15;
	static const int min_dbf_double_decimals = 1;
	static const int default_dbf_double_decimals = 7;
	static const int max_dbf_string_len = 254;
	static const int min_dbf_string_len = 1;
	static const int default_dbf_string_len = 40;
	static const int max_dbf_date_len = 8;
	static const int min_dbf_date_len = 8;
	static const int default_dbf_date_len = 8;
	
	// Standard wxFont pointers.
	
	// MyShape constantants
	 
	// MyPoint radius to give a larger target for clicking on
	static const int my_point_click_radius = 3;
	
	// Shared Colours
	
	// The following are defined in shp2cnt and should be moved from there.
	
	// Template Canvas shared by Map, Scatterplot, PCP, etc
	static const int default_virtual_screen_marg_left = 20;
	static const int default_virtual_screen_marg_right = 20;
	static const int default_virtual_screen_marg_top = 20;
	static const int default_virtual_screen_marg_bottom = 20;
	static const int shps_min_width = 100;
	static const int shps_min_height = 100;
	static const int shps_max_width = 6000;
	static const int shps_max_height = 6000;
	static const int shps_max_area = 10000000; // 10 million or 3162 squared
	
	// Map
	static const int map_default_outline_width = 1;
	
	// Map Movie
	
	// Histogram
	
	// Table
	
	// Scatterplot
	
	// Boxplot
	
	// PCP (Parallel Coordinate Plot)
	
	// 3D Plot

	
	// General Global Constants
	static const int FileNameLen = 512; // max length of file names
	static const int RealWidth = 19;    // default width of output for reals
	static const int ShpHeaderSize = 50; // size of the header record in shapefile
	static const int ShpObjIdLen = 20;    // length of the ID of shape object
};

#endif
