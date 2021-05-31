#!/usr/bin/env python
# coding: utf-8

# # Fetching data from a CSW catalog with Python tools
# 
# This notebook shows a typical workflow to query a [Catalog Service for the Web (CSW)](https://en.wikipedia.org/wiki/Catalog_Service_for_the_Web) and create a request for data endpoints that are suitable for download.
# 
# In this queries multiple catalogs for the near real time HF-Radar current data.
# 
# The first step is to create the data filter based on the geographical region bounding box, the time span, and the CF variable standard name.

# In[1]:


from datetime import datetime, timedelta

# Region: West coast.
min_lon, max_lon = -123, -121
min_lat, max_lat = 36, 40

bbox = [min_lon, min_lat, max_lon, max_lat]
crs = "urn:ogc:def:crs:OGC:1.3:CRS84"

# Temporal range: past week.
now = datetime.utcnow()
start, stop = now - timedelta(days=(14)), now - timedelta(days=(7))

# Surface velocity CF names.
cf_names = [
    "surface_northward_sea_water_velocity",
    "surface_eastward_sea_water_velocity",
]

msg = """
*standard_names*: {cf_names}
*start and stop dates*: {start} to {stop}
*bounding box*:{bbox}
*crs*: {crs}""".format

print(
    msg(
        **{
            "cf_names": ", ".join(cf_names),
            "start": start,
            "stop": stop,
            "bbox": bbox,
            "crs": crs,
        }
    )
)


# Now it is possible to assemble a [OGC Filter Encoding (FE)](http://www.opengeospatial.org/standards/filter) for the search using `owslib.fes`\*. Note that the final result is only a list with all the filtering conditions.
# 
# \* OWSLib is a Python package for client programming with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, and their related content models.

# In[2]:


from owslib import fes


def fes_date_filter(start, stop, constraint="overlaps"):
    start = start.strftime("%Y-%m-%d %H:00")
    stop = stop.strftime("%Y-%m-%d %H:00")
    if constraint == "overlaps":
        propertyname = "apiso:TempExtent_begin"
        begin = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname, literal=stop)
        propertyname = "apiso:TempExtent_end"
        end = fes.PropertyIsGreaterThanOrEqualTo(
            propertyname=propertyname, literal=start
        )
    elif constraint == "within":
        propertyname = "apiso:TempExtent_begin"
        begin = fes.PropertyIsGreaterThanOrEqualTo(
            propertyname=propertyname, literal=start
        )
        propertyname = "apiso:TempExtent_end"
        end = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname, literal=stop)
    else:
        raise NameError("Unrecognized constraint {}".format(constraint))
    return begin, end


# In[3]:


kw = dict(wildCard="*", escapeChar="\\", singleChar="?", propertyname="apiso:AnyText")

or_filt = fes.Or([fes.PropertyIsLike(literal=("*%s*" % val), **kw) for val in cf_names])

# Exclude GNOME returns.
not_filt = fes.Not([fes.PropertyIsLike(literal="*GNOME*", **kw)])

begin, end = fes_date_filter(start, stop)
bbox_crs = fes.BBox(bbox, crs=crs)
filter_list = [fes.And([bbox_crs, begin, end, or_filt, not_filt])]


# It is possible to use the same filter to search multiple catalogs. The cell below loops over 3 catalogs hoping to find which one is more up-to-date and returns the near real time data.

# In[4]:


def get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000):
    """Iterate `maxrecords`/`pagesize` times until the requested value in
    `maxrecords` is reached.
    """
    from owslib.fes import SortBy, SortProperty

    # Iterate over sorted results.
    sortby = SortBy([SortProperty("dc:title", "ASC")])
    csw_records = {}
    startposition = 0
    nextrecord = getattr(csw, "results", 1)
    while nextrecord != 0:
        csw.getrecords2(
            constraints=filter_list,
            startposition=startposition,
            maxrecords=pagesize,
            sortby=sortby,
        )
        csw_records.update(csw.records)
        if csw.results["nextrecord"] == 0:
            break
        startposition += pagesize + 1  # Last one is included.
        if startposition >= maxrecords:
            break
    csw.records.update(csw_records)


# In[5]:


from owslib.csw import CatalogueServiceWeb

endpoint = "https://data.ioos.us/csw"

csw = CatalogueServiceWeb(endpoint, timeout=60)
get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = "\n".join(csw.records.keys())
print("Found {} records.\n".format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print("[{}]: {}".format(value.title, key))


# Let us check the 6 km resolution metadata record we found above.

# In[6]:


value = csw.records[
    "HFR/USWC/6km/hourly/RTV/HFRADAR_US_West_Coast_6km_Resolution_Hourly_RTV_best.ncd"
]

print(value.abstract)


# In[7]:


attrs = [attr for attr in dir(value) if not attr.startswith("_")]
nonzero = [attr for attr in attrs if getattr(value, attr)]
nonzero


# The `xml` has the full dataset metadata from the catalog. Let's print a few key ones here:

# In[8]:


value.subjects  # What is in there?


# In[9]:


value.modified  # Is it up-to-date?


# In[10]:


bbox = value.bbox.minx, value.bbox.miny, value.bbox.maxx, value.bbox.maxy
bbox  # The actual bounding box of the data.


# The next step is to inspect the type services and schemes available for downloading the data.
# The easiest way to accomplish that is with by "sniffing" the URLs with `geolinks`.

# In[11]:


from geolinks import sniff_link

msg = "geolink: {geolink}\nscheme: {scheme}\nURL: {url}\n".format
for ref in value.references:
    if ref["scheme"] == "OPeNDAP:OPeNDAP":
        url = ref["url"]
    print(msg(geolink=sniff_link(ref["url"]), **ref))


# For a detailed description of what those `geolink` results mean check the [lookup](https://github.com/OSGeo/Cat-Interop/blob/master/LinkPropertyLookupTable.csv) table.
# There are Web Coverage Service (WCS), Web Map Service (WMS),
# direct links, and OPeNDAP services available.
# 
# We can use any of those to obtain the data but the easiest one to explore interactively is the open OPeNDAP endpoint.

# In[12]:


import xarray as xr

ds = xr.open_dataset(url)
ds


# Select "yesterday" data.

# In[13]:


from datetime import date, timedelta

yesterday = date.today() - timedelta(days=1)

ds = ds.sel(time=yesterday)


# Compute the speed while masking invalid values.

# In[14]:


import numpy.ma as ma

u = ds["u"].data
v = ds["v"].data

lon = ds.coords["lon"].data
lat = ds.coords["lat"].data
time = ds.coords["time"].data

u = ma.masked_invalid(u)
v = ma.masked_invalid(v)


# This cell is only a trick to show all quiver arrows with the same length,
# for visualization purposes,
# and indicate the vector magnitude with colors instead.

# In[15]:


import numpy as np
from oceans.ocfis import spdir2uv, uv2spdir

angle, speed = uv2spdir(u, v)
us, vs = spdir2uv(np.ones_like(speed), angle, deg=True)


# And now we are ready to create the plot.

# In[16]:


get_ipython().run_line_magic('matplotlib', 'inline')

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy import feature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

LAND = feature.NaturalEarthFeature(
    "physical", "land", "10m", edgecolor="face", facecolor="lightgray"
)

sub = 2
dx = dy = 0.5
center = -122.416667, 37.783333  # San Francisco.
bbox = lon.min(), lon.max(), lat.min(), lat.max()

fig, (ax0, ax1) = plt.subplots(
    ncols=2, figsize=(20, 20), subplot_kw=dict(projection=ccrs.PlateCarree())
)


ax0.set_extent(bbox)
cs = ax0.pcolormesh(lon, lat, ma.masked_invalid(speed))
gl = ax0.gridlines(draw_labels=True)
gl.xlabels_top = gl.ylabels_right = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

cbar = fig.colorbar(cs, ax=ax0, shrink=0.45, extend="both")
cbar.ax.set_title(r"speed m s$^{-1}$", loc="left")

ax0.add_feature(LAND, zorder=0, edgecolor="black")
ax0.set_title("{}\n{}".format(value.title, ds["time"].values))

ax1.set_extent([center[0] - dx - dx, center[0] + dx, center[1] - dy, center[1] + dy])
q = ax1.quiver(
    lon[::sub],
    lat[::sub],
    us[::sub, ::sub],
    vs[::sub, ::sub],
    speed[::sub, ::sub],
    scale=30,
)
ax1.quiverkey(q, 0.5, 0.85, 1, r"1 m s$^{-1}$", coordinates="axes")
gl = ax1.gridlines(draw_labels=True)
gl.xlabels_top = gl.ylabels_right = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

ax1.add_feature(LAND, zorder=0, edgecolor="black")
ax1.plot(
    ds["site_lon"], ds["site_lat"], marker="o", linestyle="none", color="darkorange"
)
ax1.set_title("San Francisco Bay area")


# And here is yesterday's sea surface currents from the west coast with a zoom in the San Francisco Bay area.
