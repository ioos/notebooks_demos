---
title: "Investigating ocean models skill for sea surface height with IOOS catalog and Python"
layout: notebook

---


The IOOS [catalog](https://ioos.noaa.gov/data/catalog) offers access to hundreds of datasets and data access services provided by the 11 regional associations.
In the past we demonstrate how to tap into those datasets to obtain sea [surface temperature data from observations](http://ioos.github.io/notebooks_demos/notebooks/2016-12-19-exploring_csw),
[coastal velocity from high frequency radar data](http://ioos.github.io/notebooks_demos/notebooks/2017-12-15-finding_HFRadar_currents),
and a simple model vs observation visualization of temperatures for the [Boston Light Swim competition](http://ioos.github.io/notebooks_demos/notebooks/2016-12-22-boston_light_swim).

In this notebook we'll demonstrate a step-by-step workflow on how ask the catalog for a specific variable, extract only the model data, and match the nearest model grid point to an observation. The goal is to create an automated skill score for quick assessment of ocean numerical models.


The first cell is only to reduce iris' noisy output,
the notebook start on cell [2] with the definition of the parameters:
- start and end dates for the search;
- experiment name;
- a bounding of the region of interest;
- SOS variable name for the observations;
- Climate and Forecast standard names;
- the units we want conform the variables into;
- catalogs we want to search.

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import warnings

# Suppresing warnings for a "pretty output."
warnings.simplefilter('ignore')
```

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
%%writefile config.yaml

date:
    start: 2018-2-28 00:00:00
    stop: 2018-3-5 00:00:00

run_name: 'latest'

region:
    bbox: [-71.20, 41.40, -69.20, 43.74]
    crs: 'urn:ogc:def:crs:OGC:1.3:CRS84'

sos_name: 'water_surface_height_above_reference_datum'

cf_names:
    - sea_surface_height
    - sea_surface_elevation
    - sea_surface_height_above_geoid
    - sea_surface_height_above_sea_level
    - water_surface_height_above_reference_datum
    - sea_surface_height_above_reference_ellipsoid

units: 'm'

catalogs:
    - https://data.ioos.us/csw
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Overwriting config.yaml

</pre>
</div>
To keep track of the information we'll setup a `config` variable and output them on the screen for bookkeeping.

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
    Run date: 2018-03-09 18:52:52
    Start: 2018-02-28 00:00:00
    Stop: 2018-03-05 00:00:00
    Bounding box: -71.20, 41.40,-69.20, 43.74

</pre>
</div>
To interface with the IOOS catalog we will use the [Catalogue Service for the Web (CSW)](https://live.osgeo.org/en/standards/csw_overview.html) endpoint and [python's OWSLib library](https://geopython.github.io/OWSLib).

The cell below creates the [Filter Enconding Specification (FES)](http://www.opengeospatial.org/standards/filter) with configuration we specified in cell [2]. The filter is composed of:
- `or` to catch any of the standard names;
- `not` some names we do not want to show up in the results;
- `date range` and `bounding box` for the time-space domain of the search.

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
def make_filter(config):
    from owslib import fes
    from ioos_tools.ioos import fes_date_filter
    kw = dict(
        wildCard='*',
        escapeChar='\\',
        singleChar='?',
        propertyname='apiso:Subject'
    )

    or_filt = fes.Or(
        [
            fes.PropertyIsLike(literal=('*%s*' % val), **kw)
            for val in config['cf_names']
        ]
    )

    not_filt = fes.Not([fes.PropertyIsLike(literal='GRIB-2', **kw)])

    begin, end = fes_date_filter(
        config['date']['start'],
        config['date']['stop']
    )

    bbox_crs = fes.BBox(
        config['region']['bbox'],
        crs=config['region']['crs']
    )

    filter_list = [fes.And([bbox_crs, begin, end, or_filt, not_filt])]
    return filter_list


filter_list = make_filter(config)
```

We need to wrap `OWSlib.csw.CatalogueServiceWeb` object with a custom function,
` get_csw_records`, to be able to paginate over the results.

In the cell below we loop over all the catalogs returns and extract the OPeNDAP endpoints.

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
    Number of datasets available: 9
    COAWST Modeling System: USEast: ROMS-WRF-SWAN coupled model (aka CNAPS)
    Coupled Northwest Atlantic Prediction System (CNAPS)
    HYbrid Coordinate Ocean Model (HYCOM): Global
    NECOFS (FVCOM) - Hampton - Latest Forecast
    NECOFS (FVCOM) - Scituate - Latest Forecast
    NECOFS Massachusetts (FVCOM) - Boston - Latest Forecast
    NECOFS Massachusetts (FVCOM) - Massachusetts Coastal - Latest Forecast
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC Averages
    ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW) 2013-present FMRC History
    ***************************** DAP ******************************
    http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best.html
    http://thredds.secoora.org/thredds/dodsC/SECOORA_NCSU_CNAPS.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc.html
    
    

</pre>
</div>
We found 10 dataset endpoints but only 9 of them have the proper metadata for us to identify the OPeNDAP endpoint,
those that contain either `OPeNDAP:OPeNDAP` or `urn:x-esri:specification:ServiceType:odp:url` scheme.
Unfortunately we lost the `COAWST` model in the process.

The next step is to ensure there are no observations in the list of endpoints.
We want only the models for now.

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
    ************************* Filtered DAP *************************
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc.html
    http://thredds.secoora.org/thredds/dodsC/SECOORA_NCSU_CNAPS.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best.html
    http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best.html
    http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global.html
    http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc.html

</pre>
</div>
Now we have a nice list of all the models available in the catalog for the domain we specified.
We still need to find the observations for the same domain.
To accomplish that we will use the `pyoos` libray and search the [SOS CO-OPS](https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/) services using the virtually the same configuration options from the catalog search.

<div class="prompt input_prompt">
In&nbsp;[7]:
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
    NOAA.NOS.CO-OPS SOS: 1187 offerings

</pre>
</div>
To make it easier to work with the data we extract the time-series as pandas tables and interpolate them to a common 1-hour interval index.

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
import pandas as pd
from ioos_tools.ioos import collector2table


data = collector2table(
    collector=collector_coops,
    config=config,
    col='water_surface_height_above_reference_datum (m)'
)

df = dict(
    station_name=[s._metadata.get('station_name') for s in data],
    station_code=[s._metadata.get('station_code') for s in data],
    sensor=[s._metadata.get('sensor') for s in data],
    lon=[s._metadata.get('lon') for s in data],
    lat=[s._metadata.get('lat') for s in data],
    depth=[s._metadata.get('depth') for s in data],
)

pd.DataFrame(df).set_index('station_code')
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
      <th>8418150</th>
      <td>None</td>
      <td>43.6561</td>
      <td>-70.2461</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8418150:B1</td>
      <td>Portland, ME</td>
    </tr>
    <tr>
      <th>8419317</th>
      <td>None</td>
      <td>43.3200</td>
      <td>-70.5633</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8419317:B1</td>
      <td>Wells, ME</td>
    </tr>
    <tr>
      <th>8423898</th>
      <td>None</td>
      <td>43.0714</td>
      <td>-70.7106</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8423898:A1</td>
      <td>Fort Point, NH</td>
    </tr>
    <tr>
      <th>8443970</th>
      <td>None</td>
      <td>42.3539</td>
      <td>-71.0503</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8443970:Y1</td>
      <td>Boston, MA</td>
    </tr>
    <tr>
      <th>8447386</th>
      <td>None</td>
      <td>41.7043</td>
      <td>-71.1641</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8447386:B1</td>
      <td>Fall River, MA</td>
    </tr>
    <tr>
      <th>8447435</th>
      <td>None</td>
      <td>41.6885</td>
      <td>-69.9510</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8447435:A1</td>
      <td>Chatham, Lydia Cove, MA</td>
    </tr>
    <tr>
      <th>8447930</th>
      <td>None</td>
      <td>41.5236</td>
      <td>-70.6711</td>
      <td>urn:ioos:sensor:NOAA.NOS.CO-OPS:8447930:B1</td>
      <td>Woods Hole, MA</td>
    </tr>
  </tbody>
</table>
</div>



<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
index = pd.date_range(
    start=config['date']['start'].replace(tzinfo=None),
    end=config['date']['stop'].replace(tzinfo=None),
    freq='1H'
)

# Preserve metadata with `reindex`.
observations = []
for series in data:
    _metadata = series._metadata
    obs = series.reindex(index=index, limit=1, method='nearest')
    obs._metadata = _metadata
    observations.append(obs)
```

The next cell saves those time-series as CF-compliant netCDF files on disk,
to make it easier to access them later.

<div class="prompt input_prompt">
In&nbsp;[10]:
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

We still need to read the model data from the list of endpoints we found.

The next cell takes care of that.
We use `iris`, and a set of custom functions from the `ioos_tools` library,
that downloads only the data in the domain we requested.

<div class="prompt input_prompt">
In&nbsp;[11]:
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
    
    [Reading url 1/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc
    
    [Reading url 2/8]: http://thredds.secoora.org/thredds/dodsC/SECOORA_NCSU_CNAPS.nc
    
    [Reading url 3/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc
    
    [Reading url 4/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc
    Cannot get cube for: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc
    istart must be different from istop! Got istart 0 and  istop 0
    
    [Reading url 5/8]: http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best
    
    [Reading url 6/8]: http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/avg/ESPRESSO_Real-Time_v2_Averages_Best
    
    [Reading url 7/8]: http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global
    
    [Reading url 8/8]: http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc

</pre>
</div>
Now we can match each observation time-series with its closest grid point (0.08 of a degree) on each model.
This is a complex and laborious task! If you are running this interactively grab a coffee and sit comfortably :-)

Note that we are also saving the model time-series to files that align with the observations we saved before.

<div class="prompt input_prompt">
In&nbsp;[12]:
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
    [No Data] Portland, ME
    [No Data] Wells, ME
    [No Data] Fort Point, NH
    [Water  ] Boston, MA
    [No Data] Fall River, MA
    [No Data] Chatham, Lydia Cove, MA
    [No Data] Woods Hole, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_BOSTON_FORECAST]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/SECOORA_NCSU_CNAPS.nc 
    [Land   ] Portland, ME
    [Water  ] Wells, ME
    [Water  ] Fort Point, NH
    [Land   ] Boston, MA
    [Land   ] Fall River, MA
    [Land   ] Chatham, Lydia Cove, MA
    [Water  ] Woods Hole, MA
    Finished processing [SECOORA_NCSU_CNAPS]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/Forecasts-NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc 
    [No Data] Portland, ME
    [No Data] Wells, ME
    [No Data] Fort Point, NH
    [No Data] Boston, MA
    [No Data] Fall River, MA
    [No Data] Chatham, Lydia Cove, MA
    [No Data] Woods Hole, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/roms_2013_da-ESPRESSO_Real-Time_v2_History_Best.nc 
    [No Data] Portland, ME
    [No Data] Wells, ME
    [No Data] Fort Point, NH
    [Land   ] Boston, MA
    [Land   ] Fall River, MA
    [Water  ] Chatham, Lydia Cove, MA
    [Water  ] Woods Hole, MA
    Finished processing [roms_2013_da-ESPRESSO_Real-Time_v2_History_Best]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best.nc 
    [No Data] Portland, ME
    [No Data] Wells, ME
    [No Data] Fort Point, NH
    [Land   ] Boston, MA
    [Land   ] Fall River, MA
    [Water  ] Chatham, Lydia Cove, MA
    [Water  ] Woods Hole, MA
    Finished processing [roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/pacioos_hycom-global.nc 
    [Land   ] Portland, ME
    [Water  ] Wells, ME
    [Water  ] Fort Point, NH
    [Land   ] Boston, MA
    [Land   ] Fall River, MA
    [Water  ] Chatham, Lydia Cove, MA
    [Land   ] Woods Hole, MA
    Finished processing [pacioos_hycom-global]
     Downloading to file /home/filipe/IOOS/notebooks_demos/notebooks/latest/Forecasts-NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc 
    [No Data] Portland, ME
    [No Data] Wells, ME
    [No Data] Fort Point, NH
    [No Data] Boston, MA
    [No Data] Fall River, MA
    [No Data] Chatham, Lydia Cove, MA
    [No Data] Woods Hole, MA
    Finished processing [Forecasts-NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST]

</pre>
</div>
With the matched set of models and observations time-series it is relatively easy to compute skill score metrics on them. In cells [13] to [16] we apply both mean bias and root mean square errors to the time-series.

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
from ioos_tools.ioos import stations_keys


def rename_cols(df, config):
    cols = stations_keys(config, key='station_name')
    return df.rename(columns=cols)
```

<div class="prompt input_prompt">
In&nbsp;[14]:
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

<div class="prompt input_prompt">
In&nbsp;[15]:
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

<div class="prompt input_prompt">
In&nbsp;[16]:
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

Last but not least we can assemble a GIS map, cells [17-23],
with the time-series plot for the observations and models,
and the corresponding skill scores.

<div class="prompt input_prompt">
In&nbsp;[17]:
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
In&nbsp;[18]:
</div>

```python
bbox = config['region']['bbox']

m = make_map(
    bbox,
    zoom_start=8,
    line=True,
    layers=True
)
```

<div class="prompt input_prompt">
In&nbsp;[19]:
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

MarkerCluster(locations=locations, popups=popups, name='Cluster').add_to(m);
```

<div class="prompt input_prompt">
In&nbsp;[20]:
</div>

```python
titles = {
    'coawst_4_use_best': 'COAWST_4',
    'pacioos_hycom-global': 'HYCOM',
    'NECOFS_GOM3_FORECAST': 'NECOFS_GOM3',
    'NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST': 'NECOFS_MassBay',
    'NECOFS_FVCOM_OCEAN_BOSTON_FORECAST': 'NECOFS_Boston',
    'SECOORA_NCSU_CNAPS': 'SECOORA/CNAPS',
    'roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best': 'ESPRESSO Avg',
    'roms_2013_da-ESPRESSO_Real-Time_v2_History_Best': 'ESPRESSO Hist',
    'OBS_DATA': 'Observations'
}
```

<div class="prompt input_prompt">
In&nbsp;[21]:
</div>

```python
from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.models import HoverTool, Legend
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
    leg = []
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
                line_width=5,
                line_cap='round',
                line_join='round',
                **kw
            )
            leg.append(('{}'.format(titles.get(column, column)), [line]))
            p.add_tools(HoverTool(tooltips=[('Name', '{}'.format(titles.get(column, column))),
                                            ('Bias', bias),
                                            ('Skill', skill)],
                                  renderers=[line]))
    legend = Legend(items=leg, location=(0, 60))
    legend.click_policy = 'mute'
    p.add_layout(legend, 'right')
    p.yaxis[0].axis_label = 'Water Height (m)'
    p.xaxis[0].axis_label = 'Date/time'
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
In&nbsp;[22]:
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

folium.LayerControl().add_to(m);
```

<div class="prompt input_prompt">
In&nbsp;[23]:
</div>

```python
def embed_map(m):
    from IPython.display import HTML

    m.save('index.html')
    with open('index.html') as f:
        html = f.read()

    iframe = '<iframe srcdoc="{srcdoc}" style="width: 100%; height: 750px; border: none"></iframe>'
    srcdoc = html.replace('"', '&quot;')
    return HTML(iframe.format(srcdoc=srcdoc))


embed_map(m)
```




<iframe srcdoc="<!DOCTYPE html>
<head>    
    <meta http-equiv=&quot;content-type&quot; content=&quot;text/html; charset=UTF-8&quot; />
    <script>L_PREFER_CANVAS = false; L_NO_TOUCH = false; L_DISABLE_3D = false;</script>
    <script src=&quot;https://cdn.jsdelivr.net/npm/leaflet@1.2.0/dist/leaflet.js&quot;></script>
    <script src=&quot;https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js&quot;></script>
    <script src=&quot;https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js&quot;></script>
    <script src=&quot;https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js&quot;></script>
    <link rel=&quot;stylesheet&quot; href=&quot;https://cdn.jsdelivr.net/npm/leaflet@1.2.0/dist/leaflet.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://rawgit.com/python-visualization/folium/master/folium/templates/leaflet.awesome.rotate.css&quot; />
    <style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>
    <style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>
    
            <style> #map_a13e4f67c7e54889975e34cadade7733 {
                position : relative;
                width : 100.0%;
                height: 100.0%;
                left: 0.0%;
                top: 0.0%;
                }
            </style>
        
    <script src=&quot;https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js&quot;></script>
    <link rel=&quot;stylesheet&quot; href=&quot;https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.css&quot; />
    <link rel=&quot;stylesheet&quot; href=&quot;https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.Default.css&quot; />
</head>
<body>    
    
            <div class=&quot;folium-map&quot; id=&quot;map_a13e4f67c7e54889975e34cadade7733&quot; ></div>
        
</body>
<script>    
    

            
                var bounds = null;
            

            var map_a13e4f67c7e54889975e34cadade7733 = L.map(
                                  'map_a13e4f67c7e54889975e34cadade7733',
                                  {center: [42.57,-70.2],
                                  zoom: 8,
                                  maxBounds: bounds,
                                  layers: [],
                                  worldCopyJump: false,
                                  crs: L.CRS.EPSG3857
                                 });
            
        
    
            var tile_layer_e9ad9fea4663457bbed7f64dd167b924 = L.tileLayer(
                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                {
  &quot;attribution&quot;: null,
  &quot;detectRetina&quot;: false,
  &quot;maxZoom&quot;: 18,
  &quot;minZoom&quot;: 1,
  &quot;noWrap&quot;: false,
  &quot;subdomains&quot;: &quot;abc&quot;
}
                ).addTo(map_a13e4f67c7e54889975e34cadade7733);
        
    
                var poly_line_4aca9c8eb6754ca5a353a3deb1730b41 = L.polyline(
                    [[41.4, -71.2], [41.4, -69.2], [43.74, -69.2], [43.74, -71.2], [41.4, -71.2]],
                    {
  &quot;bubblingMouseEvents&quot;: true,
  &quot;color&quot;: &quot;#FF0000&quot;,
  &quot;dashArray&quot;: null,
  &quot;dashOffset&quot;: null,
  &quot;fill&quot;: false,
  &quot;fillColor&quot;: &quot;#FF0000&quot;,
  &quot;fillOpacity&quot;: 0.2,
  &quot;fillRule&quot;: &quot;evenodd&quot;,
  &quot;lineCap&quot;: &quot;round&quot;,
  &quot;lineJoin&quot;: &quot;round&quot;,
  &quot;noClip&quot;: false,
  &quot;opacity&quot;: 0.9,
  &quot;smoothFactor&quot;: 1.0,
  &quot;stroke&quot;: true,
  &quot;weight&quot;: 2
}).addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    
            var marker_cluster_76b215f3deb04c1aa310c81990ad881c = L.markerClusterGroup({
                
            });
            map_a13e4f67c7e54889975e34cadade7733.addLayer(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    

            var marker_907da1df55444e14b4890611d4d4059f = L.marker(
                [43.26400000000003,-70.55996999999998],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_7613170e3ac44099a2228b03ccf08b7f = L.popup({maxWidth: '300'});

            
                var html_1dbf9e20e43d4ef69800b28ce7e1d360 = $('<div id=&quot;html_1dbf9e20e43d4ef69800b28ce7e1d360&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[global]: Wells, ME</div>')[0];
                popup_7613170e3ac44099a2228b03ccf08b7f.setContent(html_1dbf9e20e43d4ef69800b28ce7e1d360);
            

            marker_907da1df55444e14b4890611d4d4059f.bindPopup(popup_7613170e3ac44099a2228b03ccf08b7f);

            
        
    

            var marker_53626dabde7a4fb3b1841b8a00e736c1 = L.marker(
                [43.251140093105406,-70.54411764699331],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_2809d9c9bff3434097af63cee8b873f1 = L.popup({maxWidth: '300'});

            
                var html_7d8a1f09398744be96b977c19c58bd62 = $('<div id=&quot;html_7d8a1f09398744be96b977c19c58bd62&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[SECOORA_NCSU_CNAPS]: Wells, ME</div>')[0];
                popup_2809d9c9bff3434097af63cee8b873f1.setContent(html_7d8a1f09398744be96b977c19c58bd62);
            

            marker_53626dabde7a4fb3b1841b8a00e736c1.bindPopup(popup_2809d9c9bff3434097af63cee8b873f1);

            
        
    

            var marker_03a8a90f4bb349d6862d085f0ff5835c = L.marker(
                [43.08899999999996,-70.6399699999999],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_5b59437ad2b340e0821e7092011b9de1 = L.popup({maxWidth: '300'});

            
                var html_e86c26ccbdfc498f9c257e8be38f024a = $('<div id=&quot;html_e86c26ccbdfc498f9c257e8be38f024a&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[global]: Fort Point, NH</div>')[0];
                popup_5b59437ad2b340e0821e7092011b9de1.setContent(html_e86c26ccbdfc498f9c257e8be38f024a);
            

            marker_03a8a90f4bb349d6862d085f0ff5835c.bindPopup(popup_5b59437ad2b340e0821e7092011b9de1);

            
        
    

            var marker_6d013c2564544f6abf5988c9ddd09e5b = L.marker(
                [43.04519490099189,-70.64140271486148],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_8cb70a4959ac4e078188566a19c4deb3 = L.popup({maxWidth: '300'});

            
                var html_cbfcaa81429d45c99a6bec0ca30d6d7f = $('<div id=&quot;html_cbfcaa81429d45c99a6bec0ca30d6d7f&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[SECOORA_NCSU_CNAPS]: Fort Point, NH</div>')[0];
                popup_8cb70a4959ac4e078188566a19c4deb3.setContent(html_cbfcaa81429d45c99a6bec0ca30d6d7f);
            

            marker_6d013c2564544f6abf5988c9ddd09e5b.bindPopup(popup_8cb70a4959ac4e078188566a19c4deb3);

            
        
    

            var marker_9b794fbd528547ca92d83cfd0e3dc73a = L.marker(
                [42.35387420654297,-71.05035400390625],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_7c1bdcfa169f4d8a9cac42c034d4ce22 = L.popup({maxWidth: '300'});

            
                var html_a62a98be40f24c89aaa07e3f9e627c60 = $('<div id=&quot;html_a62a98be40f24c89aaa07e3f9e627c60&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[NECOFS_FVCOM_OCEAN_BOSTON_FORECAST]: Boston, MA</div>')[0];
                popup_7c1bdcfa169f4d8a9cac42c034d4ce22.setContent(html_a62a98be40f24c89aaa07e3f9e627c60);
            

            marker_9b794fbd528547ca92d83cfd0e3dc73a.bindPopup(popup_7c1bdcfa169f4d8a9cac42c034d4ce22);

            
        
    

            var marker_38e90f8d36754ce490698e94ab7d9eed = L.marker(
                [41.66425377919582,-69.9143933867417],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_0914c35b4b6e41979f55b8b83927e806 = L.popup({maxWidth: '300'});

            
                var html_ac79e240465747b79ebe33166af8b401 = $('<div id=&quot;html_ac79e240465747b79ebe33166af8b401&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[Time_v2_History_Best]: Chatham, Lydia Cove, MA</div>')[0];
                popup_0914c35b4b6e41979f55b8b83927e806.setContent(html_ac79e240465747b79ebe33166af8b401);
            

            marker_38e90f8d36754ce490698e94ab7d9eed.bindPopup(popup_0914c35b4b6e41979f55b8b83927e806);

            
        
    

            var marker_865e1859dc3a4917b9ab49679dc381c9 = L.marker(
                [41.67080000000001,-69.9199700000001],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_f3dfcea44c194d9186f8db37981b86a9 = L.popup({maxWidth: '300'});

            
                var html_83a5f23f62e44fd8b8bc1e427f9bea29 = $('<div id=&quot;html_83a5f23f62e44fd8b8bc1e427f9bea29&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[global]: Chatham, Lydia Cove, MA</div>')[0];
                popup_f3dfcea44c194d9186f8db37981b86a9.setContent(html_83a5f23f62e44fd8b8bc1e427f9bea29);
            

            marker_865e1859dc3a4917b9ab49679dc381c9.bindPopup(popup_f3dfcea44c194d9186f8db37981b86a9);

            
        
    

            var marker_ee91ccc2f905464e8b252b7aa6a83a60 = L.marker(
                [41.66425377919582,-69.9143933867417],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_09e8f51a922e43dfa589dde1b172aac0 = L.popup({maxWidth: '300'});

            
                var html_b825277a3b8142cdae9398fbe698bffa = $('<div id=&quot;html_b825277a3b8142cdae9398fbe698bffa&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[Time_v2_Averages_Best]: Chatham, Lydia Cove, MA</div>')[0];
                popup_09e8f51a922e43dfa589dde1b172aac0.setContent(html_b825277a3b8142cdae9398fbe698bffa);
            

            marker_ee91ccc2f905464e8b252b7aa6a83a60.bindPopup(popup_09e8f51a922e43dfa589dde1b172aac0);

            
        
    

            var marker_ca66726f9705433688b846aa8da01fbc = L.marker(
                [41.492152566660415,-70.64910206422738],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_bf58578147f6458ebe52381b48a4f7e0 = L.popup({maxWidth: '300'});

            
                var html_1a20848b44a54d78ac7ffe49f2d5d5ca = $('<div id=&quot;html_1a20848b44a54d78ac7ffe49f2d5d5ca&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[Time_v2_History_Best]: Woods Hole, MA</div>')[0];
                popup_bf58578147f6458ebe52381b48a4f7e0.setContent(html_1a20848b44a54d78ac7ffe49f2d5d5ca);
            

            marker_ca66726f9705433688b846aa8da01fbc.bindPopup(popup_bf58578147f6458ebe52381b48a4f7e0);

            
        
    

            var marker_619711018e424ea38ef4daea1c778634 = L.marker(
                [41.5137596760154,-70.64140271482802],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_5622e33cc064431dbe0d66ac4150f0b4 = L.popup({maxWidth: '300'});

            
                var html_55c4ae3c13054baca9ef6644946b1ec7 = $('<div id=&quot;html_55c4ae3c13054baca9ef6644946b1ec7&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[SECOORA_NCSU_CNAPS]: Woods Hole, MA</div>')[0];
                popup_5622e33cc064431dbe0d66ac4150f0b4.setContent(html_55c4ae3c13054baca9ef6644946b1ec7);
            

            marker_619711018e424ea38ef4daea1c778634.bindPopup(popup_5622e33cc064431dbe0d66ac4150f0b4);

            
        
    

            var marker_31649ae42c1d4fe7ae6d9d8cb784c182 = L.marker(
                [41.492152566660415,-70.64910206422738],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(marker_cluster_76b215f3deb04c1aa310c81990ad881c);
            
    
            var popup_7d0c72d0cd8f435c82f4787535dba615 = L.popup({maxWidth: '300'});

            
                var html_31c6f3bd34a048589e22ff286b63325d = $('<div id=&quot;html_31c6f3bd34a048589e22ff286b63325d&quot; style=&quot;width: 100.0%; height: 100.0%;&quot;>[Time_v2_Averages_Best]: Woods Hole, MA</div>')[0];
                popup_7d0c72d0cd8f435c82f4787535dba615.setContent(html_31c6f3bd34a048589e22ff286b63325d);
            

            marker_31649ae42c1d4fe7ae6d9d8cb784c182.bindPopup(popup_7d0c72d0cd8f435c82f4787535dba615);

            
        
    

            var marker_ed6cd15b472645718df96deb97c26273 = L.marker(
                [43.6561,-70.2461],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_9a90591f95b749d5bcdf7f0c5d1026b0 = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_ed6cd15b472645718df96deb97c26273.setIcon(icon_9a90591f95b749d5bcdf7f0c5d1026b0);
            
    
            var popup_009c787e101f4551b289770825d712a8 = L.popup({maxWidth: '2650'});

            
                var i_frame_bb427d6ef4574773aaba36d169da3264 = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQxODE1MDwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9ImEzZWMzN2YzLTU2NWItNDI2ZC1hZDNkLTRhMjczNmYxOWYyNCI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iYTRhMWE2M2ItODRjOC00ZjJlLWE2NmMtOTdkNDA3YmNjZjFiIj4KICAgICAgICAgIHsiNGIyZjZmYzYtY2NlOS00ZDYzLWE4MzktYTM0MjU2MDliNzA5Ijp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnsiYm90dG9tX3VuaXRzIjoic2NyZWVuIiwiZmlsbF9hbHBoYSI6eyJ2YWx1ZSI6MC41fSwiZmlsbF9jb2xvciI6eyJ2YWx1ZSI6ImxpZ2h0Z3JleSJ9LCJsZWZ0X3VuaXRzIjoic2NyZWVuIiwibGV2ZWwiOiJvdmVybGF5IiwibGluZV9hbHBoYSI6eyJ2YWx1ZSI6MS4wfSwibGluZV9jb2xvciI6eyJ2YWx1ZSI6ImJsYWNrIn0sImxpbmVfZGFzaCI6WzQsNF0sImxpbmVfd2lkdGgiOnsidmFsdWUiOjJ9LCJwbG90IjpudWxsLCJyZW5kZXJfbW9kZSI6ImNzcyIsInJpZ2h0X3VuaXRzIjoic2NyZWVuIiwidG9wX3VuaXRzIjoic2NyZWVuIn0sImlkIjoiYWE2YmVlNWQtOWI5ZC00NzlmLTlkYjUtMTNkYzI0Yzc2ZDE4IiwidHlwZSI6IkJveEFubm90YXRpb24ifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6ImNlYWFkYjNmLTJmYzctNGM3OC05YjRkLTc3ODNlMDYyNjEwZiIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6eyJsYWJlbCI6eyJ2YWx1ZSI6Ik9ic2VydmF0aW9ucyJ9LCJyZW5kZXJlcnMiOlt7ImlkIjoiZTEwMTBhYjUtZjljNy00ZDZkLThmN2UtMGQyNjY1MDlhYzA3IiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV19LCJpZCI6IjIwZDhmNTI1LTFjZjgtNDVhNC1hNzExLTA1Nzk4MDVhNWI1MCIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJhZTRkZjU2ZC00YWZkLTRlNjYtYjlkNC1jMjZlMDc1MGJmMTkiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJiZWxvdyI6W3siaWQiOiI2N2FlNzBkNi1mNTE4LTQzMDctOGEyOS0zNjYyZGVmOTk5ZWMiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn1dLCJsZWZ0IjpbeyJpZCI6IjRiNzdkZGM0LWZkMDMtNGUwNC1iZDc0LWZlOGRkZDFmMTE3NiIsInR5cGUiOiJMaW5lYXJBeGlzIn1dLCJwbG90X2hlaWdodCI6MjUwLCJwbG90X3dpZHRoIjo3NTAsInJlbmRlcmVycyI6W3siaWQiOiI2N2FlNzBkNi1mNTE4LTQzMDctOGEyOS0zNjYyZGVmOTk5ZWMiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJpZCI6ImVmNDA4NmRhLTJkNmYtNDk5NS1iOTZhLTA0ZjA0MzE3ZjIzNSIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjRiNzdkZGM0LWZkMDMtNGUwNC1iZDc0LWZlOGRkZDFmMTE3NiIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJpZCI6ImRmNzllYjI1LTU0YjEtNGViMi05ZmJlLWRhOTcwMzA2MjVlOCIsInR5cGUiOiJHcmlkIn0seyJpZCI6ImFhNmJlZTVkLTliOWQtNDc5Zi05ZGI1LTEzZGMyNGM3NmQxOCIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJpZCI6ImUxMDEwYWI1LWY5YzctNGQ2ZC04ZjdlLTBkMjY2NTA5YWMwNyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjdiZTk4NjlhLWIxNGYtNDFiNi1iYjY4LTI1YjhhZTNmMDI3ZiIsInR5cGUiOiJMZWdlbmQifV0sInJpZ2h0IjpbeyJpZCI6IjdiZTk4NjlhLWIxNGYtNDFiNi1iYjY4LTI1YjhhZTNmMDI3ZiIsInR5cGUiOiJMZWdlbmQifV0sInRpdGxlIjp7ImlkIjoiNGI3N2Y3ODAtYjJjNS00MjUxLWE0N2QtNzQ5MWYxZWU3ZjYyIiwidHlwZSI6IlRpdGxlIn0sInRvb2xiYXIiOnsiaWQiOiIzYjJiNmRjNC0wZjMxLTRjYTMtOTdjMy01NGU5MTYyYTAyOGMiLCJ0eXBlIjoiVG9vbGJhciJ9LCJ0b29sYmFyX2xvY2F0aW9uIjoiYWJvdmUiLCJ4X3JhbmdlIjp7ImlkIjoiZWFhOTQxMDktNjI3Ny00Y2I2LWI4NDktYzE1YjdmMTM5NTM0IiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInhfc2NhbGUiOnsiaWQiOiI1MTNkNDBmMi1lMWZhLTRiOGUtOWQ4Ny03OGMxNDgzYjg3NTYiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSwieV9yYW5nZSI6eyJpZCI6ImNlYWFkYjNmLTJmYzctNGM3OC05YjRkLTc3ODNlMDYyNjEwZiIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LCJ5X3NjYWxlIjp7ImlkIjoiYTg5ZDZkODgtYjUyYS00YjI3LTlhNzktZmY1ZTRjOGMwNzFkIiwidHlwZSI6IkxpbmVhclNjYWxlIn19LCJpZCI6ImI1YzgwZGExLTg2ODMtNGIzOS04ODU4LTJhZDRhNTE0MGIyYSIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiIyMWM0MTM5NS1kNDE3LTQwODEtOTZhNy1iYThhNzU1YmY5N2IiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiJhMGE2N2U0Mi1lYjU3LTRhNzUtODg2Ni0wMWUzY2U1NmZlYWIiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNDQ2OTEwODktODRhYi00MzU4LWJkMDUtZjlhZTdjMDY1ODZkIiwidHlwZSI6IkRhdGV0aW1lVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiM2VhYjJkMWUtMzFhZS00ZWMxLTgzNzctNzZlMGRkZTViNDNjIiwidHlwZSI6IlllYXJzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDgsMTUsMjJdfSwiaWQiOiJhN2M1N2E2ZS0xZWU4LTRlNjMtYjIwZC0wZDUzYTBhYWNmMjMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJwbG90IjpudWxsLCJ0ZXh0IjoiODQxODE1MCJ9LCJpZCI6IjRiNzdmNzgwLWIyYzUtNDI1MS1hNDdkLTc0OTFmMWVlN2Y2MiIsInR5cGUiOiJUaXRsZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMzQ2ZTk4MDYtYThkMi00NDc1LWI1YTEtZGFjYWY0OWI2Yjk1IiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDQUFCQVV6Y2Zka0k9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfSwieSI6eyJfX25kYXJyYXlfXyI6IktWeVB3dlVvQWtCZzVkQWkyL2tGUUFSV0RpMnluUWRBdjU4YUw5MGtCa0NCbFVPTGJPY0JRTnY1Zm1xOGRQYy9jVDBLMTZOdzVUODZ0TWgydnArNlAvVDkxSGpwSnJHL0p6RUlyQnhheEQva3BadkVJTERtUDJabVptWm1admcvUHpWZXVra01BMEIwa3hnRVZnNElRTkVpMi9sK2FncEE3NmZHU3plSkNVQXNoeGJaenZjRlFMVElkcjZmR3Y4L1ZnNHRzcDN2N3orMjgvM1VlT25HUHplSlFXRGwwTksveVhhK254b3YxYjg4MzArTmwyNmlQNTN2cDhaTE4ray8zU1FHZ1pWRCt6LzJLRnlQd3ZVRFFQUDkxSGpwSmdoQXBwdkVJTEJ5Q1VEYXp2ZFQ0NlVIUVA3VWVPa21NUU5BUFFyWG8zQTkrRC9KZHI2ZkdpL2xQenEweUhhK243by82U1l4Q0t3Y3VyK21tOFFnc0hMSVAyUTczMCtObCtvL0hGcGtPOTlQK3orY3hDQ3djbWdGUUpxWm1abVptUXBBdy9Vb1hJL0NERUFPTGJLZDc2Y0xRQitGNjFHNEhnZEFVcmdlaGV0UkFFQjBreGdFVmc3eFB3YUJsVU9MYk1jL1BRclhvM0E5MHIrMHlIYStueHJQdjd0SkRBSXJoOFkvalpkdUVvUEE3ai9QOTFQanBaditQODNNek16TXpBVkFvQm92M1NRR0NrRGtwWnZFSUxBS1FPWFFJdHY1ZmdoQUhWcGtPOTlQQTBDRHdNcWhSYmIzUDFUanBadkVJT1EvR0FSV0RpMnlyVCs3U1F3Q0s0ZW12OHFoUmJiei9kUS9qOEwxS0Z5UDhEOHYzU1FHZ1pVQVFLYWJ4Q0N3Y2doQUpRYUJsVU9MRFVDMjgvM1VlT2tQUUpaRGkyem4rdzVBRW9QQXlxRkZDa0NnR2kvZEpBWURRQ1BiK1g1cXZQWS9XbVE3MzArTjR6OHBYSS9DOVNqTVAwNWlFRmc1dE5BL2FyeDBreGdFNmo4Y1dtUTczMC81UDR4czUvdXA4UU5BM1NRR2daVkRDa0JGdHZQOTFIZ05RRlRqcFp2RUlBNUE2UHVwOGRKTkMwQnF2SFNUR0FRRlFFamhlaFN1Ui9zL0Y5bk85MVBqN1QrVEdBUldEaTNhUDIzbis2bngwdFUvNWRBaTIvbCs1aisweUhhK254cjNQOEhLb1VXMjh3SkFJOXY1Zm1xOENVQ1dRNHRzNS9zTlFQM1VlT2ttTVE5QWJlZjdxZkhTREVCZnVra01BaXNJUU9vbU1RaXNIQUZBcU1aTE40bEI5RCtveGtzM2lVSGdQL1lvWEkvQzlkQS82U1l4Q0t3YzJqOUk0WG9VcmtmdFA4REtvVVcyOC9zL2JlZjdxZkhTQkVCYVpEdmZUNDBLUUlnVzJjNzNVdzFBOC8zVWVPa21EVUE2dE1oMnZwOEpRSXhzNS91cDhRTkFya2ZoZWhTdStUOFNnOERLb1VYcVA3RnlhSkh0Zk5jL3FNWkxONGxCMkQra2NEMEsxNlBvUCsrbnhrczNpZmMvYmVmN3FmSFNBa0RLb1VXMjgvMElRSmR1RW9QQXlneEFNUWlzSEZwa0RVQUsxNk53UFFvTFFMYnovZFI0NlFWQWFyeDBreGdFL2orb3hrczNpVUh3UCtTbG04UWdzTm8vVUkyWGJoS0QwRDg9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfX19LCJpZCI6IjIxYzQxMzk1LWQ0MTctNDA4MS05NmE3LWJhOGE3NTViZjk3YiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiIzNzQzZmNlZi1lZTRhLTQ5NjktYjZhMy03MDA1Y2MxMDI3NzYiLCJ0eXBlIjoiQmFzaWNUaWNrRm9ybWF0dGVyIn0seyJhdHRyaWJ1dGVzIjp7ImF4aXNfbGFiZWwiOiJEYXRlL3RpbWUiLCJmb3JtYXR0ZXIiOnsiaWQiOiI0NDY5MTA4OS04NGFiLTQzNTgtYmQwNS1mOWFlN2MwNjU4NmQiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrRm9ybWF0dGVyIn0sInBsb3QiOnsiaWQiOiJiNWM4MGRhMS04NjgzLTRiMzktODg1OC0yYWQ0YTUxNDBiMmEiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiNzExYWIwNjgtYzYyZC00M2E2LTgyZGItYTY1ZjNlYTY5NjFkIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6IjY3YWU3MGQ2LWY1MTgtNDMwNy04YTI5LTM2NjJkZWY5OTllYyIsInR5cGUiOiJEYXRldGltZUF4aXMifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw2XX0sImlkIjoiN2ExMjUwYWEtOTc3MS00Njk0LWJjNjEtYjJlMmIwYzdhMmU0IiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6ImUxMDEwYWI1LWY5YzctNGQ2ZC04ZjdlLTBkMjY2NTA5YWMwNyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIk9ic2VydmF0aW9ucyJdLFsiQmlhcyIsIk5BIl0sWyJTa2lsbCIsIk5BIl1dfSwiaWQiOiJmZWMxMTc3MS01NTg0LTQxYTYtOTQ2ZC0wMjAzMjBlYWJhNDgiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOnsiaWQiOiJiNWM4MGRhMS04NjgzLTRiMzktODg1OC0yYWQ0YTUxNDBiMmEiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiNzExYWIwNjgtYzYyZC00M2E2LTgyZGItYTY1ZjNlYTY5NjFkIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6ImVmNDA4NmRhLTJkNmYtNDk5NS1iOTZhLTA0ZjA0MzE3ZjIzNSIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsNCw4XX0sImlkIjoiODVlZjA0YTgtNWJmMi00YTI5LTgxNTUtM2FjODc4ODdhYWYzIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6ImNyaW1zb24iLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjYzMjE2MzE5LWYyYTYtNDU4MC05ZGM5LTYxODRmYzM3ZjRlNSIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7Im51bV9taW5vcl90aWNrcyI6NSwidGlja2VycyI6W3siaWQiOiJhNzUxZTU3Yi04Yzg5LTQxNTEtOWQ2NC04NmM0MGZlZGEyYjAiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiOWViMDMyYzktMTFiOC00MjViLWI3NjAtMmU2ZGU1YzFmN2U5IiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6ImRjOTEwMTE0LTViMzgtNDZjYy1hNTQ3LTIxN2IyMjMyOGZlZCIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiI4MWU2Y2M1Ny0xMGE0LTQ4NjktYTViZC0wNmEyZjQyOTQ5NjYiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJkNmIzMjE5MC05ZTIyLTQzOTktYmE4OS1jNzEwMDU3Nzc0NGEiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJhN2M1N2E2ZS0xZWU4LTRlNjMtYjIwZC0wZDUzYTBhYWNmMjMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiI0ZDA0Y2MyOC1mMTg3LTQ1NTItOWM0OC03YzM0ZGI0ZmJmMDAiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJlMjI1ZTJkNy1lZjMxLTQ0NmYtOWM2OC1lMjk3YTExZDAzNzgiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjczYTU1OGVhLTRjN2ItNGU3YS05NzY3LWYzMmJlMjcwODQ3YyIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiODVlZjA0YTgtNWJmMi00YTI5LTgxNTUtM2FjODc4ODdhYWYzIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiI3YTEyNTBhYS05NzcxLTQ2OTQtYmM2MS1iMmUyYjBjN2EyZTQiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjNlYWIyZDFlLTMxYWUtNGVjMS04Mzc3LTc2ZTBkZGU1YjQzYyIsInR5cGUiOiJZZWFyc1RpY2tlciJ9XX0sImlkIjoiNzExYWIwNjgtYzYyZC00M2E2LTgyZGItYTY1ZjNlYTY5NjFkIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsMSwyLDMsNCw1LDYsNyw4LDksMTAsMTFdfSwiaWQiOiJlMjI1ZTJkNy1lZjMxLTQ0NmYtOWM2OC1lMjk3YTExZDAzNzgiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImFjdGl2ZV9kcmFnIjoiYXV0byIsImFjdGl2ZV9pbnNwZWN0IjoiYXV0byIsImFjdGl2ZV9zY3JvbGwiOiJhdXRvIiwiYWN0aXZlX3RhcCI6ImF1dG8iLCJ0b29scyI6W3siaWQiOiI0NGVkZWZlYi1mMjlhLTQ5MWItYTg1OS00ZjgxNmZkM2FkNTQiLCJ0eXBlIjoiUGFuVG9vbCJ9LHsiaWQiOiIwZDlkMDU4Ni1iMjhjLTQ3OGQtOTg5Yy00YmQ3ZTk3N2U1ZTUiLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImlkIjoiMzQ2ZTk4MDYtYThkMi00NDc1LWI1YTEtZGFjYWY0OWI2Yjk1IiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiaWQiOiJmZWMxMTc3MS01NTg0LTQxYTYtOTQ2ZC0wMjAzMjBlYWJhNDgiLCJ0eXBlIjoiSG92ZXJUb29sIn1dfSwiaWQiOiIzYjJiNmRjNC0wZjMxLTRjYTMtOTdjMy01NGU5MTYyYTAyOGMiLCJ0eXBlIjoiVG9vbGJhciJ9LHsiYXR0cmlidXRlcyI6eyJtYW50aXNzYXMiOlsxLDIsNV0sIm1heF9pbnRlcnZhbCI6NTAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiYTc1MWU1N2ItOGM4OS00MTUxLTlkNjQtODZjNDBmZWRhMmIwIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNsaWNrX3BvbGljeSI6Im11dGUiLCJpdGVtcyI6W3siaWQiOiIyMGQ4ZjUyNS0xY2Y4LTQ1YTQtYTcxMS0wNTc5ODA1YTViNTAiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9XSwibG9jYXRpb24iOlswLDYwXSwicGxvdCI6eyJpZCI6ImI1YzgwZGExLTg2ODMtNGIzOS04ODU4LTJhZDRhNTE0MGIyYSIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9fSwiaWQiOiI3YmU5ODY5YS1iMTRmLTQxYjYtYmI2OC0yNWI4YWUzZjAyN2YiLCJ0eXBlIjoiTGVnZW5kIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiI2ZjE5YWY0Yy0zMGFjLTRlZGQtYmEwOC02ODA5NDE4YmUzYjQiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjUxM2Q0MGYyLWUxZmEtNGI4ZS05ZDg3LTc4YzE0ODNiODc1NiIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNDRlZGVmZWItZjI5YS00OTFiLWE4NTktNGY4MTZmZDNhZDU0IiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IldhdGVyIEhlaWdodCAobSkiLCJmb3JtYXR0ZXIiOnsiaWQiOiIzNzQzZmNlZi1lZTRhLTQ5NjktYjZhMy03MDA1Y2MxMDI3NzYiLCJ0eXBlIjoiQmFzaWNUaWNrRm9ybWF0dGVyIn0sInBsb3QiOnsiaWQiOiJiNWM4MGRhMS04NjgzLTRiMzktODg1OC0yYWQ0YTUxNDBiMmEiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiNmYxOWFmNGMtMzBhYy00ZWRkLWJhMDgtNjgwOTQxOGJlM2I0IiwidHlwZSI6IkJhc2ljVGlja2VyIn19LCJpZCI6IjRiNzdkZGM0LWZkMDMtNGUwNC1iZDc0LWZlOGRkZDFmMTE3NiIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJhdHRyaWJ1dGVzIjp7ImJhc2UiOjYwLCJtYW50aXNzYXMiOlsxLDIsNSwxMCwxNSwyMCwzMF0sIm1heF9pbnRlcnZhbCI6MTgwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjEwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiI5ZWIwMzJjOS0xMWI4LTQyNWItYjc2MC0yZTZkZTVjMWY3ZTkiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsib3ZlcmxheSI6eyJpZCI6ImFhNmJlZTVkLTliOWQtNDc5Zi05ZGI1LTEzZGMyNGM3NmQxOCIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn19LCJpZCI6IjBkOWQwNTg2LWIyOGMtNDc4ZC05ODljLTRiZDdlOTc3ZTVlNSIsInR5cGUiOiJCb3hab29tVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSwyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTMsMTQsMTUsMTYsMTcsMTgsMTksMjAsMjEsMjIsMjMsMjQsMjUsMjYsMjcsMjgsMjksMzAsMzFdfSwiaWQiOiI4MWU2Y2M1Ny0xMGE0LTQ4NjktYTViZC0wNmEyZjQyOTQ5NjYiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSw0LDcsMTAsMTMsMTYsMTksMjIsMjUsMjhdfSwiaWQiOiJkNmIzMjE5MC05ZTIyLTQzOTktYmE4OS1jNzEwMDU3Nzc0NGEiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDIsNCw2LDgsMTBdfSwiaWQiOiI3M2E1NThlYS00YzdiLTRlN2EtOTc2Ny1mMzJiZTI3MDg0N2MiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRhdGFfc291cmNlIjp7ImlkIjoiMjFjNDEzOTUtZDQxNy00MDgxLTk2YTctYmE4YTc1NWJmOTdiIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSwiZ2x5cGgiOnsiaWQiOiI2MzIxNjMxOS1mMmE2LTQ1ODAtOWRjOS02MTg0ZmMzN2Y0ZTUiLCJ0eXBlIjoiTGluZSJ9LCJob3Zlcl9nbHlwaCI6bnVsbCwibXV0ZWRfZ2x5cGgiOm51bGwsIm5vbnNlbGVjdGlvbl9nbHlwaCI6eyJpZCI6ImFlNGRmNTZkLTRhZmQtNGU2Ni1iOWQ0LWMyNmUwNzUwYmYxOSIsInR5cGUiOiJMaW5lIn0sInNlbGVjdGlvbl9nbHlwaCI6bnVsbCwidmlldyI6eyJpZCI6ImEwYTY3ZTQyLWViNTctNGE3NS04ODY2LTAxZTNjZTU2ZmVhYiIsInR5cGUiOiJDRFNWaWV3In19LCJpZCI6ImUxMDEwYWI1LWY5YzctNGQ2ZC04ZjdlLTBkMjY2NTA5YWMwNyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJhdHRyaWJ1dGVzIjp7ImRpbWVuc2lvbiI6MSwicGxvdCI6eyJpZCI6ImI1YzgwZGExLTg2ODMtNGIzOS04ODU4LTJhZDRhNTE0MGIyYSIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI2ZjE5YWY0Yy0zMGFjLTRlZGQtYmEwOC02ODA5NDE4YmUzYjQiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifX0sImlkIjoiZGY3OWViMjUtNTRiMS00ZWIyLTlmYmUtZGE5NzAzMDYyNWU4IiwidHlwZSI6IkdyaWQifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6ImVhYTk0MTA5LTYyNzctNGNiNi1iODQ5LWMxNWI3ZjEzOTUzNCIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSwxNV19LCJpZCI6IjRkMDRjYzI4LWYxODctNDU1Mi05YzQ4LTdjMzRkYjRmYmYwMCIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImJhc2UiOjI0LCJtYW50aXNzYXMiOlsxLDIsNCw2LDgsMTJdLCJtYXhfaW50ZXJ2YWwiOjQzMjAwMDAwLjAsIm1pbl9pbnRlcnZhbCI6MzYwMDAwMC4wLCJudW1fbWlub3JfdGlja3MiOjB9LCJpZCI6ImRjOTEwMTE0LTViMzgtNDZjYy1hNTQ3LTIxN2IyMjMyOGZlZCIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiYTg5ZDZkODgtYjUyYS00YjI3LTlhNzktZmY1ZTRjOGMwNzFkIiwidHlwZSI6IkxpbmVhclNjYWxlIn1dLCJyb290X2lkcyI6WyJiNWM4MGRhMS04NjgzLTRiMzktODg1OC0yYWQ0YTUxNDBiMmEiXX0sInRpdGxlIjoiQm9rZWggQXBwbGljYXRpb24iLCJ2ZXJzaW9uIjoiMC4xMi4xNCJ9fQogICAgICAgIDwvc2NyaXB0PgogICAgICAgIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgICAgICAgIChmdW5jdGlvbigpIHsKICAgICAgICAgICAgdmFyIGZuID0gZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgQm9rZWguc2FmZWx5KGZ1bmN0aW9uKCkgewogICAgICAgICAgICAgICAgKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgZnVuY3Rpb24gZW1iZWRfZG9jdW1lbnQocm9vdCkgewogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB2YXIgZG9jc19qc29uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2E0YTFhNjNiLTg0YzgtNGYyZS1hNjZjLTk3ZDQwN2JjY2YxYicpLnRleHRDb250ZW50OwogICAgICAgICAgICAgICAgICB2YXIgcmVuZGVyX2l0ZW1zID0gW3siZG9jaWQiOiI0YjJmNmZjNi1jY2U5LTRkNjMtYTgzOS1hMzQyNTYwOWI3MDkiLCJlbGVtZW50aWQiOiJhM2VjMzdmMy01NjViLTQyNmQtYWQzZC00YTI3MzZmMTlmMjQiLCJtb2RlbGlkIjoiYjVjODBkYTEtODY4My00YjM5LTg4NTgtMmFkNGE1MTQwYjJhIn1dOwogICAgICAgICAgICAgICAgICByb290LkJva2VoLmVtYmVkLmVtYmVkX2l0ZW1zKGRvY3NfanNvbiwgcmVuZGVyX2l0ZW1zKTsKICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgICAgICB2YXIgYXR0ZW1wdHMgPSAwOwogICAgICAgICAgICAgICAgICAgIHZhciB0aW1lciA9IHNldEludGVydmFsKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZW1iZWRfZG9jdW1lbnQocm9vdCk7CiAgICAgICAgICAgICAgICAgICAgICAgIGNsZWFySW50ZXJ2YWwodGltZXIpOwogICAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgICAgYXR0ZW1wdHMrKzsKICAgICAgICAgICAgICAgICAgICAgIGlmIChhdHRlbXB0cyA+IDEwMCkgewogICAgICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZygiQm9rZWg6IEVSUk9SOiBVbmFibGUgdG8gcnVuIEJva2VoSlMgY29kZSBiZWNhdXNlIEJva2VoSlMgbGlicmFyeSBpcyBtaXNzaW5nIikKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgfSwgMTAsIHJvb3QpCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0pKHdpbmRvdyk7CiAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgIH07CiAgICAgICAgICAgIGlmIChkb2N1bWVudC5yZWFkeVN0YXRlICE9ICJsb2FkaW5nIikgZm4oKTsKICAgICAgICAgICAgZWxzZSBkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJET01Db250ZW50TG9hZGVkIiwgZm4pOwogICAgICAgICAgfSkoKTsKICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPg==&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_009c787e101f4551b289770825d712a8.setContent(i_frame_bb427d6ef4574773aaba36d169da3264);
            

            marker_ed6cd15b472645718df96deb97c26273.bindPopup(popup_009c787e101f4551b289770825d712a8);

            
        
    

            var marker_cc4095dc65334433b80c064a4dbf79c2 = L.marker(
                [43.32,-70.5633],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_1ab0d03b12394fba90f2e8c9af39dd1d = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_cc4095dc65334433b80c064a4dbf79c2.setIcon(icon_1ab0d03b12394fba90f2e8c9af39dd1d);
            
    
            var popup_21eef0adb09440edac98345b7b6171d4 = L.popup({maxWidth: '2650'});

            
                var i_frame_e2b119269772454dbe0096f4e1a91e68 = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQxOTMxNzwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9IjBmNTYxMTViLWI4MGYtNDcxNi1iMGM3LTI5YjZmYzM5ZjRlNyI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iYWY4ZDAwZGEtZmI4OC00YWRiLWJlNmQtMTk2YTIzODk1ZGNiIj4KICAgICAgICAgIHsiNzY1NTMwZmQtMTllNS00YmMxLWFkOGYtYTdhNmYxYzJiMTliIjp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJnbG9iYWwifSwicmVuZGVyZXJzIjpbeyJpZCI6IjMwYjdkYTk3LTYzMTMtNGRlMi05ZjQyLWE4MjBlODMyY2ZhNSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dfSwiaWQiOiIyMWYyZmM0Ni03NWQ2LTQ5MTUtOWNhNi1hZDhkYzg3MmVlMzMiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSw4LDE1LDIyXX0sImlkIjoiZWU0MTA1OWMtNDdjMC00YmYzLTg3MzItNDY4MTY4MjdhNWMzIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJTRUNPT1JBL0NOQVBTIn0sInJlbmRlcmVycyI6W3siaWQiOiJiYmRiZDYyOS0zNDc1LTQyZmYtYjM0Ni03ZTcxYmI1MzE0NzIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiOGQ4YTgxZmUtNmE4Ni00MDk0LWI4YzYtYmZlMzM4ZmYwYjM4IiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiJjcmltc29uIiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJkNTI1YTdhYS1mOGExLTQyNmEtYjE0Yi01NjE1ZTFkZjE0YjMiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiZmNiODFlYmMtODA0Ny00ZDk1LTk2YTctYzM5N2EzZDU4YmUxIiwidHlwZSI6IkJhc2ljVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im92ZXJsYXkiOnsiaWQiOiIyMjI0NGY4NC0xMDRiLTQzMmMtYjdiZC00YzBmODlkMTc3ZmUiLCJ0eXBlIjoiQm94QW5ub3RhdGlvbiJ9fSwiaWQiOiJmYTI2ZmJlMS1hYzNhLTRjZTYtYjE2My02ZDUxMWIyZmYyOTciLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsImNvbHVtbl9uYW1lcyI6WyJ4IiwieSJdLCJkYXRhIjp7IngiOnsiX19uZGFycmF5X18iOiJBQUNBVnBzZGRrSUFBR2pGbmgxMlFnQUFVRFNpSFhaQ0FBQTRvNlVkZGtJQUFDQVNxUjEyUWdBQUNJR3NIWFpDQUFEdzc2OGRka0lBQU5oZXN4MTJRZ0FBd00yMkhYWkNBQUNvUExvZGRrSUFBSkNydlIxMlFnQUFlQnJCSFhaQ0FBQmdpY1FkZGtJQUFFajR4eDEyUWdBQU1HZkxIWFpDQUFBWTFzNGRka0lBQUFCRjBoMTJRZ0FBNkxQVkhYWkNBQURRSXRrZGRrSUFBTGlSM0IxMlFnQUFvQURnSFhaQ0FBQ0liK01kZGtJQUFIRGU1aDEyUWdBQVdFM3FIWFpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOls5Nl19LCJ5Ijp7Il9fbmRhcnJheV9fIjoiQUFBQUFFaVkvejhBQUFEZ1Z2SDNQd0FBQU1CbFN2QS9BQUFBWU9sRzRUOEFBQUNnY0JEbXZ3QUFBRURscy82L0FBQUFJTWt2Q2NBQUFBQ2c2ck1Gd0FBQUFDQU1PQUxBQUFBQVFGdDQvYjhBQUFEZ0JGdmp2d0FBQUtDc091US9BQUFBSUMvby9UOEFBQUNBTE52N1B3QUFBQUFxenZrL0FBQUFZQ2ZCOXo4QUFBQUF3TWkwUHdBQUFHQVBLUFcvQUFBQVlGWE9CY0FBQUFEQWdtc0Z3QUFBQUNDd0NBWEFBQUFBZ04ybEJNQUFBQURncTcwRHdBQUFBRUI2MVFMQUFBQUFnUGk2M2o4QUFBQkF3S1h5UHdBQUFHRENuUDAvQUFBQVFPSkpCRUFBQUFBZ1d6ZjJQd0FBQUtDTjE4NC9BQUFBWU84QzdiOEFBQUJnQ21QOHZ3QUFBSUJPSWdYQUFBQUE0QmNURE1BQUFBQmdNaHNDd0FBQUFLQ1pSdkMvQUFBQUFJdEp6VDhBQUFEZ0hmM3lQd0FBQUVDRktBRkFBQUFBZ0h2U0NFQUFBQUFBR24wQlFBQUFBTUJ3VC9RL0FBQUFnTGFTMWo4QUFBQUFxYmJvdndBQUFLQldXLzYvQUFBQVlLd3RDTUFBQUFCQWdva0F3QUFBQUFDd3l2Ry9BQUFBZ04wU3hMOEFBQUNnblZidFB3QUFBRUQ1MlA4L0FBQUE0RkdEQ0VBQUFBQWdzaGtDUUFBQUFLQWtZUGMvQUFBQUlNb1o1VDhBQUFCZ01lWGl2d0FBQUlBV2N2Mi9BQUFBSU1xNENNQUFBQUNnRnVrQ3dBQUFBRURHTXZxL0FBQUFZTDRtN2I4QUFBRGcxR0hUUHdBQUFLQkpSUGcvQUFBQUFBL1lCVUFBQUFEZ09PRUJRQUFBQUdERjFQcy9BQUFBQUJubjh6OEFBQUJnNTQvQ3Z3QUFBT0FTaS9pL0FBQUFZQlJpQjhBQUFBQWdrYXdEd0FBQUFPQWI3disvQUFBQWdCV0QrTDhBQUFBQUtESFF2d0FBQUlDQmF2QS9BQUFBZ0tad0FrQUFBQUFnOTNNQVFBQUFBR0NQN3Z3L0FBQUFnREQxK0Q4QUFBQUFmTWk4UHdBQUFBQWhYUFcvQUFBQTRHUkNCc0FBQUFEZ2l3NEZ3QUFBQU9DeTJnUEFBQUFBNE5tbUFzQUFBQUNncmhmdnZ3QUFBS0FVMk5nL0FBQUFvT0gzK3o4QUFBQ0EzTm44UHdBQUFHRFh1LzAvQUFBQVFOS2QvajhBQUFBQUQwUGVQd0FBQUlDVitPNi9BQUFBb0t4RUE4QUFBQUNnckVRRHdBQUFBS0NzUkFQQSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbOTZdfX19LCJpZCI6Ijk2MDlhYTA0LWQzODgtNDA4Yi1hZTliLTgwZDNmMzk0ZjBlYSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsMiw0LDYsOCwxMF19LCJpZCI6IjBiNjUxNmY3LTE0ZDAtNDQyNi04OTEwLWUzM2VjOWQxNmI2ZCIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImQ4Y2ZjOTNlLTM0ZjYtNDYzMC04M2U5LTFkNzQ1ODUxMDY5MCIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiNzIxNmZjZGYtODIxMi00OGExLWI5OWMtMGI0NDYyOTNlYmU2IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiNjI2YmVkYzQtN2QxNy00ODhhLTllYjctNjQ3MDU5ZDkwMjI3IiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjgyZDA3NGUxLTdiODctNGQ2NS1iMmY1LWIxNjlkOGI3YWM4NSIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJhMjAzYmUwNy04NTZlLTRhODctOWMzNy05ZDEwMTA3MmE2YmMiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6IjcyMTZmY2RmLTgyMTItNDhhMS1iOTljLTBiNDQ2MjkzZWJlNiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiZDUyNWE3YWEtZjhhMS00MjZhLWIxNGItNTYxNWUxZGYxNGIzIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiJhMjAzYmUwNy04NTZlLTRhODctOWMzNy05ZDEwMTA3MmE2YmMiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiI2MjZiZWRjNC03ZDE3LTQ4OGEtOWViNy02NDcwNTlkOTAyMjciLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiI0NDY1NTJkNC1jMDMzLTRhYTEtODI5Yy03N2M0MzI2MjI5MmIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFCQXZPMGRka0lBQUNncjhSMTJRZ0FBRUpyMEhYWkNBQUFBSWtBZWRrSUFBT2lRUXg1MlFnQUEwUDlHSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFDQTdlUWVka0lBQUdoYzZCNTJRZ0FBVU12ckhuWkMiLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzE1XX0sInkiOnsiX19uZGFycmF5X18iOiJBQUFBNEJMcDRMOEFBQURnWkFIaHZ3QUFBT0MyR2VHL0FBQUFJTU13NDc4QUFBRGdTaHJqdndBQUFNRFNBK08vQUFBQUFINFY0YjhBQUFDZ2JYN2d2d0FBQUlDNnp0Ky9BQUFBUUtWZnQ3OEFBQUFnUHpHM3Z3QUFBQ0RaQXJlL0FBQUFJQk1Hczc4QUFBQWdFd2F6dndBQUFDQVRCck8vIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxNV19fX0sImlkIjoiY2YxZmExY2MtNTY2Yi00NjUyLTk0MjItNzc0YWEyZTUyNGUzIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImMzZDYxMzI4LTQ3MjktNDMwNS04Nzc0LWY2Mzg0MjIzNWYxZSIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiJjZjFmYTFjYy01NjZiLTQ2NTItOTQyMi03NzRhYTJlNTI0ZTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiJkZjJkMjgzYS02NDBlLTQwMjktYjY1MC1kZjZlYzc1MWQ4OTUiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiOWMxMDAwYWEtNzdhNS00ZjU5LThlMTYtN2IyNjNhOGQ0M2Y2IiwidHlwZSI6IkRhdGV0aW1lVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6IjMwYjdkYTk3LTYzMTMtNGRlMi05ZjQyLWE4MjBlODMyY2ZhNSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsImdsb2JhbCJdLFsiQmlhcyIsIi0yLjIwIl0sWyJTa2lsbCIsIjAuODgiXV19LCJpZCI6IjRiZmRlMzUxLTZhOWMtNDNjOC1hNmNmLTA2MTAyOWZjZWJiZSIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsMTVdfSwiaWQiOiI4NzA1YTQxNS05NWQ4LTQ0YTctOGVlMy0wMDVjYjc5NzNmMGQiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMzFmZThhNDItNDAzZS00MzU2LTg3NWYtYzRhOWM3YmE3Yzk3IiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjhjYTg2ODk2LWI0MjItNDcwZS1hMjdlLTI5NGJkYjU2ZTVhMiIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJiZWxvdyI6W3siaWQiOiI1OTMwMGQ0Mi04ODgyLTRhMGUtOGY0OC02NmQ4YmFhMDAyM2YiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn1dLCJsZWZ0IjpbeyJpZCI6IjI2NjE5NGRjLTY4ZDgtNDg4OS1iMzYzLTM5N2UwMTJiZDRkNiIsInR5cGUiOiJMaW5lYXJBeGlzIn1dLCJwbG90X2hlaWdodCI6MjUwLCJwbG90X3dpZHRoIjo3NTAsInJlbmRlcmVycyI6W3siaWQiOiI1OTMwMGQ0Mi04ODgyLTRhMGUtOGY0OC02NmQ4YmFhMDAyM2YiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJpZCI6Ijc2NzI4OGU4LWNjOGMtNDIyOC04Mjk5LTNlZDljMzkyYTc1MyIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjI2NjE5NGRjLTY4ZDgtNDg4OS1iMzYzLTM5N2UwMTJiZDRkNiIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJpZCI6IjkyMzg5ZTRmLWI2YTItNGE1NC04YjViLTE1MWY0M2M5MDFhNSIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjIyMjQ0Zjg0LTEwNGItNDMyYy1iN2JkLTRjMGY4OWQxNzdmZSIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJpZCI6IjQ0NjU1MmQ0LWMwMzMtNGFhMS04MjljLTc3YzQzMjYyMjkyYiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6ImJiZGJkNjI5LTM0NzUtNDJmZi1iMzQ2LTdlNzFiYjUzMTQ3MiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjMwYjdkYTk3LTYzMTMtNGRlMi05ZjQyLWE4MjBlODMyY2ZhNSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjY5NDNjYmQyLTE2MGUtNGY0MC05ZjdmLWU2YTg5MWRhOWE4NiIsInR5cGUiOiJMZWdlbmQifV0sInJpZ2h0IjpbeyJpZCI6IjY5NDNjYmQyLTE2MGUtNGY0MC05ZjdmLWU2YTg5MWRhOWE4NiIsInR5cGUiOiJMZWdlbmQifV0sInRpdGxlIjp7ImlkIjoiYjRlOTBiOWYtMWEzOC00NjM3LTljNDktMjM0ZjIwOThkZDk2IiwidHlwZSI6IlRpdGxlIn0sInRvb2xiYXIiOnsiaWQiOiJmNTkwOTVmYy1lYTljLTQ1MzMtODIzYi1mNDdiMzAxYTNjNTAiLCJ0eXBlIjoiVG9vbGJhciJ9LCJ0b29sYmFyX2xvY2F0aW9uIjoiYWJvdmUiLCJ4X3JhbmdlIjp7ImlkIjoiNjNhOWJkNDQtZGVhZC00ZDQyLTk0NjctY2JkNDQ3MDQ4NmEwIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInhfc2NhbGUiOnsiaWQiOiJjM2Q2MTMyOC00NzI5LTQzMDUtODc3NC1mNjM4NDIyMzVmMWUiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSwieV9yYW5nZSI6eyJpZCI6IjE5ZTJkZDJhLTI1ZjAtNDE5Yy1iM2UyLThjZGVlZGI3OGY3OCIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LCJ5X3NjYWxlIjp7ImlkIjoiOGNhODY4OTYtYjQyMi00NzBlLWEyN2UtMjk0YmRiNTZlNWEyIiwidHlwZSI6IkxpbmVhclNjYWxlIn19LCJpZCI6ImU5N2JkMjA3LWUyOTUtNGU2NS1hZDFjLWU0YTYwZWRlYzdlOSIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LHsiYXR0cmlidXRlcyI6eyJudW1fbWlub3JfdGlja3MiOjUsInRpY2tlcnMiOlt7ImlkIjoiZDQ5NTQ4NzMtMzRhYS00ZWJiLTk0ZmEtMjNjNmEzNDVjMjAxIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6ImMyNDFmYzJlLWE4M2QtNDVkOS04ODlhLTk2MGY4ZmY4MTVkZSIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiI5NTkzODBjNy1mMGQ4LTRkMTItYjY0MS03NWU2YzU2NWU5MDMiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiZjNiNzg5MmItMDVlNS00ODQ0LWJkMzQtMTFmYjk5YWIzNGE4IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiNWE1ZmI1ZTAtY2U1MC00Mjk0LThmOTctMWQ3MmU5MzU0MGFkIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiZWU0MTA1OWMtNDdjMC00YmYzLTg3MzItNDY4MTY4MjdhNWMzIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiODcwNWE0MTUtOTVkOC00NGE3LThlZTMtMDA1Y2I3OTczZjBkIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiZWVkNWRhMmYtMDA2NS00Y2I5LTlhNmMtNzg2MTg3NmFlOGUwIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiIwYjY1MTZmNy0xNGQwLTQ0MjYtODkxMC1lMzNlYzlkMTZiNmQiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjhiMDNiYzQyLTJmYTgtNGY1My05MzIxLTQxNzc5YjJmZGJjYiIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiODRjYzNjODEtYjQ5ZS00NGU2LWI3YTYtZGMwODg2MTc1OTVmIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiIyZThhMWRlZC04MzcwLTQ0N2QtOWJjYy0zMzBhYTlkZDIxNDEiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifV19LCJpZCI6IjI0ZmJhMjY3LTk2MGItNDQxMi05NGI4LTQyMmQzZWM4MzJjOSIsInR5cGUiOiJEYXRldGltZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjbGlja19wb2xpY3kiOiJtdXRlIiwiaXRlbXMiOlt7ImlkIjoiN2RlNzUzZjEtNmQxNS00MGMzLTk2ZDAtOTRiNzY1NWJiZDI3IiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImlkIjoiOGQ4YTgxZmUtNmE4Ni00MDk0LWI4YzYtYmZlMzM4ZmYwYjM4IiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImlkIjoiMjFmMmZjNDYtNzVkNi00OTE1LTljYTYtYWQ4ZGM4NzJlZTMzIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifV0sImxvY2F0aW9uIjpbMCw2MF0sInBsb3QiOnsiaWQiOiJlOTdiZDIwNy1lMjk1LTRlNjUtYWQxYy1lNGE2MGVkZWM3ZTkiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifX0sImlkIjoiNjk0M2NiZDItMTYwZS00ZjQwLTlmN2YtZTZhODkxZGE5YTg2IiwidHlwZSI6IkxlZ2VuZCJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjY1LCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiNhZWM3ZTgiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImUzNTY0ZmRiLWE4MjEtNDQ1YS1hNmJiLTQ2YjcyZGQ4YTQ5ZiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7Im1hbnRpc3NhcyI6WzEsMiw1XSwibWF4X2ludGVydmFsIjo1MDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiJkNDk1NDg3My0zNGFhLTRlYmItOTRmYS0yM2M2YTM0NWMyMDEiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6IjYzYTliZDQ0LWRlYWQtNGQ0Mi05NDY3LWNiZDQ0NzA0ODZhMCIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6Ijk2MDlhYTA0LWQzODgtNDA4Yi1hZTliLTgwZDNmMzk0ZjBlYSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiZTYxMDg3ZmMtMTdmYi00ZDBhLWIxOTItNTRiNzQ0ZGNjNjUyIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiIxNjQyNzRmYi05YjAxLTRkZjctYTlmYS1hOWI0OTZhYmIzMjciLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiIxNTc3ZmIwMi04Zjk1LTQ1YzEtOThlOS1lOGVmNjQ2M2I0NTIiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiJiYmRiZDYyOS0zNDc1LTQyZmYtYjM0Ni03ZTcxYmI1MzE0NzIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJwbG90IjpudWxsLCJ0ZXh0IjoiODQxOTMxNyJ9LCJpZCI6ImI0ZTkwYjlmLTFhMzgtNDYzNy05YzQ5LTIzNGYyMDk4ZGQ5NiIsInR5cGUiOiJUaXRsZSJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDQUFCQVV6Y2Zka0k9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfSwieSI6eyJfX25kYXJyYXlfXyI6IjJjNzNVK09sQUVCcXZIU1RHQVFGUUkyWGJoS0R3QVpBR3kvZEpBYUJCVUM0SG9YclViZ0JRSk1ZQkZZT0xmZy9POTlQalpkdTVqL3BKakVJckJ5NlA0bEJZT1hRSXF1L040bEJZT1hRd2o4WDJjNzNVK1BsUDNzVXJrZmhldlkvNWRBaTIvbCtBVUNObDI0U2c4QUdRRnlQd3ZVb1hBbEF2NThhTDkwa0NVQ2hSYmJ6L2RRRlFMRnlhSkh0ZlA4L3k2RkZ0dlA5OEQvSmRyNmZHaS9OUC9Zb1hJL0M5ZEMvSDRYclViZ2UxYjg4MzArTmwyNmlQNFBBeXFGRnR1Yy81S1dieENDdytEOEdnWlZEaTJ3Q1FPeFJ1QjZGNndaQWVPa21NUWlzQ0VEeTBrMWlFRmdIUURWZXVra01BZ05BOHRKTlloQlkrVDg5Q3RlamNEM21QeUd3Y21pUjdidy9tcG1abVptWnViK3VSK0Y2Rks3SFA1cVptWm1abWVrL3JrZmhlaFN1K1QvWnp2ZFQ0NlVEUU9GNkZLNUg0UWhBcEhBOUN0ZWpDMEJJNFhvVXJrY0xRQVJXRGkyeW5RZEFBQUFBQUFBQUFVQU9MYktkNzZmeVB3UldEaTJ5bmM4L1pEdmZUNDJYenIrMHlIYStueHJQdjd0SkRBSXJoOFkvVG1JUVdEbTA3RC91ZkQ4MVhycjdQM3NVcmtmaGVnUkFwSEE5Q3RlakNFRHovZFI0NlNZS1FMRnlhSkh0ZkFoQU9yVElkcjZmQTBBRVZnNHRzcDM1UDhaTE40bEJZT1UvNFhvVXJrZmh1ais0SG9YclViaU92NjVINFhvVXJ0Yy9UbUlRV0RtMDhEODZ0TWgydnAvK1A1cVptWm1abVFaQUpqRUlyQnhhQzBENFUrT2xtOFFPUU5SNDZTWXhDQTlBbk1RZ3NISm9DMER6L2RSNDZTWUZRRStObDI0U2cvby9IRnBrTzk5UDZUOHhDS3djV21UVFB5bGNqOEwxS053L0VvUEF5cUZGN2orZDc2ZkdTemY1UHgrRjYxRzRIZ05BWkR2ZlQ0MlhDRUFTZzhES29VVU1RS3J4MGsxaUVBNUF4U0N3Y21pUkRFQTZ0TWgydnA4SFFOMGtCb0dWUXdCQU40bEJZT1hROGovbys2bngwazNpUDVodUVvUEF5dUUvRGkyeW5lK242aitzSEZwa085LzNQeFN1UitGNkZBSkF2NThhTDkwa0NFRHovZFI0NlNZTVFIZStueG92M1E1QWYycThkSk1ZRGtBMlhycEpEQUlLUUFSV0RpMnluUU5BSmpFSXJCeGErRCtxOGRKTlloRG9QNVpEaTJ6bis5ay9VcmdlaGV0UjREK3hjbWlSN1h6dlAvWW9YSS9DOWZvLzdYdy9OVjY2QTBEQXlxRkZ0dk1JUU1sMnZwOGFMd3hBQ0t3Y1dtUTdEVUNnR2kvZEpBWUxRRUZnNWRBaTJ3VkFCb0dWUTR0cy9UODlDdGVqY0Qzd1AvTFNUV0lRV09FL1VJMlhiaEtENEQ4TkFpdUhGdG5xUHhzdjNTUUdnZmMvZWVrbU1RaXNBVUM3U1F3Q0s0Y0hRTFRJZHI2ZkdndEExSGpwSmpFSURVQ2FtWm1abVprTFFEcTB5SGErbndkQU40bEJZT1hRQUVEVFRXSVFXRG4wUDlWNDZTWXhDT1EvVG1JUVdEbTAyRDg9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfX19LCJpZCI6IjcyMTZmY2RmLTgyMTItNDhhMS1iOTljLTBiNDQ2MjkzZWJlNiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7InNvdXJjZSI6eyJpZCI6Ijk2MDlhYTA0LWQzODgtNDA4Yi1hZTliLTgwZDNmMzk0ZjBlYSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn19LCJpZCI6IjE1NzdmYjAyLThmOTUtNDVjMS05OGU5LWU4ZWY2NDYzYjQ1MiIsInR5cGUiOiJDRFNWaWV3In0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsNl19LCJpZCI6Ijg0Y2MzYzgxLWI0OWUtNDRlNi1iN2E2LWRjMDg4NjE3NTk1ZiIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF0YV9zb3VyY2UiOnsiaWQiOiJjZjFmYTFjYy01NjZiLTQ2NTItOTQyMi03NzRhYTJlNTI0ZTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LCJnbHlwaCI6eyJpZCI6ImUzNTY0ZmRiLWE4MjEtNDQ1YS1hNmJiLTQ2YjcyZGQ4YTQ5ZiIsInR5cGUiOiJMaW5lIn0sImhvdmVyX2dseXBoIjpudWxsLCJtdXRlZF9nbHlwaCI6bnVsbCwibm9uc2VsZWN0aW9uX2dseXBoIjp7ImlkIjoiODJkMDc0ZTEtN2I4Ny00ZDY1LWIyZjUtYjE2OWQ4YjdhYzg1IiwidHlwZSI6IkxpbmUifSwic2VsZWN0aW9uX2dseXBoIjpudWxsLCJ2aWV3Ijp7ImlkIjoiZGYyZDI4M2EtNjQwZS00MDI5LWI2NTAtZGY2ZWM3NTFkODk1IiwidHlwZSI6IkNEU1ZpZXcifX0sImlkIjoiMzBiN2RhOTctNjMxMy00ZGUyLTlmNDItYTgyMGU4MzJjZmE1IiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImF0dHJpYnV0ZXMiOnsicGxvdCI6eyJpZCI6ImU5N2JkMjA3LWUyOTUtNGU2NS1hZDFjLWU0YTYwZWRlYzdlOSIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiIyNGZiYTI2Ny05NjBiLTQ0MTItOTRiOC00MjJkM2VjODMyYzkiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiNzY3Mjg4ZTgtY2M4Yy00MjI4LTgyOTktM2VkOWMzOTJhNzUzIiwidHlwZSI6IkdyaWQifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IldhdGVyIEhlaWdodCAobSkiLCJmb3JtYXR0ZXIiOnsiaWQiOiJkOGNmYzkzZS0zNGY2LTQ2MzAtODNlOS0xZDc0NTg1MTA2OTAiLCJ0eXBlIjoiQmFzaWNUaWNrRm9ybWF0dGVyIn0sInBsb3QiOnsiaWQiOiJlOTdiZDIwNy1lMjk1LTRlNjUtYWQxYy1lNGE2MGVkZWM3ZTkiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiZmNiODFlYmMtODA0Ny00ZDk1LTk2YTctYzM5N2EzZDU4YmUxIiwidHlwZSI6IkJhc2ljVGlja2VyIn19LCJpZCI6IjI2NjE5NGRjLTY4ZDgtNDg4OS1iMzYzLTM5N2UwMTJiZDRkNiIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsLCJyZW5kZXJlcnMiOlt7ImlkIjoiYmJkYmQ2MjktMzQ3NS00MmZmLWIzNDYtN2U3MWJiNTMxNDcyIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInRvb2x0aXBzIjpbWyJOYW1lIiwiU0VDT09SQS9DTkFQUyJdLFsiQmlhcyIsIi0yLjE5Il0sWyJTa2lsbCIsIjEuMjEiXV19LCJpZCI6IjczMzYwYTk4LThjMTctNDE3OS05NzVmLWY0MTFmYzQwYTU5ZSIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6NjAsIm1hbnRpc3NhcyI6WzEsMiw1LDEwLDE1LDIwLDMwXSwibWF4X2ludGVydmFsIjoxODAwMDAwLjAsIm1pbl9pbnRlcnZhbCI6MTAwMC4wLCJudW1fbWlub3JfdGlja3MiOjB9LCJpZCI6ImMyNDFmYzJlLWE4M2QtNDVkOS04ODlhLTk2MGY4ZmY4MTVkZSIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMmU4YTFkZWQtODM3MC00NDdkLTliY2MtMzMwYWE5ZGQyMTQxIiwidHlwZSI6IlllYXJzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsfSwiaWQiOiIxOWUyZGQyYS0yNWYwLTQxOWMtYjNlMi04Y2RlZWRiNzhmNzgiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjM2ZTRiNDQ3LTcwMDgtNDFmZi04ZjE2LWExNmFiNzg0MTNlMCIsInR5cGUiOiJSZXNldFRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6MjQsIm1hbnRpc3NhcyI6WzEsMiw0LDYsOCwxMl0sIm1heF9pbnRlcnZhbCI6NDMyMDAwMDAuMCwibWluX2ludGVydmFsIjozNjAwMDAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiOTU5MzgwYzctZjBkOC00ZDEyLWI2NDEtNzVlNmM1NjVlOTAzIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDIsMyw0LDUsNiw3LDgsOSwxMCwxMSwxMiwxMywxNCwxNSwxNiwxNywxOCwxOSwyMCwyMSwyMiwyMywyNCwyNSwyNiwyNywyOCwyOSwzMCwzMV19LCJpZCI6ImYzYjc4OTJiLTA1ZTUtNDg0NC1iZDM0LTExZmI5OWFiMzRhOCIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsMSwyLDMsNCw1LDYsNyw4LDksMTAsMTFdfSwiaWQiOiJlZWQ1ZGEyZi0wMDY1LTRjYjktOWE2Yy03ODYxODc2YWU4ZTAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImF4aXNfbGFiZWwiOiJEYXRlL3RpbWUiLCJmb3JtYXR0ZXIiOnsiaWQiOiI5YzEwMDBhYS03N2E1LTRmNTktOGUxNi03YjI2M2E4ZDQzZjYiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrRm9ybWF0dGVyIn0sInBsb3QiOnsiaWQiOiJlOTdiZDIwNy1lMjk1LTRlNjUtYWQxYy1lNGE2MGVkZWM3ZTkiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiMjRmYmEyNjctOTYwYi00NDEyLTk0YjgtNDIyZDNlYzgzMmM5IiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6IjU5MzAwZDQyLTg4ODItNGEwZS04ZjQ4LTY2ZDhiYWEwMDIzZiIsInR5cGUiOiJEYXRldGltZUF4aXMifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsInJlbmRlcmVycyI6W3siaWQiOiI0NDY1NTJkNC1jMDMzLTRhYTEtODI5Yy03N2M0MzI2MjI5MmIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XSwidG9vbHRpcHMiOltbIk5hbWUiLCJPYnNlcnZhdGlvbnMiXSxbIkJpYXMiLCJOQSJdLFsiU2tpbGwiLCJOQSJdXX0sImlkIjoiZWUzOTM1ZWYtOGFlOC00ODc4LWI3YjItYTA5YjhiY2M0MjY0IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSw0LDcsMTAsMTMsMTYsMTksMjIsMjUsMjhdfSwiaWQiOiI1YTVmYjVlMC1jZTUwLTQyOTQtOGY5Ny0xZDcyZTkzNTQwYWQiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJkaW1lbnNpb24iOjEsInBsb3QiOnsiaWQiOiJlOTdiZDIwNy1lMjk1LTRlNjUtYWQxYy1lNGE2MGVkZWM3ZTkiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiZmNiODFlYmMtODA0Ny00ZDk1LTk2YTctYzM5N2EzZDU4YmUxIiwidHlwZSI6IkJhc2ljVGlja2VyIn19LCJpZCI6IjkyMzg5ZTRmLWI2YTItNGE1NC04YjViLTE1MWY0M2M5MDFhNSIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7ImJvdHRvbV91bml0cyI6InNjcmVlbiIsImZpbGxfYWxwaGEiOnsidmFsdWUiOjAuNX0sImZpbGxfY29sb3IiOnsidmFsdWUiOiJsaWdodGdyZXkifSwibGVmdF91bml0cyI6InNjcmVlbiIsImxldmVsIjoib3ZlcmxheSIsImxpbmVfYWxwaGEiOnsidmFsdWUiOjEuMH0sImxpbmVfY29sb3IiOnsidmFsdWUiOiJibGFjayJ9LCJsaW5lX2Rhc2giOls0LDRdLCJsaW5lX3dpZHRoIjp7InZhbHVlIjoyfSwicGxvdCI6bnVsbCwicmVuZGVyX21vZGUiOiJjc3MiLCJyaWdodF91bml0cyI6InNjcmVlbiIsInRvcF91bml0cyI6InNjcmVlbiJ9LCJpZCI6IjIyMjQ0Zjg0LTEwNGItNDMyYy1iN2JkLTRjMGY4OWQxNzdmZSIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsNCw4XX0sImlkIjoiOGIwM2JjNDItMmZhOC00ZjUzLTkzMjEtNDE3NzliMmZkYmNiIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjY1LCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImU2MTA4N2ZjLTE3ZmItNGQwYS1iMTkyLTU0Yjc0NGRjYzY1MiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiIxNjQyNzRmYi05YjAxLTRkZjctYTlmYS1hOWI0OTZhYmIzMjciLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJhY3RpdmVfZHJhZyI6ImF1dG8iLCJhY3RpdmVfaW5zcGVjdCI6ImF1dG8iLCJhY3RpdmVfc2Nyb2xsIjoiYXV0byIsImFjdGl2ZV90YXAiOiJhdXRvIiwidG9vbHMiOlt7ImlkIjoiMzFmZThhNDItNDAzZS00MzU2LTg3NWYtYzRhOWM3YmE3Yzk3IiwidHlwZSI6IlBhblRvb2wifSx7ImlkIjoiZmEyNmZiZTEtYWMzYS00Y2U2LWIxNjMtNmQ1MTFiMmZmMjk3IiwidHlwZSI6IkJveFpvb21Ub29sIn0seyJpZCI6IjM2ZTRiNDQ3LTcwMDgtNDFmZi04ZjE2LWExNmFiNzg0MTNlMCIsInR5cGUiOiJSZXNldFRvb2wifSx7ImlkIjoiZWUzOTM1ZWYtOGFlOC00ODc4LWI3YjItYTA5YjhiY2M0MjY0IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiaWQiOiI3MzM2MGE5OC04YzE3LTQxNzktOTc1Zi1mNDExZmM0MGE1OWUiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJpZCI6IjRiZmRlMzUxLTZhOWMtNDNjOC1hNmNmLTA2MTAyOWZjZWJiZSIsInR5cGUiOiJIb3ZlclRvb2wifV19LCJpZCI6ImY1OTA5NWZjLWVhOWMtNDUzMy04MjNiLWY0N2IzMDFhM2M1MCIsInR5cGUiOiJUb29sYmFyIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiT2JzZXJ2YXRpb25zIn0sInJlbmRlcmVycyI6W3siaWQiOiI0NDY1NTJkNC1jMDMzLTRhYTEtODI5Yy03N2M0MzI2MjI5MmIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiN2RlNzUzZjEtNmQxNS00MGMzLTk2ZDAtOTRiNzY1NWJiZDI3IiwidHlwZSI6IkxlZ2VuZEl0ZW0ifV0sInJvb3RfaWRzIjpbImU5N2JkMjA3LWUyOTUtNGU2NS1hZDFjLWU0YTYwZWRlYzdlOSJdfSwidGl0bGUiOiJCb2tlaCBBcHBsaWNhdGlvbiIsInZlcnNpb24iOiIwLjEyLjE0In19CiAgICAgICAgPC9zY3JpcHQ+CiAgICAgICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPgogICAgICAgICAgKGZ1bmN0aW9uKCkgewogICAgICAgICAgICB2YXIgZm4gPSBmdW5jdGlvbigpIHsKICAgICAgICAgICAgICBCb2tlaC5zYWZlbHkoZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgICAoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICBmdW5jdGlvbiBlbWJlZF9kb2N1bWVudChyb290KSB7CiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIHZhciBkb2NzX2pzb24gPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnYWY4ZDAwZGEtZmI4OC00YWRiLWJlNmQtMTk2YTIzODk1ZGNiJykudGV4dENvbnRlbnQ7CiAgICAgICAgICAgICAgICAgIHZhciByZW5kZXJfaXRlbXMgPSBbeyJkb2NpZCI6Ijc2NTUzMGZkLTE5ZTUtNGJjMS1hZDhmLWE3YTZmMWMyYjE5YiIsImVsZW1lbnRpZCI6IjBmNTYxMTViLWI4MGYtNDcxNi1iMGM3LTI5YjZmYzM5ZjRlNyIsIm1vZGVsaWQiOiJlOTdiZDIwNy1lMjk1LTRlNjUtYWQxYy1lNGE2MGVkZWM3ZTkifV07CiAgICAgICAgICAgICAgICAgIHJvb3QuQm9rZWguZW1iZWQuZW1iZWRfaXRlbXMoZG9jc19qc29uLCByZW5kZXJfaXRlbXMpOwogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgIGVtYmVkX2RvY3VtZW50KHJvb3QpOwogICAgICAgICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgICAgIHZhciBhdHRlbXB0cyA9IDA7CiAgICAgICAgICAgICAgICAgICAgdmFyIHRpbWVyID0gc2V0SW50ZXJ2YWwoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgICBhdHRlbXB0cysrOwogICAgICAgICAgICAgICAgICAgICAgaWYgKGF0dGVtcHRzID4gMTAwKSB7CiAgICAgICAgICAgICAgICAgICAgICAgIGNvbnNvbGUubG9nKCJCb2tlaDogRVJST1I6IFVuYWJsZSB0byBydW4gQm9rZWhKUyBjb2RlIGJlY2F1c2UgQm9rZWhKUyBsaWJyYXJ5IGlzIG1pc3NpbmciKQogICAgICAgICAgICAgICAgICAgICAgICBjbGVhckludGVydmFsKHRpbWVyKTsKICAgICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICB9LCAxMCwgcm9vdCkKICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgfSkod2luZG93KTsKICAgICAgICAgICAgICB9KTsKICAgICAgICAgICAgfTsKICAgICAgICAgICAgaWYgKGRvY3VtZW50LnJlYWR5U3RhdGUgIT0gImxvYWRpbmciKSBmbigpOwogICAgICAgICAgICBlbHNlIGRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoIkRPTUNvbnRlbnRMb2FkZWQiLCBmbik7CiAgICAgICAgICB9KSgpOwogICAgICAgIDwvc2NyaXB0PgogICAgPC9ib2R5Pgo8L2h0bWw+&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_21eef0adb09440edac98345b7b6171d4.setContent(i_frame_e2b119269772454dbe0096f4e1a91e68);
            

            marker_cc4095dc65334433b80c064a4dbf79c2.bindPopup(popup_21eef0adb09440edac98345b7b6171d4);

            
        
    

            var marker_27e6e0b8c4fc4a8d8775d3f815e1edf3 = L.marker(
                [43.0714,-70.7106],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_2d9bceda7f9a4126a3ff5dc911eed563 = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_27e6e0b8c4fc4a8d8775d3f815e1edf3.setIcon(icon_2d9bceda7f9a4126a3ff5dc911eed563);
            
    
            var popup_fd4449a48aa34fb39548f023654fe71d = L.popup({maxWidth: '2650'});

            
                var i_frame_e815084a792342028856a7425ef3c34e = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQyMzg5ODwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9IjY2MTNkMjg1LWQwZWQtNGNiYS04ZjA2LWY5ZTg4Yjc5ODdlMyI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iNDczOWI5ZjItZDY1Ny00ZWRjLTg5OTQtZDcwMDBkZTMzZjE4Ij4KICAgICAgICAgIHsiYTIxM2VmYjMtMzdjNy00MzZjLTg1YzQtYmI3MmM2ZTNmZWY4Ijp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6ImQzOTJlZGNhLTVkZWEtNGI4Yy05YzE2LTYzYjVkNzMzMjAyYSIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiZmQwNGI0MjktMGNjZS00YmU1LTk5YTItNDc0ZmU0NzQwODRlIiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsOCwxNSwyMl19LCJpZCI6ImVhZWI2NTA2LTg4NWMtNGI4Ny05MzNmLTY5NDRjOWVkMzUxMyIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOnsiaWQiOiI3Y2M0MjgwYi05NDU1LTRhM2YtYjk3Yi1lZmRiYjBkMGZhODciLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiZWZmYWFhOGQtNDlmNS00NTgzLWE2MzMtMDk1ZGQ2ODgxODcyIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6IjgwY2EzYTAwLWJmZjAtNDQxNS04MjdjLWM4OWUzYTI5MTk0NyIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7Im51bV9taW5vcl90aWNrcyI6NSwidGlja2VycyI6W3siaWQiOiIwZTVhODBjOS1iN2NjLTQwMjItODA3NC1jMjkzZjA5ZWE5OTkiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiNTIwYzNhYWItYmU1Ni00ZjNkLWI0ZTUtZThjY2YzMzdlYzNhIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6IjhlNWE5NmI3LWU3Y2EtNGRmZC04YjQyLTdiODQ5YzZiNzMxOCIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiJiOGNiMmVjOC1lMGNkLTQxYWUtOGJjNS1mMTM5MWNmOGE3NWIiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJjZTA0OTg3OS0xODYyLTQ3N2YtYjBlNC1mZDc0ZmJmY2I1OWQiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJlYWViNjUwNi04ODVjLTRiODctOTMzZi02OTQ0YzllZDM1MTMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiI3NDkxODc4OS05M2EzLTQ1ODYtOTc3Ny0yOTQwY2Q1ODk0OTYiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiIxYTU3ZTEyZC1kODQ2LTQ0YTUtOTBmNC05MTJmMWRlMjRiOGMiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjYwYTY2NWNlLTFiNjMtNGI4OC1hNjE3LWYwZjc1NDI0ZDE3NiIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiYmFmZmU3MmYtZjYzNi00YWZhLWE5YzQtZTVmNDUzY2VkYTZiIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiIwY2Y3MzdlNy01N2VlLTRhZDktOWNkYS1iN2U2OWU3MzMwYjAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6ImY4YTI5YTNhLTI0NzUtNDg5ZS04YWFjLTEwMDQzMzUyZGVhYyIsInR5cGUiOiJZZWFyc1RpY2tlciJ9XX0sImlkIjoiZWZmYWFhOGQtNDlmNS00NTgzLWE2MzMtMDk1ZGQ2ODgxODcyIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImF4aXNfbGFiZWwiOiJXYXRlciBIZWlnaHQgKG0pIiwiZm9ybWF0dGVyIjp7ImlkIjoiYWRmYzU0ZjAtZjUxOC00N2NmLWJiNTUtMTE4ZmU4MzRjZTY4IiwidHlwZSI6IkJhc2ljVGlja0Zvcm1hdHRlciJ9LCJwbG90Ijp7ImlkIjoiN2NjNDI4MGItOTQ1NS00YTNmLWI5N2ItZWZkYmIwZDBmYTg3Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6ImQxOTI0MjhiLTI5YzUtNGVmYS1iMDYyLTgwYWE0ODQ4Mjg4MSIsInR5cGUiOiJCYXNpY1RpY2tlciJ9fSwiaWQiOiJjZTg1ODQ4YS1jYjdkLTQzMWQtODQxMS03ZjgzN2RkODA4MjYiLCJ0eXBlIjoiTGluZWFyQXhpcyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiODRmODI4ZGUtZjdhOS00NDM5LWE2YmYtZDlhMWMxZDJmMjcyIiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJiYXNlIjoyNCwibWFudGlzc2FzIjpbMSwyLDQsNiw4LDEyXSwibWF4X2ludGVydmFsIjo0MzIwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjM2MDAwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiI4ZTVhOTZiNy1lN2NhLTRkZmQtOGI0Mi03Yjg0OWM2YjczMTgiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw0LDhdfSwiaWQiOiJiYWZmZTcyZi1mNjM2LTRhZmEtYTljNC1lNWY0NTNjZWRhNmIiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsLCJyZW5kZXJlcnMiOlt7ImlkIjoiZjRhN2IwMjctZTQyMC00YmZhLTk5OTMtZDA1MGFhNDk3YWU0IiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInRvb2x0aXBzIjpbWyJOYW1lIiwiZ2xvYmFsIl0sWyJCaWFzIiwiLTIuMTYiXSxbIlNraWxsIiwiMC45MCJdXX0sImlkIjoiMDZhMDFlOTctMDI5Zi00ZGFlLTgwMzAtM2U1NmUzZjQ2MGJmIiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiJhNWVhZDc3NC05ZTZhLTQxZDgtYjAwMS0yZDM2YjU3MTBkN2EiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiIxNzVmODMyMi1mOTE4LTQxZmEtOTJhNS0xOWQxYTIwNTg0ZWQiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiJlNTM1OTlmOC02OTRjLTRmMjgtYjA4Zi1jMDkxZGViOThmNTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiJkMzVhZTgzOS1iMTgyLTQxZGItYWIyYi02NmQyY2FlODQ2ZTciLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbH0sImlkIjoiNTViY2MzMWQtNjRjMi00ODE0LWIwZjMtZGU4MjA0MTIyZThiIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOm51bGwsInRleHQiOiI4NDIzODk4In0sImlkIjoiMThmMmYxZWUtMGNhNC00ODlmLTg4ZWEtNGRhNzcxNmViNzRlIiwidHlwZSI6IlRpdGxlIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDE1XX0sImlkIjoiNzQ5MTg3ODktOTNhMy00NTg2LTk3NzctMjk0MGNkNTg5NDk2IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjlhYmEzNDMyLTA4OTktNGNhYi05ODE4LWU0OTRhOWQ1OTk0YyIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJtYW50aXNzYXMiOlsxLDIsNV0sIm1heF9pbnRlcnZhbCI6NTAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiMGU1YTgwYzktYjdjYy00MDIyLTgwNzQtYzI5M2YwOWVhOTk5IiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiT2JzZXJ2YXRpb25zIn0sInJlbmRlcmVycyI6W3siaWQiOiIxMjY0ZTBhZC1hMWQxLTQyMjMtOTgyNy04ZmM4OTVjMGE4YmUiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiNmQ2MjEyMjQtOWU1OC00ODkzLTkyMzEtNzk1ZTc5ZDgzOGUxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6NjAsIm1hbnRpc3NhcyI6WzEsMiw1LDEwLDE1LDIwLDMwXSwibWF4X2ludGVydmFsIjoxODAwMDAwLjAsIm1pbl9pbnRlcnZhbCI6MTAwMC4wLCJudW1fbWlub3JfdGlja3MiOjB9LCJpZCI6IjUyMGMzYWFiLWJlNTYtNGYzZC1iNGU1LWU4Y2NmMzM3ZWMzYSIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJiZWxvdyI6W3siaWQiOiJkMGY5N2QzMC02ZDI3LTQ0MTItYTY5Mi0yZjQxOTMyZjNiODYiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn1dLCJsZWZ0IjpbeyJpZCI6ImNlODU4NDhhLWNiN2QtNDMxZC04NDExLTdmODM3ZGQ4MDgyNiIsInR5cGUiOiJMaW5lYXJBeGlzIn1dLCJwbG90X2hlaWdodCI6MjUwLCJwbG90X3dpZHRoIjo3NTAsInJlbmRlcmVycyI6W3siaWQiOiJkMGY5N2QzMC02ZDI3LTQ0MTItYTY5Mi0yZjQxOTMyZjNiODYiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJpZCI6IjgwY2EzYTAwLWJmZjAtNDQxNS04MjdjLWM4OWUzYTI5MTk0NyIsInR5cGUiOiJHcmlkIn0seyJpZCI6ImNlODU4NDhhLWNiN2QtNDMxZC04NDExLTdmODM3ZGQ4MDgyNiIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJpZCI6IjRkYjBjNmVlLWVhNjEtNGM3Yi1iMDMzLWZiZjY4ZmNiM2I0MSIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjcyYTk1ZTU0LTM4YTYtNGQxZC1iY2JmLThkY2NiZTU2MmRhMiIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJpZCI6IjEyNjRlMGFkLWExZDEtNDIyMy05ODI3LThmYzg5NWMwYThiZSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjU1ZmRmMTBlLTljMWQtNDAxOS1iZDVkLTNhYjEzN2JkY2ZkOSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6ImY0YTdiMDI3LWU0MjAtNGJmYS05OTkzLWQwNTBhYTQ5N2FlNCIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6ImE1NTVmN2M3LTQ2MGMtNGQxYy05NzcyLWNlMjZhODdjMjE2NCIsInR5cGUiOiJMZWdlbmQifV0sInJpZ2h0IjpbeyJpZCI6ImE1NTVmN2M3LTQ2MGMtNGQxYy05NzcyLWNlMjZhODdjMjE2NCIsInR5cGUiOiJMZWdlbmQifV0sInRpdGxlIjp7ImlkIjoiMThmMmYxZWUtMGNhNC00ODlmLTg4ZWEtNGRhNzcxNmViNzRlIiwidHlwZSI6IlRpdGxlIn0sInRvb2xiYXIiOnsiaWQiOiJiOTY3OTY3MC0xMmRhLTQ4NjItODJiZi00ODA3ZjhhNzllYzMiLCJ0eXBlIjoiVG9vbGJhciJ9LCJ0b29sYmFyX2xvY2F0aW9uIjoiYWJvdmUiLCJ4X3JhbmdlIjp7ImlkIjoiNTViY2MzMWQtNjRjMi00ODE0LWIwZjMtZGU4MjA0MTIyZThiIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInhfc2NhbGUiOnsiaWQiOiJjNmQyYmVjZC04ZjIzLTQ5MjgtOTUzOS1mZjUzMDJmZTI2N2UiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSwieV9yYW5nZSI6eyJpZCI6ImQzOTJlZGNhLTVkZWEtNGI4Yy05YzE2LTYzYjVkNzMzMjAyYSIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LCJ5X3NjYWxlIjp7ImlkIjoiOWFiYTM0MzItMDg5OS00Y2FiLTk4MTgtZTQ5NGE5ZDU5OTRjIiwidHlwZSI6IkxpbmVhclNjYWxlIn19LCJpZCI6IjdjYzQyODBiLTk0NTUtNGEzZi1iOTdiLWVmZGJiMGQwZmE4NyIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LHsiYXR0cmlidXRlcyI6eyJkaW1lbnNpb24iOjEsInBsb3QiOnsiaWQiOiI3Y2M0MjgwYi05NDU1LTRhM2YtYjk3Yi1lZmRiYjBkMGZhODciLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiZDE5MjQyOGItMjljNS00ZWZhLWIwNjItODBhYTQ4NDgyODgxIiwidHlwZSI6IkJhc2ljVGlja2VyIn19LCJpZCI6IjRkYjBjNmVlLWVhNjEtNGM3Yi1iMDMzLWZiZjY4ZmNiM2I0MSIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiZ2xvYmFsIn0sInJlbmRlcmVycyI6W3siaWQiOiJmNGE3YjAyNy1lNDIwLTRiZmEtOTk5My1kMDUwYWE0OTdhZTQiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiNWYzMTJkNjAtZWQxYy00YjNlLWIzYjctNWQ1NTI1ZTVlNDEwIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsiY2xpY2tfcG9saWN5IjoibXV0ZSIsIml0ZW1zIjpbeyJpZCI6IjZkNjIxMjI0LTllNTgtNDg5My05MjMxLTc5NWU3OWQ4MzhlMSIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJpZCI6ImM5NTRkNDUyLTQxOGUtNDM1Yy05MDhiLTIxMDM2MjhjODM3MyIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJpZCI6IjVmMzEyZDYwLWVkMWMtNGIzZS1iM2I3LTVkNTUyNWU1ZTQxMCIsInR5cGUiOiJMZWdlbmRJdGVtIn1dLCJsb2NhdGlvbiI6WzAsNjBdLCJwbG90Ijp7ImlkIjoiN2NjNDI4MGItOTQ1NS00YTNmLWI5N2ItZWZkYmIwZDBmYTg3Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In19LCJpZCI6ImE1NTVmN2M3LTQ2MGMtNGQxYy05NzcyLWNlMjZhODdjMjE2NCIsInR5cGUiOiJMZWdlbmQifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjZmZiYjc4IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJmNzNmNGRhYy0yNDU4LTQxN2QtYjM0Yi03ZjY1OWI1ZWUyYmYiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDZdfSwiaWQiOiIwY2Y3MzdlNy01N2VlLTRhZDktOWNkYS1iN2U2OWU3MzMwYjAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImFjdGl2ZV9kcmFnIjoiYXV0byIsImFjdGl2ZV9pbnNwZWN0IjoiYXV0byIsImFjdGl2ZV9zY3JvbGwiOiJhdXRvIiwiYWN0aXZlX3RhcCI6ImF1dG8iLCJ0b29scyI6W3siaWQiOiJmZDA0YjQyOS0wY2NlLTRiZTUtOTlhMi00NzRmZTQ3NDA4NGUiLCJ0eXBlIjoiUGFuVG9vbCJ9LHsiaWQiOiJkYjRiNTczYi0wNzg1LTRhNmEtOTI5YS1iNzlkZGFhZTNkNmEiLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImlkIjoiODRmODI4ZGUtZjdhOS00NDM5LWE2YmYtZDlhMWMxZDJmMjcyIiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiaWQiOiIxYTc2YzYzMS0zMTE1LTQ0N2UtYWUzZC00MGI0ODQ0OTE0ZTUiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJpZCI6ImEwNTNiODZhLWVhZTctNDNhYi1hMDg2LWZiY2E5NWM2MTU0MyIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImlkIjoiMDZhMDFlOTctMDI5Zi00ZGFlLTgwMzAtM2U1NmUzZjQ2MGJmIiwidHlwZSI6IkhvdmVyVG9vbCJ9XX0sImlkIjoiYjk2Nzk2NzAtMTJkYS00ODYyLTgyYmYtNDgwN2Y4YTc5ZWMzIiwidHlwZSI6IlRvb2xiYXIifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCwyLDQsNiw4LDEwXX0sImlkIjoiNjBhNjY1Y2UtMWI2My00Yjg4LWE2MTctZjBmNzU0MjRkMTc2IiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6ImE1ZWFkNzc0LTllNmEtNDFkOC1iMDAxLTJkMzZiNTcxMGQ3YSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiMjIwYTY3ZWYtNjBlYy00MTYyLTk3ZGEtNTU2OTQ1Mzc4ODY5IiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiIyYjMwMTY2YS00ZjY2LTQzMTktOGQwZC03MmY2Y2MzODZmZjYiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiIxNzVmODMyMi1mOTE4LTQxZmEtOTJhNS0xOWQxYTIwNTg0ZWQiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiIxMjY0ZTBhZC1hMWQxLTQyMjMtOTgyNy04ZmM4OTVjMGE4YmUiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiYWRmYzU0ZjAtZjUxOC00N2NmLWJiNTUtMTE4ZmU4MzRjZTY4IiwidHlwZSI6IkJhc2ljVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6ImU1MzU5OWY4LTY5NGMtNGYyOC1iMDhmLWMwOTFkZWI5OGY1MyIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiZjczZjRkYWMtMjQ1OC00MTdkLWIzNGItN2Y2NTliNWVlMmJmIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiJkYTBjZDNmNC0yMjg4LTQ4ZDMtYjRkYS1iNDZiNDRiZWY1YjUiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiJkMzVhZTgzOS1iMTgyLTQxZGItYWIyYi02NmQyY2FlODQ2ZTciLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiJmNGE3YjAyNy1lNDIwLTRiZmEtOTk5My1kMDUwYWE0OTdhZTQiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQXlLRGFIblpDQUFDd0Q5NGVka0lBQUpoKzRSNTJRZ0FBZ08za0huWkNBQUJvWE9nZWRrSUFBRkRMNng1MlFnQUFPRHJ2SG5aQ0FBQWdxZkllZGtJQUFBZ1k5aDUyUWdBQThJYjVIblpDQUFEWTlmd2Vka0lBQU1Ca0FCOTJRZ0FBcU5NREgzWkNBQUNRUWdjZmRrSUFBSGl4Q2g5MlFnQUFZQ0FPSDNaQ0FBQklqeEVmZGtJQUFERCtGQjkyUWdBQUdHMFlIM1pDQUFBQTNCc2Zka0lBQU9oS0h4OTJRZ0FBMExraUgzWkNBQUM0S0NZZmRrSUFBS0NYS1I5MlFnQUFpQVl0SDNaQ0FBQndkVEFmZGtJQUFGamtNeDkyUWdBQVFGTTNIM1pDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjBdfSwieSI6eyJfX25kYXJyYXlfXyI6IlVJMlhiaEtEQUVENmZtcThkSk1FUUdabVptWm1aZ1pBVXJnZWhldFJCVUI1NlNZeENLd0JRT3hSdUI2RjYvYy9Cb0dWUTR0czV6OU1ONGxCWU9YQVB3aXNIRnBrTzYrL1dEbTB5SGErdnovNFUrT2xtOFRrUHl5SEZ0bk85L1UvQm9HVlE0dHNBVUQ4cWZIU1RXSUdRQitGNjFHNEhnbEFJOXY1Zm1xOENFQmtPOTlQalpjRlFFU0xiT2Y3cWY4L0NLd2NXbVE3OFQrUjdYdy9OVjdTUDd0SkRBSXJoOGEvTjRsQllPWFEwcjhyaHhiWnp2ZWpQK1hRSXR2NWZ1WS9UNDJYYmhLRCtEOTlQelZldWtrQ1FEcTB5SGErbndaQWMyaVI3WHcvQ0VCZzVkQWkyL2tHUU9GNkZLNUg0UUpBNFhvVXJrZmgrRCsweUhhK254cm5QOC8zVStPbG04US95cUZGdHZQOXRMKy9ueG92M1NUR1B5UGIrWDVxdk9nL0d5L2RKQWFCK1QrdVIrRjZGSzREUUtyeDBrMWlFQWxBV21RNzMwK05DMERYbzNBOUN0Y0tRQXJYbzNBOUNnZEFPclRJZHI2ZkFFQjlQelZldWtueVB6ZUpRV0RsME5JL0VvUEF5cUZGeHI5a085OVBqWmZPdndhQmxVT0xiTWMvMUhqcEpqRUk3RC9vKzZueDBrMzhQekVJckJ4YVpBUkFJOXY1Zm1xOENFQUsxNk53UFFvS1FFamhlaFN1UndoQVptWm1abVptQTBDY3hDQ3djbWo1UDZ3Y1dtUTczK2MvQXl1SEZ0bk94eis0SG9YclViaWVQN3gwa3hnRVZ0WS9URGVKUVdEbDhEOXphSkh0ZkQvL1AyTVFXRG0weUFaQUpqRUlyQnhhREVCNDZTWXhDS3dOUUE0dHNwM3ZwdzFBWkR2ZlQ0MlhDa0FSV0RtMHlIWUVRTjlQalpkdUV2ay92SFNUR0FSVzZqOVdEaTJ5bmUvWFA2UndQUXJYbzlnL3lxRkZ0dlA5N0Qva3BadkVJTEQ0UDZBYUw5MGtCZ05BUVdEbDBDTGJDRUNQd3ZVb1hJOE1RUDNVZU9rbU1RMUFreGdFVmc0dEMwQmc1ZEFpMi9rRlFOdjVmbXE4ZFAwL0NLd2NXbVE3OFQvdnA4WkxONG5oUCtGNkZLNUg0ZG8vMi9sK2FyeDA1eitveGtzM2lVSDJQeGJaenZkVDR3RkFFb1BBeXFGRkNFQ05sMjRTZzhBTVFHUTczMCtObHcxQVJJdHM1L3VwREVBSXJCeGFaRHNMUUVXMjgvM1VlTzAvR3kvZEpBYUI1VDl0NS91cDhkTFZQOVI0NlNZeENOdy83NmZHU3plSjdULzkxSGpwSmpINlAvcCthcngwa3dOQVg3cEpEQUlyQ1VEOHFmSFNUV0lNUU52NWZtcThkQXhBNUtXYnhDQ3dDVUFHZ1pWRGkyd0VRSGpwSmpFSXJQby92SFNUR0FSVzdqOWtPOTlQalpmZVAreFJ1QjZGNjlrLzlpaGNqOEwxNkQvUDkxUGpwWnYyUHpxMHlIYStud0ZBeFNDd2NtaVJCMERHU3plSlFXQUxRSGpwSmpFSXJBeEFMOTBrQm9HVkNrQnphSkh0ZkQ4R1FPU2xtOFFnc1A0L1ZPT2xtOFFnOGovMC9kUjQ2U2JoUHlVR2daVkRpOVEvIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjBdfX19LCJpZCI6ImE1ZWFkNzc0LTllNmEtNDFkOC1iMDAxLTJkMzZiNTcxMGQ3YSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiJmOGEyOWEzYS0yNDc1LTQ4OWUtOGFhYy0xMDA0MzM1MmRlYWMiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiNjJjM2YwZGMtNzQ2Yi00ZDIwLTgyOWItMDNjMWY2NDY2YTkzIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiZTJjOTQyZmUtZjlmOS00ZjczLTg2ZTktNjQ5ZDY3ZWE4MzgyIiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjJiMzAxNjZhLTRmNjYtNDMxOS04ZDBkLTcyZjZjYzM4NmZmNiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiY3JpbXNvbiIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiMjIwYTY3ZWYtNjBlYy00MTYyLTk3ZGEtNTU2OTQ1Mzc4ODY5IiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCwxLDIsMyw0LDUsNiw3LDgsOSwxMCwxMV19LCJpZCI6IjFhNTdlMTJkLWQ4NDYtNDRhNS05MGY0LTkxMmYxZGUyNGI4YyIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImM2ZDJiZWNkLThmMjMtNDkyOC05NTM5LWZmNTMwMmZlMjY3ZSIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6IjEyNjRlMGFkLWExZDEtNDIyMy05ODI3LThmYzg5NWMwYThiZSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIk9ic2VydmF0aW9ucyJdLFsiQmlhcyIsIk5BIl0sWyJTa2lsbCIsIk5BIl1dfSwiaWQiOiIxYTc2YzYzMS0zMTE1LTQ0N2UtYWUzZC00MGI0ODQ0OTE0ZTUiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiJkMTkyNDI4Yi0yOWM1LTRlZmEtYjA2Mi04MGFhNDg0ODI4ODEiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjZmY3ZjBlIiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiIxMTM4ODkxNi00NWUyLTQ1OTQtYWVjYy1kNzllOGY1NGIwMjIiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6IjYyYzNmMGRjLTc0NmItNGQyMC04MjliLTAzYzFmNjQ2NmE5MyIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiMTEzODg5MTYtNDVlMi00NTk0LWFlY2MtZDc5ZThmNTRiMDIyIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiJlNzg1NzQzYi00YjdkLTRlNDctOTY2ZC1kNzU3MGMxYjY5ZWMiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiJlMmM5NDJmZS1mOWY5LTRmNzMtODZlOS02NDlkNjdlYTgzODIiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiI1NWZkZjEwZS05YzFkLTQwMTktYmQ1ZC0zYWIxMzdiZGNmZDkiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUFBSWtBZWRrSUFBT2lRUXg1MlFnQUEwUDlHSG5aQ0FBQzRia29lZGtJQUFLRGRUUjUyUWdBQWlFeFJIblpDQUFCd3UxUWVka0lBQUZncVdCNTJRZ0FBUUpsYkhuWkNBQUFvQ0Y4ZWRrSUFBQkIzWWg1MlFnQUErT1ZsSG5aQ0FBRGdWR2tlZGtJQUFNakRiQjUyUWdBQXNESndIblpDQUFDWW9YTWVka0lBQUlBUWR4NTJRZ0FBYUg5NkhuWkNBQUJRN24wZWRrSUFBRGhkZ1I1MlFnQUFJTXlFSG5aQ0FBQUlPNGdlZGtJQUFQQ3BpeDUyUWdBQTJCaVBIblpDQUFEQWg1SWVka0lBQUtqMmxSNTJRZ0FBa0dXWkhuWkNBQUI0MUp3ZWRrSUFBR0JEb0I1MlFnQUFTTEtqSG5aQ0FBQXdJYWNlZGtJQUFCaVFxaDUyUWdBQUFQK3RIblpDQUFEb2JiRWVka0lBQU5EY3RCNTJRZ0FBdUV1NEhuWkNBQUNndXJzZWRrSUFBSWdwdng1MlFnQUFjSmpDSG5aQ0FBQllCOFllZGtJQUFFQjJ5UjUyUWdBQUtPWE1IblpDQUFBUVZOQWVka0lBQVBqQzB4NTJRZ0FBNERIWEhuWkNBQURJb05vZWRrSUFBTEFQM2g1MlFnQUFtSDdoSG5aQ0FBQ0E3ZVFlZGtJQUFHaGM2QjUyUWdBQVVNdnJIblpDQUFBNE91OGVka0lBQUNDcDhoNTJRZ0FBQ0JqMkhuWkNBQUR3aHZrZWRrSUFBTmoxL0I1MlFnQUF3R1FBSDNaQ0FBQ28wd01mZGtJQUFKQkNCeDkyUWdBQWVMRUtIM1pDQUFCZ0lBNGZka0lBQUVpUEVSOTJRZ0FBTVA0VUgzWkNBQUFZYlJnZmRrSUFBQURjR3g5MlFnQUE2RW9mSDNaQ0FBRFF1U0lmZGtJQUFMZ29KaDkyUWdBQW9KY3BIM1pDQUFDSUJpMGZka0lBQUhCMU1COTJRZ0FBV09RekgzWkMiLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6Wzk2XX0sInkiOnsiX19uZGFycmF5X18iOiJBQUFBQVBBSC96OEFBQURBaGNMM1B3QUFBSUFiZmZBL0FBQUFZR0p2NGo4QUFBREFLdzdsdndBQUFBRGRSZjYvQUFBQUFGSUNDY0FBQUFDQUVMTUZ3QUFBQUNEUFl3TEFBQUFBWUJzcC9yOEFBQUNnQzhIa3Z3QUFBR0FmME9JL0FBQUFRS1V3L1Q4QUFBRGdoby83UHdBQUFLQm83dmsvQUFBQVFFcE4rRDhBQUFCZ0VZTytQd0FBQUNEb2ZQUy9BQUFBb0FCeEJjQUFBQURnbEVBRndBQUFBRUFwRUFYQUFBQUFnTDNmQk1BQUFBQWdSL2tEd0FBQUFPRFFFZ1BBQUFBQXdPMTEyejhBQUFEQVNCL3lQd0FBQUFBV1lmMC9BQUFBb0hGUkJFQUFBQURBdXNIMlB3QUFBSUJJZ3RNL0FBQUE0Q3dCNnI4QUFBQ0FBbXY3dndBQUFHQzM2Z1RBQUFBQVlPMGZETUFBQUFEZ2JUSUN3QUFBQU9EY2lmQy9BQUFBSUJHSnlqOEFBQUNBcHNIeVB3QUFBSUFWR1FGQUFBQUFvRmZSQ0VBQUFBQWc0cUVCUUFBQUFFRFo1UFEvQUFBQW9MZ1gyajhBQUFEQUY5bm12d0FBQUFBR1gvMi9BQUFBQU1Db0I4QUFBQUFnNFVnQXdBQUFBS0FFMHZHL0FBQUFZRGVTeUw4QUFBQUFHeXpzUHdBQUFPQmhQdjgvQUFBQUlGc3pDRUFBQUFBZ05Ba0NRQUFBQUVBYXZ2Yy9BQUFBZ0pqVDVqOEFBQURnQVR2aHZ3QUFBQ0RPcFB5L0FBQUFvQTFXQ01BQUFBQWdHY0lDd0FBQUFFQkpYUHEvQUFBQWdNQm83cjhBQUFCZ1ZFclJQd0FBQUdDSzJmYy9BQUFBNEQrd0JVQUFBQURBNi9BQlFBQUFBQ0F2WS93L0FBQUF3SWJrOUQ4QUFBQUFGS0sydndBQUFFREp1UGUvQUFBQW9MZ0RCOEFBQUFCZzZvZ0R3QUFBQUFBY0RnREFBQUFBZ0pzbStiOEFBQUNna3VYU3Z3QUFBR0NrWis4L0FBQUFnSVFRQWtBQUFBQkFEMHNBUUFBQUFFQTBDLzAvQUFBQTRFbUErVDhBQUFCZ3JVL0VQd0FBQUlCZWJQUy9BQUFBWUZteEJjQUFBQURnOExvRXdBQUFBSUNJeEFQQUFBQUFBQ0RPQXNBQUFBQkEwTm52dndBQUFBQy9DZGMvQUFBQW9NZHgrejhBQUFDZ3U3UDhQd0FBQU1DdjlmMC9BQUFBd0tNMy96OEFBQUNBM3AzZ1B3QUFBSUNLTSsyL0FBQUE0RHpCQXNBQUFBRGdQTUVDd0FBQUFPQTh3UUxBIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOls5Nl19fX0sImlkIjoiNjJjM2YwZGMtNzQ2Yi00ZDIwLTgyOWItMDNjMWY2NDY2YTkzIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsImNvbHVtbl9uYW1lcyI6WyJ4IiwieSJdLCJkYXRhIjp7IngiOnsiX19uZGFycmF5X18iOiJBQUNBVnBzZGRrSUFBR2pGbmgxMlFnQUFVRFNpSFhaQ0FBQkF2TzBkZGtJQUFDZ3I4UjEyUWdBQUVKcjBIWFpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQURBaDVJZWRrSUFBS2oybFI1MlFnQUFrR1daSG5aQ0FBQ0E3ZVFlZGtJQUFHaGM2QjUyUWdBQVVNdnJIblpDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxNV19LCJ5Ijp7Il9fbmRhcnJheV9fIjoiQUFBQUFCeno0TDhBQUFDZ2Rnemh2d0FBQUVEUkplRy9BQUFBWUpwVDQ3OEFBQUFBT1RuanZ3QUFBS0RYSHVPL0FBQUE0SG5hNEw4QUFBQ2dHajNndndBQUFLQjJQOSsvQUFBQW9Gck1zTDhBQUFBQXI5Mnd2d0FBQUdBRDc3Qy9BQUFBWUVOc3NyOEFBQUJnUTJ5eXZ3QUFBR0JEYkxLLyIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTVdfX19LCJpZCI6ImU1MzU5OWY4LTY5NGMtNGYyOC1iMDhmLWMwOTFkZWI5OGY1MyIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiIwMzI4MDRiZC04YjcyLTQ5ZTEtOWE5Yy1mNzEyOGRlMTkwZWYiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrRm9ybWF0dGVyIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJkYTBjZDNmNC0yMjg4LTQ4ZDMtYjRkYS1iNDZiNDRiZWY1YjUiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJib3R0b21fdW5pdHMiOiJzY3JlZW4iLCJmaWxsX2FscGhhIjp7InZhbHVlIjowLjV9LCJmaWxsX2NvbG9yIjp7InZhbHVlIjoibGlnaHRncmV5In0sImxlZnRfdW5pdHMiOiJzY3JlZW4iLCJsZXZlbCI6Im92ZXJsYXkiLCJsaW5lX2FscGhhIjp7InZhbHVlIjoxLjB9LCJsaW5lX2NvbG9yIjp7InZhbHVlIjoiYmxhY2sifSwibGluZV9kYXNoIjpbNCw0XSwibGluZV93aWR0aCI6eyJ2YWx1ZSI6Mn0sInBsb3QiOm51bGwsInJlbmRlcl9tb2RlIjoiY3NzIiwicmlnaHRfdW5pdHMiOiJzY3JlZW4iLCJ0b3BfdW5pdHMiOiJzY3JlZW4ifSwiaWQiOiI3MmE5NWU1NC0zOGE2LTRkMWQtYmNiZi04ZGNjYmU1NjJkYTIiLCJ0eXBlIjoiQm94QW5ub3RhdGlvbiJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjEsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzFmNzdiNCIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiZTc4NTc0M2ItNGI3ZC00ZTQ3LTk2NmQtZDc1NzBjMWI2OWVjIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IkRhdGUvdGltZSIsImZvcm1hdHRlciI6eyJpZCI6IjAzMjgwNGJkLThiNzItNDllMS05YTljLWY3MTI4ZGUxOTBlZiIsInR5cGUiOiJEYXRldGltZVRpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6IjdjYzQyODBiLTk0NTUtNGEzZi1iOTdiLWVmZGJiMGQwZmE4NyIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiJlZmZhYWE4ZC00OWY1LTQ1ODMtYTYzMy0wOTVkZDY4ODE4NzIiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiZDBmOTdkMzAtNmQyNy00NDEyLWE2OTItMmY0MTkzMmYzYjg2IiwidHlwZSI6IkRhdGV0aW1lQXhpcyJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSw0LDcsMTAsMTMsMTYsMTksMjIsMjUsMjhdfSwiaWQiOiJjZTA0OTg3OS0xODYyLTQ3N2YtYjBlNC1mZDc0ZmJmY2I1OWQiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJvdmVybGF5Ijp7ImlkIjoiNzJhOTVlNTQtMzhhNi00ZDFkLWJjYmYtOGRjY2JlNTYyZGEyIiwidHlwZSI6IkJveEFubm90YXRpb24ifX0sImlkIjoiZGI0YjU3M2ItMDc4NS00YTZhLTkyOWEtYjc5ZGRhYWUzZDZhIiwidHlwZSI6IkJveFpvb21Ub29sIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDIsMyw0LDUsNiw3LDgsOSwxMCwxMSwxMiwxMywxNCwxNSwxNiwxNywxOCwxOSwyMCwyMSwyMiwyMywyNCwyNSwyNiwyNywyOCwyOSwzMCwzMV19LCJpZCI6ImI4Y2IyZWM4LWUwY2QtNDFhZS04YmM1LWYxMzkxY2Y4YTc1YiIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsLCJyZW5kZXJlcnMiOlt7ImlkIjoiNTVmZGYxMGUtOWMxZC00MDE5LWJkNWQtM2FiMTM3YmRjZmQ5IiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInRvb2x0aXBzIjpbWyJOYW1lIiwiU0VDT09SQS9DTkFQUyJdLFsiQmlhcyIsIi0yLjExIl0sWyJTa2lsbCIsIjEuMTQiXV19LCJpZCI6ImEwNTNiODZhLWVhZTctNDNhYi1hMDg2LWZiY2E5NWM2MTU0MyIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJTRUNPT1JBL0NOQVBTIn0sInJlbmRlcmVycyI6W3siaWQiOiI1NWZkZjEwZS05YzFkLTQwMTktYmQ1ZC0zYWIxMzdiZGNmZDkiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiYzk1NGQ0NTItNDE4ZS00MzVjLTkwOGItMjEwMzYyOGM4MzczIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifV0sInJvb3RfaWRzIjpbIjdjYzQyODBiLTk0NTUtNGEzZi1iOTdiLWVmZGJiMGQwZmE4NyJdfSwidGl0bGUiOiJCb2tlaCBBcHBsaWNhdGlvbiIsInZlcnNpb24iOiIwLjEyLjE0In19CiAgICAgICAgPC9zY3JpcHQ+CiAgICAgICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPgogICAgICAgICAgKGZ1bmN0aW9uKCkgewogICAgICAgICAgICB2YXIgZm4gPSBmdW5jdGlvbigpIHsKICAgICAgICAgICAgICBCb2tlaC5zYWZlbHkoZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgICAoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICBmdW5jdGlvbiBlbWJlZF9kb2N1bWVudChyb290KSB7CiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIHZhciBkb2NzX2pzb24gPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnNDczOWI5ZjItZDY1Ny00ZWRjLTg5OTQtZDcwMDBkZTMzZjE4JykudGV4dENvbnRlbnQ7CiAgICAgICAgICAgICAgICAgIHZhciByZW5kZXJfaXRlbXMgPSBbeyJkb2NpZCI6ImEyMTNlZmIzLTM3YzctNDM2Yy04NWM0LWJiNzJjNmUzZmVmOCIsImVsZW1lbnRpZCI6IjY2MTNkMjg1LWQwZWQtNGNiYS04ZjA2LWY5ZTg4Yjc5ODdlMyIsIm1vZGVsaWQiOiI3Y2M0MjgwYi05NDU1LTRhM2YtYjk3Yi1lZmRiYjBkMGZhODcifV07CiAgICAgICAgICAgICAgICAgIHJvb3QuQm9rZWguZW1iZWQuZW1iZWRfaXRlbXMoZG9jc19qc29uLCByZW5kZXJfaXRlbXMpOwogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgIGVtYmVkX2RvY3VtZW50KHJvb3QpOwogICAgICAgICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgICAgIHZhciBhdHRlbXB0cyA9IDA7CiAgICAgICAgICAgICAgICAgICAgdmFyIHRpbWVyID0gc2V0SW50ZXJ2YWwoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgICBhdHRlbXB0cysrOwogICAgICAgICAgICAgICAgICAgICAgaWYgKGF0dGVtcHRzID4gMTAwKSB7CiAgICAgICAgICAgICAgICAgICAgICAgIGNvbnNvbGUubG9nKCJCb2tlaDogRVJST1I6IFVuYWJsZSB0byBydW4gQm9rZWhKUyBjb2RlIGJlY2F1c2UgQm9rZWhKUyBsaWJyYXJ5IGlzIG1pc3NpbmciKQogICAgICAgICAgICAgICAgICAgICAgICBjbGVhckludGVydmFsKHRpbWVyKTsKICAgICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICB9LCAxMCwgcm9vdCkKICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgfSkod2luZG93KTsKICAgICAgICAgICAgICB9KTsKICAgICAgICAgICAgfTsKICAgICAgICAgICAgaWYgKGRvY3VtZW50LnJlYWR5U3RhdGUgIT0gImxvYWRpbmciKSBmbigpOwogICAgICAgICAgICBlbHNlIGRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoIkRPTUNvbnRlbnRMb2FkZWQiLCBmbik7CiAgICAgICAgICB9KSgpOwogICAgICAgIDwvc2NyaXB0PgogICAgPC9ib2R5Pgo8L2h0bWw+&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_fd4449a48aa34fb39548f023654fe71d.setContent(i_frame_e815084a792342028856a7425ef3c34e);
            

            marker_27e6e0b8c4fc4a8d8775d3f815e1edf3.bindPopup(popup_fd4449a48aa34fb39548f023654fe71d);

            
        
    

            var marker_f8f21740706149bca3df9b8e9d3ed22b = L.marker(
                [42.3539,-71.0503],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_e721f534260244a2a16047c38261931e = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_f8f21740706149bca3df9b8e9d3ed22b.setIcon(icon_e721f534260244a2a16047c38261931e);
            
    
            var popup_ebb67f7fd46c4effaeaa89cda24f5a1c = L.popup({maxWidth: '2650'});

            
                var i_frame_b13288dae94346cea1ea57ac5ff2b237 = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQ0Mzk3MDwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9Ijc3NDY0OGU4LTA4NGYtNDNmNC05MDcyLTQ2NmJmYTg4MDA3NCI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iZTljNzMzNDItNjVjNC00OGVlLTg4ZTYtOTQ1OTgwNjlhNGU4Ij4KICAgICAgICAgIHsiZTlkYjY4OWUtN2RlNC00NGFkLWFiOGYtYzZkYjE1MGEyZjBhIjp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjY4OGIxMjU1LTNjOTktNDcyYS05Mzc4LTI3NjMzYWIyMDA5YSIsInR5cGUiOiJQYW5Ub29sIn0seyJhdHRyaWJ1dGVzIjp7ImJlbG93IjpbeyJpZCI6IjI2N2U3YjU4LTdiODItNDE5My05ZWJhLTZjOGE0YmZkN2ZiYiIsInR5cGUiOiJEYXRldGltZUF4aXMifV0sImxlZnQiOlt7ImlkIjoiZTYxM2Q1MjUtYmRiMy00YTVhLTgzOWQtNjRhNzRhNmYxZDFhIiwidHlwZSI6IkxpbmVhckF4aXMifV0sInBsb3RfaGVpZ2h0IjoyNTAsInBsb3Rfd2lkdGgiOjc1MCwicmVuZGVyZXJzIjpbeyJpZCI6IjI2N2U3YjU4LTdiODItNDE5My05ZWJhLTZjOGE0YmZkN2ZiYiIsInR5cGUiOiJEYXRldGltZUF4aXMifSx7ImlkIjoiNmRkYmMzNzctYjdjYy00YTI4LWJkZDYtMGZjODY2MTViNWEyIiwidHlwZSI6IkdyaWQifSx7ImlkIjoiZTYxM2Q1MjUtYmRiMy00YTVhLTgzOWQtNjRhNzRhNmYxZDFhIiwidHlwZSI6IkxpbmVhckF4aXMifSx7ImlkIjoiNjhjZjhkOWEtY2Y4Yy00ZWY4LTlmYzAtYjA3ZTA3NzA2YTBmIiwidHlwZSI6IkdyaWQifSx7ImlkIjoiMGUxZmEwMWQtZDkyZi00ZTU0LTkyNmEtZjM3NjJiOTNjNGQ0IiwidHlwZSI6IkJveEFubm90YXRpb24ifSx7ImlkIjoiOTc4OWVhNWEtZjdkYS00MzkxLTk5ZTctMjYyOTIyOTc1YTYyIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImlkIjoiYjIxNWUzZTQtOGUyYy00YjQ0LWE0NDItZjMxY2FmNmI3MzNhIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImlkIjoiOGFhM2M0ZmQtOWUyMS00NWYzLTlhMjItZGFiYmRmNGViZjU0IiwidHlwZSI6IkxlZ2VuZCJ9XSwicmlnaHQiOlt7ImlkIjoiOGFhM2M0ZmQtOWUyMS00NWYzLTlhMjItZGFiYmRmNGViZjU0IiwidHlwZSI6IkxlZ2VuZCJ9XSwidGl0bGUiOnsiaWQiOiI5NTQxNWM5Mi1lYTZhLTQwMGQtOWU1MS0yYmJmYWExYTc5YmIiLCJ0eXBlIjoiVGl0bGUifSwidG9vbGJhciI6eyJpZCI6ImFmZDI5M2Y0LWZhZTEtNGY4NS05ZGJiLTQ5NzllNzJlNDA0YyIsInR5cGUiOiJUb29sYmFyIn0sInRvb2xiYXJfbG9jYXRpb24iOiJhYm92ZSIsInhfcmFuZ2UiOnsiaWQiOiIxOWE3YTU1MC00NjY1LTQ1ZDAtYmY4ZS01OWE0ZTk1ZTVkNDQiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSwieF9zY2FsZSI6eyJpZCI6IjQzNzAyMWM3LTVlZDktNDU1OS04NTdkLTgwYzllNDQ2ODc5NyIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LCJ5X3JhbmdlIjp7ImlkIjoiYzM5MmFhOGItZjUyNi00NDI5LTk5OGYtNmNjODJmMzg5Yzc1IiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInlfc2NhbGUiOnsiaWQiOiJkZmQyOTA1YS1kZDQxLTQ1NjktYmJhMC1kMDIwMTIyNDBmYjMiLCJ0eXBlIjoiTGluZWFyU2NhbGUifX0sImlkIjoiYTFjNGY5YzctNDZlMi00OTQ1LWFiYjktNjU2Y2MyZTgyNDU0Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiI0MzRhNjRiNy1jZTEyLTQzODAtYTU3My0zN2QxZWJkZDNmYjUiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMmNhMDJjIiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiI1MThkMGI2My05ZjAzLTRmMjYtYTAxYS03Y2VkYzlkNjg5ZmYiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDEsMiwzLDQsNSw2LDcsOCw5LDEwLDExXX0sImlkIjoiYTA3YTNlYTItMjE3Yi00MmQ0LTk5NDktZWU0ZmJlZDViZWQyIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6ImIyMTVlM2U0LThlMmMtNGI0NC1hNDQyLWYzMWNhZjZiNzMzYSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIk9ic2VydmF0aW9ucyJdLFsiQmlhcyIsIk5BIl0sWyJTa2lsbCIsIk5BIl1dfSwiaWQiOiJmZmQ3MTBiZi1hOThhLTRiZjAtYjkxNC02MzE4NjkzNDJhZGQiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDQsNywxMCwxMywxNiwxOSwyMiwyNSwyOF19LCJpZCI6ImI1MDNmNzEzLTAxNjUtNGYzYi04ZWI4LTU3MDQzN2U3ODZjMyIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRpbWVuc2lvbiI6MSwicGxvdCI6eyJpZCI6ImExYzRmOWM3LTQ2ZTItNDk0NS1hYmI5LTY1NmNjMmU4MjQ1NCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI0MzRhNjRiNy1jZTEyLTQzODAtYTU3My0zN2QxZWJkZDNmYjUiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifX0sImlkIjoiNjhjZjhkOWEtY2Y4Yy00ZWY4LTlmYzAtYjA3ZTA3NzA2YTBmIiwidHlwZSI6IkdyaWQifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImRmZDI5MDVhLWRkNDEtNDU2OS1iYmEwLWQwMjAxMjI0MGZiMyIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDQUFCQVV6Y2Zka0k9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfSwieSI6eyJfX25kYXJyYXlfXyI6ImZUODFYcnBKQVVCSTRYb1Vya2NHUUdtUjdYdy9OUWhBNlB1cDhkSk5CMENGNjFHNEhvVURRR01RV0RtMHlQdy8wMDFpRUZnNThELzAvZFI0NlNiUlA4cWhSYmJ6L2JTL21wbVptWm1adVQrV1E0dHM1L3ZsUDZhYnhDQ3djdlkvaGV0UnVCNkZBVUNObDI0U2c4QUhRSWdXMmM3M1V3dEFqR3puKzZueENrRGF6dmRUNDZVSFFBclhvM0E5Q2dKQXUwa01BaXVIOWovQnlxRkZ0dlBoUDNzVXJrZmhlc1MvcHB2RUlMQnkyTCtNYk9mN3FmR2lQejBLMTZOd1BlWS9Fb1BBeXFGRitEOU1ONGxCWU9VQ1FDWXhDS3djV2doQWV4U3VSK0Y2Q2tCV0RpMnluZThJUURaZXVra01BZ1ZBa3UxOFB6VmUvajkzdnA4YUw5M3dQNFhyVWJnZWhkTS9QTjlQalpkdXNyL0Q5U2hjajhMRlAyM24rNm54MHVrL1VyZ2VoZXRSK2ovVFRXSVFXRGtFUUE0dHNwM3Zwd3BBeXFGRnR2UDlEVUNTN1h3L05WNE5RSkx0ZkQ4MVhnbEFVcmdlaGV0UkEwQkFOVjY2U1F6NFA0WHJVYmdlaGVNL3dNcWhSYmJ6dmIveTBrMWlFRmpSdjNTVEdBUldEczAvajhMMUtGeVA3ajk5UHpWZXVrbjhQOUVpMi9sK2FnVkFxdkhTVFdJUUMwQkFOVjY2U1F3TlFBTXJoeGJaemdwQVhJL0M5U2hjQmtER1N6ZUpRV0FBUUFyWG8zQTlDdk0vL3RSNDZTWXg0RDhYMmM3M1UrUEZQN3gwa3hnRVZ1SS94a3MzaVVGZzlUKzI4LzNVZU9rQVFDVUdnWlZEaXdoQXdNcWhSYmJ6RDBBSXJCeGFaTHNSUUF3Q0s0Y1dXUkZBUFFyWG8zQTlEMEIzdnA4YUw5MEpRTVFnc0hKb2tRSkFKakVJckJ4YTlqOVdEaTJ5bmUvblAwU0xiT2Y3cWVVL3FNWkxONGxCOUQ4ek16TXpNek1BUUVvTUFpdUhGZ1ZBWXhCWU9iVElDMEEzaVVGZzVWQVFRQjFhWkR2Znp4QkE1S1dieENDd0RrRFA5MVBqcFpzSlFHcThkSk1ZQkFSQUF5dUhGdG5POXorUzdYdy9OVjdxUDUzdnA4WkxOK0UvWEkvQzlTaGM2ei80VStPbG04VDRQNDJYYmhLRHdBSkFMYktkNzZmR0NrRDJLRnlQd3ZVUFFNdWhSYmJ6L1JCQUJGWU9MYklkRUVDTmwyNFNnOEFMUU4wa0JvR1ZRd1pBc1hKb2tlMTgvVDh2M1NRR2daWHZQOUVpMi9sK2F0dy9PclRJZHI2ZjJqOU9ZaEJZT2JUd1B3QUFBQUFBQVB3L09yVElkcjZmQkVDbW04UWdzSElMUUtyeDBrMWlFQTlBa3UxOFB6VmVEMERQOTFQanBac01RSHNVcmtmaGVnZEFqR3puKzZueEFFQ1B3dlVvWEkvMFA5djVmbXE4ZE9NL0pqRUlyQnhhM0Q4M2lVRmc1ZERxUDJtUjdYdy9OZmcvOHRKTlloQllBa0NrY0QwSzE2TUlRTzU4UHpWZXVnMUFTT0Y2Rks1SEQwREpkcjZmR2k4TlFPU2xtOFFnc0FoQUJGWU9MYktkQWtBRVZnNHRzcDMzUDlyTzkxUGpwZWMvSEZwa085OVAxVDg9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfX19LCJpZCI6IjMxYTBhMWZhLWIwZWMtNGUxMC1iMWViLWRhMWVjMjdkYWRjNiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7ImNsaWNrX3BvbGljeSI6Im11dGUiLCJpdGVtcyI6W3siaWQiOiIxZjk3OGM1NS03YzViLTQzMmEtYWI1NC02Y2I5MjUwNDdmOWIiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiaWQiOiJhZDg3NTI4ZS02ODFjLTQ5MGQtYTJhMi05NGFkYTA5MDYwMWUiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9XSwibG9jYXRpb24iOlswLDYwXSwicGxvdCI6eyJpZCI6ImExYzRmOWM3LTQ2ZTItNDk0NS1hYmI5LTY1NmNjMmU4MjQ1NCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9fSwiaWQiOiI4YWEzYzRmZC05ZTIxLTQ1ZjMtOWEyMi1kYWJiZGY0ZWJmNTQiLCJ0eXBlIjoiTGVnZW5kIn0seyJhdHRyaWJ1dGVzIjp7InNvdXJjZSI6eyJpZCI6IjMxYTBhMWZhLWIwZWMtNGUxMC1iMWViLWRhMWVjMjdkYWRjNiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn19LCJpZCI6IjQyNzI4MmY3LTc5ZjEtNDZmMi04NTBjLTc4YmVjN2IwMDY4YiIsInR5cGUiOiJDRFNWaWV3In0seyJhdHRyaWJ1dGVzIjp7ImJhc2UiOjYwLCJtYW50aXNzYXMiOlsxLDIsNSwxMCwxNSwyMCwzMF0sIm1heF9pbnRlcnZhbCI6MTgwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjEwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiI2ZWMxNThjZS0zMDRiLTRjNzktOWMxYi0zNTE3OTFmYTZmMjMiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJPYnNlcnZhdGlvbnMifSwicmVuZGVyZXJzIjpbeyJpZCI6ImIyMTVlM2U0LThlMmMtNGI0NC1hNDQyLWYzMWNhZjZiNzMzYSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dfSwiaWQiOiJhZDg3NTI4ZS02ODFjLTQ5MGQtYTJhMi05NGFkYTA5MDYwMWUiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiYXR0cmlidXRlcyI6eyJiYXNlIjoyNCwibWFudGlzc2FzIjpbMSwyLDQsNiw4LDEyXSwibWF4X2ludGVydmFsIjo0MzIwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjM2MDAwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiJlMjBhMzYxNy02YTEzLTQxMTAtYmFmMS0yODJjZmI5ZWFkYjciLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw0LDhdfSwiaWQiOiJkYWRlOTI1NS04OWQ4LTQ1MjMtYWNhNi05Y2I1OGRlODEyZjkiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRhdGFfc291cmNlIjp7ImlkIjoiMjQ0ZWQ5ZjgtY2U0OC00OWUwLWIzZDMtODIyNWNiYTZjMTA0IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSwiZ2x5cGgiOnsiaWQiOiI1MThkMGI2My05ZjAzLTRmMjYtYTAxYS03Y2VkYzlkNjg5ZmYiLCJ0eXBlIjoiTGluZSJ9LCJob3Zlcl9nbHlwaCI6bnVsbCwibXV0ZWRfZ2x5cGgiOm51bGwsIm5vbnNlbGVjdGlvbl9nbHlwaCI6eyJpZCI6IjgzZWY2NDlkLTNlMmItNDQ1My04ZmFmLWVkMmExNzY4NWQzMyIsInR5cGUiOiJMaW5lIn0sInNlbGVjdGlvbl9nbHlwaCI6bnVsbCwidmlldyI6eyJpZCI6Ijk1OTY3OWNhLWY3YmMtNGJhOS04YTFlLTE0OWNmNWY4ZGU0YyIsInR5cGUiOiJDRFNWaWV3In19LCJpZCI6Ijk3ODllYTVhLWY3ZGEtNDM5MS05OWU3LTI2MjkyMjk3NWE2MiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJhdHRyaWJ1dGVzIjp7Im1hbnRpc3NhcyI6WzEsMiw1XSwibWF4X2ludGVydmFsIjo1MDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiJjNGNlZjRjZC0zZGUxLTRhNDgtOGEyNi1lNzRmZDQ3MGNiM2UiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6IjE5YTdhNTUwLTQ2NjUtNDVkMC1iZjhlLTU5YTRlOTVlNWQ0NCIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6eyJudW1fbWlub3JfdGlja3MiOjUsInRpY2tlcnMiOlt7ImlkIjoiYzRjZWY0Y2QtM2RlMS00YTQ4LThhMjYtZTc0ZmQ0NzBjYjNlIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6IjZlYzE1OGNlLTMwNGItNGM3OS05YzFiLTM1MTc5MWZhNmYyMyIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiJlMjBhMzYxNy02YTEzLTQxMTAtYmFmMS0yODJjZmI5ZWFkYjciLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiODA5NDZjMDEtOWI5Mi00YTYwLWE1ZDYtMjU4NTBkZTk2ZmM0IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiYjUwM2Y3MTMtMDE2NS00ZjNiLThlYjgtNTcwNDM3ZTc4NmMzIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiZTI5Y2JlOTctNzBmYS00N2Y0LWI0MWEtNjY2MThjZjVlMDExIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiYzM2NTdlNzEtMzZlNC00OTc1LWFhZGUtMjNjZDA4YjhlMjc3IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiYTA3YTNlYTItMjE3Yi00MmQ0LTk5NDktZWU0ZmJlZDViZWQyIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiIyM2IzNjM3NS0yMTBhLTRlOTAtODdhZC03YjA2MDA0YjVjNDAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6ImRhZGU5MjU1LTg5ZDgtNDUyMy1hY2E2LTljYjU4ZGU4MTJmOSIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiODNmY2UxNzAtYTUwOS00OTZiLTlmODUtNzFiNTgyNzlmOGVlIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiJkYzlmMjliNi00MmI3LTQzMTItOGExZS04YTE3OTczYWYxNTYiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifV19LCJpZCI6IjdkMjFhOThjLWY1M2UtNGZmMC1hOTg0LThhNWVhOTBjZjk2OCIsInR5cGUiOiJEYXRldGltZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjEsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzFmNzdiNCIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiYjViYTA0MTQtMzMyYi00Y2ZhLTg4ZWUtZmQ4NTA4N2Q3NGFhIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGx9LCJpZCI6ImMzOTJhYThiLWY1MjYtNDQyOS05OThmLTZjYzgyZjM4OWM3NSIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjBdfSwieSI6eyJfX25kYXJyYXlfXyI6IkFBQUFBSS9hNlQ4QUFBQ0FEM0h4UHdBQUFJRFg5UFUvQUFBQWdKOTQrajhBQUFBQWM2L3VQd0FBQUVCTzI5QS9BQUFBb0VtbzI3OEFBQUJBWTBQb3Z3QUFBTUJRV2ZHL0FBQUFBUENROXI4QUFBQUFUbmZsdndBQUFLQWdtckUvQUFBQUlOYmQ2VDhBQUFEQVcvanlQd0FBQUdETUFmay9BQUFBQUQwTC96OEFBQUFBNU1uelB3QUFBTUFWRWVFL0FBQUFJSEhHeGI4QUFBQ0FubG5udndBQUFFRFFvUFMvQUFBQVlOR1UvYjhBQUFBZ002THp2d0FBQU1BcFgrTy9BQUFBZ0ZuQ2tEOEFBQURnQmN6alB3QUFBSUQ4aVBNL0FBQUFBUFlyL1Q4QUFBRGcwcGIwUHdBQUFJQmZBK2cvQUFBQW9HUmt5ejhBQUFBQVZ6M1Z2d0FBQUNCd0Z1eS9BQUFBWUJySDlyOEFBQUJBbGdudHZ3QUFBTUR2Q2RtL0FBQUF3RFQ5dno4QUFBRGdSVExvUHdBQUFLQnlNdlkvQUFBQUlPRWxBRUFBQUFCQUNuNzRQd0FBQUdCU3NQQS9BQUFBd0RURjRUOEFBQUFBNzI3QnZ3QUFBRUNzZk9xL0FBQUFZTTVPK0w4QUFBREFicGJ5dndBQUFBQWV2T20vQUFBQVlMMlczTDhBQUFEZ0xoblNQd0FBQU1CR012QS9BQUFBNEVIZSt6OEFBQURBOE9YM1B3QUFBSUNmN2ZNL0FBQUF3SnpxN3o4QUFBQmc0VmJSUHdBQUFPQjJKOTIvQUFBQXdIUHA4cjhBQUFCZ3N5anR2d0FBQUNCL2Z1Uy9BQUFBQUphbzE3OEFBQUNneEJ6YlB3QUFBT0NIZVBNL0FBQUFRTzhVQUVBQUFBRGc5UnYvUHdBQUFFQU5EdjQvQUFBQW9DUUEvVDhBQUFEQU1YbnhQd0FBQU9EN3lOYy9BQUFBZ005UzFyOEFBQURBR3dyVXZ3QUFBQUJvd2RHL0FBQUFvR2p4enI4QUFBQWc2dzNlUHdBQUFLQWk1ZkkvQUFBQWdNcEcvajhBQUFEZ3V6VC9Qd0FBQUtCV0VRQkFBQUFBWUUrSUFFQUFBQURBZ3FUMFB3QUFBRUROY09BL0FBQUFvTlhPMEw4QUFBQmdZZVhYdndBQUFFRHQrOTYvQUFBQWdEd0o0NzhBQUFCZ292VERQd0FBQUtDTkErMC9BQUFBWVBtRStqOEFBQURnUXB2OVB3QUFBRURHV0FCQUFBQUFBT3ZqQVVBQUFBRGdPclAzUHdBQUFLQS9QZWMvQUFBQTROSituYjhBQUFBQUgyblV2d0FBQUlBb2ZlTy9BQUFBWU1IRjdMOEFBQUJneW5ESXZ3QUFBRUJjamVBL0FBQUFnSFdiOHo4QUFBRGdLZ3o1UHdBQUFHRGdmUDQvQUFBQTRNcjJBVUFBQUFCZ3NBWDVQd0FBQU1DVk8rdy9BQUFBb0N1dnlUOEFBQUNnYnlITHZ3QUFBTUNDL09PL0FBQUF3RlNZOEw4QUFBQ2dTY0hadndBQUFHQi92YzAvQUFBQWdHUy82ejhBQUFBZ3pxNzBQd0FBQU9EcGZmcy9BQUFBNElJbUFVQUFBQUNBLzcvNFB3QUFBRUR5WmU0L0FBQUFZTXVYMWo4QUFBQmd5NWZXUHdBQUFHRExsOVkvIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjBdfX19LCJpZCI6IjI0NGVkOWY4LWNlNDgtNDllMC1iM2QzLTgyMjVjYmE2YzEwNCIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDE1XX0sImlkIjoiYzM2NTdlNzEtMzZlNC00OTc1LWFhZGUtMjNjZDA4YjhlMjc3IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsMiwzLDQsNSw2LDcsOCw5LDEwLDExLDEyLDEzLDE0LDE1LDE2LDE3LDE4LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI2LDI3LDI4LDI5LDMwLDMxXX0sImlkIjoiODA5NDZjMDEtOWI5Mi00YTYwLWE1ZDYtMjU4NTBkZTk2ZmM0IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF0YV9zb3VyY2UiOnsiaWQiOiIzMWEwYTFmYS1iMGVjLTRlMTAtYjFlYi1kYTFlYzI3ZGFkYzYiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LCJnbHlwaCI6eyJpZCI6ImRiNzg2ZGQ2LWQ2ODAtNDMxZC05MGE5LWNmZmU2ODk5ODc0ZSIsInR5cGUiOiJMaW5lIn0sImhvdmVyX2dseXBoIjpudWxsLCJtdXRlZF9nbHlwaCI6bnVsbCwibm9uc2VsZWN0aW9uX2dseXBoIjp7ImlkIjoiYjViYTA0MTQtMzMyYi00Y2ZhLTg4ZWUtZmQ4NTA4N2Q3NGFhIiwidHlwZSI6IkxpbmUifSwic2VsZWN0aW9uX2dseXBoIjpudWxsLCJ2aWV3Ijp7ImlkIjoiNDI3MjgyZjctNzlmMS00NmYyLTg1MGMtNzhiZWM3YjAwNjhiIiwidHlwZSI6IkNEU1ZpZXcifX0sImlkIjoiYjIxNWUzZTQtOGUyYy00YjQ0LWE0NDItZjMxY2FmNmI3MzNhIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IkRhdGUvdGltZSIsImZvcm1hdHRlciI6eyJpZCI6IjJmODc3ZTllLTY2MmItNGYyNi1hZTlkLTNiMWMzYjM0YjQ0YyIsInR5cGUiOiJEYXRldGltZVRpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6ImExYzRmOWM3LTQ2ZTItNDk0NS1hYmI5LTY1NmNjMmU4MjQ1NCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI3ZDIxYTk4Yy1mNTNlLTRmZjAtYTk4NC04YTVlYTkwY2Y5NjgiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiMjY3ZTdiNTgtN2I4Mi00MTkzLTllYmEtNmM4YTRiZmQ3ZmJiIiwidHlwZSI6IkRhdGV0aW1lQXhpcyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNDliZDcyOTAtNDRjMC00ODIzLWFkZjQtYjAzYTM2YWFiYWVjIiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJvdmVybGF5Ijp7ImlkIjoiMGUxZmEwMWQtZDkyZi00ZTU0LTkyNmEtZjM3NjJiOTNjNGQ0IiwidHlwZSI6IkJveEFubm90YXRpb24ifX0sImlkIjoiMDBjZTFmZTgtNmNlYy00ZDFhLWEzOWMtMzFjZjIyMzFmM2E4IiwidHlwZSI6IkJveFpvb21Ub29sIn0seyJhdHRyaWJ1dGVzIjp7ImF4aXNfbGFiZWwiOiJXYXRlciBIZWlnaHQgKG0pIiwiZm9ybWF0dGVyIjp7ImlkIjoiOWJhZGJjYmUtZjI3Zi00NDUxLWJkYWMtNDU4NTY1NzMwM2FmIiwidHlwZSI6IkJhc2ljVGlja0Zvcm1hdHRlciJ9LCJwbG90Ijp7ImlkIjoiYTFjNGY5YzctNDZlMi00OTQ1LWFiYjktNjU2Y2MyZTgyNDU0Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6IjQzNGE2NGI3LWNlMTItNDM4MC1hNTczLTM3ZDFlYmRkM2ZiNSIsInR5cGUiOiJCYXNpY1RpY2tlciJ9fSwiaWQiOiJlNjEzZDUyNS1iZGIzLTRhNWEtODM5ZC02NGE3NGE2ZjFkMWEiLCJ0eXBlIjoiTGluZWFyQXhpcyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMmY4NzdlOWUtNjYyYi00ZjI2LWFlOWQtM2IxYzNiMzRiNDRjIiwidHlwZSI6IkRhdGV0aW1lVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6Ijk3ODllYTVhLWY3ZGEtNDM5MS05OWU3LTI2MjkyMjk3NWE2MiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIk5FQ09GU19Cb3N0b24iXSxbIkJpYXMiLCItMS42MCJdLFsiU2tpbGwiLCIwLjM2Il1dfSwiaWQiOiJjYThkMzIyNC0xMDMwLTQzNjAtOWUxYi01OWMzMTUzMjhkZmIiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJhdHRyaWJ1dGVzIjp7ImFjdGl2ZV9kcmFnIjoiYXV0byIsImFjdGl2ZV9pbnNwZWN0IjoiYXV0byIsImFjdGl2ZV9zY3JvbGwiOiJhdXRvIiwiYWN0aXZlX3RhcCI6ImF1dG8iLCJ0b29scyI6W3siaWQiOiI2ODhiMTI1NS0zYzk5LTQ3MmEtOTM3OC0yNzYzM2FiMjAwOWEiLCJ0eXBlIjoiUGFuVG9vbCJ9LHsiaWQiOiIwMGNlMWZlOC02Y2VjLTRkMWEtYTM5Yy0zMWNmMjIzMWYzYTgiLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImlkIjoiNDliZDcyOTAtNDRjMC00ODIzLWFkZjQtYjAzYTM2YWFiYWVjIiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiaWQiOiJjYThkMzIyNC0xMDMwLTQzNjAtOWUxYi01OWMzMTUzMjhkZmIiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJpZCI6ImZmZDcxMGJmLWE5OGEtNGJmMC1iOTE0LTYzMTg2OTM0MmFkZCIsInR5cGUiOiJIb3ZlclRvb2wifV19LCJpZCI6ImFmZDI5M2Y0LWZhZTEtNGY4NS05ZGJiLTQ5NzllNzJlNDA0YyIsInR5cGUiOiJUb29sYmFyIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiTkVDT0ZTX0Jvc3RvbiJ9LCJyZW5kZXJlcnMiOlt7ImlkIjoiOTc4OWVhNWEtZjdkYS00MzkxLTk5ZTctMjYyOTIyOTc1YTYyIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV19LCJpZCI6IjFmOTc4YzU1LTdjNWItNDMyYS1hYjU0LTZjYjkyNTA0N2Y5YiIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDgsMTUsMjJdfSwiaWQiOiJlMjljYmU5Ny03MGZhLTQ3ZjQtYjQxYS02NjYxOGNmNWUwMTEiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiOWJhZGJjYmUtZjI3Zi00NDUxLWJkYWMtNDU4NTY1NzMwM2FmIiwidHlwZSI6IkJhc2ljVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6eyJib3R0b21fdW5pdHMiOiJzY3JlZW4iLCJmaWxsX2FscGhhIjp7InZhbHVlIjowLjV9LCJmaWxsX2NvbG9yIjp7InZhbHVlIjoibGlnaHRncmV5In0sImxlZnRfdW5pdHMiOiJzY3JlZW4iLCJsZXZlbCI6Im92ZXJsYXkiLCJsaW5lX2FscGhhIjp7InZhbHVlIjoxLjB9LCJsaW5lX2NvbG9yIjp7InZhbHVlIjoiYmxhY2sifSwibGluZV9kYXNoIjpbNCw0XSwibGluZV93aWR0aCI6eyJ2YWx1ZSI6Mn0sInBsb3QiOm51bGwsInJlbmRlcl9tb2RlIjoiY3NzIiwicmlnaHRfdW5pdHMiOiJzY3JlZW4iLCJ0b3BfdW5pdHMiOiJzY3JlZW4ifSwiaWQiOiIwZTFmYTAxZC1kOTJmLTRlNTQtOTI2YS1mMzc2MmI5M2M0ZDQiLCJ0eXBlIjoiQm94QW5ub3RhdGlvbiJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNDM3MDIxYzctNWVkOS00NTU5LTg1N2QtODBjOWU0NDY4Nzk3IiwidHlwZSI6IkxpbmVhclNjYWxlIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsMiw0LDYsOCwxMF19LCJpZCI6IjIzYjM2Mzc1LTIxMGEtNGU5MC04N2FkLTdiMDYwMDRiNWM0MCIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsicGxvdCI6bnVsbCwidGV4dCI6Ijg0NDM5NzAifSwiaWQiOiI5NTQxNWM5Mi1lYTZhLTQwMGQtOWU1MS0yYmJmYWExYTc5YmIiLCJ0eXBlIjoiVGl0bGUifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjgzZWY2NDlkLTNlMmItNDQ1My04ZmFmLWVkMmExNzY4NWQzMyIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiJkYzlmMjliNi00MmI3LTQzMTItOGExZS04YTE3OTczYWYxNTYiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiMjQ0ZWQ5ZjgtY2U0OC00OWUwLWIzZDMtODIyNWNiYTZjMTA0IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiOTU5Njc5Y2EtZjdiYy00YmE5LThhMWUtMTQ5Y2Y1ZjhkZTRjIiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiJjcmltc29uIiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJkYjc4NmRkNi1kNjgwLTQzMWQtOTBhOS1jZmZlNjg5OTg3NGUiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJwbG90Ijp7ImlkIjoiYTFjNGY5YzctNDZlMi00OTQ1LWFiYjktNjU2Y2MyZTgyNDU0Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6IjdkMjFhOThjLWY1M2UtNGZmMC1hOTg0LThhNWVhOTBjZjk2OCIsInR5cGUiOiJEYXRldGltZVRpY2tlciJ9fSwiaWQiOiI2ZGRiYzM3Ny1iN2NjLTRhMjgtYmRkNi0wZmM4NjYxNWI1YTIiLCJ0eXBlIjoiR3JpZCJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDZdfSwiaWQiOiI4M2ZjZTE3MC1hNTA5LTQ5NmItOWY4NS03MWI1ODI3OWY4ZWUiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn1dLCJyb290X2lkcyI6WyJhMWM0ZjljNy00NmUyLTQ5NDUtYWJiOS02NTZjYzJlODI0NTQiXX0sInRpdGxlIjoiQm9rZWggQXBwbGljYXRpb24iLCJ2ZXJzaW9uIjoiMC4xMi4xNCJ9fQogICAgICAgIDwvc2NyaXB0PgogICAgICAgIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgICAgICAgIChmdW5jdGlvbigpIHsKICAgICAgICAgICAgdmFyIGZuID0gZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgQm9rZWguc2FmZWx5KGZ1bmN0aW9uKCkgewogICAgICAgICAgICAgICAgKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgZnVuY3Rpb24gZW1iZWRfZG9jdW1lbnQocm9vdCkgewogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB2YXIgZG9jc19qc29uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2U5YzczMzQyLTY1YzQtNDhlZS04OGU2LTk0NTk4MDY5YTRlOCcpLnRleHRDb250ZW50OwogICAgICAgICAgICAgICAgICB2YXIgcmVuZGVyX2l0ZW1zID0gW3siZG9jaWQiOiJlOWRiNjg5ZS03ZGU0LTQ0YWQtYWI4Zi1jNmRiMTUwYTJmMGEiLCJlbGVtZW50aWQiOiI3NzQ2NDhlOC0wODRmLTQzZjQtOTA3Mi00NjZiZmE4ODAwNzQiLCJtb2RlbGlkIjoiYTFjNGY5YzctNDZlMi00OTQ1LWFiYjktNjU2Y2MyZTgyNDU0In1dOwogICAgICAgICAgICAgICAgICByb290LkJva2VoLmVtYmVkLmVtYmVkX2l0ZW1zKGRvY3NfanNvbiwgcmVuZGVyX2l0ZW1zKTsKICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgICAgICB2YXIgYXR0ZW1wdHMgPSAwOwogICAgICAgICAgICAgICAgICAgIHZhciB0aW1lciA9IHNldEludGVydmFsKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZW1iZWRfZG9jdW1lbnQocm9vdCk7CiAgICAgICAgICAgICAgICAgICAgICAgIGNsZWFySW50ZXJ2YWwodGltZXIpOwogICAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgICAgYXR0ZW1wdHMrKzsKICAgICAgICAgICAgICAgICAgICAgIGlmIChhdHRlbXB0cyA+IDEwMCkgewogICAgICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZygiQm9rZWg6IEVSUk9SOiBVbmFibGUgdG8gcnVuIEJva2VoSlMgY29kZSBiZWNhdXNlIEJva2VoSlMgbGlicmFyeSBpcyBtaXNzaW5nIikKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgfSwgMTAsIHJvb3QpCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0pKHdpbmRvdyk7CiAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgIH07CiAgICAgICAgICAgIGlmIChkb2N1bWVudC5yZWFkeVN0YXRlICE9ICJsb2FkaW5nIikgZm4oKTsKICAgICAgICAgICAgZWxzZSBkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJET01Db250ZW50TG9hZGVkIiwgZm4pOwogICAgICAgICAgfSkoKTsKICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPg==&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_ebb67f7fd46c4effaeaa89cda24f5a1c.setContent(i_frame_b13288dae94346cea1ea57ac5ff2b237);
            

            marker_f8f21740706149bca3df9b8e9d3ed22b.bindPopup(popup_ebb67f7fd46c4effaeaa89cda24f5a1c);

            
        
    

            var marker_afb918df9f2d4152b6d07c069e1ea90b = L.marker(
                [41.7043,-71.1641],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_64d9a2f4f719431883eab94bbd2c31a3 = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_afb918df9f2d4152b6d07c069e1ea90b.setIcon(icon_64d9a2f4f719431883eab94bbd2c31a3);
            
    
            var popup_2ca7162a30c04bb3ba7198faf13c6310 = L.popup({maxWidth: '2650'});

            
                var i_frame_8cfc1082e27842f99ecd18c3485f6c4c = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQ0NzM4NjwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9ImUxOWE4ZTE4LWYxZTQtNGE4MC05YmMzLTQ2ZWEzODVjNzY2MiI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iZTE2ODhmOTgtZWE0Ni00NDdiLTg5MDktZmE5OTVkZjgzZWNkIj4KICAgICAgICAgIHsiZjUwMTgwZWMtYmFiYy00ODU1LTllNGMtYzY2NDc5MmY4NGNjIjp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjgxMzJkMDk0LTc1MzgtNDg1Ny04MWM2LWFkYmFhZTk4NDcwMSIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsNCw3LDEwLDEzLDE2LDE5LDIyLDI1LDI4XX0sImlkIjoiMzdmNmE0MmUtZTk1Zi00YWIwLWJlNzMtOWMzMWI0Zjc5MTNhIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsInJlbmRlcmVycyI6W3siaWQiOiI2YmMwZmJiZi1lOGViLTQ4ZjAtYTI0OC05OGNiZDNiNDQzYTIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XSwidG9vbHRpcHMiOltbIk5hbWUiLCJPYnNlcnZhdGlvbnMiXSxbIkJpYXMiLCJOQSJdLFsiU2tpbGwiLCJOQSJdXX0sImlkIjoiMzBlOWI2ZmQtZGUyOC00NDdjLTllNGMtYWM2Mzk5YzUwNTI3IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6IjUwZDQyM2I5LWRhNTktNGQ5MS1iMDgyLWMwNTY5YzlmY2VkNCIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiNWYyNmY4NTEtMTE0Ny00MjBkLTkwNDEtNDcwNjlhNWNkMzgyIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiIwZjk2ZDUwMC02YWI1LTQzZDctOTUwNy0yNWIzMDE3NTY5YzgiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiI5MzQwZDg0Ny00ZGNhLTQ3ZmYtOTA5NS1kNDZiMzdkYjRiNWMiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiI2YmMwZmJiZi1lOGViLTQ4ZjAtYTI0OC05OGNiZDNiNDQzYTIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSw4LDE1LDIyXX0sImlkIjoiOTMwOTgwMDYtN2Y2OS00YmM2LTg5NTctOGNlZTUwNmVlMmFmIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsMTVdfSwiaWQiOiJkZmJhMzhkYy1kMTliLTRiNGEtYTJhZC0wMmQzYjQwZTU3ODciLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDZdfSwiaWQiOiJmZDljMTE1Mi02ZDc5LTRhZDAtYjA3Mi01NTU2YWQ4ZjQzZWMiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiI1NGJjOWI3Yy0yYjUzLTRkNTctODNhMy0wMzQ5OTY2YTgyMTkiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjYzNGY1ZjFhLTRhNTQtNGI3Mi04YmRhLWUyZDE5Zjk2YjQxOCIsInR5cGUiOiJZZWFyc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJudW1fbWlub3JfdGlja3MiOjUsInRpY2tlcnMiOlt7ImlkIjoiOTY1MzI2YWUtZmMxMy00ZWJhLWFlMTEtZjc1YTYxNGU2YTlhIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6IjhiNWZmM2FiLWJkM2YtNGZiMS05N2RlLTExOWVkNGJjY2RjNSIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiI5OTQ5ZjFmOS03NjA1LTRkMTAtYTYyNi1lMzE2ZDdmNWEzYzkiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiMjBiNGYwNDAtYzFiMy00Y2JiLThiM2UtMzkyYzk5MzFhZDQxIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiMzdmNmE0MmUtZTk1Zi00YWIwLWJlNzMtOWMzMWI0Zjc5MTNhIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiOTMwOTgwMDYtN2Y2OS00YmM2LTg5NTctOGNlZTUwNmVlMmFmIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiZGZiYTM4ZGMtZDE5Yi00YjRhLWEyYWQtMDJkM2I0MGU1Nzg3IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImlkIjoiYzBkMGRjMmEtYWYzMC00YzQ4LTg0NWYtZThmZDZkZjM3YjFmIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiI1MWQ4ZDQ5Ni1hZDk0LTRjMDMtYmJiZS1mMjc0ZmZjNWIyNzAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6ImRjYWI2Y2Q4LWUzMmEtNDg5NC1iMzM3LTg3OWZlZmUyNjViYiIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiZmQ5YzExNTItNmQ3OS00YWQwLWIwNzItNTU1NmFkOGY0M2VjIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiI2MzRmNWYxYS00YTU0LTRiNzItOGJkYS1lMmQxOWY5NmI0MTgiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifV19LCJpZCI6ImZjNTVlZTI4LWM0OGUtNGE3MS1hOGJjLWFlZWQwNDdjNjMyZCIsInR5cGUiOiJEYXRldGltZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJtYW50aXNzYXMiOlsxLDIsNV0sIm1heF9pbnRlcnZhbCI6NTAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiOTY1MzI2YWUtZmMxMy00ZWJhLWFlMTEtZjc1YTYxNGU2YTlhIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiIwZjk2ZDUwMC02YWI1LTQzZDctOTUwNy0yNWIzMDE3NTY5YzgiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMTdmZTlkZDQtN2RlNy00ZTU1LTg3MDgtYTlmZWUzM2VkMzdhIiwidHlwZSI6IkxpbmVhclNjYWxlIn0seyJhdHRyaWJ1dGVzIjp7ImJvdHRvbV91bml0cyI6InNjcmVlbiIsImZpbGxfYWxwaGEiOnsidmFsdWUiOjAuNX0sImZpbGxfY29sb3IiOnsidmFsdWUiOiJsaWdodGdyZXkifSwibGVmdF91bml0cyI6InNjcmVlbiIsImxldmVsIjoib3ZlcmxheSIsImxpbmVfYWxwaGEiOnsidmFsdWUiOjEuMH0sImxpbmVfY29sb3IiOnsidmFsdWUiOiJibGFjayJ9LCJsaW5lX2Rhc2giOls0LDRdLCJsaW5lX3dpZHRoIjp7InZhbHVlIjoyfSwicGxvdCI6bnVsbCwicmVuZGVyX21vZGUiOiJjc3MiLCJyaWdodF91bml0cyI6InNjcmVlbiIsInRvcF91bml0cyI6InNjcmVlbiJ9LCJpZCI6ImJhMzNlMjVkLTQ3NjUtNGIyNS04YzkyLWY2ODM4ZTRlMzg4YyIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOnsiaWQiOiJmMWEwNDE0My01MDE5LTQ2ZTMtOTVmMi1kODQ1NjQxY2EyYjYiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiZmM1NWVlMjgtYzQ4ZS00YTcxLWE4YmMtYWVlZDA0N2M2MzJkIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6IjA3ODk2YWMzLTFmYjQtNDk3MS1iNTM0LWRjY2U0Y2Q5ODJkMSIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiT2JzZXJ2YXRpb25zIn0sInJlbmRlcmVycyI6W3siaWQiOiI2YmMwZmJiZi1lOGViLTQ4ZjAtYTI0OC05OGNiZDNiNDQzYTIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiYzhjY2E1NGQtODdmMS00MDI4LTgyNmYtODI0MjA0MzgzYmVmIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsiYWN0aXZlX2RyYWciOiJhdXRvIiwiYWN0aXZlX2luc3BlY3QiOiJhdXRvIiwiYWN0aXZlX3Njcm9sbCI6ImF1dG8iLCJhY3RpdmVfdGFwIjoiYXV0byIsInRvb2xzIjpbeyJpZCI6IjczYzlkMjIzLWRkODctNDhhOC04Y2ZkLWQyMTVhYjk2ZjY2NyIsInR5cGUiOiJQYW5Ub29sIn0seyJpZCI6ImMyNTVlYzk5LWVjMjAtNDM2YS04NWYzLTg5YWYxMTdhODVkYiIsInR5cGUiOiJCb3hab29tVG9vbCJ9LHsiaWQiOiJhNjY0NDliNi01YWJiLTRjZGQtYTJiZC1kMjUyNmRlZWJiYWYiLCJ0eXBlIjoiUmVzZXRUb29sIn0seyJpZCI6IjMwZTliNmZkLWRlMjgtNDQ3Yy05ZTRjLWFjNjM5OWM1MDUyNyIsInR5cGUiOiJIb3ZlclRvb2wifV19LCJpZCI6IjQyYzFmYzU0LTg2MWEtNDZhMy04YWU1LTYxNjJhZDM1NTU5MiIsInR5cGUiOiJUb29sYmFyIn0seyJhdHRyaWJ1dGVzIjp7ImF4aXNfbGFiZWwiOiJXYXRlciBIZWlnaHQgKG0pIiwiZm9ybWF0dGVyIjp7ImlkIjoiODEzMmQwOTQtNzUzOC00ODU3LTgxYzYtYWRiYWFlOTg0NzAxIiwidHlwZSI6IkJhc2ljVGlja0Zvcm1hdHRlciJ9LCJwbG90Ijp7ImlkIjoiZjFhMDQxNDMtNTAxOS00NmUzLTk1ZjItZDg0NTY0MWNhMmI2Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6Ijc2YTRiMGJmLTY5MjYtNDA3Yy1iYTQzLTM1NWIyMjFiNjM3MCIsInR5cGUiOiJCYXNpY1RpY2tlciJ9fSwiaWQiOiJmZjNjNDBjYy1hZDg1LTQxOGYtOWMwYi0yMzExN2I3M2JhMDUiLCJ0eXBlIjoiTGluZWFyQXhpcyJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbH0sImlkIjoiMjA5ZDhmYWMtNmU5Zi00NjZhLWEwNjQtMGNiOTA4MDhlNTBjIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0seyJhdHRyaWJ1dGVzIjp7ImNsaWNrX3BvbGljeSI6Im11dGUiLCJpdGVtcyI6W3siaWQiOiJjOGNjYTU0ZC04N2YxLTQwMjgtODI2Zi04MjQyMDQzODNiZWYiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9XSwibG9jYXRpb24iOlswLDYwXSwicGxvdCI6eyJpZCI6ImYxYTA0MTQzLTUwMTktNDZlMy05NWYyLWQ4NDU2NDFjYTJiNiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9fSwiaWQiOiI2NjQwMzQ0MC0wODQ2LTQ0YWMtYWY1Yi0zZjE5ZTA1OTI3MGYiLCJ0eXBlIjoiTGVnZW5kIn0seyJhdHRyaWJ1dGVzIjp7InNvdXJjZSI6eyJpZCI6IjUwZDQyM2I5LWRhNTktNGQ5MS1iMDgyLWMwNTY5YzlmY2VkNCIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn19LCJpZCI6IjkzNDBkODQ3LTRkY2EtNDdmZi05MDk1LWQ0NmIzN2RiNGI1YyIsInR5cGUiOiJDRFNWaWV3In0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiI5NjJjY2ViYy1hOGJlLTQxNTItYTJjYS00NGM2Y2M4YzVmYTkiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrRm9ybWF0dGVyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsfSwiaWQiOiJjYmUyY2U0Yi03Y2MwLTQ5OTYtYjZhZS0xNjk1YjU4MjRiYTIiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCwxLDIsMyw0LDUsNiw3LDgsOSwxMCwxMV19LCJpZCI6ImMwZDBkYzJhLWFmMzAtNGM0OC04NDVmLWU4ZmQ2ZGYzN2IxZiIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGltZW5zaW9uIjoxLCJwbG90Ijp7ImlkIjoiZjFhMDQxNDMtNTAxOS00NmUzLTk1ZjItZDg0NTY0MWNhMmI2Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6Ijc2YTRiMGJmLTY5MjYtNDA3Yy1iYTQzLTM1NWIyMjFiNjM3MCIsInR5cGUiOiJCYXNpY1RpY2tlciJ9fSwiaWQiOiJhODliNTMwMC0zYzM0LTQ5ZWEtYjM0My04MzY1YTMwYjI5MDQiLCJ0eXBlIjoiR3JpZCJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNzNjOWQyMjMtZGQ4Ny00OGE4LThjZmQtZDIxNWFiOTZmNjY3IiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCwyLDQsNiw4LDEwXX0sImlkIjoiNTFkOGQ0OTYtYWQ5NC00YzAzLWJiYmUtZjI3NGZmYzViMjcwIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJkYXlzIjpbMSwyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTMsMTQsMTUsMTYsMTcsMTgsMTksMjAsMjEsMjIsMjMsMjQsMjUsMjYsMjcsMjgsMjksMzAsMzFdfSwiaWQiOiIyMGI0ZjA0MC1jMWIzLTRjYmItOGIzZS0zOTJjOTkzMWFkNDEiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNzZhNGIwYmYtNjkyNi00MDdjLWJhNDMtMzU1YjIyMWI2MzcwIiwidHlwZSI6IkJhc2ljVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiY3JpbXNvbiIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiNWYyNmY4NTEtMTE0Ny00MjBkLTkwNDEtNDcwNjlhNWNkMzgyIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6MjQsIm1hbnRpc3NhcyI6WzEsMiw0LDYsOCwxMl0sIm1heF9pbnRlcnZhbCI6NDMyMDAwMDAuMCwibWluX2ludGVydmFsIjozNjAwMDAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiOTk0OWYxZjktNzYwNS00ZDEwLWE2MjYtZTMxNmQ3ZjVhM2M5IiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOm51bGwsInRleHQiOiI4NDQ3Mzg2In0sImlkIjoiYzNlMzY3NDItMzk1My00MTg0LTllODMtOTE2Yjg5ZTRlZTFmIiwidHlwZSI6IlRpdGxlIn0seyJhdHRyaWJ1dGVzIjp7ImJhc2UiOjYwLCJtYW50aXNzYXMiOlsxLDIsNSwxMCwxNSwyMCwzMF0sIm1heF9pbnRlcnZhbCI6MTgwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjEwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiI4YjVmZjNhYi1iZDNmLTRmYjEtOTdkZS0xMTllZDRiY2NkYzUiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw0LDhdfSwiaWQiOiJkY2FiNmNkOC1lMzJhLTQ4OTQtYjMzNy04NzlmZWZlMjY1YmIiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im92ZXJsYXkiOnsiaWQiOiJiYTMzZTI1ZC00NzY1LTRiMjUtOGM5Mi1mNjgzOGU0ZTM4OGMiLCJ0eXBlIjoiQm94QW5ub3RhdGlvbiJ9fSwiaWQiOiJjMjU1ZWM5OS1lYzIwLTQzNmEtODVmMy04OWFmMTE3YTg1ZGIiLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsImNvbHVtbl9uYW1lcyI6WyJ4IiwieSJdLCJkYXRhIjp7IngiOnsiX19uZGFycmF5X18iOiJBQUNBVnBzZGRrSUFBR2pGbmgxMlFnQUFVRFNpSFhaQ0FBQTRvNlVkZGtJQUFDQVNxUjEyUWdBQUNJR3NIWFpDQUFEdzc2OGRka0lBQU5oZXN4MTJRZ0FBd00yMkhYWkNBQUNvUExvZGRrSUFBSkNydlIxMlFnQUFlQnJCSFhaQ0FBQmdpY1FkZGtJQUFFajR4eDEyUWdBQU1HZkxIWFpDQUFBWTFzNGRka0lBQUFCRjBoMTJRZ0FBNkxQVkhYWkNBQURRSXRrZGRrSUFBTGlSM0IxMlFnQUFvQURnSFhaQ0FBQ0liK01kZGtJQUFIRGU1aDEyUWdBQVdFM3FIWFpDQUFCQXZPMGRka0lBQUNncjhSMTJRZ0FBRUpyMEhYWkNBQUQ0Q1BnZGRrSUFBT0IzK3gxMlFnQUF5T2IrSFhaQ0FBQ3dWUUllZGtJQUFKakVCUjUyUWdBQWdETUpIblpDQUFCb29nd2Vka0lBQUZBUkVCNTJRZ0FBT0lBVEhuWkNBQUFnN3hZZWRrSUFBQWhlR2g1MlFnQUE4TXdkSG5aQ0FBRFlPeUVlZGtJQUFNQ3FKQjUyUWdBQXFCa29IblpDQUFDUWlDc2Vka0lBQUhqM0xoNTJRZ0FBWUdZeUhuWkNBQUJJMVRVZWRrSUFBREJFT1I1MlFnQUFHTE04SG5aQ0FBQUFJa0FlZGtJQUFPaVFReDUyUWdBQTBQOUdIblpDQUFDNGJrb2Vka0lBQUtEZFRSNTJRZ0FBaUV4UkhuWkNBQUJ3dTFRZWRrSUFBRmdxV0I1MlFnQUFRSmxiSG5aQ0FBQW9DRjhlZGtJQUFCQjNZaDUyUWdBQStPVmxIblpDQUFEZ1ZHa2Vka0lBQU1qRGJCNTJRZ0FBc0RKd0huWkNBQUNZb1hNZWRrSUFBSUFRZHg1MlFnQUFhSDk2SG5aQ0FBQlE3bjBlZGtJQUFEaGRnUjUyUWdBQUlNeUVIblpDQUFBSU80Z2Vka0lBQVBDcGl4NTJRZ0FBMkJpUEhuWkNBQURBaDVJZWRrSUFBS2oybFI1MlFnQUFrR1daSG5aQ0FBQjQxSndlZGtJQUFHQkRvQjUyUWdBQVNMS2pIblpDQUFBd0lhY2Vka0lBQUJpUXFoNTJRZ0FBQVArdEhuWkNBQURvYmJFZWRrSUFBTkRjdEI1MlFnQUF1RXU0SG5aQ0FBQ2d1cnNlZGtJQUFJZ3B2eDUyUWdBQWNKakNIblpDQUFCWUI4WWVka0lBQUVCMnlSNTJRZ0FBS09YTUhuWkNBQUFRVk5BZWRrSUFBUGpDMHg1MlFnQUE0REhYSG5aQ0FBRElvTm9lZGtJQUFMQVAzaDUyUWdBQW1IN2hIblpDQUFDQTdlUWVka0lBQUdoYzZCNTJRZ0FBVU12ckhuWkNBQUE0T3U4ZWRrSUFBQ0NwOGg1MlFnQUFDQmoySG5aQ0FBRHdodmtlZGtJQUFOajEvQjUyUWdBQXdHUUFIM1pDQUFDbzB3TWZka0lBQUpCQ0J4OTJRZ0FBZUxFS0gzWkNBQUJnSUE0ZmRrSUFBRWlQRVI5MlFnQUFNUDRVSDNaQ0FBQVliUmdmZGtJQUFBRGNHeDkyUWdBQTZFb2ZIM1pDQUFEUXVTSWZka0lBQUxnb0poOTJRZ0FBb0pjcEgzWkNBQUNJQmkwZmRrSUFBSEIxTUI5MlFnQUFXT1F6SDNaQ0FBQkFVemNmZGtJPSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTIxXX0sInkiOnsiX19uZGFycmF5X18iOiJabVptWm1abTlEL0F5cUZGdHZQdFAvWW9YSS9DOWVBL0NLd2NXbVE3dno5WU9iVElkcjYvditPbG04UWdzTEsvcHB2RUlMQnl5RC80VStPbG04VFlQeHhhWkR2ZlQrVS96L2RUNDZXYjhEL056TXpNek16MlA5ZWpjRDBLMS9rL1RtSVFXRG0wK0Qra2NEMEsxNlAwUDVaRGkyem4rKzAvVXJnZWhldFI0RDhyaHhiWnp2ZkRQMHczaVVGZzVhQy9PclRJZHI2ZmlqK0Y2MUc0SG9YTFB5bGNqOEwxS053L2NUMEsxNk53NlQ5WU9iVElkcjd6UHdSV0RpMnluZmsvTjRsQllPWFErajlrTzk5UGpaZjJQMXBrTzk5UGplOC96Y3pNek16TTREK294a3MzaVVIQVAycThkSk1ZQkxhLy9LbngwazFpa0w4MlhycEpEQUxMUDk5UGpaZHVFdHMvdHZQOTFIanA1ajgvTlY2NlNRenlQM2pwSmpFSXJQZy8rbjVxdkhTVC9EOXBrZTE4UHpYOFB6RUlyQnhhWlBjL3RNaDJ2cDhhN3o4Ykw5MGtCb0hkUHp6ZlQ0MlhickkvV0RtMHlIYStuejhFVmc0dHNwM1BQMVRqcFp2RUlOZy91QjZGNjFHNDNqK2dHaS9kSkFicFAwVzI4LzNVZVBVL2pHem4rNm54L0QrdVIrRjZGSzc5UDBvTUFpdUhGdmsvbk1RZ3NISm84VDlZT2JUSWRyN2pQeEZZT2JUSWRzNC9HeS9kSkFhQmxULzhxZkhTVFdLd1B6RUlyQnhhWk1zL2lVRmc1ZEFpMno5dUVvUEF5cUhwUCtYUUl0djVmdlEvdjU4YUw5MGsvRCtzSEZwa085Ly9QNEdWUTR0czUvMC9RRFZldWtrTStELzRVK09sbThUd1AyOFNnOERLb2VFL3NYSm9rZTE4MXo4WUJGWU9MYkxOUC9oVDQ2V2J4TUEvZU9rbU1RaXN2RC9QOTFQanBadlVQM0U5Q3RlamNPay90TWgydnA4YTlUODJYcnBKREFMN1AxWU9MYktkNy9zLzVkQWkyL2wrK0QrcThkSk5ZaEQwUDBvTUFpdUhGdTAvVk9PbG04UWc1RDhSV0RtMHlIYldQKzU4UHpWZXVzay8wU0xiK1g1cXpEOS9hcngwa3hqZ1A0R1ZRNHRzNStzL0g0WHJVYmdlOXo5bVptWm1abVlBUUIxYVpEdmZUd0pBZzhES29VVzJBRUFJckJ4YVpEdjVQMk1RV0RtMHlQQS9WZzR0c3AzdjR6OWpFRmc1dE1qZVB3aXNIRnBrTzk4L1hJL0M5U2hjNHovYitYNXF2SFRuUDZSd1BRclhvL0EvRGkyeW5lK245ajlNTjRsQllPWCtQK3hSdUI2RjZ3RkE0WG9VcmtmaEFVRHVmRDgxWHJyOVA5UjQ2U1l4Q1BZLzlpaGNqOEwxN0QvdnA4WkxONG5oUHlVR2daVkRpOXcvWkR2ZlQ0MlgzajhBQUFBQUFBRGtQeTJ5bmUrbnh1cy9sa09MYk9mNzh6L0ZJTEJ5YUpIN1AxQ05sMjRTZ3dCQXlYYStueG92QVVCbVptWm1abWIrUDRsQllPWFFJdmMvTGJLZDc2Zkc3ei91ZkQ4MVhycmxQMlptWm1abVp1SS95WGErbnhvdjVUOGxCb0dWUTR2b1A4WkxONGxCWU8wL1VJMlhiaEtEOGo4PSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTIxXX19fSwiaWQiOiI1MGQ0MjNiOS1kYTU5LTRkOTEtYjA4Mi1jMDU2OWM5ZmNlZDQiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LHsiYXR0cmlidXRlcyI6eyJheGlzX2xhYmVsIjoiRGF0ZS90aW1lIiwiZm9ybWF0dGVyIjp7ImlkIjoiOTYyY2NlYmMtYThiZS00MTUyLWEyY2EtNDRjNmNjOGM1ZmE5IiwidHlwZSI6IkRhdGV0aW1lVGlja0Zvcm1hdHRlciJ9LCJwbG90Ijp7ImlkIjoiZjFhMDQxNDMtNTAxOS00NmUzLTk1ZjItZDg0NTY0MWNhMmI2Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6ImZjNTVlZTI4LWM0OGUtNGE3MS1hOGJjLWFlZWQwNDdjNjMyZCIsInR5cGUiOiJEYXRldGltZVRpY2tlciJ9fSwiaWQiOiI5MmU4MjQ4MS1kMGY1LTQ5YTctYmE1OC01MjY5ZWQ3NzIzMzgiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJhdHRyaWJ1dGVzIjp7ImJlbG93IjpbeyJpZCI6IjkyZTgyNDgxLWQwZjUtNDlhNy1iYTU4LTUyNjllZDc3MjMzOCIsInR5cGUiOiJEYXRldGltZUF4aXMifV0sImxlZnQiOlt7ImlkIjoiZmYzYzQwY2MtYWQ4NS00MThmLTljMGItMjMxMTdiNzNiYTA1IiwidHlwZSI6IkxpbmVhckF4aXMifV0sInBsb3RfaGVpZ2h0IjoyNTAsInBsb3Rfd2lkdGgiOjc1MCwicmVuZGVyZXJzIjpbeyJpZCI6IjkyZTgyNDgxLWQwZjUtNDlhNy1iYTU4LTUyNjllZDc3MjMzOCIsInR5cGUiOiJEYXRldGltZUF4aXMifSx7ImlkIjoiMDc4OTZhYzMtMWZiNC00OTcxLWI1MzQtZGNjZTRjZDk4MmQxIiwidHlwZSI6IkdyaWQifSx7ImlkIjoiZmYzYzQwY2MtYWQ4NS00MThmLTljMGItMjMxMTdiNzNiYTA1IiwidHlwZSI6IkxpbmVhckF4aXMifSx7ImlkIjoiYTg5YjUzMDAtM2MzNC00OWVhLWIzNDMtODM2NWEzMGIyOTA0IiwidHlwZSI6IkdyaWQifSx7ImlkIjoiYmEzM2UyNWQtNDc2NS00YjI1LThjOTItZjY4MzhlNGUzODhjIiwidHlwZSI6IkJveEFubm90YXRpb24ifSx7ImlkIjoiNmJjMGZiYmYtZThlYi00OGYwLWEyNDgtOThjYmQzYjQ0M2EyIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImlkIjoiNjY0MDM0NDAtMDg0Ni00NGFjLWFmNWItM2YxOWUwNTkyNzBmIiwidHlwZSI6IkxlZ2VuZCJ9XSwicmlnaHQiOlt7ImlkIjoiNjY0MDM0NDAtMDg0Ni00NGFjLWFmNWItM2YxOWUwNTkyNzBmIiwidHlwZSI6IkxlZ2VuZCJ9XSwidGl0bGUiOnsiaWQiOiJjM2UzNjc0Mi0zOTUzLTQxODQtOWU4My05MTZiODllNGVlMWYiLCJ0eXBlIjoiVGl0bGUifSwidG9vbGJhciI6eyJpZCI6IjQyYzFmYzU0LTg2MWEtNDZhMy04YWU1LTYxNjJhZDM1NTU5MiIsInR5cGUiOiJUb29sYmFyIn0sInRvb2xiYXJfbG9jYXRpb24iOiJhYm92ZSIsInhfcmFuZ2UiOnsiaWQiOiJjYmUyY2U0Yi03Y2MwLTQ5OTYtYjZhZS0xNjk1YjU4MjRiYTIiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSwieF9zY2FsZSI6eyJpZCI6IjU0YmM5YjdjLTJiNTMtNGQ1Ny04M2EzLTAzNDk5NjZhODIxOSIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LCJ5X3JhbmdlIjp7ImlkIjoiMjA5ZDhmYWMtNmU5Zi00NjZhLWEwNjQtMGNiOTA4MDhlNTBjIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInlfc2NhbGUiOnsiaWQiOiIxN2ZlOWRkNC03ZGU3LTRlNTUtODcwOC1hOWZlZTMzZWQzN2EiLCJ0eXBlIjoiTGluZWFyU2NhbGUifX0sImlkIjoiZjFhMDQxNDMtNTAxOS00NmUzLTk1ZjItZDg0NTY0MWNhMmI2Iiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiJhNjY0NDliNi01YWJiLTRjZGQtYTJiZC1kMjUyNmRlZWJiYWYiLCJ0eXBlIjoiUmVzZXRUb29sIn1dLCJyb290X2lkcyI6WyJmMWEwNDE0My01MDE5LTQ2ZTMtOTVmMi1kODQ1NjQxY2EyYjYiXX0sInRpdGxlIjoiQm9rZWggQXBwbGljYXRpb24iLCJ2ZXJzaW9uIjoiMC4xMi4xNCJ9fQogICAgICAgIDwvc2NyaXB0PgogICAgICAgIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgICAgICAgIChmdW5jdGlvbigpIHsKICAgICAgICAgICAgdmFyIGZuID0gZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgQm9rZWguc2FmZWx5KGZ1bmN0aW9uKCkgewogICAgICAgICAgICAgICAgKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgZnVuY3Rpb24gZW1iZWRfZG9jdW1lbnQocm9vdCkgewogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB2YXIgZG9jc19qc29uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2UxNjg4Zjk4LWVhNDYtNDQ3Yi04OTA5LWZhOTk1ZGY4M2VjZCcpLnRleHRDb250ZW50OwogICAgICAgICAgICAgICAgICB2YXIgcmVuZGVyX2l0ZW1zID0gW3siZG9jaWQiOiJmNTAxODBlYy1iYWJjLTQ4NTUtOWU0Yy1jNjY0NzkyZjg0Y2MiLCJlbGVtZW50aWQiOiJlMTlhOGUxOC1mMWU0LTRhODAtOWJjMy00NmVhMzg1Yzc2NjIiLCJtb2RlbGlkIjoiZjFhMDQxNDMtNTAxOS00NmUzLTk1ZjItZDg0NTY0MWNhMmI2In1dOwogICAgICAgICAgICAgICAgICByb290LkJva2VoLmVtYmVkLmVtYmVkX2l0ZW1zKGRvY3NfanNvbiwgcmVuZGVyX2l0ZW1zKTsKICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgICAgICB2YXIgYXR0ZW1wdHMgPSAwOwogICAgICAgICAgICAgICAgICAgIHZhciB0aW1lciA9IHNldEludGVydmFsKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZW1iZWRfZG9jdW1lbnQocm9vdCk7CiAgICAgICAgICAgICAgICAgICAgICAgIGNsZWFySW50ZXJ2YWwodGltZXIpOwogICAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgICAgYXR0ZW1wdHMrKzsKICAgICAgICAgICAgICAgICAgICAgIGlmIChhdHRlbXB0cyA+IDEwMCkgewogICAgICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZygiQm9rZWg6IEVSUk9SOiBVbmFibGUgdG8gcnVuIEJva2VoSlMgY29kZSBiZWNhdXNlIEJva2VoSlMgbGlicmFyeSBpcyBtaXNzaW5nIikKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgfSwgMTAsIHJvb3QpCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0pKHdpbmRvdyk7CiAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgIH07CiAgICAgICAgICAgIGlmIChkb2N1bWVudC5yZWFkeVN0YXRlICE9ICJsb2FkaW5nIikgZm4oKTsKICAgICAgICAgICAgZWxzZSBkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJET01Db250ZW50TG9hZGVkIiwgZm4pOwogICAgICAgICAgfSkoKTsKICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPg==&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_2ca7162a30c04bb3ba7198faf13c6310.setContent(i_frame_8cfc1082e27842f99ecd18c3485f6c4c);
            

            marker_afb918df9f2d4152b6d07c069e1ea90b.bindPopup(popup_2ca7162a30c04bb3ba7198faf13c6310);

            
        
    

            var marker_f7d508705bf5440c92ef0912b2bd6162 = L.marker(
                [41.6885,-69.951],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_d34fef2a41c54a9586e2ce1b59c1e4c2 = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_f7d508705bf5440c92ef0912b2bd6162.setIcon(icon_d34fef2a41c54a9586e2ce1b59c1e4c2);
            
    
            var popup_fc5030ea6f36446e9ec85817b1ba7377 = L.popup({maxWidth: '2650'});

            
                var i_frame_6e4e999a42e64ca29e024c571b5e134a = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQ0NzQzNTwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9IjJkYTBjODdmLWNmMmItNGZlNy05Mjk3LWM3Y2EyM2JlNjcyNiI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iYWU4MWI3ZjktOTkwZS00OTM4LTkzOGEtZmY2OTc5YWI3ZGFmIj4KICAgICAgICAgIHsiYjA0NzdlZmItY2VkYi00MTJlLTg3MWEtOGFkODMxNWQ0Y2M2Ijp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnsiYWN0aXZlX2RyYWciOiJhdXRvIiwiYWN0aXZlX2luc3BlY3QiOiJhdXRvIiwiYWN0aXZlX3Njcm9sbCI6ImF1dG8iLCJhY3RpdmVfdGFwIjoiYXV0byIsInRvb2xzIjpbeyJpZCI6IjY0NDc5ZjQxLTFjM2QtNDA0Yi04ZjE1LTQ1ODc5NWNkY2UzMiIsInR5cGUiOiJQYW5Ub29sIn0seyJpZCI6IjdmNzQ4YWE5LTI1MTYtNDA3Ni1hMGMwLTUzMzhkMjE0OTIxZiIsInR5cGUiOiJCb3hab29tVG9vbCJ9LHsiaWQiOiIyOGVlZDUzNy1iNzNmLTRiZDctYTI3Zi1hMTYwYTA4ZWM3MzAiLCJ0eXBlIjoiUmVzZXRUb29sIn0seyJpZCI6ImU5ZGYwMTYyLWZiZjgtNDlmMC1hOGY2LWQxOTdiM2QxNzk4OSIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImlkIjoiZWEzMWI2NjktZGFlNy00YjUxLWJlOWYtYWU2NGJmYWYwY2I2IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiaWQiOiJhMGRmZjE3Ny1kYjU0LTQzNTUtYWU1OC1mMDE3NzIyNWUwZDkiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJpZCI6IjgxMjQ0YjZkLWIzNTEtNDk1MS04ZWM3LWMyMDlhMGIzNTU2ZSIsInR5cGUiOiJIb3ZlclRvb2wifV19LCJpZCI6Ijk2YjdlNzNjLThjZGQtNGJmYi04ZmUxLTFlOGE1OWJlOTMwMCIsInR5cGUiOiJUb29sYmFyIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiY3JpbXNvbiIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiNjAwNjBiY2EtMzRkYy00OWViLTlhMzktYzFkYTIzZjI1ZTA4IiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiZTYwODljNGQtN2Y3Ny00ZGQyLWEzNGUtY2ZlNzkyMjMxMTkzIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiYjAwZTAzYzAtZmE0YS00YjJjLTk5YjUtYjEyOGRmNGJlYzExIiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjZDYyNzI4IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiI4NDExZDEzMy0wZmRhLTRkMmYtODEzNy05OWQwMGRiZGFhODUiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFCQXZPMGRka0lBQUNncjhSMTJRZ0FBRUpyMEhYWkNBQUFBSWtBZWRrSUFBT2lRUXg1MlFnQUEwUDlHSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFDQTdlUWVka0lBQUdoYzZCNTJRZ0FBVU12ckhuWkMiLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzE1XX0sInkiOnsiX19uZGFycmF5X18iOiJBQUFBQU5ZUDRiOEFBQUNBemk3aHZ3QUFBQURIVGVHL0FBQUFRQ0gzNDc4QUFBRGdwTlBqdndBQUFJQW9zT08vQUFBQUlIaWo0TDhBQUFBZ2thM2Z2d0FBQUNBeUZONi9BQUFBd09kbnREOEFBQUFnT3FtelB3QUFBSUNNNnJJL0FBQUFnQWM5aEQ4QUFBQ0FCejJFUHdBQUFJQUhQWVEvIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxNV19fX0sImlkIjoiZmMzMWZhMmEtMTc4Ny00MzQyLThlNGEtYzFmNjdmYzI3OGUwIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsInJlbmRlcmVycyI6W3siaWQiOiIxNDkzNDAwNi0wZTgwLTRkMDctYWJmMS1iNmMyM2Y1MzM0NWYiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XSwidG9vbHRpcHMiOltbIk5hbWUiLCJPYnNlcnZhdGlvbnMiXSxbIkJpYXMiLCJOQSJdLFsiU2tpbGwiLCJOQSJdXX0sImlkIjoiZTlkZjAxNjItZmJmOC00OWYwLWE4ZjYtZDE5N2IzZDE3OTg5IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDEsMiwzLDQsNSw2LDcsOCw5LDEwLDExXX0sImlkIjoiNGQ2YTgxMTItMGE2Mi00ODllLWI2NDMtMTA2YWMwZjEwMWY2IiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQUQvclI1MlFnQUE2RzJ4SG5aQ0FBRFEzTFFlZGtJQUFMaEx1QjUyUWdBQW9McTdIblpDQUFDSUtiOGVka0lBQUhDWXdoNTJRZ0FBV0FmR0huWkNBQUJBZHNrZWRrSUFBQ2psekI1MlFnQUFFRlRRSG5aQ0FBRElvTm9lZGtJQUFMQVAzaDUyUWdBQW1IN2hIblpDQUFDQTdlUWVka0lBQUdoYzZCNTJRZ0FBVU12ckhuWkNBQUE0T3U4ZWRrSUFBQ0NwOGg1MlFnQUFDQmoySG5aQ0FBRHdodmtlZGtJQUFOajEvQjUyUWdBQXdHUUFIM1pDQUFDbzB3TWZka0lBQUpCQ0J4OTJRZ0FBZUxFS0gzWkNBQUJnSUE0ZmRrSUFBRWlQRVI5MlFnQUFNUDRVSDNaQ0FBQVliUmdmZGtJQUFBRGNHeDkyUWdBQTZFb2ZIM1pDQUFEUXVTSWZka0lBQUxnb0poOTJRZ0FBb0pjcEgzWkNBQUNJQmkwZmRrSUFBSEIxTUI5MlFnQUFXT1F6SDNaQ0FBQkFVemNmZGtJPSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTE4XX0sInkiOnsiX19uZGFycmF5X18iOiJmVDgxWHJwSjZEL3NVYmdlaGV2elA3YnovZFI0NmZnL3dNcWhSYmJ6K1QrRHdNcWhSYmIzUHplSlFXRGwwUEkvYVpIdGZEODE2ajlPWWhCWU9iVGdQNFhyVWJnZWhkTS9LNGNXMmM3M3d6L2pwWnZFSUxDeVA3YnovZFI0NmRZLzBTTGIrWDVxN0QrUzdYdy9OVjcyUDA1aUVGZzV0UHcvU09GNkZLNUgveit4Y21pUjdYejlQMCtObDI0U2cvZy9GdG5POTFQajhUK294a3MzaVVIb1A3Z2VoZXRSdU40L2pHem4rNm54MGovWG8zQTlDdGZEUC9UOTFIanBKckUvWU9YUUl0djUxai9GSUxCeWFKSHRQM2pwSmpFSXJQWS9WT09sbThRZy9EOEsxNk53UFFyOVA1THRmRDgxWHZvL1g3cEpEQUlyOVQrV1E0dHM1L3Z0UDY1SDRYb1VydU0vOWloY2o4TDEyRCs4ZEpNWUJGYk9QMk1RV0RtMHlNWS91a2tNQWl1SDRqOHRzcDN2cDhieFA2RkZ0dlA5MVBvL2JlZjdxZkhTQUVCM3ZwOGFMOTBCUUQ4MVhycEpEQUZBajhMMUtGeVAvRDhLMTZOd1BRcjFQeHN2M1NRR2dlMC9LNGNXMmM3MzR6K0pRV0RsMENMYlAwamhlaFN1UjlFL25lK254a3MzeVQ5eFBRclhvM0RsUDVxWm1abVptZk0vSEZwa085OVArejhUZzhES29VVUFRTHBKREFJcmh3QkFSSXRzNS91cC9ULzkxSGpwSmpINFB5L2RKQWFCbGZFL2ZUODFYcnBKNkQ4aHNISm9rZTNnUDZqR1N6ZUpRZGcvd01xaFJiYnozVDlGdHZQOTFIanRQeS9kSkFhQmxmay9qR3puKzZueEFVQTlDdGVqY0QwRlFETXpNek16TXdWQWFaSHRmRDgxQlVCemFKSHRmRDhGUUZnNXRNaDJ2Z0ZBbGtPTGJPZjcrei9vKzZueDBrMzJQeWxjajhMMUtQUS9TZ3dDSzRjVzh6OE9MYktkNzZmMlA4VWdzSEpva2YwL2c4REtvVVcyQWtBY1dtUTczMDhGUUhOb2tlMThQd1ZBYzJpUjdYdy9CVUFFVmc0dHNwMy9QMUs0SG9YclVmdy81ZEFpMi9sKzlqOXhQUXJYbzNEeFA1WkRpMnpuKyswL3ZIU1RHQVJXOGo4aHNISm9rZTM0UHd3Q0s0Y1cyUUJBQ3RlamNEMEtCVUJ6YUpIdGZEOEZRUDNVZU9rbU1RVkFYSS9DOVNoYytUOElyQnhhWkR2M1AycThkSk1ZQlBJL0JvR1ZRNHRzNnorWGJoS0R3TXJwUCsrbnhrczNpZkUvWU9YUUl0djUrRDlPWWhCWU9iUUFRRE16TXpNek13UkFzcDN2cDhaTEJVQWNXbVE3MzA4RlFNUDFLRnlQd2dOQTMwK05sMjRTQUVCa085OVBqWmY0UDgzTXpNek16UEkvZDc2ZkdpL2Q3RDlPWWhCWU9iVG9QenEweUhhK24rNC9VcmdlaGV0UjlEK3NIRnBrTzkvOVB6emZUNDJYYmdKQWVPa21NUWlzQkVCTU40bEJZT1VFUUx4MGt4Z0VWZ05BQ0t3Y1dtUTdBRUFoc0hKb2tlMzRQN3gwa3hnRVZ2SS9BeXVIRnRuTzZ6OD0iLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzExOF19fX0sImlkIjoiMDhiYTM5MTgtYWQxZi00MTdhLWJhNTMtZTU4ZmQxYTdjYzFmIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnsib3ZlcmxheSI6eyJpZCI6ImIyNmZiOTNhLTY0YmYtNGE4MC04MTI5LTUzODcwZWNjZDFlMyIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn19LCJpZCI6IjdmNzQ4YWE5LTI1MTYtNDA3Ni1hMGMwLTUzMzhkMjE0OTIxZiIsInR5cGUiOiJCb3hab29tVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjY1LCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiNmZjk4OTYiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjgwNDJlNzdjLTBkNjMtNDZiOS04YzBjLTJkNjJkMjE5NTVlNyIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiZ2xvYmFsIn0sInJlbmRlcmVycyI6W3siaWQiOiI0ZmViNjRhYS00ODc2LTRkZjAtYmVjNi1iMTA0NWI5NDY5NTEiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiZjc4ODcwNTQtYTFjMC00ZTYwLWI4YTktZmZmNzU5OWZkYjUzIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJUaW1lX3YyX0hpc3RvcnlfQmVzdCJ9LCJyZW5kZXJlcnMiOlt7ImlkIjoiOWNmNWY1NzktNmFmNC00MTViLThmZTktYjI5NmZkNTBkMDViIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV19LCJpZCI6IjQyZWI2OTJhLWI1YTctNDVmYS05ZDI1LWUxMjA1MjQ1ZTBkMSIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsfSwiaWQiOiI3OTRmMmI4Yi01OGZkLTQ0NzQtOGI1ZS1lNTg4YWUzMmM5ZTEiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImMxYjc0MzdlLTdjNzEtNGMwZC1hNjJiLTNhOWVkYzEwMWQyZSIsInR5cGUiOiJMaW5lYXJTY2FsZSJ9LHsiYXR0cmlidXRlcyI6eyJsYWJlbCI6eyJ2YWx1ZSI6IlRpbWVfdjJfQXZlcmFnZXNfQmVzdCJ9LCJyZW5kZXJlcnMiOlt7ImlkIjoiODBjMWJhZDEtYTFjOS00NjliLWI2NzEtNTJmZjYxOTAyMjNkIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV19LCJpZCI6IjI4NmUyZmZjLTYwNzMtNDk0OC1iOWM4LTYwNjliYWFhODQzYiIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDgsMTUsMjJdfSwiaWQiOiJjZmY3NTEzYS1jYWUyLTQxNWEtYjVlNC1lZmE3MmQ0MDcyMGMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiN2Y3NWFiYTItOTliNC00Y2E1LTg1NGUtYWQwODAwNWMwYzQyIiwidHlwZSI6IkJhc2ljVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOm51bGwsInRleHQiOiI4NDQ3NDM1In0sImlkIjoiNjNjYTg5MzktMmIyMi00NWY0LTkwY2EtMmE1NWMyOTdlNTIxIiwidHlwZSI6IlRpdGxlIn0seyJhdHRyaWJ1dGVzIjp7ImRpbWVuc2lvbiI6MSwicGxvdCI6eyJpZCI6ImEwNzU4YjJhLTc3ZjMtNGQzNy04MmE4LTQ2ZDE5OTljZjA5NiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI3Zjc1YWJhMi05OWI0LTRjYTUtODU0ZS1hZDA4MDA1YzBjNDIiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifX0sImlkIjoiODMzZGZkMTctYjg0NC00MjljLTg3MmEtZTVlY2Q1NmIxN2YxIiwidHlwZSI6IkdyaWQifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6MjQsIm1hbnRpc3NhcyI6WzEsMiw0LDYsOCwxMl0sIm1heF9pbnRlcnZhbCI6NDMyMDAwMDAuMCwibWluX2ludGVydmFsIjozNjAwMDAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiZTMyZDU3ODAtNmQ3My00NmIzLWEzZTMtMmFhZDY0NjlkMjM1IiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsfSwiaWQiOiJjOThlZDg5YS00MjIxLTRmM2QtYTdiNi1mNDkxYThhZjM4NjMiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSx7ImF0dHJpYnV0ZXMiOnsiZGF0YV9zb3VyY2UiOnsiaWQiOiJlNjA4OWM0ZC03Zjc3LTRkZDItYTM0ZS1jZmU3OTIyMzExOTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LCJnbHlwaCI6eyJpZCI6Ijg0MTFkMTMzLTBmZGEtNGQyZi04MTM3LTk5ZDAwZGJkYWE4NSIsInR5cGUiOiJMaW5lIn0sImhvdmVyX2dseXBoIjpudWxsLCJtdXRlZF9nbHlwaCI6bnVsbCwibm9uc2VsZWN0aW9uX2dseXBoIjp7ImlkIjoiOTVmNjQ1NmEtZGEwZi00N2NlLTg1YTEtZmQzY2MxYTlkYzAzIiwidHlwZSI6IkxpbmUifSwic2VsZWN0aW9uX2dseXBoIjpudWxsLCJ2aWV3Ijp7ImlkIjoiYjAwZTAzYzAtZmE0YS00YjJjLTk5YjUtYjEyOGRmNGJlYzExIiwidHlwZSI6IkNEU1ZpZXcifX0sImlkIjoiOWNmNWY1NzktNmFmNC00MTViLThmZTktYjI5NmZkNTBkMDViIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJPYnNlcnZhdGlvbnMifSwicmVuZGVyZXJzIjpbeyJpZCI6IjE0OTM0MDA2LTBlODAtNGQwNy1hYmYxLWI2YzIzZjUzMzQ1ZiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dfSwiaWQiOiI5NDdhMDcxNy1mOTcwLTRkNDMtYmEwZC03Mzg1MWIxNmJlMmIiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiYXR0cmlidXRlcyI6eyJtYW50aXNzYXMiOlsxLDIsNV0sIm1heF9pbnRlcnZhbCI6NTAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiNjhhNzI0MzUtMzQ4My00MmZkLWJlZDUtOTQ3ZDA2OTdmMDJhIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsNCw4XX0sImlkIjoiOWQ2ZDJjNWMtMzNiZS00MGVmLTkyNGQtNGFlZjNjYTA3YzRjIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJiZWxvdyI6W3siaWQiOiIxM2U1OTY5ZC0yZjE5LTQyNzAtYmJhMi05OGZiOTc4N2RmNGIiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn1dLCJsZWZ0IjpbeyJpZCI6IjNhNzk2OWU4LWFkNDctNGZlOC04MjA3LWRlODA0M2YxYzMxNSIsInR5cGUiOiJMaW5lYXJBeGlzIn1dLCJwbG90X2hlaWdodCI6MjUwLCJwbG90X3dpZHRoIjo3NTAsInJlbmRlcmVycyI6W3siaWQiOiIxM2U1OTY5ZC0yZjE5LTQyNzAtYmJhMi05OGZiOTc4N2RmNGIiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJpZCI6IjQ3MjgxNjk2LWM2NGYtNDIxZC1hNzczLTYyMzFkZDA5OGM5OCIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjNhNzk2OWU4LWFkNDctNGZlOC04MjA3LWRlODA0M2YxYzMxNSIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJpZCI6IjgzM2RmZDE3LWI4NDQtNDI5Yy04NzJhLWU1ZWNkNTZiMTdmMSIsInR5cGUiOiJHcmlkIn0seyJpZCI6ImIyNmZiOTNhLTY0YmYtNGE4MC04MTI5LTUzODcwZWNjZDFlMyIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJpZCI6IjE0OTM0MDA2LTBlODAtNGQwNy1hYmYxLWI2YzIzZjUzMzQ1ZiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjgwYzFiYWQxLWExYzktNDY5Yi1iNjcxLTUyZmY2MTkwMjIzZCIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjljZjVmNTc5LTZhZjQtNDE1Yi04ZmU5LWIyOTZmZDUwZDA1YiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjRmZWI2NGFhLTQ4NzYtNGRmMC1iZWM2LWIxMDQ1Yjk0Njk1MSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6ImZlYjBhOTFiLWNmNDAtNGI4NS1hOTdlLWQzMTRkMDJjNGMxOCIsInR5cGUiOiJMZWdlbmQifV0sInJpZ2h0IjpbeyJpZCI6ImZlYjBhOTFiLWNmNDAtNGI4NS1hOTdlLWQzMTRkMDJjNGMxOCIsInR5cGUiOiJMZWdlbmQifV0sInRpdGxlIjp7ImlkIjoiNjNjYTg5MzktMmIyMi00NWY0LTkwY2EtMmE1NWMyOTdlNTIxIiwidHlwZSI6IlRpdGxlIn0sInRvb2xiYXIiOnsiaWQiOiI5NmI3ZTczYy04Y2RkLTRiZmItOGZlMS0xZThhNTliZTkzMDAiLCJ0eXBlIjoiVG9vbGJhciJ9LCJ0b29sYmFyX2xvY2F0aW9uIjoiYWJvdmUiLCJ4X3JhbmdlIjp7ImlkIjoiNzk0ZjJiOGItNThmZC00NDc0LThiNWUtZTU4OGFlMzJjOWUxIiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInhfc2NhbGUiOnsiaWQiOiIzYjBkOTRlZC04OWUxLTQyNmYtOTljOC1mNmI2NzUxYzc5YjMiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSwieV9yYW5nZSI6eyJpZCI6ImM5OGVkODlhLTQyMjEtNGYzZC1hN2I2LWY0OTFhOGFmMzg2MyIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LCJ5X3NjYWxlIjp7ImlkIjoiYzFiNzQzN2UtN2M3MS00YzBkLWE2MmItM2E5ZWRjMTAxZDJlIiwidHlwZSI6IkxpbmVhclNjYWxlIn19LCJpZCI6ImEwNzU4YjJhLTc3ZjMtNGQzNy04MmE4LTQ2ZDE5OTljZjA5NiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LHsiYXR0cmlidXRlcyI6eyJheGlzX2xhYmVsIjoiV2F0ZXIgSGVpZ2h0IChtKSIsImZvcm1hdHRlciI6eyJpZCI6ImU2ODhmYzEyLWNjYTctNDBlMC1iZjU1LThkZTk3OWQ2YTQ3ZiIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6ImEwNzU4YjJhLTc3ZjMtNGQzNy04MmE4LTQ2ZDE5OTljZjA5NiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI3Zjc1YWJhMi05OWI0LTRjYTUtODU0ZS1hZDA4MDA1YzBjNDIiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifX0sImlkIjoiM2E3OTY5ZTgtYWQ0Ny00ZmU4LTgyMDctZGU4MDQzZjFjMzE1IiwidHlwZSI6IkxpbmVhckF4aXMifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImU2ODhmYzEyLWNjYTctNDBlMC1iZjU1LThkZTk3OWQ2YTQ3ZiIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsMTVdfSwiaWQiOiJlNzc4MjE4My0wOTI0LTQ3MzYtOWRkMi1iY2ZmMWI0ODJjNGMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiYWUzYjQ4MGItYjJkZi00MzJkLTkwZjQtYmY4M2JmMWI3ZmMxIiwidHlwZSI6IlllYXJzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7InNvdXJjZSI6eyJpZCI6IjA4YmEzOTE4LWFkMWYtNDE3YS1iYTUzLWU1OGZkMWE3Y2MxZiIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn19LCJpZCI6IjZkZmI4MjIxLTc2MTUtNGFmZS04ZTE2LWU4NmI0OTEwZjZhOSIsInR5cGUiOiJDRFNWaWV3In0seyJhdHRyaWJ1dGVzIjp7ImNsaWNrX3BvbGljeSI6Im11dGUiLCJpdGVtcyI6W3siaWQiOiI5NDdhMDcxNy1mOTcwLTRkNDMtYmEwZC03Mzg1MWIxNmJlMmIiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiaWQiOiIyODZlMmZmYy02MDczLTQ5NDgtYjljOC02MDY5YmFhYTg0M2IiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiaWQiOiI0MmViNjkyYS1iNWE3LTQ1ZmEtOWQyNS1lMTIwNTI0NWUwZDEiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9LHsiaWQiOiJmNzg4NzA1NC1hMWMwLTRlNjAtYjhhOS1mZmY3NTk5ZmRiNTMiLCJ0eXBlIjoiTGVnZW5kSXRlbSJ9XSwibG9jYXRpb24iOlswLDYwXSwicGxvdCI6eyJpZCI6ImEwNzU4YjJhLTc3ZjMtNGQzNy04MmE4LTQ2ZDE5OTljZjA5NiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9fSwiaWQiOiJmZWIwYTkxYi1jZjQwLTRiODUtYTk3ZS1kMzE0ZDAyYzRjMTgiLCJ0eXBlIjoiTGVnZW5kIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuNjUsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzk4ZGY4YSIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiYThhNjQ2YTktYzdlZC00Y2ZiLWE3OGQtMzFmYjI1YTk5NTVhIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImU1OTI0MTU2LTRhOTEtNDA5Yi05MmU2LTdlMmE3MjFmYjEzYyIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDIsMyw0LDUsNiw3LDgsOSwxMCwxMSwxMiwxMywxNCwxNSwxNiwxNywxOCwxOSwyMCwyMSwyMiwyMywyNCwyNSwyNiwyNywyOCwyOSwzMCwzMV19LCJpZCI6ImE4OWE1NmIyLTNhZWItNDRmNC04ZTdmLTUzZWMyYzRlZGRkMyIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7InBsb3QiOnsiaWQiOiJhMDc1OGIyYS03N2YzLTRkMzctODJhOC00NmQxOTk5Y2YwOTYiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifSwidGlja2VyIjp7ImlkIjoiODBjMTM0MzctMGQ0OS00MDQxLTgzM2ItZjJmNmRlZjlmMzczIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn19LCJpZCI6IjQ3MjgxNjk2LWM2NGYtNDIxZC1hNzczLTYyMzFkZDA5OGM5OCIsInR5cGUiOiJHcmlkIn0seyJhdHRyaWJ1dGVzIjp7ImRhdGFfc291cmNlIjp7ImlkIjoiZmMzMWZhMmEtMTc4Ny00MzQyLThlNGEtYzFmNjdmYzI3OGUwIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSwiZ2x5cGgiOnsiaWQiOiI4MDQyZTc3Yy0wZDYzLTQ2YjktOGMwYy0yZDYyZDIxOTU1ZTciLCJ0eXBlIjoiTGluZSJ9LCJob3Zlcl9nbHlwaCI6bnVsbCwibXV0ZWRfZ2x5cGgiOm51bGwsIm5vbnNlbGVjdGlvbl9nbHlwaCI6eyJpZCI6ImU1OTI0MTU2LTRhOTEtNDA5Yi05MmU2LTdlMmE3MjFmYjEzYyIsInR5cGUiOiJMaW5lIn0sInNlbGVjdGlvbl9nbHlwaCI6bnVsbCwidmlldyI6eyJpZCI6ImMyYjZjNTU3LTE1ZDAtNDBlMS05ZTBkLTIyZjdjNDNjZGNmOSIsInR5cGUiOiJDRFNWaWV3In19LCJpZCI6IjRmZWI2NGFhLTQ4NzYtNGRmMC1iZWM2LWIxMDQ1Yjk0Njk1MSIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsLCJyZW5kZXJlcnMiOlt7ImlkIjoiNGZlYjY0YWEtNDg3Ni00ZGYwLWJlYzYtYjEwNDViOTQ2OTUxIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInRvb2x0aXBzIjpbWyJOYW1lIiwiZ2xvYmFsIl0sWyJCaWFzIiwiLTEuMzUiXSxbIlNraWxsIiwiMC40MyJdXX0sImlkIjoiODEyNDRiNmQtYjM1MS00OTUxLThlYzctYzIwOWEwYjM1NTZlIiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJib3R0b21fdW5pdHMiOiJzY3JlZW4iLCJmaWxsX2FscGhhIjp7InZhbHVlIjowLjV9LCJmaWxsX2NvbG9yIjp7InZhbHVlIjoibGlnaHRncmV5In0sImxlZnRfdW5pdHMiOiJzY3JlZW4iLCJsZXZlbCI6Im92ZXJsYXkiLCJsaW5lX2FscGhhIjp7InZhbHVlIjoxLjB9LCJsaW5lX2NvbG9yIjp7InZhbHVlIjoiYmxhY2sifSwibGluZV9kYXNoIjpbNCw0XSwibGluZV93aWR0aCI6eyJ2YWx1ZSI6Mn0sInBsb3QiOm51bGwsInJlbmRlcl9tb2RlIjoiY3NzIiwicmlnaHRfdW5pdHMiOiJzY3JlZW4iLCJ0b3BfdW5pdHMiOiJzY3JlZW4ifSwiaWQiOiJiMjZmYjkzYS02NGJmLTRhODAtODEyOS01Mzg3MGVjY2QxZTMiLCJ0eXBlIjoiQm94QW5ub3RhdGlvbiJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiMjhlZWQ1MzctYjczZi00YmQ3LWEyN2YtYTE2MGEwOGVjNzMwIiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6IjljZjVmNTc5LTZhZjQtNDE1Yi04ZmU5LWIyOTZmZDUwZDA1YiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIlRpbWVfdjJfSGlzdG9yeV9CZXN0Il0sWyJCaWFzIiwiLTEuMzgiXSxbIlNraWxsIiwiMC40MyJdXX0sImlkIjoiYTBkZmYxNzctZGI1NC00MzU1LWFlNTgtZjAxNzcyMjVlMGQ5IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiJkNjBkYmZhYy1hOThmLTQ5NGEtOThlNi1hODg5MjZhMjRiMTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiI1YWVjYTJlYy01N2NiLTQ4NWQtOGY0NS0wZGUyN2NmYjM0ZmQiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiOWY1MjhhZGQtNWE3NS00M2I2LWIzNjItZjA0Zjg5Yjc0NGQ5IiwidHlwZSI6IkRhdGV0aW1lVGlja0Zvcm1hdHRlciJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjEsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzFmNzdiNCIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiMmM1YjdhODUtNTYwMC00MDdlLThkMjgtNjM3NzlkZWM0YWU0IiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiZmMzMWZhMmEtMTc4Ny00MzQyLThlNGEtYzFmNjdmYzI3OGUwIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiYzJiNmM1NTctMTVkMC00MGUxLTllMGQtMjJmN2M0M2NkY2Y5IiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCwyLDQsNiw4LDEwXX0sImlkIjoiMjU5NTlkMWEtYWY4Ny00NWY0LWJhMTEtZGU2YWFkMTJmMTA1IiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQmdpY1FkZGtJQUFFajR4eDEyUWdBQU1HZkxIWFpDQUFBZzd4WWVka0lBQUFoZUdoNTJRZ0FBOE13ZEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ2d1cnNlZGtJQUFJZ3B2eDUyUWdBQWNKakNIblpDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMl19LCJ5Ijp7Il9fbmRhcnJheV9fIjoiQUFBQVFNcnAxYjhBQUFCQWgrRFZ2d0FBQUVCRTE5Vy9BQUFBNElFTDFiOEFBQUNBVElyVHZ3QUFBQ0FYQ2RLL0FBQUFZUDBpemo4QUFBQkFMMERQUHdBQUFLQ3dMdEEvQUFBQW9OVnYzRDhBQUFDZzFXL2NQd0FBQUtEVmI5dy8iLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzEyXX19fSwiaWQiOiJkNjBkYmZhYy1hOThmLTQ5NGEtOThlNi1hODg5MjZhMjRiMTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiNjQ0NzlmNDEtMWMzZC00MDRiLThmMTUtNDU4Nzk1Y2RjZTMyIiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsImNvbHVtbl9uYW1lcyI6WyJ4IiwieSJdLCJkYXRhIjp7IngiOnsiX19uZGFycmF5X18iOiJBQUNBVnBzZGRrSUFBR2pGbmgxMlFnQUFVRFNpSFhaQ0FBQTRvNlVkZGtJQUFDQVNxUjEyUWdBQUNJR3NIWFpDQUFEdzc2OGRka0lBQU5oZXN4MTJRZ0FBd00yMkhYWkNBQUNvUExvZGRrSUFBSkNydlIxMlFnQUFlQnJCSFhaQ0FBQmdpY1FkZGtJQUFFajR4eDEyUWdBQU1HZkxIWFpDQUFBWTFzNGRka0lBQUFCRjBoMTJRZ0FBNkxQVkhYWkNBQURRSXRrZGRrSUFBTGlSM0IxMlFnQUFvQURnSFhaQ0FBQ0liK01kZGtJQUFIRGU1aDEyUWdBQVdFM3FIWFpDQUFCQXZPMGRka0lBQUNncjhSMTJRZ0FBRUpyMEhYWkNBQUQ0Q1BnZGRrSUFBT0IzK3gxMlFnQUF5T2IrSFhaQ0FBQ3dWUUllZGtJQUFKakVCUjUyUWdBQWdETUpIblpDQUFCb29nd2Vka0lBQUZBUkVCNTJRZ0FBT0lBVEhuWkNBQUFnN3hZZWRrSUFBQWhlR2g1MlFnQUE4TXdkSG5aQ0FBRFlPeUVlZGtJQUFNQ3FKQjUyUWdBQXFCa29IblpDQUFDUWlDc2Vka0lBQUhqM0xoNTJRZ0FBWUdZeUhuWkNBQUJJMVRVZWRrSUFBREJFT1I1MlFnQUFHTE04SG5aQ0FBQUFJa0FlZGtJQUFPaVFReDUyUWdBQTBQOUdIblpDQUFDNGJrb2Vka0lBQUtEZFRSNTJRZ0FBaUV4UkhuWkNBQUJ3dTFRZWRrSUFBRmdxV0I1MlFnQUFRSmxiSG5aQ0FBQW9DRjhlZGtJQUFCQjNZaDUyUWdBQStPVmxIblpDQUFEZ1ZHa2Vka0lBQU1qRGJCNTJRZ0FBc0RKd0huWkNBQUNZb1hNZWRrSUFBSUFRZHg1MlFnQUFhSDk2SG5aQ0FBQlE3bjBlZGtJQUFEaGRnUjUyUWdBQUlNeUVIblpDQUFBSU80Z2Vka0lBQVBDcGl4NTJRZ0FBMkJpUEhuWkNBQURBaDVJZWRrSUFBS2oybFI1MlFnQUFrR1daSG5aQ0FBQjQxSndlZGtJQUFHQkRvQjUyUWdBQVNMS2pIblpDQUFBd0lhY2Vka0lBQUJpUXFoNTJRZ0FBQVArdEhuWkNBQURvYmJFZWRrSUFBTkRjdEI1MlFnQUF1RXU0SG5aQ0FBQ2d1cnNlZGtJQUFJZ3B2eDUyUWdBQWNKakNIblpDQUFCWUI4WWVka0lBQUVCMnlSNTJRZ0FBS09YTUhuWkNBQUFRVk5BZWRrSUFBUGpDMHg1MlFnQUE0REhYSG5aQ0FBRElvTm9lZGtJQUFMQVAzaDUyUWdBQW1IN2hIblpDQUFDQTdlUWVka0lBQUdoYzZCNTJRZ0FBVU12ckhuWkNBQUE0T3U4ZWRrSUFBQ0NwOGg1MlFnQUFDQmoySG5aQ0FBRHdodmtlZGtJQUFOajEvQjUyUWdBQXdHUUFIM1pDQUFDbzB3TWZka0lBQUpCQ0J4OTJRZ0FBZUxFS0gzWkNBQUJnSUE0ZmRrSUFBRWlQRVI5MlFnQUFNUDRVSDNaQ0FBQVliUmdmZGtJQUFBRGNHeDkyUWdBQTZFb2ZIM1pDQUFEUXVTSWZka0lBQUxnb0poOTJRZ0FBb0pjcEgzWkNBQUNJQmkwZmRrSUFBSEIxTUI5MlFnQUFXT1F6SDNaQ0FBQkFVemNmZGtJPSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTIxXX0sInkiOnsiX19uZGFycmF5X18iOiJBQUFBUUlQVTA3OEFBQUFnaVV6U1B3QUFBS0FaMWVVL0FBQUFZRTA4NlQ4QUFBQWdSQ3pqUHdBQUFDQ0NpOEkvQUFBQWdKR04zYjhBQUFBZ3BzM3d2d0FBQU1EdlZ2ZS9BQUFBb0JwdCtiOEFBQURBZnpiMnZ3QUFBQ0JCWCt5L0FBQUFJT0h5eWI4QUFBQWdpaGJlUHdBQUFBQVRydTQvQUFBQVFEU284ajhBQUFCQUh1WHdQd0FBQUtDdkxPUS9BQUFBQUdBNm9MOEFBQUFBb0hIb3Z3QUFBR0Q0WGZhL0FBQUFJRk9jL0w4QUFBRGdWRTc5dndBQUFHQUdLdmkvQUFBQVFBdXM3TDhBQUFCZy9nZlF2d0FBQUFCa3F0Zy9BQUFBb09lNTZEOEFBQUNBaGxUclB3QUFBR0NPcitNL0FBQUFnQld4dVQ4QUFBREFTaFRpdndBQUFJQ1dOZk8vQUFBQUFDWWIrcjhBQUFBZ0lQLzd2d0FBQU1EeisvZS9BQUFBUUdLZjdiOEFBQUFBS3pMR3Z3QUFBS0FOVCtFL0FBQUFZQUNZOEQ4QUFBRGdwY2p6UHdBQUFFRExlZkUvQUFBQUlLYkw0ejhBQUFDZ1Z4TzJ2d0FBQUtBdzErcS9BQUFBSU5sWjk3OEFBQUFBbGQ3OHZ3QUFBTUMyYXZ5L0FBQUF3Tno3OWI4QUFBQUFSNnZsdndBQUFHQThXcjQvQUFBQUlCNEo2VDhBQUFDQXMrVHlQd0FBQUtDbUEvUS9BQUFBQUx4UDd6OEFBQURna1lQYVB3QUFBSUNHK2RHL0FBQUFJTEJCN2I4QUFBQkEwTlAwdndBQUFNQUwrdlMvQUFBQTRCRUE3YjhBQUFCQTFMZkt2d0FBQUlBNnR1SS9BQUFBWVA1djlEOEFBQUJBT2pYOFB3QUFBSUQ1ZWY4L0FBQUFnSmdkL1Q4QUFBRGdra2YxUHdBQUFDQUFMdVEvQUFBQUlMUGZ1cjhBQUFBZ1RXam12d0FBQUVCQldlKy9BQUFBb0lPMTZyOEFBQUNBQ0RuYXZ3QUFBS0JoSnRNL0FBQUFnTWVMN3o4QUFBQmdDSXI0UHdBQUFDQXZ0ZjAvQUFBQW9OMWovVDhBQUFDQVF5cjNQd0FBQUtBR1orZy9BQUFBUUNxMXA3OEFBQUNBeHREb3Z3QUFBRUFnYXZPL0FBQUFBQktNODc4QUFBQ0E0RGpwdndBQUFDQ2tCcmkvQUFBQVlBUXA1VDhBQUFEZzMwbjFQd0FBQU1DWXJ2dy9BQUFBWUdQLy9qOEFBQUFBWGgvN1B3QUFBR0F6d3ZFL0FBQUFJRUhzMVQ4QUFBQmczMTNhdndBQUFPREhwTzYvQUFBQXdBRUE4cjhBQUFBZzB0SHR2d0FBQUlDUmR0Vy9BQUFBSU8rSjJEOEFBQUNnUlR2eFB3QUFBR0FVU3ZrL0FBQUFRT1RkL0Q4QUFBQmdHTzc2UHdBQUFNQWpSL00vQUFBQWdLRSszejhBQUFCQVo3elJ2d0FBQUNCU0dPMi9BQUFBWUN5dTg3OEFBQUNBeEVIeXZ3QUFBSUN3aHVXL0FBQUFJQ2RoaUQ4QUFBQUF1enJuUHdBQUFHQk82dlEvQUFBQUlJSmorajhBQUFCQXd1YjZQd0FBQUtCNndQVS9BQUFBb0YzWTV6OEFBQURBOTA2SVB3QUFBQUR5K09TL0FBQUFBUEw0NUw4PSIsImR0eXBlIjoiZmxvYXQ2NCIsInNoYXBlIjpbMTIxXX19fSwiaWQiOiJlNjA4OWM0ZC03Zjc3LTRkZDItYTM0ZS1jZmU3OTIyMzExOTMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6ImQ2MGRiZmFjLWE5OGYtNDk0YS05OGU2LWE4ODkyNmEyNGIxMyIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiYThhNjQ2YTktYzdlZC00Y2ZiLWE3OGQtMzFmYjI1YTk5NTVhIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiIyYzViN2E4NS01NjAwLTQwN2UtOGQyOC02Mzc3OWRlYzRhZTQiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiI1YWVjYTJlYy01N2NiLTQ4NWQtOGY0NS0wZGUyN2NmYjM0ZmQiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiI4MGMxYmFkMS1hMWM5LTQ2OWItYjY3MS01MmZmNjE5MDIyM2QiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2FscGhhIjowLjEsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzFmNzdiNCIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiOTVmNjQ1NmEtZGEwZi00N2NlLTg1YTEtZmQzY2MxYTlkYzAzIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IkRhdGUvdGltZSIsImZvcm1hdHRlciI6eyJpZCI6IjlmNTI4YWRkLTVhNzUtNDNiNi1iMzYyLWYwNGY4OWI3NDRkOSIsInR5cGUiOiJEYXRldGltZVRpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6ImEwNzU4YjJhLTc3ZjMtNGQzNy04MmE4LTQ2ZDE5OTljZjA5NiIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiI4MGMxMzQzNy0wZDQ5LTQwNDEtODMzYi1mMmY2ZGVmOWYzNzMiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiMTNlNTk2OWQtMmYxOS00MjcwLWJiYTItOThmYjk3ODdkZjRiIiwidHlwZSI6IkRhdGV0aW1lQXhpcyJ9LHsiYXR0cmlidXRlcyI6eyJiYXNlIjo2MCwibWFudGlzc2FzIjpbMSwyLDUsMTAsMTUsMjAsMzBdLCJtYXhfaW50ZXJ2YWwiOjE4MDAwMDAuMCwibWluX2ludGVydmFsIjoxMDAwLjAsIm51bV9taW5vcl90aWNrcyI6MH0sImlkIjoiMjg2YzVkNWMtNWMxZi00OTU2LWE2MTItOTVkMDA3YmQ2MDUyIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiIzYjBkOTRlZC04OWUxLTQyNmYtOTljOC1mNmI2NzUxYzc5YjMiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw2XX0sImlkIjoiNmNlNDUzMzItMjIzZC00MGJkLTlhYzgtMTBjYWE2MjYxN2FlIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6IjgwYzFiYWQxLWExYzktNDY5Yi1iNjcxLTUyZmY2MTkwMjIzZCIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIlRpbWVfdjJfQXZlcmFnZXNfQmVzdCJdLFsiQmlhcyIsIi0xLjE2Il0sWyJTa2lsbCIsIjAuNTciXV19LCJpZCI6ImVhMzFiNjY5LWRhZTctNGI1MS1iZTlmLWFlNjRiZmFmMGNiNiIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImNlYjJjOGJiLTA2YWItNDMwNS1iYzBiLTc3M2VkZDBmZmM1ZiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDQsNywxMCwxMywxNiwxOSwyMiwyNSwyOF19LCJpZCI6IjUzNzkxODM2LWE2ZDUtNDNlNS04MmUyLTcxYjYwOGRjM2IwYiIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7Im51bV9taW5vcl90aWNrcyI6NSwidGlja2VycyI6W3siaWQiOiI2OGE3MjQzNS0zNDgzLTQyZmQtYmVkNS05NDdkMDY5N2YwMmEiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiMjg2YzVkNWMtNWMxZi00OTU2LWE2MTItOTVkMDA3YmQ2MDUyIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6ImUzMmQ1NzgwLTZkNzMtNDZiMy1hM2UzLTJhYWQ2NDY5ZDIzNSIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiJhODlhNTZiMi0zYWViLTQ0ZjQtOGU3Zi01M2VjMmM0ZWRkZDMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiI1Mzc5MTgzNi1hNmQ1LTQzZTUtODJlMi03MWI2MDhkYzNiMGIiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJjZmY3NTEzYS1jYWUyLTQxNWEtYjVlNC1lZmE3MmQ0MDcyMGMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiJlNzc4MjE4My0wOTI0LTQ3MzYtOWRkMi1iY2ZmMWI0ODJjNGMiLCJ0eXBlIjoiRGF5c1RpY2tlciJ9LHsiaWQiOiI0ZDZhODExMi0wYTYyLTQ4OWUtYjY0My0xMDZhYzBmMTAxZjYiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjI1OTU5ZDFhLWFmODctNDVmNC1iYTExLWRlNmFhZDEyZjEwNSIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiOWQ2ZDJjNWMtMzNiZS00MGVmLTkyNGQtNGFlZjNjYTA3YzRjIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiI2Y2U0NTMzMi0yMjNkLTQwYmQtOWFjOC0xMGNhYTYyNjE3YWUiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6ImFlM2I0ODBiLWIyZGYtNDMyZC05MGY0LWJmODNiZjFiN2ZjMSIsInR5cGUiOiJZZWFyc1RpY2tlciJ9XX0sImlkIjoiODBjMTM0MzctMGQ0OS00MDQxLTgzM2ItZjJmNmRlZjlmMzczIiwidHlwZSI6IkRhdGV0aW1lVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRhdGFfc291cmNlIjp7ImlkIjoiMDhiYTM5MTgtYWQxZi00MTdhLWJhNTMtZTU4ZmQxYTdjYzFmIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSwiZ2x5cGgiOnsiaWQiOiI2MDA2MGJjYS0zNGRjLTQ5ZWItOWEzOS1jMWRhMjNmMjVlMDgiLCJ0eXBlIjoiTGluZSJ9LCJob3Zlcl9nbHlwaCI6bnVsbCwibXV0ZWRfZ2x5cGgiOm51bGwsIm5vbnNlbGVjdGlvbl9nbHlwaCI6eyJpZCI6ImNlYjJjOGJiLTA2YWItNDMwNS1iYzBiLTc3M2VkZDBmZmM1ZiIsInR5cGUiOiJMaW5lIn0sInNlbGVjdGlvbl9nbHlwaCI6bnVsbCwidmlldyI6eyJpZCI6IjZkZmI4MjIxLTc2MTUtNGFmZS04ZTE2LWU4NmI0OTEwZjZhOSIsInR5cGUiOiJDRFNWaWV3In19LCJpZCI6IjE0OTM0MDA2LTBlODAtNGQwNy1hYmYxLWI2YzIzZjUzMzQ1ZiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJyb290X2lkcyI6WyJhMDc1OGIyYS03N2YzLTRkMzctODJhOC00NmQxOTk5Y2YwOTYiXX0sInRpdGxlIjoiQm9rZWggQXBwbGljYXRpb24iLCJ2ZXJzaW9uIjoiMC4xMi4xNCJ9fQogICAgICAgIDwvc2NyaXB0PgogICAgICAgIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgICAgICAgIChmdW5jdGlvbigpIHsKICAgICAgICAgICAgdmFyIGZuID0gZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgQm9rZWguc2FmZWx5KGZ1bmN0aW9uKCkgewogICAgICAgICAgICAgICAgKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgZnVuY3Rpb24gZW1iZWRfZG9jdW1lbnQocm9vdCkgewogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB2YXIgZG9jc19qc29uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2FlODFiN2Y5LTk5MGUtNDkzOC05MzhhLWZmNjk3OWFiN2RhZicpLnRleHRDb250ZW50OwogICAgICAgICAgICAgICAgICB2YXIgcmVuZGVyX2l0ZW1zID0gW3siZG9jaWQiOiJiMDQ3N2VmYi1jZWRiLTQxMmUtODcxYS04YWQ4MzE1ZDRjYzYiLCJlbGVtZW50aWQiOiIyZGEwYzg3Zi1jZjJiLTRmZTctOTI5Ny1jN2NhMjNiZTY3MjYiLCJtb2RlbGlkIjoiYTA3NThiMmEtNzdmMy00ZDM3LTgyYTgtNDZkMTk5OWNmMDk2In1dOwogICAgICAgICAgICAgICAgICByb290LkJva2VoLmVtYmVkLmVtYmVkX2l0ZW1zKGRvY3NfanNvbiwgcmVuZGVyX2l0ZW1zKTsKICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgICAgICB2YXIgYXR0ZW1wdHMgPSAwOwogICAgICAgICAgICAgICAgICAgIHZhciB0aW1lciA9IHNldEludGVydmFsKGZ1bmN0aW9uKHJvb3QpIHsKICAgICAgICAgICAgICAgICAgICAgIGlmIChyb290LkJva2VoICE9PSB1bmRlZmluZWQpIHsKICAgICAgICAgICAgICAgICAgICAgICAgZW1iZWRfZG9jdW1lbnQocm9vdCk7CiAgICAgICAgICAgICAgICAgICAgICAgIGNsZWFySW50ZXJ2YWwodGltZXIpOwogICAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgICAgYXR0ZW1wdHMrKzsKICAgICAgICAgICAgICAgICAgICAgIGlmIChhdHRlbXB0cyA+IDEwMCkgewogICAgICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZygiQm9rZWg6IEVSUk9SOiBVbmFibGUgdG8gcnVuIEJva2VoSlMgY29kZSBiZWNhdXNlIEJva2VoSlMgbGlicmFyeSBpcyBtaXNzaW5nIikKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgfSwgMTAsIHJvb3QpCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0pKHdpbmRvdyk7CiAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgIH07CiAgICAgICAgICAgIGlmIChkb2N1bWVudC5yZWFkeVN0YXRlICE9ICJsb2FkaW5nIikgZm4oKTsKICAgICAgICAgICAgZWxzZSBkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJET01Db250ZW50TG9hZGVkIiwgZm4pOwogICAgICAgICAgfSkoKTsKICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPg==&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_fc5030ea6f36446e9ec85817b1ba7377.setContent(i_frame_6e4e999a42e64ca29e024c571b5e134a);
            

            marker_f7d508705bf5440c92ef0912b2bd6162.bindPopup(popup_fc5030ea6f36446e9ec85817b1ba7377);

            
        
    

            var marker_0029681616e74713bfd07f1ceed51945 = L.marker(
                [41.5236,-70.6711],
                {
                    icon: new L.Icon.Default()
                    }
                )
                .addTo(map_a13e4f67c7e54889975e34cadade7733);
            
    

                var icon_1ff8ab2c80b343ea8a9477927fc592be = L.AwesomeMarkers.icon({
                    icon: 'stats',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
                marker_0029681616e74713bfd07f1ceed51945.setIcon(icon_1ff8ab2c80b343ea8a9477927fc592be);
            
    
            var popup_9056cd4f54894db38f5e049bd4ecb907 = L.popup({maxWidth: '2650'});

            
                var i_frame_57b60dcb5bb84352aabd3d708b15c98b = $('<iframe src=&quot;data:text/html;charset=utf-8;base64,CiAgICAKPCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICAgIDxoZWFkPgogICAgICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgICAgICA8dGl0bGU+ODQ0NzkzMDwvdGl0bGU+CiAgICAgICAgCjxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4ucHlkYXRhLm9yZy9ib2tlaC9yZWxlYXNlL2Jva2VoLTAuMTIuMTQubWluLmNzcyIgdHlwZT0idGV4dC9jc3MiIC8+CiAgICAgICAgCjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9Imh0dHBzOi8vY2RuLnB5ZGF0YS5vcmcvYm9rZWgvcmVsZWFzZS9ib2tlaC0wLjEyLjE0Lm1pbi5qcyI+PC9zY3JpcHQ+CjxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij4KICAgIEJva2VoLnNldF9sb2dfbGV2ZWwoImluZm8iKTsKPC9zY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICAKICAgICAgICA8ZGl2IGNsYXNzPSJiay1yb290Ij4KICAgICAgICAgICAgPGRpdiBjbGFzcz0iYmstcGxvdGRpdiIgaWQ9IjdiYmVhODVhLTA2MjctNGJhMS05ZTc0LTNjYjIyNjM0MWIwNSI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgCiAgICAgICAgPHNjcmlwdCB0eXBlPSJhcHBsaWNhdGlvbi9qc29uIiBpZD0iYTQ3NTAyMjgtNGU4Yi00ZWJjLWFkY2EtZGYxYzc2OTNjZTBmIj4KICAgICAgICAgIHsiNTZkMzVhOWMtZmJmNS00MmRlLTlkZWItNTFiYTdmYTRkZjU3Ijp7InJvb3RzIjp7InJlZmVyZW5jZXMiOlt7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsInJlbmRlcmVycyI6W3siaWQiOiI3MDVkM2E2My0zNGI3LTQxMTItODJmZi01ZTgwY2Q3MjQxZDAiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XSwidG9vbHRpcHMiOltbIk5hbWUiLCJUaW1lX3YyX0F2ZXJhZ2VzX0Jlc3QiXSxbIkJpYXMiLCItMS4xNSJdLFsiU2tpbGwiLCIwLjA5Il1dfSwiaWQiOiI3ODg2NzI0NC00OGEzLTRiNjUtODQ5Yy1jZWVlMjIyYzg5YjgiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJhdHRyaWJ1dGVzIjp7ImxhYmVsIjp7InZhbHVlIjoiVGltZV92Ml9BdmVyYWdlc19CZXN0In0sInJlbmRlcmVycyI6W3siaWQiOiI3MDVkM2E2My0zNGI3LTQxMTItODJmZi01ZTgwY2Q3MjQxZDAiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiY2U4Zjc0MjctNDQ2MS00YjBhLWExZTItNmU1NmUxMTc2NTQxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw2XX0sImlkIjoiNTViZmYwYWYtNWYyNy00NWE2LTg2NTctODJkMTNiMzZjYzgwIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiJkNmJmNzdlMS01ODNlLTQ0NjItYTcwNi1mMDJiOGE1NGE5NTUiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiI3N2M2Mzg1Mi05NmM4LTQzODgtODExMC0zNjg5ZDI2YjQ0YTciLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6eyJsYWJlbCI6eyJ2YWx1ZSI6IlRpbWVfdjJfSGlzdG9yeV9CZXN0In0sInJlbmRlcmVycyI6W3siaWQiOiIyZDNlZGM3MS04ZWVmLTRhNGItYWQzNC03YjRkMzg1ZDFiYzMiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiNDFmYTNmNWQtM2JlOC00NGU4LWI2ZjUtNWUzMmE0OWExMDUxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsicGxvdCI6eyJpZCI6IjBjYjQ2NjU0LTBiN2YtNDYzZi1hMTA2LTNhOTdhZDA3Mzk0MCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiIzOTk1MzU1Yi1kMDExLTRiODItOGI2ZC03YmI4ZjI0NTNkYzkiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiZGQ5YWJlMDYtN2NkYS00ZTVjLWIyZTYtNTkwOTM2ZTI2YWI2IiwidHlwZSI6IkdyaWQifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjYzViMGQ1IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJjODUyZWNmMS1mMTUxLTQ0MDMtOWEzNy1mYWQxNDNhMmFjOTMiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6IjU5YzFmYWIzLTliNDYtNDQwMC04ZjNkLWVhODZjMWEyZDQ2NyIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiY2UzZmVjM2MtYjAwYS00NjhjLTk0ZDYtMjQ5YmViOWIyYzJiIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiI4YTZlYThmYS04MGNiLTQ5YjQtYTc3Ni1mZTkwYjI4Zjg5MzgiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiI2NjlmNDExMy03MTI5LTQ1YjYtOWRjZi04NjUzNjgyYTkyM2UiLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiI1ODE5YTg5Mi1kMGFmLTQ1OTktYWVkMi1lNDhlMTllNzIxYWIiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbH0sImlkIjoiOWUzNzhkYjYtZmI0MS00MjNlLThhYWYtZTg5NzZjOGM4MmQ3IiwidHlwZSI6IkRhdGFSYW5nZTFkIn0seyJhdHRyaWJ1dGVzIjp7ImFjdGl2ZV9kcmFnIjoiYXV0byIsImFjdGl2ZV9pbnNwZWN0IjoiYXV0byIsImFjdGl2ZV9zY3JvbGwiOiJhdXRvIiwiYWN0aXZlX3RhcCI6ImF1dG8iLCJ0b29scyI6W3siaWQiOiI5ODVhMzkxZi04ZjBmLTQ5NTAtYmIwNi1hMWQyMDBkZGFiMWIiLCJ0eXBlIjoiUGFuVG9vbCJ9LHsiaWQiOiIwNzJlYWMyZC0zMDhkLTRlYWYtYjc1Zi0zODc2MzcwMzVkNzYiLCJ0eXBlIjoiQm94Wm9vbVRvb2wifSx7ImlkIjoiMzAyNDkwYWYtNTIyZS00NDQ2LWEzNzMtMDQxNWQ4MTNiODA0IiwidHlwZSI6IlJlc2V0VG9vbCJ9LHsiaWQiOiI0YTgzNjRjYS02ZDEwLTRhMTYtYWYzNC01NzQ1NTAyM2IyYjUiLCJ0eXBlIjoiSG92ZXJUb29sIn0seyJpZCI6ImFjZjUwYzBiLTYxZjUtNGM3OS05M2MzLTE0ZjVlNjc0MDRmNyIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImlkIjoiNzg4NjcyNDQtNDhhMy00YjY1LTg0OWMtY2VlZTIyMmM4OWI4IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiaWQiOiJmNDJiZmM3MC1iOWYxLTQwNzMtODJhYS1iNWQ0YmRiZWNmZGQiLCJ0eXBlIjoiSG92ZXJUb29sIn1dfSwiaWQiOiJmYjUyNzI5MC1lMWM1LTQyMTMtODI0YS1hYzRhNjY2YjQ3YzMiLCJ0eXBlIjoiVG9vbGJhciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUFBSWtBZWRrSUFBT2lRUXg1MlFnQUEwUDlHSG5aQ0FBQzRia29lZGtJQUFLRGRUUjUyUWdBQWlFeFJIblpDQUFCd3UxUWVka0lBQUZncVdCNTJRZ0FBUUpsYkhuWkNBQUFvQ0Y4ZWRrSUFBQkIzWWg1MlFnQUErT1ZsSG5aQ0FBRGdWR2tlZGtJQUFNakRiQjUyUWdBQXNESndIblpDQUFDWW9YTWVka0lBQUlBUWR4NTJRZ0FBYUg5NkhuWkNBQUJRN24wZWRrSUFBRGhkZ1I1MlFnQUFJTXlFSG5aQ0FBQUlPNGdlZGtJQUFQQ3BpeDUyUWdBQTJCaVBIblpDQUFEQWg1SWVka0lBQUtqMmxSNTJRZ0FBa0dXWkhuWkNBQUI0MUp3ZWRrSUFBR0JEb0I1MlFnQUFTTEtqSG5aQ0FBQXdJYWNlZGtJQUFCaVFxaDUyUWdBQUFQK3RIblpDQUFEb2JiRWVka0lBQU5EY3RCNTJRZ0FBdUV1NEhuWkNBQUNndXJzZWRrSUFBSWdwdng1MlFnQUFjSmpDSG5aQ0FBQllCOFllZGtJQUFFQjJ5UjUyUWdBQUtPWE1IblpDQUFBUVZOQWVka0lBQVBqQzB4NTJRZ0FBNERIWEhuWkNBQURJb05vZWRrSUFBTEFQM2g1MlFnQUFtSDdoSG5aQ0FBQ0E3ZVFlZGtJQUFHaGM2QjUyUWdBQVVNdnJIblpDQUFBNE91OGVka0lBQUNDcDhoNTJRZ0FBQ0JqMkhuWkNBQUR3aHZrZWRrSUFBTmoxL0I1MlFnQUF3R1FBSDNaQ0FBQ28wd01mZGtJQUFKQkNCeDkyUWdBQWVMRUtIM1pDQUFCZ0lBNGZka0lBQUVpUEVSOTJRZ0FBTVA0VUgzWkNBQUFZYlJnZmRrSUFBQURjR3g5MlFnQUE2RW9mSDNaQ0FBRFF1U0lmZGtJQUFMZ29KaDkyUWdBQW9KY3BIM1pDQUFDSUJpMGZka0lBQUhCMU1COTJRZ0FBV09RekgzWkMiLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6Wzk2XX0sInkiOnsiX19uZGFycmF5X18iOiJBQUFBSUl2bndiOEFBQURBTGpPL3Z3QUFBRUJIbDdxL0FBQUF3Ri83dGI4QUFBRGd1UlhndndBQUFPQUhiTzIvQUFBQTRDcGg5YjhBQUFDQUdYRHl2d0FBQUFBUS91Ni9BQUFBSU8wYjZiOEFBQUFBZnhUanZ3QUFBT0FoR3RxL0FBQUFZSXNXekw4QUFBQ2d4MWF1dndBQUFDQlAxcmsvQUFBQWdBQzIwRDhBQUFBQW1IWFJ2d0FBQUVDWTBPbS9BQUFBUURKejliOEFBQUJnWVVIenZ3QUFBSUNRRC9HL0FBQUFZSCs3N2I4QUFBQ0FuY3pzdndBQUFLQzczZXUvQUFBQUlMSW13cjhBQUFCZ01OdWd2d0FBQU9BemNyTS9BQUFBQUFDcHh6OEFBQURnWkRMRXZ3QUFBR0J5QStDL0FBQUFvRXY2NnI4QUFBQmcva251dndBQUFJRFl6UEMvQUFBQTRMRjA4cjhBQUFBQUt3RG92d0FBQUtEa0xkYS9BQUFBNEdVa3JUOEFBQURBZVJETlB3QUFBQ0R0YTlrL0FBQUFvTTRuNGo4QUFBQ0FsQnJVUHdBQUFLQmRMSzgvQUFBQUlQcWV5TDhBQUFEZ0VuN2h2d0FBQUNCbjFPeS9BQUFBd0YwVjlMOEFBQUNnV3pycXZ3QUFBRUQzazlpL0FBQUFZRVJtcWo4QUFBQ0FlenErUHdBQUFHRHFvTWMvQUFBQWdFc1MwRDhBQUFDZ05qbTBQd0FBQUtEQTFyZS9BQUFBQUs3NTBMOEFBQUNBbWJUa3Z3QUFBQUF1ZHZDL0FBQUFRQStTOXI4QUFBQ0EzeGZ3dndBQUFLQmZPK08vQUFBQW9BQWN5YjhBQUFBZ2p1T292d0FBQUNCelZMay9BQUFBb0ZhTnp6OEFBQUNBdW1QTVB3QUFBR0FlT3NrL0FBQUFRSUlReGo4QUFBQkFjOURTdndBQUFNQ1RWT2kvQUFBQUFIZWc4NzhBQUFEZ09kRHN2d0FBQU9DRlgrSy9BQUFBQUVlN3o3OEFBQURBTzBIRHZ3QUFBTURCSEt1L0FBQUFZR3ZMcGo4QUFBREFoaUM1UHdBQUFPQ3JiY00vQUFBQVlCUkx5ajhBQUFDQUc3VFJ2d0FBQUtEZ1J1aS9BQUFBd05uWjg3OEFBQUNnZXRyd3Z3QUFBQ0EzdHV1L0FBQUE0SGkzNWI4QUFBQWdhVm5odndBQUFPQ3k5dG0vQUFBQWdKTTYwYjhBQUFCQVc4Tzh2d0FBQUFBdng2WS9BQUFBSUVYRnlUOEFBQUJBODJEUnZ3QUFBS0JFMHVlL0FBQUF3QWQ2ODc4QUFBREFCM3J6dndBQUFNQUhldk8vIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOls5Nl19fX0sImlkIjoiYmU5NjkyMzQtOGRlYS00MmVmLThlOGMtYTMxY2FlYmE5N2M3IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnsibWFudGlzc2FzIjpbMSwyLDVdLCJtYXhfaW50ZXJ2YWwiOjUwMC4wLCJudW1fbWlub3JfdGlja3MiOjB9LCJpZCI6IjZmZDE4M2E1LWVjZTUtNDVhZS04MDBhLWRjZjRjOWY5OWVhNyIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUFPSUFUSG5aQ0FBQWc3eFllZGtJQUFBaGVHaDUyUWdBQThNd2RIblpDQUFEWU95RWVka0lBQU1DcUpCNTJRZ0FBcUJrb0huWkNBQUNRaUNzZWRrSUFBSGozTGg1MlFnQUFZR1l5SG5aQ0FBQkkxVFVlZGtJQUFEQkVPUjUyUWdBQUdMTThIblpDQUFBQUlrQWVka0lBQU9pUVF4NTJRZ0FBMFA5R0huWkNBQUM0YmtvZWRrSUFBS0RkVFI1MlFnQUFpRXhSSG5aQ0FBQnd1MVFlZGtJQUFGZ3FXQjUyUWdBQVFKbGJIblpDQUFBb0NGOGVka0lBQUJCM1loNTJRZ0FBK09WbEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ1lvWE1lZGtJQUFJQVFkeDUyUWdBQWFIOTZIblpDQUFCUTduMGVka0lBQURoZGdSNTJRZ0FBSU15RUhuWkNBQUFJTzRnZWRrSUFBUENwaXg1MlFnQUEyQmlQSG5aQ0FBREFoNUllZGtJQUFLajJsUjUyUWdBQWtHV1pIblpDQUFCNDFKd2Vka0lBQUdCRG9CNTJRZ0FBU0xLakhuWkNBQUF3SWFjZWRrSUFBQmlRcWg1MlFnQUFBUCt0SG5aQ0FBRG9iYkVlZGtJQUFORGN0QjUyUWdBQXVFdTRIblpDQUFDZ3Vyc2Vka0lBQUlncHZ4NTJRZ0FBY0pqQ0huWkNBQUJZQjhZZWRrSUFBRUIyeVI1MlFnQUFLT1hNSG5aQ0FBQVFWTkFlZGtJQUFQakMweDUyUWdBQTRESFhIblpDQUFESW9Ob2Vka0lBQUxBUDNoNTJRZ0FBbUg3aEhuWkNBQUNBN2VRZWRrSUFBR2hjNkI1MlFnQUFVTXZySG5aQ0FBQTRPdThlZGtJQUFDQ3A4aDUyUWdBQUNCajJIblpDQUFEd2h2a2Vka0lBQU5qMS9CNTJRZ0FBd0dRQUgzWkNBQUNvMHdNZmRrSUFBSkJDQng5MlFnQUFlTEVLSDNaQ0FBQmdJQTRmZGtJQUFFaVBFUjkyUWdBQU1QNFVIM1pDQUFBWWJSZ2Zka0lBQUFEY0d4OTJRZ0FBNkVvZkgzWkNBQURRdVNJZmRrSUFBTGdvSmg5MlFnQUFvSmNwSDNaQ0FBQ0lCaTBmZGtJQUFIQjFNQjkyUWdBQVdPUXpIM1pDQUFCQVV6Y2Zka0k9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfSwieSI6eyJfX25kYXJyYXlfXyI6IkFBQUF3QTJteGI4QUFBQ2ducHJXdndBQUFFRHFrdUMvQUFBQUFLSzE0YjhBQUFDZzNoN252d0FBQU1BZ2NPZS9BQUFBUUx2eTU3OEFBQUFnYS83bHZ3QUFBR0FTcHQrL0FBQUFRS0J2MUw4QUFBQUFxMnpHdndBQUFNQlIwS08vQUFBQWdEb2doYjhBQUFBQTZPZTh2d0FBQUtCdHR0Ty9BQUFBb015SzJyOEFBQUFnMXZMa3Z3QUFBQUR4YU9lL0FBQUFnSkx5NmI4QUFBQmdaRTNydndBQUFDRFNVK2EvQUFBQVlDbmUzNzhBQUFBZ2doTFd2d0FBQUdEaElNaS9BQUFBd0dOT3Y3OEFBQUNBb0E3SHZ3QUFBS0RJTE5tL0FBQUFRSEtsNGI4QUFBQkFiR0RqdndBQUFLQzhIK2kvQUFBQVlHbk41NzhBQUFCQUNCenB2d0FBQUFBaDdlYS9BQUFBQVBoUzM3OEFBQUFBUDNUVXZ3QUFBR0JNU3NLL0FBQUE0Q09ObmI4QUFBQ2djNUEyUHdBQUFPQjZpTUcvQUFBQVlKN3kxTDhBQUFBQUhaTGJ2d0FBQUdDKzZ1Uy9BQUFBSUUxbDViOEFBQUFBMnYvbXZ3QUFBR0JTS2VlL0FBQUFJQnExNEw4QUFBQ0FBQ1BVdndBQUFBQkkzTUsvQUFBQW9ENnFhNzhBQUFCZ0sxT2xQd0FBQU9EdjQ3Sy9BQUFBb0JFbzByOEFBQUFnZDhmVnZ3QUFBS0J4c3QrL0FBQUFJQlJmNDc4QUFBQmdkQlBrdndBQUFFRGlRZVcvQUFBQTRMYng0TDhBQUFDZ0dwdlJ2d0FBQUFBSkk2dS9BQUFBSUZqT3ZEOEFBQUFBTkg3TlB3QUFBQ0RmUU13L0FBQUFvQ3FHd0Q4QUFBQWdXcTZmUHdBQUFBQUJHOUcvQUFBQVlGRWIyYjhBQUFEZ0ZqWGh2d0FBQUVBMGYrYS9BQUFBUU8xOTVMOEFBQURBbUN6YXZ3QUFBS0NFejdHL0FBQUFBTVh5eWo4QUFBQWd0cmJRUHdBQUFNRDVxTkEvQUFBQW9MeFN3VDhBQUFEQTV3eWF2d0FBQUVBVmN0Qy9BQUFBWUNmczJyOEFBQUJBYytIaHZ3QUFBQ0M4TGVTL0FBQUFBS0w4NGI4QUFBQWdGaWJYdndBQUFNQU1POEcvQUFBQUFMbktscjhBQUFBQWRKZTJQd0FBQUdEVFlzRS9BQUFBb0MxUHVqOEFBQUJBZFFLelB3QUFBS0JtYTZvL0FBQUFJR1I3eUw4QUFBREFFVXJXdndBQUFLQXZIdDYvQUFBQWdIZWEzYjhBQUFCQWk0clB2d0FBQUtESFY1ay9BQUFBb0Q1S3pEOEFBQUFnWE9YVFB3QUFBRUE4bHRrL0FBQUFnTVMyMWo4QUFBQmdtSjNQUHdBQUFPQVEwTW8vQUFBQXdFTFBzajhBQUFDQWE2YkJ2d0FBQU1DVnd0Qy9BQUFBZ0ZRUDJMOEFBQUFBYW4vVnZ3QUFBT0R6S3NLL0FBQUF3R2Zhc1Q4QUFBQ2dZR0xEUHdBQUFDQXJnczAvQUFBQVFGcjV5ejhBQUFCZ0ZXMjlQd0FBQU1EMDJaay9BQUFBZ01GemlEOEFBQURBY1c3R3Z3QUFBSUJiaDg2L0FBQUFRRG1jMWI4QUFBREFKR1RYdndBQUFPQW51OGUvQUFBQTRDZTd4Nzg9IiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMjFdfX19LCJpZCI6ImQ2YmY3N2UxLTU4M2UtNDQ2Mi1hNzA2LWYwMmI4YTU0YTk1NSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiIyOGZiMTczZC1mOWNhLTQ5YTktODkyNy1mMTcwY2M1NmJhZWQiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImM5NTk0ZjAxLTYzMDYtNDAyNy04Yjk1LTM2OWRkMjE1MjE4MSIsInR5cGUiOiJEYXRldGltZVRpY2tGb3JtYXR0ZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6ImUxMGM2YjJkLTNjYWUtNDZiNS1iYmM3LWI0NjQxNjZlMTNiYiIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSx7ImF0dHJpYnV0ZXMiOnt9LCJpZCI6IjMwMjQ5MGFmLTUyMmUtNDQ0Ni1hMzczLTA0MTVkODEzYjgwNCIsInR5cGUiOiJSZXNldFRvb2wifSx7ImF0dHJpYnV0ZXMiOnsibGFiZWwiOnsidmFsdWUiOiJTRUNPT1JBL0NOQVBTIn0sInJlbmRlcmVycyI6W3siaWQiOiJmZDQxZTJmYi0xYWZiLTQ2MTktYTMxOC1kOGNiMDI2NTY4NmMiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XX0sImlkIjoiZWMxMTVhZTQtMTZhMC00MDNhLWIyMDctMzU3OWVjZWIxYWUxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImF0dHJpYnV0ZXMiOnsicGxvdCI6bnVsbCwidGV4dCI6Ijg0NDc5MzAifSwiaWQiOiIxMjVhODQzMy05ZGMyLTRiYjQtOTk5NS0xZWM0NDhkNTI0MGUiLCJ0eXBlIjoiVGl0bGUifSx7ImF0dHJpYnV0ZXMiOnsibnVtX21pbm9yX3RpY2tzIjo1LCJ0aWNrZXJzIjpbeyJpZCI6IjZmZDE4M2E1LWVjZTUtNDVhZS04MDBhLWRjZjRjOWY5OWVhNyIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiaWQiOiIyNzBhZmRjYi1hNzIyLTQxZjctYmFkYi0zMjA2YjdlZmQ5OGIiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImlkIjoiMmZlMzNlOWMtYzBhNy00N2VmLWFjNjItMDI1ZThjZjM1ZDVhIiwidHlwZSI6IkFkYXB0aXZlVGlja2VyIn0seyJpZCI6IjY5ZDUxNTEyLTNlNGEtNDcwZC04MGQxLTRkYmYwZGY5MDk4YSIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJpZCI6IjQwYTcxOWY5LTIzY2QtNDRmOC1hOTYyLTZkYWQ4NmMzYTZiMSIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJpZCI6Ijk4ZGU4NWZiLTMyOTUtNGVlZS05MTg5LTM3MjQ2YWEyMTBmZiIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJpZCI6ImE5NmYxNDljLTU1NzItNGJjMy05YWFmLWE3ZDZkNDNiMmQxNSIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJpZCI6ImZjOTBhY2ZmLTFiNDYtNDEzOC04YjNmLTdhODQxZGU4YWRiMCIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiMDExOGI3NTYtYTU3NS00ZDQ5LWJkMjUtMzZiYTJkM2U2MTQxIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiaWQiOiI2NzFhM2E5Ni1hZDA1LTRhM2UtYTgxMC05YWRlN2VjNTlkMTAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJpZCI6IjU1YmZmMGFmLTVmMjctNDVhNi04NjU3LTgyZDEzYjM2Y2M4MCIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImlkIjoiZDY1YjEyZTMtNTBiNy00ZWMxLWIxNWUtM2NhZjZmZTJlMjcwIiwidHlwZSI6IlllYXJzVGlja2VyIn1dfSwiaWQiOiIzOTk1MzU1Yi1kMDExLTRiODItOGI2ZC03YmI4ZjI0NTNkYzkiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiYXhpc19sYWJlbCI6IkRhdGUvdGltZSIsImZvcm1hdHRlciI6eyJpZCI6ImM5NTk0ZjAxLTYzMDYtNDAyNy04Yjk1LTM2OWRkMjE1MjE4MSIsInR5cGUiOiJEYXRldGltZVRpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6IjBjYjQ2NjU0LTBiN2YtNDYzZi1hMTA2LTNhOTdhZDA3Mzk0MCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiIzOTk1MzU1Yi1kMDExLTRiODItOGI2ZC03YmI4ZjI0NTNkYzkiLCJ0eXBlIjoiRGF0ZXRpbWVUaWNrZXIifX0sImlkIjoiNGZkOGQxMDMtYTQxMy00ODU3LTgxMGEtODExNjc3YjA2OGYwIiwidHlwZSI6IkRhdGV0aW1lQXhpcyJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiI5MmRhM2ZiMy05NWIyLTRhYmQtODg1Zi0yMTk2NWQ4ZGJmZmMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiIxYjg0YTk4NC1hYjQ3LTQzMWItYTA0My01MWUzYmJkYTdmNWIiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6eyJiYXNlIjoyNCwibWFudGlzc2FzIjpbMSwyLDQsNiw4LDEyXSwibWF4X2ludGVydmFsIjo0MzIwMDAwMC4wLCJtaW5faW50ZXJ2YWwiOjM2MDAwMDAuMCwibnVtX21pbm9yX3RpY2tzIjowfSwiaWQiOiIyZmUzM2U5Yy1jMGE3LTQ3ZWYtYWM2Mi0wMjVlOGNmMzVkNWEiLCJ0eXBlIjoiQWRhcHRpdmVUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsib3ZlcmxheSI6eyJpZCI6ImIzOGNiMzU2LTI2MTAtNGJiNi1hZTYyLWZjOGJlYWEwNTlkZCIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn19LCJpZCI6IjA3MmVhYzJkLTMwOGQtNGVhZi1iNzVmLTM4NzYzNzAzNWQ3NiIsInR5cGUiOiJCb3hab29tVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJsYWJlbCI6eyJ2YWx1ZSI6Ik9ic2VydmF0aW9ucyJ9LCJyZW5kZXJlcnMiOlt7ImlkIjoiNTgxOWE4OTItZDBhZi00NTk5LWFlZDItZTQ4ZTE5ZTcyMWFiIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV19LCJpZCI6IjU1MTEzYWNhLTJhN2YtNGY1Ni04OTA5LWViZTQ0Y2I2NjZjOCIsInR5cGUiOiJMZWdlbmRJdGVtIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuMSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjMWY3N2I0IiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiJiMDk2MThkOC1lOTFiLTRmMWEtOGE5OS04NzBkYTI3Yjc2NDAiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6eyJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6ImNyaW1zb24iLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImNlM2ZlYzNjLWIwMGEtNDY4Yy05NGQ2LTI0OWJlYjliMmMyYiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7Im1vbnRocyI6WzAsMiw0LDYsOCwxMF19LCJpZCI6IjAxMThiNzU2LWE1NzUtNGQ0OS1iZDI1LTM2YmEyZDNlNjE0MSIsInR5cGUiOiJNb250aHNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6IjhhNmVhOGZhLTgwY2ItNDliNC1hNzc2LWZlOTBiMjhmODkzOCIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImxpbmVfYWxwaGEiOjAuNjUsImxpbmVfY2FwIjoicm91bmQiLCJsaW5lX2NvbG9yIjoiIzk0NjdiZCIsImxpbmVfam9pbiI6InJvdW5kIiwibGluZV93aWR0aCI6NSwieCI6eyJmaWVsZCI6IngifSwieSI6eyJmaWVsZCI6InkifX0sImlkIjoiOWYyYmQyNjUtNWRlOS00Yjk1LWI0MTUtOGEyNDA2NzExZWMxIiwidHlwZSI6IkxpbmUifSx7ImF0dHJpYnV0ZXMiOnsiYmFzZSI6NjAsIm1hbnRpc3NhcyI6WzEsMiw1LDEwLDE1LDIwLDMwXSwibWF4X2ludGVydmFsIjoxODAwMDAwLjAsIm1pbl9pbnRlcnZhbCI6MTAwMC4wLCJudW1fbWlub3JfdGlja3MiOjB9LCJpZCI6IjI3MGFmZGNiLWE3MjItNDFmNy1iYWRiLTMyMDZiN2VmZDk4YiIsInR5cGUiOiJBZGFwdGl2ZVRpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwicmVuZGVyZXJzIjpbeyJpZCI6IjJkM2VkYzcxLThlZWYtNGE0Yi1hZDM0LTdiNGQzODVkMWJjMyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn1dLCJ0b29sdGlwcyI6W1siTmFtZSIsIlRpbWVfdjJfSGlzdG9yeV9CZXN0Il0sWyJCaWFzIiwiLTAuODMiXSxbIlNraWxsIiwiMC4wOCJdXX0sImlkIjoiZjQyYmZjNzAtYjlmMS00MDczLTgyYWEtYjVkNGJkYmVjZmRkIiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJheGlzX2xhYmVsIjoiV2F0ZXIgSGVpZ2h0IChtKSIsImZvcm1hdHRlciI6eyJpZCI6ImUxMGM2YjJkLTNjYWUtNDZiNS1iYmM3LWI0NjQxNjZlMTNiYiIsInR5cGUiOiJCYXNpY1RpY2tGb3JtYXR0ZXIifSwicGxvdCI6eyJpZCI6IjBjYjQ2NjU0LTBiN2YtNDYzZi1hMTA2LTNhOTdhZDA3Mzk0MCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LCJ0aWNrZXIiOnsiaWQiOiJlMGZhZjgwYi1kZmI4LTQxYTktOWExNy1kYjNhZmE3N2EyYTUiLCJ0eXBlIjoiQmFzaWNUaWNrZXIifX0sImlkIjoiMjhlMWI1ZDMtZmI3ZC00NzVhLThiYjctOTdkZmNhMjQ0M2YzIiwidHlwZSI6IkxpbmVhckF4aXMifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsMiwzLDQsNSw2LDcsOCw5LDEwLDExLDEyLDEzLDE0LDE1LDE2LDE3LDE4LDE5LDIwLDIxLDIyLDIzLDI0LDI1LDI2LDI3LDI4LDI5LDMwLDMxXX0sImlkIjoiNjlkNTE1MTItM2U0YS00NzBkLTgwZDEtNGRiZjBkZjkwOThhIiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsibW9udGhzIjpbMCw0LDhdfSwiaWQiOiI2NzFhM2E5Ni1hZDA1LTRhM2UtYTgxMC05YWRlN2VjNTlkMTAiLCJ0eXBlIjoiTW9udGhzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiJkNjViMTJlMy01MGI3LTRlYzEtYjE1ZS0zY2FmNmZlMmUyNzAiLCJ0eXBlIjoiWWVhcnNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsic291cmNlIjp7ImlkIjoiYmU5NjkyMzQtOGRlYS00MmVmLThlOGMtYTMxY2FlYmE5N2M3IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifX0sImlkIjoiNjg4NWQyZDUtODdjYS00YzAzLWIwZTMtNzYxYjRlMWNlMTY3IiwidHlwZSI6IkNEU1ZpZXcifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImIxNWQwNGJkLWY4ZjQtNDhlNC1hYWNlLWEzNTY0MTg2MDIzNiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImRhdGFfc291cmNlIjp7ImlkIjoiOTJkYTNmYjMtOTViMi00YWJkLTg4NWYtMjE5NjVkOGRiZmZjIiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSwiZ2x5cGgiOnsiaWQiOiJjODUyZWNmMS1mMTUxLTQ0MDMtOWEzNy1mYWQxNDNhMmFjOTMiLCJ0eXBlIjoiTGluZSJ9LCJob3Zlcl9nbHlwaCI6bnVsbCwibXV0ZWRfZ2x5cGgiOm51bGwsIm5vbnNlbGVjdGlvbl9nbHlwaCI6eyJpZCI6ImIwOTYxOGQ4LWU5MWItNGYxYS04YTk5LTg3MGRhMjdiNzY0MCIsInR5cGUiOiJMaW5lIn0sInNlbGVjdGlvbl9nbHlwaCI6bnVsbCwidmlldyI6eyJpZCI6IjFiODRhOTg0LWFiNDctNDMxYi1hMDQzLTUxZTNiYmRhN2Y1YiIsInR5cGUiOiJDRFNWaWV3In19LCJpZCI6IjcwNWQzYTYzLTM0YjctNDExMi04MmZmLTVlODBjZDcyNDFkMCIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJhdHRyaWJ1dGVzIjp7fSwiaWQiOiI5NWMzMzY5MS0xODY2LTQ5NmMtODc4Ny0xYmEwOTQ1NTYzOGUiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSx7ImF0dHJpYnV0ZXMiOnsiY2FsbGJhY2siOm51bGwsInJlbmRlcmVycyI6W3siaWQiOiJmZDQxZTJmYi0xYWZiLTQ2MTktYTMxOC1kOGNiMDI2NTY4NmMiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9XSwidG9vbHRpcHMiOltbIk5hbWUiLCJTRUNPT1JBL0NOQVBTIl0sWyJCaWFzIiwiLTEuMDQiXSxbIlNraWxsIiwiMC40MyJdXX0sImlkIjoiYWNmNTBjMGItNjFmNS00Yzc5LTkzYzMtMTRmNWU2NzQwNGY3IiwidHlwZSI6IkhvdmVyVG9vbCJ9LHsiYXR0cmlidXRlcyI6eyJtb250aHMiOlswLDEsMiwzLDQsNSw2LDcsOCw5LDEwLDExXX0sImlkIjoiZmM5MGFjZmYtMWI0Ni00MTM4LThiM2YtN2E4NDFkZThhZGIwIiwidHlwZSI6Ik1vbnRoc1RpY2tlciJ9LHsiYXR0cmlidXRlcyI6eyJzb3VyY2UiOnsiaWQiOiI1OWMxZmFiMy05YjQ2LTQ0MDAtOGYzZC1lYTg2YzFhMmQ0NjciLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9fSwiaWQiOiI2NjlmNDExMy03MTI5LTQ1YjYtOWRjZi04NjUzNjgyYTkyM2UiLCJ0eXBlIjoiQ0RTVmlldyJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQ0FWcHNkZGtJQUFHakZuaDEyUWdBQVVEU2lIWFpDQUFBNG82VWRka0lBQUNBU3FSMTJRZ0FBQ0lHc0hYWkNBQUR3NzY4ZGRrSUFBTmhlc3gxMlFnQUF3TTIySFhaQ0FBQ29QTG9kZGtJQUFKQ3J2UjEyUWdBQWVCckJIWFpDQUFCZ2ljUWRka0lBQUVqNHh4MTJRZ0FBTUdmTEhYWkNBQUFZMXM0ZGRrSUFBQUJGMGgxMlFnQUE2TFBWSFhaQ0FBRFFJdGtkZGtJQUFMaVIzQjEyUWdBQW9BRGdIWFpDQUFDSWIrTWRka0lBQUhEZTVoMTJRZ0FBV0UzcUhYWkNBQUJBdk8wZGRrSUFBQ2dyOFIxMlFnQUFFSnIwSFhaQ0FBRDRDUGdkZGtJQUFPQjMreDEyUWdBQXlPYitIWFpDQUFDd1ZRSWVka0lBQUpqRUJSNTJRZ0FBZ0RNSkhuWkNBQUJvb2d3ZWRrSUFBRkFSRUI1MlFnQUEwTGtpSDNaQ0FBQzRLQ1lmZGtJQUFLQ1hLUjkyUWdBQWlBWXRIM1pDQUFCd2RUQWZka0lBQUZqa014OTJRZ0FBUUZNM0gzWkMiLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzQyXX0sInkiOnsiX19uZGFycmF5X18iOiI5aWhjajhMMTREOU1ONGxCWU9YWVA4M016TXpNek13L2xrT0xiT2Y3eVQrQmxVT0xiT2U3UDl2NWZtcThkSk0vV21RNzMwK05sNzlZT2JUSWRyNnZQN3gwa3hnRVZzNC83bncvTlY2NjJUK3NIRnBrTzkvalA4WkxONGxCWU9rLzdudy9OVjY2NlQrL254b3YzU1RtUHhGWU9iVElkdUkvWU9YUUl0djUzajhVcmtmaGVoVFdQeEtEd01xaFJjWS9HeS9kSkFhQnBUK2N4Q0N3Y21pUnYvcCthcngwazVnLytuNXF2SFNUeUQ4c2h4Ylp6dmZiUDA1aUVGZzV0T1EvVk9PbG04UWc2RC9UVFdJUVdEbmtQM2pwSmpFSXJOdy9kSk1ZQkZZTzFUOS9hcngwa3hqVVB5UGIrWDVxdk1RL1Nnd0NLNGNXcVQ4Ykw5MGtCb0dsUC95cDhkSk5Zc0EvaGV0UnVCNkYwejl1RW9QQXlxSGRQL0xTVFdJUVdPMC9nWlZEaTJ6bjZ6K05sMjRTZzhEbVB4RllPYlRJZHVJL21HNFNnOERLNFQ4eENLd2NXbVRqUHlVR2daVkRpK2cvIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOls0Ml19fX0sImlkIjoiNTljMWZhYjMtOWI0Ni00NDAwLThmM2QtZWE4NmMxYTJkNDY3IiwidHlwZSI6IkNvbHVtbkRhdGFTb3VyY2UifSx7ImF0dHJpYnV0ZXMiOnsiZGltZW5zaW9uIjoxLCJwbG90Ijp7ImlkIjoiMGNiNDY2NTQtMGI3Zi00NjNmLWExMDYtM2E5N2FkMDczOTQwIiwic3VidHlwZSI6IkZpZ3VyZSIsInR5cGUiOiJQbG90In0sInRpY2tlciI6eyJpZCI6ImUwZmFmODBiLWRmYjgtNDFhOS05YTE3LWRiM2FmYTc3YTJhNSIsInR5cGUiOiJCYXNpY1RpY2tlciJ9fSwiaWQiOiJmODBiMTc0Yi01OTYwLTQ3NWYtYmYwNi03MzZjNmJlZWNiYjciLCJ0eXBlIjoiR3JpZCJ9LHsiYXR0cmlidXRlcyI6eyJiZWxvdyI6W3siaWQiOiI0ZmQ4ZDEwMy1hNDEzLTQ4NTctODEwYS04MTE2NzdiMDY4ZjAiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn1dLCJsZWZ0IjpbeyJpZCI6IjI4ZTFiNWQzLWZiN2QtNDc1YS04YmI3LTk3ZGZjYTI0NDNmMyIsInR5cGUiOiJMaW5lYXJBeGlzIn1dLCJwbG90X2hlaWdodCI6MjUwLCJwbG90X3dpZHRoIjo3NTAsInJlbmRlcmVycyI6W3siaWQiOiI0ZmQ4ZDEwMy1hNDEzLTQ4NTctODEwYS04MTE2NzdiMDY4ZjAiLCJ0eXBlIjoiRGF0ZXRpbWVBeGlzIn0seyJpZCI6ImRkOWFiZTA2LTdjZGEtNGU1Yy1iMmU2LTU5MDkzNmUyNmFiNiIsInR5cGUiOiJHcmlkIn0seyJpZCI6IjI4ZTFiNWQzLWZiN2QtNDc1YS04YmI3LTk3ZGZjYTI0NDNmMyIsInR5cGUiOiJMaW5lYXJBeGlzIn0seyJpZCI6ImY4MGIxNzRiLTU5NjAtNDc1Zi1iZjA2LTczNmM2YmVlY2JiNyIsInR5cGUiOiJHcmlkIn0seyJpZCI6ImIzOGNiMzU2LTI2MTAtNGJiNi1hZTYyLWZjOGJlYWEwNTlkZCIsInR5cGUiOiJCb3hBbm5vdGF0aW9uIn0seyJpZCI6IjU4MTlhODkyLWQwYWYtNDU5OS1hZWQyLWU0OGUxOWU3MjFhYiIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6ImZkNDFlMmZiLTFhZmItNDYxOS1hMzE4LWQ4Y2IwMjY1Njg2YyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjcwNWQzYTYzLTM0YjctNDExMi04MmZmLTVlODBjZDcyNDFkMCIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjJkM2VkYzcxLThlZWYtNGE0Yi1hZDM0LTdiNGQzODVkMWJjMyIsInR5cGUiOiJHbHlwaFJlbmRlcmVyIn0seyJpZCI6IjhlOWMwMjdjLWY1NzgtNDJhZC1hNDRlLTcwNDE3YWE5Njc0ZSIsInR5cGUiOiJMZWdlbmQifV0sInJpZ2h0IjpbeyJpZCI6IjhlOWMwMjdjLWY1NzgtNDJhZC1hNDRlLTcwNDE3YWE5Njc0ZSIsInR5cGUiOiJMZWdlbmQifV0sInRpdGxlIjp7ImlkIjoiMTI1YTg0MzMtOWRjMi00YmI0LTk5OTUtMWVjNDQ4ZDUyNDBlIiwidHlwZSI6IlRpdGxlIn0sInRvb2xiYXIiOnsiaWQiOiJmYjUyNzI5MC1lMWM1LTQyMTMtODI0YS1hYzRhNjY2YjQ3YzMiLCJ0eXBlIjoiVG9vbGJhciJ9LCJ0b29sYmFyX2xvY2F0aW9uIjoiYWJvdmUiLCJ4X3JhbmdlIjp7ImlkIjoiOWUzNzhkYjYtZmI0MS00MjNlLThhYWYtZTg5NzZjOGM4MmQ3IiwidHlwZSI6IkRhdGFSYW5nZTFkIn0sInhfc2NhbGUiOnsiaWQiOiIyOGZiMTczZC1mOWNhLTQ5YTktODkyNy1mMTcwY2M1NmJhZWQiLCJ0eXBlIjoiTGluZWFyU2NhbGUifSwieV9yYW5nZSI6eyJpZCI6ImIxNGNkNTc1LTkwOTUtNDc0Ni05Nzk3LTdjMzk2NTgwNDE2OSIsInR5cGUiOiJEYXRhUmFuZ2UxZCJ9LCJ5X3NjYWxlIjp7ImlkIjoiOTVjMzM2OTEtMTg2Ni00OTZjLTg3ODctMWJhMDk0NTU2MzhlIiwidHlwZSI6IkxpbmVhclNjYWxlIn19LCJpZCI6IjBjYjQ2NjU0LTBiN2YtNDYzZi1hMTA2LTNhOTdhZDA3Mzk0MCIsInN1YnR5cGUiOiJGaWd1cmUiLCJ0eXBlIjoiUGxvdCJ9LHsiYXR0cmlidXRlcyI6eyJjbGlja19wb2xpY3kiOiJtdXRlIiwiaXRlbXMiOlt7ImlkIjoiNTUxMTNhY2EtMmE3Zi00ZjU2LTg5MDktZWJlNDRjYjY2NmM4IiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImlkIjoiZWMxMTVhZTQtMTZhMC00MDNhLWIyMDctMzU3OWVjZWIxYWUxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImlkIjoiY2U4Zjc0MjctNDQ2MS00YjBhLWExZTItNmU1NmUxMTc2NTQxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifSx7ImlkIjoiNDFmYTNmNWQtM2JlOC00NGU4LWI2ZjUtNWUzMmE0OWExMDUxIiwidHlwZSI6IkxlZ2VuZEl0ZW0ifV0sImxvY2F0aW9uIjpbMCw2MF0sInBsb3QiOnsiaWQiOiIwY2I0NjY1NC0wYjdmLTQ2M2YtYTEwNi0zYTk3YWQwNzM5NDAiLCJzdWJ0eXBlIjoiRmlndXJlIiwidHlwZSI6IlBsb3QifX0sImlkIjoiOGU5YzAyN2MtZjU3OC00MmFkLWE0NGUtNzA0MTdhYTk2NzRlIiwidHlwZSI6IkxlZ2VuZCJ9LHsiYXR0cmlidXRlcyI6eyJkYXRhX3NvdXJjZSI6eyJpZCI6ImQ2YmY3N2UxLTU4M2UtNDQ2Mi1hNzA2LWYwMmI4YTU0YTk1NSIsInR5cGUiOiJDb2x1bW5EYXRhU291cmNlIn0sImdseXBoIjp7ImlkIjoiNjFiMDdjYmEtNGRlMS00YWViLTlkNmMtN2NiMjJmZTg3ZTdjIiwidHlwZSI6IkxpbmUifSwiaG92ZXJfZ2x5cGgiOm51bGwsIm11dGVkX2dseXBoIjpudWxsLCJub25zZWxlY3Rpb25fZ2x5cGgiOnsiaWQiOiJkYTdkZGVlYi1mZDNjLTRlMGItYjM1NC0wZTE0YTBlZjg4YzYiLCJ0eXBlIjoiTGluZSJ9LCJzZWxlY3Rpb25fZ2x5cGgiOm51bGwsInZpZXciOnsiaWQiOiI3N2M2Mzg1Mi05NmM4LTQzODgtODExMC0zNjg5ZDI2YjQ0YTciLCJ0eXBlIjoiQ0RTVmlldyJ9fSwiaWQiOiIyZDNlZGM3MS04ZWVmLTRhNGItYWQzNC03YjRkMzg1ZDFiYzMiLCJ0eXBlIjoiR2x5cGhSZW5kZXJlciJ9LHsiYXR0cmlidXRlcyI6eyJjYWxsYmFjayI6bnVsbCwiY29sdW1uX25hbWVzIjpbIngiLCJ5Il0sImRhdGEiOnsieCI6eyJfX25kYXJyYXlfXyI6IkFBQmdpY1FkZGtJQUFFajR4eDEyUWdBQU1HZkxIWFpDQUFBZzd4WWVka0lBQUFoZUdoNTJRZ0FBOE13ZEhuWkNBQURnVkdrZWRrSUFBTWpEYkI1MlFnQUFzREp3SG5aQ0FBQ2d1cnNlZGtJQUFJZ3B2eDUyUWdBQWNKakNIblpDIiwiZHR5cGUiOiJmbG9hdDY0Iiwic2hhcGUiOlsxMl19LCJ5Ijp7Il9fbmRhcnJheV9fIjoiQUFBQXdMZXozYjhBQUFCZ1RwL2R2d0FBQUNEbGl0Mi9BQUFBSU5qSjI3OEFBQUFnQ0UvYnZ3QUFBQUE0MU5xL0FBQUFRRmRHMEw4QUFBQ0E1dS9QdndBQUFJQWVVOCsvQUFBQVlPN1p3YjhBQUFCZzd0bkJ2d0FBQUdEdTJjRy8iLCJkdHlwZSI6ImZsb2F0NjQiLCJzaGFwZSI6WzEyXX19fSwiaWQiOiI5MmRhM2ZiMy05NWIyLTRhYmQtODg1Zi0yMTk2NWQ4ZGJmZmMiLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiZTBmYWY4MGItZGZiOC00MWE5LTlhMTctZGIzYWZhNzdhMmE1IiwidHlwZSI6IkJhc2ljVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsfSwiaWQiOiJiMTRjZDU3NS05MDk1LTQ3NDYtOTc5Ny03YzM5NjU4MDQxNjkiLCJ0eXBlIjoiRGF0YVJhbmdlMWQifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC4xLCJsaW5lX2NhcCI6InJvdW5kIiwibGluZV9jb2xvciI6IiMxZjc3YjQiLCJsaW5lX2pvaW4iOiJyb3VuZCIsImxpbmVfd2lkdGgiOjUsIngiOnsiZmllbGQiOiJ4In0sInkiOnsiZmllbGQiOiJ5In19LCJpZCI6ImRhN2RkZWViLWZkM2MtNGUwYi1iMzU0LTBlMTRhMGVmODhjNiIsInR5cGUiOiJMaW5lIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDQsNywxMCwxMywxNiwxOSwyMiwyNSwyOF19LCJpZCI6IjQwYTcxOWY5LTIzY2QtNDRmOC1hOTYyLTZkYWQ4NmMzYTZiMSIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImRheXMiOlsxLDE1XX0sImlkIjoiYTk2ZjE0OWMtNTU3Mi00YmMzLTlhYWYtYTdkNmQ0M2IyZDE1IiwidHlwZSI6IkRheXNUaWNrZXIifSx7ImF0dHJpYnV0ZXMiOnsiYm90dG9tX3VuaXRzIjoic2NyZWVuIiwiZmlsbF9hbHBoYSI6eyJ2YWx1ZSI6MC41fSwiZmlsbF9jb2xvciI6eyJ2YWx1ZSI6ImxpZ2h0Z3JleSJ9LCJsZWZ0X3VuaXRzIjoic2NyZWVuIiwibGV2ZWwiOiJvdmVybGF5IiwibGluZV9hbHBoYSI6eyJ2YWx1ZSI6MS4wfSwibGluZV9jb2xvciI6eyJ2YWx1ZSI6ImJsYWNrIn0sImxpbmVfZGFzaCI6WzQsNF0sImxpbmVfd2lkdGgiOnsidmFsdWUiOjJ9LCJwbG90IjpudWxsLCJyZW5kZXJfbW9kZSI6ImNzcyIsInJpZ2h0X3VuaXRzIjoic2NyZWVuIiwidG9wX3VuaXRzIjoic2NyZWVuIn0sImlkIjoiYjM4Y2IzNTYtMjYxMC00YmI2LWFlNjItZmM4YmVhYTA1OWRkIiwidHlwZSI6IkJveEFubm90YXRpb24ifSx7ImF0dHJpYnV0ZXMiOnsibGluZV9hbHBoYSI6MC42NSwibGluZV9jYXAiOiJyb3VuZCIsImxpbmVfY29sb3IiOiIjOGM1NjRiIiwibGluZV9qb2luIjoicm91bmQiLCJsaW5lX3dpZHRoIjo1LCJ4Ijp7ImZpZWxkIjoieCJ9LCJ5Ijp7ImZpZWxkIjoieSJ9fSwiaWQiOiI2MWIwN2NiYS00ZGUxLTRhZWItOWQ2Yy03Y2IyMmZlODdlN2MiLCJ0eXBlIjoiTGluZSJ9LHsiYXR0cmlidXRlcyI6e30sImlkIjoiOTg1YTM5MWYtOGYwZi00OTUwLWJiMDYtYTFkMjAwZGRhYjFiIiwidHlwZSI6IlBhblRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiZGF5cyI6WzEsOCwxNSwyMl19LCJpZCI6Ijk4ZGU4NWZiLTMyOTUtNGVlZS05MTg5LTM3MjQ2YWEyMTBmZiIsInR5cGUiOiJEYXlzVGlja2VyIn0seyJhdHRyaWJ1dGVzIjp7ImNhbGxiYWNrIjpudWxsLCJyZW5kZXJlcnMiOlt7ImlkIjoiNTgxOWE4OTItZDBhZi00NTk5LWFlZDItZTQ4ZTE5ZTcyMWFiIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInRvb2x0aXBzIjpbWyJOYW1lIiwiT2JzZXJ2YXRpb25zIl0sWyJCaWFzIiwiTkEiXSxbIlNraWxsIiwiTkEiXV19LCJpZCI6IjRhODM2NGNhLTZkMTAtNGExNi1hZjM0LTU3NDU1MDIzYjJiNSIsInR5cGUiOiJIb3ZlclRvb2wifSx7ImF0dHJpYnV0ZXMiOnsiZGF0YV9zb3VyY2UiOnsiaWQiOiJiZTk2OTIzNC04ZGVhLTQyZWYtOGU4Yy1hMzFjYWViYTk3YzciLCJ0eXBlIjoiQ29sdW1uRGF0YVNvdXJjZSJ9LCJnbHlwaCI6eyJpZCI6IjlmMmJkMjY1LTVkZTktNGI5NS1iNDE1LThhMjQwNjcxMWVjMSIsInR5cGUiOiJMaW5lIn0sImhvdmVyX2dseXBoIjpudWxsLCJtdXRlZF9nbHlwaCI6bnVsbCwibm9uc2VsZWN0aW9uX2dseXBoIjp7ImlkIjoiYjE1ZDA0YmQtZjhmNC00OGU0LWFhY2UtYTM1NjQxODYwMjM2IiwidHlwZSI6IkxpbmUifSwic2VsZWN0aW9uX2dseXBoIjpudWxsLCJ2aWV3Ijp7ImlkIjoiNjg4NWQyZDUtODdjYS00YzAzLWIwZTMtNzYxYjRlMWNlMTY3IiwidHlwZSI6IkNEU1ZpZXcifX0sImlkIjoiZmQ0MWUyZmItMWFmYi00NjE5LWEzMTgtZDhjYjAyNjU2ODZjIiwidHlwZSI6IkdseXBoUmVuZGVyZXIifV0sInJvb3RfaWRzIjpbIjBjYjQ2NjU0LTBiN2YtNDYzZi1hMTA2LTNhOTdhZDA3Mzk0MCJdfSwidGl0bGUiOiJCb2tlaCBBcHBsaWNhdGlvbiIsInZlcnNpb24iOiIwLjEyLjE0In19CiAgICAgICAgPC9zY3JpcHQ+CiAgICAgICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPgogICAgICAgICAgKGZ1bmN0aW9uKCkgewogICAgICAgICAgICB2YXIgZm4gPSBmdW5jdGlvbigpIHsKICAgICAgICAgICAgICBCb2tlaC5zYWZlbHkoZnVuY3Rpb24oKSB7CiAgICAgICAgICAgICAgICAoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICBmdW5jdGlvbiBlbWJlZF9kb2N1bWVudChyb290KSB7CiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIHZhciBkb2NzX2pzb24gPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnYTQ3NTAyMjgtNGU4Yi00ZWJjLWFkY2EtZGYxYzc2OTNjZTBmJykudGV4dENvbnRlbnQ7CiAgICAgICAgICAgICAgICAgIHZhciByZW5kZXJfaXRlbXMgPSBbeyJkb2NpZCI6IjU2ZDM1YTljLWZiZjUtNDJkZS05ZGViLTUxYmE3ZmE0ZGY1NyIsImVsZW1lbnRpZCI6IjdiYmVhODVhLTA2MjctNGJhMS05ZTc0LTNjYjIyNjM0MWIwNSIsIm1vZGVsaWQiOiIwY2I0NjY1NC0wYjdmLTQ2M2YtYTEwNi0zYTk3YWQwNzM5NDAifV07CiAgICAgICAgICAgICAgICAgIHJvb3QuQm9rZWguZW1iZWQuZW1iZWRfaXRlbXMoZG9jc19qc29uLCByZW5kZXJfaXRlbXMpOwogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgIGVtYmVkX2RvY3VtZW50KHJvb3QpOwogICAgICAgICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgICAgIHZhciBhdHRlbXB0cyA9IDA7CiAgICAgICAgICAgICAgICAgICAgdmFyIHRpbWVyID0gc2V0SW50ZXJ2YWwoZnVuY3Rpb24ocm9vdCkgewogICAgICAgICAgICAgICAgICAgICAgaWYgKHJvb3QuQm9rZWggIT09IHVuZGVmaW5lZCkgewogICAgICAgICAgICAgICAgICAgICAgICBlbWJlZF9kb2N1bWVudChyb290KTsKICAgICAgICAgICAgICAgICAgICAgICAgY2xlYXJJbnRlcnZhbCh0aW1lcik7CiAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgICBhdHRlbXB0cysrOwogICAgICAgICAgICAgICAgICAgICAgaWYgKGF0dGVtcHRzID4gMTAwKSB7CiAgICAgICAgICAgICAgICAgICAgICAgIGNvbnNvbGUubG9nKCJCb2tlaDogRVJST1I6IFVuYWJsZSB0byBydW4gQm9rZWhKUyBjb2RlIGJlY2F1c2UgQm9rZWhKUyBsaWJyYXJ5IGlzIG1pc3NpbmciKQogICAgICAgICAgICAgICAgICAgICAgICBjbGVhckludGVydmFsKHRpbWVyKTsKICAgICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICB9LCAxMCwgcm9vdCkKICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgfSkod2luZG93KTsKICAgICAgICAgICAgICB9KTsKICAgICAgICAgICAgfTsKICAgICAgICAgICAgaWYgKGRvY3VtZW50LnJlYWR5U3RhdGUgIT0gImxvYWRpbmciKSBmbigpOwogICAgICAgICAgICBlbHNlIGRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoIkRPTUNvbnRlbnRMb2FkZWQiLCBmbik7CiAgICAgICAgICB9KSgpOwogICAgICAgIDwvc2NyaXB0PgogICAgPC9ib2R5Pgo8L2h0bWw+&quot; width=&quot;790&quot; style=&quot;border:none !important;&quot; height=&quot;330&quot;></iframe>')[0];
                popup_9056cd4f54894db38f5e049bd4ecb907.setContent(i_frame_57b60dcb5bb84352aabd3d708b15c98b);
            

            marker_0029681616e74713bfd07f1ceed51945.bindPopup(popup_9056cd4f54894db38f5e049bd4ecb907);

            
        
    
            var layer_control_bd407b48fdec4a1b8f9c899e6fec5626 = {
                base_layers : { &quot;openstreetmap&quot; : tile_layer_e9ad9fea4663457bbed7f64dd167b924, },
                overlays : { &quot;Cluster&quot; : marker_cluster_76b215f3deb04c1aa310c81990ad881c, }
                };
            L.control.layers(
                layer_control_bd407b48fdec4a1b8f9c899e6fec5626.base_layers,
                layer_control_bd407b48fdec4a1b8f9c899e6fec5626.overlays,
                {position: 'topright',
                 collapsed: true,
                 autoZIndex: true
                }).addTo(map_a13e4f67c7e54889975e34cadade7733);
        
</script>" style="width: 100%; height: 750px; border: none"></iframe>


<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2018-03-15-ssh-skillscore.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2018-03-15-ssh-skillscore.ipynb) to run a live instance of this notebook.