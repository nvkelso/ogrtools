"""
From GeoDjango (an old copy, with new mods)...

This module includes some utility functions for inspecting the layout
of a GDAL data source -- the functionality is analogous to the output
produced by the `ogrinfo` utility.
"""

import os, sys
from optparse import OptionParser

try:
    from osgeo import gdal, ogr  
except ImportError:
    import gdal
    import ogr
from gdal import Dataset as Dataset
from ogr import Geometry as GEO_CLASSES

optparser = OptionParser(usage="""%prog [options]

Utility functions for inspecting the layout of a GDAL/OGR data source -- the 
functionality is analogous to the output produced by the `ogrinfo` utility.

Walks the available layers in the supplied `data_source`, displaying
the fields for the first `num_features` features.""")

def ogrinfo(   data_source, 
                num_features=10000 ):
    
    describe(   data_source, num_features )


def getData( filename ):
    #print 'data_source: ', data_source, ' num_features: ', num_features
    
    in_dir = os.path.dirname( os.path.abspath( filename ) )    
    in_file_name_part = os.path.basename( os.path.abspath( filename ) )
    os.chdir( in_dir )
    
    # get the shapefile driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
        
    # Checking the parameters.
    if isinstance( filename, str ):
        data_source = driver.Open( in_file_name_part, 0 )
        #data_source = Dataset(data_source)
    elif isinstance(data_source, DataSource):
        pass
    else:
        raise Exception('Data source parameter must be a string or a DataSource object.')
        
    if data_source is None:
        print 'Could not open file'
        sys.exit(1)
        
    return data_source    

def describe(   data_source, 
                num_features=10000 ):
    
    in_file_fullpath = os.path.abspath( data_source )    

    data_source = getData( data_source )

    for i, layer in enumerate(data_source):
        print "data source : %s" % data_source.name
        print "   full path: %s" % in_file_fullpath
        print "==== layer %s" % i
        print "  shape type: %s" % ogr.GeometryTypeToName(layer.GetGeomType())
        print "  # features: %s" % len(layer)
        print "         srs: %s" % layer.GetSpatialRef()
        extent_tup = layer.GetExtent()
        print "      extent: %s - %s" % (extent_tup[0:2], extent_tup[2:4])
        
        #reportFeatures( layer, num_features )
        
        first_feature = layer.GetNextFeature()
        
        print "  # fields %s: NAME (first value)" % len(first_feature.keys())
        print "               ------------------"
        for key in first_feature.keys():
            try:
                #print 'first_feature.GetField(key): ', first_feature.GetField(key), ' - ', type( first_feature.GetField(key) )
                if type( first_feature.GetField(key) ) is str:
                    type = 'String'
                else:
                    type = 'Number'
            except:
                type = 'Other'
            
            print "               %s\t(%s)" % (key, first_feature.GetField(key) )
            
            
            #a = gather_ogr_stats( layer, key, num_features )

def getFieldNames( data_source ):
    field_names = []
    
    in_file_fullpath = os.path.abspath( data_source )    

    data_source = getData( data_source )

    for i, layer in enumerate(data_source):
        first_feature = layer.GetNextFeature()
        
        for key in first_feature.keys():
            field_names.append( key )
            
    return field_names


def fieldNamesToLowercase( data_source ):

    field_names = getFieldNames( data_source )
       
    lowercase = ''
    for key in enumerate(field_names):
        if len(lowercase) > 0:
            lowercase = lowercase + ", %s as %s" % (key[1], key[1].lower() )
        else:
            lowercase = lowercase + "%s as %s" % (key[1], key[1].lower() )
                   
    print lowercase
    return lowercase
        

def fieldNamesToUppercase( data_source ):

    field_names = getFieldNames( data_source )
    
    uppercase = ''
    for key in enumerate(field_names):
        if len(uppercase) > 0:
            uppercase = uppercase + ", %s as %s" % (key[1], key[1].upper() )
        else:
            uppercase = uppercase + "%s as %s" % (key[1], key[1].upper() )
            
    print uppercase        
    return uppercase
        
        #ogr2ogr -sql "Bla as bla, Thing as thing, Second as second" outfile infile


def parseFieldNameAliases( alias_str ):
    aliases = {}
    for alias in alias_str.split(","):
        # TODO: make this case-insensitive (use a regular expression)
        input, output = alias.split(" as ") # " AS "
        aliases[input] = output
    return aliases
    
def fieldNamesRename( data_source, aliases ):
    """
    >>> fieldNamesRename( "path/to/foo.shp", {'foo': "Foo"} )
    >>> fieldNamesRename( "path/to/foo.shp", "foo as Foo, bar as Bar" )
    > "foo as Foo, bar as Bar, qux"
    """

    field_names = getFieldNames( data_source )
    
    # Name1 as name, Name2 as name_alt

    if type(aliases) is str:
        aliases = parseFieldNameAliases(aliases)
        
    output = []
    for i, key in enumerate(field_names):
        #print "%d. %s" % (i, key)
        if key in aliases:
            output.append("%s as %s" % (key, aliases[key]))
        else:
            output.append(key)
    new_names = ", ".join(output)
    
    print new_names
    return new_names

                
# TODO: This isn't tested yet
def gather_ogr_stats( layer, indicator_field, num_features=10000 ):
    statistics = {'values':{}, 'min':{}, 'max':{}, 'type':'', 'count':0, 'count_not_null':0}

    # Loop through the features in the layer
    feature = layer.GetNextFeature()
    
    print type(feature)
    try:
        if type( feature.GetField( indicator_field) ) is str:
            statistics['type'] = 'String'
        else:
            statistics['type'] = 'Number'
    except:
        return False
        
    # Gather values
    while feature:        
        # get the attributes
        key = feature.GetField(indicator_field)
        
        # Add key to dictonary, and track with value counter for total values (histogram)
        if key in statistics['values']:
            statistics['values'][ key ] += 1
        else:
            statistics['values'][ key ] = 1
        
        # Increment the statistics counter
        statistics['count'] += 1
        if key:
            statistics['count_not_null'] += 1
               
        # Destroy the feature and get a new one
        feature.Destroy()
        feature = layer.GetNextFeature()
    
    # Calculate min/max for the data ranges
    
    field_values = []
    field_values_counts = []
    for k, v in statistics['values'].iteritems():
        field_values.append(k)
        field_values_counts.append(v)
    
    #print min(field_values)
    #print max(field_values)
    #print min(field_values_counts)
    #print max(field_values_counts)
    
    statistics['min'] = min(field_values)
    statistics['max'] = max(field_values)
        
    # TODO: sort the dict and take the last and first
    print 'statistics: ', statistics
    
    # Return the results
    return statistics
    
    
def reportFeatures( layer, num_features ):
    
    print "Displaying the first %s features ====" % num_features

    #width = max(*map(len,layer.fields))
    #fmt = " %%%ss: %%s" % width
    
    feature = layer.GetNextFeature()
    j = 0
    
    # Gather values
    #while feature:  
        #print "=== Feature %s" % j
        
        #for fieldCounter in range(feature.GetFieldCount()):
            #type_name = feature.GetField( fieldCounter ).GetFieldTypeName()
            #output = fmt % (feature.GetName(), feature.GetFieldTypeName())
            #val = feature.get(fld_name)
            #if val:
            #    if isinstance(val, str):
            #        val_fmt = ' ("%s")'
            #    else:
            #        val_fmt = ' (%s)'
            #    output += val_fmt % val
            #else:
            #    output += ' (None)'
            #print output
        #j = j + 1
        
    #gather_ogr_stats( layer, fld_name, 100000 )


if __name__ == "__main__":

    (options, args) = optparser.parse_args()
    
    num_features = 10000
    
    if len(args) > 0:
        filename = str(args[0])
    if len(args) > 1:
        num_features = str(args[1])
        
    if not filename:
        print 'Requires input file'
        sys.exit(1)
    
    if not num_features:
        describe( filename )
    else:
        describe( filename, num_features )
    
    #fieldNamesToLowercase( filename )