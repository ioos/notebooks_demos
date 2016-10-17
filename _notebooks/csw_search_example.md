---
layout: notebook
title: ""
---


# Demonstrate CSW query capabilities

We will use the owslib library to construct queries and parse responses from CSW

Specify a CSW endpoint.  You can test if it's working with a getCapabilities
request:

```
<endpoint>?request=GetCapabilities&service=CSW
```

for example:

```
http://catalog.data.gov/csw-
all?service=CSW&version=2.0.2&request=GetCapabilities
```

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
from owslib.csw import CatalogueServiceWeb

endpoints = dict(
    csw_all='http://catalog.data.gov/csw-all',  # Granule level production catalog.
    whoi='http://geoport.whoi.edu/csw',
    geoportal='http://www.ngdc.noaa.gov/geoportal/csw',
    ioos='https://data.ioos.us/csw',
    ioos_dev='https://dev-catalog.ioos.us/csw'
)

csw = CatalogueServiceWeb(endpoints['ioos'], timeout=60)

print(csw.version)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    2.0.2

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
from owslib import fes

filter1 = fes.PropertyIsLike(
    propertyname='apiso:AnyText',
    literal=('*sea_water_salinity*'),
    escapeChar='\\',
    wildCard='*',
    singleChar='?'
)

csw.getrecords2(constraints=[filter1], maxrecords=100, esn='full')

print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print('[{}]: {}'.format(value.title, key))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 10 records.

    [Mooring Temperature and Salinity Data from site WHOTS-5]: OceanSITES:OS_WHOTS_200806_D_MICROCAT-105m
    [BATS BTL Timeseries ExpoCode=33H420090303 Station=BATSBLMA Cast=4]: OceanSITES:OS_BATS-1_BATSBLMA-0245-4_D_BTL
    [Time-series of in situ Temperature, Conductivity, and derived Salinity Data from the ALOHA Cabled Observatory]: OceanSITES:OS_ACO_20111010-00-08_P_CTD3-4726m
    [clark-20150709T1803]: deployments/rutgers/clark-20150709T1803/clark-20150709T1803.nc3.nc
    [None]: OceanSITES:OS_DYFAMED_2000_TSOF
    [BATS BTL Timeseries ExpoCode=320G19900716 Station=BATSCR Cast=1]: OceanSITES:OS_BATS-1_BATSCR-0022-1_D_BTL
    [BATS BTL Timeseries ExpoCode=320G19900813 Station=BATSCR Cast=2]: OceanSITES:OS_BATS-1_BATSCR-0023-2_D_BTL
    [BATS BTL Timeseries ExpoCode=320G19980113 Station=BATSCR Cast=8]: OceanSITES:OS_BATS-1_BATSCR-0112-8_D_BTL
    [Ocean salinity data from surface mooring NTAS deployment 10]: OceanSITES:OS_NTAS_2010_P_TS
    [gichigami-20110701T0123]: deployments/lfiorentino/gichigami-20110701T0123/gichigami-20110701T0123.nc3.nc

</pre>
</div>
Hmmm..... In the query above, we only get 10 records, even though we specified
maxrecords=100.

What's up with that?

Turns out the CSW service specified a MaxRecordDefault that cannot be exceeded.
For example, checking
https://data.ioos.us/csw?request=GetCapabilities&service=CSW we find:

```
<ows:Constraint name="MaxRecordDefault">
    <ows:Value>10</ows:Value>
</ows:Constraint>
```

So we need to loop the getrecords request, incrementing the startposition:

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
from owslib.fes import SortBy, SortProperty

pagesize = 10
maxrecords = 50
sort_order = 'ASC'  # Should be 'ASC' or 'DESC' (ascending or descending).
sort_property = 'dc:title'  # A supported queryable of the CSW.

sortby = SortBy([SortProperty(sort_property, sort_order)])
```

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
startposition = 0

while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=[filter1],
                    startposition=startposition,
                    maxrecords=pagesize,
                    sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L0 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L1 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L2 Forecast
    AOOS/Models/Prince William Sound ROMS/Regional Ocean Modeling System (ROMS) Nowcast
    Arctic Seas Regional Climatology : sea_water_temperature January 0.25 degree
    ASIMet logger data from surface mooring NTAS deployment 1
    ASIMet logger data from surface mooring NTAS deployment 10
    ASIMet logger data from surface mooring NTAS deployment 11
    ASIMet logger data from surface mooring NTAS deployment 12
    ASIMet logger data from surface mooring NTAS deployment 2

    getting records 10 to 20
    ASIMet logger data from surface mooring NTAS deployment 2
    ASIMet logger data from surface mooring NTAS deployment 3
    ASIMet logger data from surface mooring NTAS deployment 4
    ASIMet logger data from surface mooring NTAS deployment 5
    ASIMet logger data from surface mooring NTAS deployment 6
    ASIMet logger data from surface mooring NTAS deployment 7
    ASIMet logger data from surface mooring NTAS deployment 8
    ASIMet logger data from surface mooring NTAS deployment 9
    ASIMet logger data from surface mooring Stratus deployment 1
    ASIMet logger data from surface mooring Stratus deployment 10

    getting records 20 to 30
    ASIMet logger data from surface mooring Stratus deployment 11
    ASIMet logger data from surface mooring Stratus deployment 12
    ASIMet logger data from surface mooring Stratus deployment 2
    ASIMet logger data from surface mooring Stratus deployment 3
    ASIMet logger data from surface mooring Stratus deployment 4
    ASIMet logger data from surface mooring Stratus deployment 5
    ASIMet logger data from surface mooring Stratus deployment 6
    ASIMet logger data from surface mooring Stratus deployment 7
    ASIMet logger data from surface mooring Stratus deployment 8
    ASIMet logger data from surface mooring Stratus deployment 9

    getting records 30 to 40
    ASIMet logger data from surface mooring WHOTS deployment 1
    ASIMet logger data from surface mooring WHOTS deployment 2
    ASIMet logger data from surface mooring WHOTS deployment 3
    ASIMet logger data from surface mooring WHOTS deployment 4
    ASIMet logger data from surface mooring WHOTS deployment 5
    ASIMet logger data from surface mooring WHOTS deployment 6
    ASIMet logger data from surface mooring WHOTS deployment 7
    ASIMet logger data from surface mooring WHOTS deployment 8
    ASIMet logger data from surface mooring WHOTS deployment 9
    bass-20150706T151619Z

    getting records 40 to 50
    bass-20150827T1909
    BATS BTL Timeseries ExpoCode=320G19891119 Station=BATSCR Cast=1
    BATS BTL Timeseries ExpoCode=320G19891119 Station=BATSCR Cast=2
    BATS BTL Timeseries ExpoCode=320G19891119 Station=BATSCR Cast=3
    BATS BTL Timeseries ExpoCode=320G19891119 Station=BATSCR Cast=4
    BATS BTL Timeseries ExpoCode=320G19891119 Station=BATSCR Cast=5
    BATS BTL Timeseries ExpoCode=320G19891219 Station=BATSCR Cast=1
    BATS BTL Timeseries ExpoCode=320G19891219 Station=BATSCR Cast=2
    BATS BTL Timeseries ExpoCode=320G19900115 Station=BATSBLMA Cast=1
    BATS BTL Timeseries ExpoCode=320G19900115 Station=BATSBLMA Cast=2


</pre>
</div>
Okay, now lets add another query filter and add it to the first one

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
filter2 = fes.PropertyIsLike(
    propertyname='apiso:AnyText',
    literal=('*ROMS*'),
    escapeChar='\\',
    wildCard='*', singleChar='?'
)

filter_list = [fes.And([filter1, filter2])]
```

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
startposition = 0
maxrecords = 50

while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition, maxrecords=pagesize, sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L0 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L1 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L2 Forecast
    AOOS/Models/Prince William Sound ROMS/Regional Ocean Modeling System (ROMS) Nowcast
    CBOFS - Chesapeake Bay Operational Forecast System - NOAA CO-OPS - POM
    CeNCOOS/Models/ROMS/California ROMS/California Coastal Regional Ocean Modeling System (ROMS) Forecast
    CeNCOOS/Models/ROMS/California ROMS/California Coastal Regional Ocean Modeling System (ROMS) Nowcast
    CeNCOOS/Models/ROMS/Monterey Bay ROMS (Oct 2010 to Jan 2013)/Monterey Bay (MB) Regional Ocean Modeling System (ROMS) Forecast
    DBOFS - Delaware Bay Operational Forecast System - NOAA CO-OPS - POM
    Regional Ocean Modeling System (ROMS): CNMI

    getting records 10 to 20
    Regional Ocean Modeling System (ROMS): CNMI
    Regional Ocean Modeling System (ROMS): CNMI: Data Assimilating
    Regional Ocean Modeling System (ROMS): Guam
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu
    Regional Ocean Modeling System (ROMS): Oahu: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu South Shore
    Regional Ocean Modeling System (ROMS): Oregon Coast
    Regional Ocean Modeling System (ROMS): Samoa

    getting records 20 to 30
    Regional Ocean Modeling System (ROMS): Samoa: Data Assimilating
    Regional Ocean Modeling System (ROMS): Waikiki
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC Averages
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC History
    ROMS/TOMS 3.0 - New Floria Shelf Application
    Shelf Hypoxia : DAL : ROMS : 2004-2009 climatology obc with oxygen inst rem 20layers
    TBOFS - Tampa Bay Operational Forecast System - NOAA CO-OPS - POM
    UCSC California Current System ROMS Nowcast 10km


</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
import random

choice = random.choice(list(csw.records.keys()))

print(csw.records[choice].title)

csw.records[choice].references
```
<div class="output_area"><div class="prompt"></div>
<pre>
    ROMS/TOMS 3.0 - New Floria Shelf Application

</pre>
</div>



    [{'scheme': 'WWW:LINK',
      'url': 'http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd.html'},
     {'scheme': 'None',
      'url': 'http://www.ncdc.noaa.gov/oa/wct/wct-jnlp-beta.php?singlefile=http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd'},
     {'scheme': 'None',
      'url': 'http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd'},
     {'scheme': 'None',
      'url': 'http://crow.marine.usf.edu:8080/thredds/wms/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd?service=WMS&version=1.3.0&request=GetCapabilities'}]



Lets see what the full XML record looks like

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
import xml.dom.minidom

xml = xml.dom.minidom.parseString(csw.records[choice].xml)

print(xml.toprettyxml())
```
<div class="output_area"><div class="prompt"></div>
<pre>
    <?xml version="1.0" ?>
    <csw:SummaryRecord xmlns:apiso="http://www.opengis.net/cat/csw/apiso/1.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:dif="http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/" xmlns:fgdc="http://www.opengis.net/cat/csw/csdgm" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gml="http://www.opengis.net/gml" xmlns:inspire_common="http://inspire.ec.europa.eu/schemas/common/1.0" xmlns:inspire_ds="http://inspire.ec.europa.eu/schemas/inspire_ds/1.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:os="http://a9.com/-/spec/opensearch/1.1/" xmlns:ows="http://www.opengis.net/ows" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:srv="http://www.isotc211.org/2005/srv" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xs="
http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    	<dc:identifier>WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd</dc:identifier>
    	<dc:title>ROMS/TOMS 3.0 - New Floria Shelf Application</dc:title>
    	<dc:type>dataset</dc:type>
    	<dc:subject>West Florida Shelf Nowcast/Forecast System</dc:subject>
    	<dc:subject>College of Marine Science</dc:subject>
    	<dc:subject> University of South Florida</dc:subject>
    	<dc:subject>sea_floor_depth</dc:subject>
    	<dc:subject>sea_surface_height</dc:subject>
    	<dc:subject>northward_sea_water_vertically_integrated_velocity_assuming_no_tide</dc:subject>
    	<dc:subject>eastward_sea_water_velocity_assuming_no_tide</dc:subject>
    	<dc:subject>northward_sea_water_velocity_assuming_no_tide</dc:subject>
    	<dc:subject>upward_sea_water_velocity_assuming_no_tide</dc:subject>
    	<dc:subject>sea_water_potential_temperature</dc:subject>
    	<dc:subject>sea_water_salinity</dc:subject>
    	<dc:subject>forecast_period</dc:subject>
    	<dc:subject>ocean_s_coordinate_g1</dc:subject>
    	<dc:subject>ocean_s_coordinate_g1</dc:subject>
    	<dc:subject>longitude</dc:subject>
    	<dc:subject>latitude</dc:subject>
    	<dc:subject>longitude</dc:subject>
    	<dc:subject>latitude</dc:subject>
    	<dc:subject>longitude</dc:subject>
    	<dc:subject>latitude</dc:subject>
    	<dc:subject>longitude</dc:subject>
    	<dc:subject>latitude</dc:subject>
    	<dc:subject>time</dc:subject>
    	<dc:subject>forecast_reference_time</dc:subject>
    	<dct:references scheme="WWW:LINK">http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd.html</dct:references>
    	<dct:references scheme="None">http://www.ncdc.noaa.gov/oa/wct/wct-jnlp-beta.php?singlefile=http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd</dct:references>
    	<dct:references scheme="None">http://crow.marine.usf.edu:8080/thredds/dodsC/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd</dct:references>
    	<dct:references scheme="None">http://crow.marine.usf.edu:8080/thredds/wms/WFS_ROMS_NF_model/USF_Ocean_Circulation_Group_West_Florida_Shelf_Daily_ROMS_Nowcast_Forecast_Model_Data_best.ncd?service=WMS&amp;version=1.3.0&amp;request=GetCapabilities</dct:references>
    	<dc:relation/>
    	<dct:modified>2014-06-25</dct:modified>
    	<ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326" dimensions="2">
    		<ows:LowerCorner>24.31 -90.47</ows:LowerCorner>
    		<ows:UpperCorner>30.78 -80.45</ows:UpperCorner>
    	</ows:BoundingBox>
    </csw:SummaryRecord>


</pre>
</div>
Yuk!  That's why we use OWSlib!  :-)

Now add contraint to return only records that have either the OPeNDAP or SOS
service.

Let's first see what services are advertised:

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')
```
<div class="output_area"><div class="prompt"></div>
<pre>
    ['THREDDS OPeNDAP,Open Geospatial Consortium Web Map Service (WMS),THREDDS NetCDF Subset Service', 'ERDDAP OPeNDAP', 'Open Geospatial Consortium Web Map Service (WMS),Open Geospatial Consortium Web Feature Service (WFS)', 'THREDDS OPeNDAP,Open Geospatial Consortium Web Coverage Service (WCS),Open Geospatial Consortium Web Map Service (WMS),THREDDS NetCDF Subset Service', 'THREDDS OPeNDAP,Open Geospatial Consortium Sensor Observation Service (SOS),THREDDS HTTP Service', 'Open Geospatial Consortium Web Feature Service (WFS),Open Geospatial Consortium Web Map Service (WMS)', 'THREDDS OPeNDAP,Open Geospatial Consortium Web Coverage Service (WCS),THREDDS NetCDF Subset Service', 'OPeNDAP:OPeNDAP,OGC:WCS,OGC:WMS,UNIDATA:NCSS', 'OPeNDAP:OPeNDAP,file', 'OPeNDAP:OPeNDAP,OGC:WMS,UNIDATA:NCSS', 'THREDDS OPeNDAP,Open Geospatial Consortium Sensor Observation Service (SOS)', 'ERDDAP tabledap,OPeNDAP,ERDDAP Subset', 'OPeNDAP:OPeNDAP,OGC:SOS', 'THREDDS OPeNDAP,Open Geospatial Consortium Web Coverage Service (WCS),Open
Geospatial Consortium Web Map Service (WMS),Open Geospatial Consortium Sensor Observation Service (SOS),THREDDS HTTP Service', 'OPeNDAP:OPeNDAP,OGC:SOS,file', 'THREDDS OPeNDAP,THREDDS NetCDF Subset Service', 'OPeNDAP:OPeNDAP', 'THREDDS OPeNDAP,Open Geospatial Consortium Web Map Service (WMS)', 'OPeNDAP:OPeNDAP,OGC:WMS,UNIDATA:NCSS,file', 'OPeNDAP:OPeNDAP,OGC:WCS,OGC:WMS', 'OPeNDAP:OPeNDAP,OGC:WMS,file', 'THREDDS OPeNDAP,Open Geospatial Consortium Web Map Service (WMS),THREDDS HTTP Service', 'THREDDS OPeNDAP,THREDDS HTTP Service', 'OGC:SOS', 'THREDDS OPeNDAP', 'OPeNDAP:OPeNDAP,OGC:WMS', 'Open Geospatial Consortium Web Map Service (WMS)']

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
services = ['OPeNDAP', 'SOS']

service_filt = fes.Or(
    [fes.PropertyIsLike(propertyname='apiso:ServiceType',
                        literal=('*%s*' % val),
                        escapeChar='\\',
                        wildCard='*',
                        singleChar='?')
     for val in services])

filter_list = [fes.And([filter1, filter2, service_filt])]
```

<div class="prompt input_prompt">
In&nbsp;[11]:
</div>

```python
startposition = 0

while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition,
                    maxrecords=pagesize,
                    sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L0 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L1 Forecast
    AOOS/Models/Prince William Sound ROMS/Prince William Sound (PWS) Regional Ocean Modeling System (ROMS) L2 Forecast
    AOOS/Models/Prince William Sound ROMS/Regional Ocean Modeling System (ROMS) Nowcast
    CBOFS - Chesapeake Bay Operational Forecast System - NOAA CO-OPS - POM
    CeNCOOS/Models/ROMS/California ROMS/California Coastal Regional Ocean Modeling System (ROMS) Forecast
    CeNCOOS/Models/ROMS/California ROMS/California Coastal Regional Ocean Modeling System (ROMS) Nowcast
    CeNCOOS/Models/ROMS/Monterey Bay ROMS (Oct 2010 to Jan 2013)/Monterey Bay (MB) Regional Ocean Modeling System (ROMS) Forecast
    DBOFS - Delaware Bay Operational Forecast System - NOAA CO-OPS - POM
    Regional Ocean Modeling System (ROMS): CNMI

    getting records 10 to 20
    Regional Ocean Modeling System (ROMS): CNMI
    Regional Ocean Modeling System (ROMS): CNMI: Data Assimilating
    Regional Ocean Modeling System (ROMS): Guam
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu
    Regional Ocean Modeling System (ROMS): Oahu: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu South Shore
    Regional Ocean Modeling System (ROMS): Oregon Coast
    Regional Ocean Modeling System (ROMS): Samoa

    getting records 20 to 30
    Regional Ocean Modeling System (ROMS): Samoa: Data Assimilating
    Regional Ocean Modeling System (ROMS): Waikiki
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC Averages
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC History
    ROMS/TOMS 3.0 - New Floria Shelf Application
    Shelf Hypoxia : DAL : ROMS : 2004-2009 climatology obc with oxygen inst rem 20layers
    TBOFS - Tampa Bay Operational Forecast System - NOAA CO-OPS - POM
    UCSC California Current System ROMS Nowcast 10km


</pre>
</div>
Let's try adding a search for a non-existant service, which should result in no
records back:

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
val = 'not_a_real_service'

filter3 = fes.PropertyIsLike(
    propertyname='apiso:ServiceType',
    literal=('*%s*' % val),
    escapeChar='\\',
    wildCard='*',
    singleChar='?'
)

filter_list = [fes.And([filter1, filter2, filter3])]

csw.getrecords2(constraints=filter_list, maxrecords=100, esn='full')

print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print('[{}]: {}'.format(value.title, key))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 0 records.


</pre>
</div>
Good!

Now add bounding box constraint. To specify lon,lat order for bbox (which we
want to do so that we can use the same bbox with either geoportal server or
pycsw requests), we need to request the bounding box specifying the CRS84
coordinate reference system.   The CRS84 option is available in `pycsw 1.1.10`+.
The ability to specify the `crs` in the bounding box request is available in
`owslib 0.8.12`+.  For more info on the bounding box problem and how it was
solved, see this [pycsw issue](https://github.com/geopython/pycsw/issues/287),
this [geoportal server issue](https://github.com/Esri/geoportal-
server/issues/124), and this [owslib
issue](https://github.com/geopython/OWSLib/issues/201)

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
# [lon_min, lat_min, lon_max, lat_max]
bbox = [-158.4, 21.24, -157.5, 21.77]
bbox_filter = fes.BBox(bbox, crs='urn:ogc:def:crs:OGC:1.3:CRS84')

filter_list = [fes.And([filter1, filter2, service_filt, bbox_filter])]

startposition = 0

while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition, maxrecords=pagesize, sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands
    Regional Ocean Modeling System (ROMS): Main Hawaiian Islands: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu
    Regional Ocean Modeling System (ROMS): Oahu: Data Assimilating
    Regional Ocean Modeling System (ROMS): Oahu South Shore
    Regional Ocean Modeling System (ROMS): Waikiki


</pre>
</div>
Now add time contraints.  Here we first define a function that will return
records if any data in the records overlaps the specified time period

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
def date_range(start, stop, constraint='overlaps'):
    """
    Take start and stop datetime objects and return a `fes.PropertyIs<>` filter.

    """
    start = start.strftime('%Y-%m-%d %H:%M')
    stop = stop.strftime('%Y-%m-%d %H:%M')

    if constraint == 'overlaps':
        begin = fes.PropertyIsLessThanOrEqualTo(
            propertyname='apiso:TempExtent_begin', literal=stop
        )
        end = fes.PropertyIsGreaterThanOrEqualTo(
            propertyname='apiso:TempExtent_end', literal=start
        )
    elif constraint == 'within':
        begin = fes.PropertyIsGreaterThanOrEqualTo(
            propertyname='apiso:TempExtent_begin', literal=start
        )
        end = fes.PropertyIsLessThanOrEqualTo(
            propertyname='apiso:TempExtent_end', literal=stop
        )
    return begin, end
```

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
from datetime import datetime, timedelta

now = datetime.utcnow()
start = now - timedelta(days=3)
stop = now + timedelta(days=3)

print('{} to {}'.format(start, stop))

start, stop = date_range(start, stop)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    2016-10-08 17:38:35.456314 to 2016-10-14 17:38:35.456314

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[16]:
</div>

```python
filter_list = [fes.And([filter1, filter2, service_filt, bbox_filter, start, stop])]

startposition = 0
while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition,
                    maxrecords=pagesize,
                    sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10


</pre>
</div>
Now add a NOT filter to eliminate some entries

<div class="prompt input_prompt">
In&nbsp;[17]:
</div>

```python
kw = dict(
    wildCard='*',
    escapeChar='\\',
    singleChar='?',
    propertyname='apiso:AnyText')

not_filt = fes.Not([fes.PropertyIsLike(literal='*Waikiki*', **kw)])
```

<div class="prompt input_prompt">
In&nbsp;[18]:
</div>

```python
filter_list = [fes.And([filter1, filter2, service_filt, bbox_filter, start, stop, not_filt])]

startposition = 0
while True:
    print('getting records %d to %d' % (startposition, startposition+pagesize))
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition, maxrecords=pagesize, sortby=sortby)
    for rec, item in csw.records.items():
        print(item.title)
    print()
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    getting records 0 to 10


</pre>
</div>
Hopefully this notebook demonstrated some of the power (and complexity) of CSW!
;-)
