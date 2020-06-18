# GPX_Toolbox
An ESRI Python Toolbox created to convert .gpx files to a point and line shapefile.  Users can set limits for max speed of travel, max distance between points, and the minimum number of points to form a line.  These options allow omission of bad locations and, for example, data which was collected at highway speeds rather than off road.

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
