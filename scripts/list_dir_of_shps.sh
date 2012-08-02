#!/bin/bash

# loop through all of the shapefiles in the directory and act on them
# http://trac.osgeo.org/gdal/wiki/FAQVector#HowcanImergehundredsofShapefiles
# http://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash

if [ $# -ne 1 ]; then
    echo "USAGE: ./list_dir_of_shps.sh <in_dir_path>"
    exit 1
fi

in_dir_of_shps=$1

for i in $(ls ${in_dir_of_shps}/*.shp); do
  echo ${i}
done