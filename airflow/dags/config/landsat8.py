"""
/*********************************************************************************/
 *  The MIT License (MIT)                                                         *
 *                                                                                *
 *  Copyright (c) 2014 EOX IT Services GmbH                                       *
 *                                                                                *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy  *
 *  of this software and associated documentation files (the "Software"), to deal *
 *  in the Software without restriction, including without limitation the rights  *
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     *
 *  copies of the Software, and to permit persons to whom the Software is         *
 *  furnished to do so, subject to the following conditions:                      *
 *                                                                                *
 *  The above copyright notice and this permission notice shall be included in    *
 *  all copies or substantial portions of the Software.                           *
 *                                                                                *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR    *
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,      *
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE   *
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER        *
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, *
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE *
 *  SOFTWARE.                                                                     *
 *                                                                                *
 *********************************************************************************/
"""

from datetime import datetime, timedelta
import os
import config
from collections import namedtuple
from datetime import timedelta

#
# DAG
#
dag_schedule_interval='@hourly'
dagrun_timeout=timedelta(hours=1)
catchup=False

#
# Collection
#
id = "Landsat8"
platformname = 'Landsat-8'
collection_dir = os.path.join(config.base_dir, platformname)
download_dir = os.path.join(collection_dir,"download")
process_dir = os.path.join(collection_dir,"process")
repository_dir = os.path.join(collection_dir,"repository")
original_package_upload_dir = os.path.join(collection_dir,"upload")
original_package_download_base_url = "http://cloudsdi.geo-solutions.it/data/landsa8/L8/"

#
# Search and Download
#

download_url = 'http://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz'

Landsat8Area = namedtuple("Landsat8Area", [
    "name",
    "paths_rows",
    "bands"
])

# please change the number of days to increase/decrease the time interval for searching
startdate = datetime.today() - timedelta(days=100)
enddate = datetime.now()
filter_max = 5

ascending = "ASC"
descending = "DESC"

# please use acquisitiondate or cloudCover to order by 
order_by = "acquisitiondate"
# please use ascending or descending for ordering type
order_type = ascending

download_max = 1

# For multi paths/rows, please add different paths/rows in pairs  e.g: paths_rows= [(37,17), (38,18)] which will search for those 2 scenes.
# For single path/row, please declare as following example: paths_rows=[(80,37)]
AREAS = [
    Landsat8Area(name="B1_B11", paths_rows=[(37,17), (38,18), (39,19)], bands=range(1, 12)),
    # These are just some dummy areas in order to test generation of
    # multiple DAGs
    #Landsat8Area(name="neighbour", paths_rows=[(80,37)], bands=[1, 2, 3, 7]),
    #Landsat8Area(name="other", paths_rows=[(111,27)], bands=range(1, 12)),
]

cloud_coverage = 90.9

#
# GeoServer
#
geoserver_workspace = "landsat"
geoserver_featuretype = "product"
geoserver_layer = "LANDSAT8"
geoserver_coverage = "LANDSAT8"
geoserver_oseo_collection="LANDSAT8"
geoserver_oseo_wfs_format = "application/json"
geoserver_oseo_wfs_version = "2.0.0"
geoserver_oseo_wms_width = 512
geoserver_oseo_wms_height = 512
geoserver_oseo_wms_format = "image/jpeg"
geoserver_oseo_wms_version = "1.3.0"
geoserver_oseo_wcs_scale_i = 0.1
geoserver_oseo_wcs_scale_j = 0.1
geoserver_oseo_wcs_format = "geotiff"
geoserver_oseo_wcs_version = "2.0.1"

#
# Product
#

try:
    from override.landsat8 import *
except:
    pass
