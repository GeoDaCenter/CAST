stars_menus='''
<?xml version="1.0" encoding="ISO-8859-15"?>
<resource>
  <object class="wxMenuBar" name="ID_SHARED_MAIN_MENU">
    <object class="wxMenu" name="ID_MENU">
      <label>&amp;File</label>
      <object class="wxMenuItem" name="ID_OPEN_SHAPE_FILE">
        <label>&amp;Open Shape File...</label>
        <accel>Ctrl+O</accel>
      </object>
      <object class="wxMenuItem" name="ID_MAPANALYSIS_MAPMOVIE">
        <label>Open Map Movie</label>
      </object>
      <object class="wxMenuItem" name="ID_CLOSE_ALL">
        <label>Close &amp;All</label>
      </object>
      <object class="separator"/>
      <object class="wxMenuItem" name="wxID_EXIT">
        <label>Exit</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>&amp;Tools</label>
        <object class="wxMenuItem" name="ID_SHAPE_POLYGONS_FROM_GRID">
          <label>Polygons from Grid</label>
        </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Table</label>
      <object class="wxMenuItem" name="IDM_TABLE">
        <label>View Table</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Weights</label>
      <object class="wxMenuItem" name="ID_TOOLS_WEIGHTS_CREATE">
        <label>Create</label>
        <enabled>1</enabled>
      </object>
      <object class="wxMenuItem" name="ID_TOOLS_WEIGHTS_CHAR">
        <label>Histogram</label>
        <enabled>1</enabled>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>&amp;Map</label>
      <!--
      <object class="wxMenu" name="ID_MENU">
        <label>Classify Maps</label>
      -->
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_QUANTILE">
          <label>Quantile</label>
          <bitmap stock_id="ToolBarBitmaps_25"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_PERCENTILE">
          <label>Percentile</label>
          <bitmap stock_id="ToolBarBitmaps_26"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_BOXPLOT">
          <label>Box Map</label>
          <bitmap stock_id="ToolBarBitmaps_28"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_STDDEV">
          <label>Standard Deviation Map</label>
          <bitmap stock_id="ToolBarBitmaps_27"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_UNIQUE_VALUES">
          <label>Unique Values Map</label>
          <bitmap stock_id="ToolBarBitmaps_38"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_NATURAL_BREAKS">
          <label>Natural Breaks Map</label>
          <bitmap stock_id="ToolBarBitmaps_39"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_MAXIMUM_BREAKS">
          <label>Maximum Breaks Map</label>
          <bitmap stock_id="ToolBarBitmaps_39"/>
        </object>
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_EQUAL_INTERVALS">
          <label>Equal Intervals Map</label>
          <bitmap stock_id="ToolBarBitmaps_40"/>
        </object>
        <!--
        <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_JENKS_CASPALL">
          <label>Jenks Caspall Map</label>
        </object>
        -->
        <object class="wxMenu" name="ID_MAP_SMOOTHING_CHOICES">
          <object class="wxMenuItem" name="ID_OPEN_RATES_SMOOTH_RAWRATE">
            <label>Raw Rate</label>
          </object>
          <object class="wxMenuItem" name="ID_OPEN_RATES_SMOOTH_EXCESSRISK">
            <label>Excess Risk</label>
          </object>
          <object class="wxMenuItem" name="ID_OPEN_RATES_EMPERICAL_BAYES_SMOOTHER">
            <label>Empirical Bayes</label>
          </object>
          <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_RATE_SMOOTHER">
            <label>Spatial Rate</label>
          </object>
          <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_EMPERICAL_BAYES">
            <label>Spatial Empirical Bayes</label>
          </object>
          <label>Rates-Calculated Maps</label>
          <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_MEDIAN_RATE">
            <label>Spatial Median Rate</label>
          </object>
          <object class="wxMenuItem" name="ID_OPEN_RATES_DISK_SMOOTHER">
            <label>Disk Smoother</label>
          </object>
      <!--
        </object>
      -->
      </object>

    </object>
    
    <object class="wxMenu" name="ID_MENU">
      <label>Calendar Map</label>
      <object class="wxMenuItem" name="IDM_CALENDAR_MAP">
        <label>Calendar Map</label>
        <enabled>1</enabled>
      </object>
      <object class="wxMenuItem" name="IDM_DYNAMIC_CALENDAR_MAP">
        <label>Dynamic Calendar Map</label>
      </object>
    </object>

    
    <object class="wxMenu" name="ID_MENU">
      <label>C&amp;luster Map</label>
      <object class="wxMenuItem" name="IDM_UNI_LISA">
        <label>Univariate LISA</label>
      </object>
      <object class="wxMenuItem" name="IDM_DYNAMIC_LISAMAP">
        <label>Dynamic LISA</label>
      </object>
      <object class="separator"/>
      <object class="wxMenuItem" name="IDM_LOCAL_G">
        <label>Local G Statistics</label>
      </object>
      <object class="wxMenuItem" name="IDM_DYNAMIC_LOCAL_G">
        <label>Dynamic Local G Statistics</label>
      </object>
      <object class="separator"/>
      <object class="wxMenuItem" name="IDM_DENSITY_MAP">
        <label>Density Map</label>
      </object>
      <object class="wxMenuItem" name="IDM_TIME_DENSITY_MAP">
        <label>Time Density Map</label>
      </object>
      <object class="wxMenuItem" name="IDM_DYNAMIC_DENSITY_MAP">
        <label>Dynamic Density Map</label>
      </object>
    </object>
    
    <object class="wxMenu" name="ID_MENU">
      <label>T&amp;ime</label>
      <object class="wxMenuItem" name="IDM_TREND_GRAPH">
        <label>Trend Graph</label>
      </object>
      <object class="wxMenuItem" name="IDM_DYNAMIC_TREND_GRAPH">
        <label>Dynamic Trend Graph</label>
      </object>
      <object class="wxMenu" name="ID_MENU">
        <label>Significant Trend Graphs</label>
          <object class="wxMenuItem" name="IDM_GI_SPACETIME_MAP">
            <label>Local G Trend Graph</label>
          </object>
          <object class="wxMenuItem" name="IDM_LISA_SPACETIME_MAP">
            <label>LISA Trend Graph</label>
          </object>
      </object>
    </object>
    
    <object class="wxMenu" name="ID_MENU">
      <label>E&amp;xplore</label>
      <object class="wxMenuItem" name="IDM_HIST">
        <label>Histogram</label>
      </object>
      <object class="wxMenuItem" name="IDM_SCATTERPLOT">
        <label>Scatter Plot</label>
      </object>
      <object class="wxMenuItem" name="IDM_BOX">
        <label>Box Plot</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>&amp;Help</label>
      <object class="wxMenuItem" name="wxID_ABOUT">
        <label>About CAST</label>
      </object>
    </object>
  </object>
  <object class="wxMenu" name="ID_BOXPLOT_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenu" name="ID_MENU">
      <label>Hinge</label>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_15">
        <label>1.5</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_30">
        <label>3.0</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_BOXPLOT_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Hinge</label>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_15">
        <label>1.5</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_30">
        <label>3.0</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_CARTOGRAM_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenu" name="ID_MENU">
      <label>Improve catrogram with...</label>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_100">
        <label>100 iterations</label>
      </object>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_500">
        <label>500 iterations</label>
      </object>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_1000">
        <label>1000 iterations</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Hinge</label>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_15">
        <label>1.5</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_30">
        <label>3.0</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_CARTOGRAM_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Improve catrogram with...</label>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_100">
        <label>100 iterations</label>
      </object>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_500">
        <label>500 iterations</label>
      </object>
      <object class="wxMenuItem" name="ID_CONTEXT_MOREITERATIONS_1000">
        <label>1000 iterations</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Hinge</label>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_15">
        <label>1.5</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_HINGE_30">
        <label>3.0</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_CARTOGRAM_VIEW_MENU_LEGEND">
    <object class="wxMenuItem" name="ID_LEGEND_BACKGROUND_COLOR">
      <label>Legend Background Color</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_LEGEND_TO_CLIPBOARD">
      <label>Copy Legend To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_HISTOGRAM_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenuItem" name="IDM_HIST_INTERVALS">
      <label>Intervals</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_HISTOGRAM_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="IDM_HIST_INTERVALS">
      <label>Intervals</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_GETIS_ORD_VIEW_MENU_OPTIONS">
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Significance Filter</label>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_05">
        <label>0.05</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_01">
        <label>0.01</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_001">
        <label>0.001</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_0001">
        <label>0.0001</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_ADD_NEIGHBORS_TO_SELECTION">
      <label>Add Neighbors To Selection</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Select All...</label>
      <object class="wxMenuItem" name="ID_SELECT_CORES">
        <label>Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_NEIGHBORS_OF_CORES">
        <label>Neighbors of Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_CORES_AND_NEIGHBORS">
        <label>Cores and Neighbors</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_MAP_ADDMEANCENTERS">
      <label>Add Mean Centers to Table</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_ADDCENTROIDS">
      <label>Add Centroids to Table</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_GETIS_ORD">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_GETIS_ORD_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Significance Filter</label>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_05">
        <label>0.05</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_01">
        <label>0.01</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_001">
        <label>0.001</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_0001">
        <label>0.0001</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_ADD_NEIGHBORS_TO_SELECTION">
      <label>Add Neighbors To Selection</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Select All...</label>
      <object class="wxMenuItem" name="ID_SELECT_CORES">
        <label>Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_NEIGHBORS_OF_CORES">
        <label>Neighbors of Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_CORES_AND_NEIGHBORS">
        <label>Cores and Neighbors</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_GETIS_ORD">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_LISAMAP_VIEW_MENU_OPTIONS">
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Significance Filter</label>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_05">
        <label>0.05</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_01">
        <label>0.01</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_001">
        <label>0.001</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_0001">
        <label>0.0001</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_ADD_NEIGHBORS_TO_SELECTION">
      <label>Add Neighbors To Selection</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Select All...</label>
      <object class="wxMenuItem" name="ID_SELECT_CORES">
        <label>Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_NEIGHBORS_OF_CORES">
        <label>Neighbors of Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_CORES_AND_NEIGHBORS">
        <label>Cores and Neighbors</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_MAP_ADDMEANCENTERS">
      <label>Add Mean Centers to Table</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_ADDCENTROIDS">
      <label>Add Centroids to Table</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_LISA">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_LISAMAP_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Significance Filter</label>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_05">
        <label>0.05</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_01">
        <label>0.01</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_001">
        <label>0.001</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SIGNIFICANCE_FILTER_0001">
        <label>0.0001</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_ADD_NEIGHBORS_TO_SELECTION">
      <label>Add Neighbors To Selection</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Select All...</label>
      <object class="wxMenuItem" name="ID_SELECT_CORES">
        <label>Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_NEIGHBORS_OF_CORES">
        <label>Neighbors of Cores</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_CORES_AND_NEIGHBORS">
        <label>Cores and Neighbors</label>
      </object>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_LISA">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_MAP_ADDMEANCENTERS">
      <label>Add Mean Centers to Table</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_ADDCENTROIDS">
      <label>Add Centroids to Table</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Map</label>
      <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_QUANTILE">
        <label>Quantile</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_PERCENTILE">
        <label>Percentile</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenu" name="ID_MENU">
        <label>Box Map</label>
        <object class="wxMenuItem" name="ID_MAP_HINGE_15">
          <label>Hinge = 1.5</label>
          <checkable>1</checkable>
        </object>
        <object class="wxMenuItem" name="ID_MAP_HINGE_30">
          <label>Hinge = 3.0</label>
          <checkable>1</checkable>
        </object>
      </object>
      <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_STDDEV">
        <label>Std Dev</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenu" name="ID_MENU">
      <label>Smooth</label>
      <object class="wxMenuItem" name="IDM_SMOOTH_RAWRATE">
        <label>Raw Rate</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="IDM_SMOOTH_EXCESSRISK">
        <label>Excess Risk</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="IDM_EMPERICAL_BAYES_SMOOTHER">
        <label>Empirical Bayes</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="IDM_SPATIAL_RATE_SMOOTHER">
        <label>Spatial Rate</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="IDM_SPATIAL_EMPIRICAL_BAYES">
        <label>Spatial Empirical Bayes</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_MAPANALYSIS_SAVERESULTS">
      <label>Save Rates</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_MAP_ADDMEANCENTERS">
      <label>Add Mean Centers to Table</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_ADDCENTROIDS">
      <label>Add Centroids to Table</label>
    </object>
    <object class="separator"/>
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Zoom</label>
      <object class="wxMenuItem" name="ID_ZOOM_IN">
        <label>Zoom In</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_ZOOM_OUT">
        <label>Zoom out</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
        <label>Fit To Window</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_VIEW_MENU_LEGEND">
    <object class="wxMenuItem" name="ID_LEGEND_BACKGROUND_COLOR">
      <label>Legend Background Color</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_LEGEND_TO_CLIPBOARD">
      <label>Copy Legend To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_MOVIE_VIEW_MENU_OPTIONS">
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Map</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background</label>
      </object>
    </object>
    <label>Options</label>
  </object>
  <object class="wxMenu" name="ID_PCP_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenuItem" name="ID_VIEW_STANDARDIZED_DATA">
      <label>View Standardized Data</label>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_ORIGINAL_DATA">
      <label>View Original Data</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_PCP_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_VIEW_STANDARDIZED_DATA">
      <label>View Standardized Data</label>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_ORIGINAL_DATA">
      <label>View Original Data</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_SCATTER_NEW_PLOT_VIEW_MENU_OPTIONS">
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_STANDARDIZED_DATA">
      <label>View Standardized Data</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_ORIGINAL_DATA">
      <label>View Original Data</label>
      <checkable>1</checkable>
      <checked>1</checked>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED">
      <label>Show Regression of Selected</label>
      <checkable>1</checkable>
      <checked>0</checked>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED_EXCLUDED">
      <label>Show Regression of Selected Excluded</label>
      <checkable>1</checkable>
      <checked>0</checked>
    </object>
    <object class="wxMenuItem" name="ID_DISPLAY_STATISTICS">
      <label>Display Statistics</label>
      <checkable>1</checkable>
      <checked>0</checked>
    </object>
    <object class="wxMenuItem" name="ID_SHOW_AXES_THROUGH_ORIGIN">
      <label>Show Axes Through Origin</label>
      <checkable>1</checkable>
      <checked>1</checked>
    </object>
    <object class="separator"/>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_COLOR">
        <label>Outline Color</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Selectable Fill Color</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background Color</label>
      </object>
    </object>
    <label>Options</label>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_SCATTER_PLOT_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenuItem" name="ID_VIEW_STANDARDIZED_DATA">
      <label>View Standardized Data</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_ORIGINAL_DATA">
      <label>View Original Data</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED_EXCLUDED">
      <label>Excluded Selected</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_SCATTER_PLOT_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_VIEW_STANDARDIZED_DATA">
      <label>View Standardized Data</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_ORIGINAL_DATA">
      <label>View Original Data</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED_EXCLUDED">
      <label>Excluded Selected</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_SCATTER_M_PLOT_VIEW_MENU_OPTIONS">
    <label>Options</label>
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED_EXCLUDED">
      <label>Exclude Selected</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_OPTION_ENVELOPESLOPES">
      <label>Envelope Slopes</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background Color</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_MORANI">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_SCATTER_M_PLOT_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_VIEW_REGRESSION_SELECTED_EXCLUDED">
      <label>Exclude Selected</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Randomization</label>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_99PERMUTATION">
        <label>99 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_199PERMUTATION">
        <label>199 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_499PERMUTATION">
        <label>499 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_999PERMUTATION">
        <label>999 Permutations</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_OPTIONS_RANDOMIZATION_OTHER">
        <label>Other (up to 49999)</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_OPTION_ENVELOPESLOPES">
      <label>Envelope Slopes</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
      <label>Background</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_MORANI">
      <label>Save Results</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_TABLE_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_TABLE_MOVE_SELECTED_TO_TOP">
      <label>Move Selected to Top</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_CLEAR_SELECTION">
      <label>Clear Selection</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_RANGE_SELECTION">
      <label>Range Selection</label>
    </object>
    <object class="wxMenuItem" name="ID_ADD_NEIGHBORS_TO_SELECTION">
      <label>Add Neighbors To Selection</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_TABLE_FIELD_CALCULATION">
      <label>Field Calculation</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_ADD_COLUMN">
      <label>Add Column</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_DELETE_COLUMN">
      <label>Delete Column</label>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_TABLE_RELOAD_DATA">
      <label>Reload Data</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_MERGE_TABLE_DATA">
      <label>Merge Table Data</label>
    </object>
    <object class="wxMenuItem" name="ID_TABLE_SAVE_AS_NEW_SHP_FILE">
      <label>Save as New Shape File...</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_REPORT_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_FONT">
      <label>Change Font</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_TESTMAP_VIEW_MENU_CONTEXT">
    <object class="wxMenu" name="ID_MENU">
      <label>Selection Shape</label>
      <object class="wxMenuItem" name="ID_SELECT_WITH_RECT">
        <label>Rectangle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_CIRCLE">
        <label>Circle</label>
        <checkable>1</checkable>
      </object>
      <object class="wxMenuItem" name="ID_SELECT_WITH_LINE">
        <label>Line</label>
        <checkable>1</checkable>
      </object>
    </object>
    <object class="wxMenuItem" name="ID_SELECTION_MODE">
      <label>Selection Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_PAN_MODE">
      <label>Panning Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_ZOOM_MODE">
      <label>Zooming Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_FIT_TO_WINDOW_MODE">
      <label>Fit-To-Window Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_FIXED_ASPECT_RATIO_MODE">
      <label>Fixed Aspect Ratio Mode</label>
      <checkable>1</checkable>
    </object>
    <object class="wxMenuItem" name="ID_PRINT_CANVAS_STATE">
      <label>Print Canvas State to Log File</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_COLOR">
        <label>Outline Color</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Selectable Fill Color</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background Color</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_TEST_TABLE_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_PRINT_CANVAS_STATE">
      <label>Print Canvas State to Log File</label>
    </object>
    <object class="wxMenu" name="ID_MENU">
      <label>Color</label>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_COLOR">
        <label>Outline Color</label>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_OUTLINE_VISIBLE">
        <label>Outlines Visible</label>
        <checkable>1</checkable>
        <checked>1</checked>
      </object>
      <object class="wxMenuItem" name="ID_SELECTABLE_FILL_COLOR">
        <label>Selectable Fill Color</label>
      </object>
      <object class="wxMenuItem" name="ID_HIGHLIGHT_COLOR">
        <label>Highlight Color</label>
      </object>
      <object class="wxMenuItem" name="ID_CANVAS_BACKGROUND_COLOR">
        <label>Background Color</label>
      </object>
    </object>
    <object class="separator"/>
    <object class="wxMenuItem" name="ID_SAVE_CANVAS_IMAGE_AS">
      <label>Save Image As</label>
    </object>
    <object class="wxMenuItem" name="ID_SAVE_SELECTED_TO_COLUMN">
      <label>Save Selected To Column</label>
    </object>
    <object class="wxMenuItem" name="ID_COPY_IMAGE_TO_CLIPBOARD">
      <label>Copy Image To Clipboard</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_TEST_SCROLL_WIN_VIEW_MENU_CONTEXT">
    <object class="wxMenuItem" name="ID_HELLO_WORLD">
      <label>Hello World</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_CHOICES">
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_QUANTILE">
      <label>Quantile</label>
      <bitmap stock_id="ToolBarBitmaps_25"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_PERCENTILE">
      <label>Percentile</label>
      <bitmap stock_id="ToolBarBitmaps_26"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_BOXPLOT">
      <label>Box Map</label>
      <bitmap stock_id="ToolBarBitmaps_28"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_CHOROPLETH_STDDEV">
      <label>Standard Deviation Map</label>
      <bitmap stock_id="ToolBarBitmaps_27"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_UNIQUE_VALUES">
      <label>Unique Values Map</label>
      <bitmap stock_id="ToolBarBitmaps_38"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_NATURAL_BREAKS">
      <label>Natural Breaks Map</label>
      <bitmap stock_id="ToolBarBitmaps_39"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_MAXIMUM_BREAKS">
      <label>Maximum Breaks Map</label>
      <bitmap stock_id="ToolBarBitmaps_39"/>
    </object>
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_EQUAL_INTERVALS">
      <label>Equal Intervals Map</label>
      <bitmap stock_id="ToolBarBitmaps_40"/>
    </object>
    <!--
    <object class="wxMenuItem" name="ID_OPEN_MAPANALYSIS_JENKS_CASPALL">
      <label>Jenks Caspall Map</label>
    </object>
    -->
    <object class="wxMenu" name="ID_MAP_SMOOTHING_CHOICES">
      <object class="wxMenuItem" name="ID_OPEN_RATES_SMOOTH_RAWRATE">
        <label>Raw Rate</label>
      </object>
      <object class="wxMenuItem" name="ID_OPEN_RATES_SMOOTH_EXCESSRISK">
        <label>Excess Risk</label>
      </object>
      <object class="wxMenuItem" name="ID_OPEN_RATES_EMPERICAL_BAYES_SMOOTHER">
        <label>Empirical Bayes</label>
      </object>
      <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_RATE_SMOOTHER">
        <label>Spatial Rate</label>
      </object>
      <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_EMPERICAL_BAYES">
        <label>Spatial Empirical Bayes</label>
      </object>
      <label>Rates-Calculated Maps</label>
      <object class="wxMenuItem" name="ID_OPEN_RATES_SPATIAL_MEDIAN_RATE">
        <label>Spatial Median Rate</label>
      </object>
      <object class="wxMenuItem" name="ID_OPEN_RATES_DISK_SMOOTHER">
        <label>Disk Smoother</label>
      </object>
    </object>
  </object>
  <object class="wxMenu" name="ID_MAP_CHOICES_NO_ICONS">
    <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_QUANTILE">
      <label>Quantile</label>
    </object>
    <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_PERCENTILE">
      <label>Percentile</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_HINGE_15">
      <label>Hinge = 1.5</label>
    </object>
    <object class="wxMenuItem" name="ID_MAP_HINGE_30">
      <label>Hinge = 3.0</label>
    </object>
    <object class="wxMenuItem" name="ID_MAPANALYSIS_CHOROPLETH_STDDEV">
      <label>Standard Deviation</label>
    </object>
    <object class="wxMenu" name="ID_MAP_SMOOTHING_CHOICES">
      <object class="wxMenuItem" name="IDM_SMOOTH_RAWRATE">
        <label>Raw Rate</label>
      </object>
      <object class="wxMenuItem" name="IDM_SMOOTH_EXCESSRISK">
        <label>Excess Risk</label>
      </object>
      <object class="wxMenuItem" name="IDM_EMPERICAL_BAYES_SMOOTHER">
        <label>Empirical Bayes</label>
      </object>
      <object class="wxMenuItem" name="IDM_SPATIAL_RATE_SMOOTHER">
        <label>Spatial Rate</label>
      </object>
      <object class="wxMenuItem" name="IDM_SPATIAL_EMPIRICAL_BAYES">
        <label>Spatial Empirical Bayes</label>
      </object>
      <label>Smoothing</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_DENSITY_MAPS">
    <label/>
    <object class="wxMenuItem" name="IDM_DENSITY_MAP">
      <label>Density Map</label>
    </object>
    <object class="wxMenuItem" name="IDM_TIME_DENSITY_MAP">
      <label>Time Density Map</label>
    </object>
    <object class="wxMenuItem" name="IDM_DYNAMIC_DENSITY_MAP">
      <label>Dynamic Density Map</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_TREND_GRAPHS">
    <label/>
    <object class="wxMenuItem" name="IDM_TREND_GRAPH">
      <label>Trend Graph</label>
    </object>
    <object class="wxMenuItem" name="IDM_DYNAMIC_TREND_GRAPH">
      <label>Dynamic Trend Graph</label>
    </object>
    <object class="wxMenu" name="ID_SIGNIFICANT_TREND_GRAPH">
      <label>Significant Trend Graph</label>
        <object class="wxMenuItem" name="IDM_LISA_SPACETIME_MAP">
          <label>LISA Trend Graph</label>
        </object>
        <object class="wxMenuItem" name="IDM_GI_SPACETIME_MAP">
          <label>Local G Trend Graph</label>
        </object>
    </object>
  </object>
  <object class="wxMenu" name="ID_CALENDAR_MAPS">
    <label/>
    <object class="wxMenuItem" name="IDM_CALENDAR_MAP">
      <label>Calendar Map</label>
    </object>
    <object class="wxMenuItem" name="IDM_DYNAMIC_CALENDAR_MAP">
      <label>Dynamic Calendar Map</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MENU_LISA">
    <label/>
    <object class="wxMenuItem" name="IDM_UNI_LISA">
      <label>Univariate LISA</label>
    </object>
    <object class="wxMenuItem" name="IDM_DYNAMIC_LISAMAP">
      <label>Dynamic LISA</label>
    </object>
  </object>
  <object class="wxMenu" name="ID_MENU_LOCAL_G">
    <label/>
    <object class="wxMenuItem" name="IDM_LOCAL_G">
      <label>Local G Statistics</label>
    </object>
    <!--
    <object class="wxMenuItem" name="IDM_MARKOV_LISAMAP">
      <label>Markov LISA Map</label>
    </object>
    -->
    <object class="wxMenuItem" name="IDM_DYNAMIC_LOCAL_G">
      <label>Dynamic Local G Statistics</label>
    </object>
  </object>
</resource>
'''