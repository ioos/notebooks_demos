---
title: "How to search the IOOS CSW catalog with Python tools"
layout: notebook

---


This notebook demonstrates a how to query the IOOS Catalog [Catalog Service for the Web (CSW)](https://en.wikipedia.org/wiki/Catalog_Service_for_the_Web), parse resulting records to obtain web data service endpoints, and retrieve data from these service endpoints.

Let's start by creating the search filters.
The filter used here constraints the search on a certain geographical region (bounding box), a time span (last week), and some [CF](http://cfconventions.org/Data/cf-standard-names/37/build/cf-standard-name-table.html) variable standard names that represent sea surface temperature.

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
from datetime import datetime

# Region: Northwest coast.
bbox = [-127, 43, -123.75, 48]
min_lon, max_lon = -127, -123.75
min_lat, max_lat = 43, 48

bbox = [min_lon, min_lat, max_lon, max_lat]
crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'

# Temporal range of 1 week.
start = datetime(2017, 4, 14, 0, 0, 0)
stop = datetime(2017, 4, 21, 0, 0, 0)

# Sea surface temperature CF names.
cf_names = ['sea_water_temperature',
            'sea_surface_temperature',
            'sea_water_potential_temperature',
            'equivalent_potential_temperature',
            'sea_water_conservative_temperature',
            'pseudo_equivalent_potential_temperature']
```

With these 3 elements it is possible to assemble a [OGC Filter Encoding (FE)](http://www.opengeospatial.org/standards/filter) using the `owslib.fes`\* module.

\* OWSLib is a Python package for client programming with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, and their related content models.

Although CSW has a built-in feature to find datasets within a specified bounding box, it doesn't have a feature to find datasets within a specified time interval. We therefore create the function `fes_date_filter` below that finds all datasets that have at least part of their data within the specified interval.  So we find all datasets that start before the end of the interval and stop after the beginning of the interval.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
from owslib import fes


def fes_date_filter(start, stop, constraint='overlaps'):
    """
    Take datetime-like objects and returns a fes filter for date range
    (begin and end inclusive).
    NOTE: Truncates the minutes!!!

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> stop = datetime(2010, 1, 1, 12, 30, 59).replace(tzinfo=pytz.utc)
    >>> start = stop - timedelta(days=7)
    >>> begin, end = fes_date_filter(start, stop, constraint='overlaps')
    >>> begin.literal, end.literal
    ('2010-01-01 12:00', '2009-12-25 12:00')
    >>> begin.propertyoperator, end.propertyoperator
    ('ogc:PropertyIsLessThanOrEqualTo', 'ogc:PropertyIsGreaterThanOrEqualTo')
    >>> begin, end = fes_date_filter(start, stop, constraint='within')
    >>> begin.literal, end.literal
    ('2009-12-25 12:00', '2010-01-01 12:00')
    >>> begin.propertyoperator, end.propertyoperator
    ('ogc:PropertyIsGreaterThanOrEqualTo', 'ogc:PropertyIsLessThanOrEqualTo')

    """
    start = start.strftime('%Y-%m-%d %H:00')
    stop = stop.strftime('%Y-%m-%d %H:00')
    if constraint == 'overlaps':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                                literal=stop)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                 literal=start)
    elif constraint == 'within':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                   literal=start)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                              literal=stop)
    else:
        raise NameError('Unrecognized constraint {}'.format(constraint))
    return begin, end
```

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
kw = dict(wildCard='*', escapeChar='\\',
          singleChar='?', propertyname='apiso:AnyText')

or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                  for val in cf_names])

begin, end = fes_date_filter(start, stop)
bbox_crs = fes.BBox(bbox, crs=crs)

filter_list = [
    fes.And(
        [
            bbox_crs,  # bounding box
            begin, end,  # start and end date
            or_filt  # or conditions (CF variable names)
        ]
    )
]
```

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
from owslib.csw import CatalogueServiceWeb


endpoint = 'https://data.ioos.us/csw'

csw = CatalogueServiceWeb(endpoint, timeout=60)
```

We have created a `csw` object, but nothing has been searched yet.

Below we create a `get_csw_records` function that calls the OSWLib method `getrecords2` iteratively to retrieve all the records matching the search criteria specified by the `filter_list`.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
def get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000):
    """Iterate `maxrecords`/`pagesize` times until the requested value in
    `maxrecords` is reached.
    """
    from owslib.fes import SortBy, SortProperty
    # Iterate over sorted results.
    sortby = SortBy([SortProperty('dc:title', 'ASC')])
    csw_records = {}
    startposition = 0
    nextrecord = getattr(csw, 'results', 1)
    while nextrecord != 0:
        csw.getrecords2(constraints=filter_list, startposition=startposition,
                        maxrecords=pagesize, sortby=sortby)
        csw_records.update(csw.records)
        if csw.results['nextrecord'] == 0:
            break
        startposition += pagesize + 1  # Last one is included.
        if startposition >= maxrecords:
            break
    csw.records.update(csw_records)
```

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print(u'[{}]\n{}\n'.format(value.title, key))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 43 records.
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9441102 station, Westport, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9441102
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9442396 station, La Push, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9442396
    
    [(WhiskeyCrShelfish) PCSGA - Whiskey Creek Shellfish Hatchery, Netarts Bay]
    data.nanoos.org-urn_ioos_station_nanoos_wcsh_whiskey1
    
    [(APL-UW) UW/NANOOS NEMO Subsurface profiler near La Push]
    data.nanoos.org-urn_ioos_station_nanoos_apl_nemo
    
    [ce_382-20160410T2230]
    org.oceanobservatories:ce_382-20160410T2230_f070_8f49_1646
    
    [ce_382-20160410T2230]
    ce_382-20160410T2230
    
    [ce_383-20170131T1942]
    ce_383-20170131T1942
    
    [ce_383-20170131T1942]
    org.oceanobservatories:ce_383-20170131T1942_f070_8f49_1646
    
    [CeNCOOS/Models/ROMS/California ROMS/California Coastal Regional Ocean Modeling System (ROMS) Nowcast]
    CA_DAS
    
    [(CMOP) SATURN-03]
    data.nanoos.org-urn_ioos_station_nanoos_cmop_saturn03
    
    [(CMOP) SATURN-04]
    data.nanoos.org-urn_ioos_station_nanoos_cmop_mottb
    
    [COAMPS 12-hour Total Precipitation forecast, 4km]
    COAMPS_4KM_TTL_PRCP
    
    [COAMPS Cloud Base Altitude Forecast, 4km]
    COAMPS_4KM_CLD_BASE
    
    [COAMPS Ground and Sea Surface Temperature, 4km]
    COAMPS_4KM_GRND_SEA_TEMP
    
    [COAMPS IR_heat_flux @ surface, 4km]
    COAMPS_4KM_IR_FLUX
    
    [COAMPS Net short wave radiation at surface, 4km]
    COAMPS_4KM_SOL_RAD
    
    [COAMPS Relative Humidity, 4km]
    COAMPS_4KM_RLTV_HUM
    
    [COAMPS Visibility Forecast, 4km]
    COAMPS_4KM_VISIB
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near ASTORIA CANYON, OR from 2016/03/30 17:00:00 to 2017/07/03 18:11:47.]
    edu.ucsd.cdip:CDIP_179p1_20160330-20170703
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near CLATSOP SPIT, OR from 2016/10/12 17:00:00 to 2017/07/03 18:00:53.]
    edu.ucsd.cdip:CDIP_162p1_20161012-20170703
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near LAKESIDE, OR from 2017/03/31 23:00:00 to 2017/07/03 17:30:42.]
    edu.ucsd.cdip:CDIP_231p1_20170331-20170703
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near LOWER COOK INLET, AK from 2016/12/16 00:00:00 to 2017/07/03 18:09:44.]
    edu.ucsd.cdip:CDIP_204p1_20161216-20170703
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near OCEAN STATION PAPA from 2015/01/01 01:00:00 to 2017/07/03 17:40:54.]
    edu.ucsd.cdip:CDIP_166p1_20150101-20170703
    
    [Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near SCRIPPS NEARSHORE, CA from 2015/01/07 23:00:00 to 2017/07/03 18:00:18.]
    edu.ucsd.cdip:CDIP_201p1_20150107-20170703
    
    [G1SST, 1km blended SST]
    G1_SST_GLOBAL
    
    [(HMSC) Hatfield Marine Sci. Ctr. monitoring site, Newport]
    data.nanoos.org-urn_ioos_station_nanoos_hmsc_newport
    
    [HYbrid Coordinate Ocean Model (HYCOM): Global]
    hycom_global
    
    [(NERRS SOS) Tom's Creek (sostcmet), South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sostcmet
    
    [(NERRS) Station SOSCWQ - Charleston Bridge, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_soscwq
    
    [(NERRS) Station SOSECWQ - Elliot Creek, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosecwq
    
    [(NERRS) Station SOSVAWQ - Valino Island, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosvawq
    
    [(NERRS) Station SOSWIWQ - Winchester Arm, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_soswiwq
    
    [NOAA Coral Reef Watch Operational Daily Near-Real-Time Global 5-km Satellite Coral Bleaching Monitoring Products]
    dhw_5km
    
    [(PSI) PCSGA - Bay Center Port mooring, Willapa Bay]
    data.nanoos.org-urn_ioos_station_nanoos_psi_baycenter
    
    [(PSI) PCSGA - Nahcotta Port hatchery mooring, Willapa Bay]
    data.nanoos.org-urn_ioos_station_nanoos_psi_nahcotta
    
    [Regional Ocean Modeling System (ROMS): Oregon Coast]
    /opendap/hyrax/aggregated/ocean_time_aggregation.ncml
    
    [(SSNERR) SOSNSWQ Station - North Spit-BLM Boat Ramp near North Bend]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosnswq
    
    [UCSC California Current System ROMS Nowcast 10km]
    UCSC
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9432780 station, Charleston, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9432780
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9435380 station, South Beach, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9435380
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9437540 station, Garibaldi, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9437540
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9439040 station, Astoria, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9439040
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9440581 station, Cape Disappointment]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9440581
    

</pre>
</div>
That search returned a lot of records!
What if we are not interested in those model results nor global dataset?
We can those be excluded  from the search with a `fes.Not` filter.

<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
kw = dict(
    wildCard='*',
    escapeChar='\\\\',
    singleChar='?',
    propertyname='apiso:AnyText')


filter_list = [
    fes.And(
        [
            bbox_crs,  # Bounding box
            begin, end,  # start and end date
            or_filt,  # or conditions (CF variable names).
            fes.Not([fes.PropertyIsLike(literal='*NAM*', **kw)]),  # no NAM results
            fes.Not([fes.PropertyIsLike(literal='*CONUS*', **kw)]),  # no NAM results
            fes.Not([fes.PropertyIsLike(literal='*GLOBAL*', **kw)]),  # no NAM results
            fes.Not([fes.PropertyIsLike(literal='*ROMS*', **kw)]),  # no NAM results
        ]
    )
]

get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print(u'[{}]\n{}\n'.format(value.title, key))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 31 records.
    
    [(WhiskeyCrShelfish) PCSGA - Whiskey Creek Shellfish Hatchery, Netarts Bay]
    data.nanoos.org-urn_ioos_station_nanoos_wcsh_whiskey1
    
    [(APL-UW) UW/NANOOS NEMO Subsurface profiler near La Push]
    data.nanoos.org-urn_ioos_station_nanoos_apl_nemo
    
    [ce_382-20160410T2230]
    org.oceanobservatories:ce_382-20160410T2230_f070_8f49_1646
    
    [ce_382-20160410T2230]
    ce_382-20160410T2230
    
    [ce_383-20170131T1942]
    ce_383-20170131T1942
    
    [ce_383-20170131T1942]
    org.oceanobservatories:ce_383-20170131T1942_f070_8f49_1646
    
    [(CMOP) SATURN-03]
    data.nanoos.org-urn_ioos_station_nanoos_cmop_saturn03
    
    [(CMOP) SATURN-04]
    data.nanoos.org-urn_ioos_station_nanoos_cmop_mottb
    
    [COAMPS 12-hour Total Precipitation forecast, 4km]
    COAMPS_4KM_TTL_PRCP
    
    [COAMPS Cloud Base Altitude Forecast, 4km]
    COAMPS_4KM_CLD_BASE
    
    [COAMPS Ground and Sea Surface Temperature, 4km]
    COAMPS_4KM_GRND_SEA_TEMP
    
    [COAMPS IR_heat_flux @ surface, 4km]
    COAMPS_4KM_IR_FLUX
    
    [COAMPS Net short wave radiation at surface, 4km]
    COAMPS_4KM_SOL_RAD
    
    [COAMPS Relative Humidity, 4km]
    COAMPS_4KM_RLTV_HUM
    
    [COAMPS Visibility Forecast, 4km]
    COAMPS_4KM_VISIB
    
    [(HMSC) Hatfield Marine Sci. Ctr. monitoring site, Newport]
    data.nanoos.org-urn_ioos_station_nanoos_hmsc_newport
    
    [(NERRS SOS) Tom's Creek (sostcmet), South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sostcmet
    
    [(NERRS) Station SOSCWQ - Charleston Bridge, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_soscwq
    
    [(NERRS) Station SOSECWQ - Elliot Creek, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosecwq
    
    [(NERRS) Station SOSVAWQ - Valino Island, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosvawq
    
    [(NERRS) Station SOSWIWQ - Winchester Arm, South Slough Reserve]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_soswiwq
    
    [(PSI) PCSGA - Bay Center Port mooring, Willapa Bay]
    data.nanoos.org-urn_ioos_station_nanoos_psi_baycenter
    
    [(PSI) PCSGA - Nahcotta Port hatchery mooring, Willapa Bay]
    data.nanoos.org-urn_ioos_station_nanoos_psi_nahcotta
    
    [(SSNERR) SOSNSWQ Station - North Spit-BLM Boat Ramp near North Bend]
    data.nanoos.org-urn_ioos_station_nanoos_nerrs_sosnswq
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9432780 station, Charleston, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9432780
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9435380 station, South Beach, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9435380
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9437540 station, Garibaldi, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9437540
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9439040 station, Astoria, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9439040
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9440581 station, Cape Disappointment]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9440581
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9440910 station, Toke Point, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9440910
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9441102 station, Westport, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9441102
    

</pre>
</div>
Now we got fewer records to deal with. That's better. But if the user is interested in only some specific service, it is better to filter by a string, like [`CO-OPS`](https://tidesandcurrents.noaa.gov/).

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
filter_list = [
    fes.And(
        [
            bbox_crs,  # Bounding box
            begin, end,  # start and end date
            or_filt,  # or conditions (CF variable names).
            fes.PropertyIsLike(literal='*CO-OPS*', **kw),  # must have CO-OPS
        ]
    )
]

get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print('[{}]\n{}\n'.format(value.title, key))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 8 records.
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9432780 station, Charleston, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9432780
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9435380 station, South Beach, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9435380
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9437540 station, Garibaldi, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9437540
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9439040 station, Astoria, OR]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9439040
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9440581 station, Cape Disappointment]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9440581
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9440910 station, Toke Point, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9440910
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9441102 station, Westport, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9441102
    
    [urn:ioos:station:NOAA.NOS.CO-OPS:9442396 station, La Push, WA]
    opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9442396
    

</pre>
</div>
The easiest way to get more information is to explorer the individual records.
Here is the `abstract` and `subjects` from the station in Astoria, OR.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
import textwrap


value = csw.records['opendap.co-ops.nos.noaa.gov-urn_ioos_station_NOAA.NOS.CO-OPS_9439040']

print('\n'.join(textwrap.wrap(value.abstract)))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    NOAA.NOS.CO-OPS Sensor Observation Service (SOS) Server  This station
    provides the following variables: Air pressure, Air temperature, Sea
    surface height amplitude due to equilibrium ocean tide, Sea water
    temperature, Water surface height above reference datum, Wind from
    direction, Wind speed, Wind speed of gust

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
print('\n'.join(value.subjects))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Air Temperature
    Barometric Pressure
    Conductivity
    Currents
    Datum
    Harmonic Constituents
    Rain Fall
    Relative Humidity
    Salinity
    Visibility
    Water Level
    Water Level Predictions
    Water Temperature
    Winds
    air_pressure
    air_temperature
    sea_surface_height_amplitude_due_to_equilibrium_ocean_tide
    sea_water_temperature
    water_surface_height_above_reference_datum
    wind_from_direction
    wind_speed
    wind_speed_of_gust
    climatologyMeteorologyAtmosphere

</pre>
</div>
The next step is to inspect the type services/schemes available for downloading the data. The easiest way to accomplish that is with by "sniffing" the URLs with `geolinks`.

<div class="prompt input_prompt">
In&nbsp;[11]:
</div>

```python
from geolinks import sniff_link

msg = 'geolink: {geolink}\nscheme: {scheme}\nURL: {url}\n'.format
for ref in value.references:
    print(msg(geolink=sniff_link(ref['url']), **ref))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    geolink: OGC:SOS
    scheme: Astoria
    URL: https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?procedure=urn:ioos:station:NOAA.NOS.CO-OPS:9439040&service=SOS&outputFormat=text/xml; subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&request=DescribeSensor&version=1.0.0
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/air_pressure&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/air_temperature&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/sea_surface_height_amplitude_due_to_equilibrium_ocean_tide&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/sea_water_temperature&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/water_surface_height_above_reference_datum&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/wind_from_direction&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/wind_speed&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/wind_speed_of_gust&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    
    geolink: None
    scheme: WWW:LINK
    URL: https://tidesandcurrents.noaa.gov/images/stationphotos/9439040A.jpg
    
    geolink: None
    scheme: WWW:LINK
    URL: https://tidesandcurrents.noaa.gov/publications/NOAA_Technical_Report_NOS_CO-OPS_030_QC_requirements_doc(revised)-11102004.pdf
    
    geolink: None
    scheme: WWW:LINK
    URL: https://tidesandcurrents.noaa.gov/stationhome.html?id=9439040
    
    geolink: OGC:SOS
    scheme: OGC:SOS
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?acceptVersions=1.0.0&service=SOS&request=GetCapabilities
    

</pre>
</div>
There are many direct links to Comma Separated Value (`CSV`) and
eXtensible Markup Language (`XML`) responses to the various variables available in that station. 

In addition to those links, there are three very interesting links for more information: 1.) the QC document, 2.) the station photo, 3.) the station home page.


For a detailed description of what those `geolink` results mean check the [lookup](https://github.com/OSGeo/Cat-Interop/blob/master/LinkPropertyLookupTable.csv) table.


![](https://tidesandcurrents.noaa.gov/images/stationphotos/9439040A.jpg)

The original search was focused on sea water temperature,
so there is the need to extract only the endpoint for that variable.

PS: see also the [pyoos example](http://ioos.github.io/notebooks_demos/notebooks/2016-10-12-fetching_data/) for fetching data from `CO-OPS`.

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
start, stop
```




    (datetime.datetime(2017, 4, 14, 0, 0), datetime.datetime(2017, 4, 21, 0, 0))



<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
for ref in value.references:
    url = ref['url']
    if 'csv' in url and 'sea' in url and 'temperature' in url:
        print(msg(geolink=sniff_link(url), **ref))
        break
```
<div class="output_area"><div class="prompt"></div>
<pre>
    geolink: OGC:SOS
    scheme: WWW:LINK - text/csv
    URL: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?version=1.0.0&request=GetObservation&observedProperty=http://mmisw.org/ont/cf/parameter/sea_water_temperature&responseFormat=text/csv&eventTime=2017-05-06T22:11:56/2017-05-07T00:11:56&service=SOS&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040
    

</pre>
</div>
Note that the URL returned by the service has some hard-coded start/stop dates.
It is easy to overwrite those with the same dates from the filter.

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
fmt = ('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
       'service=SOS&'
       'eventTime={0:%Y-%m-%dT00:00:00}/{1:%Y-%m-%dT00:00:00}&'
       'observedProperty=http://mmisw.org/ont/cf/parameter/sea_water_temperature&'
       'version=1.0.0&'
       'request=GetObservation&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040&'
       'responseFormat=text/csv')

url = fmt.format(start, stop)
```

Finally, it is possible to download the data directly into a data `pandas` data frame and plot it.

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
import io
import requests
import pandas as pd

r = requests.get(url)

df = pd.read_csv(io.StringIO(r.content.decode('utf-8')),
                 index_col='date_time', parse_dates=True)
```

<div class="prompt input_prompt">
In&nbsp;[16]:
</div>

```python
%matplotlib inline
import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(11, 2.75))
ax = df['sea_water_temperature (C)'].plot(ax=ax)
ax.set_xlabel('')
ax.set_ylabel(r'Sea water temperature ($^\circ$C)')
ax.set_title(value.title)
```




    <matplotlib.text.Text at 0x7f9c462446d8>




![png](data:image/png;base64,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
)

<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2016-12-19-exploring_csw.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2016-12-19-exploring_csw.ipynb) to run a live instance of this notebook.