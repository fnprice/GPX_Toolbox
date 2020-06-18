'''----------------------------------------------------------------------------
Name:        FNAI_GPX_Toolbox

Purpose:     Converts a set of GPX files into an ESRI pt and line shapefile.
             There are parameters for speed, distance between points, and maximum
             number of points in a line that are used to produce cleaner line outputs.

Author:      Frank Price (FNAI)

Created:     2019-03-25
Copyright:   (c) FrankP 2019
License:     MIT
#----------------------------------------------------------------------------'''

import arcpy
import os, fnmatch
from os import listdir
from os.path import isfile, join
from datetime import datetime
from dateutil.parser import parse
from arcpy import env

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FNAI GPX Toolbox"
        self.alias = "GPX tool"

        # List of tool classes associated with this toolbox
        self.tools = [FNAI_GPX_Tool]


class FNAI_GPX_Tool(object):
    """------------------------------------------------------------------------
    Description: Takes a folder of GPX files as input and outputs a point and
    a line shapefile.  The point file will contain all track points.  The line
    file will contain the points converted to lines following the parameters
    specified.

    handles errors due to missing DateTime values and invalid GPX files.

    handles errors due to valid but empty GPX files

    in cases of Basic License doesn't recalc extent AND fixes error "Output
    Dataset or Feature Class is same as input" on line 301 when output name edited

    added check for Avenza maps datetime format: 2019-06-25T12:25:54-04:00
       and moved the datetime handling to a separate function (parse_time)

    added repair geometry to each output line fc before merge to handle cases
       of lines composed of only identical points (null geom), also added del of
       final update cursors to prevent locks

    edited to accomodate files with no timestamps

    Potential future additions:
        project to albers
        repair geometry
        progress indicator
        select individual files rather than folder

    Create date: 20190325
    Last mod date: 20190924
    ------------------------------------------------------------------------"""
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FNAI GPX Tool"
        self.description = """Takes a folder of GPX files as input and outputs a
        point and a line shapefile.  The point file will contain all track
        points.  The line will contain the points converted to lines using
        the parameters specified.  Points will not be connected to form lines
        if the maximum speed or distance is exceeded or if there is not at least
        the minimum number of points in a segment."""
        #self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        start_folder = arcpy.Parameter(
            displayName='''Folder containing GPX files (all .gpx files in folder will be merged)''',
            name='start_folder',
            datatype='Folder',
            parameterType='Required',
            direction='Input')

        out_pt_file = arcpy.Parameter(
            displayName='Name for output point file',
            name='out_pt',
            datatype='Feature Class',
            parameterType='Required',
            direction='Output')

        out_ln_file = arcpy.Parameter(
            displayName='Name for output line file',
            name='out_ln',
            datatype='Feature Class',
            parameterType='Required',
            direction='Output')

        max_mph = arcpy.Parameter(
            displayName='Maximum speed traveled (mph) before line is split (Default = 20mph)',
            name='max_mph',
            datatype='Double',
            parameterType='Required',
            direction='Input')

        max_mi = arcpy.Parameter(
            displayName='Maximum distance traveled (mi) before line is split (Default = 0.1mi)',
            name='max_mi',
            datatype='Double',
            parameterType='Required',
            direction='Input')

        min_vertices = arcpy.Parameter(
            displayName='Mininum number of points to form a line (Default = 5)',
            name='min_vertices',
            datatype='Double',
            parameterType='Required',
            direction='Input')

        params = [start_folder, out_pt_file, out_ln_file,
          max_mph, max_mi, min_vertices]

        params[3].value = 20
        params[4].value = 0.1
        params[5].value = 5


        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def initializeParameters(self):
        return

    def updateParameters(self, params):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        # This sets the location of the output to the starting folder with a
        # default name but this can be edited at runtime.
        if params[0].altered:
            folder = params[0].valueAsText
            pt_file_name = 'GPX_points_merged'
            pt_file_cnt = 1

            if 'Default.gdb' in params[1].valueAsText:
                while arcpy.Exists(folder +'\\'+ pt_file_name +str(pt_file_cnt)+'.shp'):
                        pt_file_cnt += 1
                params[1].value = folder +'\\'+ pt_file_name +str(pt_file_cnt)+'.shp'

            ln_file_name = 'GPX_lines_merged'
            ln_file_cnt = 1

            if 'Default.gdb' in params[2].valueAsText:
                while arcpy.Exists(folder +'\\'+ ln_file_name +str(ln_file_cnt)+'.shp'):
                        ln_file_cnt += 1
                params[2].value = folder +'\\'+ ln_file_name +str(ln_file_cnt)+'.shp'

        return

    def updateMessages(self, params):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    # replace from right function
    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    # function for interpreting datetime values
    def parse_time(self, time_str):
        # datetime format example: 2018-08-01T11:31:44Z
        if time_str[-1]=='Z':
            dt_ti_val = parse(time_str)
        # datetime format example: 2019-06-25T12:25:54-04:00
        elif time_str[-6]=='-' or time_str[-6]== '+':
            # get rid of colon in utc offset
            time_str = self.rreplace(time_str,':','',1)
            dt_ti_val = parse(time_str)
        return dt_ti_val

    def execute(self, params, messages):
        """The source code of the tool."""

        # get input parameters
        in_folder = params[0].valueAsText
        out_pt = params[1].valueAsText
        temp_pt = params[1].valueAsText.replace('.shp','_temp.shp')
        out_line = params[2].valueAsText
        temp_line = params[2].valueAsText.replace('.shp','_temp.shp')
        threshold_mph = float(params[3].valueAsText)
        threshold_mi = float(params[4].valueAsText)
        threshold_vertices = float(params[5].valueAsText)

        # only look at files in the folder
        onlyfiles = [f for f in listdir(in_folder) if isfile(join(in_folder, f))]

        # create lists to store names of processed files to merge
        pt_to_merge = []
        ln_to_merge = []

        # define FL Albers spatial ref for later use
        sr_FLAlbers = arcpy.SpatialReference(3087)  #FLAlbers

        GPX_conversion_errors = 0
        Missing_time_stamps = 0

        for i,file in enumerate(onlyfiles,1):
            # if file is a gpx file
            if fnmatch.fnmatch(file, '*.gpx'):
                arcpy.AddMessage('File ' + str(i) + '/' + str(len(onlyfiles)) + ': ' + file)
                # define temp output names in the in_memory workspace
                pt_fc = 'in_memory\\pt_'+str(i)
                ln_fc = 'in_memory\\line_'+str(i)
                # Process: GPX To Features
                input_gpx = in_folder+'\\'+file
                # convert this gpx file to a shapefile
                try:
                    arcpy.GPXtoFeatures_conversion(input_gpx, pt_fc)
                except:
                    arcpy.AddWarning('There is a problem with the format of ' +
                    file + '.  It will be omitted from the merged results. '+
                    'You may be able to convert it using a different method.')
                    GPX_conversion_errors += 1
                    continue

                result = arcpy.GetCount_management(pt_fc)

                if result[0] == '0':
                    arcpy.AddWarning('There are no points in ' +
                    file + '.  It will be omitted from the merged results.')
                    continue
                elif result[0] == 1:
                    arcpy.AddWarning('There is only 1 point in ' +
                    file + '.  It will be omitted from the merged results.')
                    continue

                # add a field to store the id which will group pts into lines
                arcpy.AddField_management(pt_fc,'line_id',"LONG")

                pt_fc_flds = ['OID@','SHAPE@','DateTimeS']
                pt_list = []

                # write point shape file data to a list
                with arcpy.da.SearchCursor(pt_fc,pt_fc_flds) as cursor_all:
                    for row in cursor_all:
                        pt_list.append(list(row))

                # get geometry object from pt shape and project in albers
                geom1 = pt_list[0][1].projectAs(sr_FLAlbers)
                time1_str = pt_list[0][2]
                time1 = None
                time2 = None
                # convert first datetime string to a real datetime value
                try:
                    if time1_str == '':
                        arcpy.AddWarning('First point has no time stamp.')
                    else:
                        time1 = self.parse_time(time1_str)
                except:
                    arcpy.AddWarning('Problem parsing DateTime of first record.')
                    break
                current_line_id = 1
                pt_list[0].append(current_line_id)

                # loop through points in the list starting with the second
                good_pt_list = []
                bad_datetime_cnt = 0
                any_time_stamps = None
                for pt in pt_list[1:]:
                    geom2 = pt[1].projectAs(sr_FLAlbers)
                    time2_str = pt[2]
                    try:
                        if time2_str == '':
##                            arcpy.AddWarning('Point has no time stamp.')
                            pass
                        else:
                            time2 = self.parse_time(time2_str)
                            any_time_stamps = 1
                    except:
                        #if DateTIme other than first record can't be parsed...
                        time2 = time1
                        bad_datetime_cnt += 1
                        pass
                    # calculate miles between geometry objects
                    dist_m = geom1.distanceTo(geom2)
                    dist_mi = dist_m / 1609.344
                    # calculate time difference & speed
                    if time1 is None or time2 is None or time1 == time2:
                        time_diff_h = 0
                    else:
                        time_diff_h = ((time2 - time1).total_seconds())/3600

                    if time_diff_h > 0:
                        mph = dist_mi / time_diff_h
                    else:
                        mph = 0

                    # set the first geom and time variable to equal the second
                    geom1 = geom2
                    time1 = time2
                    # if the speed or distance between pts is exceeded
                    # increase line id
                    if mph > threshold_mph or dist_mi > threshold_mi:
                        current_line_id += 1
                    pt.append(current_line_id)
                    good_pt_list.append(pt)
                    # now loop back to next point until no more

                if not any_time_stamps:
                    arcpy.AddWarning('No point in this file has a time stamp.')
                    Missing_time_stamps += 1
                if bad_datetime_cnt > 0:
                    arcpy.AddWarning(str(bad_datetime_cnt)+' point(s) in a total of '
                    + str(len(pt_list))+' have invalid DateTime.')

                pt_dict = {}
                for point in good_pt_list:
                    pt_dict[point[0]] = point[3]
                with arcpy.da.UpdateCursor(pt_fc,['OID@','line_id']) as cursor_up:
                    for row in cursor_up:
                        if row[0] in pt_dict:
                        # add line id value to output row
                            row[1] = pt_dict[row[0]]
                            # update the row in the pt file
                            cursor_up.updateRow(row)
                        else:
                            cursor_up.deleteRow()


                # disable Z (elevation) and M (routes) in output
                # these caused weird probelms and aren't needed
                env.outputZFlag = "DISABLED"
                env.outputMFlag = "DISABLED"

                # add the pt file to the list of fiels to merge
                pt_to_merge.append(pt_fc)

                # convert the point to lines and add to list of lines to merge
                arcpy.PointsToLine_management(pt_fc, ln_fc, 'line_id')
                # repair geom to handle lines composed of only identical points
                arcpy.RepairGeometry_management(ln_fc)
                ln_to_merge.append(ln_fc)

        if len(pt_to_merge) == 0:
            arcpy.AddError('None of the GPX files contain valid points so no output will be generated.')
        else:
            arcpy.AddWarning('Number of files for which GPX conversion failed: ' + str(GPX_conversion_errors))
            arcpy.AddWarning('Number of files without time stamps: ' + str(Missing_time_stamps))
            # merge and project the point files
            arcpy.AddMessage('Merging point files: ' + str(pt_to_merge) + ' to temp file')
            arcpy.Merge_management(pt_to_merge, temp_pt)
            arcpy.Project_management(temp_pt, out_pt, sr_FLAlbers)
            arcpy.Delete_management(temp_pt)

            #merge and project the line files
            arcpy.AddMessage('Merging line files: ' + str(ln_to_merge)+ ' to temp file')
            arcpy.Merge_management(ln_to_merge, temp_line)
            arcpy.Project_management(temp_line, out_line, sr_FLAlbers)
            arcpy.Delete_management(temp_line)

            # clear in_memory workspace
            arcpy.Delete_management('in_memory')

            # delete short lines
            arcpy.AddMessage('Deleting short lines')
            with arcpy.da.UpdateCursor(out_line,['OID@','SHAPE@','line_id']) as ln_cursor:
                for row in ln_cursor:
                    line_geom = row[1]
                    vertex_cnt = line_geom.pointCount
                    if vertex_cnt < threshold_vertices:
                        ln_cursor.deleteRow()
            # recalculate line_id to equal OID so it makes sense
            with arcpy.da.UpdateCursor(out_line,['OID@','line_id']) as ln_cursor1:
                for row in ln_cursor1:
                    row[1] = row[0]
                    ln_cursor1.updateRow(row)

            #cleanup to prevent locks
            del ln_cursor,ln_cursor1

            # reclaculate fc extent IF available! (not available with basic license)
            lic_type = arcpy.ProductInfo()
            arcpy.AddMessage('License: ' + lic_type)
            if lic_type == 'ArcEditor' or lic_type == 'ArcInfo':
                arcpy.RecalculateFeatureClassExtent_management(out_line)

            arcpy.AddMessage('COMPLETE!')
            arcpy.AddMessage('Merged points = ' + out_pt)
            arcpy.AddMessage('Merged lines = ' + out_line)

        # Done
