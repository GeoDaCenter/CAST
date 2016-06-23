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

#ifndef __GEODA_CENTER_SHAPE_FILE_HDR_H__
#define __GEODA_CENTER_SHAPE_FILE_HDR_H__

#include "AbstractShape.h"
#include "Box.h"
#include "ShapeFile.h"
#include "ShapeFileTypes.h"
#include <string>
using namespace std;
/*
 ShapeFileHdr
 Header Data structure that corresponds to the first record of
 all *.SHP files.
  */
class ShapeFileHdr  {
private:
    int FileCode, Version, fShape, FileLength;
    Box FileBox;
    typedef struct {
        int    f[9];
        Box     b;
        int    s[8];
    } HdrRecord;
    typedef struct {
        int f[9];
        Box b;
        int s[8];
    } HdrRecord64;
public:
	enum  HdrEnum  {
		kVersion = 1000,
		kFileCode = 9994
	};
	ShapeFileHdr(const ShapeFileTypes::ShapeType FileShape=ShapeFileTypes::SPOINT);
	ShapeFileHdr(const char* s);
	int FileShape() const { return fShape; }
	int Length() const { return FileLength; }
	Box BoundingBox() const { return FileBox; }
	void MakeBuffer(char *s) const;
	void SetFileBox(const Box& fBox);
	void SetFileLength(int flength);
	friend ShapeFileHdr& operator<<(ShapeFileHdr& hd, const AbstractShape& s);
	friend oShapeFile& operator<<(oShapeFile& s, const ShapeFileHdr& hd);
	void Replace(const string& fname, const int& recs);
	int getFileCode() const { return FileCode; }
	int getVersion() const { return Version; }
};

#endif
