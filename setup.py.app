"""
setup.py for wxpysal package.
"""

from setuptools import setup
import glob,sys


APP = ['stars.py']
DATA_FILES = ['stars','stars/examples']
OPTIONS = {
    'packages':['wx','numpy','scipy','PIL','pysal'],
    'iconfile':'logo.icns'
}

setup(
    name='CAST PySAL',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app':OPTIONS},
    setup_requires=['py2app'],
)

setup(
    name = 'wxpysal',
    description = 'CAST',
    #long_description = open('INSTALL.txt'),
    maintainer = "Xun Li",
	maintainer_email = "xunli@asu.edu",
    url = 'http://geoda.asu.edu/',
    download_url = 'http://geodacenter.asu.edu/',
    version = '0.98',
    license = 'BSD License',
    packages = [
				'stars', 
				'stars.og', 
				'stars.rc', 
                'stars.core',
                'stars.model',
				'stars.stats',
                'stars.visualization',
                'stars.visualization.maps',
                'stars.visualization.dialogs',
                'stars.visualization.plots',
                'stars.visualization.utils',
                ],
    #package_data = {'stars':['examples/*.*']},
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
