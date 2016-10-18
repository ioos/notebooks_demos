---
layout: notebook
title: ""
---


# Finding Near real-time current data

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import os
import sys

ioos_tools = os.path.join(os.path.pardir, os.path.pardir)
sys.path.append(ioos_tools)
```

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
from datetime import datetime, timedelta

# Region: West coast.
bbox = [-123, 36, -121, 40]
crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'

# Temporal range: Last week.
now = datetime.utcnow()
start, stop = now - timedelta(days=(7)), now

# Surface velocity CF names.
cf_names = ['surface_northward_sea_water_velocity',
            'surface_eastward_sea_water_velocity']
```

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
from owslib import fes
from ioos_tools.ioos import fes_date_filter

kw = dict(wildCard='*', escapeChar='\\',
          singleChar='?', propertyname='apiso:AnyText')

or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                  for val in cf_names])

# Exclude GNOME returns.
not_filt = fes.Not([fes.PropertyIsLike(literal='*GNOME*', **kw)])

begin, end = fes_date_filter(start, stop)
bbox_crs = fes.BBox(bbox, crs=crs)
filter_list = [fes.And([bbox_crs, begin, end, or_filt, not_filt])]
```

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
from owslib.csw import CatalogueServiceWeb


catalogs = ['http://www.ngdc.noaa.gov/geoportal/csw',
            'https://dev-catalog.ioos.us/csw',
            'http://geoport.whoi.edu/csw']

for endpoint in catalogs:
    csw = CatalogueServiceWeb(endpoint, timeout=60)
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
    records = '\n'.join(csw.records.keys())
    print('{}\n{}\n'.format(endpoint, records))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    http://www.ngdc.noaa.gov/geoportal/csw
    
    
    https://dev-catalog.ioos.us/csw
    hycom_global
    ncep_global
    
    http://geoport.whoi.edu/csw
    
    

</pre>
</div>
### We could not find any HF-Radar data there :-(

### Let's test removing the time constraint.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
filter_list = [fes.And([bbox_crs, or_filt, not_filt])]


for endpoint in catalogs:
    csw = CatalogueServiceWeb(endpoint, timeout=60)
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
    records = '\n'.join(csw.records.keys())
    print('{}\n{}\n'.format(endpoint, records))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    http://www.ngdc.noaa.gov/geoportal/csw
    HFRNet/USWC/500m/hourly/RTV
    HFRNet/USWC/1km/hourly/RTV
    HFRNet/USWC/2km/hourly/RTV
    HFRNet/USWC/6km/hourly/RTV
    HFR/USWC/1km/hourly/RTV/HFRADAR,_US_West_Coast,_1km_Resolution,_Hourly_RTV_best.ncd
    HFR/USWC/2km/hourly/RTV/HFRADAR,_US_West_Coast,_2km_Resolution,_Hourly_RTV_best.ncd
    
    https://dev-catalog.ioos.us/csw
    hycom_global
    ncep_global
    CORDC_MONTHLY
    UCSC
    CA_DAS
    
    http://geoport.whoi.edu/csw
    
    

</pre>
</div>