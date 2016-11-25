---
layout: notebook
title: ""
---


<img style='float: left' width="150px" src="http://bostonlightswim.org/wp/wp-
content/uploads/2011/08/BLS-front_4-color.jpg">
<br><br>

## [The Boston Light Swim](http://bostonlightswim.org/)

### Fetch Sea Surface Temperature time-series data

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import os
import sys
import time
import warnings

ioos_tools = os.path.join(os.path.pardir, os.path.pardir)
sys.path.append(ioos_tools)

# Suppresing warnings for a "pretty output."
# Remove this line to debug any possible issues.
warnings.simplefilter("ignore")

start_time = time.time()
```

### Configuration

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
    - http://www.ngdc.noaa.gov/geoportal/csw
    - https://dev-catalog.ioos.us/csw
    - http://geoport.whoi.edu/csw

# See https://raw.githubusercontent.com/OSGeo/Cat-Interop/master/LinkPropertyLookupTable.csv
service_strings:
    opendap:
        - OPeNDAP:OPeNDAP
        - urn:x-esri:specification:ServiceType:odp:url
    sos:
        - urn:x-esri:specification:ServiceType:sos:url
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Overwriting config.yaml

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
from datetime import datetime
from ioos_tools.ioos import parse_config

config = parse_config('config.yaml')

save_dir = os.path.abspath(config['run_name'])


def _reload_log():
    """IPython workaround."""
    import imp
    import logging as log
    imp.reload(log)
    return log


def start_log(save_dir):
    import shutil
    log = _reload_log()
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)

    log.captureWarnings(True)
    LOG_FILENAME = 'log.txt'
    LOG_FILENAME = os.path.join(save_dir, LOG_FILENAME)
    formatter = '%(asctime)s %(levelname)s: %(message)s'
    log.basicConfig(filename=LOG_FILENAME,
                    filemode='w',
                    format=formatter,
                    datefmt='%I:%M:%S',
                    level=log.INFO)
    return log

log = start_log(save_dir)
fmt = '{:*^64}'.format
log.info(fmt('Saving data inside directory {}'.format(save_dir)))
log.info(fmt(' Run information '))
log.info('Run date: {:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow()))
log.info('Start: {:%Y-%m-%d %H:%M:%S}'.format(config['date']['start']))
log.info('Stop: {:%Y-%m-%d %H:%M:%S}'.format(config['date']['stop']))
log.info('Bounding box: {0:3.2f}, {1:3.2f},'
         '{2:3.2f}, {3:3.2f}'.format(*config['region']['bbox']))
```

### Create the data filter

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

    # Exclude ROMS Averages and History files.
    not_filt = fes.Not([fes.PropertyIsLike(literal='*Averages*', **kw)])

    begin, end = fes_date_filter(config['date']['start'],
                                 config['date']['stop'])
    bbox_crs = fes.BBox(config['region']['bbox'],
                        crs=config['region']['crs'])
    return [fes.And([bbox_crs, begin, end, or_filt, not_filt])]

filter_list = make_filter(config)
```

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
from ioos_tools.ioos import service_urls
from owslib.csw import CatalogueServiceWeb

# Logging info.
fmt = '{:*^64}'.format
log.info(fmt(' Catalog information '))

# Check for the strings at
# https://raw.githubusercontent.com/OSGeo/Cat-Interop/master/LinkPropertyLookupTable.csv
opendap_strings = config['service_strings']['opendap']
sos_strings = config['service_strings']['sos']

dap_urls = []
sos_urls = []
for endpoint in config['catalogs']:
    log.info(fmt(' CSW '))
    log.info("URL: {}".format(endpoint))

    csw = CatalogueServiceWeb(endpoint, timeout=120)
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
    dap = service_urls(csw.records, services=opendap_strings)
    sos = service_urls(csw.records, services=sos_strings)
    dap_urls.extend(dap)
    sos_urls.extend(sos)

    log.info("CSW version: {}".format(csw.version))
    log.info("Number of datasets available: {}".format(len(csw.records.keys())))

    for rec, item in csw.records.items():
        log.info('{}'.format(item.title))
    if sos:
        log.info(fmt(' SOS '))
        for url in sos:
            log.info('{}'.format(url))
    if dap:
        log.info(fmt(' DAP '))
        for url in dap:
            log.info('{}.html'.format(url))

# Get only unique endpoints.
dap_urls = list(set(dap_urls))
sos_urls = list(set(sos_urls))
```

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
from ioos_tools.ioos import is_station

# Filter out some station endpoints.
non_stations = []
for url in dap_urls:
    try:
        if not is_station(url):
            non_stations.append(url)
    except (RuntimeError, OSError) as e:
        log.warn("Could not access URL {}. {!r}".format(url, e))

dap_urls = non_stations

log.info(fmt(' Filtered DAP '))
for url in dap_urls:
    log.info('{}.html'.format(url))
```

### NdbcSos

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
log.info(fmt(' NDBC Collector offerings '))
log.info('{}: {} offerings'.format(title, len(ofrs)))
```

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
import pandas as pd
from ioos_tools.ioos import collector2table, to_html

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
to_html(table)
```




<style>.info {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.success {
    background-color:#d9edf7;
    border-color:#bce8f1;
    border-left:5px solid #31708f;
    padding:.5em;
    color:#31708f
}

.error {
    background-color:#f2dede;
    border-color:#ebccd1;
    border-left:5px solid #a94442;
    padding:.5em;
    color:#a94442
}

.warning {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.text-shadow {
    text-shadow:0 1px 0 #ccc,0 2px 0 #c9c9c9,0 3px 0 #bbb,0 4px 0 #b9b9b9,0 5px 0 #aaa,0 6px 1px rgba(0,0,0,.1)
}

.datagrid table {
    border-collapse:collapse;
    text-align:left;
    width:65%
}

.datagrid td {
    border-collapse:collapse;
    text-align:right;
}

.datagrid {
    font:normal 12px/150% Arial,Helvetica,sans-serif;
    background:#fff;
    overflow:hidden;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px
}

.datagrid table td,.datagrid table th {
    padding:3px 10px
}

.datagrid table thead th {
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069;
    color:#FFF;
    font-size:15px;
    font-weight:700;
    border-left:1px solid #0070A8
}

.datagrid table thead th:first-child {
    border:none
}

.datagrid table tbody td {
    color:#00496B;
    border-left:1px solid #E1EEF4;
    font-size:12px;
    font-weight:400
}

.datagrid table tbody .alt td {
    background:#E1EEF4;
    color:#00496B
}

.datagrid table tbody td:first-child {
    border-left:none
}

.datagrid table tbody tr:last-child td {
    border-bottom:none
}

.datagrid table tfoot td div {
    border-top:1px solid #069;
    background:#E1EEF4
}

.datagrid table tfoot td {
    padding:0;
    font-size:12px
}

.datagrid table tfoot td div {
    padding:2px
}

.datagrid table tfoot td ul {
    margin:0;
    padding:0;
    list-style:none;
    text-align:right
}

.datagrid table tfoot li {
    display:inline
}

.datagrid table tfoot li a {
    text-decoration:none;
    display:inline-block;
    padding:2px 8px;
    margin:1px;
    color:#FFF;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px;
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069
}

.datagrid table tfoot ul.active,.datagrid table tfoot ul a:hover {
    text-decoration:none;
    border-color:#069;
    color:#FFF;
    background:none;
    background-color:#00557F
}

div.dhtmlx_window_active,div.dhx_modal_cover_dv {
    position:fixed!important
}
</style><div class="datagrid"><table border="1" class="dataframe">
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
      <td>42.35</td>
      <td>-70.69</td>
      <td>urn:ioos:sensor:wmo:44013::watertemp1</td>
      <td>BOSTON 16 NM East of Boston, MA</td>
    </tr>
    <tr>
      <th>44029</th>
      <td>1.0</td>
      <td>42.52</td>
      <td>-70.57</td>
      <td>urn:ioos:sensor:wmo:44029::ct1</td>
      <td>Buoy A0102 - Mass. Bay/Stellwagen</td>
    </tr>
  </tbody>
</table></div>



### CoopsSoS

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
log.info(fmt(' Collector offerings '))
log.info('{}: {} offerings'.format(title, len(ofrs)))
```

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
to_html(table)
```




<style>.info {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.success {
    background-color:#d9edf7;
    border-color:#bce8f1;
    border-left:5px solid #31708f;
    padding:.5em;
    color:#31708f
}

.error {
    background-color:#f2dede;
    border-color:#ebccd1;
    border-left:5px solid #a94442;
    padding:.5em;
    color:#a94442
}

.warning {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.text-shadow {
    text-shadow:0 1px 0 #ccc,0 2px 0 #c9c9c9,0 3px 0 #bbb,0 4px 0 #b9b9b9,0 5px 0 #aaa,0 6px 1px rgba(0,0,0,.1)
}

.datagrid table {
    border-collapse:collapse;
    text-align:left;
    width:65%
}

.datagrid td {
    border-collapse:collapse;
    text-align:right;
}

.datagrid {
    font:normal 12px/150% Arial,Helvetica,sans-serif;
    background:#fff;
    overflow:hidden;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px
}

.datagrid table td,.datagrid table th {
    padding:3px 10px
}

.datagrid table thead th {
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069;
    color:#FFF;
    font-size:15px;
    font-weight:700;
    border-left:1px solid #0070A8
}

.datagrid table thead th:first-child {
    border:none
}

.datagrid table tbody td {
    color:#00496B;
    border-left:1px solid #E1EEF4;
    font-size:12px;
    font-weight:400
}

.datagrid table tbody .alt td {
    background:#E1EEF4;
    color:#00496B
}

.datagrid table tbody td:first-child {
    border-left:none
}

.datagrid table tbody tr:last-child td {
    border-bottom:none
}

.datagrid table tfoot td div {
    border-top:1px solid #069;
    background:#E1EEF4
}

.datagrid table tfoot td {
    padding:0;
    font-size:12px
}

.datagrid table tfoot td div {
    padding:2px
}

.datagrid table tfoot td ul {
    margin:0;
    padding:0;
    list-style:none;
    text-align:right
}

.datagrid table tfoot li {
    display:inline
}

.datagrid table tfoot li a {
    text-decoration:none;
    display:inline-block;
    padding:2px 8px;
    margin:1px;
    color:#FFF;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px;
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069
}

.datagrid table tfoot ul.active,.datagrid table tfoot ul a:hover {
    text-decoration:none;
    border-color:#069;
    color:#FFF;
    background:none;
    background-color:#00557F
}

div.dhtmlx_window_active,div.dhx_modal_cover_dv {
    position:fixed!important
}
</style><div class="datagrid"><table border="1" class="dataframe">
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
      <th>8443970</th>
      <td>None</td>
      <td>42.3548</td>
      <td>-71.0534</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8443970:E1</td>
      <td>Boston, MA</td>
    </tr>
  </tbody>
</table></div>



### Join CoopsSoS and NdbcSos in uniform 1-hour time base series for model/data
comparison

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

### Save simpler station code/name file

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
    cdm_data_type="Station",
    comment="Data from http://opendap.co-ops.nos.noaa.gov"
)

log.info(fmt(' Observations '))
outfile = os.path.join(save_dir, 'OBS_DATA.nc')

cubes = iris.cube.CubeList(
    [series2cube(obs, attr=attr) for obs in observations]
)

iris.save(cubes, outfile)
```

### Loop discovered models and save the nearest time-series

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
from iris.exceptions import (CoordinateNotFoundError, ConstraintMismatchError,
                             MergeError)
from ioos_tools.ioos import get_model_name
from ioos_tools.tardis import quick_load_cubes, proc_cube, is_model, get_surface

log.info(fmt(' Models '))
cubes = dict()
for k, url in enumerate(dap_urls):
    log.info('\n[Reading url {}/{}]: {}'.format(k+1, len(dap_urls), url))
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
            log.warning("[Not model data]: {}".format(url))
            continue
        cube = get_surface(cube)
        mod_name = get_model_name(url)
        cubes.update({mod_name: cube})
    except (RuntimeError, ValueError,
            ConstraintMismatchError, CoordinateNotFoundError,
            IndexError) as e:
        log.warning('Cannot get cube for: {}\n{}'.format(url, e))
```

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
import iris
from iris.pandas import as_series
from ioos_tools.tardis import (make_tree, get_nearest_water,
                               add_station, ensure_timeseries, remove_ssh)

for mod_name, cube in cubes.items():
    fname = '{}.nc'.format(mod_name)
    fname = os.path.join(save_dir, fname)
    log.info(fmt(' Downloading to file {} '.format(fname)))
    try:
        tree, lon, lat = make_tree(cube)
    except CoordinateNotFoundError as e:
        log.warning('Cannot make KDTree for: {}'.format(mod_name))
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
                log.info('Cannot download {!r}.\n{}'.format(cube, e))
                series = None
        except ValueError as e:
            status = "No Data"
            log.info('[{}] {}'.format(status, obs['station_name']))
            continue
        if not series:
            status = "Land   "
        else:
            raw_series.update({station: series})
            series = as_series(series)
            status = "Water  "
        log.info('[{}] {}'.format(status, obs['station_name']))
    if raw_series:  # Save cube.
        for station, cube in raw_series.items():
            cube = add_station(cube, station)
            cube = remove_ssh(cube)
        try:
            cube = iris.cube.CubeList(raw_series.values()).merge_cube()
        except MergeError as e:
            log.warning(e)
        ensure_timeseries(cube)
        iris.save(cube, fname)
        del cube
    log.info('Finished processing [{}]'.format(mod_name))
```

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
elapsed = time.time() - start_time
log.info('{:.2f} minutes'.format(elapsed/60.))
log.info('EOF')

logfile = os.path.join(config['run_name'], 'log.txt')

with open(logfile) as f:
    print(f.read())
```
<div class="output_area"><div class="prompt"></div>
<pre>
    02:32:39 INFO: Saving data inside directory /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest
    02:32:39 INFO: *********************** Run information ************************
    02:32:39 INFO: Run date: 2016-09-14 17:32:39
    02:32:39 INFO: Start: 2016-09-09 00:00:00
    02:32:39 INFO: Stop: 2016-09-18 00:00:00
    02:32:39 INFO: Bounding box: -71.30, 42.03,-70.57, 42.63
    02:32:39 INFO: ********************* Catalog information **********************
    02:32:39 INFO: ***************************** CSW ******************************
    02:32:39 INFO: URL: http://www.ngdc.noaa.gov/geoportal/csw
    02:32:41 INFO: CSW version: 2.0.2
    02:32:41 INFO: Number of datasets available: 1
    02:32:41 INFO: HYbrid Coordinate Ocean Model (HYCOM): Global
    02:32:41 INFO: ***************************** DAP ******************************
    02:32:41 INFO: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    02:32:41 INFO: ***************************** CSW ******************************
    02:32:41 INFO: URL: https://dev-catalog.ioos.us/csw
    02:32:43 INFO: CSW version: 2.0.2
    02:32:43 INFO: Number of datasets available: 5
    02:32:43 INFO: HYbrid Coordinate Ocean Model (HYCOM): Global
    02:32:43 INFO: NOAA/NCEP Global Forecast System (GFS) Atmospheric Model
    02:32:43 INFO: G1SST, 1km blended SST
    02:32:43 INFO: 1-Day-Aggregation
    02:32:43 INFO: AVHRR Sea Surface Temperature for MARACOOS (Mid-Atlantic Regional Association Coastal Ocean Observing System)
    02:32:43 INFO: ***************************** DAP ******************************
    02:32:43 INFO: http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/atm/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd.html
    02:32:43 INFO: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    02:32:43 INFO: http://tds.maracoos.org/thredds/dodsC/MODIS-One-Agg.nc.html
    02:32:43 INFO: http://tds.maracoos.org/thredds/dodsC/SST-Seven-Agg.nc.html
    02:32:43 INFO: http://thredds.cencoos.org/thredds/dodsC/G1_SST_GLOBAL.nc.html
    02:32:43 INFO: ***************************** CSW ******************************
    02:32:43 INFO: URL: http://geoport.whoi.edu/csw
    02:32:44 INFO: CSW version: 2.0.2
    02:32:44 INFO: Number of datasets available: 3
    02:32:44 INFO: COAWST Forecast System : USGS : US East Coast and Gulf of Mexico (Experimental)
    02:32:44 INFO: NECOFS GOM3 (FVCOM) - Northeast US - Latest Forecast
    02:32:44 INFO: NECOFS Massachusetts (FVCOM) - Massachusetts Coastal - Latest Forecast
    02:32:44 INFO: ***************************** DAP ******************************
    02:32:44 INFO: http://geoport-dev.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd.html
    02:32:44 INFO: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    02:32:44 INFO: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc.html
    02:33:06 INFO: ************************* Filtered DAP *************************
    02:33:06 INFO: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc.html
    02:33:06 INFO: http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/atm/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd.html
    02:33:06 INFO: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    02:33:06 INFO: http://tds.maracoos.org/thredds/dodsC/MODIS-One-Agg.nc.html
    02:33:06 INFO: http://thredds.cencoos.org/thredds/dodsC/G1_SST_GLOBAL.nc.html
    02:33:06 INFO: http://geoport-dev.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd.html
    02:33:06 INFO: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    02:33:06 INFO: http://tds.maracoos.org/thredds/dodsC/SST-Seven-Agg.nc.html
    02:33:09 INFO: ******************* NDBC Collector offerings *******************
    02:33:09 INFO: National Data Buoy Center SOS: 985 offerings
    02:33:38 INFO: ********************* Collector offerings **********************
    02:33:38 INFO: NOAA.NOS.CO-OPS SOS: 1111 offerings
    02:33:41 INFO: ************************* Observations *************************
    02:33:41 INFO: **************************** Models ****************************
    02:33:41 INFO: 
    [Reading url 1/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc
    02:33:55 INFO: 
    [Reading url 2/8]: http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/atm/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd
    02:34:00 WARNING: Cannot get cube for: http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/atm/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd
    Cannot find ['sea_water_temperature', 'sea_surface_temperature', 'sea_water_potential_temperature', 'equivalent_potential_temperature', 'sea_water_conservative_temperature', 'pseudo_equivalent_potential_temperature'] in http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/atm/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd.
    02:34:00 INFO: 
    [Reading url 3/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc
    02:34:22 INFO: 
    [Reading url 4/8]: http://tds.maracoos.org/thredds/dodsC/MODIS-One-Agg.nc
    02:34:28 WARNING: Cannot get cube for: http://tds.maracoos.org/thredds/dodsC/MODIS-One-Agg.nc
    Cannot find ['sea_water_temperature', 'sea_surface_temperature', 'sea_water_potential_temperature', 'equivalent_potential_temperature', 'sea_water_conservative_temperature', 'pseudo_equivalent_potential_temperature'] in http://tds.maracoos.org/thredds/dodsC/MODIS-One-Agg.nc.
    02:34:28 INFO: 
    [Reading url 5/8]: http://thredds.cencoos.org/thredds/dodsC/G1_SST_GLOBAL.nc
    02:34:35 INFO: 
    [Reading url 6/8]: http://geoport-dev.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd
    02:35:41 INFO: 
    [Reading url 7/8]: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global
    02:35:45 INFO: 
    [Reading url 8/8]: http://tds.maracoos.org/thredds/dodsC/SST-Seven-Agg.nc
    02:39:13 WARNING: [Not model data]: http://tds.maracoos.org/thredds/dodsC/SST-Seven-Agg.nc
    02:39:13 INFO:  Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest/pacioos_hycom-global.nc 
    02:39:17 INFO: [Water  ] BOSTON 16 NM East of Boston, MA
    02:39:21 INFO: [Water  ] Buoy A0102 - Mass. Bay/Stellwagen
    02:39:39 INFO: [Land   ] Boston, MA
    02:39:39 INFO: Finished processing [pacioos_hycom-global]
    02:39:39 INFO:  Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest/Forecasts-NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc 
    02:39:44 INFO: [Water  ] BOSTON 16 NM East of Boston, MA
    02:39:49 INFO: [Water  ] Buoy A0102 - Mass. Bay/Stellwagen
    02:39:54 INFO: [Water  ] Boston, MA
    02:39:54 INFO: Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST]
    02:39:54 INFO:  Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest/fmrc-coawst_4_use_best.nc 
    02:40:06 INFO: [Water  ] BOSTON 16 NM East of Boston, MA
    02:40:18 INFO: [Water  ] Buoy A0102 - Mass. Bay/Stellwagen
    02:42:04 INFO: [Water  ] Boston, MA
    02:42:22 INFO: Finished processing [fmrc-coawst_4_use_best]
    02:42:22 INFO:  Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest/G1_SST_GLOBAL.nc 
    02:42:22 INFO: [Water  ] BOSTON 16 NM East of Boston, MA
    02:42:22 INFO: [Water  ] Buoy A0102 - Mass. Bay/Stellwagen
    02:42:22 INFO: [Water  ] Boston, MA
    02:42:22 INFO: Finished processing [G1_SST_GLOBAL]
    02:42:22 INFO:  Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/boston_light_swim/latest/FVCOM_Forecasts-NECOFS_GOM3_FORECAST.nc 
    02:42:29 INFO: [Water  ] BOSTON 16 NM East of Boston, MA
    02:42:33 INFO: [Water  ] Buoy A0102 - Mass. Bay/Stellwagen
    02:42:39 INFO: [Water  ] Boston, MA
    02:42:39 INFO: Finished processing [FVCOM_Forecasts-NECOFS_GOM3_FORECAST]
    02:42:39 INFO: 10.02 minutes
    02:42:39 INFO: EOF
    

</pre>
</div>