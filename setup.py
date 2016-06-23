"""
setup.py for wxpysal package.
"""

#import distribute_setup
#distribute_setup.use_setuptools()
from setuptools import setup

setup(
    name = 'wxpysal',
    description = 'WxPySAL: Wx windows application of Python Spatial Analysis Library',
    #long_description = open('INSTALL.txt'),
    maintainer = "WxPySAL Developers",
	maintainer_email = "pysal-dev@googlegroups.com",
    url = 'http://geoda.asu.edu/',
    download_url = 'http://code.google.com/p/pysal/downloads/list',
    version = '0.98',
    license = 'BSD License',
    packages = ['stars', 
                'stars.core',
                'stars.model',
                'stars.visualization',
                'stars.visualization.maps',
                'stars.visualization.dialogs',
                'stars.visualization.plots',
                'stars.visualization.utils'
                ],
    package_data = {'stars':['examples/*.*','rc/*.*']},
    requires = ['py2app','scipy','numpy','PIL','wx'],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
