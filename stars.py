#!/usr/bin/env python -W ignore::DeprecationWarning

import stars
import warnings

def dependencies_for_myprogram():
    from scipy.sparse.csgraph import _validation
    
warnings.filterwarnings("ignore")
stars.main()
