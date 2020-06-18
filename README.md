# GPX_Toolbox
An ESRI Python Toolbox that converts multiple .gpx (GPS exchange XML format) files to a single point and line shapefile.  

**Users can limit the points used to create the output line file by:**
* Max speed of travel
* Max distance between points
* Minimum number of points to form a line  

These options create a cleaner output line file by allowing omission of bad GPS locations and, for example, data which was collected at highway speeds rather than off road.

ALL input points from the gpx file are returned in the output point shape file.  The limiting options are only used in creating the line output.

## Getting Started

### Dependencies

* ArcMap (ArcGIS for Desktop) version 10.2 or greater (may work with earlier versions but not tested)
* Python 2.7
* No additional packages are required beyond those in the default ESRI installation

### Installing

* Just copy the .pyt folder to an accessible location on your computer

### Executing program

* Navigate to the .pyt file in the Catalog window of ArcMap and double click to run
* Add the .pyt to ArcToolbox for easier access
* In the ArcGIS tool interface select a folder containing one or more .gpx files as input
* You can change the name for the output point and line files which  will be created, or they will be created with a default name in the    folder containing the .gpx files

![Screenshot of ArcGIS interface](https://github.com/fnprice/GPX_Toolbox/blob/master/GPX_Toolbox_screenshot.png)

## Authors

Frank Price (Florida Natural Areas Inventory)

## Version History

* v1 initial release

* v2 handles errors due to missing DateTime values and invalid GPX files.

* v3 handles errors due to valid but empty GPX files

* v4 in cases of Basic License doesn't recalc extent AND fixes error "Output
Dataset or Feature Class is same as input" on line 301 when output name edited

* v5 added check for Avenza maps datetime format: 2019-06-25T12:25:54-04:00
and moved the datetime handling to a separate function (parse_time)

* v6 added repair geometry to each output line fc before merge to handle cases
of lines composed of only identical points (null geom), also added del of
final update cursors to prevent locks

* v7 edited to accomodate files with no timestamps

## License

The MIT License (MIT)

Copyright (c) 2020 Frank Price

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments

Created with support of the Florida Fish and Wildlife Conservation Commission Invasive Plant Management Section
