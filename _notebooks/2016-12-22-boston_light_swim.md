---
title: "The Boston Light Swim temperature analysis with Python"
layout: notebook

---

In the past we demonstrated how to perform a CSW catalog search with [`OWSLib`](https://ioos.github.io/notebooks_demos//notebooks/2016-12-19-exploring_csw),
and how to obtain near real-time data with [`pyoos`](https://ioos.github.io/notebooks_demos//notebooks/2016-10-12-fetching_data).
In this notebook we will use both to find all observations and model data around the Boston Harbor to access the sea water temperature.


This workflow is part of an example to advise swimmers of the annual [Boston lighthouse swim](http://bostonlightswim.org/) of the Boston Harbor water temperature conditions prior to the race. For more information regarding the workflow presented here see [Signell, Richard P.; Fernandes, Filipe; Wilcox, Kyle.   2016. "Dynamic Reusable Workflows for Ocean Science." *J. Mar. Sci. Eng.* 4, no. 4: 68](http://dx.doi.org/10.3390/jmse4040068).

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import warnings

# Suppresing warnings for a "pretty output."
warnings.simplefilter('ignore')
```

This notebook is quite big and complex,
so to help us keep things organized we'll define a cell with the most important options and switches.

Below we can define the date,
bounding box, phenomena `SOS` and `CF` names and units,
and the catalogs we will search.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
%%writefile config.yaml

# Specify a YYYY-MM-DD hh:mm:ss date or integer day offset.
# If both start and stop are offsets they will be computed relative to datetime.today() at midnight.
# Use the dates commented below to reproduce the last Boston Light Swim event forecast.
date:
    start: -5 # 2016-8-16 00:00:00
    stop: +4 # 2016-8-29 00:00:00

run_name: 'latest'

# Boston harbor.
region:
    bbox: [-71.3, 42.03, -70.57, 42.63]
    # Try the bounding box below to see how the notebook will behave for a different region.
    #bbox: [-74.5, 40, -72., 41.5]
    crs: 'urn:ogc:def:crs:OGC:1.3:CRS84'

sos_name: 'sea_water_temperature'

cf_names:
    - sea_water_temperature
    - sea_surface_temperature
    - sea_water_potential_temperature
    - equivalent_potential_temperature
    - sea_water_conservative_temperature
    - pseudo_equivalent_potential_temperature

units: 'celsius'

catalogs:
    - https://data.ioos.us/csw
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Overwriting config.yaml

</pre>
</div>
We'll print some of the search configuration options along the way to keep track of them.

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
import os
import shutil
from datetime import datetime
from ioos_tools.ioos import parse_config

config = parse_config('config.yaml')

# Saves downloaded data into a temporary directory.
save_dir = os.path.abspath(config['run_name'])
if os.path.exists(save_dir):
    shutil.rmtree(save_dir)
os.makedirs(save_dir)

fmt = '{:*^64}'.format
print(fmt('Saving data inside directory {}'.format(save_dir)))
print(fmt(' Run information '))
print('Run date: {:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow()))
print('Start: {:%Y-%m-%d %H:%M:%S}'.format(config['date']['start']))
print('Stop: {:%Y-%m-%d %H:%M:%S}'.format(config['date']['stop']))
print('Bounding box: {0:3.2f}, {1:3.2f},'
      '{2:3.2f}, {3:3.2f}'.format(*config['region']['bbox']))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Saving data inside directory /home/filipe/IOOS/notebooks_demos/notebooks/latest
    *********************** Run information ************************
    Run date: 2018-02-27 23:06:25
    Start: 2018-02-22 00:00:00
    Stop: 2018-03-03 00:00:00
    Bounding box: -71.30, 42.03,-70.57, 42.63

</pre>
</div>
We already created an `OWSLib.fes` filter [before](https://ioos.github.io/notebooks_demos//notebooks/2016-12-19-exploring_csw).
The main difference here is that we do not want the atmosphere model data,
so we are filtering out all the `GRIB-2` data format.

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
def make_filter(config):
    from owslib import fes
    from ioos_tools.ioos import fes_date_filter
    kw = dict(wildCard='*', escapeChar='\\',
              singleChar='?', propertyname='apiso:AnyText')

    or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                      for val in config['cf_names']])

    not_filt = fes.Not([fes.PropertyIsLike(literal='GRIB-2', **kw)])

    begin, end = fes_date_filter(config['date']['start'],
                                 config['date']['stop'])
    bbox_crs = fes.BBox(config['region']['bbox'],
                        crs=config['region']['crs'])
    filter_list = [fes.And([bbox_crs, begin, end, or_filt, not_filt])]
    return filter_list


filter_list = make_filter(config)
```

In the cell below we ask the catalog for all the returns that match the filter and have an OPeNDAP endpoint.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
from ioos_tools.ioos import service_urls, get_csw_records
from owslib.csw import CatalogueServiceWeb


dap_urls = []
print(fmt(' Catalog information '))
for endpoint in config['catalogs']:
    print('URL: {}'.format(endpoint))
    try:
        csw = CatalogueServiceWeb(endpoint, timeout=120)
    except Exception as e:
        print('{}'.format(e))
        continue
    csw = get_csw_records(csw, filter_list, esn='full')
    OPeNDAP = service_urls(csw.records, identifier='OPeNDAP:OPeNDAP')
    odp = service_urls(csw.records, identifier='urn:x-esri:specification:ServiceType:odp:url')
    dap = OPeNDAP + odp
    dap_urls.extend(dap)

    print('Number of datasets available: {}'.format(len(csw.records.keys())))

    for rec, item in csw.records.items():
        print('{}'.format(item.title))
    if dap:
        print(fmt(' DAP '))
        for url in dap:
            print('{}.html'.format(url))
    print('\n')

# Get only unique endpoints.
dap_urls = list(set(dap_urls))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    ********************* Catalog information **********************
    URL: https://data.ioos.us/csw
    Number of datasets available: 20
    G1SST, 1km blended SST
    HYbrid Coordinate Ocean Model (HYCOM): Global
    NECOFS (FVCOM) - Scituate - Latest Forecast
    NECOFS Massachusetts (FVCOM) - Boston - Latest Forecast
    NECOFS Massachusetts (FVCOM) - Massachusetts Coastal - Latest Forecast
    NERACOOS Gulf of Maine Ocean Array: Realtime Buoy Observations: A01 Massachusetts Bay: A01 OPTICS3m Massachusetts Bay
    NERACOOS Gulf of Maine Ocean Array: Realtime Buoy Observations: A01 Massachusetts Bay: A01 OPTODE51m Massachusetts Bay
    NOAA Coral Reef Watch Operational Daily Near-Real-Time Global 5-km Satellite Coral Bleaching Monitoring Products
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC Averages
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC History
    COAWST Modeling System: USEast: ROMS-WRF-SWAN coupled model (aka CNAPS)
    Coupled Northwest Atlantic Prediction System (CNAPS)
    Department of Physical Oceanography, School of Marine Sciences, University of Maine A01 Accelerometer Buoy Sensor
    Department of Physical Oceanography, School of Marine Sciences, University of Maine A01 Met Buoy Sensor
    Department of Physical Oceanography, School of Marine Sciences, University of Maine A01 Sbe37 1m Buoy Sensor
    Department of Physical Oceanography, School of Marine Sciences, University of Maine A01 Sbe37 20m Buoy Sensor
    Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near ASTORIA CANYON, OR from 2017/08/03 18:00:00 to 2018/02/26 17:57:08.
    Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near GRAYS HARBOR, WA from 2017/06/29 16:00:00 to 2018/02/26 17:30:16.
    Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near LAKESIDE, OR from 2017/03/31 23:00:00 to 2018/02/26 17:30:55.
    Directional wave and sea surface temperature measurements collected in situ by Datawell Mark 3 directional buoy located near LOWER COOK INLET, AK from 2016/12/16 00:00:00 to 2018/02/26 18:09:36.
    ***************************** DAP ******************************
    http://oos.soest.hawaii.edu/thredds/dodsC/hioos/satellite/dhw_5km.html
    http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best.html
    http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/036p1_rt.nc.html
    http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/179p1_rt.nc.html
    http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/204p1_rt.nc.html
    http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/231p1_rt.nc.html
    http://thredds.secoora.org/thredds/dodsC/G1_SST_GLOBAL.nc.html
    http://thredds.secoora.org/thredds/dodsC/SECOORA_NCSU_CNAPS.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/DSG/SOS/A01/OPTICS_S3m/HistoricRealtime.html
    http://www.neracoos.org/thredds/dodsC/UMO/DSG/SOS/A01/OPTODE51m/HistoricRealtime.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.accelerometer.realtime.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.met.realtime.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.1m.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.20m.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc.html
    
    

</pre>
</div>
We found some models, and observations from NERACOOS there.
However, we do know that there are some buoys from NDBC and CO-OPS available too.
Also, those NERACOOS observations seem to be from a [CTD](http://www.neracoos.org/thredds/dodsC/UMO/DSG/SOS/A01/CTD1m/HistoricRealtime/Agg.ncml.html) mounted at 65 meters below the sea surface. Rendering them useless from our purpose.

So let's use the catalog only for the models by filtering the observations with `is_station` below.
And we'll rely `CO-OPS` and `NDBC` services for the observations.

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
from timeout_decorator import TimeoutError
from ioos_tools.ioos import is_station

# Filter out some station endpoints.
non_stations = []
for url in dap_urls:
    try:
        if not is_station(url):
            non_stations.append(url)
    except (IOError, OSError, RuntimeError, TimeoutError) as e:
        print('Could not access URL {}.html\n{!r}'.format(url, e))

dap_urls = non_stations

print(fmt(' Filtered DAP '))
for url in dap_urls:
    print('{}.html'.format(url))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Could not access URL http://thredds.secoora.org/thredds/dodsC/G1_SST_GLOBAL.nc.html
    TimeoutError()
    Could not access URL http://thredds.secoora.org/thredds/dodsC/SECOORA_NCSU_CNAPS.nc.html
    TimeoutError()
    ************************* Filtered DAP *************************
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.met.realtime.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.accelerometer.realtime.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.1m.nc.html
    http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.20m.nc.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc.html
    http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best.html
    http://oos.soest.hawaii.edu/thredds/dodsC/hioos/satellite/dhw_5km.html

</pre>
</div>
Now we can use `pyoos` collectors for `NdbcSos`,

<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos

collector_ndbc = NdbcSos()

collector_ndbc.set_bbox(config['region']['bbox'])
collector_ndbc.end_time = config['date']['stop']
collector_ndbc.start_time = config['date']['start']
collector_ndbc.variables = [config['sos_name']]

ofrs = collector_ndbc.server.offerings
title = collector_ndbc.server.identification.title
print(fmt(' NDBC Collector offerings '))
print('{}: {} offerings'.format(title, len(ofrs)))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    ******************* NDBC Collector offerings *******************
    National Data Buoy Center SOS: 1017 offerings

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
import pandas as pd
from ioos_tools.ioos import collector2table

ndbc = collector2table(collector=collector_ndbc,
                       config=config,
                       col='sea_water_temperature (C)')

if ndbc:
    data = dict(
        station_name=[s._metadata.get('station_name') for s in ndbc],
        station_code=[s._metadata.get('station_code') for s in ndbc],
        sensor=[s._metadata.get('sensor') for s in ndbc],
        lon=[s._metadata.get('lon') for s in ndbc],
        lat=[s._metadata.get('lat') for s in ndbc],
        depth=[s._metadata.get('depth') for s in ndbc],
    )

table = pd.DataFrame(data).set_index('station_code')
table
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>depth</th>
      <th>lat</th>
      <th>lon</th>
      <th>sensor</th>
      <th>station_name</th>
    </tr>
    <tr>
      <th>station_code</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>44013</th>
      <td>0.6</td>
      <td>42.346</td>
      <td>-70.651</td>
      <td>urn:ioos:sensor:wmo:44013::watertemp1</td>
      <td>BOSTON 16 NM East of Boston, MA</td>
    </tr>
  </tbody>
</table>
</div>



and `CoopsSos`.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
from pyoos.collectors.coops.coops_sos import CoopsSos

collector_coops = CoopsSos()

collector_coops.set_bbox(config['region']['bbox'])
collector_coops.end_time = config['date']['stop']
collector_coops.start_time = config['date']['start']
collector_coops.variables = [config['sos_name']]

ofrs = collector_coops.server.offerings
title = collector_coops.server.identification.title
print(fmt(' Collector offerings '))
print('{}: {} offerings'.format(title, len(ofrs)))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    ********************* Collector offerings **********************
    NOAA.NOS.CO-OPS SOS: 1189 offerings

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
coops = collector2table(collector=collector_coops,
                        config=config,
                        col='sea_water_temperature (C)')

if coops:
    data = dict(
        station_name=[s._metadata.get('station_name') for s in coops],
        station_code=[s._metadata.get('station_code') for s in coops],
        sensor=[s._metadata.get('sensor') for s in coops],
        lon=[s._metadata.get('lon') for s in coops],
        lat=[s._metadata.get('lat') for s in coops],
        depth=[s._metadata.get('depth') for s in coops],
    )

table = pd.DataFrame(data).set_index('station_code')
table
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>depth</th>
      <th>lat</th>
      <th>lon</th>
      <th>sensor</th>
      <th>station_name</th>
    </tr>
    <tr>
      <th>station_code</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>44013</th>
      <td>0.6</td>
      <td>42.346</td>
      <td>-70.651</td>
      <td>urn:ioos:sensor:wmo:44013::watertemp1</td>
      <td>BOSTON 16 NM East of Boston, MA</td>
    </tr>
  </tbody>
</table>
</div>



We will join all the observations into an uniform series, interpolated to 1-hour interval, for the model-data comparison.

This step is necessary because the observations can be 7 or 10 minutes resolution,
while the models can be 30 to 60 minutes.

<div class="prompt input_prompt">
In&nbsp;[11]:
</div>

```python
data = ndbc + coops

index = pd.date_range(start=config['date']['start'].replace(tzinfo=None),
                      end=config['date']['stop'].replace(tzinfo=None),
                      freq='1H')

# Preserve metadata with `reindex`.
observations = []
for series in data:
    _metadata = series._metadata
    obs = series.reindex(index=index, limit=1, method='nearest')
    obs._metadata = _metadata
    observations.append(obs)
```

In this next cell we will save the data for quicker access later.

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
import iris
from ioos_tools.tardis import series2cube

attr = dict(
    featureType='timeSeries',
    Conventions='CF-1.6',
    standard_name_vocabulary='CF-1.6',
    cdm_data_type='Station',
    comment='Data from http://opendap.co-ops.nos.noaa.gov'
)


cubes = iris.cube.CubeList(
    [series2cube(obs, attr=attr) for obs in observations]
)

outfile = os.path.join(save_dir, 'OBS_DATA.nc')
iris.save(cubes, outfile)
```

Taking a quick look at the observations:

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
%matplotlib inline

ax = pd.concat(data).plot(figsize=(11, 2.25))
```


![png](data:image/png;base64,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
)


Now it is time to loop the models we found above,

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
from iris.exceptions import (CoordinateNotFoundError, ConstraintMismatchError,
                             MergeError)
from ioos_tools.ioos import get_model_name
from ioos_tools.tardis import quick_load_cubes, proc_cube, is_model, get_surface

print(fmt(' Models '))
cubes = dict()
for k, url in enumerate(dap_urls):
    print('\n[Reading url {}/{}]: {}'.format(k+1, len(dap_urls), url))
    try:
        cube = quick_load_cubes(url, config['cf_names'],
                                callback=None, strict=True)
        if is_model(cube):
            cube = proc_cube(cube,
                             bbox=config['region']['bbox'],
                             time=(config['date']['start'],
                                   config['date']['stop']),
                             units=config['units'])
        else:
            print('[Not model data]: {}'.format(url))
            continue
        cube = get_surface(cube)
        mod_name = get_model_name(url)
        cubes.update({mod_name: cube})
    except (RuntimeError, ValueError,
            ConstraintMismatchError, CoordinateNotFoundError,
            IndexError) as e:
        print('Cannot get cube for: {}\n{}'.format(url, e))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    **************************** Models ****************************
    
    [Reading url 1/11]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.met.realtime.nc
    Cannot get cube for: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.met.realtime.nc
    Cannot find ['sea_water_temperature', 'sea_surface_temperature', 'sea_water_potential_temperature', 'equivalent_potential_temperature', 'sea_water_conservative_temperature', 'pseudo_equivalent_potential_temperature'] in http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.met.realtime.nc.
    
    [Reading url 2/11]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.accelerometer.realtime.nc
    Cannot get cube for: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.accelerometer.realtime.nc
    Cannot find ['sea_water_temperature', 'sea_surface_temperature', 'sea_water_potential_temperature', 'equivalent_potential_temperature', 'sea_water_conservative_temperature', 'pseudo_equivalent_potential_temperature'] in http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.accelerometer.realtime.nc.
    
    [Reading url 3/11]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc
    
    [Reading url 4/11]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc
    
    [Reading url 5/11]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.1m.nc
    [Not model data]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.1m.nc
    
    [Reading url 6/11]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.20m.nc
    [Not model data]: http://www.neracoos.org/thredds/dodsC/UMO/Realtime/SOS/A01/DSG_A0138.sbe37.realtime.20m.nc
    
    [Reading url 7/11]: http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best
    
    [Reading url 8/11]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc
    
    [Reading url 9/11]: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global
    
    [Reading url 10/11]: http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best
    
    [Reading url 11/11]: http://oos.soest.hawaii.edu/thredds/dodsC/hioos/satellite/dhw_5km

</pre>
</div>
Next, we will match them with the nearest observed time-series. The `max_dist=0.08` is in degrees, that is roughly 8 kilometers.

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
import iris
from iris.pandas import as_series
from ioos_tools.tardis import (make_tree, get_nearest_water,
                               add_station, ensure_timeseries, remove_ssh)

for mod_name, cube in cubes.items():
    fname = '{}.nc'.format(mod_name)
    fname = os.path.join(save_dir, fname)
    print(fmt(' Downloading to file {} '.format(fname)))
    try:
        tree, lon, lat = make_tree(cube)
    except CoordinateNotFoundError as e:
        print('Cannot make KDTree for: {}'.format(mod_name))
        continue
    # Get model series at observed locations.
    raw_series = dict()
    for obs in observations:
        obs = obs._metadata
        station = obs['station_code']
        try:
            kw = dict(k=10, max_dist=0.08, min_var=0.01)
            args = cube, tree, obs['lon'], obs['lat']
            try:
                series, dist, idx = get_nearest_water(*args, **kw)
            except RuntimeError as e:
                print('Cannot download {!r}.\n{}'.format(cube, e))
                series = None
        except ValueError as e:
            status = 'No Data'
            print('[{}] {}'.format(status, obs['station_name']))
            continue
        if not series:
            status = 'Land   '
        else:
            raw_series.update({station: series})
            series = as_series(series)
            status = 'Water  '
        print('[{}] {}'.format(status, obs['station_name']))
    if raw_series:  # Save cube.
        for station, cube in raw_series.items():
            cube = add_station(cube, station)
            cube = remove_ssh(cube)
        try:
            cube = iris.cube.CubeList(raw_series.values()).merge_cube()
        except MergeError as e:
            print(e)
        ensure_timeseries(cube)
        try:
            iris.save(cube, fname)
        except AttributeError:
            # FIXME: we should patch the bad attribute instead of removing everything.
            cube.attributes = {}
            iris.save(cube, fname)
        del cube
    print('Finished processing [{}]'.format(mod_name))
```
<div class="output_area"><div class="prompt"></div>
<pre>
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/Forecasts-NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc 
    [No Data] BOSTON 16 NM East of Boston, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_BOSTON_FORECAST]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/Forecasts-NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc 
    [Water  ] BOSTON 16 NM East of Boston, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best.nc 
    [Land   ] BOSTON 16 NM East of Boston, MA
    Finished processing [roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/Forecasts-NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc 
    [No Data] BOSTON 16 NM East of Boston, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/pacioos_hycom-global.nc 
    [Water  ] BOSTON 16 NM East of Boston, MA
    Finished processing [pacioos_hycom-global]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/roms_2013_da-ESPRESSO_Real-Time_v2_History_Best.nc 
    [Land   ] BOSTON 16 NM East of Boston, MA
    Finished processing [roms_2013_da-ESPRESSO_Real-Time_v2_History_Best]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/hioos_satellite-dhw_5km.nc 
    [Water  ] BOSTON 16 NM East of Boston, MA
    Finished processing [hioos_satellite-dhw_5km]

</pre>
</div>
Now it is possible to compute some simple comparison metrics. First we'll calculate the model mean bias:

$$ \text{MB} = \mathbf{\overline{m}} - \mathbf{\overline{o}}$$

<div class="prompt input_prompt">
In&nbsp;[16]:
</div>

```python
from ioos_tools.ioos import stations_keys


def rename_cols(df, config):
    cols = stations_keys(config, key='station_name')
    return df.rename(columns=cols)
```

<div class="prompt input_prompt">
In&nbsp;[17]:
</div>

```python
from ioos_tools.ioos import load_ncs
from ioos_tools.skill_score import mean_bias, apply_skill

dfs = load_ncs(config)

df = apply_skill(dfs, mean_bias, remove_mean=False, filter_tides=False)
skill_score = dict(mean_bias=df.to_dict())

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')
```

And the root mean squared rrror of the deviations from the mean:
$$ \text{CRMS} = \sqrt{\left(\mathbf{m'} - \mathbf{o'}\right)^2}$$

where: $\mathbf{m'} = \mathbf{m} - \mathbf{\overline{m}}$ and $\mathbf{o'} = \mathbf{o} - \mathbf{\overline{o}}$

<div class="prompt input_prompt">
In&nbsp;[18]:
</div>

```python
from ioos_tools.skill_score import rmse

dfs = load_ncs(config)

df = apply_skill(dfs, rmse, remove_mean=True, filter_tides=False)
skill_score['rmse'] = df.to_dict()

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')
```

The next 2 cells make the scores "pretty" for plotting.

<div class="prompt input_prompt">
In&nbsp;[19]:
</div>

```python
import pandas as pd

# Stringfy keys.
for key in skill_score.keys():
    skill_score[key] = {str(k): v for k, v in skill_score[key].items()}

mean_bias = pd.DataFrame.from_dict(skill_score['mean_bias'])
mean_bias = mean_bias.applymap('{:.2f}'.format).replace('nan', '--')

skill_score = pd.DataFrame.from_dict(skill_score['rmse'])
skill_score = skill_score.applymap('{:.2f}'.format).replace('nan', '--')
```

<div class="prompt input_prompt">
In&nbsp;[20]:
</div>

```python
import folium
from ioos_tools.ioos import get_coordinates


def make_map(bbox, **kw):
    line = kw.pop('line', True)
    layers = kw.pop('layers', True)
    zoom_start = kw.pop('zoom_start', 5)

    lon = (bbox[0] + bbox[2]) / 2
    lat = (bbox[1] + bbox[3]) / 2
    m = folium.Map(width='100%', height='100%',
                   location=[lat, lon], zoom_start=zoom_start)

    if layers:
        url = 'http://oos.soest.hawaii.edu/thredds/wms/hioos/satellite/dhw_5km'
        w = folium.WmsTileLayer(
            url,
            name='Sea Surface Temperature',
            fmt='image/png',
            layers='CRW_SST',
            attr='PacIOOS TDS',
            overlay=True,
            transparent=True)
        w.add_to(m)

    if line:
        p = folium.PolyLine(get_coordinates(bbox),
                            color='#FF0000',
                            weight=2,
                            opacity=0.9,
                            latlon=True)
        p.add_to(m)
    return m
```

<div class="prompt input_prompt">
In&nbsp;[21]:
</div>

```python
bbox = config['region']['bbox']

m = make_map(
    bbox,
    zoom_start=11,
    line=True,
    layers=True
)
```

The cells from `[20]` to `[25]` create a [`folium`](https://github.com/python-visualization/folium) map with [`bokeh`](http://bokeh.pydata.org/en/latest/) for the time-series at the observed points.

Note that we did mark the nearest model cell location used in the comparison.

<div class="prompt input_prompt">
In&nbsp;[22]:
</div>

```python
all_obs = stations_keys(config)

from glob import glob
from operator import itemgetter

import iris
from folium.plugins import MarkerCluster

iris.FUTURE.netcdf_promote = True

big_list = []
for fname in glob(os.path.join(save_dir, '*.nc')):
    if 'OBS_DATA' in fname:
        continue
    cube = iris.load_cube(fname)
    model = os.path.split(fname)[1].split('-')[-1].split('.')[0]
    lons = cube.coord(axis='X').points
    lats = cube.coord(axis='Y').points
    stations = cube.coord('station_code').points
    models = [model]*lons.size
    lista = zip(models, lons.tolist(), lats.tolist(), stations.tolist())
    big_list.extend(lista)

big_list.sort(key=itemgetter(3))
df = pd.DataFrame(big_list, columns=['name', 'lon', 'lat', 'station'])
df.set_index('station', drop=True, inplace=True)
groups = df.groupby(df.index)


locations, popups = [], []
for station, info in groups:
    sta_name = all_obs[station]
    for lat, lon, name in zip(info.lat, info.lon, info.name):
        locations.append([lat, lon])
        popups.append('[{}]: {}'.format(name, sta_name))

MarkerCluster(locations=locations, popups=popups, name='Cluster').add_to(m)
```




    <folium.plugins.marker_cluster.MarkerCluster at 0x7fb67a37f080>



Here we use a dictionary with some models we expect to find so we can create a better legend for the plots. If any new models are found, we will use its filename in the legend as a default until we can go back and add a short name to our library.

<div class="prompt input_prompt">
In&nbsp;[23]:
</div>

```python
titles = {
    'coawst_4_use_best': 'COAWST_4',
    'global': 'HYCOM',
    'NECOFS_GOM3_FORECAST': 'NECOFS_GOM3',
    'NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST': 'NECOFS_MassBay',
    'OBS_DATA': 'Observations'
}
```

<div class="prompt input_prompt">
In&nbsp;[24]:
</div>

```python
from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.models import HoverTool
from itertools import cycle
from bokeh.palettes import Category20

from folium import IFrame

# Plot defaults.
colors = Category20[20]
colorcycler = cycle(colors)
tools = 'pan,box_zoom,reset'
width, height = 750, 250


def make_plot(df, station):
    p = figure(
        toolbar_location='above',
        x_axis_type='datetime',
        width=width,
        height=height,
        tools=tools,
        title=str(station)
    )
    for column, series in df.iteritems():
        series.dropna(inplace=True)
        if not series.empty:
            if 'OBS_DATA' not in column:
                bias = mean_bias[str(station)][column]
                skill = skill_score[str(station)][column]
                line_color = next(colorcycler)
                kw = dict(alpha=0.65, line_color=line_color)
            else:
                skill = bias = 'NA'
                kw = dict(alpha=1, color='crimson')
            line = p.line(
                x=series.index,
                y=series.values,
                legend='{}'.format(titles.get(column, column)),
                line_width=5,
                line_cap='round',
                line_join='round',
                **kw
            )
            p.add_tools(HoverTool(tooltips=[('Name', '{}'.format(titles.get(column, column))),
                                            ('Bias', bias),
                                            ('Skill', skill)],
                                  renderers=[line]))
    return p


def make_marker(p, station):
    lons = stations_keys(config, key='lon')
    lats = stations_keys(config, key='lat')

    lon, lat = lons[station], lats[station]
    html = file_html(p, CDN, station)
    iframe = IFrame(html, width=width+40, height=height+80)

    popup = folium.Popup(iframe, max_width=2650)
    icon = folium.Icon(color='green', icon='stats')
    marker = folium.Marker(location=[lat, lon],
                           popup=popup,
                           icon=icon)
    return marker
```

<div class="prompt input_prompt">
In&nbsp;[25]:
</div>

```python
dfs = load_ncs(config)

for station in dfs:
    sta_name = all_obs[station]
    df = dfs[station]
    if df.empty:
        continue
    p = make_plot(df, station)
    marker = make_marker(p, station)
    marker.add_to(m)

folium.LayerControl().add_to(m)

m
```




<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><iframe src="data:text/html;charset=utf-8;base64,PCFET0NUWVBFIGh0bWw+CjxoZWFkPiAgICAKICAgIDxtZXRhIGh0dHAtZXF1aXY9ImNvbnRlbnQtdHlwZSIgY29udGVudD0idGV4dC9odG1sOyBjaGFyc2V0PVVURi04IiAvPgogICAgPHNjcmlwdD5MX1BSRUZFUl9DQU5WQVMgPSBmYWxzZTsgTF9OT19UT1VDSCA9IGZhbHNlOyBMX0RJU0FCTEVfM0QgPSBmYWxzZTs8L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQvbnBtL2xlYWZsZXRAMS4yLjAvZGlzdC9sZWFmbGV0LmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2FqYXguZ29vZ2xlYXBpcy5jb20vYWpheC9saWJzL2pxdWVyeS8xLjExLjEvanF1ZXJ5Lm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9tYXhjZG4uYm9vdHN0cmFwY2RuLmNvbS9ib290c3RyYXAvMy4yLjAvanMvYm9vdHN0cmFwLm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvTGVhZmxldC5hd2Vzb21lLW1hcmtlcnMvMi4wLjIvbGVhZmxldC5hd2Vzb21lLW1hcmtlcnMuanMiPjwvc2NyaXB0PgogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQvbnBtL2xlYWZsZXRAMS4yLjAvZGlzdC9sZWFmbGV0LmNzcyIgLz4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9tYXhjZG4uYm9vdHN0cmFwY2RuLmNvbS9ib290c3RyYXAvMy4yLjAvY3NzL2Jvb3RzdHJhcC5taW4uY3NzIiAvPgogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL21heGNkbi5ib290c3RyYXBjZG4uY29tL2Jvb3RzdHJhcC8zLjIuMC9jc3MvYm9vdHN0cmFwLXRoZW1lLm1pbi5jc3MiIC8+CiAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Imh0dHBzOi8vbWF4Y2RuLmJvb3RzdHJhcGNkbi5jb20vZm9udC1hd2Vzb21lLzQuNi4zL2Nzcy9mb250LWF3ZXNvbWUubWluLmNzcyIgLz4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvTGVhZmxldC5hd2Vzb21lLW1hcmtlcnMvMi4wLjIvbGVhZmxldC5hd2Vzb21lLW1hcmtlcnMuY3NzIiAvPgogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL3Jhd2dpdC5jb20vcHl0aG9uLXZpc3VhbGl6YXRpb24vZm9saXVtL21hc3Rlci9mb2xpdW0vdGVtcGxhdGVzL2xlYWZsZXQuYXdlc29tZS5yb3RhdGUuY3NzIiAvPgogICAgPHN0eWxlPmh0bWwsIGJvZHkge3dpZHRoOiAxMDAlO2hlaWdodDogMTAwJTttYXJnaW46IDA7cGFkZGluZzogMDt9PC9zdHlsZT4KICAgIDxzdHlsZT4jbWFwIHtwb3NpdGlvbjphYnNvbHV0ZTt0b3A6MDtib3R0b206MDtyaWdodDowO2xlZnQ6MDt9PC9zdHlsZT4KICAgIAogICAgICAgICAgICA8c3R5bGU+ICNtYXBfZWQ4Yjk0MGMxZjM4NDU1ZGJhOGYyZmM1YjRlYWJlYTAgewogICAgICAgICAgICAgICAgcG9zaXRpb24gOiByZWxhdGl2ZTsKICAgICAgICAgICAgICAgIHdpZHRoIDogMTAwLjAlOwogICAgICAgICAgICAgICAgaGVpZ2h0OiAxMDAuMCU7CiAgICAgICAgICAgICAgICBsZWZ0OiAwLjAlOwogICAgICAgICAgICAgICAgdG9wOiAwLjAlOwogICAgICAgICAgICAgICAgfQogICAgICAgICAgICA8L3N0eWxlPgogICAgICAgIAogICAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2xlYWZsZXQubWFya2VyY2x1c3Rlci8xLjEuMC9sZWFmbGV0Lm1hcmtlcmNsdXN0ZXIuanMiPjwvc2NyaXB0PgogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9sZWFmbGV0Lm1hcmtlcmNsdXN0ZXIvMS4xLjAvTWFya2VyQ2x1c3Rlci5jc3MiIC8+CiAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2xlYWZsZXQubWFya2VyY2x1c3Rlci8xLjEuMC9NYXJrZXJDbHVzdGVyLkRlZmF1bHQuY3NzIiAvPgo8L2hlYWQ+Cjxib2R5PiAgICAKICAgIAogICAgICAgICAgICA8ZGl2IGNsYXNzPSJmb2xpdW0tbWFwIiBpZD0ibWFwX2VkOGI5NDBjMWYzODQ1NWRiYThmMmZjNWI0ZWFiZWEwIiA+PC9kaXY+CiAgICAgICAgCjwvYm9keT4KPHNjcmlwdD4gICAgCiAgICAKCiAgICAgICAgICAgIAogICAgICAgICAgICAgICAgdmFyIGJvdW5kcyA9IG51bGw7CiAgICAgICAgICAgIAoKICAgICAgICAgICAgdmFyIG1hcF9lZDhiOTQwYzFmMzg0NTVkYmE4ZjJmYzViNGVhYmVhMCA9IEwubWFwKAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ21hcF9lZDhiOTQwYzFmMzg0NTVkYmE4ZjJmYzViNGVhYmVhMCcsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7Y2VudGVyOiBbNDIuMzMsLTcwLjkzNV0sCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB6b29tOiAxMSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIG1heEJvdW5kczogYm91bmRzLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbGF5ZXJzOiBbXSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHdvcmxkQ29weUp1bXA6IGZhbHNlLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgY3JzOiBMLkNSUy5FUFNHMzg1NwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB9KTsKICAgICAgICAgICAgCiAgICAgICAgCiAgICAKICAgICAgICAgICAgdmFyIHRpbGVfbGF5ZXJfM2UyZDU3MGQxY2I4NDM4Zjg2YWMwYTg0NWRjNDg0NmEgPSBMLnRpbGVMYXllcigKICAgICAgICAgICAgICAgICdodHRwczovL3tzfS50aWxlLm9wZW5zdHJlZXRtYXAub3JnL3t6fS97eH0ve3l9LnBuZycsCiAgICAgICAgICAgICAgICB7CiAgImF0dHJpYnV0aW9uIjogbnVsbCwKICAiZGV0ZWN0UmV0aW5hIjogZmFsc2UsCiAgIm1heFpvb20iOiAxOCwKICAibWluWm9vbSI6IDEsCiAgIm5vV3JhcCI6IGZhbHNlLAogICJzdWJkb21haW5zIjogImFiYyIKfQogICAgICAgICAgICAgICAgKS5hZGRUbyhtYXBfZWQ4Yjk0MGMxZjM4NDU1ZGJhOGYyZmM1YjRlYWJlYTApOwogICAgICAgIAogICAgCiAgICAgICAgICAgIHZhciBtYWNyb19lbGVtZW50X2YyZDM4NjM5YTI0MTQwNTk5YzRmMjEyZDA0ZWZmZTY2ID0gTC50aWxlTGF5ZXIud21zKAogICAgICAgICAgICAgICAgJ2h0dHA6Ly9vb3Muc29lc3QuaGF3YWlpLmVkdS90aHJlZGRzL3dtcy9oaW9vcy9zYXRlbGxpdGUvZGh3XzVrbScsCiAgICAgICAgICAgICAgICB7CiAgImF0dHJpYnV0aW9uIjogIlBhY0lPT1MgVERTIiwKICAiY3JzIjogbnVsbCwKICAiZm9ybWF0IjogImltYWdlL3BuZyIsCiAgImxheWVycyI6ICJDUldfU1NUIiwKICAic3R5bGVzIjogIiIsCiAgInRyYW5zcGFyZW50IjogdHJ1ZSwKICAidXBwZXJjYXNlIjogZmFsc2UsCiAgInZlcnNpb24iOiAiMS4xLjEiCn0KICAgICAgICAgICAgICAgICkuYWRkVG8obWFwX2VkOGI5NDBjMWYzODQ1NWRiYThmMmZjNWI0ZWFiZWEwKTsKCiAgICAgICAgCiAgICAKICAgICAgICAgICAgICAgIHZhciBwb2x5X2xpbmVfYTFmMWIzMmQzODNhNGJiZmIzOWNmYjQzNzQ2NTgzZDcgPSBMLnBvbHlsaW5lKAogICAgICAgICAgICAgICAgICAgIFtbNDIuMDMsIC03MS4zXSwgWzQyLjAzLCAtNzAuNTddLCBbNDIuNjMsIC03MC41N10sIFs0Mi42MywgLTcxLjNdLCBbNDIuMDMsIC03MS4zXV0sCiAgICAgICAgICAgICAgICAgICAgewogICJidWJibGluZ01vdXNlRXZlbnRzIjogdHJ1ZSwKICAiY29sb3IiOiAiI0ZGMDAwMCIsCiAgImRhc2hBcnJheSI6IG51bGwsCiAgImRhc2hPZmZzZXQiOiBudWxsLAogICJmaWxsIjogZmFsc2UsCiAgImZpbGxDb2xvciI6ICIjRkYwMDAwIiwKICAiZmlsbE9wYWNpdHkiOiAwLjIsCiAgImZpbGxSdWxlIjogImV2ZW5vZGQiLAogICJsaW5lQ2FwIjogInJvdW5kIiwKICAibGluZUpvaW4iOiAicm91bmQiLAogICJub0NsaXAiOiBmYWxzZSwKICAib3BhY2l0eSI6IDAuOSwKICAic21vb3RoRmFjdG9yIjogMS4wLAogICJzdHJva2UiOiB0cnVlLAogICJ3ZWlnaHQiOiAyCn0pLmFkZFRvKG1hcF9lZDhiOTQwYzFmMzg0NTVkYmE4ZjJmYzViNGVhYmVhMCk7CiAgICAgICAgICAgIAogICAgCiAgICAgICAgICAgIHZhciBtYXJrZXJfY2x1c3Rlcl8yMzMyODg2ZGRlNGU0NTI1OTgzNTdhMDE5ZWExNjAzZSA9IEwubWFya2VyQ2x1c3Rlckdyb3VwKHsKICAgICAgICAgICAgICAgIAogICAgICAgICAgICB9KTsKICAgICAgICAgICAgbWFwX2VkOGI5NDBjMWYzODQ1NWRiYThmMmZjNWI0ZWFiZWEwLmFkZExheWVyKG1hcmtlcl9jbHVzdGVyXzIzMzI4ODZkZGU0ZTQ1MjU5ODM1N2EwMTllYTE2MDNlKTsKICAgICAgICAgICAgCiAgICAKCiAgICAgICAgICAgIHZhciBtYXJrZXJfZDI0ZTE0YWIyM2IxNDhjMzk0ODcwNzdhYjdhZTQzNzcgPSBMLm1hcmtlcigKICAgICAgICAgICAgICAgIFs0Mi4zMjUwMDQ1Nzc2MzY3NSwtNzAuNjc0OTk1NDIyMzYzMzJdLAogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIGljb246IG5ldyBMLkljb24uRGVmYXVsdCgpCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgKQogICAgICAgICAgICAgICAgLmFkZFRvKG1hcmtlcl9jbHVzdGVyXzIzMzI4ODZkZGU0ZTQ1MjU5ODM1N2EwMTllYTE2MDNlKTsKICAgICAgICAgICAgCiAgICAKICAgICAgICAgICAgdmFyIHBvcHVwX2Q3ZDNmMTIzZDgwZjRlZWI5MGE2YWQ4MzU1ZjY2ZDA4ID0gTC5wb3B1cCh7bWF4V2lkdGg6ICczMDAnfSk7CgogICAgICAgICAgICAKICAgICAgICAgICAgICAgIHZhciBodG1sXzc3MmUzNDQ3ZTFkYzQxNzE4NjgxZGU2NjZiNGE4ZDhmID0gJCgnPGRpdiBpZD0iaHRtbF83NzJlMzQ0N2UxZGM0MTcxODY4MWRlNjY2YjRhOGQ4ZiIgc3R5bGU9IndpZHRoOiAxMDAuMCU7IGhlaWdodDogMTAwLjAlOyI+W2Rod181a21dOiBCT1NUT04gMTYgTk0gRWFzdCBvZiBCb3N0b24sIE1BPC9kaXY+JylbMF07CiAgICAgICAgICAgICAgICBwb3B1cF9kN2QzZjEyM2Q4MGY0ZWViOTBhNmFkODM1NWY2NmQwOC5zZXRDb250ZW50KGh0bWxfNzcyZTM0NDdlMWRjNDE3MTg2ODFkZTY2NmI0YThkOGYpOwogICAgICAgICAgICAKCiAgICAgICAgICAgIG1hcmtlcl9kMjRlMTRhYjIzYjE0OGMzOTQ4NzA3N2FiN2FlNDM3Ny5iaW5kUG9wdXAocG9wdXBfZDdkM2YxMjNkODBmNGVlYjkwYTZhZDgzNTVmNjZkMDgpOwoKICAgICAgICAgICAgCiAgICAgICAgCiAgICAKCiAgICAgICAgICAgIHZhciBtYXJrZXJfOThmYTdiOTM2ZjI1NDA2NGI2YWEyMDZiNTEyNGYxY2UgPSBMLm1hcmtlcigKICAgICAgICAgICAgICAgIFs0Mi4zMjQ4MDAwMDAwMDAwMSwtNzAuNjM5OTY5OTk5OTk5OTldLAogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIGljb246IG5ldyBMLkljb24uRGVmYXVsdCgpCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgKQogICAgICAgICAgICAgICAgLmFkZFRvKG1hcmtlcl9jbHVzdGVyXzIzMzI4ODZkZGU0ZTQ1MjU5ODM1N2EwMTllYTE2MDNlKTsKICAgICAgICAgICAgCiAgICAKICAgICAgICAgICAgdmFyIHBvcHVwXzJhOGE2OGM1NGE1MDQxN2ZiNThlNDFkM2VmNzE2MzA0ID0gTC5wb3B1cCh7bWF4V2lkdGg6ICczMDAnfSk7CgogICAgICAgICAgICAKICAgICAgICAgICAgICAgIHZhciBodG1sXzg5OTMwMDBmODk2NDQ5ODRhNDdmMDEwYjI0ZmZkMmRkID0gJCgnPGRpdiBpZD0iaHRtbF84OTkzMDAwZjg5NjQ0OTg0YTQ3ZjAxMGIyNGZmZDJkZCIgc3R5bGU9IndpZHRoOiAxMDAuMCU7IGhlaWdodDogMTAwLjAlOyI+W2dsb2JhbF06IEJPU1RPTiAxNiBOTSBFYXN0IG9mIEJvc3RvbiwgTUE8L2Rpdj4nKVswXTsKICAgICAgICAgICAgICAgIHBvcHVwXzJhOGE2OGM1NGE1MDQxN2ZiNThlNDFkM2VmNzE2MzA0LnNldENvbnRlbnQoaHRtbF84OTkzMDAwZjg5NjQ0OTg0YTQ3ZjAxMGIyNGZmZDJkZCk7CiAgICAgICAgICAgIAoKICAgICAgICAgICAgbWFya2VyXzk4ZmE3YjkzNmYyNTQwNjRiNmFhMjA2YjUxMjRmMWNlLmJpbmRQb3B1cChwb3B1cF8yYThhNjhjNTRhNTA0MTdmYjU4ZTQxZDNlZjcxNjMwNCk7CgogICAgICAgICAgICAKICAgICAgICAKICAgIAoKICAgICAgICAgICAgdmFyIG1hcmtlcl80Nzc4MTljNjRlZDU0YWMwODU3MmY3OGM3ZWM0ZmM2MyA9IEwubWFya2VyKAogICAgICAgICAgICAgICAgWzQyLjM0MTMyNzY2NzIzNjMzLC03MC42NDgzMTU0Mjk2ODc1XSwKICAgICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICAgICBpY29uOiBuZXcgTC5JY29uLkRlZmF1bHQoKQogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICkKICAgICAgICAgICAgICAgIC5hZGRUbyhtYXJrZXJfY2x1c3Rlcl8yMzMyODg2ZGRlNGU0NTI1OTgzNTdhMDE5ZWExNjAzZSk7CiAgICAgICAgICAgIAogICAgCiAgICAgICAgICAgIHZhciBwb3B1cF84ZWEyNmFkMmIzZDA0YmEyYmI4YWI4ODI0OGU1MDlhMSA9IEwucG9wdXAoe21heFdpZHRoOiAnMzAwJ30pOwoKICAgICAgICAgICAgCiAgICAgICAgICAgICAgICB2YXIgaHRtbF82YzQ1YjZkYWNiNGU0MTFmODgzMDFhZDA3MTg4NTc0OCA9ICQoJzxkaXYgaWQ9Imh0bWxfNmM0NWI2ZGFjYjRlNDExZjg4MzAxYWQwNzE4ODU3NDgiIHN0eWxlPSJ3aWR0aDogMTAwLjAlOyBoZWlnaHQ6IDEwMC4wJTsiPltORUNPRlNfRlZDT01fT0NFQU5fTUFTU0JBWV9GT1JFQ0FTVF06IEJPU1RPTiAxNiBOTSBFYXN0IG9mIEJvc3RvbiwgTUE8L2Rpdj4nKVswXTsKICAgICAgICAgICAgICAgIHBvcHVwXzhlYTI2YWQyYjNkMDRiYTJiYjhhYjg4MjQ4ZTUwOWExLnNldENvbnRlbnQoaHRtbF82YzQ1YjZkYWNiNGU0MTFmODgzMDFhZDA3MTg4NTc0OCk7CiAgICAgICAgICAgIAoKICAgICAgICAgICAgbWFya2VyXzQ3NzgxOWM2NGVkNTRhYzA4NTcyZjc4YzdlYzRmYzYzLmJpbmRQb3B1cChwb3B1cF84ZWEyNmFkMmIzZDA0YmEyYmI4YWI4ODI0OGU1MDlhMSk7CgogICAgICAgICAgICAKICAgICAgICAKICAgIAoKICAgICAgICAgICAgdmFyIG1hcmtlcl9mNjZjNWJkNTRmNzM0MTg3YjdiM2RlYWFmNDY3MjQ5MiA9IEwubWFya2VyKAogICAgICAgICAgICAgICAgWzQyLjM0NjAwMDAwMDAwMDAwNCwtNzAuNjUxMDAwMDAwMDAwMDFdLAogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIGljb246IG5ldyBMLkljb24uRGVmYXVsdCgpCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgKQogICAgICAgICAgICAgICAgLmFkZFRvKG1hcF9lZDhiOTQwYzFmMzg0NTVkYmE4ZjJmYzViNGVhYmVhMCk7CiAgICAgICAgICAgIAogICAgCgogICAgICAgICAgICAgICAgdmFyIGljb25fMDEwZDBjYzQ5MmVmNDczNGJkNjZmMDBiYzk0MmNlYjkgPSBMLkF3ZXNvbWVNYXJrZXJzLmljb24oewogICAgICAgICAgICAgICAgICAgIGljb246ICdzdGF0cycsCiAgICAgICAgICAgICAgICAgICAgaWNvbkNvbG9yOiAnd2hpdGUnLAogICAgICAgICAgICAgICAgICAgIG1hcmtlckNvbG9yOiAnZ3JlZW4nLAogICAgICAgICAgICAgICAgICAgIHByZWZpeDogJ2dseXBoaWNvbicsCiAgICAgICAgICAgICAgICAgICAgZXh0cmFDbGFzc2VzOiAnZmEtcm90YXRlLTAnCiAgICAgICAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgICAgICBtYXJrZXJfZjY2YzViZDU0ZjczNDE4N2I3YjNkZWFhZjQ2NzI0OTIuc2V0SWNvbihpY29uXzAxMGQwY2M0OTJlZjQ3MzRiZDY2ZjAwYmM5NDJjZWI5KTsKICAgICAgICAgICAgCiAgICAKICAgICAgICAgICAgdmFyIHBvcHVwXzNhZDU0MzdiMWNjZDQyZjY5NjFmOThlNWQxMDIzMTUzID0gTC5wb3B1cCh7bWF4V2lkdGg6ICcyNjUwJ30pOwoKICAgICAgICAgICAgCiAgICAgICAgICAgICAgICB2YXIgaV9mcmFtZV9kYjEwMjRmZDk4ODg0MzFjYWQxZTU3NmZlZWMyMTgzMyA9ICQoJzxpZnJhbWUgc3JjPSJkYXRhOnRleHQvaHRtbDtjaGFyc2V0PXV0Zi04O2Jhc2U2NCxDaUFnSUNBS1BDRkVUME5VV1ZCRklHaDBiV3crQ2p4b2RHMXNJR3hoYm1jOUltVnVJajRLSUNBZ0lEeG9aV0ZrUGdvZ0lDQWdJQ0FnSUR4dFpYUmhJR05vWVhKelpYUTlJblYwWmkwNElqNEtJQ0FnSUNBZ0lDQThkR2wwYkdVK05EUXdNVE04TDNScGRHeGxQZ29nSUNBZ0lDQWdJQW84YkdsdWF5QnlaV3c5SW5OMGVXeGxjMmhsWlhRaUlHaHlaV1k5SW1oMGRIQnpPaTh2WTJSdUxuQjVaR0YwWVM1dmNtY3ZZbTlyWldndmNtVnNaV0Z6WlM5aWIydGxhQzB3TGpFeUxqRXpMbTFwYmk1amMzTWlJSFI1Y0dVOUluUmxlSFF2WTNOeklpQXZQZ29nSUNBZ0lDQWdJQW84YzJOeWFYQjBJSFI1Y0dVOUluUmxlSFF2YW1GMllYTmpjbWx3ZENJZ2MzSmpQU0pvZEhSd2N6b3ZMMk5rYmk1d2VXUmhkR0V1YjNKbkwySnZhMlZvTDNKbGJHVmhjMlV2WW05clpXZ3RNQzR4TWk0eE15NXRhVzR1YW5NaVBqd3ZjMk55YVhCMFBnbzhjMk55YVhCMElIUjVjR1U5SW5SbGVIUXZhbUYyWVhOamNtbHdkQ0krQ2lBZ0lDQkNiMnRsYUM1elpYUmZiRzluWDJ4bGRtVnNLQ0pwYm1adklpazdDand2YzJOeWFYQjBQZ29nSUNBZ0lDQWdJRHh6ZEhsc1pUNEtJQ0FnSUNBZ0lDQWdJR2gwYld3Z2V3b2dJQ0FnSUNBZ0lDQWdJQ0IzYVdSMGFEb2dNVEF3SlRzS0lDQWdJQ0FnSUNBZ0lDQWdhR1ZwWjJoME9pQXhNREFsT3dvZ0lDQWdJQ0FnSUNBZ2ZRb2dJQ0FnSUNBZ0lDQWdZbTlrZVNCN0NpQWdJQ0FnSUNBZ0lDQWdJSGRwWkhSb09pQTVNQ1U3Q2lBZ0lDQWdJQ0FnSUNBZ0lHaGxhV2RvZERvZ01UQXdKVHNLSUNBZ0lDQWdJQ0FnSUNBZ2JXRnlaMmx1T2lCaGRYUnZPd29nSUNBZ0lDQWdJQ0FnZlFvZ0lDQWdJQ0FnSUR3dmMzUjViR1UrQ2lBZ0lDQThMMmhsWVdRK0NpQWdJQ0E4WW05a2VUNEtJQ0FnSUNBZ0lDQUtJQ0FnSUNBZ0lDQThaR2wySUdOc1lYTnpQU0ppYXkxeWIyOTBJajRLSUNBZ0lDQWdJQ0FnSUNBZ1BHUnBkaUJqYkdGemN6MGlZbXN0Y0d4dmRHUnBkaUlnYVdROUltUTFZVGRpTURaaExUSTNaR1F0TkRaaVppMDVOelV3TFdSbE1HWTNNMlUwT1dJNU5pSStQQzlrYVhZK0NpQWdJQ0FnSUNBZ1BDOWthWFkrQ2lBZ0lDQWdJQ0FnQ2lBZ0lDQWdJQ0FnUEhOamNtbHdkQ0IwZVhCbFBTSmhjSEJzYVdOaGRHbHZiaTlxYzI5dUlpQnBaRDBpWkRjME1tRmtPRFl0TTJVeU1TMDBOMlJrTFdKaFl6a3RNVEEyWkRVelpqVXpZV1E0SWo0S0lDQWdJQ0FnSUNBZ0lIc2lObUkxWkdGallqY3ROR1V4WmkwMFlXVTFMV0ZtWTJRdFpEWTRaVFkyWmpabE1tUmxJanA3SW5KdmIzUnpJanA3SW5KbFptVnlaVzVqWlhNaU9sdDdJbUYwZEhKcFluVjBaWE1pT25zaWJXOXVkR2h6SWpwYk1DdzBMRGhkZlN3aWFXUWlPaUk0TmpNMllUSTBaUzFtTjJSakxUUmpObUl0T1Raak1TMDJPVEk1TlRNMk9ERmlNbUlpTENKMGVYQmxJam9pVFc5dWRHaHpWR2xqYTJWeUluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltUmhlWE1pT2xzeExEUXNOeXd4TUN3eE15d3hOaXd4T1N3eU1pd3lOU3d5T0YxOUxDSnBaQ0k2SWpsaU56Y3lPR1V4TFdSaVlUY3ROR05oTXkxaE56QmlMV0l5TVdVeFkyWXpORGRqTnlJc0luUjVjR1VpT2lKRVlYbHpWR2xqYTJWeUluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN2ZTd2lhV1FpT2lKaE4yWTFOVFJoTXkwd1lqZGlMVFJtTUdNdFlXVXlNeTAxTURNMFpUa3paRGN5TlRBaUxDSjBlWEJsSWpvaVJHRjBaWFJwYldWVWFXTnJSbTl5YldGMGRHVnlJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbVJoZEdGZmMyOTFjbU5sSWpwN0ltbGtJam9pT1RCbE1HTXdPREV0WmpRM05TMDBOVFF5TFRoa05tTXRPV1ptTXpFeE56azBNR1V5SWl3aWRIbHdaU0k2SWtOdmJIVnRia1JoZEdGVGIzVnlZMlVpZlN3aVoyeDVjR2dpT25zaWFXUWlPaUpsWlRRelpUZ3lPUzFsTUdFeExUUXlOekl0T1RVMllpMWxNVE0wWlRNM09URTBaV1lpTENKMGVYQmxJam9pVEdsdVpTSjlMQ0pvYjNabGNsOW5iSGx3YUNJNmJuVnNiQ3dpYlhWMFpXUmZaMng1Y0dnaU9tNTFiR3dzSW01dmJuTmxiR1ZqZEdsdmJsOW5iSGx3YUNJNmV5SnBaQ0k2SWpsa09UTTJOR1EyTFRCbU5ERXROR0V4TnkxaFlUaGtMVEV4Tm1GbU9EZGpPVFJsWVNJc0luUjVjR1VpT2lKTWFXNWxJbjBzSW5ObGJHVmpkR2x2Ymw5bmJIbHdhQ0k2Ym5Wc2JDd2lkbWxsZHlJNmV5SnBaQ0k2SWpoaE56aGlPVFkyTFdFek5ERXRORGt5TmkwNU5ESTVMV1pqTmpjd01HRTFNRGN3TWlJc0luUjVjR1VpT2lKRFJGTldhV1YzSW4xOUxDSnBaQ0k2SW1Ga1pXUXlOakpqTFdGaVl6QXROREV6WXkwNVpXRmtMV000WVdJeE56STVOR1ptTmlJc0luUjVjR1VpT2lKSGJIbHdhRkpsYm1SbGNtVnlJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbXhwYm1WZllXeHdhR0VpT2pBdU1Td2liR2x1WlY5allYQWlPaUp5YjNWdVpDSXNJbXhwYm1WZlkyOXNiM0lpT2lJak1XWTNOMkkwSWl3aWJHbHVaVjlxYjJsdUlqb2ljbTkxYm1RaUxDSnNhVzVsWDNkcFpIUm9Jam8xTENKNElqcDdJbVpwWld4a0lqb2llQ0o5TENKNUlqcDdJbVpwWld4a0lqb2llU0o5ZlN3aWFXUWlPaUk1WkRrek5qUmtOaTB3WmpReExUUmhNVGN0WVdFNFpDMHhNVFpoWmpnM1l6azBaV0VpTENKMGVYQmxJam9pVEdsdVpTSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SmpZV3hzWW1GamF5STZiblZzYkN3aVkyOXNkVzF1WDI1aGJXVnpJanBiSW5naUxDSjVJbDBzSW1SaGRHRWlPbnNpZUNJNmV5SmZYMjVrWVhKeVlYbGZYeUk2SWtGQlJHZEtkRmxpWkd0SlFVRk5hVll5VW5ReVVXZEJRWE5CVkdSSE0xcERRVUZEWjJwRFoyTmthMGxCUVVscU4wdDRlREpSWjBGQlkwZHZka2hJV2tOQlFVSm5PRzV2WTJSclNVRkJSV2hvWm1oNE1sRm5RVUZOVGtOQ1NFaGFRMEZCUVdkWFRUQmpaR3RKUVVGQmFrZ3dRbmd5VVdkQlFUaEVXRlZJU0ZwRElpd2laSFI1Y0dVaU9pSm1iRzloZERZMElpd2ljMmhoY0dVaU9sc3hNbDE5TENKNUlqcDdJbDlmYm1SaGNuSmhlVjlmSWpvaVFVRkJRV2RHVTFaRlZVRkJRVUZDUVdJMVVWSlJRVUZCUVVGRFMydDRSa0ZCUVVGQmQwNVdMMFZWUVVGQlFVUkJlRmh2VWxGQlFVRkJTME14WkZKR1FVRkJRVUZuUmxGSFJWVkJRVUZCUTJkU1FWVlNVVUZCUVVGTlFUQkNRa1pCUVVGQlFVbE9abk5GUlVGQlFVRkJaekVyZDFGUlFVRkJRVU5FV0RkQ1FrRWlMQ0prZEhsd1pTSTZJbVpzYjJGME5qUWlMQ0p6YUdGd1pTSTZXekV5WFgxOWZTd2lhV1FpT2lJNU1HVXdZekE0TVMxbU5EYzFMVFExTkRJdE9HUTJZeTA1Wm1Zek1URTNPVFF3WlRJaUxDSjBlWEJsSWpvaVEyOXNkVzF1UkdGMFlWTnZkWEpqWlNKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKc1lXSmxiQ0k2ZXlKMllXeDFaU0k2SWs1RlEwOUdVMTlOWVhOelFtRjVJbjBzSW5KbGJtUmxjbVZ5Y3lJNlczc2lhV1FpT2lKbU9EWTRZbVU1TUMweFpHVXhMVFJtTkRVdFltTmtPUzB5TkRrME9EVXlObVl4T0dVaUxDSjBlWEJsSWpvaVIyeDVjR2hTWlc1a1pYSmxjaUo5WFgwc0ltbGtJam9pTXpObU1XVTVaREF0WldJM05DMDBNV1U1TFRreU56QXRaRFE0TlRFMk5tUXdNamRoSWl3aWRIbHdaU0k2SWt4bFoyVnVaRWwwWlcwaWZTeDdJbUYwZEhKcFluVjBaWE1pT25zaVkyRnNiR0poWTJzaU9tNTFiR3g5TENKcFpDSTZJakk0Tm1VM1pUUXlMV0UzTkdVdE5EYzVNUzA1WmpkakxXWXdZVFJqTVdZM1lUTXpOU0lzSW5SNWNHVWlPaUpFWVhSaFVtRnVaMlV4WkNKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKc1lXSmxiQ0k2ZXlKMllXeDFaU0k2SWs5aWMyVnlkbUYwYVc5dWN5SjlMQ0p5Wlc1a1pYSmxjbk1pT2x0N0ltbGtJam9pWVdNeU1UVTNNVGt0Tm1VeE1pMDBPVGhpTFRnd01UZ3RZV1U0WkRsbU9HWTNaRGswSWl3aWRIbHdaU0k2SWtkc2VYQm9VbVZ1WkdWeVpYSWlmVjE5TENKcFpDSTZJakUwTm1VeFpqUTBMV05tTVdJdE5ESXlNQzFpTURWakxUVTBORE5oWkRObFpUZzNOQ0lzSW5SNWNHVWlPaUpNWldkbGJtUkpkR1Z0SW4wc2V5SmhkSFJ5YVdKMWRHVnpJanA3SW1GamRHbDJaVjlrY21Gbklqb2lZWFYwYnlJc0ltRmpkR2wyWlY5cGJuTndaV04wSWpvaVlYVjBieUlzSW1GamRHbDJaVjl6WTNKdmJHd2lPaUpoZFhSdklpd2lZV04wYVhabFgzUmhjQ0k2SW1GMWRHOGlMQ0owYjI5c2N5STZXM3NpYVdRaU9pSXpNR1prWmpoaU5DMDVZVFUyTFRSa05XVXRPREJoTkMwNU5UaG1OelkzTkdFellXWWlMQ0owZVhCbElqb2lVR0Z1Vkc5dmJDSjlMSHNpYVdRaU9pSTRNV1EyTWpFMVpDMHpORFl3TFRSak5UQXRPV0k1WVMweE0yTTFPR1pqTTJFeFlXRWlMQ0owZVhCbElqb2lRbTk0V205dmJWUnZiMndpZlN4N0ltbGtJam9pT1dOalptVXdZV0V0TjJJeVppMDBOMlE1TFRobFpHSXROV1V6WmpNMk9EZzBZV1V5SWl3aWRIbHdaU0k2SWxKbGMyVjBWRzl2YkNKOUxIc2lhV1FpT2lKalpEbGpNekkzTlMxaU5UZ3dMVFE0TkRJdFlqTTNNeTB4T0RnNE9EQXhZMk5pWVRZaUxDSjBlWEJsSWpvaVNHOTJaWEpVYjI5c0luMHNleUpwWkNJNklqSTVPRFF4WTJabExXVmpOVEl0TkRZellTMDRPR1UzTFRVNFpXRTFZV0V4WkdFek1TSXNJblI1Y0dVaU9pSkliM1psY2xSdmIyd2lmU3g3SW1sa0lqb2lNVE01TURVelptVXRZbVJsWWkwME56Z3hMV0U1WWpJdE1XSTFabVppTW1abU1tUmlJaXdpZEhsd1pTSTZJa2h2ZG1WeVZHOXZiQ0o5TEhzaWFXUWlPaUpoTm1KaU9UWXdNeTAxTVRFNExUUmhNMkV0WW1KaU55MDVaR1V5WWpoaU56WmpNRFFpTENKMGVYQmxJam9pU0c5MlpYSlViMjlzSW4xZGZTd2lhV1FpT2lJMFpURmlabVkzTkMwek5ERXhMVFExWTJJdFlqSTRPQzAzWW1Zek5qRTVPR0prWkdNaUxDSjBlWEJsSWpvaVZHOXZiR0poY2lKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKdGIyNTBhSE1pT2xzd0xERXNNaXd6TERRc05TdzJMRGNzT0N3NUxERXdMREV4WFgwc0ltbGtJam9pWkRaaE5qQXlNVGN0Tm1Jek15MDBNR1l4TFdFMk5URXRNMkV4T1RrMk16ZGhNRFkxSWl3aWRIbHdaU0k2SWsxdmJuUm9jMVJwWTJ0bGNpSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SnRZVzUwYVhOellYTWlPbHN4TERJc05WMHNJbTFoZUY5cGJuUmxjblpoYkNJNk5UQXdMakFzSW01MWJWOXRhVzV2Y2w5MGFXTnJjeUk2TUgwc0ltbGtJam9pTURnNU1qbG1NR1l0TXpWa1l5MDBZekl4TFdFellXUXRaV0l4WXpWaVpESXdNek01SWl3aWRIbHdaU0k2SWtGa1lYQjBhWFpsVkdsamEyVnlJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbk52ZFhKalpTSTZleUpwWkNJNkltUm1ZV0pqTkRrM0xUUTRZekF0TkRKak1TMWlOelZsTFdZNU5qRm1aR1ExTm1Rd09DSXNJblI1Y0dVaU9pSkRiMngxYlc1RVlYUmhVMjkxY21ObEluMTlMQ0pwWkNJNkltUmlZV1ppWVRnNUxUVTRNVGt0TkdWa05TMDVZelZqTFRVM05tRmlNMkV3WW1Ga1pDSXNJblI1Y0dVaU9pSkRSRk5XYVdWM0luMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltUmhkR0ZmYzI5MWNtTmxJanA3SW1sa0lqb2labUl3TURRNU5EZ3RZVFEwWXkwMFptRTNMVGt5Tm1RdE5UWTRNekE1WTJKak9EWmpJaXdpZEhsd1pTSTZJa052YkhWdGJrUmhkR0ZUYjNWeVkyVWlmU3dpWjJ4NWNHZ2lPbnNpYVdRaU9pSTFaamsxWVdabFpDMWtOV0kzTFRRM056QXRZbVEzWXkweU4ySXhPV0V6WlRjME56Z2lMQ0owZVhCbElqb2lUR2x1WlNKOUxDSm9iM1psY2w5bmJIbHdhQ0k2Ym5Wc2JDd2liWFYwWldSZloyeDVjR2dpT201MWJHd3NJbTV2Ym5ObGJHVmpkR2x2Ymw5bmJIbHdhQ0k2ZXlKcFpDSTZJamxqT0RNeVltRTJMVGsxTXpNdE5EYzJaQzA1TldObExXSTNZVEk0WTJRNE5HUm1OeUlzSW5SNWNHVWlPaUpNYVc1bEluMHNJbk5sYkdWamRHbHZibDluYkhsd2FDSTZiblZzYkN3aWRtbGxkeUk2ZXlKcFpDSTZJak13WXpFNE9HUTBMVE5qTWpndE5EazROeTFoTURnM0xXTTNZVEpsTURRM05EWTRaaUlzSW5SNWNHVWlPaUpEUkZOV2FXVjNJbjE5TENKcFpDSTZJbUZqTWpFMU56RTVMVFpsTVRJdE5EazRZaTA0TURFNExXRmxPR1E1WmpobU4yUTVOQ0lzSW5SNWNHVWlPaUpIYkhsd2FGSmxibVJsY21WeUluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltSmhjMlVpT2pZd0xDSnRZVzUwYVhOellYTWlPbHN4TERJc05Td3hNQ3d4TlN3eU1Dd3pNRjBzSW0xaGVGOXBiblJsY25aaGJDSTZNVGd3TURBd01DNHdMQ0p0YVc1ZmFXNTBaWEoyWVd3aU9qRXdNREF1TUN3aWJuVnRYMjFwYm05eVgzUnBZMnR6SWpvd2ZTd2lhV1FpT2lJNU1EWXpZMkUxWmkwNFlUZ3hMVFF3TkdVdFlXWXhOQzB3T1RjMFlqTXpaR00xTmpJaUxDSjBlWEJsSWpvaVFXUmhjSFJwZG1WVWFXTnJaWElpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpY0d4dmRDSTZiblZzYkN3aWRHVjRkQ0k2SWpRME1ERXpJbjBzSW1sa0lqb2lNekUyWkRWaE56a3Raak0zWlMwMFpESmpMVGd3T1RjdE1HTXhPR1E0TW1SaVpqWTJJaXdpZEhsd1pTSTZJbFJwZEd4bEluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltUmhlWE1pT2xzeExESXNNeXcwTERVc05pdzNMRGdzT1N3eE1Dd3hNU3d4TWl3eE15d3hOQ3d4TlN3eE5pd3hOeXd4T0N3eE9Td3lNQ3d5TVN3eU1pd3lNeXd5TkN3eU5Td3lOaXd5Tnl3eU9Dd3lPU3d6TUN3ek1WMTlMQ0pwWkNJNklqRmtOelF6T0dSakxUVTFOR1V0TkRoaVppMWhaakppTFdJd1pqTTJNall5TnpjeU55SXNJblI1Y0dVaU9pSkVZWGx6VkdsamEyVnlJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbXhwYm1WZllXeHdhR0VpT2pBdU1Td2liR2x1WlY5allYQWlPaUp5YjNWdVpDSXNJbXhwYm1WZlkyOXNiM0lpT2lJak1XWTNOMkkwSWl3aWJHbHVaVjlxYjJsdUlqb2ljbTkxYm1RaUxDSnNhVzVsWDNkcFpIUm9Jam8xTENKNElqcDdJbVpwWld4a0lqb2llQ0o5TENKNUlqcDdJbVpwWld4a0lqb2llU0o5ZlN3aWFXUWlPaUkxWVRZd05qY3pOeTFpTXpVNUxUUTRNakl0WWpObU5pMHlaR1kyTkdGaVlqSXlNRE1pTENKMGVYQmxJam9pVEdsdVpTSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5Sm1iM0p0WVhSMFpYSWlPbnNpYVdRaU9pSXdOV0kwTnpabE5DMDFPV05qTFRRMU9URXRPVEZtWXkxbU1XWmxaVEF4TUdSaFpUVWlMQ0owZVhCbElqb2lRbUZ6YVdOVWFXTnJSbTl5YldGMGRHVnlJbjBzSW5Cc2IzUWlPbnNpYVdRaU9pSXdZV1poTmpJellpMHlPV015TFRRek5tRXRPR1JsTXkxbE5EazVPR0kwT1RGaE1UUWlMQ0p6ZFdKMGVYQmxJam9pUm1sbmRYSmxJaXdpZEhsd1pTSTZJbEJzYjNRaWZTd2lkR2xqYTJWeUlqcDdJbWxrSWpvaVkyRTNZMkkyWlRJdFltTTRNaTAwTTJaakxUZzJNall0TXpRMU5tTXhOemhqWVRCbUlpd2lkSGx3WlNJNklrSmhjMmxqVkdsamEyVnlJbjE5TENKcFpDSTZJbVk1WXpZME5EQTVMV1prWm1VdE5HWTRZeTA0WTJKa0xUQTBObUU0TVRNM01ETTFZU0lzSW5SNWNHVWlPaUpNYVc1bFlYSkJlR2x6SW4wc2V5SmhkSFJ5YVdKMWRHVnpJanA3SW0xdmJuUm9jeUk2V3pBc05sMTlMQ0pwWkNJNkltRXhZMkZoT1RjMUxXWTVZekV0TkRRMVlpMDRaVGxoTFdWaVpUSTBNemt3WVRaaFpTSXNJblI1Y0dVaU9pSk5iMjUwYUhOVWFXTnJaWElpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnQ5TENKcFpDSTZJbUV3WWpJeFpXUTBMV1k0TW1RdE5EWTVNaTFpTURNNExXTTNOekl6T0dNeU1XWTRZaUlzSW5SNWNHVWlPaUpaWldGeWMxUnBZMnRsY2lKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKallXeHNZbUZqYXlJNmJuVnNiQ3dpY21WdVpHVnlaWEp6SWpwYmV5SnBaQ0k2SW1Gak1qRTFOekU1TFRabE1USXRORGs0WWkwNE1ERTRMV0ZsT0dRNVpqaG1OMlE1TkNJc0luUjVjR1VpT2lKSGJIbHdhRkpsYm1SbGNtVnlJbjFkTENKMGIyOXNkR2x3Y3lJNlcxc2lUbUZ0WlNJc0lrOWljMlZ5ZG1GMGFXOXVjeUpkTEZzaVFtbGhjeUlzSWs1QklsMHNXeUpUYTJsc2JDSXNJazVCSWwxZGZTd2lhV1FpT2lJeU9UZzBNV05tWlMxbFl6VXlMVFEyTTJFdE9EaGxOeTAxT0dWaE5XRmhNV1JoTXpFaUxDSjBlWEJsSWpvaVNHOTJaWEpVYjI5c0luMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltUmhlWE1pT2xzeExEZ3NNVFVzTWpKZGZTd2lhV1FpT2lJd1lqQm1ZalUzWVMwMk5qazVMVFF5WVRVdFlUTm1aUzA0Tnpjd1ptWXlOekEzTW1FaUxDSjBlWEJsSWpvaVJHRjVjMVJwWTJ0bGNpSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SmpZV3hzWW1GamF5STZiblZzYkgwc0ltbGtJam9pTjJFMU56UTNZek10TXpCbVlTMDBPVFEwTFdGbE9HWXROekkyWWpWaFlqVTBNelJtSWl3aWRIbHdaU0k2SWtSaGRHRlNZVzVuWlRGa0luMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltTmhiR3hpWVdOcklqcHVkV3hzTENKeVpXNWtaWEpsY25NaU9sdDdJbWxrSWpvaVlXUmxaREkyTW1NdFlXSmpNQzAwTVROakxUbGxZV1F0WXpoaFlqRTNNamswWm1ZMklpd2lkSGx3WlNJNklrZHNlWEJvVW1WdVpHVnlaWElpZlYwc0luUnZiMngwYVhCeklqcGJXeUpPWVcxbElpd2laR2gzWHpWcmJTSmRMRnNpUW1saGN5SXNJaTB3TGpFeElsMHNXeUpUYTJsc2JDSXNJakF1TVRNaVhWMTlMQ0pwWkNJNklqRXpPVEExTTJabExXSmtaV0l0TkRjNE1TMWhPV0l5TFRGaU5XWm1ZakptWmpKa1lpSXNJblI1Y0dVaU9pSkliM1psY2xSdmIyd2lmU3g3SW1GMGRISnBZblYwWlhNaU9uc2liR2x1WlY5aGJIQm9ZU0k2TUM0Mk5Td2liR2x1WlY5allYQWlPaUp5YjNWdVpDSXNJbXhwYm1WZlkyOXNiM0lpT2lJalptWTNaakJsSWl3aWJHbHVaVjlxYjJsdUlqb2ljbTkxYm1RaUxDSnNhVzVsWDNkcFpIUm9Jam8xTENKNElqcDdJbVpwWld4a0lqb2llQ0o5TENKNUlqcDdJbVpwWld4a0lqb2llU0o5ZlN3aWFXUWlPaUpsT1RCak1XSXlNUzAwWTJFeUxUUTFOR1l0WW1ZMU9TMWxORFppTkdRek1EZzJZbUVpTENKMGVYQmxJam9pVEdsdVpTSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SndiRzkwSWpwN0ltbGtJam9pTUdGbVlUWXlNMkl0TWpsak1pMDBNelpoTFRoa1pUTXRaVFE1T1RoaU5Ea3hZVEUwSWl3aWMzVmlkSGx3WlNJNklrWnBaM1Z5WlNJc0luUjVjR1VpT2lKUWJHOTBJbjBzSW5ScFkydGxjaUk2ZXlKcFpDSTZJakJoTmpFME5XVmxMVFU0TnpFdE5HUTVNQzA0WkRjM0xURmhNVGM0WWpNMU1URmtaaUlzSW5SNWNHVWlPaUpFWVhSbGRHbHRaVlJwWTJ0bGNpSjlmU3dpYVdRaU9pSm1OemRpWVdRM09TMDBaR0kwTFRRM09ERXRPVFZqT1MwMVpEVXhZbVl5WXpNMU5UUWlMQ0owZVhCbElqb2lSM0pwWkNKOUxIc2lZWFIwY21saWRYUmxjeUk2ZTMwc0ltbGtJam9pWmpoaE1qVmlPRE10T0dNME5TMDBZVEEzTFdJeU1EY3RZalk1Tm1aa09XWmxOREZtSWl3aWRIbHdaU0k2SWt4cGJtVmhjbE5qWVd4bEluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0ltTmhiR3hpWVdOcklqcHVkV3hzTENKamIyeDFiVzVmYm1GdFpYTWlPbHNpZUNJc0lua2lYU3dpWkdGMFlTSTZleUo0SWpwN0lsOWZibVJoY25KaGVWOWZJam9pUVVGRFFYWXhSV05rYTBsQlFVZG5kVlpTZURKUlowRkJWVW94V1VoSVdrTkJRVUUwUkVaM1kyUnJTVUZCUTBJM1dIaDRNbEZuUVVGRFQzQnBTRWhhUTBGQlJIZFhSMWxqWkd0SlFVRk9ha2hoVW5neVVXZEJRWGRFV25SSVNGcERRVUZEYjNCWVFXTmthMGxCUVVwQlZXUkNlREpSWjBGQlpVbE9NMGhJV2tOQlFVSm5PRzV2WTJSclNVRkJSV2hvWm1oNE1sRm5RVUZOVGtOQ1NFaGFRMEZCUVZsUU5GVmpaR3RKUVVGQlEzVnBRbmd5VVdkQlFUWkNlVTFJU0ZwRFFVRkVVV2swT0dOa2EwbEJRVXhxTm10b2VESlJaMEZCYjBkdFYwaElXa05CUVVOSk1rcHJZMlJyU1VGQlNFSklibEo0TWxGblFVRlhUR0ZuU0VoYVEwRkJRa0ZLWVZGalpHdEpRVUZEYVZWd2VIZ3lVV2RCUVVWQlQzSklTRnBEUVVGRU5HTmhOR05rYTBsQlFVOUVaM05TZURKUlowRkJlVVVyTVVoSVdrTkJRVU4zZG5KblkyUnJTVUZCU21kMGRrSjRNbEZuUVVGblNua3ZTRWhhUTBGQlFtOURPRTFqWkd0SlFVRkdRalo0YUhneVVXZEJRVTlQYmtwSVNGcERRVUZCWjFkTk1HTmthMGxCUVVGcVNEQkNlREpSWjBGQk9FUllWVWhJV2tOQlFVUlpjRTVqWTJSclNVRkJUVUZVTW5oNE1sRm5RVUZ4U1V4bFNFaGFRMEZCUTFFNFpVVmpaR3RKUVVGSWFHYzFVbmd5VVdkQlFWbE5MMjlJU0ZwRFFVRkNTVkIxZDJOa2EwbEJRVVJEZERkNGVESlJaMEZCUjBKNmVraElXa05CUVVGQmFTOVpZMlJyU1VGQlQybzFLMUo0TWxGblFVRXdSMm81U0VoYVEwRkJRelF4ZDBGa1pHdEpRVUZMUWtkQ1FqRXlVV2RCUVdsTVZVaElXRnBEUVVGQ2QwcEJjMlJrYTBsQlFVWnBWRVJvTVRKUlowRkJVVUZKVTBoWVdrTkJRVUZ2WTFKVlpHUnJTVUZCUWtSblIwSXhNbEZuUVVFclJUUmpTRmhhUTBGQlJHZDJVamhrWkd0SlFVRk5aM05KZURFeVVXZEJRWE5LYzIxSVdGcERRVUZEV1VOcGIyUmthMGxCUVVsQ05VeFNNVEpSWjBGQllVOW5kMGhZV2tOQlFVSlJWbnBSWkdSclNVRkJSR3BIVG5neE1sRm5RVUZKUkZVM1NGaGFRMEZCUVVsd1JEUmtaR3RKUVVGUVFWTlJhREV5VVdkQlFUSkpSa1pJV0ZwRFFVRkVRVGhGWjJSa2EwbEJRVXRvWmxSQ01USlJaMEZCYTAwMVVFaFlXa05CUVVJMFVGWk5aR1JyU1VGQlIwTnpWbWd4TWxGblFVRlRRblJoU0ZoYVEwRkJRWGRwYkRCa1pHdEpRVUZDYWpWWlFqRXlVV2RCUVVGSGFHdElXRnBEUVVGRWJ6RnRZMlJrYTBsQlFVNUNSbUY0TVRKUlowRkJkVXhTZFVoWVdrTkJRVU5uU1ROSlpHUnJTVUZCU1dsVFpGSXhNbEZuUVVGalFVWTFTRmhhUTBGQlFsbGpTSGRrWkd0SlFVRkZSR1ptZURFeVVXZEJRVXRGTmtSSVdGcERRVUZCVVhaWldXUmthMGxCUVZCbmNtbG9NVEpSWjBGQk5FcHhUa2hZV2tOQlFVUkpRMXBGWkdSclNVRkJURUkwYkVJeE1sRm5RVUZ0VDJWWVNGaGFRMEZCUTBGV2NITmtaR3RKUVVGSGFrWnVhREV5VVdkQlFWVkVVMmxJV0ZwRFFVRkJORzgyVldSa2EwbEJRVU5CVTNGU01USlJaMEZCUTBsSGMwaFlXa05CUVVSM056WTRaR1JyU1VGQlRtaGxjM2d4TWxGblFVRjNUVEl5U0ZoYVEwRkJRMjlRVEc5a1pHdEpRVUZLUTNKMlVqRXlVV2RCUVdWQ2NrSklXRnBEUVVGQ1oybGpVV1JrYTBsQlFVVnFOSGg0TVRKUlowRkJUVWRtVEVoWVdrTkJRVUZaTVhNMFpHUnJTVUZCUVVKR01HZ3hNbEZuUVVFMlRGQldTRmhhUTBGQlJGRkpkR3RrWkd0SlFVRk1hVkl6UWpFeVVXZEJRVzlCUkdkSVdGcERRVUZEU1dJclRXUmthMGxCUVVoRVpUVm9NVEpSWjBGQlYwVXpjVWhZV2tOQlFVSkJkazh3WkdSclNVRkJRMmR5T0ZJeE1sRm5RVUZGU25Jd1NGaGFRMEZCUkRSRFVHZGtaR3RKUVVGUFFqTXJlREV5VVdkQlFYbFBZaXRJV0ZwRFFVRkRkMVpSU1dWa2EwbEJRVXBxUlVKU05USlJaMEZCWjBSTlNraHVXa05CUVVKdmIyZDNaV1JyU1VGQlJrRlNSVUkxTWxGblFVRlBTVUZVU0c1YVEwRkJRV2MzZUZsbFpHdEpRVUZCYUdWSGFEVXlVV2RCUVRoTmQyUklibHBEUVVGRVdVOTVSV1ZrYTBsQlFVMURjVXBDTlRKUlowRkJjVUpyYjBodVdrTkJRVU5SYVVOelpXUnJTVUZCU0dvelRHZzFNbEZuUVVGWlIxbDVTRzVhUTBGQlFra3hWRlZsWkd0SlFVRkVRa1ZQVWpVeVVXZEJRVWRNVFRoSWJscERJaXdpWkhSNWNHVWlPaUptYkc5aGREWTBJaXdpYzJoaGNHVWlPbHN4TkRSZGZTd2llU0k2ZXlKZlgyNWtZWEp5WVhsZlh5STZJa0ZCUVVGUlJtSnFSVVZCUVVGQlJHZFNjVGhTVVVGQlFVRkxRVE5sZUVwQlFVRkJRVkZEYUVoRk1FRkJRVUZEUVVsSVRWUlJRVUZCUVU5QldXNTRUa0ZCUVVGQlNVSklURVV3UVVGQlFVTkJPQzlWVkZGQlFVRkJUMFJXU1VKU1FVRkJRVUZSVEdoTVJrVkJRVUZCUVdkWWJGbFZVVUZCUVVGRFFVVlpVbEpCUVVGQlFVRkxjSEpHUlVGQlFVRkNaM2xaWjFWUlFVRkJRVXRFYjNCU1VrRkJRVUZCUVVGcVJFWkZRVUZCUVVKQlduWnZWVkZCUVVGQlMwUkZUVkpXUVVGQlFVRTBRMHB3UmxWQlFVRkJSRUYxYldOV1VVRkJRVUZMUWxOYWFGWkJRVUZCUVdkUGNHdEdWVUZCUVVGRVFURlZkMVpSUVVGQlFVTkVRazVDVmtGQlFVRkJXVXQzWTBaVlFVRkJRVUZuY0hVNFZWRkJRVUZCVDBObWQyaFNRVUZCUVVGdlNtMVdSa1ZCUVVGQlFVRmtiMWxWVVVGQlFVRkhRbE5rZUZKQlFVRkJRWGRETlc5R1JVRkJRVUZEWjFOc2QxVlJRVUZCUVVkQ2JWVkNVa0ZCUVVGQlVVbEtSVVpGUVVGQlFVRkJhVk5CVlZGQlFVRkJUVU5RTDBKT1FVRkJRVUZuU21KWlJUQkJRVUZCUVVGTVltTlVVVUZCUVVGSlJFUnNVazVCUVVGQlFVRkdjREJGTUVGQlFVRkRRWHBUU1ZSUlFVRkJRVUZDUWpCU1NrRkJRVUZCWjB4U0wwVnJRVUZCUVVOQlNrWkZVMUZCUVVGQlMwTlZTV2hLUVVGQlFVRnZRVlF3UlZWQlFVRkJRa0ZuWm10U1VVRkJRVUZQUkRrdmFFWkJRVUZCUVdkSWIwVkZhMEZCUVVGQlp5OVdiMU5SUVVGQlFVOUNMM05TU2tGQlFVRkJaMEZKU1VVd1FVRkJRVVJCT1VOalZGRkJRVUZCUVVSdVVuaE9RVUZCUVVGUlRteHVSVEJCUVVGQlFVRTRNMFZVVVVGQlFVRk5RVTFtUWs1QlFVRkJRV2REWVVkRk1FRkJRVUZDUVRGSlRWUlJRVUZCUVU5RFFtZFNUa0ZCUVVGQmIwTTVMMFV3UVVGQlFVUkJjbGcwVkZGQlFVRkJUMEZ5Wm1oT1FVRkJRVUZCUzNBNVJUQkJRVUZCUWtGaFMzZFVVVUZCUVVGTFFXMHllRTVCUVVGQlFUUlBVVXBHUlVGQlFVRkVRWHBwYTFWUlFVRkJRVTFETkZOU1VrRkJRVUZCYjB0S2NFWkZRVUZCUVVObllXdFJWVkZCUVVGQlNVRjVTSGhTUVVGQlFVRm5VSEkxUlRCQlFVRkJRVUU1WkRCVVVVRkJRVUZKUkhaM1VrNUJRVUZCUVVGUGNXeEZNRUZCUVVGQlowcElPRlJSUVVGQlFVTkNaVmRDVGtGQlFVRkJVVXBuZUVVd1FVRkJRVVJuV1dkdlZGRkJRVUZCUjBGME5IaEtRVUZCUVVGQlVHazNSV3RCUVVGQlEwRXZOVmxUVVVGQlFVRkRRVWhqYUVwQlFVRkJRVzlCTlU1RmEwRkJRVUZDUVM5c05GTlJRVUZCUVU5RWRHTkNTa0ZCUVVGQlowNHlRMFZyUVVGQlFVUm5hSE5SVTFGQlFVRkJRMEYzUW1oT1FVRkJRVUZuVG14SVJUQkJRVUZCUW1kS1ZqaFVVVUZCUVVGRFFuaGthRTVCUVVGQlFVRk1NazVGTUVGQlFVRkRRVEJ1VVZSUlFVRkJRVU5FYjFkNFRrRkJRVUZCYjFBeFEwVXdRVUZCUVVGQk9IbEpWRkZCUVVGQlJVUnZRV2hPUVVGQlFVRnZUak5wUld0QlFVRkJSRUY0T0hkVFVVRkJRVUZOUTNoMGFFcEJRVUZCUVRSS2RXZEZhMEZCUVVGRFoyTndaMU5SUVVGQlFVVkNTbXRDU2tGQlFVRkJRVU5EU1VWclFVRkJRVVJCTW01blUxRkJRVUZCUzBOV1lWSktRVUZCUVVGWlJrSmhSV3RCUVVGQlFXZEVSamhUVVVGQlFVRlBSRWhaZUVwQlFVRkJRVzlKVG05RmEwRkJRVUZFWnpKd1JWTlJRVUZCUVVOQmVYVjRTa0ZCUVVGQldVbHVhMFZyUVVGQlFVRm5PRTg0VTFGQlFVRkJUMEpYSzNoS1FVRkJRVUZ2VERCSFJUQkJRVUZCUTBGWFFVbFVVVUZCUVVGRlJIb3ZVa3BCUVVGQlFVbEpOelZGYTBGQlFVRkNaM0IyYTFOUlFVRkJRVTFES3l0U1NrRkJRVUZCUVU1bU5VVnJRVUZCUVVKQk1YWkpVMUZCUVVGQlIwUldObmhLUVVGQlFVRnZUbFJyUld0QlFVRkJRMEY0WlVGVFVVRkJRVUZKUXpJelFrcEJRVUZCUVZsTFpsbEZhMEZCUVVGQ1FVZE9SVk5SUVVGQlFVVkRTbmxTU2tGQlFVRkJTVkJ5UWtWclFVRkJRVU5uVWswNFUxRkJRVUZCUlVOUU0wSktRVUZCUVVGM1RtNXdSV3RCUVVGQlEwRkpaamhUVVVGQlFVRkRRbkJHUWs1QlFVRkJRVFJNUVhCRk1FRkJRVUZFUVdSVE1GUlJRVUZCUVUxQk5rMVNUa0ZCUVVGQmIxQTRNRVV3UVVGQlFVTm5MM3BSVkZGQlFVRkJTMFF2VGtKT1FTSXNJbVIwZVhCbElqb2labXh2WVhRMk5DSXNJbk5vWVhCbElqcGJNVFEwWFgxOWZTd2lhV1FpT2lKa1ptRmlZelE1TnkwME9HTXdMVFF5WXpFdFlqYzFaUzFtT1RZeFptUmtOVFprTURnaUxDSjBlWEJsSWpvaVEyOXNkVzF1UkdGMFlWTnZkWEpqWlNKOUxIc2lZWFIwY21saWRYUmxjeUk2ZTMwc0ltbGtJam9pTkRFNE9EVTNNRGt0TVRkak1pMDBNalZoTFdFM1pHUXRNamhqTldNMU5tSTNOMlUzSWl3aWRIbHdaU0k2SWt4cGJtVmhjbE5qWVd4bEluMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0lteHBibVZmWVd4d2FHRWlPakF1TmpVc0lteHBibVZmWTJGd0lqb2ljbTkxYm1RaUxDSnNhVzVsWDJOdmJHOXlJam9pSXpGbU56ZGlOQ0lzSW14cGJtVmZhbTlwYmlJNkluSnZkVzVrSWl3aWJHbHVaVjkzYVdSMGFDSTZOU3dpZUNJNmV5Sm1hV1ZzWkNJNkluZ2lmU3dpZVNJNmV5Sm1hV1ZzWkNJNklua2lmWDBzSW1sa0lqb2lPRFUzWVRVNVptSXRZekkxTkMwME9HTTRMVGxtT0RjdE1qZzVNekkzTUdGaU9UTTRJaXdpZEhsd1pTSTZJa3hwYm1VaWZTeDdJbUYwZEhKcFluVjBaWE1pT250OUxDSnBaQ0k2SWpBMVlqUTNObVUwTFRVNVkyTXRORFU1TVMwNU1XWmpMV1l4Wm1WbE1ERXdaR0ZsTlNJc0luUjVjR1VpT2lKQ1lYTnBZMVJwWTJ0R2IzSnRZWFIwWlhJaWZTeDdJbUYwZEhKcFluVjBaWE1pT250OUxDSnBaQ0k2SWpsalkyWmxNR0ZoTFRkaU1tWXRORGRrT1MwNFpXUmlMVFZsTTJZek5qZzROR0ZsTWlJc0luUjVjR1VpT2lKU1pYTmxkRlJ2YjJ3aWZTeDdJbUYwZEhKcFluVjBaWE1pT25zaWJuVnRYMjFwYm05eVgzUnBZMnR6SWpvMUxDSjBhV05yWlhKeklqcGJleUpwWkNJNklqQTRPVEk1WmpCbUxUTTFaR010TkdNeU1TMWhNMkZrTFdWaU1XTTFZbVF5TURNek9TSXNJblI1Y0dVaU9pSkJaR0Z3ZEdsMlpWUnBZMnRsY2lKOUxIc2lhV1FpT2lJNU1EWXpZMkUxWmkwNFlUZ3hMVFF3TkdVdFlXWXhOQzB3T1RjMFlqTXpaR00xTmpJaUxDSjBlWEJsSWpvaVFXUmhjSFJwZG1WVWFXTnJaWElpZlN4N0ltbGtJam9pWVROa01tRXlPVGd0WkdGak9DMDBaakpsTFdJd05Ua3RNREEzWWpNeE5qYzRaV1EwSWl3aWRIbHdaU0k2SWtGa1lYQjBhWFpsVkdsamEyVnlJbjBzZXlKcFpDSTZJakZrTnpRek9HUmpMVFUxTkdVdE5EaGlaaTFoWmpKaUxXSXdaak0yTWpZeU56Y3lOeUlzSW5SNWNHVWlPaUpFWVhselZHbGphMlZ5SW4wc2V5SnBaQ0k2SWpsaU56Y3lPR1V4TFdSaVlUY3ROR05oTXkxaE56QmlMV0l5TVdVeFkyWXpORGRqTnlJc0luUjVjR1VpT2lKRVlYbHpWR2xqYTJWeUluMHNleUpwWkNJNklqQmlNR1ppTlRkaExUWTJPVGt0TkRKaE5TMWhNMlpsTFRnM056Qm1aakkzTURjeVlTSXNJblI1Y0dVaU9pSkVZWGx6VkdsamEyVnlJbjBzZXlKcFpDSTZJbU0yWkdabVpqazNMVGc0TUdNdE5ERmhOUzFpTlRJNExUUTRNVEpoWkRrM05HVXdNU0lzSW5SNWNHVWlPaUpFWVhselZHbGphMlZ5SW4wc2V5SnBaQ0k2SW1RMllUWXdNakUzTFRaaU16TXROREJtTVMxaE5qVXhMVE5oTVRrNU5qTTNZVEEyTlNJc0luUjVjR1VpT2lKTmIyNTBhSE5VYVdOclpYSWlmU3g3SW1sa0lqb2lNek5pT1dGa1lqTXROVFJtTlMwMFlUTm1MV0ptWVdFdFpXVTROMk0xTkRSak1UUXhJaXdpZEhsd1pTSTZJazF2Ym5Sb2MxUnBZMnRsY2lKOUxIc2lhV1FpT2lJNE5qTTJZVEkwWlMxbU4yUmpMVFJqTm1JdE9UWmpNUzAyT1RJNU5UTTJPREZpTW1JaUxDSjBlWEJsSWpvaVRXOXVkR2h6VkdsamEyVnlJbjBzZXlKcFpDSTZJbUV4WTJGaE9UYzFMV1k1WXpFdE5EUTFZaTA0WlRsaExXVmlaVEkwTXprd1lUWmhaU0lzSW5SNWNHVWlPaUpOYjI1MGFITlVhV05yWlhJaWZTeDdJbWxrSWpvaVlUQmlNakZsWkRRdFpqZ3laQzAwTmpreUxXSXdNemd0WXpjM01qTTRZekl4WmpoaUlpd2lkSGx3WlNJNklsbGxZWEp6VkdsamEyVnlJbjFkZlN3aWFXUWlPaUl3WVRZeE5EVmxaUzAxT0RjeExUUmtPVEF0T0dRM055MHhZVEUzT0dJek5URXhaR1lpTENKMGVYQmxJam9pUkdGMFpYUnBiV1ZVYVdOclpYSWlmU3g3SW1GMGRISnBZblYwWlhNaU9uc2lZbVZzYjNjaU9sdDdJbWxrSWpvaVltRmxNbVZoTURJdFpqUTVOQzAwWldWaExUbGtZbU10TkdSa09XTm1ZalF3WWpOaUlpd2lkSGx3WlNJNklrUmhkR1YwYVcxbFFYaHBjeUo5WFN3aWJHVm1kQ0k2VzNzaWFXUWlPaUptT1dNMk5EUXdPUzFtWkdabExUUm1PR010T0dOaVpDMHdORFpoT0RFek56QXpOV0VpTENKMGVYQmxJam9pVEdsdVpXRnlRWGhwY3lKOVhTd2ljR3h2ZEY5b1pXbG5hSFFpT2pJMU1Dd2ljR3h2ZEY5M2FXUjBhQ0k2TnpVd0xDSnlaVzVrWlhKbGNuTWlPbHQ3SW1sa0lqb2lZbUZsTW1WaE1ESXRaalE1TkMwMFpXVmhMVGxrWW1NdE5HUmtPV05tWWpRd1lqTmlJaXdpZEhsd1pTSTZJa1JoZEdWMGFXMWxRWGhwY3lKOUxIc2lhV1FpT2lKbU56ZGlZV1EzT1MwMFpHSTBMVFEzT0RFdE9UVmpPUzAxWkRVeFltWXlZek0xTlRRaUxDSjBlWEJsSWpvaVIzSnBaQ0o5TEhzaWFXUWlPaUptT1dNMk5EUXdPUzFtWkdabExUUm1PR010T0dOaVpDMHdORFpoT0RFek56QXpOV0VpTENKMGVYQmxJam9pVEdsdVpXRnlRWGhwY3lKOUxIc2lhV1FpT2lJMVpEUTBOVFppTlMwNVltRXhMVFJsWVdFdE9HUTBPQzAzTm1OaVltWmtZVGN6TUdRaUxDSjBlWEJsSWpvaVIzSnBaQ0o5TEhzaWFXUWlPaUprTmprM1l6RmlZUzA1TkRVMkxUUXpaR0l0WVROaE55MDROR1ZpWW1KaE9EWTVZaklpTENKMGVYQmxJam9pUW05NFFXNXViM1JoZEdsdmJpSjlMSHNpYVdRaU9pSTJNRFJrT0dVMVlpMWtOV1ZsTFRReE4yTXRPVGsyWVMwM05qVTJaRE0zTXpnNFlqRWlMQ0owZVhCbElqb2lUR1ZuWlc1a0luMHNleUpwWkNJNkltWTROamhpWlRrd0xURmtaVEV0TkdZME5TMWlZMlE1TFRJME9UUTROVEkyWmpFNFpTSXNJblI1Y0dVaU9pSkhiSGx3YUZKbGJtUmxjbVZ5SW4wc2V5SnBaQ0k2SW1Gak1qRTFOekU1TFRabE1USXRORGs0WWkwNE1ERTRMV0ZsT0dRNVpqaG1OMlE1TkNJc0luUjVjR1VpT2lKSGJIbHdhRkpsYm1SbGNtVnlJbjBzZXlKcFpDSTZJbUZrWldReU5qSmpMV0ZpWXpBdE5ERXpZeTA1WldGa0xXTTRZV0l4TnpJNU5HWm1OaUlzSW5SNWNHVWlPaUpIYkhsd2FGSmxibVJsY21WeUluMHNleUpwWkNJNkltSmlOREk0WldNd0xUZGtNV1l0TkRnek1TMDRNV05pTFdNME9HVTJZV0l6WW1ZMlppSXNJblI1Y0dVaU9pSkhiSGx3YUZKbGJtUmxjbVZ5SW4xZExDSjBhWFJzWlNJNmV5SnBaQ0k2SWpNeE5tUTFZVGM1TFdZek4yVXROR1F5WXkwNE1EazNMVEJqTVRoa09ESmtZbVkyTmlJc0luUjVjR1VpT2lKVWFYUnNaU0o5TENKMGIyOXNZbUZ5SWpwN0ltbGtJam9pTkdVeFltWm1OelF0TXpReE1TMDBOV05pTFdJeU9EZ3ROMkptTXpZeE9UaGlaR1JqSWl3aWRIbHdaU0k2SWxSdmIyeGlZWElpZlN3aWRHOXZiR0poY2w5c2IyTmhkR2x2YmlJNkltRmliM1psSWl3aWVGOXlZVzVuWlNJNmV5SnBaQ0k2SWpJNE5tVTNaVFF5TFdFM05HVXRORGM1TVMwNVpqZGpMV1l3WVRSak1XWTNZVE16TlNJc0luUjVjR1VpT2lKRVlYUmhVbUZ1WjJVeFpDSjlMQ0o0WDNOallXeGxJanA3SW1sa0lqb2lOREU0T0RVM01Ea3RNVGRqTWkwME1qVmhMV0UzWkdRdE1qaGpOV00xTm1JM04yVTNJaXdpZEhsd1pTSTZJa3hwYm1WaGNsTmpZV3hsSW4wc0lubGZjbUZ1WjJVaU9uc2lhV1FpT2lJM1lUVTNORGRqTXkwek1HWmhMVFE1TkRRdFlXVTRaaTAzTWpaaU5XRmlOVFF6TkdZaUxDSjBlWEJsSWpvaVJHRjBZVkpoYm1kbE1XUWlmU3dpZVY5elkyRnNaU0k2ZXlKcFpDSTZJbVk0WVRJMVlqZ3pMVGhqTkRVdE5HRXdOeTFpTWpBM0xXSTJPVFptWkRsbVpUUXhaaUlzSW5SNWNHVWlPaUpNYVc1bFlYSlRZMkZzWlNKOWZTd2lhV1FpT2lJd1lXWmhOakl6WWkweU9XTXlMVFF6Tm1FdE9HUmxNeTFsTkRrNU9HSTBPVEZoTVRRaUxDSnpkV0owZVhCbElqb2lSbWxuZFhKbElpd2lkSGx3WlNJNklsQnNiM1FpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnQ5TENKcFpDSTZJbU5oTjJOaU5tVXlMV0pqT0RJdE5ETm1ZeTA0TmpJMkxUTTBOVFpqTVRjNFkyRXdaaUlzSW5SNWNHVWlPaUpDWVhOcFkxUnBZMnRsY2lKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKc2FXNWxYMkZzY0doaElqb3dMalkxTENKc2FXNWxYMk5oY0NJNkluSnZkVzVrSWl3aWJHbHVaVjlqYjJ4dmNpSTZJaU5oWldNM1pUZ2lMQ0pzYVc1bFgycHZhVzRpT2lKeWIzVnVaQ0lzSW14cGJtVmZkMmxrZEdnaU9qVXNJbmdpT25zaVptbGxiR1FpT2lKNEluMHNJbmtpT25zaVptbGxiR1FpT2lKNUluMTlMQ0pwWkNJNkltVmxORE5sT0RJNUxXVXdZVEV0TkRJM01pMDVOVFppTFdVeE16UmxNemM1TVRSbFppSXNJblI1Y0dVaU9pSk1hVzVsSW4wc2V5SmhkSFJ5YVdKMWRHVnpJanA3SW1OaGJHeGlZV05ySWpwdWRXeHNMQ0p5Wlc1a1pYSmxjbk1pT2x0N0ltbGtJam9pWmpnMk9HSmxPVEF0TVdSbE1TMDBaalExTFdKalpEa3RNalE1TkRnMU1qWm1NVGhsSWl3aWRIbHdaU0k2SWtkc2VYQm9VbVZ1WkdWeVpYSWlmVjBzSW5SdmIyeDBhWEJ6SWpwYld5Sk9ZVzFsSWl3aVRrVkRUMFpUWDAxaGMzTkNZWGtpWFN4YklrSnBZWE1pTENJd0xqUXlJbDBzV3lKVGEybHNiQ0lzSWpBdU1qWWlYVjE5TENKcFpDSTZJbU5rT1dNek1qYzFMV0kxT0RBdE5EZzBNaTFpTXpjekxURTRPRGc0TURGalkySmhOaUlzSW5SNWNHVWlPaUpJYjNabGNsUnZiMndpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpWTJGc2JHSmhZMnNpT201MWJHd3NJbU52YkhWdGJsOXVZVzFsY3lJNld5SjRJaXdpZVNKZExDSmtZWFJoSWpwN0luZ2lPbnNpWDE5dVpHRnljbUY1WDE4aU9pSkJRVUZCT1V0M1ltUnJTVUZCVDJocGMwSjBNbEZuUVVFd1RrZDZSek5hUTBGQlF6UlJUR05pWkd0SlFVRkxRM1oxYUhReVVXZEJRV2xDTml0SE0xcERRVUZDZDJwalJXSmthMGxCUVVacU9IaENkREpSWjBGQlVVZDJTVWN6V2tOQlFVRnZNbk56WW1SclNVRkJRa0pLZW5oME1sRm5RVUVyVEdaVFJ6TmFRMEZCUkdkS2RGbGlaR3RKUVVGTmFWWXlVblF5VVdkQlFYTkJWR1JITTFwRFFVRkRXV01yUVdKa2EwbEJRVWxFYVRSNGRESlJaMEZCWVVaSWJrY3pXa05CUVVKUmQwOXZZbVJyU1VGQlJHZDJOMmgwTWxGblFVRkpTamQ0UnpOYVEwRkJRVWxFWmxWaVpHdEpRVUZRUWpjclFuUXlVV2RCUVRKUGNqZEhNMXBEUVVGRVFWZG1PR0prYTBsQlFVdHFTVUZvZURKUlowRkJhMFJqUjBoSVdrTkJRVUkwY0dkclkyUnJTVUZCUjBGV1JGSjRNbEZuUVVGVFNWRlJTRWhhUTBGQlFYYzRlRTFqWkd0SlFVRkNhR2xHZUhneVVXZEJRVUZPUldGSVNGcERRVUZFYjFCNE5HTmthMGxCUVU1RGRVbFNlREpSWjBGQmRVSXdiRWhJV2tOQlFVTm5ha05uWTJSclNVRkJTV28zUzNoNE1sRm5RVUZqUjI5MlNFaGFRMEZCUWxreVZFbGpaR3RKUVVGRlFrbE9hSGd5VVdkQlFVdE1ZelZJU0ZwRFFVRkJVVXBxTUdOa2EwbEJRVkJwVlZGQ2VESlJaMEZCTkVGT1JVaElXa05CUVVSSlkydGpZMlJyU1VGQlRFUm9VMmg0TWxGblFVRnRSa0pQU0VoYVEwRkJRMEYyTVVWalpHdEpRVUZIWjNWV1VuZ3lVV2RCUVZWS01WbElTRnBEUVVGQk5FUkdkMk5rYTBsQlFVTkNOMWg0ZURKUlowRkJRMDl3YVVoSVdrTkJRVVIzVjBkWlkyUnJTVUZCVG1wSVlWSjRNbEZuUVVGM1JGcDBTRWhhUTBGQlEyOXdXRUZqWkd0SlFVRktRVlZrUW5neVVXZEJRV1ZKVGpOSVNGcERRVUZDWnpodWIyTmthMGxCUVVWb2FHWm9lREpSWjBGQlRVNURRa2hJV2tOQlFVRlpVRFJWWTJSclNVRkJRVU4xYVVKNE1sRm5RVUUyUW5sTlNFaGFRMEZCUkZGcE5EaGpaR3RKUVVGTWFqWnJhSGd5VVdkQlFXOUhiVmRJU0ZwRFFVRkRTVEpLYTJOa2EwbEJRVWhDU0c1U2VESlJaMEZCVjB4aFowaElXa05CUVVKQlNtRlJZMlJyU1VGQlEybFZjSGg0TWxGblFVRkZRVTl5U0VoYVEwRkJSRFJqWVRSalpHdEpRVUZQUkdkelVuZ3lVV2RCUVhsRkt6RklTRnBEUVVGRGQzWnlaMk5rYTBsQlFVcG5kSFpDZURKUlowRkJaMHA1TDBoSVdrTkJRVUp2UXpoTlkyUnJTVUZCUmtJMmVHaDRNbEZuUVVGUFQyNUtTRWhhUTBGQlFXZFhUVEJqWkd0SlFVRkJha2d3UW5neVVXZEJRVGhFV0ZWSVNGcERRVUZFV1hCT1kyTmthMGxCUVUxQlZESjRlREpSWjBGQmNVbE1aVWhJV2tOQlFVTlJPR1ZGWTJSclNVRkJTR2huTlZKNE1sRm5RVUZaVFM5dlNFaGFRMEZCUWtsUWRYZGpaR3RKUVVGRVEzUTNlSGd5VVdkQlFVZENlbnBJU0ZwRFFVRkJRV2t2V1dOa2EwbEJRVTlxTlN0U2VESlJaMEZCTUVkcU9VaElXa05CUVVNME1YZEJaR1JyU1VGQlMwSkhRa0l4TWxGblFVRnBURlZJU0ZoYVEwRkJRbmRLUVhOa1pHdEpRVUZHYVZSRWFERXlVV2RCUVZGQlNWTklXRnBEUVVGQmIyTlNWV1JrYTBsQlFVSkVaMGRDTVRKUlowRkJLMFUwWTBoWVdrTkJRVVJuZGxJNFpHUnJTVUZCVFdkelNYZ3hNbEZuUVVGelNuTnRTRmhhUTBGQlExbERhVzlrWkd0SlFVRkpRalZNVWpFeVVXZEJRV0ZQWjNkSVdGcERRVUZDVVZaNlVXUmthMGxCUVVScVIwNTRNVEpSWjBGQlNVUlZOMGhZV2tOQlFVRkpjRVEwWkdSclNVRkJVRUZUVVdneE1sRm5RVUV5U1VaR1NGaGFRMEZCUkVFNFJXZGtaR3RKUVVGTGFHWlVRakV5VVdkQlFXdE5OVkJJV0ZwRFFVRkNORkJXVFdSa2EwbEJRVWREYzFab01USlJaMEZCVTBKMFlVaFlXa05CUVVGM2FXd3daR1JyU1VGQlFtbzFXVUl4TWxGblFVRkJSMmhyU0ZoYVEwRkJSRzh4YldOa1pHdEpRVUZPUWtaaGVERXlVV2RCUVhWTVVuVklXRnBEUVVGRFowa3pTV1JrYTBsQlFVbHBVMlJTTVRKUlowRkJZMEZHTlVoWVdrTkJRVUpaWTBoM1pHUnJTVUZCUlVSbVpuZ3hNbEZuUVVGTFJUWkVTRmhhUTBGQlFWRjJXVmxrWkd0SlFVRlFaM0pwYURFeVVXZEJRVFJLY1U1SVdGcERRVUZFU1VOYVJXUmthMGxCUVV4Q05HeENNVEpSWjBGQmJVOWxXRWhZV2tNaUxDSmtkSGx3WlNJNkltWnNiMkYwTmpRaUxDSnphR0Z3WlNJNld6RTBORjE5TENKNUlqcDdJbDlmYm1SaGNuSmhlVjlmSWpvaVRYcE5lazE2VFhwRk1FRjZUWHBOZWsxNlRWUlJTbkZhYlZwdFdtMVNUa0ZCUVVGQlFVRkJRVVpGUVhwTmVrMTZUWHBOVkZGRVRYcE5lazE2VFhoT1FWcHRXbTFhYlZwdFJXdENiVnB0V20xYWJWbFRVVTB6VFhwTmVrMTZRa3BCVFhwTmVrMTZUWHBGTUVGNlRYcE5lazE2VFZSUlJFMTZUWHBOZWsxNFRrRjZZM3BOZWsxNlRVVnJSRTU2VFhwTmVrMTNVMUZIV20xYWJWcHRXbWhLUVVGQlFVRkJRVUZCUld0RFlXMWFiVnB0V210U1VVcHhXbTFhYlZwdFVrWkJiWEJ0V20xYWJWcEZWVU5oYlZwdFdtMWFhMUpSU25GYWJWcHRXbTFTUmtGdGNHMWFiVnB0V2tWVlEyRnRXbTFhYlZwclVsRkVUWHBOZWsxNlRYaEdRVTE2VFhwTmVrMTZSVlZCZWsxNlRYcE5lazFTVVVSTmVrMTZUWHBOZUVaQlRYcE5lazE2VFhwRlZVRjZUWHBOZWsxNlRWSlJSRTE2VFhwTmVrMTRSa0ZOZWsxNlRYcE5la1ZWUVhwTmVrMTZUWHBOVWxGRVRYcE5lazE2VFhoR1FVMTZUWHBOZWsxNlJWVkJlazE2VFhwTmVrMVNVVVJOZWsxNlRYcE5lRVpCVFhwTmVrMTZUWHBGVlVGNlRYcE5lazE2VFZKUlJFMTZUWHBOZWsxNFJrRk5lazE2VFhwTmVrVlZRWHBOZWsxNlRYcE5VbEZLY1ZwdFdtMWFiVkpHUVcxd2JWcHRXbTFhUlZWRFlXMWFiVnB0V210U1VVcHhXbTFhYlZwdFVrWkJiWEJ0V20xYWJWcEZWVUY2VFhwTmVrMTZUVkpSUkUxNlRYcE5lazE0UmtGTmVrMTZUWHBOZWtWVlFYcE5lazE2VFhwTlVsRkVUWHBOZWsxNlRYaEdRVTE2VFhwTmVrMTZSVlZEWVcxYWJWcHRXbXRTVVVweFdtMWFiVnB0VWtaQmJYQnRXbTFhYlZwRlZVTmhiVnB0V20xYWExSlJTbkZhYlZwdFdtMVNSa0ZOZWsxNlRYcE5la1ZWUVhwTmVrMTZUWHBOVWxGRVRYcE5lazE2VFhoR1FVMTZUWHBOZWsxNlJWVkJlazE2VFhwTmVrMVNVVVJOZWsxNlRYcE5lRVpCYlhCdFdtMWFiVnBGVlVGQlFVRkJRVUZCUVZOUlIxcHRXbTFhYlZwb1NrRjZZM3BOZWsxNlRVVnJRWHBOZWsxNlRYcE5WRkZFVFhwTmVrMTZUWGhPUVcxd2JWcHRXbTFhUlRCRFlXMWFiVnB0V210VVVVcHhXbTFhYlZwdFVrNUJUWHBOZWsxNlRYcEZNRVJPZWsxNlRYcE5kMU5SUVVGQlFVRkJRVUZDU2tGQlFVRkJRVUZCUVVWclEyRnRXbTFhYlZwclVsRktjVnB0V20xYWJWSkdRVzF3YlZwdFdtMWFSVlZCUVVGQlFVRkJRVUZUVVVweFdtMWFiVnB0VWtaQlRYcE5lazE2VFhwRlZVRjZUWHBOZWsxNlRWSlJSRTE2VFhwTmVrMTRSa0ZOZWsxNlRYcE5la1ZWUkU1NlRYcE5lazEzVVZGTk0wMTZUWHBOZWtKQ1FYcGplazE2VFhwTlJVVkJlazE2VFhwTmVrMVNVVVJOZWsxNlRYcE5lRVpCVFhwTmVrMTZUWHBGVlVOaGJWcHRXbTFhYTFKUlNuRmFiVnB0V20xU1JrRnRjRzFhYlZwdFdrVlZRVUZCUVVGQlFVRkJVMUZCUVVGQlFVRkJRVUpLUVVGQlFVRkJRVUZCUld0QlFVRkJRVUZCUVVGVFVVRkJRVUZCUVVGQlFrcEJRVUZCUVVGQlFVRkZhMEZCUVVGQlFVRkJRVk5SUVVGQlFVRkJRVUZDU2tGQlFVRkJRVUZCUVVWclFVRkJRVUZCUVVGQlUxRkJRVUZCUVVGQlFVSktRVUZCUVVGQlFVRkJSV3RCUVVGQlFVRkJRVUZUVVVGQlFVRkJRVUZCUWtwQmJYQnRXbTFhYlZwRlZVTmhiVnB0V20xYWExSlJRVUZCUVVGQlFVRkNTa0ZCUVVGQlFVRkJRVVZyUVVGQlFVRkJRVUZCVTFGSFdtMWFiVnB0V21oS1FWcHRXbTFhYlZwdFJXdEVUbnBOZWsxNlRYZFRVVTB6VFhwTmVrMTZRa3BCZW1ONlRYcE5lazFGYTBST2VrMTZUWHBOZDFOUlIxcHRXbTFhYlZwb1NrRmFiVnB0V20xYWJVVnJRbTFhYlZwdFdtMVpVMUZIV20xYWJWcHRXbWhLUVZwdFdtMWFiVnB0Uld0QlFVRkJRVUZCUVVGVFVVRkJRVUZCUVVGQlFrcEJRVUZCUVVGQlFVRkZhMEZCUVVGQlFVRkJRVk5SUVVGQlFVRkJRVUZDU2tGQlFVRkJRVUZCUVVWclFVRkJRVUZCUVVGQlUxRktjVnB0V20xYWJWSkdRVzF3YlZwdFdtMWFSVlZCZWsxNlRYcE5lazFTVVVweFdtMWFiVnB0VWtaQmJYQnRXbTFhYlZwRlZVRkJRVUZCUVVGQlFWTlJRVUZCUVVGQlFVRkNTa0ZhYlZwdFdtMWFiVVZyUVVGQlFVRkJRVUZCVlZGTk0wMTZUWHBOZWtKU1FVMTZUWHBOZWsxNlJsVkNiVnB0V20xYWJWbFZVVXB4V20xYWJWcHRVazVCSWl3aVpIUjVjR1VpT2lKbWJHOWhkRFkwSWl3aWMyaGhjR1VpT2xzeE5EUmRmWDE5TENKcFpDSTZJbVppTURBME9UUTRMV0UwTkdNdE5HWmhOeTA1TWpaa0xUVTJPRE13T1dOaVl6ZzJZeUlzSW5SNWNHVWlPaUpEYjJ4MWJXNUVZWFJoVTI5MWNtTmxJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbVJwYldWdWMybHZiaUk2TVN3aWNHeHZkQ0k2ZXlKcFpDSTZJakJoWm1FMk1qTmlMVEk1WXpJdE5ETTJZUzA0WkdVekxXVTBPVGs0WWpRNU1XRXhOQ0lzSW5OMVluUjVjR1VpT2lKR2FXZDFjbVVpTENKMGVYQmxJam9pVUd4dmRDSjlMQ0owYVdOclpYSWlPbnNpYVdRaU9pSmpZVGRqWWpabE1pMWlZemd5TFRRelptTXRPRFl5Tmkwek5EVTJZekUzT0dOaE1HWWlMQ0owZVhCbElqb2lRbUZ6YVdOVWFXTnJaWElpZlgwc0ltbGtJam9pTldRME5EVTJZalV0T1dKaE1TMDBaV0ZoTFRoa05EZ3ROelpqWW1KbVpHRTNNekJrSWl3aWRIbHdaU0k2SWtkeWFXUWlmU3g3SW1GMGRISnBZblYwWlhNaU9uc2ljMjkxY21ObElqcDdJbWxrSWpvaVptSXdNRFE1TkRndFlUUTBZeTAwWm1FM0xUa3lObVF0TlRZNE16QTVZMkpqT0Raaklpd2lkSGx3WlNJNklrTnZiSFZ0YmtSaGRHRlRiM1Z5WTJVaWZYMHNJbWxrSWpvaU16QmpNVGc0WkRRdE0yTXlPQzAwT1RnM0xXRXdPRGN0WXpkaE1tVXdORGMwTmpobUlpd2lkSGx3WlNJNklrTkVVMVpwWlhjaWZTeDdJbUYwZEhKcFluVjBaWE1pT25zaVptOXliV0YwZEdWeUlqcDdJbWxrSWpvaVlUZG1OVFUwWVRNdE1HSTNZaTAwWmpCakxXRmxNak10TlRBek5HVTVNMlEzTWpVd0lpd2lkSGx3WlNJNklrUmhkR1YwYVcxbFZHbGphMFp2Y20xaGRIUmxjaUo5TENKd2JHOTBJanA3SW1sa0lqb2lNR0ZtWVRZeU0ySXRNamxqTWkwME16WmhMVGhrWlRNdFpUUTVPVGhpTkRreFlURTBJaXdpYzNWaWRIbHdaU0k2SWtacFozVnlaU0lzSW5SNWNHVWlPaUpRYkc5MEluMHNJblJwWTJ0bGNpSTZleUpwWkNJNklqQmhOakUwTldWbExUVTROekV0TkdRNU1DMDRaRGMzTFRGaE1UYzRZak0xTVRGa1ppSXNJblI1Y0dVaU9pSkVZWFJsZEdsdFpWUnBZMnRsY2lKOWZTd2lhV1FpT2lKaVlXVXlaV0V3TWkxbU5EazBMVFJsWldFdE9XUmlZeTAwWkdRNVkyWmlOREJpTTJJaUxDSjBlWEJsSWpvaVJHRjBaWFJwYldWQmVHbHpJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbk52ZFhKalpTSTZleUpwWkNJNklqa3daVEJqTURneExXWTBOelV0TkRVME1pMDRaRFpqTFRsbVpqTXhNVGM1TkRCbE1pSXNJblI1Y0dVaU9pSkRiMngxYlc1RVlYUmhVMjkxY21ObEluMTlMQ0pwWkNJNklqaGhOemhpT1RZMkxXRXpOREV0TkRreU5pMDVOREk1TFdaak5qY3dNR0UxTURjd01pSXNJblI1Y0dVaU9pSkRSRk5XYVdWM0luMHNleUpoZEhSeWFXSjFkR1Z6SWpwN0luTnZkWEpqWlNJNmV5SnBaQ0k2SWpReU9XUmpOell3TFdZNVkyRXROR1JrTlMwNFl6UXpMV0pqT0RCaVl6bGtPRE0zTUNJc0luUjVjR1VpT2lKRGIyeDFiVzVFWVhSaFUyOTFjbU5sSW4xOUxDSnBaQ0k2SWpkalptRmxPREZqTFdJNU4yVXROR1ZoWWkwNE5UazRMV1ptWVRReE16UXlaRFU0TXlJc0luUjVjR1VpT2lKRFJGTldhV1YzSW4wc2V5SmhkSFJ5YVdKMWRHVnpJanA3SW1KaGMyVWlPakkwTENKdFlXNTBhWE56WVhNaU9sc3hMRElzTkN3MkxEZ3NNVEpkTENKdFlYaGZhVzUwWlhKMllXd2lPalF6TWpBd01EQXdMakFzSW0xcGJsOXBiblJsY25aaGJDSTZNell3TURBd01DNHdMQ0p1ZFcxZmJXbHViM0pmZEdsamEzTWlPakI5TENKcFpDSTZJbUV6WkRKaE1qazRMV1JoWXpndE5HWXlaUzFpTURVNUxUQXdOMkl6TVRZM09HVmtOQ0lzSW5SNWNHVWlPaUpCWkdGd2RHbDJaVlJwWTJ0bGNpSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SmpZV3hzWW1GamF5STZiblZzYkN3aWNtVnVaR1Z5WlhKeklqcGJleUpwWkNJNkltSmlOREk0WldNd0xUZGtNV1l0TkRnek1TMDRNV05pTFdNME9HVTJZV0l6WW1ZMlppSXNJblI1Y0dVaU9pSkhiSGx3YUZKbGJtUmxjbVZ5SW4xZExDSjBiMjlzZEdsd2N5STZXMXNpVG1GdFpTSXNJa2haUTA5TklsMHNXeUpDYVdGeklpd2lMVEF1TVRjaVhTeGJJbE5yYVd4c0lpd2lNQzR4T1NKZFhYMHNJbWxrSWpvaVlUWmlZamsyTURNdE5URXhPQzAwWVROaExXSmlZamN0T1dSbE1tSTRZamMyWXpBMElpd2lkSGx3WlNJNklraHZkbVZ5Vkc5dmJDSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmV5SnNZV0psYkNJNmV5SjJZV3gxWlNJNkltUm9kMTgxYTIwaWZTd2ljbVZ1WkdWeVpYSnpJanBiZXlKcFpDSTZJbUZrWldReU5qSmpMV0ZpWXpBdE5ERXpZeTA1WldGa0xXTTRZV0l4TnpJNU5HWm1OaUlzSW5SNWNHVWlPaUpIYkhsd2FGSmxibVJsY21WeUluMWRmU3dpYVdRaU9pSmlNVFE0Tm1Ga09TMDVNVE0wTFRReU5qUXRZVEUyWXkxall6WmxZelV4TkRVME5qWWlMQ0owZVhCbElqb2lUR1ZuWlc1a1NYUmxiU0o5TEhzaVlYUjBjbWxpZFhSbGN5STZleUprWVhSaFgzTnZkWEpqWlNJNmV5SnBaQ0k2SW1SbVlXSmpORGszTFRRNFl6QXROREpqTVMxaU56VmxMV1k1TmpGbVpHUTFObVF3T0NJc0luUjVjR1VpT2lKRGIyeDFiVzVFWVhSaFUyOTFjbU5sSW4wc0ltZHNlWEJvSWpwN0ltbGtJam9pT0RVM1lUVTVabUl0WXpJMU5DMDBPR000TFRsbU9EY3RNamc1TXpJM01HRmlPVE00SWl3aWRIbHdaU0k2SWt4cGJtVWlmU3dpYUc5MlpYSmZaMng1Y0dnaU9tNTFiR3dzSW0xMWRHVmtYMmRzZVhCb0lqcHVkV3hzTENKdWIyNXpaV3hsWTNScGIyNWZaMng1Y0dnaU9uc2lhV1FpT2lJMVlUWXdOamN6TnkxaU16VTVMVFE0TWpJdFlqTm1OaTB5WkdZMk5HRmlZakl5TURNaUxDSjBlWEJsSWpvaVRHbHVaU0o5TENKelpXeGxZM1JwYjI1ZloyeDVjR2dpT201MWJHd3NJblpwWlhjaU9uc2lhV1FpT2lKa1ltRm1ZbUU0T1MwMU9ERTVMVFJsWkRVdE9XTTFZeTAxTnpaaFlqTmhNR0poWkdRaUxDSjBlWEJsSWpvaVEwUlRWbWxsZHlKOWZTd2lhV1FpT2lKbU9EWTRZbVU1TUMweFpHVXhMVFJtTkRVdFltTmtPUzB5TkRrME9EVXlObVl4T0dVaUxDSjBlWEJsSWpvaVIyeDVjR2hTWlc1a1pYSmxjaUo5TEhzaVlYUjBjbWxpZFhSbGN5STZleUpzWVdKbGJDSTZleUoyWVd4MVpTSTZJa2haUTA5TkluMHNJbkpsYm1SbGNtVnljeUk2VzNzaWFXUWlPaUppWWpReU9HVmpNQzAzWkRGbUxUUTRNekV0T0RGallpMWpORGhsTm1GaU0ySm1ObVlpTENKMGVYQmxJam9pUjJ4NWNHaFNaVzVrWlhKbGNpSjlYWDBzSW1sa0lqb2lOREppWkRBM05UWXRNRFZrWXkwME1EQmtMVGt6WVRVdE1HTXhaRFF3TXpaaVpHRXhJaXdpZEhsd1pTSTZJa3hsWjJWdVpFbDBaVzBpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpWW05MGRHOXRYM1Z1YVhSeklqb2ljMk55WldWdUlpd2labWxzYkY5aGJIQm9ZU0k2ZXlKMllXeDFaU0k2TUM0MWZTd2labWxzYkY5amIyeHZjaUk2ZXlKMllXeDFaU0k2SW14cFoyaDBaM0psZVNKOUxDSnNaV1owWDNWdWFYUnpJam9pYzJOeVpXVnVJaXdpYkdWMlpXd2lPaUp2ZG1WeWJHRjVJaXdpYkdsdVpWOWhiSEJvWVNJNmV5SjJZV3gxWlNJNk1TNHdmU3dpYkdsdVpWOWpiMnh2Y2lJNmV5SjJZV3gxWlNJNkltSnNZV05ySW4wc0lteHBibVZmWkdGemFDSTZXelFzTkYwc0lteHBibVZmZDJsa2RHZ2lPbnNpZG1Gc2RXVWlPako5TENKd2JHOTBJanB1ZFd4c0xDSnlaVzVrWlhKZmJXOWtaU0k2SW1OemN5SXNJbkpwWjJoMFgzVnVhWFJ6SWpvaWMyTnlaV1Z1SWl3aWRHOXdYM1Z1YVhSeklqb2ljMk55WldWdUluMHNJbWxrSWpvaVpEWTVOMk14WW1FdE9UUTFOaTAwTTJSaUxXRXpZVGN0T0RSbFltSmlZVGcyT1dJeUlpd2lkSGx3WlNJNklrSnZlRUZ1Ym05MFlYUnBiMjRpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpYkdsdVpWOWpZWEFpT2lKeWIzVnVaQ0lzSW14cGJtVmZZMjlzYjNJaU9pSmpjbWx0YzI5dUlpd2liR2x1WlY5cWIybHVJam9pY205MWJtUWlMQ0pzYVc1bFgzZHBaSFJvSWpvMUxDSjRJanA3SW1acFpXeGtJam9pZUNKOUxDSjVJanA3SW1acFpXeGtJam9pZVNKOWZTd2lhV1FpT2lJMVpqazFZV1psWkMxa05XSTNMVFEzTnpBdFltUTNZeTB5TjJJeE9XRXpaVGMwTnpnaUxDSjBlWEJsSWpvaVRHbHVaU0o5TEhzaVlYUjBjbWxpZFhSbGN5STZleUp0YjI1MGFITWlPbHN3TERJc05DdzJMRGdzTVRCZGZTd2lhV1FpT2lJek0ySTVZV1JpTXkwMU5HWTFMVFJoTTJZdFltWmhZUzFsWlRnM1l6VTBOR014TkRFaUxDSjBlWEJsSWpvaVRXOXVkR2h6VkdsamEyVnlJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbU5oYkd4aVlXTnJJanB1ZFd4c0xDSmpiMngxYlc1ZmJtRnRaWE1pT2xzaWVDSXNJbmtpWFN3aVpHRjBZU0k2ZXlKNElqcDdJbDlmYm1SaGNuSmhlVjlmSWpvaVFVRkJRVGxMZDJKa2EwbEJRVTlvYVhOQ2RESlJaMEZCTUU1SGVrY3pXa05CUVVSQlYyWTRZbVJyU1VGQlMycEpRV2g0TWxGblFVRnJSR05IU0VoYVEwRkJRMEYyTVVWalpHdEpRVUZIWjNWV1VuZ3lVV2RCUVZWS01WbElTRnBEUVVGQ1FVcGhVV05rYTBsQlFVTnBWWEI0ZURKUlowRkJSVUZQY2toSVdrTkJRVUZCYVM5WlkyUnJTVUZCVDJvMUsxSjRNbEZuUVVFd1IybzVTRWhhUTBGQlJFRTRSV2RrWkd0SlFVRkxhR1pVUWpFeVVXZEJRV3ROTlZCSVdGcERRVUZEUVZad2MyUmthMGxCUVVkcVJtNW9NVEpSWjBGQlZVUlRhVWhZV2tOQlFVSkJkazh3WkdSclNVRkJRMmR5T0ZJeE1sRm5RVUZGU25Jd1NGaGFRMEZCUVVGSmEwRmxaR3RKUVVGUGFWRlJlRFV5VVdkQlFUQlFPVWRJYmxwRElpd2laSFI1Y0dVaU9pSm1iRzloZERZMElpd2ljMmhoY0dVaU9sc3lOMTE5TENKNUlqcDdJbDlmYm1SaGNuSmhlVjlmSWpvaVFVRkJRV2RHZWtKRlZVRkJRVUZFWjBaalFWSlJRVUZCUVVORVVIWm9Sa0ZCUVVGQloweDVhVVZWUVVGQlFVRkJObkJ6VWxGQlFVRkJTVUZZYkZKR1FVRkJRVUZuUVVRdlJVVkJRVUZCUkdkU2FGVlNVVUZCUVVGRlEwNUxlRVpCUVVGQlFXOUthMVpGTUVGQlFVRkNRVGRuVFZSUlFVRkJRVUZDUkRob1NrRkJRVUZCUVVsd2RFVlZRVUZCUVVSQmFXMHdVbEZCUVVGQlMwTk1ZbEpHUVVGQlFVRTBTbmgwUlZWQlFVRkJRa0ZxTWpCU1VVRkJRVUZMUTBKaVVrWkJRVUZCUVZsR1duTkZWVUZCUVVGRVFWTnVPRkpSUVVGQlFVVkJMMnRvUmtGQlFVRkJaMFZCZWtVd1FVRkJRVUpuWTBOTlZGRkJRVUZCUjBOblJYaE9RVUZCUVVGWlREWXpSVlZCUVVGQlFtZDJjbU5TVVVGQlFVRkhReXQwZUVaQklpd2laSFI1Y0dVaU9pSm1iRzloZERZMElpd2ljMmhoY0dVaU9sc3lOMTE5Zlgwc0ltbGtJam9pTkRJNVpHTTNOakF0WmpsallTMDBaR1ExTFRoak5ETXRZbU00TUdKak9XUTRNemN3SWl3aWRIbHdaU0k2SWtOdmJIVnRia1JoZEdGVGIzVnlZMlVpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpYkdsdVpWOWhiSEJvWVNJNk1DNHhMQ0pzYVc1bFgyTmhjQ0k2SW5KdmRXNWtJaXdpYkdsdVpWOWpiMnh2Y2lJNklpTXhaamMzWWpRaUxDSnNhVzVsWDJwdmFXNGlPaUp5YjNWdVpDSXNJbXhwYm1WZmQybGtkR2dpT2pVc0luZ2lPbnNpWm1sbGJHUWlPaUo0SW4wc0lua2lPbnNpWm1sbGJHUWlPaUo1SW4xOUxDSnBaQ0k2SWpsak9ETXlZbUUyTFRrMU16TXRORGMyWkMwNU5XTmxMV0kzWVRJNFkyUTROR1JtTnlJc0luUjVjR1VpT2lKTWFXNWxJbjBzZXlKaGRIUnlhV0oxZEdWeklqcDdJbTkyWlhKc1lYa2lPbnNpYVdRaU9pSmtOamszWXpGaVlTMDVORFUyTFRRelpHSXRZVE5oTnkwNE5HVmlZbUpoT0RZNVlqSWlMQ0owZVhCbElqb2lRbTk0UVc1dWIzUmhkR2x2YmlKOWZTd2lhV1FpT2lJNE1XUTJNakUxWkMwek5EWXdMVFJqTlRBdE9XSTVZUzB4TTJNMU9HWmpNMkV4WVdFaUxDSjBlWEJsSWpvaVFtOTRXbTl2YlZSdmIyd2lmU3g3SW1GMGRISnBZblYwWlhNaU9uc2lhWFJsYlhNaU9sdDdJbWxrSWpvaU16Tm1NV1U1WkRBdFpXSTNOQzAwTVdVNUxUa3lOekF0WkRRNE5URTJObVF3TWpkaElpd2lkSGx3WlNJNklreGxaMlZ1WkVsMFpXMGlmU3g3SW1sa0lqb2lNVFEyWlRGbU5EUXRZMll4WWkwME1qSXdMV0l3TldNdE5UUTBNMkZrTTJWbE9EYzBJaXdpZEhsd1pTSTZJa3hsWjJWdVpFbDBaVzBpZlN4N0ltbGtJam9pWWpFME9EWmhaRGt0T1RFek5DMDBNalkwTFdFeE5tTXRZMk0yWldNMU1UUTFORFkySWl3aWRIbHdaU0k2SWt4bFoyVnVaRWwwWlcwaWZTeDdJbWxrSWpvaU5ESmlaREEzTlRZdE1EVmtZeTAwTURCa0xUa3pZVFV0TUdNeFpEUXdNelppWkdFeElpd2lkSGx3WlNJNklreGxaMlZ1WkVsMFpXMGlmVjBzSW5Cc2IzUWlPbnNpYVdRaU9pSXdZV1poTmpJellpMHlPV015TFRRek5tRXRPR1JsTXkxbE5EazVPR0kwT1RGaE1UUWlMQ0p6ZFdKMGVYQmxJam9pUm1sbmRYSmxJaXdpZEhsd1pTSTZJbEJzYjNRaWZYMHNJbWxrSWpvaU5qQTBaRGhsTldJdFpEVmxaUzAwTVRkakxUazVObUV0TnpZMU5tUXpOek00T0dJeElpd2lkSGx3WlNJNklreGxaMlZ1WkNKOUxIc2lZWFIwY21saWRYUmxjeUk2ZXlKc2FXNWxYMkZzY0doaElqb3dMakVzSW14cGJtVmZZMkZ3SWpvaWNtOTFibVFpTENKc2FXNWxYMk52Ykc5eUlqb2lJekZtTnpkaU5DSXNJbXhwYm1WZmFtOXBiaUk2SW5KdmRXNWtJaXdpYkdsdVpWOTNhV1IwYUNJNk5Td2llQ0k2ZXlKbWFXVnNaQ0k2SW5naWZTd2llU0k2ZXlKbWFXVnNaQ0k2SW5raWZYMHNJbWxrSWpvaU1XSmhaVFExT1RVdE0yRm1ZaTAwWWpReUxXRXhabU10WVRSbE1UVmlPR0UxTWpKa0lpd2lkSGx3WlNJNklreHBibVVpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpWkdGMFlWOXpiM1Z5WTJVaU9uc2lhV1FpT2lJME1qbGtZemMyTUMxbU9XTmhMVFJrWkRVdE9HTTBNeTFpWXpnd1ltTTVaRGd6TnpBaUxDSjBlWEJsSWpvaVEyOXNkVzF1UkdGMFlWTnZkWEpqWlNKOUxDSm5iSGx3YUNJNmV5SnBaQ0k2SW1VNU1HTXhZakl4TFRSallUSXRORFUwWmkxaVpqVTVMV1UwTm1JMFpETXdPRFppWVNJc0luUjVjR1VpT2lKTWFXNWxJbjBzSW1odmRtVnlYMmRzZVhCb0lqcHVkV3hzTENKdGRYUmxaRjluYkhsd2FDSTZiblZzYkN3aWJtOXVjMlZzWldOMGFXOXVYMmRzZVhCb0lqcDdJbWxrSWpvaU1XSmhaVFExT1RVdE0yRm1ZaTAwWWpReUxXRXhabU10WVRSbE1UVmlPR0UxTWpKa0lpd2lkSGx3WlNJNklreHBibVVpZlN3aWMyVnNaV04wYVc5dVgyZHNlWEJvSWpwdWRXeHNMQ0oyYVdWM0lqcDdJbWxrSWpvaU4yTm1ZV1U0TVdNdFlqazNaUzAwWldGaUxUZzFPVGd0Wm1aaE5ERXpOREprTlRneklpd2lkSGx3WlNJNklrTkVVMVpwWlhjaWZYMHNJbWxrSWpvaVltSTBNamhsWXpBdE4yUXhaaTAwT0RNeExUZ3hZMkl0WXpRNFpUWmhZak5pWmpabUlpd2lkSGx3WlNJNklrZHNlWEJvVW1WdVpHVnlaWElpZlN4N0ltRjBkSEpwWW5WMFpYTWlPbnNpWkdGNWN5STZXekVzTVRWZGZTd2lhV1FpT2lKak5tUm1abVk1TnkwNE9EQmpMVFF4WVRVdFlqVXlPQzAwT0RFeVlXUTVOelJsTURFaUxDSjBlWEJsSWpvaVJHRjVjMVJwWTJ0bGNpSjlMSHNpWVhSMGNtbGlkWFJsY3lJNmUzMHNJbWxrSWpvaU16Qm1aR1k0WWpRdE9XRTFOaTAwWkRWbExUZ3dZVFF0T1RVNFpqYzJOelJoTTJGbUlpd2lkSGx3WlNJNklsQmhibFJ2YjJ3aWZWMHNJbkp2YjNSZmFXUnpJanBiSWpCaFptRTJNak5pTFRJNVl6SXRORE0yWVMwNFpHVXpMV1UwT1RrNFlqUTVNV0V4TkNKZGZTd2lkR2wwYkdVaU9pSkNiMnRsYUNCQmNIQnNhV05oZEdsdmJpSXNJblpsY25OcGIyNGlPaUl3TGpFeUxqRXpJbjE5Q2lBZ0lDQWdJQ0FnUEM5elkzSnBjSFErQ2lBZ0lDQWdJQ0FnUEhOamNtbHdkQ0IwZVhCbFBTSjBaWGgwTDJwaGRtRnpZM0pwY0hRaVBnb2dJQ0FnSUNBZ0lDQWdLR1oxYm1OMGFXOXVLQ2tnZXdvZ0lDQWdJQ0FnSUNBZ0lDQjJZWElnWm00Z1BTQm1kVzVqZEdsdmJpZ3BJSHNLSUNBZ0lDQWdJQ0FnSUNBZ0lDQkNiMnRsYUM1ellXWmxiSGtvWm5WdVkzUnBiMjRvS1NCN0NpQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBb1puVnVZM1JwYjI0b2NtOXZkQ2tnZXdvZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNCbWRXNWpkR2x2YmlCbGJXSmxaRjlrYjJOMWJXVnVkQ2h5YjI5MEtTQjdDaUFnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnQ2lBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUhaaGNpQmtiMk56WDJwemIyNGdQU0JrYjJOMWJXVnVkQzVuWlhSRmJHVnRaVzUwUW5sSlpDZ25aRGMwTW1Ga09EWXRNMlV5TVMwME4yUmtMV0poWXprdE1UQTJaRFV6WmpVellXUTRKeWt1ZEdWNGRFTnZiblJsYm5RN0NpQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lIWmhjaUJ5Wlc1a1pYSmZhWFJsYlhNZ1BTQmJleUprYjJOcFpDSTZJalppTldSaFkySTNMVFJsTVdZdE5HRmxOUzFoWm1Oa0xXUTJPR1UyTm1ZMlpUSmtaU0lzSW1Wc1pXMWxiblJwWkNJNkltUTFZVGRpTURaaExUSTNaR1F0TkRaaVppMDVOelV3TFdSbE1HWTNNMlUwT1dJNU5pSXNJbTF2WkdWc2FXUWlPaUl3WVdaaE5qSXpZaTB5T1dNeUxUUXpObUV0T0dSbE15MWxORGs1T0dJME9URmhNVFFpZlYwN0NpQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lISnZiM1F1UW05clpXZ3VaVzFpWldRdVpXMWlaV1JmYVhSbGJYTW9aRzlqYzE5cWMyOXVMQ0J5Wlc1a1pYSmZhWFJsYlhNcE93b2dJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0NpQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lIMEtJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdhV1lnS0hKdmIzUXVRbTlyWldnZ0lUMDlJSFZ1WkdWbWFXNWxaQ2tnZXdvZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lHVnRZbVZrWDJSdlkzVnRaVzUwS0hKdmIzUXBPd29nSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0I5SUdWc2MyVWdld29nSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUhaaGNpQmhkSFJsYlhCMGN5QTlJREE3Q2lBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ2RtRnlJSFJwYldWeUlEMGdjMlYwU1c1MFpYSjJZV3dvWm5WdVkzUnBiMjRvY205dmRDa2dld29nSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ2FXWWdLSEp2YjNRdVFtOXJaV2dnSVQwOUlIVnVaR1ZtYVc1bFpDa2dld29nSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQmxiV0psWkY5a2IyTjFiV1Z1ZENoeWIyOTBLVHNLSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdZMnhsWVhKSmJuUmxjblpoYkNoMGFXMWxjaWs3Q2lBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQjlDaUFnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNCaGRIUmxiWEIwY3lzck93b2dJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnYVdZZ0tHRjBkR1Z0Y0hSeklENGdNVEF3S1NCN0NpQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUdOdmJuTnZiR1V1Ykc5bktDSkNiMnRsYURvZ1JWSlNUMUk2SUZWdVlXSnNaU0IwYnlCeWRXNGdRbTlyWldoS1V5QmpiMlJsSUdKbFkyRjFjMlVnUW05clpXaEtVeUJzYVdKeVlYSjVJR2x6SUcxcGMzTnBibWNpS1FvZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0JqYkdWaGNrbHVkR1Z5ZG1Gc0tIUnBiV1Z5S1RzS0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJSDBLSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdJQ0FnSUNCOUxDQXhNQ3dnY205dmRDa0tJQ0FnSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdmUW9nSUNBZ0lDQWdJQ0FnSUNBZ0lDQWdmU2tvZDJsdVpHOTNLVHNLSUNBZ0lDQWdJQ0FnSUNBZ0lDQjlLVHNLSUNBZ0lDQWdJQ0FnSUNBZ2ZUc0tJQ0FnSUNBZ0lDQWdJQ0FnYVdZZ0tHUnZZM1Z0Wlc1MExuSmxZV1I1VTNSaGRHVWdJVDBnSW14dllXUnBibWNpS1NCbWJpZ3BPd29nSUNBZ0lDQWdJQ0FnSUNCbGJITmxJR1J2WTNWdFpXNTBMbUZrWkVWMlpXNTBUR2x6ZEdWdVpYSW9Ja1JQVFVOdmJuUmxiblJNYjJGa1pXUWlMQ0JtYmlrN0NpQWdJQ0FnSUNBZ0lDQjlLU2dwT3dvZ0lDQWdJQ0FnSUR3dmMyTnlhWEIwUGdvZ0lDQWdQQzlpYjJSNVBnbzhMMmgwYld3KyIgd2lkdGg9Ijc5MCIgc3R5bGU9ImJvcmRlcjpub25lICFpbXBvcnRhbnQ7IiBoZWlnaHQ9IjMzMCI+PC9pZnJhbWU+JylbMF07CiAgICAgICAgICAgICAgICBwb3B1cF8zYWQ1NDM3YjFjY2Q0MmY2OTYxZjk4ZTVkMTAyMzE1My5zZXRDb250ZW50KGlfZnJhbWVfZGIxMDI0ZmQ5ODg4NDMxY2FkMWU1NzZmZWVjMjE4MzMpOwogICAgICAgICAgICAKCiAgICAgICAgICAgIG1hcmtlcl9mNjZjNWJkNTRmNzM0MTg3YjdiM2RlYWFmNDY3MjQ5Mi5iaW5kUG9wdXAocG9wdXBfM2FkNTQzN2IxY2NkNDJmNjk2MWY5OGU1ZDEwMjMxNTMpOwoKICAgICAgICAgICAgCiAgICAgICAgCiAgICAKICAgICAgICAgICAgdmFyIGxheWVyX2NvbnRyb2xfMTM5MmI2ZjIzNTgxNDgzMTlhNDE0MmQzZmUwMDZhMDQgPSB7CiAgICAgICAgICAgICAgICBiYXNlX2xheWVycyA6IHsgIm9wZW5zdHJlZXRtYXAiIDogdGlsZV9sYXllcl8zZTJkNTcwZDFjYjg0MzhmODZhYzBhODQ1ZGM0ODQ2YSwgfSwKICAgICAgICAgICAgICAgIG92ZXJsYXlzIDogeyAiU2VhIFN1cmZhY2UgVGVtcGVyYXR1cmUiIDogbWFjcm9fZWxlbWVudF9mMmQzODYzOWEyNDE0MDU5OWM0ZjIxMmQwNGVmZmU2NiwiQ2x1c3RlciIgOiBtYXJrZXJfY2x1c3Rlcl8yMzMyODg2ZGRlNGU0NTI1OTgzNTdhMDE5ZWExNjAzZSwgfQogICAgICAgICAgICAgICAgfTsKICAgICAgICAgICAgTC5jb250cm9sLmxheWVycygKICAgICAgICAgICAgICAgIGxheWVyX2NvbnRyb2xfMTM5MmI2ZjIzNTgxNDgzMTlhNDE0MmQzZmUwMDZhMDQuYmFzZV9sYXllcnMsCiAgICAgICAgICAgICAgICBsYXllcl9jb250cm9sXzEzOTJiNmYyMzU4MTQ4MzE5YTQxNDJkM2ZlMDA2YTA0Lm92ZXJsYXlzLAogICAgICAgICAgICAgICAge3Bvc2l0aW9uOiAndG9wcmlnaHQnLAogICAgICAgICAgICAgICAgIGNvbGxhcHNlZDogdHJ1ZSwKICAgICAgICAgICAgICAgICBhdXRvWkluZGV4OiB0cnVlCiAgICAgICAgICAgICAgICB9KS5hZGRUbyhtYXBfZWQ4Yjk0MGMxZjM4NDU1ZGJhOGYyZmM1YjRlYWJlYTApOwogICAgICAgIAo8L3NjcmlwdD4=" style="position:absolute;width:100%;height:100%;left:0;top:0;border:none !important;" allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe></div></div>



Now we can navigate the map and click on the markers to explorer our findings.

The green markers locate the observations locations. They pop-up an interactive plot with the time-series and scores for the models (hover over the lines to se the scores). The blue markers indicate the nearest model grid point found for the comparison.
<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2016-12-22-boston_light_swim.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2016-12-22-boston_light_swim.ipynb) to run a live instance of this notebook.