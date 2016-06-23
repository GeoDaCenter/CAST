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

/**
 *  Note: This file is the place to hold all constants such as default colors,
 *  as well as common text strings used in various dialogs.  Everything
 *  should be kept in the GeoDaConst namespace
 *
 */

#ifndef __GEODA_CENTER_GEODACONST_H__
#define __GEODA_CENTER_GEODACONST_H__

#include <vector>
/*
#include <wx/gdicmn.h>
#include <wx/string.h>
#include <wx/colour.h>
#include <wx/font.h>
#include <wx/pen.h>
*/

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
	static const int default_display_decimals = 4;
	static const int default_dbf_double_decimals = 7;
	static const int max_dbf_string_len = 254;
	static const int min_dbf_string_len = 1;
	static const int default_dbf_string_len = 40;
	static const int max_dbf_date_len = 8;
	static const int min_dbf_date_len = 8;
	static const int default_dbf_date_len = 8;
	
	/*
	// Shared menu ids
	static const int ID_TIME_SYNC_VAR1 = wxID_HIGHEST + 1000;
	static const int ID_TIME_SYNC_VAR2 = wxID_HIGHEST + 1001;
	static const int ID_TIME_SYNC_VAR3 = wxID_HIGHEST + 1002;
	static const int ID_TIME_SYNC_VAR4 = wxID_HIGHEST + 1004;
	
	static const int ID_FIX_SCALE_OVER_TIME_VAR1 = wxID_HIGHEST + 2000;
	static const int ID_FIX_SCALE_OVER_TIME_VAR2 = wxID_HIGHEST + 2001;
	static const int ID_FIX_SCALE_OVER_TIME_VAR3 = wxID_HIGHEST + 2002;
	static const int ID_FIX_SCALE_OVER_TIME_VAR4 = wxID_HIGHEST + 2004;
	
	static const int ID_PLOTS_PER_VIEW_1 = wxID_HIGHEST + 3000;
	static const int ID_PLOTS_PER_VIEW_2 = wxID_HIGHEST + 3001;
	static const int ID_PLOTS_PER_VIEW_3 = wxID_HIGHEST + 3002;
	static const int ID_PLOTS_PER_VIEW_4 = wxID_HIGHEST + 3003;
	static const int ID_PLOTS_PER_VIEW_5 = wxID_HIGHEST + 3004;
	static const int ID_PLOTS_PER_VIEW_6 = wxID_HIGHEST + 3005;
	static const int ID_PLOTS_PER_VIEW_7 = wxID_HIGHEST + 3006;
	static const int ID_PLOTS_PER_VIEW_8 = wxID_HIGHEST + 3007;
	static const int ID_PLOTS_PER_VIEW_9 = wxID_HIGHEST + 3008;
	static const int ID_PLOTS_PER_VIEW_10 = wxID_HIGHEST + 3009;
	static const int max_plots_per_view_menu_items = 10;
	static const int ID_PLOTS_PER_VIEW_OTHER = wxID_HIGHEST + 3100;
	static const int ID_PLOTS_PER_VIEW_ALL = wxID_HIGHEST + 3200;

	// Standard wxFont pointers.
	static wxFont* extra_small_font;
	static wxFont* small_font;
	static wxFont* medium_font;
	static wxFont* large_font;
	
	// MyShape constants
	static const wxPen* default_myshape_pen;
	static const wxBrush* default_myshape_brush;
	
	// MyPoint radius to give a larger target for clicking on
	static const int my_point_click_radius = 2;
	
	// Shared Colours
	static std::vector<wxColour> qualitative_colors;
	
	// The following are defined in shp2cnt and should be moved from there.
	//background color -- this is light gray
	static const wxColour backColor;
	// background color -- this is light gray
	static const wxColour darkColor;
	// color of text, frames, points -- this is dark cherry
	static const wxColour textColor;
	// outliers color (also used for regression, etc.) -- blue
	static const wxColour outliers_colour;
	// envelope color (also used for regression, etc.) -- red
	static const wxColour envelope_colour;
	
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
	
	static const wxColour selectable_outline_color; // black
	static const wxColour selectable_fill_color; // forest green
	static const wxColour highlight_color; // yellow
	static const wxColour canvas_background_color; // white
	static const wxColour legend_background_color; // white
	
	// Map
	static const wxSize map_default_size;
	static const int map_default_legend_width;
	// this is a light forest green
	static const wxColour map_default_fill_colour;
	static const wxColour map_default_outline_colour;
	static const int map_default_outline_width = 1;
	static const wxColour map_default_highlight_colour;
	
	// Map Movie
	static const wxColour map_movie_default_fill_colour;
	static const wxColour map_movie_default_highlight_colour;
	
	// Histogram
	static const wxSize hist_default_size;
	
	// Table
	static const wxString new_table_frame_title;
	static const wxString table_frame_title;
	static const wxSize table_default_size;
	static const wxColour table_no_edit_color;
	
	// Scatterplot
	static const wxSize scatterplot_default_size;
	static const wxColour scatterplot_scale_color; // black
	static const wxColour scatterplot_regression_color; // purple
	static const wxColour scatterplot_regression_selected_color; // red
	static const wxColour scatterplot_regression_excluded_color; // blue
	static const wxColour scatterplot_origin_axes_color; // grey
	static wxPen* scatterplot_reg_pen;
	static wxPen* scatterplot_reg_selected_pen;
	static wxPen* scatterplot_reg_excluded_pen;
	static wxPen* scatterplot_scale_pen;
	static wxPen* scatterplot_origin_axes_pen;

	// Bubble Chart
	static const wxSize bubble_chart_default_size;
	static const int bubble_chart_default_legend_width;
	
	// 3D Plot
	static const wxColour three_d_plot_default_highlight_colour;
	static const wxColour three_d_plot_default_point_colour;
	static const wxColour three_d_plot_default_background_colour;
	
	// Boxplot
	static const wxSize boxplot_default_size;
	static const wxColour boxplot_point_color;
	static const wxColour boxplot_median_color;
	static const wxColour boxplot_mean_point_color;
	static const wxColour boxplot_q1q2q3_color;
	
	// PCP (Parallel Coordinate Plot)
	static const wxSize pcp_default_size;
	static const wxColour pcp_line_color;
	static const wxColour pcp_horiz_line_color;
	
	// 3D Plot
	static const wxSize three_d_default_size;
	
	// Conditional View
	static const wxSize cond_view_default_size;
	*/
	
	// General Global Constants
	static const int FileNameLen = 512; // max length of file names
	static const int RealWidth = 19;    // default width of output for reals
	static const int ShpHeaderSize = 50; // size of the header record in Shapefile
	static const int ShpObjIdLen = 20;    // length of the ID of shape object
};

#endif
