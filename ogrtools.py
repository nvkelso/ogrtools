# By Nathaniel Vaughn KELSO
#
# OGR based Python tools for querrying a data source (SHP, etc).

import os, sys
import subprocess
from optparse import OptionParser

try:
  from osgeo import gdal, ogr  
except ImportError:
  import gdal
  import ogr
  
from ogrtools import describe as Describe
from ogrtools import fieldNamesToLowercase as Lowercase
from ogrtools import fieldNamesToUppercase as Uppercase
from ogrtools import fieldNamesRename as Rename


optparser = OptionParser(usage="""%prog [options]

OGR TOOLS

OGR based Python tools for querrying and transforming data sources.""")

optparser.add_option('-s', '--in_file','--data_file', dest='infile',
                      help='Give me your huddled masses of geodata!')

optparser.add_option('-o', '--out_file', dest='outfile',
                      help='Where should they huddle?')

optparser.add_option('-f', '--function', dest='function', 
                      help='ogrinfo (describe), lowercase, uppercase...')

optparser.add_option('-a', '--arguments', dest='arguments', 
                      help='Tell me more...')


if __name__ == "__main__":

    (options, args) = optparser.parse_args()
    
    #print 'len(args): ', len(args)
    function = 'ogrinfo'
        
    if len(args) > 0:
        filename = str(args[:1][0])
        outfile = args[1:] # this list might be empty, if no other output files were provided

        if not outfile:
            other_files = options.outfile
    else:
        filename = options.infile
        outfile = options.outfile
        function = options.function
        arguments = options.arguments
   
    #filename, columnname = args[:2] # this will fail if there are any fewer than two args
    #other_files = args[2:] # this list might be empty, if no other output files were provided

    if not filename:
        print 'Requires input file'
        sys.exit(1)
            
    # Input geodata
    in_dir = os.path.dirname( os.path.abspath( filename ) )
    in_file, in_file_extension = os.path.splitext( os.path.abspath( filename ) )
    in_file_name_part, in_file_ext_part = os.path.basename( os.path.abspath( filename ) ).split('.')
    in_file_fullpath = os.path.abspath( filename )
    
    if in_file_ext_part == 'shp':
        format = 'Esri Shapefile'
            
    # Output MSS, MML, and HTML files
    #out_dir = os.path.dirname( os.path.abspath( other_files[0] ) )
            
    # What OGR functions are we using?
    if function == 'ogrinfo' or function == 'describe':
        Describe( in_file_fullpath )        
        sys.exit(1)
    elif function == 'fieldnames_lowercase' or function == 'lowercase':
        args = Lowercase( in_file_fullpath )
        args = 'SELECT %s FROM \'%s\'' % (args, in_file_name_part) 
        print "ogr2ogr", "-f", format, '-overwrite', "-sql", args, outfile, filename
        subprocess.check_call(['ogr2ogr', '-f', format, '-overwrite', '-sql', args, outfile, filename])
        sys.exit(1)        
    elif function == 'fieldnames_uppercase' or function == 'uppercase':
        args = Uppercase( in_file_fullpath )
        args = 'SELECT %s FROM \'%s\'' % (args, in_file_name_part) 
        print "ogr2ogr", "-f", format, '-overwrite', "-sql", args, outfile, filename
        subprocess.check_call(['ogr2ogr', '-f', format, '-overwrite', '-sql', args, outfile, filename])
        sys.exit(1)
    elif function == 'rename':
        if not arguments:
            print 'Requires field alias list in format of: Fieldname1 as NewFieldName1, Fieldname2 as NewFieldName2'
            sys.exit(1)

        args = Rename( in_file_fullpath, arguments )
        args = 'SELECT %s FROM \'%s\'' % (args, in_file_name_part) 
        subprocess.check_call(['ogr2ogr', '-f', format, '-overwrite', '-sql', args, outfile, filename])
        sys.exit(1)
    else:
        print 'Bad legend or classification type, exiting.'
        sys.exit(1)