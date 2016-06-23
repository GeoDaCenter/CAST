#include <iostream>
#include <cmath>
#include <ctime>
#include <pthread.h>
#include <cstdlib>
#include <cstring>

#include "mt_densitymap.h"

using namespace std;

KDE::~KDE()
{
    r_buffer.clear();
    g_buffer.clear();
    b_buffer.clear();
    a_buffer.clear();

    for ( int i=0; i<rows;++i)
        delete grid[i];
    delete grid;
}

/*
 * KDE construction function
 *
 */
KDE::KDE(int _n, 
         vector<double> &_x_list, 
         vector<double> &_y_list, 
         vector<int> &_pts_ids, 
         vector<double> &_extent, 
         double _bandwidth, 
         double _cellsize, 
         int _kernel_func_type,
         int _gradient_type,
         double _opaque) 
{
    n = _n;
    x_list = _x_list;  
    y_list = _y_list;
    pts_ids = _pts_ids; 
    extent = _extent;
    bandwidth = _bandwidth;
    cellsize = _cellsize;
    gradient_type = _gradient_type;
    opaque = _opaque; 

    switch (_kernel_func_type)
    {
        case 0:
            kernel_func = quadratic;
            break;
        case 1:
            kernel_func = triangular;
            break;
        case 2:
            kernel_func = uniform;
            break;
        case 3:
            kernel_func = gaussian;
            break;
        default:
            kernel_func = quadratic;
            break;
    }
            
    // from extend to grid
    left  = extent[0];
    lower = extent[1];
    right = extent[2];
    upper = extent[3];

    extent_width = right - left;
    extent_height = upper - lower;

    cols = (int)(ceil(extent_width  / (double)cellsize));
    rows = (int)(ceil(extent_height / (double)cellsize));

    // grid variables
    grid_lower = lower + (cellsize / 2.0);
    grid_upper = grid_lower + ((rows - 1) * cellsize);
    grid_left  = left + (cellsize / 2.0);
    grid_right = grid_left + ((cols - 1) * cellsize);

    grid = new double*[rows];
    for ( int i=0; i<rows; ++i)
    {
        grid[i] = new double[cols];
        memset(grid[i], 0, sizeof(double)*cols);
    }
}

/*
 * Thread.Start() will call this function for each thread
 *
 */
void KDE::run()
{
    update_grid();
}

/*
 * KDE::update_grid function, threaded version
 *
 * go through each point in points data, and calculate the density value 
 * of cells it impacted
 */
void* KDE::update_grid()
{
    vector<int>::iterator it;
    for ( it=pts_ids.begin(); it!=pts_ids.end(); ++it)
    {
        int idx = (*it);
        double x = x_list[idx];
        double y = y_list[idx];
        int i,j,I,J;
        double radius, float_i, float_j;

        radius = bandwidth / cellsize; 
        float_i = (y - grid_lower) / cellsize;
        i = (int)(floor(float_i - radius));
        i = (i>=0) ? i : 0;
        I = (int)(floor(float_i + radius));
        I = (I<rows) ? I : rows -1;

        float_j = (x - grid_left) / cellsize;
        j = (int) (floor(float_j - radius));
        j = (j>=0) ? j : 0;
        J = (int)(floor(float_j + radius));
        J = (J<cols) ? J : cols -1;

        double _x,_y,_z,d;

        for (int row_idx=i; row_idx < I+1; ++row_idx) 
        {
            for (int col_idx=j; col_idx < J+1; ++col_idx) 
            {
                _x = grid_left + (col_idx * cellsize);
                _y = grid_lower + (row_idx * cellsize);
                d = (_x-x) * (_x-x) + (_y-y)*(_y-y);
                d = sqrt(d);
                if (d <= bandwidth) 
                {
                    _z = d / bandwidth;
                    grid[row_idx][col_idx] += kernel_func(_z);
                }
            }
        }
    }

}

/*
 * Draw grid on rgba_buffer
 *
 */
void KDE::create_rgba_buffer(double gradientMin, double gradientMax)
{
    int R=0,G=1,B=2;  
    
    // tansfer 0~1 value in grid to 0~255 pixel values
    double grid_range = gradientMax- gradientMin;

    for ( int i=rows-1; i>=0; --i)
    {
        for ( int j=0; j< cols; ++j)
        {
            double scaleVal = (grid[i][j] - gradientMin) / grid_range;
            int color_idx = 255 - scaleVal * 255;
            switch (gradient_type)
            {
                case 0:
                    r_buffer.push_back(GRADIENT_CLASSIC[R][color_idx]);
                    g_buffer.push_back(GRADIENT_CLASSIC[G][color_idx]);
                    b_buffer.push_back(GRADIENT_CLASSIC[B][color_idx]);
                    break;
                case 1:
                    r_buffer.push_back(GRADIENT_FIRE[R][color_idx]);
                    g_buffer.push_back(GRADIENT_FIRE[G][color_idx]);
                    b_buffer.push_back(GRADIENT_FIRE[B][color_idx]);
                    break;
                case 2:
                    r_buffer.push_back(GRADIENT_OMG[R][color_idx]);
                    g_buffer.push_back(GRADIENT_OMG[G][color_idx]);
                    b_buffer.push_back(GRADIENT_OMG[B][color_idx]);
                    break;
                case 3:
                    r_buffer.push_back(GRADIENT_PBJ[R][color_idx]);
                    g_buffer.push_back(GRADIENT_PBJ[G][color_idx]);
                    b_buffer.push_back(GRADIENT_PBJ[B][color_idx]);
                    break;
                case 4:
                    r_buffer.push_back(GRADIENT_PJAITCH[R][color_idx]);
                    g_buffer.push_back(GRADIENT_PJAITCH[G][color_idx]);
                    b_buffer.push_back(GRADIENT_PJAITCH[B][color_idx]);
                    break;
                case 5:
                    r_buffer.push_back(GRADIENT_RDYIBU[R][color_idx]);
                    g_buffer.push_back(GRADIENT_RDYIBU[G][color_idx]);
                    b_buffer.push_back(GRADIENT_RDYIBU[B][color_idx]);
                    break;
                default:
                    r_buffer.push_back(GRADIENT_CLASSIC[R][color_idx]);
                    g_buffer.push_back(GRADIENT_CLASSIC[G][color_idx]);
                    b_buffer.push_back(GRADIENT_CLASSIC[B][color_idx]);
                    break;
            }
            a_buffer.push_back(scaleVal > 0.05 ? opaque:0);
        }
    }
}

/*
 * Get min & max values from a matrix
 *
 */
void KDE::get_minmax_gradient()
{
    double maxVal = 0, minVal = 0xFFFFFFFF;
    for ( int i=0; i<rows; ++i) 
    {
        for ( int j=0; j<cols; ++j)
        {
            if (grid[i][j] > maxVal)
                maxVal = grid[i][j];
            if (grid[i][j] < minVal)
                minVal = grid[i][j];
        }
    }
    gradient_min = minVal;
    gradient_max = maxVal;
}

DKDE::~DKDE()
{
    
    r_buffer_array.clear();
    g_buffer_array.clear();
    b_buffer_array.clear();
    a_buffer_array.clear();
}

DKDE::DKDE(vector<double> _x_list, 
           vector<double> _y_list, 
           int _intervals, 
           vector<vector<int> > _itv_pts_ids,
           vector<double> _extent, 
           double _bandwidth, 
           double _cellsize, 
           int kernel_func_type,
           int gradient_type,
           double _opaque)
{
    KDE** kde_tasks = new KDE*[_intervals];
    
    for (int i=0; i<_intervals; ++i)
    {
        // for each point set, start a KDE thread 
        int n_point_set = _itv_pts_ids[i].size();
        kde_tasks[i] = new KDE(n_point_set, _x_list, _y_list, _itv_pts_ids[i], _extent, _bandwidth, _cellsize,kernel_func_type, gradient_type, _opaque); 
        kde_tasks[i]->start(); 
    }
    
    // join all KDE threads
    for ( int i=0; i<_intervals; ++i)
    {
        kde_tasks[i]->join();
    }
    
    // get min/max gradient value
    double minGradient=0xFFFFFFFF, maxGradient=0;
    for ( int i=0; i<_intervals; ++i)
    {
        kde_tasks[i]->get_minmax_gradient(); 
        if (minGradient > kde_tasks[i]->gradient_min)
            minGradient = kde_tasks[i]->gradient_min;
        if (maxGradient < kde_tasks[i]->gradient_max)
            maxGradient = kde_tasks[i]->gradient_max;
        rows = kde_tasks[i]->rows;
        cols = kde_tasks[i]->cols;
    }
    gradient_min = minGradient;
    gradient_max = maxGradient;
        
    // create images
    for ( int i=0; i<_intervals; ++i)
    {
        kde_tasks[i]->create_rgba_buffer(minGradient,maxGradient);  
        r_buffer_array.push_back(kde_tasks[i]->r_buffer);
        g_buffer_array.push_back(kde_tasks[i]->g_buffer);
        b_buffer_array.push_back(kde_tasks[i]->b_buffer);
        a_buffer_array.push_back(kde_tasks[i]->a_buffer);
    }
}

int main(int argc, char** argv) 
{
    // test help functions
    cout << "triangular:" << triangular(10) <<endl;
    cout << "uniform:" << uniform(10) <<endl;
    cout << "quadratic:" << quadratic(10)<<endl;
    cout << "guassian:" << gaussian(10)<<endl;

    // generate random points
    size_t n = 1000;
    vector<double> x_list;
    vector<double> y_list;
    
    srand(time(NULL));
   
    for ( size_t i=0; i<n; ++i)
    { 
        x_list.push_back(rand() % 100);
        y_list.push_back(rand() % 100);
    }
   
    int intervals = 2;
    
    vector<double> extent;
    extent.push_back(0);
    extent.push_back(0);
    extent.push_back(100);
    extent.push_back(100);
   
    vector<vector<int> > itv_pts_ids;
    vector<int> ids;
    for ( int i=0; i< 500; ++i)
    {
        ids.push_back(i);
    }
    itv_pts_ids.push_back(ids);
    vector<int> ids1;
    for ( int i=500; i< 1000; ++i)
    {
        ids1.push_back(i);
    }
    itv_pts_ids.push_back(ids1);
    
    
    DKDE* dkde = new DKDE(x_list, y_list, intervals, itv_pts_ids,extent, 5, 0.5,1,2, 60);
    delete dkde;    
    cout << "done"<<endl; 
}
