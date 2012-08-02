#!/bin/bash

# loop through all of the shapefiles in the directory and act on them
# http://trac.osgeo.org/gdal/wiki/FAQVector#HowcanImergehundredsofShapefiles
# http://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash

if [ $# -ne 3 ]; then
    echo "USAGE: ./delete_fieldnames_on_dir_of_shps.sh <in_dir_path> <out_dir_path> <fieldname_options>"
    echo "NOTE: Requires fieldname_options list in format of: Fieldname1, Fieldname2"
    exit 1
fi

#Capture the shell arguments
in_dir_of_shps=$1
out_dir_of_shps=$2
fieldname_options=$3

#Ensure the output directory exists
mkdir -p ${out_dir_of_shps}

#Loop thru all the shps in the input dir
for i in $(ls ${in_dir_of_shps}/*.shp); do
  #echo ${i}
  
  #Capture each filename
  filename=$(basename "$i")
  #extension="${filename##*.}"
  #filename="${filename%.*}"
  
  o=${out_dir_of_shps}/${filename}
  #echo ${o}
  
  python ../ogrtools.py --in_file ${i} --out_file ${o} --function delete --arguments fieldname_options
done