
import os
import sys
from distutils.core import setup, Extension
from distutils.util import convert_path
 
# try to determine the directory where the shapelib source files are.
# There are currently two supported situations.
#
# 1. "Standalone" build: the parent directory is the shapelib source
#    directory
# 2. Built in the Thuban source tree where ../shapelib/ relative to the
#    directory containing this setup.py contains (the relevant parts of)
#    shapelib
#
# 3. Binary build with e.g. bdist_rpm.  This takes place deep in the
#    build directory.

# os.path expects filenames in OS-specific form so we have to construct
# the files with os.path functions. distutils, OTOH, uses posix-style
# filenames exclusively, so we use posix conventions when making
# filenames for distutils.
for shp_dir in ["..", "./shapelib", "../../../../../../shapelib"]:
    if (os.path.isdir(convert_path(shp_dir))
        and os.path.exists(os.path.join(convert_path(shp_dir), "shpopen.c"))):
        # shp_dir contains shpopen.c, so assume it's the directory with
        # the shapefile library to use
        break
else:
    print >>sys.stderr, "no shapelib directory found"
    sys.exit(1)

def dbf_macros():
    """Return the macros to define when compiling the dbflib wrapper.

    The returned list specifies one macro, HAVE_UPDATE_HEADER, which is
    '1' if the dbflib version we will be compiling with has the
    DBFUpdateHeader function and '0' otherwise.  To check whether
    DBFUpdateHeader is available, we scan shapefil.h for the string
    'DBFUpdateHeader'.
    """
    f = open(convert_path(shp_dir + "/shapefil.h"))
    contents = f.read()
    f.close()
    if contents.find("DBFUpdateHeader") >= 0:
        return [("HAVE_UPDATE_HEADER", "1")]
    else:
        return [("HAVE_UPDATE_HEADER", "0")]

extensions = [Extension("shapelibc",
                        ["shapelib_wrap.c",
                         shp_dir + "/shpopen.c",
                         shp_dir + "/shptree.c"],
                        include_dirs = [shp_dir]),
              Extension("shptree",
                        ["shptreemodule.c",
                         shp_dir + "/shpopen.c",
			 shp_dir+ "/shptree.c"],
                        include_dirs = [shp_dir]),
              Extension("coordinator",
                        ["coordinator_converter.c",
			 shp_dir + "/shpopen.c"],
                        include_dirs = [shp_dir]),
              Extension("dbflibc",
                        ["dbflib_wrap.c",
                         shp_dir + "/dbfopen.c"],
                        include_dirs = [shp_dir],
                        define_macros = dbf_macros())]

setup(name = "pyshapelib",
      version = "0.3",
      description = "Python bindings for shapelib",
      author = "Bernhard Herzog",
      author_email = "bh@intevation.de",
      url = "ftp:intevation.de/users/bh",
      py_modules = ["shapelib", "dbflib"],
      ext_modules = extensions)

